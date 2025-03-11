"""
urlhandler.py - uses langchain to import the entire url into context and rag

Memoir+ a persona extension for Text Gen Web UI. 
MIT License

Copyright (c) 2025 brucepro, corbin-hayden13
"""
from datetime import datetime
from extensions.Memoir.big_memory.big_memory import RagDataMemory
from langchain_community.document_loaders import SeleniumURLLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

class UrlHandler:
    def __init__(self, memoir_config_params: dict):
        self.character_name = memoir_config_params['current_persona']
        self.qdrant_address = memoir_config_params['qdrant_address']

    def get_url(self, url, mode='output'):
        urls = [url]
        loader = SeleniumURLLoader(urls=urls)
        
        data = loader.load()
        print("##############")
        print(data)
        print("##############")
        
        #save to rag memory
        text_splitter = RecursiveCharacterTextSplitter(
            separators=["\n"], chunk_size=1000, chunk_overlap=50, keep_separator=False
        )
        verbose = False
        ltm_limit = 2
        rag = RagDataMemory(self.character_name, ltm_limit,verbose, address=self.qdrant_address)
        for document in data:
            splits = text_splitter.split_text(document.page_content)
        
            for text in splits:
                 now = datetime.utcnow()
                 data_to_insert = str(text) + " reference:" + str(url)
                 doc_to_insert = {'comment': str(data_to_insert),'datetime': now}
                 rag.store(doc_to_insert)
            
        if mode == 'input':
            return data
        elif mode == 'output':
            data_as_str: str = str(data)
            print(f"outputting {data_as_str}")
            return f"[URL_CONTENT={url}]\n{data_as_str}"
