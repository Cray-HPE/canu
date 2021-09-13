#!/bin/bash

docker-compose up -d --build
docker exec -it canu /bin/bash