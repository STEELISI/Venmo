import re
import os
import sys
import time
import json
import nltk
import pickle
import os.path
import numpy as np
import pandas as pd
import tensorflow as tf
from nltk import tokenize



#===============================================================#
CHECKPOINT_INTERVAL = 10000000
#===============================================================#
PATH_TO_AA_LIST = "data/BIKERS.txt"
PATH_TO_STOPWORDS_LIST = "data/STOPWORDS.txt"
#===============================================================#
USERS_FILE = "checkpoint_part1/PARTIAL_OUTPUT.txt"
CHECKPOINT_FILE = "checkpoint_part1/current.txt"
CHECKPOINT_DIR = "checkpoint_part1/"
#===============================================================#
if(len(sys.argv) != 3 or not (os.path.exists(CHECKPOINT_DIR))):
    print("==========================================================================")
    print("SORRY!! Please provide the path to the INPUT json file and the OUTPUT file")
    print("==========================================================================")
    print("Example: python3 Filter_Group_Users.py ./dummy.json ./output.txt          ")
    print("==========================================================================")
    sys.exit()
#===============================================================#
## AA : Bikers  
#===============================================================#

##Special checks AA
##FRATERNITY Camel case or UPPER Case
##BET should not be in contain
## 
#===============================================================#

aa=set()

filter_users = {}

stopwords = set()


current = 0
numbatch = 0
transactions = 0

pattern = re.compile(r"(.)\1{2,}")

#===============================================================#
f = open(sys.argv[1])

if(os.path.exists(CHECKPOINT_FILE)):
    with open(CHECKPOINT_FILE, "rb") as myFile:
        current = pickle.load(myFile)
    print("RESUMING FROM " + str(current))
    if(current > 0):
        with open(USERS_FILE, "rb") as myFile:
            filter_users = pickle.load(myFile)


        if(len(filter_users) == 0):
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
Remove blancs on words
"""
def remove_blanc(tokens):
    return [token.strip() for token in tokens]
#===============================================================#
with open(PATH_TO_STOPWORDS_LIST,'r') as fp:
    for l in fp:
        stopwords.add(l.strip())


#===============================================================#
"""
Stopwords Removal
"""
def remove_stopwords(tokens):
    return [token for token in tokens if token not in stopwords]
#===============================================================#

"""
Remove all digits and special characters
"""
def remove_special(tokens):
  return [re.sub("(\\d|\\W)+", " ", token) for token in tokens]
#===============================================================#



with open(PATH_TO_AA_LIST,'r') as fp:
    for l in fp:
        aa.add(''.join(convert_letters(l.strip())))


#===============================================================#
"""
Preprocessing Work 
"""
def preprocessing(origtokens):
    tokens = remove_blanc(origtokens)
    tokens = remove_stopwords(tokens)
    tokens = remove_special(tokens)
    tokens = reduce_lengthening(tokens)
    return tokens
#===============================================================#


#====================================================================================================================#
#************************************************   FORMAT EXPECTED    **********************************************#
#  1,           2,       ,   3      ,     4     ,      5         ,   6             ,      7        ,       8         #
#"message","created_time","actor_id","target_id","actor_username","target_username","actor_created","target_created" #
#"d dummy message",1618035048,11111111,99999,"John-Smith-2","janedoe",1618035048,1618035048                          #
#"dussmmy,tht ,refrf ,r message",1618035048,11111111,99999,"John-Smith-2","janedoe",1618035048,1618035048            #
#====================================================================================================================#
# target_name
#====================================================================================================================#


for line in f:
    data = json.loads(line)
    transactions = transactions + 1
    try:
        if(transactions < current):
            continue

        if((transactions % CHECKPOINT_INTERVAL) == 0):
            current = transactions

            with open(CHECKPOINT_FILE, "wb") as myFile:
                pickle.dump(current, myFile,protocol=pickle.HIGHEST_PROTOCOL)

            with open(USERS_FILE, "wb") as myFile:
                pickle.dump(filter_users, myFile,protocol=pickle.HIGHEST_PROTOCOL)

            outputfile = open(sys.argv[2],"w")
            outputfile.write("TRANSACTIONS PROCESSED TILL NOW = " + str(current) + "\n")
            outputfile.write("NUMBER OF POSSIBLE GROUPS FOUND TILL NOW = " + str(len(filter_users)) + "\n")
            outputfile.close()


        if(data is None):
            continue

        if('transactions' not in data or data['transactions'] is None  or 'target' not in data['transactions'][0] or 'username' not in data['transactions'][0]['target']):
            continue
        tusername = data['transactions'][0]['target']['username']

        lastname = "###;###;###;"

        if('lastname' in data['transactions'][0]['target']):
            lastname = data['transactions'][0]['target']['lastname']

        firstname = "###;###;###;"

        if('firstname' in data['transactions'][0]['target']):
            firstname = data['transactions'][0]['target']['firstname']

        name = "###;###;###;"
        if('name' in data['transactions'][0]['target']):
            name = data['transactions'][0]['target']['name']
       
        lfirstname = firstname.lower()
        llastname = lastname.lower()
        lname = name.lower()
        
        ## IDENTIFIED FROM Unames
        note = str(data['message'])
   
        #print(tusername,lastname,firstname,name,note)     
        parts = tusername.split("-")
 
        flag = 0
        for username in parts:
            lusername = username.lower()
            
            if(firstname in aa or lastname in aa or username in aa or name in aa):
                if(tusername not in filter_users):
                    filter_users[tusername] = {}
                    filter_users[tusername]['C'] = set()
                filter_users[tusername]['C'].add("AA-U")
                flag = 1
                break

            elif(lfirstname in aa or llastname in aa or lusername in aa or lname in aa):
                if(tusername not in filter_users):
                    filter_users[tusername] = {}
                    filter_users[tusername]['C'] = set()
                filter_users[tusername]['C'].add("AA-U")
                flag = 1
                break

    
        if(flag == 1):
            continue


        parts = name.split(" ")
        for username in parts:
            lusername = username.lower()
            ltusername = tusername.lower()
            if(firstname in aa or lastname in aa or username in aa or name in aa):
                if(tusername not in filter_users):
                    filter_users[tusername] = {}
                    filter_users[tusername]['C'] = set()
                filter_users[tusername]['C'].add("AA-U")
                flag = 1
                break

            elif(lfirstname in aa or llastname in aa or lusername in aa or lname in aa or ltusername in aa):
                if(tusername not in filter_users):
                    filter_users[tusername] = {}
                    filter_users[tusername]['C'] = set()
                filter_users[tusername]['C'].add("AA-U")
                flag = 1
                break

        if(flag == 1):
            continue

        note = note.lower()
        origtokens = nltk.word_tokenize(note)
        origtokens =  preprocessing(origtokens)
 
        if(len(origtokens) > 30):
            continue


        name = name.lower()

        for l in aa:
            if( l in name):
                if(username not in filter_users):
                    filter_users[tusername] = {}
                    filter_users[tusername]['C'] = set()
                filter_users[tusername]['C'].add("AA-U")
                flag = 1
                break
            if(l in note):
                if(username not in filter_users):
                    filter_users[tusername] = {}
                    filter_users[tusername]['C'] = set()
                filter_users[tusername]['C'].add("AA-N")
                flag = 1
                break

        if(flag == 1):
            continue

    except Exception as e:
        continue
f.close()

with open(CHECKPOINT_FILE, "wb") as myFile:
    pickle.dump(transactions, myFile,protocol=pickle.HIGHEST_PROTOCOL)

with open(USERS_FILE, "wb") as myFile:
    pickle.dump(filter_users, myFile,protocol=pickle.HIGHEST_PROTOCOL)

outputfile = open(sys.argv[2],"w")
outputfile.write("TRANSACTIONS PROCESSED = " + str(transactions) + "\n")
outputfile.write("NUMBER OF POSSIBLE GROUPS FOUND = " + str(len(filter_users)) + "\n")
outputfile.close()
