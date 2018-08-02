#!/usr/bin/env python3

"""
BASICS


Checks if there is any available work to be processed
If there is, it creates a new entry on the Redis database
"""

import requests
import redis
import sys
import datetime
import json


r_ser = redis.Redis(host='0.0.0.0', port=6389,db=10)
r_dat = redis.Redis(host='0.0.0.0', port=6389,db=1)

server_route = r_ser.get("server IP").decode("UTF-8")+':'+r_ser.get("server port").decode("UTF-8")

# Checks if there are any jobs available
jobs_ava = requests.get("http://"+server_route+"/boincserver/v2/api/available_adtdp").text.split(', ')

if jobs_ava[0] == "No jobs available":
	print("No jobs available")
    sys.exit()


gpu_able = r_ser.get("gpu able").decode("UTF-8")
# Checks the job database one by one
# Adds the first  job which the system can run

for wid in jobs_ava:

    resp = requests.get("http://"+server_route+"/boincserver/v2/api/adtdp/info/"+wid)
    jdat = json.loads(resp.text)

    if (jdat["GPU"] == "True") and (gpu_able == "n"):
        continue


    prestime = prestime = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    # Adds the job to the database of jobs left to do
    r_dat.set(wid, prestime)

    print("Job No. "+wid)
