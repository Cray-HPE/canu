from opensuse/leap:15.3

COPY . /app/canu
RUN zypper -n install python3 python3-pip
RUN pip3 install -r /app/canu/requirements.txt
RUN pip3 install --editable /app/canu/
