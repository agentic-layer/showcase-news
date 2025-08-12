import requests
from bs4 import BeautifulSoup

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm


def extract_article_content(article_url: str) -> str:
    print(f"Extracting content from: {article_url}")
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; News Summarizer Agent; +https://github.com/agentic-layer/demo)'
        }
        response = requests.get(article_url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # Remove script and style elements
        for script in soup(["script", "style", "nav", "header", "footer", "aside"]):
            script.decompose()

        # Extract text from paragraphs
        paragraphs = soup.find_all(['p', 'article', 'div'])
        content_parts = []

        for p in paragraphs:
            text = p.get_text().strip()
            if len(text) > 50:  # Only include substantial paragraphs
                content_parts.append(text)

        content = ' '.join(content_parts)
        return content[:3000]  # Limit content to 3000 chars for summarization

    except Exception as e:
        print(f"Error extracting content from {article_url}: {e}")
        return f"Could not extract content from the article URL: {str(e)}"


root_agent = Agent(
    name="summarizer_agent",
    model=LiteLlm("gemini/gemini-2.0-flash"),
    description=(
        "Agent that can summarize articles from websites."
    ),
    instruction="""
        You are a professional article summarizer. Your task is to:

        1. **Extract Article Content**: When given an article URL, extract the full text content from the webpage using the extract_article_content tool.
           - Hint: The extract_article_content tool can access the internet.
        
        2. **Generate Summary**: Create a concise 2-3 paragraph summary that captures:
           - The main topic and key points
           - Important facts, numbers, or quotes
           - The significance or implications of the news
           - Who is involved and what happened

        ## Process
        1. When you receive a request to summarize an article URL, first extract the content using the available tools
        2. Read and analyze the extracted content
        3. Generate a clear, informative summary
        4. Focus on the most newsworthy aspects

        ## Style Guidelines  
        - Write in clear, professional language
        - Be objective and factual
        - Include specific details when relevant
        - Keep summaries concise but comprehensive
        - Mention the source or publication when relevant

        If you cannot access or extract content from a URL, explain the issue clearly and suggest alternatives.
    """,
    tools=[extract_article_content],
)
