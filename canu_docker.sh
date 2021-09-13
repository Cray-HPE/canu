#!/bin/bash

# check for folder call files
# used to mount data between local and container
if [[ ! -d "files" ]]
then
    mkdir files
fi

if [[ "$1" == "up" ]]; then
    docker-compose up -d --build
    docker exec -it canu /bin/bash
fi

if [[ "$1" == "down" ]]; then
    docker-compose down
fi

if [[ "$1" != "up" ]] || [[ "$1" != "up" ]]; then
    echo "usuage is:"
    echo "canu_docker.sh up - for starting container"
    echo "canu_docker.sh down - for stopping container"
fi