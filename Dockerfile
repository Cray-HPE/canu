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

FROM artifactory.algol60.net/csm-docker/stable/csm-docker-sle-python:3.10

# create canu user
RUN     useradd -ms /bin/bash canu

# update command prompt
RUN     echo 'export PS1="canu \w : "' >> /etc/bash.bashrc

# make files dir
RUN     mkdir /files

# prep image layer for faster builds
COPY    requirements.txt /app/canu/

RUN     pip3 install -r /app/canu/requirements.txt

# copy canu files
COPY    . /app/canu

# install canu
RUN     pip3 install --editable /app/canu/

# set file perms for canu
RUN     chown -R canu /app/canu /files /home
# set none root user: canu
USER    canu

WORKDIR /files
