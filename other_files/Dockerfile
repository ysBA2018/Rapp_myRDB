FROM s390x/nginx:python3.7
USER root
WORKDIR /RechteDB

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       mysql-client \
       vim \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --upgrade pip \
    && pip install psycopg2 \
    && pip install uwsgi

COPY requirements.txt /RechteDB/requirements.txt
RUN pip install -r requirements.txt

COPY . /RechteDB
EXPOSE 8000
CMD ["uwsgi", "--ini", "uwsgi.ini"]
