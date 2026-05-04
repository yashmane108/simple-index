FROM python:3.9-slim
WORKDIR /app

# Install system dependencies for cryptography
RUN apt-get update && apt-get install -y gcc libssl-dev && rm -rf /var/lib/apt/lists/*

# Install python libraries
RUN pip install --no-cache-dir flask pymysql cryptography boto3 botocore

COPY app.py .
COPY index.html .

EXPOSE 80
CMD ["python", "app.py"]
