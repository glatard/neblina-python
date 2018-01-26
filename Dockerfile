FROM ubuntu:14.04

RUN apt-get update
ADD . /usr/local/neblina-python
RUN apt-get install -y python3-setuptools
RUN easy_install3 pip
