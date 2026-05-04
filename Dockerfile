# ------------- STAGE 1 -------------------- # 
# Use Python instead of Nginx
FROM python:3.9-slim AS builder
# Set the working directory inside the container
WORKDIR /app
# only copy app.py and index.html. remaining added in .dockerignore
COPY . .
# Install system dependencies for cryptography
RUN apt-get update && apt-get install -y gcc libssl-dev ca-certificates && rm -rf /var/lib/apt/lists/*
# Install python libraries
RUN pip install --no-cache-dir flask pymysql cryptography boto3 botocore

# ------------- STAGE 2 -------------------- # 
FROM gcr.io/distroless/python3-debian12
WORKDIR /app
COPY --from=builder /app .

# Still expose port 80
EXPOSE 80
# Command to start the Python server
CMD ["python3", "app.py"]
