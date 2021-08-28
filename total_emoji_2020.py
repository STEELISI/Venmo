#============================================================================================================#
#*******************************   HOW TO RUN?  ************************************************************ #
# python3 emoji_2020.py <path to the input json file>  <path to the output file>    #
#*********************************************************************************************************** #
# Example:                                                                                                   #
# python3 emoji_2020.py  /Users/rajattan/venmo/dummy.json ./output.txt   #
#============================================================================================================#
import re
import sys
import json
import nltk
import os
import time
import json
import nltk
import emoji
import pickle
import os.path
import datetime
import numpy as np
import pandas as pd
import tensorflow as tf
from nltk import tokenize
from langdetect import detect
from transformers import TFBertModel
from transformers import BertTokenizer
from tensorflow.keras.layers import Dense, Flatten

#===============================================================#
BATCH = 5000000
CHUNKSIZE = 10000

#===============================================================#
current = 0
numbatch = 0
transactions = 0
#===============================================================#
cnt = 0
sender = {}
receiver = {}
keywords = set()
stopwords = set()
interjections = set()
date_category_stat = {}
date_personal_stat = {}

adult = set()
health = set()
dag = set()
race = set()
politics = set()
crime = set()
relation = set()
location = set()
#===============================================================#
SENDER_FILE = "checkpoint_2020/sender.txt"
RECEIVER_FILE = "checkpoint_2020/receiver.txt"
CHECKPOINT_FILE = "checkpoint_2020/current.txt"
PATH_TO_STOPWORDS_LIST = "data/STOPWORDS.txt"
DATECAT_FILE = "checkpoint_2020/date_category_stat.txt"
DATEPER_FILE = "checkpoint_2020/date_personal_stat.txt"
PATH_TO_KEYWORDS_LIST = "data/UNIQ_KEYWORDS_LIST.txt"
PATH_TO_INTERJECTIONS_LIST = "data/INTERJECTIONS.txt"

PATH_TO_ADULT_EMOJI = "Emojis/Adult.txt"
PATH_TO_HEALTH_EMOJI = "Emojis/Health.txt"
PATH_TO_DAG_EMOJI = "Emojis/DAG.txt"
PATH_TO_RACE_EMOJI = "Emojis/Race.txt"
PATH_TO_POLITICS_EMOJI = "Emojis/Politics.txt"
PATH_TO_CRIME_EMOJI = "Emojis/Violence-Crime.txt"
PATH_TO_RELATION_EMOJI = "Emojis/Relations.txt"
PATH_TO_LOCATION_EMOJI = "Emojis/Location.txt"
#===============================================================#
pattern = re.compile(r"(.)\1{2,}")
pattern_rm1 = re.compile(r"(.)\1{1,}")
english_ch = re.compile("[A-Za-z0-9]+")
#===============================================================#

if(len(sys.argv) != 3):
    print("==========================================================================")
    print("SORRY!! Please provide the path to the INPUT json file and the OUTPUT file")
    print("==========================================================================")
    print("Example: python3 cryptic_2020.py  ./dummy.json ./output.txt  ")
    print("==========================================================================")
    sys.exit()

#f = open(sys.argv[1])
print(sys.argv[1])
if(os.path.exists(CHECKPOINT_FILE)):
    with open(CHECKPOINT_FILE, "rb") as myFile:
        current = pickle.load(myFile)
    print("RESUMING FROM " + str(current))
    if(current > 0):
        dateper = DATEPER_FILE
        with open(dateper, "rb") as myFile:
            date_personal_stat = pickle.load(myFile)

        if(len(date_personal_stat) == 0):
            print("===================================================================")
            print("****** COULD NOT SUCCESSFULLY LOAD THE CONTENTS USING PICKLE.******")
            print("***                YOU NEED TO RECOMPUTE THINGS AGAIN.          ***")
            print("***    PLEASE remove the file checkpoint_2020/current.txt and re-run.***")
            print("===================================================================")
            sys.exit()
        else:
            print("=========================================================")
            print(" CHECKPOINT FILES AND DICTIONARIES LOADED SUCCESSFULLY!!!")
            print("=========================================================")

#===============================================================#
with open(PATH_TO_STOPWORDS_LIST,'r') as fp:
    for l in fp:
        stopwords.add(l.strip())
#===============================================================#
"""
Creating interjections set
"""
with open(PATH_TO_INTERJECTIONS_LIST,'r') as fp:
    for l in fp:
        interjections.add(l.strip())
#===================================================================================#
# A - ALL | AL - Average Length | C - CRYPTIC | ET - Emoji + Text | OE - Only Emoji #
# NC - Non Cryptic | L1 - 1-5 words | L2 - 6 to 10 words | L3 - 11 to 20 |          #
# L4 - 21 to 30 | L5 - 31 to 50 | L6 - 50+                                          #                       
# E - English
#===================================================================================#
userfields = ['A']
#===================================================================================#
'''
Check if a token is an emoji
'''
def is_emoji(word):
    if any(char in emoji.UNICODE_EMOJI for char in word):
        return True
    return False

#===============================================================#

"""
Convert all letters to lower or upper case (common : lower case)
"""
def convert_letters(tokens, style = "lower"):
    if (style == "lower"):
        return [token.lower() for token in tokens]
    else:
        return [token.upper() for token in tokens]
#===============================================================#
"""
Eliminate all continuous duplicate characters more than twice
"""
def reduce_lengthening(tokens):
    return [pattern.sub(r"\1\1", token) for token in tokens]
#===============================================================#
"""
Eliminate all continuous duplicate characters more than once
"""
def reduce_lengthening_rm1(tokens):
    return [pattern_rm1.sub(r"\1", token) for token in tokens]
#===============================================================#
"""
Remove all digits and special characters
"""
def remove_special(tokens):
  return [re.sub("(\\d|\\W)+", " ", token) for token in tokens]
#===============================================================#
"""
Remove blancs on words
"""
def remove_blanc(tokens):
    return [token.strip() for token in tokens]
#===============================================================#
"""
Stopwords Removal
"""
def remove_stopwords(tokens):
    return [token for token in tokens if token not in stopwords]
#===============================================================#
"""
Stopwords Removal
"""
def remove_interjections(tokens):
    return [token for token in tokens if token not in interjections]
#===============================================================#
"""
Preprocessing Work 
"""

def preprocessing(origtokens):
    tokens = remove_blanc(origtokens)
    tokens = reduce_lengthening(tokens)
    return tokens
#===============================================================#
"""
More Preprocessing Work 
"""
def preprocessing_cntd(tokens):
    tokens = remove_special(tokens)
    tokens = [t for t in tokens if len(t) != 0]
    return tokens
#===============================================================#
with open(PATH_TO_KEYWORDS_LIST,'r') as fp:
    for l in fp:
        keywords.add(''.join(convert_letters(l.strip())))
#===============================================================#
with open(PATH_TO_ADULT_EMOJI,'r') as fp:
    for l in fp:
        adult.add(l.strip())
#===============================================================#
with open(PATH_TO_HEALTH_EMOJI,'r') as fp:
    for l in fp:
        health.add(l.strip())
#===============================================================#
with open(PATH_TO_DAG_EMOJI,'r') as fp:
    for l in fp:
        dag.add(l.strip())
#===============================================================#
with open(PATH_TO_RACE_EMOJI,'r') as fp:
    for l in fp:
        race.add(l.strip())
#===============================================================#
with open(PATH_TO_POLITICS_EMOJI,'r') as fp:
    for l in fp:
        politics.add(l.strip())
#===============================================================#
with open(PATH_TO_CRIME_EMOJI,'r') as fp:
    for l in fp:
        crime.add(l.strip())
#===============================================================#
with open(PATH_TO_RELATION_EMOJI,'r') as fp:
    for l in fp:
        relation.add(l.strip())
#===============================================================#
with open(PATH_TO_LOCATION_EMOJI,'r') as fp:
    for l in fp:
        location.add(l.strip())
#===============================================================#


#===============================================================#
#   MAIN FLOW                                                   #
#===============================================================#

#====================================================================================================================#
#************************************************   FORMAT EXPECTED    **********************************************#
#  1,           2,       ,   3      ,     4     ,      5         ,   6             ,      7        ,       8         #
#"message","created_time","actor_id","target_id","actor_username","target_username","actor_created","target_created" #
#"d dummy message",1618035048,11111111,99999,"John-Smith-2","janedoe",1618035048,1618035048                          #
#"dussmmy,tht ,refrf ,r message",1618035048,11111111,99999,"John-Smith-2","janedoe",1618035048,1618035048            #
#====================================================================================================================#


for chunk in pd.read_csv(sys.argv[1], chunksize=CHUNKSIZE, error_bad_lines=False):
    for row in chunk.itertuples():
        transactions = transactions + 1
        try:
            if(transactions < current or len(row) < 8):
                continue
            username = row[5]
            tusername = row[6]
            note = row[1]
            origtokens = nltk.word_tokenize(note)
            tokens_partial = preprocessing(origtokens)
            only_emojis = 0
            for t in tokens_partial:
                if(emoji.emoji_count(t) == len(t)):
                    only_emojis += 1
                    break

            if(only_emojis == 0):
                continue        
    

            timestampp = str(row[2])
            your_dt = datetime.datetime.fromtimestamp(float(timestampp))
            day = your_dt.strftime("%Y-%m-%dT")
            date = day.split("T")
            month = date[0][2:7]

            if(date[0] not in date_personal_stat):
                date_personal_stat[date[0]] = {col:0 for col in userfields}
            date_personal_stat[date[0]]['A'] += 1

            if cnt == (BATCH-1):
                current = transactions
                cnt = -1

                strcurrent = "." + str(current)
                dateper  = DATEPER_FILE
                with open(CHECKPOINT_FILE, "wb") as myFile:
                    pickle.dump(current, myFile,protocol=pickle.HIGHEST_PROTOCOL)
                with open(dateper, "wb") as myFile:
                    pickle.dump(date_personal_stat, myFile,protocol=pickle.HIGHEST_PROTOCOL)
                send = SENDER_FILE + strcurrent
                with open(send, "wb") as myFile:
                    pickle.dump(sender, myFile,protocol=pickle.HIGHEST_PROTOCOL)
                recv = RECEIVER_FILE + strcurrent
                with open(recv, "wb") as myFile:
                    pickle.dump(receiver, myFile,protocol=pickle.HIGHEST_PROTOCOL)
    
                df_stat = pd.DataFrame.from_dict(date_personal_stat, orient='index', columns=userfields)
                df_stat = df_stat.rename_axis('Date').reset_index()
                df_stat.to_csv(sys.argv[2] + "per.output", index=False)

                outputfile = open(sys.argv[2],"w")
                outputfile.write("TRANSACTIONS PROCESSED TILL NOW = " + str(current) + "\n")
                scnt=-1
                for k,v in sender.items():
                    if(v is None):
                        continue
                    scnt = scnt + 1
                    s = ""
                    try:
                        s = str(scnt) + "|"
                        if('joined' in sender[k]):
                            s = s + str(sender[k]['joined'])
                        s = s + "|"
    
                        if('dates' in sender[k]):
                            for kk,vv in sender[k]['dates'].items():
                                s = s + str(kk)
                                for kkk,vvv in sorted(vv.items()):
                                    s = s + "," + str(kkk) + ":" +  str(vvv)
                                s = s + ";"
                        s = s + "|"
                        if(k in receiver and 'dates' in receiver[k]):
                            for kk,vv in receiver[k]['dates'].items():
                                s = s + str(kk)
                                for kkk,vvv in sorted(vv.items()):
                                    s = s + "," + str(kkk) + ":" +  str(vvv)
                                s = s + ";"
    
                        outputfile.write(s + "\n")
                    except:
                        continue


                outputfile.close()
                outputfile1 = open(sys.argv[2] + "recv.output","w")
                rcnt=-1
                for k,v in receiver.items():
                    if(v is None or k in sender):
                        continue
                    rcnt = rcnt + 1
                    s = ""
                    try:
                        s = str(rcnt) + "|"
                        if('joined' in receiver[k]):
                            s = s + str(receiver[k]['joined'])
                        s = s + "|"
                        if('dates' in receiver[k]):
                            for kk,vv in receiver[k]['dates'].items():
                                s = s + str(kk)
                                for kkk,vvv in sorted(vv.items()):
                                    s = s + "," + str(kkk) + ":" +  str(vvv)
                                s = s + ";"
    
                        outputfile1.write(s + "\n")
                    except:
                        continue
    
                outputfile1.close()
                sender.clear()
                receiver.clear()


            cnt = cnt + 1

        except Exception as e:
            print(e)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            continue


strcurrent = "." + str(transactions)
datecat = DATECAT_FILE
dateper  = DATEPER_FILE
with open(CHECKPOINT_FILE, "wb") as myFile:
    pickle.dump(transactions, myFile,protocol=pickle.HIGHEST_PROTOCOL)
with open(dateper, "wb") as myFile:
    pickle.dump(date_personal_stat, myFile,protocol=pickle.HIGHEST_PROTOCOL)
send = SENDER_FILE + strcurrent
with open(send, "wb") as myFile:
    pickle.dump(sender, myFile,protocol=pickle.HIGHEST_PROTOCOL)
recv = RECEIVER_FILE + strcurrent
with open(recv, "wb") as myFile:
    pickle.dump(receiver, myFile,protocol=pickle.HIGHEST_PROTOCOL)


df_stat = pd.DataFrame.from_dict(date_personal_stat, orient='index', columns=userfields)
df_stat = df_stat.rename_axis('Date').reset_index()
df_stat.to_csv(sys.argv[2] + "per.output", index=False)

outputfile = open(sys.argv[2],"w")
outputfile.write("TRANSACTIONS PROCESSED TILL NOW = " + str(transactions) + "\n")
scnt=-1
for k,v in sender.items():
    if(v is None):
        continue
    scnt = scnt + 1
    s = ""
    try:
        s = str(scnt) + "|"
        if('joined' in sender[k]):
            s = s + str(sender[k]['joined'])
        s = s + "|"

        if('dates' in sender[k]):
            for kk,vv in sender[k]['dates'].items():
                s = s + str(kk)
                for kkk,vvv in sorted(vv.items()):
                    s = s + "," + str(kkk) + ":" +  str(vvv)
                s = s + ";"

        s = s + "|"
        if(k in receiver and 'dates' in receiver[k]):
            for kk,vv in receiver[k]['dates'].items():
                s = s + str(kk)
                for kkk,vvv in sorted(vv.items()):
                    s = s + "," + str(kkk) + ":" +  str(vvv)
                s = s + ";"
        outputfile.write(s + "\n")
    except:
        continue

outputfile.close()

outputfile1 = open(sys.argv[2] + "recv.output","w")
outputfile1.write("TRANSACTIONS PROCESSED TILL NOW = " + str(transactions) + "\n")


rcnt=-1
for k,v in receiver.items():
    if(v is None or k in sender):
        continue
    rcnt = rcnt + 1
    s = ""
    try:
        s = str(rcnt) + "|"
        if('joined' in receiver[k]):
            s = s + str(receiver[k]['joined'])
        s = s + "|"

        if('dates' in receiver[k]):
            for kk,vv in receiver[k]['dates'].items():
                s = s + str(kk)
                for kkk,vvv in sorted(vv.items()):
                    s = s + "," + str(kkk) + ":" +  str(vvv)
                s = s + ";"

        outputfile1.write(s + "\n")
    except:
        continue

outputfile1.close()


