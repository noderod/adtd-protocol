#!/bin/bash


# Checks docker installation
docker_command=$(docker --version)

if [ "$docker_command" = *"command not found"* ]; then
    printf "Failed installation, docker is not installed\n"
    exit 0
fi



apt-get update -y
apt-get install redis-server -y
redis-server --port 6389 &

pip3 install docker requests redis


chmod +x $PWD/work_checker.py
chmod +x $PWD/work_processor.py
export adtd_install=$PWD
adtd_install=$PWD/
printf "\nexport adtd_install=$PWD/\n" >> "$HOME/.bashrc"
printf "\nexport adtd_install=$PWD/\n" >> "$/root/.bashrc"

# Sets up the necessary connections
python3 server-connect.py

# Deletes unnecessary images and containers every hour
crontab -l | { cat; echo "0 * * * * $adtd_install/idir.py"; } | crontab -

rm -- "$0"
