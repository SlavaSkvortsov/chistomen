FROM python:3

ADD req.txt /requirements.txt

#RUN apt-get install libpq-dev libcurl4-openssl-dev libjpeg8-dev zlib1g-dev libfreetype6-dev

RUN pip install -r requirements.txt

RUN mkdir /code/
WORKDIR /code/
ADD . /code/

RUN pip install gunicorn

ADD chistomen/local_settings.py /code/chistomen/settings_local.py

EXPOSE 8000

CMD ["gunicorn", "--workers", "4", "--timeout", "600", "--bind", "0.0.0.0:8000", "chistomen.wsgi"]