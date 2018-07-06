#!/usr/bin/env python3

"""
BASICS

Processes all the jobs received by this server
"""

import requests
import redis
import docker
import tarfile
import json
import os, shutil, sys


r_ser = redis.Redis(host='0.0.0.0', port=6389,db=10)
r_dat = redis.Redis(host='0.0.0.0', port=6389,db=1)
r_run = redis.Redis(host='0.0.0.0', port=6389,db=0)
image =docker.from_env().images
container =  docker.from_env().containers

server_route = r_ser.get("server IP").decode("UTF-8")+':'+r_ser.get("server port").decode("UTF-8")

# Obtains all the jobs to be processed
to_be_processed = [z.decode("UTF-8") for z in r_dat.keys()]

if len(to_be_processed) == 0:
    sys.exit()

file_location = r_ser.get("file loc").decode("UTF-8")

os.chdir(file_location)

for tbp in to_be_processed:

    # Downloads the files in the current directory

    star = requests.post("http://"+server_route+"/boincserver/v2/api/adtdp/request_work", data=[("work_ID", tbp)], stream=True)
    with open(file_location+"all_data.tar.gz", 'wb') as f:
        shutil.copyfileobj(star.raw, f)

    # There is always the same files, so we extract both and delete the main one
    tar = tarfile.open("all_data.tar.gz")
    tar.extractall()
    os.remove("all_data.tar.gz")

    # Gets the data
    with open(file_location+"adtdp.json", "r") as jdat:
        addat = json.load(jdat)

    # Loads the docker image
    ff = open("image.tar.gz", "rb")
    IMG = image.load(ff.read())
    ff.close()

    # Runs the commands in a container
    try:
        CONTAINER = container.run(image = IMG[0].short_id.split(':')[1], command="/bin/bash", detach=True)
    except:

        # Container has failed
        # Send data of failed construction
        pass 
        # TODO TODO TODO

    # Starts the container
    CONTAINER.start()
    all_comms = addat["Command"].split("\"")[1].split(";")


    # Deletes the temporary files

