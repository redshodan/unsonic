FROM python:3.6-alpine3.7
MAINTAINER Ben Schumacher <me@benschumacher.com>

ENV HOME=/home/unsonic \
    APP_DIR=/unsonic \
    LANG=en_US.UTF-8

# Default is SQLite but can be overridden.
ARG MISHMASH_DBURL=sqlite:///${APP_DIR}/var/music.db
ENV MISHMASH_DBURL=${MISHMASH_DBURL} \
    UNSONIC_CONFIG=${APP_DIR}/etc/config.ini

RUN set -ex; \
       apk add --no-cache \
          bash \
          ca-certificates \
          curl \
          libmagic \
          postgresql-libs \
          pwgen \
    && apk add --no-cache --virtual=.build-deps \
          gcc \
          linux-headers \
          postgresql-dev \
          musl-dev

COPY requirements.txt /usr/src/unsonic/
WORKDIR /usr/src/unsonic
RUN set -ex; \
       pip3 install -r requirements.txt

COPY . /usr/src/unsonic/
RUN set -ex; \
       python3 setup.py build \
    && python3 setup.py install --prefix=/usr/local \
    && apk del .build-deps \
    && if [ -d docker/Jamstash/dist ]; then \
           mkdir -p ${APP_DIR}/ui; \
           cp -pR docker/Jamstash/dist/* ${APP_DIR}/ui; \
       fi \
    && rm -rf /usr/src/unsonic /home/unsonic

#RUN set -ex; \
#       apk add --no-cache shadow \
#    && useradd -m unsonic -d ${HOME} -u 6543 \
#    && apk del shadow \
#    && mkdir -p ${APP_DIR}/var/log \
#    && chown -R unsonic:unsonic ${APP_DIR}/var \

RUN set -ex; rm -vrf /var/cache/apk/*

#USER unsonic
WORKDIR ${APP_DIR}
VOLUME ${APP_DIR}/var

CMD ["/unsonic/bin/unsonic-init"]
COPY docker/unsonic-init ${APP_DIR}/bin/
COPY docker/config.ini ${APP_DIR}/etc/config.ini

