#FROM phusion/baseimage
#FROM jfloff/alpine-python:recent-onbuild
#FROM python:onbuild
FROM python
#FROM python:3

# Install dependency packages
#RUN apt-get clean && apt-get update && apt-get install -y apt-utils python3 python3-dev python3-pip build-essential python3-nose libpq-dev

WORKDIR /bot
ADD . /bot
RUN pip3 install -r requirements.txt
CMD ["python3", "inno_quiz_bot.py"]
#COPY ./bot/requirements.txt /bot/requirements.txt
#RUN pip3 install -r requirements.txt
#COPY ./bot /bot
