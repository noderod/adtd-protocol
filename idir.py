#!/usr/bin/env python3

"""
BASICS

Removes all stopped containers and images older than 4h. Designed to aboid filling the system's disk space with user's images.
Since user's will have already received their images in a tar file, no data will be lost.
Designed to be run as a cron job, but it can also be done manually
"""


import docker
import redis
import datetime
import sys


# Database for keeping deleted images and the time of doing so
r9 = redis.Redis(host='0.0.0.0', port = 6389, db=9)


client = docker.from_env()
image = client.images
container = client.containers


all_images = [y.short_id.split(':')[1] for y in image.list()]
all_containers = [z.short_id for z in container.list()]


# Obtains the time when an image was created
def Image_creation_time(IMTAG):

    ptim = image.get(IMTAG).attrs['Created'].replace("T", ' ').split('.')[0]

    return datetime.datetime.strptime(ptim, "%Y-%m-%d %H:%M:%S")


# Checks if an image was created more than 4 hours ago
# creation_time (datetime obj.): Time when the image was created
def image_older_4h(IMTAG):

    if (datetime.datetime.utcnow() - Image_creation_time(IMTAG)).total_seconds() > (4*3600):
        return True

    return False

def container_older_4h(CONTAG):
    contim = container.get(CONTAG).attrs['Created'].replace("T", ' ').split('.')[0]
    contim_dateObj = datetime.datetime.strptime(contim, "%Y-%m-%d %H:%M:%S")

    if (datetime.datetime.utcnow() - contim_dateObj).total_seconds() > (4*3600):
        return True

    return False

# Stops all containers older than 4 hours
container_to_be_stopped = [fg for fg in all_containers if container_older_4h(fg)]
for contan in container_to_be_stopped:
    container.get(contan).kill()



# Removes all exited containers
container.prune()

# Checks if there are any images due to be deleted
to_be_deleted = [w for w in all_images if image_older_4h(w)]

if len(to_be_deleted) == 0:
    print("No new MIDAS images")
    sys.exit()


for imim in to_be_deleted:

    try:
        image.remove(image=imim, force=True)
    except:
        # Not all images will be able to be deleted
        continue
    r9.set(imim, datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"))
