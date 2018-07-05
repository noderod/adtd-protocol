"""
BASICS

Ensures that the server is adtd-p able
Also useful to swicth servers
"""

import requests
import redis
import os, sys

r = redis.Redis(host = '0.0.0.0', port = 6389, db = 10)


server_IP = str(input("Enter server IP: "))
server_port = str(input("Enter server port: "))

resp = requests.get("http://"+server_IP+':'+server_port+"/boincserver/v2/api/adtdp_server")

if resp.text != "Server is ADTDP able":
    print("Server is not connected, unable to receive jobs")
    sys.exit()


# Sets the values
r.set("server IP", server_IP)
r.set("server port", server_port)
r.set("file loc", os.environ['adtd_install'])

print("Server "+server_IP+":"+server_port+" is now available for adtd-p")
