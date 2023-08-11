# Base image
FROM python:3.11-slim-buster AS base
ARG DEV
# Install system packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Build stage
FROM base AS build

# Install Poetry
RUN pip install poetry==1.4.2
ENV POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_CREATE=true \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1
ENV PATH="$PATH:$POETRY_HOME/bin"

WORKDIR /app
COPY pyproject.toml .
RUN  poetry lock --no-update && poetry install

# Copy the rest of the application code
COPY . .
# Runtime stage
FROM base AS runtime
WORKDIR /app
COPY --from=build /app /app
ENV PATH="/app/.venv/bin:$PATH"
RUN echo "source /app/.venv/bin/activate" >> /etc/profile.d/venv.sh
