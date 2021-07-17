# Base Image
FROM python:3.7

# Application Directory
RUN mkdir /app
WORKDIR /app

# Add code in CWD to Application Directory
COPY . /app/

# Default Environment Variables
ENV PYTHONUNBUFFERED 1
ENV LANG C.UTF-8
ENV DEBIAN_FRONTEND=noninteractive

# Project Environment Variables
ENV PORT=8000

# Install Docker Requirements
RUN apt-get update && apt-get install -y --no-install-recommends \
    tzdata \
    python3-setuptools \
    python3-pip \
    python3-dev \
    python3-venv \
    git \
    && \
apt-get clean && \
rm -fr /var/lib/opt/lists/*

RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

EXPOSE $PORT
