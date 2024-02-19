import requests
import langchain
from datetime import datetime, timedelta
from extensions.Memoir.rag.rag_data_memory import RAG_DATA_MEMORY
from langchain_community.document_loaders import SeleniumURLLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

class UrlHandler():
    def __init__(self, character_name):
        self.character_name = character_name
        pass

    def get_url(self, url, mode='output'):
        urls = [url]
        loader = SeleniumURLLoader(urls=urls)
        
        data = loader.load()
        #print("##############")
        #print(data)
        #print("##############")
        
        #save to rag memory
        text_splitter = RecursiveCharacterTextSplitter(
    separators=["\n"], chunk_size=1000, chunk_overlap=50, keep_separator=False
)
        verbose = False
        ltm_limit = 2
        address = "http://localhost:6333"
        rag = RAG_DATA_MEMORY(self.character_name,ltm_limit,verbose, address=address)
        for document in data:
            splits = text_splitter.split_text(document.page_content)
        
            for text in splits:
                 #print("----")
                 #print(text)
                 #print("----")
                 now = datetime.utcnow()
                 data_to_insert = str(text) + " reference:" + str(url)
                 doc_to_insert = {'comment': str(data_to_insert),'datetime': now}
                 rag.store(doc_to_insert)
            
        if mode == 'input':
            return data
        elif mode == 'output':
            return f"[URL_CONTENT={url}]\n{data}"
