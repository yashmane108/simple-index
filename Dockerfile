# Use Python instead of Nginx
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Install the necessary 'libraries' for Python to talk to the web and RDS
RUN pip install --no-cache-dir flask pymysql

# Copy your Python code (app.py) and your HTML (index.html)
COPY app.py .
COPY index.html .

# Still expose port 80
EXPOSE 80

# Command to start the Python server
CMD ["python", "app.py"]
