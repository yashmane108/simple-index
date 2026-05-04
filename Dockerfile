# -------- STAGE 1 --------
FROM python:3.9-slim AS builder

WORKDIR /app

COPY app.py .
COPY index.html .

RUN apt-get update && apt-get install -y gcc libssl-dev ca-certificates && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir flask pymysql cryptography boto3 botocore --target=/app/deps


# -------- STAGE 2 --------
FROM gcr.io/distroless/python3-debian12

WORKDIR /app

COPY --from=builder /app/deps /app/deps
COPY --from=builder /app .

ENV PYTHONPATH=/app/deps

EXPOSE 80

CMD ["python3", "app.py"]
