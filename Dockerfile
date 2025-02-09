FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app
CMD ["prefect", "worker", "start", "-p", "stock-analysis-pool"]
