"""
rag_data_memory.py - main class that implements that vector store for the RAG system

Memoir+ a persona extension for Text Gen Web UI. 
MIT License

Copyright (c) 2025 brucepro, corbin-hayden13
 
"""

import random
from datetime import datetime, timedelta
from qdrant_client import models, QdrantClient
from qdrant_client.http.models import PointStruct, QueryResponse
from sentence_transformers import SentenceTransformer


default_port: int = 6333
default_embedder: str = 'all-mpnet-base-v2'


class BigMemory:
    def __init__(self, memoir_config_params: dict, port: int=default_port, embedder: str=default_embedder):
        self.verbose = memoir_config_params.get("verbose", False)
        if self.verbose: print("initiating verbose debug mode.............")

        self.collection = memoir_config_params.get("current_persona")
        self.ltm_limit = memoir_config_params.get("ltm_limit", 2)
        self.address = memoir_config_params.get("qdrant_address", "http://localhost:6333")
        self.port = port
        if self.verbose: print(f"addr:{self.address}, port:{self.port}")

        self.embedder = embedder
        self.encoder = SentenceTransformer(self.embedder)
        self.qdrant = QdrantClient(url=self.address)

        self.create_vector_db_if_missing()
        
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
                
    # This is unused, dead code?
    def store(self, doc_to_upsert):
        operation_info = self.qdrant.upsert(
            collection_name=self.collection,
            wait=True,
            points=self.get_embedding_vector(doc_to_upsert),
        )
        if self.verbose:
            print(operation_info)
            
    def get_embedding_vector(self, doc):
        data = doc['comment'] + doc['people']
        vector = self.encoder.encode(data).tolist()
        next_id = random.randint(0, 1e10)
        points = [
            PointStruct(id=next_id,
                        vector=vector,
                        payload=doc),
        ]
        return points
    
    def recall(self, query):
        results: QueryResponse = self.qdrant.query_points(
            self.collection,
            query=self.encoder.encode(query).tolist(),
            limit=self.ltm_limit + 1
        )
        return self.format_results_from_qdrant(results)

    def format_results_from_qdrant(self, results: QueryResponse):
        formated_results = []
        seen_comments = set()
        result_count = 0
        for result in results[1:]:
            comment = result.payload['comment']
            if comment not in seen_comments:
                seen_comments.add(comment)
                datetime_obj = datetime.strptime(result.payload['datetime'], "%Y-%m-%dT%H:%M:%S.%f")
                date_str = datetime_obj.strftime("%Y-%m-%d")
                formated_results.append(result.payload['comment'] + ": on " + str(date_str))

            else:
                if self.verbose:
                    print("Not adding " + comment)
            result_count += 1

        return formated_results


class RagDataMemory(BigMemory):
    def __init__(self, memoir_config_params: dict, port: int=default_port, embedder: str=default_embedder):
        super().__init__(memoir_config_params, port, embedder)

    def __repr__(self):
        return f"address: {self.address}, collection: {self.collection}"

    def __len__(self):
        return self.qdrant.get_collection(self.collection).vectors_count
    
    
class LTM(BigMemory):
    def __init__(self, memoir_config_params: dict, port: int=default_port, embedder: str=default_embedder):
        super().__init__(memoir_config_params, port, embedder)

    def get_last_summaries(self, summary_range):
        # Retrieve all vectors
        all_vectors = self.qdrant.query_points(
            self.collection,
            query=self.encoder.encode("").tolist(),
            limit=99999999999 + 1
        )

        formated_results = []
        seen_comments = set()
        result_count = 0
        for result in all_vectors:
            comment = result.payload['comment']
            if comment not in seen_comments:
                seen_comments.add(comment)
                datetime_obj = datetime.strptime(result.payload['datetime'], "%Y-%m-%dT%H:%M:%S.%f")
                date_str = datetime_obj.strftime("%Y-%m-%d")
                now = datetime.now()
                if now - datetime_obj <= timedelta(hours=summary_range):
                    if self.verbose:
                        print("Adding memory to stm_context")
                    formated_results.append(result.payload['comment'] + ": on " + str(date_str))

            else:
                if self.verbose:
                    print("Not adding " + comment)
            result_count += 1
        return formated_results
