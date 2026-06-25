# Use a lightweight Python base image
FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies (gcc is needed for some python packages)
# Clean up apt cache to keep the image small
RUN apt-get update && apt-get install -y --no-install-recommends gcc && \
    rm -rf /var/lib/apt/lists/*

# Install uv, a fast Python package manager
RUN pip install --no-cache-dir uv

# Copy dependency files first to leverage Docker's layer caching
# This makes subsequent builds much faster
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# Copy the rest of the application code
COPY . .

RUN addgroup --system appgroup && adduser --system --group --home /app appuser

# Ensure the new user owns the application files for write permissions
RUN chown -R appuser:appgroup /app

# Switch to the non-root user
USER appuser

# Expose the application port
EXPOSE 8000

# Run the application using Uvicorn
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]