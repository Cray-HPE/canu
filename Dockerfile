# MIT License
#
# (C) Copyright [2022] Hewlett Packard Enterprise Development LP
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

# Stage 1 Create wheels for dependencies
FROM       artifactory.algol60.net/docker.io/library/alpine:3.17 as wheels_builder

# set environment variables to avoid py cache files
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

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


# make canu group
RUN        addgroup -S canu 

# create (system) canu user, add to canu group, make home folder, and set login shell, no password
RUN        adduser \
             -S canu \
             -G canu \
             -h /home/canu \
             -s /bin/bash \
             -D

RUN        mkdir /wheels

COPY       . /source

# set file perms for canu
RUN        chown -R canu /source /wheels

# set rootless user: canu
USER       canu

WORKDIR    /source

RUN        pip --no-cache-dir install --upgrade pip wheel setuptools && pip --no-cache-dir wheel . --wheel-dir=/wheels


# Stage 2 Build the final image without build depoendencies
FROM       artifactory.algol60.net/docker.io/library/alpine:3.17 as prod

# set environment variables to avoid py cache files
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# In order to volume mount the CA certs file, we need to create the directory and file
# othwerwise the volume mount will mount the file as a directory
# Since this is an empty file and not a valid cert bundle, the inventory script will fail without the volume mount
RUN        mkdir -p /etc/pki/trust/anchors/
RUN        touch /etc/pki/trust/anchors/platform-ca-certs.crt

# Git it still used in find_version() in setup.py
RUN        apk add --update --no-cache git py3-pip

COPY       . /source

COPY       --from=wheels_builder /wheels /tmp/wheels

# make canu group
RUN        addgroup -S canu 

# create (system) canu user, add to canu group, make home folder, and set login shell, no password
RUN        adduser \
             -S canu \
             -G canu \
             -h /home/canu \
             -s /bin/bash \
             -D

WORKDIR    /source

RUN        pip --no-cache-dir install --no-index --find-links=/tmp/wheels .

RUN        rm -rf /tmp/wheels
RUN        rm -rf /source
# set rootless user: canu
USER       canu

WORKDIR    /home/canu

# update command prompt
RUN        echo 'export PS1="canu \w : "' >> /home/canu/bash.bashrc

# The gateway and token are needed to connect to the SLS API
ENV        SLS_API_GW "api-gw-service.local"
ENV        SLS_TOKEN ""
# canu-inventory will use TOKEN as well if SLS_TOKEN is not set
ENV        TOKEN ""

# The path to the CA certs file is needed for a secure connection
# this should be volume mounted into the container: '-v /absolute_path/to/local.crt:/etc/pki/trust/anchors/platform-ca-certs.crt'
ENV        REQUESTS_CA_BUNDLE "/etc/pki/trust/anchors/platform-ca-certs.crt"

# These do not do anything in terms of connecting to the inventory, but they add the credentials to the dynamic inventory, which ansible then can use
ENV        SWITCH_USERNAME "admin"
ENV        SWITCH_PASSWORD ""

# override '--entrypoint canu-inventory' for use with ansible
ENTRYPOINT [ "canu" ]
