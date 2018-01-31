FROM python

WORKDIR /web
ADD . /web
RUN pip3 install -r requirements.txt
EXPOSE 5002
CMD ["gunicorn", "--config=gunicorn.py", "initialization:app"]
