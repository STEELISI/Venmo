#============================================================================================================#
#*******************************   HOW TO RUN?  ************************************************************ #
#*********************************************************************************************************** #
# Example:                                                                                                   #
# python3 Process_Group_Users.py /Users/rajattan/venmo/dummy.json ./transactions_date_wise.txt               #
#============================================================================================================#
import re
import os
import sys
import time
import json
import nltk
import pickle
import emoji
import enchant
import datetime
import os.path
import numpy as np
import pandas as pd
import tensorflow as tf
from nltk import tokenize
from langdetect import detect
from transformers import TFBertModel
from transformers import BertTokenizer
from tensorflow.keras.layers import Dense, Flatten

#===============================================================#
BATCH = 1000000

#===============================================================#
current = 0
numbatch = 0
transactions = 0
#===============================================================#
cnt = 0
stopwords = set()
date_category_stat = {}
date_personal_stat = {}
unique_s = {}
unique_r = {}

aa=set()
gambling = set()
moreaa=set()
filter_users = {}
unique = {}


#===============================================================#
USERS_FILE = "checkpoint_part1/PARTIAL_OUTPUT.txt"

UNIQUESENDERS = "checkpoint/unique.txt"
CHECKPOINT_FILE = "checkpoint/current.txt"
PATH_TO_STOPWORDS_LIST = "data/STOPWORDS.txt"

PATH_TO_AA_LIST = "data/BIKERS.txt"
PATH_TO_MORE_AA_LIST = "data/MOREBIKERS.txt"

#===============================================================#
english_ch = re.compile("[A-Za-z0-9]+")
email = re.compile("[^@]+@[^@]+\.[^@]+")
dat = re.compile("([0-9]{1,2}(/|-)[0-9]{1,2}(/|-)[0-9]{4})|([0-9]{1,2}(/|-)[0-9]{1,2})")
#===============================================================#

if(len(sys.argv) != 3):
    print("==========================================================================")
    print("SORRY!! Please provide the path to the INPUT json file and the OUTPUT file")
    print("==========================================================================")
    print("Example: python3 Process_Group_Users.py ./dummy.json ./output.txt         ")
    print("==========================================================================")
    sys.exit()

f = open(sys.argv[1])

if(os.path.exists(CHECKPOINT_FILE)):
    with open(CHECKPOINT_FILE, "rb") as myFile:
        current = pickle.load(myFile)
    print("RESUMING FROM " + str(current))
    if(current > 0):
        us = UNIQUESENDERS + "." + str(current)
        with open(us, "rb") as myFile:
            unique = pickle.load(myFile)

        if(len(unique) == 0):
            print("===================================================================")
            print("****** COULD NOT SUCCESSFULLY LOAD THE CONTENTS USING PICKLE.******")
            print("***                YOU NEED TO RECOMPUTE THINGS AGAIN.          ***")
            print("***    PLEASE remove the file checkpoint/current.txt and re-run.***")
            print("===================================================================")
            sys.exit()
        else:
            print("=========================================================")
            print(" CHECKPOINT FILES AND DICTIONARIES LOADED SUCCESSFULLY!!!")
            print("=========================================================")


with open(USERS_FILE, "rb") as myFile:
    filter_users = pickle.load(myFile)


if(len(filter_users) == 0):
    print("============================================================================")
    print("****** COULD NOT SUCCESSFULLY LOAD FILTER FILE  CONTENTS USING PICKLE.******")
    print("***                YOU NEED TO RECOMPUTE THINGS AGAIN.                   ***")
    print("***    PLEASE remove the file checkpoint/current.txt and re-run.         ***")
    print("============================================================================")
    sys.exit()
else:
    print("=========================================================")
    print(" CHECKPOINT FILTERED USER     FILE LOADED SUCCESSFULLY!!!")
    print("=========================================================")


#===============================================================#
with open(PATH_TO_STOPWORDS_LIST,'r') as fp:
    for l in fp:
        stopwords.add(l.strip())

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
Email address regex
"""
def contains_email(note):
    if(email.search(note)):
        return True
    return False
#===============================================================#
"""
Stopwords Removal
"""
def remove_stopwords(tokens):
    return [token for token in tokens if token not in stopwords]
#===============================================================#
"""
Preprocessing Work 
"""
def preprocessing(origtokens):
    tokens = convert_letters(origtokens)
    tokens = reduce_lengthening(tokens)
    return tokens
#===============================================================#
"""
More Preprocessing Work 
"""
def preprocessing_cntd(tokens):
    tokens = remove_stopwords(tokens)
    tokens = remove_special(tokens)
    tokens = remove_blanc(tokens)
    tokens = [t for t in tokens if len(t) != 0]
    return tokens
#===============================================================#


with open(PATH_TO_AA_LIST,'r') as fp:
    for l in fp:
        aa.add(''.join(convert_letters(l.strip())))

with open(PATH_TO_MORE_AA_LIST,'r') as fp:
    for l in fp:
        moreaa.add(''.join(convert_letters(l.strip())))



#===============================================================#
#   MAIN FLOW                                                   #
#===============================================================#

for line in f:
    data = json.loads(line)
    transactions = transactions + 1
    try:
        if(transactions < current):
            continue
        
        #==============================#
        ### Checks for Invalid JSONs ###
        #==============================#
        if(data is None or data['created_time'] is None):
            continue
        if(data['message'] is None or data['message'] == ""):
            continue
        if('actor' not in data or 'username' not in data['actor'] or 'transactions' not in data or data['transactions'] is None  or 'target' not in data['transactions'][0] or 'username' not in data['transactions'][0]['target']):
            continue
        tusername = data['transactions'][0]['target']['username']
        if(tusername not in filter_users):
            continue

        username = data['actor']['username']

        if(tusername not in unique):
            unique[tusername] = {}

        recv = tusername
        sen = username
        AAflag = 0
        if("AA-U" in filter_users[tusername]['C'] or "AA-N" in filter_users[tusername]['C']):
            AAflag = 1


        if(username not in unique[tusername]):
            if(AAflag == 1):
                #unique[tusername][username] = {'TAA':0, 'AA':0,'Tradition':0,'Lunch Bunch':0,'Book Study':0,'Early Bird':0,'Eye Opener':0, 'Attitude':0, 'O' : 0, 'N':0,'T':0, '11 step':0, 'meeting':0, 'dues':0, 'donation':0, 'only emoji':0, 'greeting/gratitude':0, 'date':0}
                unique[tusername][username] = {'TB':0,'Gang':0,'Helper':0,'N':0,'T':0}

        unique[tusername][username]['T'] += 1
        note = str(data['message'])
        note = note.lower()


        if(AAflag == 1):
            flag =0
            if("dues" in note or "due" in note or "payment" in note):
                unique[recv][sen]['dues'] += 1
                flag = 1
    
            origtokens = nltk.word_tokenize(note)
            origtokens = remove_blanc(origtokens)

            fl = 0
            for t in origtokens:
                if(t in moreaa):
                    flag = 1
                    unique[recv][sen]['Helper'] += 1
                    break
                if(t in aa):
                    flag = 1
                    unique[recv][sen]['Gang'] += 1
                    break
            if(flag == 1):
                unique[recv][sen]['TB'] += 1
            if(flag == 0):
                unique[recv][sen]['N'] += 1
            """
            if(flag == 0):
                fl = 0
                for t in origtokens:
                    if(not (t in moreaa)):
                        fl = 0
                        break
                    else:
                        fl = 1
                if(fl == 1):
                    unique[recv][sen]['greeting/gratitude'] += 1
                    flag = 1
    
            if(flag == 1):
                unique[recv][sen]['TAA'] += 1
            if(flag == 0):
                for ll in aa:
                    if(ll in note):
                        unique[recv][sen]['O'] += 1
                        flag = 1
    
                        break
            if(flag == 0):
                unique[recv][sen]['N'] += 1
            """
        if cnt == (BATCH-1):
            current = transactions
            numbatch = numbatch + 1
            cnt = -1
            if(numbatch % CHECKPOINT_INTERVAL == 0):
                strcurrent = "." + str(current)
                with open(CHECKPOINT_FILE, "wb") as myFile:
                    pickle.dump(current, myFile,protocol=pickle.HIGHEST_PROTOCOL)
                sen = UNIQUESENDERS + strcurrent
                with open(sen, "wb") as myFile:
                    pickle.dump(unique, myFile,protocol=pickle.HIGHEST_PROTOCOL)

        cnt = cnt + 1


    except Exception as e:
        continue        
f.close()

# Last batch

strcurrent = "." + str(transactions)
with open(CHECKPOINT_FILE, "wb") as myFile:
    pickle.dump(transactions, myFile,protocol=pickle.HIGHEST_PROTOCOL)
sen = UNIQUESENDERS + strcurrent
with open(sen, "wb") as myFile:
    pickle.dump(unique, myFile,protocol=pickle.HIGHEST_PROTOCOL)


outputfile1 = open(sys.argv[2] + "GAMBLING.txt","w")

scount = -1
for k,v in unique.items():
    tusername = k
    if("AA-U" in filter_users[tusername]['C'] or "AA-N" in filter_users[tusername]['C']):
        continue
    scount = scount + 1

    s = str(scount) + "|" + str(len(v)) + "|"
    tot = {'TB':0,'Gang':0,'Helper':0,'N':0,'T':0}
    senders_no_posts = 0

    for kk,vv in sorted(v.items()):
        for kkk, vvv in sorted(vv.items()):
            tot[kkk] += vvv
            if(kkk == 'TB' and vvv == 0):
                senders_no_posts += 1

    for key, val in sorted(tot.items()):
        s += key + "|" + str(val) + "|"

    per = int((tot['TB']/tot['T'])* 100.0)
    s += str(per) + "|"
    s += str(senders_no_posts) + "|"
    for l in filter_users[k]['C']:
        s += l + " "
    outputfile1.write(s + "\n")

outputfile1.close()

outputfile1 = open(sys.argv[2] + "AA.txt","w")
for k,v in unique.items():

    tusername = k 
    if(not("AA-U" in filter_users[tusername]['C'] or "AA-N" in filter_users[tusername]['C'])):
        continue
    scount = scount + 1
    s = str(scount) + "|" + str(len(v)) + "|"
    tot = {'TB':0,'Gang':0,'Helper':0,'N':0,'T':0}
    senders_no_posts = 0
    for kk,vv in sorted(v.items()):
        for kkk, vvv in sorted(vv.items()):
            tot[kkk] += vvv
            if(kkk == 'TB' and vvv == 0):
                senders_no_posts += 1

    for key, val in sorted(tot.items()):
        s += key + "|" + str(val) + "|"

    per = int((tot['TB']/tot['T'])* 100.0)
    s += str(per) + "|"
    s += str(senders_no_posts) + "|"
    for l in filter_users[k]['C']:
        s += l + " "
    outputfile1.write(s + "\n")
outputfile1.close()
