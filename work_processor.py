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
import datetime
import subprocess as sbp


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
    tar.close()

    # Gets the data
    with open(file_location+"adtdp.json", "r") as jdat:
        addat = json.load(jdat)

    # Loads the docker image
    ff = open("image.tar.gz", "rb")
    IMG = image.load(ff.read())
    ff.close()

    # Runs the commands in a container
    try:
        P = sbp.Popen("docker run -itd "+str(IMG[0].short_id.split(':')[1]), shell=True, stdout = sbp.PIPE)
        CID = P.communicate()[0].decode("UTF-8")[:12:] # Container ID
        CONTAINER = container.get(CID)
        # CONTAINER = container.run(image = IMG[0].short_id.split(':')[1], command="/bin/bash", detach=True)
    except:

        # Container has failed
        # Send data of failed construction
        Con_Data = {"date (Run)":prestime, "Commands":"Failed container", "Id":tbp}
        r_dat.delete(tbp)
        r_run.hmset(tbp, Con_Data)
        container.prune()
        # Notifies the server
        requests.post("http://"+server_route+"/boincserver/v2/api/adtdp/failed_job", data=[("work_ID", tbp)])
        sys.exit()

    # Runs the commands, keeping track of which succeed and which fail
    all_comms = addat["Command"].split("\"")[1].split(";")
    prestime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    Con_Data = {"date (Run)":prestime, "Commands":[], "Id":tbp}
    comres = [[], []]
    for command in all_comms:
        try:
            RESP = CONTAINER.exec_run("/bin/bash -c \""+command+"\"")
            comres[0].append(command)
            comres[1].append("Success")
        except:
            comres[1].append("Error")

    Con_Data["Commands"] = comres
    # Gets the result
    try:
        RESRES = CONTAINER.get_archive(path=addat["Results"])
    except:
        addat["Result Error"] = "Folder with results does exist"

    with open("Job_Data.json", "w") as jobdat:
        addat["Error"] = "Success"
        addat["Log"] = comres
        json.dump(addat, jobdat)
    with open("Results.tar.gz", "wb") as tarta:
        for bitbit in RESRES[0]:
            tarta.write(bitbit)

    # Because tar files cannot be modified once created, we have to untar the file and then tar it again
    os.mkdir("Process-Tar")
    shutil.move("Job_Data.json", "Process-Tar/Job_Data.json")
    tar = tarfile.open("Results.tar.gz")
    tar.extractall("./Process-Tar")
    tar.close()
    os.chdir("./Process-Tar")
    with tarfile.open("Results.tar.gz", "w:gz") as tar:
        for file in os.listdir("."):
            tar.add(file)

    shutil.move("Results.tar.gz", "../Results.tar.gz")
    os.chdir("..")

    # Uploads the results to the server
    requests.post("http://"+server_route+"/boincserver/v2/api/adtdp/succesful_job", data=[("work_ID", tbp)],
                  files={"resfil": open("Results.tar.gz", "rb")})

    comres = []
    for command in all_comms:
        try:
            RESP = CONTAINER.exec_run("/bin/bash -c \""+command+"\"", detach=True)
            comres.append(RESP)
        except:
            comres.append("Error")

    # Gets the result
    RESRES = CONTAINER.get_archive(path=addat["Results"])
    # Eliminates the container
    CONTAINER = container.get(CID) # Needed because of bugs
    CONTAINER.kill()
    container.prune()

    # Deletes the temporary files
    r_dat.delete(tbp)
    r_run.hmset(tbp, Con_Data) # Keeps a log of run jobs
    shutil.rmtree("./Process-Tar")
