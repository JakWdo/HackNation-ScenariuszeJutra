import os
import re
import requests
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from haystack.agents import Agent, Tool
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.components.builders.prompt_builder import PromptBuilder
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack.components.retrievers.in_memory import InMemoryBM25Retriever

# --- 1. Define Tools ---

# Tool 1: Web Search using DuckDuckGo
def web_search_function(query: str):
    """
    Searches the web using DuckDuckGo and returns a list of URLs.
    """
    from duckduckgo_search import DDGS
    results = DDGS().text(query, max_results=5)
    return [r['href'] for r in results]

web_search_tool = Tool(
    name="web_search",
    description="A tool to search the web for information and get a list of URLs.",
    payload_callback=web_search_function,
)

# Tool 2: URL Parser to find files
def url_parser_function(url: str):
    """
    Crawls a given URL to find links to non-text files (images, audio).
    """
    FILE_EXTENSIONS = ['.png', '.jpg', '.jpeg', '.gif', '.mp3', '.wav', '.ogg']
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        file_urls = []
        for link in soup.find_all('a'):
            href = link.get('href')
            if href and any(href.endswith(ext) for ext in FILE_EXTENSIONS):
                file_urls.append(urljoin(url, href))
        return file_urls
    except Exception as e:
        return f"Error crawling {url}: {e}"

url_parser_tool = Tool(
    name="url_parser",
    description="A tool to crawl a URL and extract links to image and audio files.",
    payload_callback=url_parser_function,
)

# Tool 3: File Downloader
def file_downloader_function(url: str, save_path: str = "downloads"):
    """
    Downloads a file from a URL and saves it.
    """
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        parsed_url = urlparse(url)
        filename = os.path.basename(parsed_url.path)
        if not filename:
            filename = url.split("/")[-1]
            
        filepath = os.path.join(save_path, filename)
        
        with open(filepath, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                
        return f"Downloaded {url} to {filepath}"
    except Exception as e:
        return f"Failed to download {url}: {e}"

file_downloader_tool = Tool(
    name="file_downloader",
    description="A tool to download a file from a URL.",
    payload_callback=file_downloader_function,
)

# --- 2. Initialize Agents ---

# Agent 1: Researcher Agent
researcher_prompt = PromptBuilder(template="You are a research assistant. Use the 'web_search' tool to find URLs for the query: {{ query }}")
researcher_generator = OpenAIChatGenerator(model="gpt-4o-mini")
document_store = InMemoryDocumentStore()

researcher_agent = Agent(
    name="ResearcherAgent",
    prompt_builder=researcher_prompt,
    llm=researcher_generator,
    tools=[web_search_tool],
    memory_retriever=InMemoryBM25Retriever(document_store=document_store),
    full_history=True,
)

# Agent 2: Downloader Agent
downloader_prompt = PromptBuilder(template="You are a downloader. For each URL, use the 'url_parser' to find file links, then use the 'file_downloader' to save them. URLs: {{ urls }}")
downloader_generator = OpenAIChatGenerator(model="gpt-4o-mini")

downloader_agent = Agent(
    name="DownloaderAgent",
    prompt_builder=downloader_prompt,
    llm=downloader_generator,
    tools=[url_parser_tool, file_downloader_tool],
    memory_retriever=InMemoryBM25Retriever(document_store=document_store),
    full_history=True,
)

# --- 3. Create the Main Orchestrating Agent ---

main_agent_prompt_template = """
You are a helpful assistant. Your goal is to find and download non-text files based on a user query.
1. Use the 'call_researcher_agent' to find relevant URLs.
2. Pass the URLs to the 'call_downloader_agent' to find and download files.

User request: {{ query }}
"""
main_agent_prompt_builder = PromptBuilder(template=main_agent_prompt_template)
main_agent_generator = OpenAIChatGenerator(model="gpt-4o-mini")

main_agent = Agent(
    name="MainOrchestrator",
    prompt_builder=main_agent_prompt_builder,
    llm=main_agent_generator,
    tools=[
        Tool(
            name="call_researcher_agent",
            description="Call the ResearcherAgent to find URLs for a query.",
            payload_callback=lambda query: researcher_agent.run(query=query)["replies"][0],
        ),
        Tool(
            name="call_downloader_agent",
            description="Call the DownloaderAgent to process a list of URLs.",
            payload_callback=lambda urls: downloader_agent.run(urls=urls)["replies"][0],
        ),
    ],
    memory_retriever=InMemoryBM25Retriever(document_store=document_store),
    full_history=True,
)

# --- 4. Run the Pipeline ---

if __name__ == "__main__":
    # IMPORTANT: Set your OpenAI API key
    # os.environ["OPENAI_API_KEY"] = "YOUR_OPENAI_API_KEY"
    
    if not os.environ.get("OPENAI_API_KEY"):
        print("Please set your OPENAI_API_KEY environment variable.")
    else:
        query = "Find me pictures of the Artemis moon mission"
        print(f"--- Running pipeline for query: '{query}' ---")
        
        # 1. Run researcher
        research_result = main_agent.run(query=f"call_researcher_agent with query: {query}")
        print("\n--- Research Agent Output ---")
        print(research_result["replies"][0])
        
        # Extract URLs from the researcher's output
        urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', research_result["replies"][0])
        
        if urls:
            # 2. Run downloader
            download_result = main_agent.run(query=f"call_downloader_agent with urls: {urls}")
            print("\n--- Downloader Agent Output ---")
            print(download_result["replies"][0])
        else:
            print("\nNo URLs found by the research agent.")
