# MIT License
#
# (C) Copyright 2022-2023 Hewlett Packard Enterprise Development LP
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
# STAGE 1
FROM       artifactory.algol60.net/docker.io/library/alpine:3.17 as builder
RUN        apk add --update --no-cache \
             py3-pip \
             gcc \
             openssl \
             jq \
             vim \
             libffi-dev \
             musl-dev \
             python3 \
             python3-dev \
             git
# make canu group, create (system) canu user, add to canu group, make home folder, and set login shell, no password
RUN        addgroup -S canu 
RUN        adduser \
             -S canu \
             -G canu \
             -h /home/canu \
             -s /bin/bash \
             -D
USER       canu
RUN        mkdir -p /home/canu/app/wheels
WORKDIR    /home/canu/app
# copy the source code into the container
COPY       --chown=canu:canu . .
# Install the build dependencies as wheels
ENV        PYTHONDONTWRITEBYTECODE 1
ENV        PYTHONUNBUFFERED 1
RUN        python -m pip install --user -U pyinstaller wheel setuptools
RUN        python -m pip install --user build
RUN        python -m pip --no-cache-dir wheel . '.[build-system]' --wheel-dir wheels/

# STAGE 2
FROM       artifactory.algol60.net/docker.io/library/alpine:3.17 as prod
RUN        apk add --update --no-cache \
              git \
              py3-pip \
              python3 
# add the canu user and group to the prod container
RUN        addgroup -S canu 
RUN        adduser \
             -S canu \
             -G canu \
             -h /home/canu \
             -s /bin/bash \
             -D
USER       canu
WORKDIR    /home/canu/app
# copy the wheels from the builder container
COPY       --chown=canu:canu --from=builder /home/canu/app/wheels /home/canu/app/wheels
COPY       --chown=canu:canu . .
# install using the wheels compiled from stage 1
ENV        PATH "/home/canu/.local/bin:$PATH"
ENV        PYTHONDONTWRITEBYTECODE 1
ENV        PYTHONUNBUFFERED 1
# not all wheels are possible on alpine: https://github.com/pypa/manylinux/issues/37
RUN        python -m pip --no-cache-dir install --user --find-links=wheels/ .
# add a script that installs in editable mode for ad-hoc debugging
RUN        install -m 0755 -o canu -g canu /home/canu/app/canu-debug /home/canu/.local/bin/canu-debug
WORKDIR    /home/canu
ENV        PS1 "canu \w$ "
# env vars for canu-inventory
ENV        CANU_NET "HMN"
ENV        SLS_API_GW "api-gw-service.local"
ENV        SLS_TOKEN ""
ENV        REQUESTS_CA_BUNDLE ""
ENV        SLS_FILE ""
ENV        SWITCH_USERNAME "admin"
ENV        SWITCH_PASSWORD ""
CMD        [ "canu" ]
