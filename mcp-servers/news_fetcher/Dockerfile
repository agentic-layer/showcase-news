FROM python:3.13-slim-trixie

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv
WORKDIR /app

# Copy the news_fetcher project files
COPY mcp-servers/news_fetcher ./

# Install dependencies and the project
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen

# Expose port 8001 for news_fetcher
EXPOSE 8001

# Run the news_fetcher module
CMD uv run python -m news_fetcher
