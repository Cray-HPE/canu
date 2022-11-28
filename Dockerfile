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
ARG     PY_VERSION
ARG     SLE_VERSION
FROM    artifactory.algol60.net/csm-docker/stable/csm-docker-sle-python:${PY_VERSION}-SLES${SLE_VERSION}

# update command prompt
RUN     echo 'export PS1="canu \w : "' >> /etc/bash.bashrc

# make files dir
RUN     mkdir /files

COPY    dist/rpmbuild/RPMS/x86_64/ /files

RUN     ls -l /files && \
        zypper --no-gpg-checks -n in --allow-unsigned-rpm --auto-agree-with-licenses -y /files/canu*.rpm

# set file perms for canu
RUN      chown -R canu /files /home

USER     canu

WORKDIR /files
