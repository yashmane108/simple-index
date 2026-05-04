# --- Stage 1: Build Stage ---
FROM python:3.9-slim AS builder

WORKDIR /build

# Install compiler tools needed to build certain Python packages
RUN apt-get update && apt-get install -y \
    gcc \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies into a local folder (wheels)
RUN pip install --no-cache-dir flask pymysql cryptography boto3 botocore --traget=/build/deps

# --- Stage 2: Final Runtime Stage ---
FROM python:3.9-slim

WORKDIR /app

# Copy only the installed Python packages from the builder stage
COPY --from=builder /build/deps /app/deps
# Copy your application files
COPY app.py .
COPY global-bundle.pem .
# Ensure your index.html is copied if your app.py references it externally
COPY index.html .

# Ensure the local bin is in the PATH so Python can find the libraries
ENV PATH=/root/.local/bin:$PATH

EXPOSE 80

CMD ["python", "app.py"]
