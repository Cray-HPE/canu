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
ARG         ALPINE_VERSION="3.17"
FROM        ${ALPINE_IMAGE}:${ALPINE_VERSION} AS deps
ARG         PYTHON_VERSION='3.10'
# hadolint ignore=DL3002
USER        root
WORKDIR     /root
ENV         PYTHON_VERSION=${PYTHON_VERSION}
# To use the virtualenv, all that is needed are these two vars
# The 'activate' command is not even necessary
# Since ENVs can transfer beween layers, the virtualenv can always be in use
ENV         VIRTUAL_ENV=/opt/venv
ENV         PATH="$VIRTUAL_ENV/bin:$PATH"
RUN         apk add --no-cache \
              cmake~=3.24 \
              g++~=12.2 \
              gcc~=12.2 \
              git~=2.38 \
              libffi-dev~=3.4 \
              make~=4.3 \
              musl-dev~=1.2 \
              openssl~=3.0 \
              py3-pip~=22.3 \
              py3-virtualenv~=20.16 \
              py3-wheel~=0.38 \
              python3~=${PYTHON_VERSION} \
              python3-dev~=${PYTHON_VERSION}


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
            PATH="$VIRTUAL_ENV/bin:$PATH"
# Create the virtualenv and install ansible
RUN         python -m venv $VIRTUAL_ENV
# hadolint ignore=DL3059
RUN         PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 python -m pip install --no-cache-dir ansible~=7.3.0
# hadolint ignore=DL3059
RUN         PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 python -m pip install --no-cache-dir -r https://raw.githubusercontent.com/aruba/aoscx-ansible-collection/a2ee40a937d8d6da1740adca434cbb59b04011d0/requirements.txt
# hadolint ignore=DL3059
RUN         ansible-galaxy collection install --no-cache --no-deps arubanetworks.aoscx


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
            SSH_AUTH_SOCK=/ssh-agent
ENV         PATH="$VIRTUAL_ENV/bin:$PATH"
COPY        --from=ansible $VIRTUAL_ENV $VIRTUAL_ENV
RUN         apk --no-cache add \
              openssh-client~=9.1
COPY        .flake8 ./.flake8
COPY        .git/ ./.git
COPY        .darglint ./.darglint
COPY        canu/ ./canu
COPY        docs/ ./docs
COPY        network_modeling/ ./network_modeling
COPY        pyinstaller_hooks/ ./pyinstaller_hooks
COPY        tests/ ./tests
COPY        canu.spec ./canu.spec
COPY        canuctl ./canuctl
COPY        Dockerfile ./Dockerfile
COPY        entry_points.ini ./entry_points.ini
COPY        LICENSE ./LICENSE
COPY        Makefile ./Makefile
COPY        MANIFEST.in ./MANIFEST.in
COPY        mkdocs.yml ./mkdocs.yml
COPY        noxfile.py ./noxfile.py
COPY        pyinstaller.py ./pyinstaller.py
COPY        pyproject.toml ./pyproject.toml
RUN         PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 python -m pip install --no-cache-dir --editable '.[ci,docs]'
# hadolint ignore=DL3059
RUN         nox -e docs

##########################
#
# STAGE 3 - documentation image
#
##########################
FROM        ${ALPINE_IMAGE}:${ALPINE_VERSION} AS docs
ARG         PYTHON_VERSION='3.10'
USER        root
WORKDIR     /root
ENV         VIRTUAL_ENV=/opt/venv
ENV         PATH="$VIRTUAL_ENV/bin:$PATH"
# hadolint ignore=SC2086
RUN         apk add --no-cache \
              py3-pip~=22.3 \
              py3-virtualenv~=20.16 \
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
ENV         VIRTUAL_ENV=/opt/venv
ENV         PATH="$VIRTUAL_ENV/bin:$PATH"
# Get the canu installation files
COPY        --from=dev /root /root
WORKDIR     /root
# install canu in prod mode so the canu user can use it in the final image
RUN         PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 pip install --no-cache-dir .

##########################
#
# STAGE 6 - final production image
#
##########################
FROM        ${ALPINE_IMAGE}:${ALPINE_VERSION} AS prod
ARG         PYTHON_VERSION='3.10'
USER        root
WORKDIR     /root
ENV         VIRTUAL_ENV=/opt/venv
ENV         PATH=$VIRTUAL_ENV/bin:$PATH
RUN         apk --no-cache add \
              py3-pip~=22.3 \
              py3-virtualenv~=20.16 \
              python3~=${PYTHON_VERSION} \
              python3-dev~=${PYTHON_VERSION} \
              openssh-client~=9.1
#           must mount ${SSH_AUTH_SOCK} to /ssh-agent to use host ssh
ENV         SSH_AUTH_SOCK=/ssh-agent
RUN         addgroup -S canu && \
              adduser \
              -S canu \
              -G canu \
              -h /home/canu \
              -s /bin/bash \
              -D
USER        canu
WORKDIR     /home/canu
# get the virtualenv with only ansible and collections installed
# if it is installed from the dev stage, things are owned by root in editable mode and is not useable
COPY        --from=prod_build --chown=canu:canu $VIRTUAL_ENV $VIRTUAL_ENV
COPY        --from=ansible --chown=canu:canu /root/.ansible /home/canu/.ansible
# hadolint ignore=DL3059
RUN         echo PS1="'canu \w$ '" >> /home/canu/.profile
# hadolint ignore=DL3059
RUN         mkdir -p /home/canu/mounted
ENV         CANU_NET=HMN \
            KUBECONFIG=/etc/kubernetes/admin.conf \
            PS1="canu \w$ " \
            REQUESTS_CA_BUNDLE="" \
            SLS_API_GW=api-gw-service.local \
            SLS_FILE="" \
            SLS_TOKEN="" \
            SSH_AUTH_SOCK=/ssh-agent \
            SWITCH_USERNAME=admin \
            SWITCH_PASSWORD=""
CMD         [ "sh", "-l" ]
