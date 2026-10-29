FROM python:3.12-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends default-mysql-client \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1
ENV FLASK_HOST=0.0.0.0

ARG FLASK_PORT=${FLASK_PORT}
EXPOSE ${FLASK_PORT}

CMD ["python", "app.py"]