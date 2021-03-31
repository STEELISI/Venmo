#============================================================================================================#
#*******************************   HOW TO RUN?  ************************************************************ #
# python3 get_intermediate_outputs.py <path to the output file>                                              #
#*********************************************************************************************************** #
# Example:                                                                                                   #
# python3 get_intermediate_outputs.py intermediate_output                                                    #
#============================================================================================================#
import sys
import time
import nltk
import pickle
import os.path
import datetime
import numpy as np
import pandas as pd

#===============================================================#
current = 0
date_category_stat = {}  # number of each category for each day
date_personal_stat = {}
sender = {}
receiver = {}
CHECKPOINT_FILE = "checkpoint/current.txt"
#===============================================================#

if(len(sys.argv) != 2):
    print("==========================================================================")
    print("SORRY!! Please provide the path to the INPUT json file and the OUTPUT file")
    print("==========================================================================")
    print("Example: python3 BERT_Classification_script.py ./dummy.json ./output.txt  ")
    print("==========================================================================")
    sys.exit()


if(os.path.exists(CHECKPOINT_FILE)):
    with open(CHECKPOINT_FILE, "rb") as myFile:
        current = pickle.load(myFile)
    if(current > 0):
        with open("checkpoint/date_category_stat.txt", "rb") as myFile:
            date_category_stat = pickle.load(myFile)
        with open("checkpoint/date_personal_stat.txt", "rb") as myFile:
            date_personal_stat = pickle.load(myFile)
        with open("checkpoint/sender.txt", "rb") as myFile:
            sender = pickle.load(myFile)
        with open("checkpoint/receiver.txt", "rb") as myFile:
            receiver = pickle.load(myFile)
        if(len(date_category_stat) == 0 or len(date_category_stat) == 0 or len(sender) == 0 or len(receiver) == 0):
            print("COULD NOT SUCCESSFULLY LOAD THE CONTENTS USING PICKLE.")
            print("YOU NEED TO RECOMPUTE THINGS AGAIN.")
            print("PLEASE remove the file checkpoint/current.txt and re-run.")
            sys.exit()
        else:
            print(" CHECKPOINT FILES AND DICTIONARIES LOADED SUCCESSFULLY!!!")

cols_name = ['Date', 'Note','myr','uname','tuname','ADULT_CONTENT', 'HEALTH', 'DRUGS_ALCOHOL_GAMBLING', 'RACE', 'VIOLENCE_CRIME', 'POLITICS', 'RELATION', 'LOCATION']
label_cols = cols_name[5:]  # drop 'Date' & 'Note' (the 2 leftmost columns)
sens_cols = ['ADULT_CONTENT', 'HEALTH', 'DRUGS_ALCOHOL_GAMBLING', 'RACE', 'VIOLENCE_CRIME', 'POLITICS', 'RELATION', 'LOCATION','T']

personal_cols = ['A','E','I','P','T']
userfields = ['S','P','T','A']

# Write stats

df_stat = pd.DataFrame.from_dict(date_category_stat, orient='index', columns=sens_cols)
df_stat = df_stat.rename_axis('Date').reset_index()
df_stat.to_csv(sys.argv[1] + "sen.output", index=False)


df_stat = pd.DataFrame.from_dict(date_personal_stat, orient='index', columns=personal_cols)
df_stat = df_stat.rename_axis('Date').reset_index()
df_stat.to_csv(sys.argv[1] + "per.output", index=False)

outputfile = open(sys.argv[1],"w")

outputfile.write("TRANSACTIONS PROCESSED TILL NOW = " + str(current) + "\n")
scnt=-1
for k,v in sender.items():
    if(v is None):
        continue
    scnt = scnt + 1
    s = ""
    try:
        s = str(k) + "|"
        if('joined' in sender[k]):
            s = s + str(sender[k]['joined'])
        s = s + "|"

        if('dates' in sender[k]):
            for kk,vv in sender[k]['dates'].items():
                s = s + str(kk) + "," +  str(sender[k]['dates'][kk]['S']) + "," + str(sender[k]['dates'][kk]['P']) + "," + str(sender[k]['dates'][kk]['T']) + "," + str(sender[k]['dates'][kk]['A']) + ";"
        
        s = s + "|"
        if(k in receiver and 'dates' in receiver[k]):
            for kk,vv in receiver[k]['dates'].items():
                s = s + str(kk) + "," +  str(receiver[k]['dates'][kk]['S']) + "," + str(receiver[k]['dates'][kk]['P']) + "," + str(receiver[k]['dates'][kk]['T']) + "," + str(receiver[k]['dates'][kk]['A']) + ";"
    
        
        outputfile.write(s + "\n")
    except:
        continue

outputfile.close()

outputfile1 = open(sys.argv[1] + "recv.output","w")
outputfile1.write("TRANSACTIONS PROCESSED TILL NOW = " + str(current) + "\n")

rcnt=-1
for k,v in receiver.items():
    if(v is None or k in sender):
        continue
    rcnt = rcnt + 1
    s = ""
    try:
        s = str(k) + "|"
        if('joined' in receiver[k]):
            s = s + str(receiver[k]['joined'])
        s = s + "|"

        if('dates' in receiver[k]):
            for kk,vv in receiver[k]['dates'].items():
                s = s + str(kk) + "," +  str(receiver[k]['dates'][kk]['S']) + "," + str(receiver[k]['dates'][kk]['P']) + "," + str(receiver[k]['dates'][kk]['T']) + "," + str(receiver[k]['dates'][kk]['A']) + ";"

        outputfile1.write(s + "\n")
    except:
        continue

outputfile1.close()
