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
       apk add -Uv --no-cache \
          bash \
          ca-certificates \
          curl \
          libmagic \
          postgresql-libs \
          pwgen \
    && apk add --no-cache --virtual=.build-deps \
          gcc \
          linux-headers \
          musl-dev \
          postgresql-dev \
          tar \
          xz

ARG FFMPEG_CHANNEL=release
ARG FFMPEG_URL=https://johnvansickle.com/ffmpeg/releases/ffmpeg-${FFMPEG_CHANNEL}-64bit-static.tar.xz
ARG FFMPEG_MD5=d027382742314ed2ea03551c802c1369
RUN set -ex; \
       cd /usr/src \
    && curl -fSL -o ffmpeg.tar.xz "${FFMPEG_URL}" \
    && echo "${FFMPEG_MD5}  ffmpeg.tar.xz" | md5sum -c \
    && tar -xf ffmpeg.tar.xz  -C /usr/local/bin --strip=1 --no-anchored ffmpeg \
    && rm -f /usr/src/ffmpeg.tar.xz

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
           mkdir -p "${APP_DIR}/ui"; \
           cp -pR docker/Jamstash/dist/* "${APP_DIR}/ui"; \
       fi \
    && rm -rf /usr/src/unsonic /home/unsonic

# add 'unsonic' user
RUN set -ex; \
       apk add --no-cache shadow \
    && useradd -m unsonic -d "${HOME}" -u 6543 \
    && apk del shadow \
    && mkdir -p ${APP_DIR}/var/log \
    && chown -R unsonic:unsonic "${APP_DIR}/var"

# cleanup
RUN set -ex; rm -rf /var/cache/apk/*

WORKDIR ${APP_DIR}
VOLUME ${APP_DIR}/var

CMD ["/unsonic/bin/unsonic-init"]
COPY docker/unsonic-init ${APP_DIR}/bin/
COPY docker/config.ini ${APP_DIR}/etc/config.ini

