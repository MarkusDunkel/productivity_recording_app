FROM python:buster

RUN apt update \
    && mkdir /app/ \
    && apt install -y python3-pip tree vim \
    && pip3 install Django 
    
CMD /bin/bash /app/setup.sh