# Use an official Python base image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies
# Updated system dependencies
RUN apt-get update && apt-get -y dist-upgrade
RUN apt-get update && apt-get install -y \
    gcc \
    pkg-config \
    curl\
    libmariadb-dev-compat \
    libmariadb-dev \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*
# Download and install dockerize
RUN curl -sSL https://github.com/jwilder/dockerize/releases/download/v0.6.1/dockerize-linux-amd64-v0.6.1.tar.gz \
    | tar -xz -C /usr/local/bin


# Create and set work directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Entrypoint script (optional, e.g., to run migrations)
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]