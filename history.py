#!/usr/bin/env python3

"""
BASICS

Used to check the job history of this device
"""

import redis
import sys


r = redis.Redis(host='0.0.0.0', port=6389,db=0)


# Splits a set of strings into simpler mini-strings, each 20 chars long
# The string is preceded and followed by an space
# sst (arr) (str): List of strings
def manageable_string(sst):


    s2 = sst

    for item, nvnv in zip(sst, range(0, len(sst))):
        ll = len(item)

        mits = ll//22

        ytr = ''
        for qq in range(0, mits - 1):
            ytr += item[qq*22:(qq + 1)*22] + '\n'
        else:
            ytr += item[mits*22:(mits + 1)*22]

        s2[nvnv] = ytr.split('\n')
    
    return s2


# Prints a manageable string
def manprint(mst):

    # Finds the number of rows required
    nrow = max(len(k) for k in mst)

    for idid in range(0, nrow):
        # To avoid new line
        print('| ', end='')

        for elem in mst[:-1]:
            try:
                print(elem[idid]  + (22-len(elem[idid]))*' ' +'| ', end='')
            except:
                print(22*' '+'| ', end='')

        # Last element has a new line
        try:
            print(mst[-1][idid]  + (22-len(mst[-1][idid]))*' ' +'|')
        except:
            print(22*' '+'|')


# Obtains all the keys
jobs_run = [x.decode("UTF-8") for x in r.keys()]

if len(jobs_run) == 0:
    print("No jobs completed yet")
    sys.exit()


# Keys are always the same
cols = [z.decode("UTF-8") for z in r.hkeys(jobs_run[0])]


# Prints the information on a table

# Assigns 1 space margin to each side 
# Assigns 22 spaces to each row, if more space is needed, continues on the next one
print(73*'-')

# Titles
print('| '+ cols[0]+(22-len(cols[0]))*' '+'| '+ cols[1]+(22-len(cols[1]))*' '+'| '+cols[2]+(22-len(cols[2]))*' '+'|')
print(73*'-')

for jrun in jobs_run:
    d = len(cols)*[0]
    for cc in range(0, len(cols)):
        d[cc] = r.hget(jrun, cols[cc]).decode("UTF-8")

    manprint(manageable_string(d))

    print(73*'-')

