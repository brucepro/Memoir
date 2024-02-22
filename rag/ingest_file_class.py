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
        processed = 0
        print("File suffix to be processed:" + str(pathlib.Path(self.file).suffix))
        if pathlib.Path(self.file).suffix == ".csv":
            loader = langchain_community.document_loaders.CSVLoader(self.file)

            data = loader.load()
            processed = 1
            return data
        if pathlib.Path(self.file).suffix == ".txt":
            loader = langchain_community.document_loaders.TextLoader(file_path=self.file,encoding='utf-8',autodetect_encoding=True)
            document = loader.load()
            processed = 1
            return document
        if pathlib.Path(self.file).suffix == ".xml":
            loader = langchain_community.document_loaders.UnstructuredXMLLoader(self.file)
            document = loader.load()
            processed = 1
            return document

        if pathlib.Path(self.file).suffix == ".md":
            loader = langchain_community.document_loaders.UnstructuredMarkdownLoader(self.file)
            document = loader.load()
            processed = 1
            return document
        
        if pathlib.Path(self.file).suffix == ".pdf":
            loader = langchain_community.document_loaders.PyPDFLoader(self.file, extract_images=True)
            pages = loader.load_and_split()
            processed = 1
            return pages
        if pathlib.Path(self.file).suffix == ".epub":
            loader = langchain_community.document_loaders.UnstructuredEPubLoader(self.file, mode="single", strategy="fast")
            docs = loader.load();
            processed = 1
            return docs
        if pathlib.Path(self.file).suffix == ".html":
            loader = langchain_community.document_loaders.BSHTMLLoader(self.file, mode="single", strategy="fast")
            docs = loader.load();
            processed = 1
            return docs
        if pathlib.Path(self.file).suffix == ".xls":
            loader = langchain_community.document_loaders.UnstructuredExcelLoader(self.file, mode="elements")
            docs = loader.load();
            processed = 1
            return docs
        if pathlib.Path(self.file).suffix == ".xlsx":
            loader = langchain_community.document_loaders.UnstructuredExcelLoader(self.file, mode="elements")
            docs = loader.load();
            processed = 1
            return docs
        if pathlib.Path(self.file).suffix == ".ppt":
            loader = langchain_community.document_loaders.UnstructuredPowerPointLoader(self.file, mode="elements")
            data = loader.load();
            processed = 1
            return data
        if pathlib.Path(self.file).suffix == ".pptx":
            loader = langchain_community.document_loaders.UnstructuredPowerPointLoader(self.file, mode="elements")
            data = loader.load();
            processed = 1
            return data
        if pathlib.Path(self.file).suffix == ".doc":
            loader = langchain_community.document_loaders.UnstructuredWordDocumentLoader(self.file, mode="elements")
            data = loader.load();
            processed = 1
            return data
        if pathlib.Path(self.file).suffix == ".docx":
            loader = langchain_community.document_loaders.UnstructuredWordDocumentLoader(self.file, mode="elements")
            data = loader.load();
            processed = 1
            return data
        if pathlib.Path(self.file).suffix == ".vsdx":
            loader = langchain_community.document_loaders.VsdxLoader(file_path=self.file)
            data = loader.load();
            processed = 1
            return data

        if pathlib.Path(self.file).suffix == ".odt":
            loader = langchain_community.document_loaders.UnstructuredODTLoader(self.file, mode="elements")
            data = loader.load();
            processed = 1
            return data

        if pathlib.Path(self.file).suffix == "":
            #defaults to unstructured loader so not as good as the specific loaders.
            loader = langchain_community.document_loaders.DirectoryLoader(self.file)
            documents = loader.load()
            processed = 1
            return documents
        if processed == 0:
            #defaults to unstructured loader so not as good as the specific loaders.
            loader = langchain_community.document_loaders.UnstructuredFileLoader(self.file)
            documents = loader.load()
            processed = 1
            return documents
        pass
