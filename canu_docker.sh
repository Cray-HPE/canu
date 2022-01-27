#!/bin/bash
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

if [[ ! -d "files" ]]
then
    echo 'Making local directory for Docker volume.'
    mkdir -v files
fi

path=$(pwd)

case $1 in

    up)
        docker-compose up -d --build
        echo ""
        echo "The folder ${path}/files"
        echo "is mounted on the container at /files"
        echo ""
        echo "Type exit to disconnect from container before trying to shutdown the container"
        echo ""
        docker exec -it canu /bin/bash
    ;;

    down)
        docker-compose down
    ;;

    *)
        echo ""
        echo "$0 usage is:"
        echo "$0 up   - for starting container"
        echo "$0 down - for stopping container"
        echo ""
    ;;
esac
