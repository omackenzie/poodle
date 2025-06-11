FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        build-essential \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt dev-requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt -r dev-requirements.txt

# Copy project
COPY . /app/

# Make entrypoint script executable
RUN chmod +x /app/docker-entrypoint.sh

# Create media directory with proper permissions
RUN mkdir -p /app/media && chmod 755 /app/media

# Expose port
EXPOSE 8000

# Run the application
CMD ["./docker-entrypoint.sh"]
