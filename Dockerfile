FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install minimal build tools (some dependencies may need compilation)
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy only what we need for install first to leverage Docker cache
COPY pyproject.toml pyproject.toml
COPY src/ src/
COPY scenarios/ scenarios/
COPY sample.env sample.env
COPY README.md README.md

# Upgrade pip and install the package (this will install dependencies listed in pyproject.toml)
RUN pip install --upgrade pip setuptools wheel \
    && pip install .

# Provide a tiny `uv` shim so the README examples continue to work.
# Usage: uv run <console-script> [args...] -> executes the installed console script
RUN printf '#!/bin/sh\nif [ "$1" = "run" ]; then shift; exec "$@"; else exec "$@"; fi\n' > /usr/local/bin/uv \
    && chmod +x /usr/local/bin/uv

# Expose ports used by the example scenario (green + two participants)
EXPOSE 9009 9018 9019

# Default to running the debate scenario like the README suggests.
CMD ["uv", "run", "agentbeats-run", "scenarios/debate/scenario.toml"]
