#FROM phusion/baseimage
FROM python

# Install dependency packages
#RUN apt-get clean && apt-get update && apt-get install -y apt-utils python3 python3-dev python3-pip build-essential python3-nose libpq-dev

WORKDIR /web
ADD . /web
RUN pip3 install -r requirements.txt
EXPOSE 5000
CMD ["gunicorn", "--config=gunicorn.py", "initialization:app"]
#COPY ./srv/requirements.txt /back/requirements.txt
#COPY ./srv /back
