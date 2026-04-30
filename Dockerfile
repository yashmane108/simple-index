# Use Python instead of Nginx
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies for cryptography
RUN apt-get update && apt-get install -y gcc libssl-dev && rm -rf /var/lib/apt/lists/*

# Install python libraries
RUN pip install --no-cache-dir flask pymysql cryptography boto3

# Copy your Python code (app.py) and your HTML (index.html)
COPY app.py .
COPY index.html .

# Still expose port 80
EXPOSE 80

# Command to start the Python server
CMD ["python", "app.py"]
