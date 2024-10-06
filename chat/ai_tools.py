from langchain_community.utilities import WikipediaAPIWrapper
from langchain_community.tools import WikipediaQueryRun,DuckDuckGoSearchRun
from langchain_community.document_loaders import UnstructuredURLLoader
from urlextract import URLExtract
from duckduckgo_search.exceptions import RatelimitException

def wikipedia_tool(query):
    api_wrapper=WikipediaAPIWrapper(top_k_results=1,doc_content_chars_max=2000)
    wiki=WikipediaQueryRun(api_wrapper=api_wrapper)
    return wiki.run(query)

def duckduckgo_search_tool(query):
    try:
        search=DuckDuckGoSearchRun(name="Search")
        return search.run(query)
    except RatelimitException:
        return "Failed to get context from Web due to rate limiting."

def web_url_tool(query):
    extractor = URLExtract()
    urls = extractor.find_urls(query)
    loader=UnstructuredURLLoader(urls=urls)
    docs = loader.load()
    content = ""
    for url, doc in zip(urls,docs):
        content += f"Url : {url}\n\n Content : {doc.page_content.strip()}\n\n"
    return content


if __name__ == "__main____":
    print(wikipedia_tool("What is the capital of France?"))
    print(duckduckgo_search_tool("What is today date?"))
    print(web_url_tool("How i can visit this urls https://python.langchain.com/docs/integrations/,  https://python.langchain.com/docs/integrations/document_loaders/url/"))