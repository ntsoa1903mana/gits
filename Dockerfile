FROM python:3.10.12-slim-bullseye

WORKDIR /app

COPY requirements.txt requirements.txt

RUN python3 -m venv venv
ENV PATH="/app/venv/bin:$PATH"

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libffi-dev \
    cmake \
    libcurl4-openssl-dev \
    nodejs && \
    python -m pip install --no-cache-dir -U pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x app.py

EXPOSE 8000

CMD ["python3", "app.py"]
