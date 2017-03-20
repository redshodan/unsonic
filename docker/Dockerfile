FROM greyltc/archlinux
MAINTAINER Travis Shirk <travis@pobox.com>

EXPOSE 6543

RUN curl -o /etc/pacman.d/mirrorlist \
            "https://www.archlinux.org/mirrorlist/?country=US&protocol=https&use_mirror_status=on" && \
    sed -i 's/^#//' /etc/pacman.d/mirrorlist
RUN pacman -Syu --noconfirm
RUN pacman -S --noconfirm python python-virtualenv python-pip \
                          postgresql-libs python-psycopg2 git

ENV HOME=/home/unsonic \
    APP_DIR=/unsonic

# Default is SQLite but can be overridden.
ARG MISHMASH_DBURL=sqlite:///${APP_DIR}/var/music.db
ENV MISHMASH_DBURL=${MISHMASH_DBURL} \
    UNSONIC_CONFIG=${APP_DIR}/etc/config.ini

RUN useradd -m unsonic -d ${HOME} -u 6543
RUN echo "source ${APP_DIR}/bin/activate" >> ${HOME}/.bashrc && \
    echo "alias ll='ls -l'" >> ${HOME}/.bashrc

RUN mkdir -p ${APP_DIR} && chown unsonic:unsonic ${APP_DIR}
WORKDIR $APP_DIR
CMD ["/unsonic/bin/unsonic-init"]

USER unsonic
ENV LANG en_US.UTF-8

RUN mkdir -p ${APP_DIR}/etc ${APP_DIR}/var/log && \
    virtualenv ${APP_DIR}

RUN source ${APP_DIR}/bin/activate && \
    pip install git+https://github.com/redshodan/unsonic.git
#RUN source ${APP_DIR}/bin/activate && \
#    pip install unsonic

COPY unsonic-init ${APP_DIR}/bin/
COPY config.ini ${APP_DIR}/etc/config.ini
#CMD ["/bin/bash"]
