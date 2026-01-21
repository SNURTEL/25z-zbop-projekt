FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies and uv
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy project files
COPY pyproject.toml ./
COPY *.py ./
COPY model/ ./model/
COPY models/ ./models/
COPY repositories/ ./repositories/
COPY services/ ./services/
COPY schemas/ ./schemas/
COPY routers/ ./routers/
COPY middleware/ ./middleware/
COPY db_handle/ ./db_handle/

# Install Python dependencies with uv
RUN uv pip install --system --no-cache .

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
