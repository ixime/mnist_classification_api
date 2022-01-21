From ubuntu:20.04
MAINTAINER ixime

ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8
ENV LANGUAGE=C.UTF-8
ENV LC_CTYPE=C.UTF-8
ENV LC_MESSAGES=C.UTF-8
ENV DEBIAN_FRONTEND noninteractive

ARG NEWUID=1010
ARG NEWGID=1090

RUN set -ex && \
    apt-get update -yq && \
    apt-get upgrade -yq && \
    apt-get install -y software-properties-common \
        apt-utils \
        sudo \
        htop \
        nano \
        gcc \
        libpq-dev \
        python3-pip python3-dev && \
        pip3 --no-cache-dir install --upgrade pip setuptools wheel

RUN groupadd -g ${NEWGID} common_user && \
    useradd -ms /bin/bash -g common_user -u ${NEWUID} -o -c "" -m common_user && \
    echo "common_user ALL=(ALL:ALL) NOPASSWD:ALL" | (EDITOR="tee -a" visudo) && \
    usermod -aG sudo common_user

COPY ./requirements.txt /requirements.txt

RUN pip --no-cache-dir install -r /requirements.txt

RUN apt-get autoremove -yqq --purge \
    && apt-get clean \
    && rm -rf \
        /var/lib/apt/lists/* \
        /tmp/* \
        /var/tmp/* \
        /usr/share/man \
        /usr/share/doc \
        /usr/share/doc-base

RUN mkdir /app
RUN chown -R common_user:common_user /app
WORKDIR /app
COPY ./app /app

RUN mkdir -p /vol/web/media
RUN mkdir -p /vol/web/static

RUN chown -R common_user:common_user /vol/
RUN chmod -R 755 /vol/web

USER common_user
