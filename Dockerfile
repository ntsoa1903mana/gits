# Use the Python 3.10.12-slim-bullseye as the base image
FROM python:3.10.12-slim-bullseye

# Set the working directory in the container
WORKDIR /app

# Copy requirements.txt to the container
COPY requirements.txt requirements.txt

# Create a virtual environment and set PATH
RUN python3 -m venv venv
ENV PATH="/app/venv/bin:$PATH"

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libffi-dev \
    cmake \
    libcurl4-openssl-dev \
    nodejs \
    screen && \
    python -m pip install --no-cache-dir -U pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy your application code to the container
COPY . .

# Make your app.py script executable
RUN chmod +x app.py

# Change permissions (use with caution, as it grants full access)
RUN chmod -R 777 /app

# Specify the command to run your application
CMD [ "screen", "-d", "-m", "python3", "app.py" ]
