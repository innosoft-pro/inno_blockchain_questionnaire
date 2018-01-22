#FROM jfloff/alpine-python:recent-onbuild
#FROM python:onbuild
FROM python

WORKDIR /bot
ADD . /bot
RUN pip3 install -r requirements.txt
CMD ["python3", "inno_quiz_bot.py"]
