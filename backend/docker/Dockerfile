# FROM python:3.11-bookworm
FROM python:3.13-slim

RUN apt-get update && apt-get install -y netcat-openbsd && rm -rf /var/lib/apt/lists/*
RUN apt-get update && apt-get install -y gettext

WORKDIR /app

RUN apt-get update && apt-get install -y netcat-openbsd && rm -rf /var/lib/apt/lists/*

EXPOSE 8000

RUN pip install --upgrade pip setuptools wheel 
 
RUN pip install python-decouple
RUN pip install rich

COPY requirements.txt /app/
RUN pip install -r requirements.txt

COPY ./docker/entrypoint.sh /usr/local/bin/
COPY . /app/

RUN chmod +x /usr/local/bin/entrypoint.sh

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]

# The host machine makes a request to https://tranceanddance.local/.
# Docker intercepts that request and forwards it to the container on port 8000.
    #because we mapped host machine's port 8000 to container's 8000 in docker-compose
# The container is listening on 0.0.0.0:8000, so it handles the request and serves the response.