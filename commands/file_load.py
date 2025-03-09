"""
file_load.py - handles the loading of files from the ui

Memoir+ a persona extension for Text Gen Web UI. 
MIT License

Copyright (c) 2025 brucepro, corbin-hayden13
"""
from datetime import datetime
from extensions.Memoir.rag.ingest_file_class import Ingest_File
from extensions.Memoir.big_memory.big_memory import RagDataMemory
from langchain.text_splitter import RecursiveCharacterTextSplitter


class File_Load:
    def __init__(self, memoir_config_params: dict):
        self.character_name = memoir_config_params['current_persona']
        self.qdrant_address = memoir_config_params['qdrant_address']

    def read_file(self, file):
        load_file = Ingest_File(file)
        file_content = load_file.loadfile()
        
        #save to rag memory
        text_splitter = RecursiveCharacterTextSplitter(
            separators=["\n"], chunk_size=1000, chunk_overlap=100, keep_separator=False
        )
        verbose = False
        ltm_limit = 2
        rag = RagDataMemory(self.character_name,ltm_limit,verbose, address=self.qdrant_address)

        for document in file_content:
            splits = text_splitter.split_text(document.page_content)
    
            for text in splits:
                 now = datetime.utcnow()
                 data_to_insert = str(text) + " reference:" + str(file)
                 doc_to_insert = {'comment': str(data_to_insert),'datetime': now}
                 rag.store(doc_to_insert)

        return f"[FILE_CONTENT={file}]\n{file_content}"
    
