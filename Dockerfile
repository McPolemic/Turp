FROM ubuntu:latest
MAINTAINER Adam Lukens <spawn968@gmail.com>

RUN apt-get update
RUN apt-get install -y redis-server python-pip
RUN pip install redis honcho simplejson
ADD . /app
WORKDIR /app
CMD ["honcho", "start"]
