# Use Python 3.13 slim image for smaller size
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install system dependencies required by curl_cffi
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install UV for fast package management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy project files
COPY ./ /app

# Install dependencies using UV
RUN uv sync --frozen --no-dev --no-install-project

# Run the application
CMD ["uv", "run", "python", "main.py"]

