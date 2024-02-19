'''
using all the langchain loaders since I am lazy. 

'''
import os
import re
import unicodedata
import langchain
import langchain_community.document_loaders
import pathlib

class Ingest_File:
    def __init__(self, file, max_pages=None, max_time=None):
        self.file = file
        self.max_pages = max_pages
        self.max_time = max_time
    
    def loadfile(self):
        if pathlib.Path(self.file).suffix == ".csv":
            loader = langchain_community.document_loaders.CSVLoader(self.file)

            data = loader.load()
            return data
        if pathlib.Path(self.file).suffix == ".txt":
            loader = langchain_community.document_loaders.TextLoader(self.file)
            document = loader.load()
            return document
        if pathlib.Path(self.file).suffix == ".md":
            loader = langchain_community.document_loaders.UnstructuredMarkdownLoader(self.file)
            document = loader.load()
            return document
        
        if pathlib.Path(self.file).suffix == ".pdf":
            loader = langchain_community.document_loaders.PyPDFLoader(self.file, extract_images=True)
            pages = loader.load_and_split()
            return pages
        if pathlib.Path(self.file).suffix == ".epub":
            loader = langchain_community.document_loaders.UnstructuredEPubLoader(self.file, mode="single", strategy="fast")
            docs = loader.load();
            return docs
        if pathlib.Path(self.file).suffix == ".html":
            loader = langchain_community.document_loaders.BSHTMLLoader(self.file, mode="single", strategy="fast")
            docs = loader.load();
            return docs
        
        if pathlib.Path(self.file).suffix == "":
            #defaults to unstructured loader so not as good as the specific loaders.
            loader = langchain_community.document_loaders.DirectoryLoader(self.file)
            documents = loader.load()
            return documents
        pass
