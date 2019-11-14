FROM s390x/nginx
FROM python:3.7
USER root
WORKDIR /

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       mariadb-client \
       vim \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip \
    && pip install psycopg2 \
    && pip install uwsgi
COPY . /RechteDB
WORKDIR /RechteDB
RUN pip3 install -r requirements.txt

CMD ["python", "manage.py", "makemigrations"]
CMD ["python", "manage.py", "migrate"]

EXPOSE 8000
CMD ["uwsgi", "--ini", "uwsgi.ini"]