FROM python:3.10-slim

WORKDIR /app

# Install system packages
RUN apt-get update && \
    apt-get install -y \
    pkg-config \
    default-libmysqlclient-dev \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt \
    && pip install pytest pytest-html pytest-cov

RUN mkdir -p /reports

COPY . /app/

EXPOSE 8080

CMD ["/app/start.sh"]