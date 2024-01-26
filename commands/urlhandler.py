import requests
from bs4 import BeautifulSoup

class UrlHandler:
    def __init__(self):
        pass

    def get_url(self, url, mode='input', tags=['title','h1','h2','h3','h4','h5','h6','p','table','ul','ol']):
        """
        This function fetches the content of a given URL and returns it in either input or output format.

        Args:
            url (str): The URL to fetch the content from.
            mode (str): Specifies whether the returned content should be added as an input ('input') or output ('output'). Defaults to 'input'.
            tags (list): A list of HTML tags to extract the text from. Defaults to ['h1', 'p'].

        Returns:
            str: The text content of the specified tags from the specified URL in either input or output format, depending on the value of `mode`.

        Side Effects:
            None.
        """
        headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36', 'Accept-Encoding': 'gzip, deflate', 'Accept': '*/*', 'Connection': 'keep-alive'}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, "html.parser")
        text = ""
        for tag in tags:
            text += "\n".join([element.get_text() for element in soup.find_all(tag)]) + "\n"
        if mode == 'input':
            return text
        elif mode == 'output':
            return f"[URL_CONTENT={url}]\n{text}"
