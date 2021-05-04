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
from langdetect import detect
from transformers import TFBertModel
from transformers import BertTokenizer
from tensorflow.keras.layers import Dense, Flatten


PATH_TO_AA_LIST = "data/AA.txt"
PATH_TO_FRATERNITY_LIST = "data/FRATERNITY.txt"
PATH_TO_GAMBLING_LIST = "data/GAMBLING.txt"
PATH_TO_ADULT_LIST = "data/ADULT.txt"
PATH_TO_DRUGS_LIST = "data/DRUGS.txt"
PATH_TO_ALCOHOLICS_LIST = "data/ALCOHOLICS.txt"

## AA : AA 
## F : Fraternity
## G : Gambling
## A : Adult
## D : Drug
## AL : Alcohol


##Special checks AA
##FRATERNITY Camel case or UPPER Case
##BET should not be in contain
## 

aa=set()
fraternity = set()
fraternity_small = set()
gambling = set()
adult = set()
drugs = set()
alcoholics = set()

filter_users = {}

current = 0
numbatch = 0
transactions = 0

pattern = re.compile(r"(.)\1{2,}")
#===============================================================#
if(len(sys.argv) != 2):
    print("==========================================================================")
    print("SORRY!! Please provide the path to the INPUT json file and the OUTPUT file")
    print("==========================================================================")
    print("Example: python3 BERT_Classification_script.py ./dummy.json ./output.txt  ")
    print("==========================================================================")
    sys.exit()

f = open(sys.argv[1])







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


with open(PATH_TO_GAMBLING_LIST,'r') as fp:
    for l in fp:
        gambling.add(''.join(convert_letters(l.strip())))

with open(PATH_TO_ADULT_LIST,'r') as fp:
    for l in fp:
        adult.add(''.join(convert_letters(l.strip())))

with open(PATH_TO_DRUGS_LIST,'r') as fp:
    for l in fp:
        drugs.add(''.join(convert_letters(l.strip())))

with open(PATH_TO_ALCOHOLICS_LIST,'r') as fp:
    for l in fp:
        alcoholics.add(''.join(convert_letters(l.strip())))

with open(PATH_TO_AA_LIST,'r') as fp:
    for l in fp:
        aa.add(''.join(convert_letters(l.strip())))

with open(PATH_TO_FRATERNITY_LIST,'r') as fp:
    for l in fp:
        fraternity_small.add(''.join(convert_letters(l.strip())))

with open(PATH_TO_FRATERNITY_LIST,'r') as fp:
    for l in fp:
        fraternity.add(l.strip())





#===============================================================#
"""
Preprocessing Work 
"""
def preprocessing(origtokens):
    tokens = reduce_lengthening(origtokens)
    return tokens
#===============================================================#



for line in f:
    data = json.loads(line)
    transactions = transactions + 1
    try:

        if(data is None or data['message'] is None):
            continue

        if('transactions' not in data or data['transactions'] is None  or 'target' not in data['transactions'][0] or 'username' not in data['transactions'][0]['target']):
            continue
        tusername = data['transactions'][0]['target']['username']

        lastname = "###;###;###;"

        if('lastname' not in data['transactions'][0]['target']):
            lastname = data['transactions'][0]['target']['lastname']

        firstname = "###;###;###;"

        if('firstname' not in data['transactions'][0]['target']):
            firstname = data['transactions'][0]['target']['firstname']

        name = "###;###;###;"

        if('name' not in data['transactions'][0]['target']):
            firstname = data['transactions'][0]['target']['name']



        ## IDENTIFIED FROM Unames
        note = str(data['message'])
   
        #print(tusername,lastname,firstname,name,note)     
        parts = tusername.split("-")
 
        flag = 0
        for username in parts:
     
            if(firstname == "AA" or lastname == "AA" or username == "AA" or name == "AA" or " AA " in name or name.startswith("AA ")  or name.endswith("AA")):
                if(username not in filter_users):
                    filter_users[username] = {}
                    filter_users[username]['C'] = set()
                filter_users[username]['C'].add("AA-U")
                flag = 1
                break
    
    
            elif(firstname in fraternity or lastname in fraternity or username in fraternity or name in fraternity):
                if(username not in filter_users):
                    filter_users[username] = {}
                    filter_users[username]['C'] = set()
                filter_users[username]['C'].add("F-U")
                flag = 1 
                break
                
    
            elif(firstname in gambling or lastname in gambling or username in gambling or name in gambling):
                if(username not in filter_users):
                    filter_users[username] = {}
                    filter_users[username]['C'] = set()
                filter_users[username]['C'].add("G-U")
                flag = 1 
                break
    
            elif(firstname in adult or lastname in adult or username in adult or name in adult):
                if(username not in filter_users):
                    filter_users[username] = {}
                    filter_users[username]['C'] = set()
                filter_users[username]['C'].add("A-U")
                flag = 1 
                break
    
            elif(firstname in drugs or lastname in drugs or username in drugs or name in drugs):
                if(username not in filter_users):
                    filter_users[username] = {}
                    filter_users[username]['C'] = set()
                filter_users[username]['C'].add("D-U")
                flag = 1 
                break
    
            elif(firstname in alcoholics or lastname in alcoholics or username in alcoholics or name in alcoholics):
                if(username not in filter_users):
                    filter_users[username] = {}
                    filter_users[username]['C'] = set()
                filter_users[username]['C'].add("AL-U")
                flag = 1 
                break
    
        if(flag == 1):
            continue


        for l in fraternity:
            if(len(l) > 3 and (firstname in l or lastname in l or tusername in l or name in l)):
                if(username not in filter_users):
                    filter_users[tusername] = {}
                    filter_users[tusername]['C'] = set()
                filter_users[tusername]['C'].add("F-U")
                flag = 1
                break

        if(flag == 1):
            continue

        note = note.lower()
        origtokens = nltk.word_tokenize(note)
        origtokens =  preprocessing(origtokens)
 
        if(len(origtokens) > 30):
            continue



        for l in aa:
            if( name in l):
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




        for l in origtokens:

            if(l in fraternity_small):
                if(username not in filter_users):
                    filter_users[tusername] = {}
                    filter_users[tusername]['C'] = set()
                filter_users[tusername]['C'].add("F-N")
                flag = 1
                break

            elif(l in gambling):
                if(username not in filter_users):
                    filter_users[tusername] = {}
                    filter_users[tusername]['C'] = set()
                filter_users[tusername]['C'].add("G-N")
                flag = 1
                break

            elif(l in adult):
                if(username not in filter_users):
                    filter_users[tusername] = {}
                    filter_users[tusername]['C'] = set()
                filter_users[tusername]['C'].add("A-N")
                flag = 1
                break

            elif(l in alcoholics):
                if(username not in filter_users):
                    filter_users[tusername] = {}
                    filter_users[tusername]['C'] = set()
                filter_users[tusername]['C'].add("AL-N")
                flag = 1
                break


        if(flag == 1):
            continue

        for l in gambling:
            if(len(l) > 3 and (firstname in l or lastname in l or tusername in l or name in l)):
                if(username not in filter_users):
                    filter_users[tusername] = {}
                    filter_users[tusername]['C'] = set()
                filter_users[tusername]['C'].add("G-U")
                flag = 1
                break


        if(flag == 1):
            continue

        for l in adult:
            if(len(l) > 3 and (firstname in l or lastname in l or tusername in l or name in l)):
                if(username not in filter_users):
                    filter_users[tusername] = {}
                    filter_users[tusername]['C'] = set()
                filter_users[tusername]['C'].add("A-U")
                flag = 1
                break


        if(flag == 1):
            continue

        for l in alcoholics:
            if(len(l) > 3 and (firstname in l or lastname in l or tusername in l or name in l)):
                if(username not in filter_users):
                    filter_users[tusername] = {}
                    filter_users[tusername]['C'] = set()
                filter_users[tusername]['C'].add("AL-U")
                flag = 1
                break


    except:
        continue
f.close()

print(filter_users)
