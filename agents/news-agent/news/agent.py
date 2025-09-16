import json
import logging
import os

from google.adk.agents import Agent
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.mcp_tool import StreamableHTTPConnectionParams
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset

def create_sub_agents():
    """Create sub agents from environment variable configuration."""
    sub_agents_config = os.environ.get("SUB_AGENTS", "{}")
    print("sub_agents_config: {}".format(sub_agents_config))
    try:
        agents_map = json.loads(sub_agents_config)
    except json.JSONDecodeError:
        print(f"Warning: Invalid JSON in SUB_AGENTS environment variable. Using empty configuration.")
        agents_map = {}

    sub_agents = []
    for agent_name, config in agents_map.items():
        if "url" not in config:
            print(f"Warning: Missing 'url' for agent '{agent_name}'. Skipping.")
            continue

        logging.info("Adding sub-agent: %s with URL: %s", agent_name, config["url"])
        sub_agents.append(RemoteA2aAgent(
            name=agent_name,
            agent_card=config["url"],
        ))

    return sub_agents

news_fetcher_toolset = MCPToolset(
    connection_params=StreamableHTTPConnectionParams(
        url="http://mcp-news-fetcher:8001/mcp/",  # News RSS MCP server endpoint
    ),
)

root_agent = Agent(
    name="news_agent",
    model=LiteLlm("gemini/gemini-2.0-flash"),
    description=(
        "Agent that can get the latest news articles and talk to other agents to summarize them."
    ),
    instruction=("""
    You are a professional news host agent. Your role is to help users access the latest news information.

    ## Core Functions

    ### 1. Latest News Requests
    When users ask for "latest news", "recent news", or similar:
    - Call `fetch_article_titles_and_urls()` to get recent article titles and URLs
    - Present the articles in a clean, readable format
    - Show article titles, URLs, and dates
    
    ### 2. Article Summarization Requests  
    When users ask to summarize a specific article:
    - Contact the summarizer agent to generate a summary
    - Present the summary to the user
    """
    ),
    sub_agents=create_sub_agents(),
    tools=[
        news_fetcher_toolset,
    ],
)
