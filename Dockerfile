# Base image
FROM python:3.7

# Application directory
RUN mkdir /app
WORKDIR /app

# Add code in CWD to application directory
COPY . /app/

# Default environment variables
ENV PYTHONUNBUFFERED 1
ENV LANG C.UTF-8
ENV DEBIAN_FRONTEND=noninteractive

# Install requirements
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

# Check code style and run tests
RUN pycodestyle . --config=pycodestyle.ini
RUN . /app/make_env.sh && python carbon_friendly_api/manage.py test carbon_friendly_api -v 2
