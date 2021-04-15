#============================================================================================================#
# This script finds the number of transactions that have been processed till now using our sequential script #
#============================================================================================================#
import sys
import time
import pickle
import os.path

CHECKPOINT_FILE = "checkpoint/current.txt"
current = 0
if(os.path.exists(CHECKPOINT_FILE)):
    with open(CHECKPOINT_FILE, "rb") as myFile:
        current = pickle.load(myFile)

outputfile = open("checkpoint/processed_till_now.txt","w")
outputfile.write(str(current))
outputfile.close()

