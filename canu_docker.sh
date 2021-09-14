#!/bin/bash

# check for folder call files
# used to mount data between local and container
if [[ ! -d "files" ]]
then
    mkdir files
fi

# get local path
path=$(pwd)

case $1 in

    up)
        docker-compose up -d --build
        echo ""
        echo "The folder ${path}/files"
        echo "is mounted on the container at /files"
        echo ""
    ;;

    down)
        docker-compose down
    ;;

    *)
        echo ""
        echo "canu_docker.sh usuage is:"
        echo "canu_docker.sh up - for starting container"
        echo "canu_docker.sh down - for stopping container"
        echo ""
    ;;
esac