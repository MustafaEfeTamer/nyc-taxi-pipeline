FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir --only-binary :all: --require-hashes -r /tmp/requirements.txt

CMD ["python", "producer/main.py"]

