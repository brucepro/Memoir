"""
ingest_file_class.py - implementation of the langchain loaders to parse the files and chunk them. 

Memoir+ a persona extension for Text Gen Web UI. 
MIT License

Copyright (c) 2025 brucepro, corbin-hayden13
 
"""

import langchain_community.document_loaders
import pathlib


class Ingest_File:
    def __init__(self, file, max_pages=None, max_time=None):
        self.file = file
        self.max_pages = max_pages
        self.max_time = max_time
    
    def loadfile(self):
        path_suffix: str = str(pathlib.Path(self.file).suffix)
        print(f"File suffix to be processed: {path_suffix}")

        match path_suffix:
            case ".csv":
                return langchain_community.document_loaders.CSVLoader(self.file)

            case ".txt":
                return langchain_community.document_loaders.TextLoader(file_path=self.file,encoding='utf-8',autodetect_encoding=True).load()

            case ".xml":
                return langchain_community.document_loaders.UnstructuredXMLLoader(self.file).load()

            case ".md":
                return langchain_community.document_loaders.UnstructuredMarkdownLoader(self.file).load()

            case ".pdf":
                return langchain_community.document_loaders.PyPDFLoader(self.file, extract_images=True).load_and_split()

            case ".epub":
                return langchain_community.document_loaders.UnstructuredEPubLoader(self.file, mode="single", strategy="fast").load()

            case ".html":
                # At present, mode="single" and strategy="fast" do nothing so I'll pass those to BeautifulSoup to deal with
                return langchain_community.document_loaders.BSHTMLLoader(self.file, bs_kwargs={"mode": "single", "strategy": "fast"}).load()

            case ".xls", ".xlsx":
                return langchain_community.document_loaders.UnstructuredExcelLoader(self.file, mode="elements").load()

            case ".ppt", ".pptx":
                return langchain_community.document_loaders.UnstructuredPowerPointLoader(self.file, mode="elements").load()

            case ".doc", ".docx":
                return langchain_community.document_loaders.UnstructuredWordDocumentLoader(self.file, mode="elements").load()

            case ".vsdx":
                return langchain_community.document_loaders.VsdxLoader(file_path=self.file).load()

            case ".odt":
                return langchain_community.document_loaders.UnstructuredODTLoader(self.file, mode="elements").load()

            case "":
                return langchain_community.document_loaders.DirectoryLoader(self.file).load()

            case _:  # Default
                return langchain_community.document_loaders.UnstructuredFileLoader(self.file).load()
