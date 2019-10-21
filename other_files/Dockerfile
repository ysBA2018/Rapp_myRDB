FROM s390x/nginx
FROM python:3.7
USER root
WORKDIR /RechteDB

RUN apt-get update \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get install -y \
       mysql-client \
       vim \
RUN pip install --upgrade pip \
    && pip install psycopg2 \
    && pip install uwsgi

COPY requirements.txt /RechteDB/requirements.txt
RUN pip install -r requirements.txt

COPY . /RechteDB
EXPOSE 8000
CMD ["uwsgi", "--ini", "uwsgi.ini"]
