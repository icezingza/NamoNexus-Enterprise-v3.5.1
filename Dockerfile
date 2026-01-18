FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libsqlcipher-dev \
    pkg-config \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*
ENV CFLAGS="-I/usr/include/sqlcipher"
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8080
USER 1001
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
