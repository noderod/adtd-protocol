#!/bin/bash


# Checks docker installation
docker_command=$(docker --version)

if [ "$docker_command" = *"not installed"* ]; then
    printf "Failed installation, docker is not installed\n"
    exit 0
fi



apt-get update -y
apt-get install redis-server python3 python3-pip -y
redis-server --port 6389 &

pip3 install docker requests redis


chmod +x ./work_checker.py
chmod +x ./work_processor.py

# Sets up the necessary connections
python3 server-connect.py

# Deletes unnecessary images and containers every hour
crontab -l | { cat; echo "0 * * * * $PWD/idir.py"; } | crontab -

rm -- "$0"
