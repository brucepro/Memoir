"""
rag_data_memory.py - main class that implements that vector store for the RAG system

Memoir+ a persona extension for Text Gen Web UI.
MIT License

Copyright (c) 2024 brucepro

"""

import random
import logging
import time
import traceback
import uuid
from datetime import datetime
from qdrant_client import models, QdrantClient
from qdrant_client.http.models import PointStruct
from html import escape
from sentence_transformers import SentenceTransformer

# Setup logging
logger = logging.getLogger(__name__)

class RagDataMemory():
    def __init__(self,
                 collection,
                 ltm_limit,
                 verbose=False,
                 embedder='all-mpnet-base-v2',
                 address='localhost',
                 port=6333,
                 max_retries=3
                 ):

        self.verbose = verbose
        if self.verbose:
            print("initiating verbose debug mode.............")
        self.collection = collection + "_rag_data"
        self.ltm_limit = ltm_limit
        self.max_retries = max_retries
        self.error_log = []  # Track errors for debugging
        print("RAG LIMIT:" + str(ltm_limit))
        self.address = address
        self.port = port
        if self.verbose:
            print(f"addr:{self.address}, port:{self.port}")

        self.embedder = embedder
        # Force encoder onto CPU to avoid CUDA memory errors (same as LTM)
        self.encoder = SentenceTransformer(self.embedder, device='cpu')
        self.qdrant = QdrantClient(self.address, port=self.port)
        self.create_vector_db_if_missing()

    def _log_error(self, operation: str, error: Exception):
        """Log detailed error information"""
        error_entry = {
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "error_type": type(error).__name__,
            "error_msg": str(error),
            "traceback": traceback.format_exc(),
        }
        self.error_log.append(error_entry)
        if len(self.error_log) > 100:  # Keep last 100 errors
            self.error_log = self.error_log[-100:]
        logger.error(f"RAG Error in {operation}: {error}")

    
    def create_vector_db_if_missing(self):
        try:
            self.qdrant.create_collection(
                collection_name=self.collection,
                vectors_config=models.VectorParams(
                    size=self.encoder.get_sentence_embedding_dimension(),
                    distance=models.Distance.COSINE
                )

            )
            if self.verbose:
                print(f"created self.collection: {self.collection}")
        except Exception as e:
            if self.verbose:
                vectors_count = self.qdrant.get_collection(
                    self.collection).vectors_count
                if self.verbose:
                    print(
                        f"self.collection: {self.collection} already exists with {vectors_count} vectors, not creating: {e}")

    def delete_vector_db(self):
        try:
            self.qdrant.delete_collection(
                collection_name=self.collection,
                )
            if self.verbose:
                print(f"deleted self.collection: {self.collection}")
        except Exception as e:
            if self.verbose:
                print(
                    f"self.collection: {self.collection} does not exists, not deleting: {e}")


    def store(self, doc_to_upsert):
        """Store document with retry logic"""
        for attempt in range(self.max_retries):
            try:
                operation_info = self.qdrant.upsert(
                    collection_name=self.collection,
                    wait=True,
                    points=self.get_embedding_vector(doc_to_upsert),
                )
                if self.verbose:
                    print(operation_info)
                return True
            except Exception as e:
                if attempt == self.max_retries - 1:
                    self._log_error("store", e)
                    if self.verbose:
                        print(f"Failed to store after {self.max_retries} attempts: {e}")
                    return False
                if self.verbose:
                    print(f"Store attempt {attempt + 1} failed, retrying...")
                time.sleep(2 ** attempt)  # Exponential backoff
        return False

    def get_embedding_vector(self, doc):
        """Generate embedding vector with UUID-based ID"""
        data = doc['comment']
        self.vector = self.encoder.encode(data).tolist()

        # Use UUID for better uniqueness (backport from BuildAutomata)
        try:
            self.next_id = str(uuid.uuid4())
        except Exception as e:
            logger.warning(f"UUID generation failed, using random int: {e}")
            self.next_id = random.randint(0, int(1e10))

        points = [
            PointStruct(id=self.next_id,
                        vector=self.vector,
                        payload=doc),
        ]
        return points

    def recall(self, query):
        """Recall RAG data with error handling (Fixes GitHub Issue #92)"""
        try:
            self.query_vector = self.encoder.encode(query).tolist()

            # Updated to use query_points (new Qdrant API)
            results = self.qdrant.query_points(
                collection_name=self.collection,
                query=self.query_vector,
                limit=self.ltm_limit + 1,
                with_payload=True
            )
            return self.format_results_from_qdrant(results.points)
        except Exception as e:
            self._log_error("recall", e)
            if self.verbose:
                print(f"RAG recall failed: {e}")
            return []  # Return empty list on failure

    def delete(self, comment_id):
        """Delete RAG data with error handling"""
        try:
            self.qdrant.delete_points(self.collection, [comment_id])
            logger.debug(f"Deleted RAG data with ID: {comment_id}")
            return True
        except Exception as e:
            self._log_error("delete", e)
            if self.verbose:
                print(f"Delete failed for ID {comment_id}: {e}")
            return False
        
    def format_results_from_qdrant(self, results):
        formated_results = []
        seen_comments = set()
        result_count = 0
        for result in results[1:]:
            comment = result.payload['comment']
            if comment not in seen_comments:
                seen_comments.add(comment)
                #formated_results.append("(" + result.payload['datetime'] + "'Memory':" + result.payload['comment'] + ", 'Emotions:" + result.payload['emotions'] + ", 'People':" + result.payload['people'] + ")")                
                #formated_results.append("(" + result.payload['datetime'] + "Memory:" + escape(result.payload['comment']) + ",Emotions:" + escape(result.payload['emotions']) + ",People:" + escape(result.payload['people']) + ")")
                datetime_obj = datetime.strptime(result.payload['datetime'], "%Y-%m-%dT%H:%M:%S.%f")
                date_str = datetime_obj.strftime("%Y-%m-%d")
                formated_results.append(result.payload['comment'] + ": on " + str(date_str))
                
            else:
                if self.verbose:
                    print("Not adding " + comment)
            result_count += 1
        return formated_results


    def __repr__(self):
        return f"address: {self.address}, collection: {self.collection}"

    def __len__(self):
        return self.qdrant.get_collection(self.collection).vectors_count
