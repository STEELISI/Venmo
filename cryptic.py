#============================================================================================================#
#*******************************   HOW TO RUN?  ************************************************************ #
# python3 datewise_textual_transactions_count.py <path to the input json file>  <path to the output file>    #
#*********************************************************************************************************** #
# Example:                                                                                                   #
#python3 datewise_textual_transactions_count.py /Users/rajattan/venmo/dummy.json ./transactions_date_wise.txt#
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
import enchant
import numpy as np
import pandas as pd
from nltk import tokenize


#===============================================================#
BATCH = 10000000
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
#===============================================================#
SENDER_FILE = "checkpoint/sender.txt"
RECEIVER_FILE = "checkpoint/receiver.txt"
CHECKPOINT_FILE = "checkpoint/current.txt"
PATH_TO_STOPWORDS_LIST = "data/STOPWORDS.txt"
DATECAT_FILE = "checkpoint/date_category_stat.txt"
DATEPER_FILE = "checkpoint/date_personal_stat.txt"
PATH_TO_KEYWORDS_LIST = "data/UNIQ_KEYWORDS_LIST.txt"
PATH_TO_INTERJECTIONS_LIST = "data/INTERJECTIONS.txt"
#===============================================================#
pattern = re.compile(r"(.)\1{2,}")
pattern_rm1 = re.compile(r"(.)\1{1,}")
english_ch = re.compile("[A-Za-z0-9]+")
#===============================================================#

if(len(sys.argv) != 3):
    print("==========================================================================")
    print("SORRY!! Please provide the path to the INPUT json file and the OUTPUT file")
    print("==========================================================================")
    print("Example: python3 cryptic.py ./dummy.json ./output.txt                     ")
    print("==========================================================================")
    sys.exit()

f = open(sys.argv[1])

if(os.path.exists(CHECKPOINT_FILE)):
    with open(CHECKPOINT_FILE, "rb") as myFile:
        current = pickle.load(myFile)
    print("RESUMING FROM " + str(current))
    if(current > 0):
        dateper = DATEPER_FILE
        with open(dateper, "rb") as myFile:
            date_personal_stat = pickle.load(myFile)


        if(len(date_personal_stat) == 0): # or len(sender) == 0 or len(receiver) == 0):
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
Creating stopwords set
"""
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
userfields = ['A','AL', 'C', 'E' ,'ET','OE', 'NC', 'L1', 'L2' , 'L3' , 'L4' , 'L5' , 'L6']
dic = enchant.Dict("en_US")
#===================================================================================#
'''
Check if a token is an emoji
'''
def is_emoji(word):
    if any(char in emoji.UNICODE_EMOJI for char in word):
        return True
    return False
#===================================================================================#
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
    tokens = convert_letters(origtokens)
    tokens = remove_stopwords(tokens)
    tokens = remove_interjections(tokens)
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
#   MAIN FLOW                                                   #
#===============================================================#

if(len(sys.argv) != 3):
    print("==========================================================================")
    print("SORRY!! Please provide the path to the INPUT json file and the OUTPUT file")
    print("==========================================================================")
    print("Example: python3 datewise_transactions_count.py ./dummy.json ./output.txt ")
    print("==========================================================================")
    sys.exit()

for line in f:
    data = json.loads(line)
    transactions = transactions + 1
    try:

        #==============================#
        ### Checks for Invalid JSONs ###
        #==============================#
        if(data is None or data['created_time'] is None):
            continue
        if(data['message'] is None or data['message'] == ""):
            continue
        if('actor' not in data or 'username' not in data['actor'] or 'transactions' not in data or data['transactions'] is None  or 'target' not in data['transactions'][0] or 'username' not in data['transactions'][0]['target']):
            continue

        username = data['actor']['username']
        tusername = data['transactions'][0]['target']['username']

        datetim = str(data['created_time'])
        date = datetim.split("T")
        month = date[0][2:7]

        if(username not in sender):
            sender[username] = {}
            sender[username]['dates'] = {}

            if('date_created' in data['actor']):
                s = str(data['actor']['date_created'])
                d = s.split("T")
                sender[username]['joined'] = d[0]

        if(month not in sender[username]['dates']):
            sender[username]['dates'][month] = {col:0 for col in userfields}
        sender[username]['dates'][month]['A'] = sender[username]['dates'][month]['A'] + 1

        if(tusername not in receiver):
            receiver[tusername] = {}
            receiver[tusername]['dates'] = {}
            if('date_created' in data['transactions'][0]['target']):
                s = str(data['transactions'][0]['target']['date_created'])
                d = s.split("T")
                receiver[tusername]['joined'] = d[0]

        if(month not in receiver[tusername]['dates']):
            receiver[tusername]['dates'][month] = {col:0 for col in userfields}
        receiver[tusername]['dates'][month]['A'] = receiver[tusername]['dates'][month]['A'] + 1

        if(date[0] not in date_personal_stat):
            date_personal_stat[date[0]] = {col:0 for col in userfields}
        date_personal_stat[date[0]]['A'] += 1



        note = str(data['message'])
        origtokens = nltk.word_tokenize(note)

        ## Removing extra spaces  ##
        tokens = remove_blanc(origtokens)
        tokens = [t for t in tokens if len(t) != 0]

        ## LENGTH ##
        words = remove_special(tokens)
        length = len(words)
        sender[username]['dates'][month]['AL'] = int((((sender[username]['dates'][month]['AL'] * (sender[username]['dates'][month]['A'] - 1)) + length)/sender[username]['dates'][month]['A']))
        date_personal_stat[date[0]]['AL'] = int((((date_personal_stat[date[0]]['AL'] * (date_personal_stat[date[0]]['A'] - 1)) + length)/date_personal_stat[date[0]]['A']))
        receiver[tusername]['dates'][month]['AL'] = int((((receiver[tusername]['dates'][month]['AL'] * (receiver[tusername]['dates'][month]['A']  - 1)) + length)/receiver[tusername]['dates'][month]['A']))      

        cryptic = 0

        if(length <= 5):
            sender[username]['dates'][month]['L1'] += 1
            date_personal_stat[date[0]]['L1'] += 1
            receiver[tusername]['dates'][month]['L1'] += 1

        elif(length > 5 and length <= 10):
            sender[username]['dates'][month]['L2'] += 1
            date_personal_stat[date[0]]['L2'] += 1
            receiver[tusername]['dates'][month]['L2'] += 1

        elif(length > 10 and length <= 20):
            sender[username]['dates'][month]['L3'] += 1
            date_personal_stat[date[0]]['L3'] += 1
            receiver[tusername]['dates'][month]['L3'] += 1

        elif(length > 20 and length <= 30):
            sender[username]['dates'][month]['L4'] += 1
            date_personal_stat[date[0]]['L4'] += 1
            receiver[tusername]['dates'][month]['L4'] += 1

        elif(length > 30 and length <= 50):
            sender[username]['dates'][month]['L5'] += 1
            date_personal_stat[date[0]]['L5'] += 1
            receiver[tusername]['dates'][month]['L5'] += 1
            cryptic = 1

        else:
            sender[username]['dates'][month]['L6'] += 1
            date_personal_stat[date[0]]['L6'] += 1
            receiver[tusername]['dates'][month]['L6'] += 1
            cryptic = 1

        
        english = 0
        if(english_ch.search(note) is not None):
            english = 1
            sender[username]['dates'][month]['E'] += 1
            receiver[tusername]['dates'][month]['E'] += 1
            date_personal_stat[date[0]]['E'] += 1

        tokens_partial = preprocessing(origtokens)


        for t in tokens_partial:
            if(is_emoji(t)):
                if(english == 1):
                    sender[username]['dates'][month]['ET'] += 1
                    date_personal_stat[date[0]]['ET'] += 1
                    receiver[tusername]['dates'][month]['ET'] += 1
                else:
                    sender[username]['dates'][month]['OE'] += 1
                    date_personal_stat[date[0]]['OE'] += 1
                    receiver[tusername]['dates'][month]['OE'] += 1
                break
        kod = 0
        if(cryptic == 0):
            tokens = preprocessing_cntd(tokens_partial)
            if(len(tokens) == 0):
                cryptic = 1
            else:    
                for t in tokens:
                    if(t in keywords or dic.check(t)):
                        kod = 1
                        break
            
            if(kod == 0 and ('a' not in tokens and 'e' not in tokens and 'i' not in tokens and 'o' not in tokens and 'u' not in tokens)):
                cryptic = 1    
       
        if(cryptic == 1):
            sender[username]['dates'][month]['C'] += 1
            receiver[tusername]['dates'][month]['C'] += 1
            date_personal_stat[date[0]]['C'] += 1         
        else:
            sender[username]['dates'][month]['NC'] += 1
            receiver[tusername]['dates'][month]['NC'] += 1
            date_personal_stat[date[0]]['NC'] += 1
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


    except:
        continue        
f.close()


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


