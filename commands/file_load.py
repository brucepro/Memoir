import requests
import os
from datetime import datetime, timedelta
from extensions.Memoir.rag.ingest_file_class import Ingest_File
from extensions.Memoir.rag.rag_data_memory import RAG_DATA_MEMORY
from langchain.text_splitter import RecursiveCharacterTextSplitter


class File_Load():
    def __init__(self, character_name):
        self.character_name = character_name

    def read_file(self, file):
        load_file = Ingest_File(file)
        file_content = load_file.loadfile()
        
        #save to rag memory
        text_splitter = RecursiveCharacterTextSplitter(
separators=["\n"], chunk_size=1000, chunk_overlap=100, keep_separator=False
)
        verbose = False
        ltm_limit = 2
        address = "http://localhost:6333"
        rag = RAG_DATA_MEMORY(self.character_name,ltm_limit,verbose, address=address)
        for document in file_content:
            splits = text_splitter.split_text(document.page_content)
    
        for text in splits:
             #print("----")
             #print(text)
             #print("----")
             now = datetime.utcnow()
             data_to_insert = str(text) + " reference:" + str(file)
             doc_to_insert = {'comment': str(data_to_insert),'datetime': now}
             rag.store(doc_to_insert)
        return f"[FILE_CONTENT={file}]\n{file_content}"
    
