FROM python:3.10-slim

WORKDIR /app

# Install the system packages required by Flask-MySQLdb
RUN apt-get update && \
    apt-get install -y \
    pkg-config \
    default-libmysqlclient-dev \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY . /app/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

EXPOSE 6666
CMD ["python", "app.py"]
