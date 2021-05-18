import sys
import json
import numpy as np
import pandas as pd
unique = {}
start = ['a','f','l','q','u']
end = ['e','k','p','t','z']
CHUNKSIZE = 10000


if(len(sys.argv) != 4):
    print("========================================================================================================")
    print("SORRY!! Please provide the path to the INPUT json file, the OUTPUT file, alphabet selection number [0-5]")
    print("========================================================================================================")
    print("Example: python3 Fan_in.py  ./dummy.json ./output.txt 2                                                 ")
    print("========================================================================================================")
    sys.exit()

f = open(sys.argv[1])
index = int(sys.argv[3])
if(index < 0 or index > 5):
    print("INDEX should be between 0 and 5 only")
    sys.exit()


for chunk in pd.read_csv(sys.argv[1], chunksize=CHUNKSIZE, error_bad_lines=False):
    for row in chunk.itertuples():

        try:
            if(len(row) < 11):
                continue

            username = row[5]
            tusername = row[6]

            ltuser = tusername[0].lower()
            if(index != 5 and (ltuser < start[index] or ltuser > end[index])):
                continue 
            if(index == 5 and (ltuser >= 'a' or ltuser <= 'z')):
                continue
            if(tusername not in unique):
                unique[tusername] = {'T':0,'users':set()}
            if(username not in unique[tusername]):
                unique[tusername]['users'].add(username.strip())
            unique[tusername]['T'] += 1
    
        except Exception as e:
            continue
f.close()


outputfile1 = open(sys.argv[2] + str(index),"w")

for k,v in unique.items():
    s = str(len(v['users']))+ " " + str(v['T'])
    outputfile1.write(s + "\n")
outputfile1.close()
