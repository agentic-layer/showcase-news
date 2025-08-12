import os

from agenticlayer.agent_to_a2a import to_a2a

from news.agent import root_agent

app = to_a2a(root_agent)

# Entry point for IDE to start in debug mode
# Make sure that the IDE uses the .env file
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=os.environ.get("UVICORN_HOST", "localhost"), port=int(os.environ.get("UVICORN_PORT", 8000)))
