# Start with a Python image.
FROM python:latest

# Some stuff that everyone has been copy-pasting
# since the dawn of time.
ENV PYTHONUNBUFFERED 1

RUN apt-get install -y libgeos-c1

# Copy all our files into the image.
RUN mkdir /code
WORKDIR /code
ADD . /code/
