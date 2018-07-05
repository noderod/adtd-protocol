#!/bin/bash


# Checks the installation of docker and nvidia-docker
docker_command=$(docker)
nvdock=$(nvidia-docker)

if [ "$docker_command" = *"command not found"* ]; then
    printf "Failed installation, docker is not installed\n"
    exit 0
fi

if [ "$nvdock" = *"command not found"* ]; then
    printf "Failed installation, nvidia-docker is not installed\n"
    exit 0
fi



apt-get update -y
apt-get install redis-server -y
redis-server --port 6389 &

pip3 install docker requests redis


chmod +x $PWD/work_checker.py
chmod +x $PWD/work_processor.py


# Sets up the necessary connections
python3 server-connect.py


# Adds the installation location
export adtd_install=$PWD/
printf "\nexport adtd_install=$PWD/\n" >> "$HOME/.bashrc"

