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
##########################
#
# STAGE 1 - install build dependencies
#
##########################
ARG         ALPINE_IMAGE="artifactory.algol60.net/docker.io/library/alpine"
ARG         ALPINE_VERSION="3.20"
FROM        ${ALPINE_IMAGE}:${ALPINE_VERSION} AS deps
ARG         PYTHON_VERSION='3.12'
# hadolint ignore=DL3002
USER        root
WORKDIR     /root
# To use the virtualenv, all that is needed are these two vars
# The 'activate' command is not even necessary
# Since ENVs can transfer beween layers, the virtualenv can always be in use
ENV         PYTHON_VERSION=${PYTHON_VERSION} \
            VIRTUAL_ENV=/opt/venv

# Must be set by itself or it won't stick around when the container runs.
ENV         PATH="$VIRTUAL_ENV/bin:$PATH"
RUN         apk add --no-cache \
              bash \
              cmake \
              g++ \
              gcc \
              git \
              libffi-dev \
              libssh-dev \
              make \
              musl-dev \
              openssl-dev \
              py3-pip \
              py3-virtualenv \
              py3-wheel \
              python3~=${PYTHON_VERSION} \
              python3-dev~=${PYTHON_VERSION}

COPY        .darglint ./.darglint
COPY        .flake8 ./.flake8
COPY        .git/ ./.git
COPY        Dockerfile ./Dockerfile
COPY        LICENSE ./LICENSE
COPY        MANIFEST.in ./MANIFEST.in
COPY        Makefile ./Makefile
COPY        README.md ./README.md
COPY        canu/ ./canu
COPY        canuctl ./canuctl
COPY        docs/ ./docs
COPY        entry_points.ini ./entry_points.ini
COPY        mkdocs.yml ./mkdocs.yml
COPY        network_modeling/ ./network_modeling
COPY        noxfile.py ./noxfile.py
COPY        pyinstaller.py ./pyinstaller.py
COPY        pyinstaller_hooks/ ./pyinstaller_hooks
COPY        pyproject.toml ./pyproject.toml
COPY        tests/ ./tests

##########################
#
# STAGE 2 - install ansible and collections
#
##########################
FROM        deps AS ansible
# hadolint ignore=DL3002
USER        root
WORKDIR     /root
# These two vars are all that is needed to use the virtualenv
ENV         VIRTUAL_ENV=/opt/venv \
            PYTHONDONTWRITEBYTECODE=1 \
            PYTHONUNBUFFERED=1

# Must be set by itself or it won't stick around when the container runs.
ENV         PATH="$VIRTUAL_ENV/bin:$PATH"

# Create the virtualenv and install ansible
RUN         python -m venv $VIRTUAL_ENV
# hadolint ignore=DL3059
RUN         python -m pip install --no-cache-dir ansible
# hadolint ignore=DL3059
RUN         python -m pip install --no-cache-dir --no-binary ansible-pylibssh ansible
# hadolint ignore=DL3059
RUN         python -m pip install --no-cache-dir -r https://raw.githubusercontent.com/aruba/aoscx-ansible-collection/master/requirements.txt
# hadolint ignore=DL3059
RUN         ansible-galaxy collection install arubanetworks.aoscx

##########################
#
# STAGE 3 - install canu in editable mode and generate docs
#
##########################
FROM        ansible AS dev
# hadolint ignore=DL3002
USER        root
WORKDIR     /root
#           must mount ${SSH_AUTH_SOCK} to /ssh-agent to use host ssh
RUN         mkdir -p /root/mounted
ENV         VIRTUAL_ENV=/opt/venv \
            SSH_AUTH_SOCK=/ssh-agent \
            PYTHONDONTWRITEBYTECODE=1 \
            PYTHONUNBUFFERED=1

ENV         PATH="$VIRTUAL_ENV/bin:$PATH"
COPY        --from=ansible $VIRTUAL_ENV $VIRTUAL_ENV
RUN         apk --no-cache add \
              openssh-client
RUN         python -m pip install --no-cache-dir --editable '.[docs]'
# hadolint ignore=DL3059
RUN         sphinx-build -M markdown docs/templates docs/_build -a

##########################
#
# STAGE 3 - documentation image
#
##########################
ARG         ALPINE_IMAGE="artifactory.algol60.net/docker.io/library/alpine"
ARG         ALPINE_VERSION="3.20"
FROM        ${ALPINE_IMAGE}:${ALPINE_VERSION} AS docs
ARG         PYTHON_VERSION='3.12'
USER        root
WORKDIR     /root
ENV         VIRTUAL_ENV=/opt/venv

# Must be set by itself or it won't stick around when the container runs.
ENV          PATH="$VIRTUAL_ENV/bin:$PATH"

# hadolint ignore=SC2086
RUN         apk add --no-cache \
              py3-pip \
              py3-virtualenv \
              python3~=${PYTHON_VERSION} \
              python3-dev~=${PYTHON_VERSION}

# The dev stage has the docs built and has mkdocs installed
COPY        --from=dev --chown=root:root $VIRTUAL_ENV $VIRTUAL_ENV
# Since this is an end-user image, it will run rootless
RUN         addgroup -S canu && \
              adduser \
              -S canu \
              -G canu \
              -h /home/canu \
              -s /bin/bash \
              -D
USER        canu
WORKDIR     /home/canu
# Copy just the generated docs and the config file
COPY        --from=dev --chown=canu:canu /root/docs /home/canu/docs
COPY        --from=dev --chown=canu:canu /root/mkdocs.yml /home/canu/mkdocs.yml
EXPOSE      8000
CMD         [ "mkdocs", "serve", "-a", "0.0.0.0:8000", "--config-file", "mkdocs.yml"]

##########################
#
# STAGE 5 - production build image
#
##########################
FROM        ansible AS prod_build
USER        root
ENV         VIRTUAL_ENV=/opt/venv \
            PYTHONDONTWRITEBYTECODE=1 \
            PYTHONUNBUFFERED=1

# Must be set by itself or it won't stick around when the container runs.
ENV         PATH="$VIRTUAL_ENV/bin:$PATH"

# Get the canu installation files
COPY        --from=ansible /root /root
WORKDIR     /root

# install canu in prod mode so the canu user can use it in the final image
RUN         pip install --no-cache-dir .

##########################
#
# STAGE 6 - final production image
#
##########################
ARG         ALPINE_IMAGE="artifactory.algol60.net/docker.io/library/alpine"
ARG         ALPINE_VERSION="3.20"
FROM        ${ALPINE_IMAGE}:${ALPINE_VERSION} AS prod
ARG         PYTHON_VERSION='3.12'
USER        root
WORKDIR     /root

#           must mount ${SSH_AUTH_SOCK} to /ssh-agent to use host ssh
RUN         apk --no-cache add \
              bash \
              py3-pip \
              py3-virtualenv \
              python3~=${PYTHON_VERSION} \
              python3-dev~=${PYTHON_VERSION} \
              openssh-client

RUN         addgroup -S canu \
            && adduser \
              -S canu \
              -G canu \
              -h /home/canu \
              -s /bin/bash \
              -D

USER        canu
WORKDIR     /home/canu
ENV         VIRTUAL_ENV=/opt/venv \
            SSH_AUTH_SOCK=/ssh-agent \
            CANU_NET=HMN \
            KUBECONFIG=/etc/kubernetes/admin.conf \
            PS1="canu \w$ " \
            REQUESTS_CA_BUNDLE="" \
            SLS_API_GW=api-gw-service.local \
            SLS_FILE="" \
            SLS_TOKEN="" \
            SSH_AUTH_SOCK=/ssh-agent \
            SWITCH_USERNAME=admin \
            SWITCH_PASSWORD=""

# Must be set by itself or it won't stick around when the container runs.
ENV         PATH=$VIRTUAL_ENV/bin:$PATH

RUN         echo PS1="${PS1}" >> /home/canu/.profile \
            && mkdir -p /home/canu/mounted

# get the virtualenv with only ansible and collections installed
# if it is installed from the dev stage, things are owned by root in editable mode and is not useable
COPY        --from=prod_build --chown=canu:canu $VIRTUAL_ENV $VIRTUAL_ENV
COPY        --from=ansible --chown=canu:canu /root/.ansible /home/canu/.ansible

CMD         [ "sh", "-l" ]
