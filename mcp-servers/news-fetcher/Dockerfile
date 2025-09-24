FROM python:3.13-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv
WORKDIR /app

# Copy the project files
COPY . ./

# Install dependencies and the project
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen

# Expose port
EXPOSE 8000

# Run the news_fetcher module
CMD uv run python -m news_fetcher
