# Start with a Python image.
FROM python:latest

# Some stuff that everyone has been copy-pasting
# since the dawn of time.
ENV PYTHONUNBUFFERED 1

RUN apt-get update
RUN apt-get install -y apt-utils python3-dev libmemcached-dev zlib1g-dev libgeos-c1

# Copy all our files into the image.
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY requirements.txt /usr/src/app/
RUN pip install -U pip && pip install -Ur requirements.txt

ADD . /usr/src/app