from opensuse/leap:15.3

# create canu user
RUN useradd -u 1001 -m canu -d /home/canu

# update command prompt
RUN echo 'export PS1="canu \w : "' >> /etc/bash.bashrc

# prep image layer for faster builds
COPY requirements.txt /app/canu/
RUN zypper -n install python3 python3-pip vim
RUN pip3 install -r /app/canu/requirements.txt

# copy canu files
COPY . /app/canu

# install canu
RUN pip3 install --editable /app/canu/

# set file perms for canu
RUN chown -R canu /app/canu

# set none root user: canu
USER canu

WORKDIR /app/canu