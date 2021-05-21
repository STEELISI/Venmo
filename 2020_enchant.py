#=================================================================================================================#
#*******************************   HOW TO RUN?  ***************************************************************** #
# python3 2020_enchant.py <path to the input 2020 csv file>  <path to the output file>#
#*****************************************************************************************************************#
# Example:                                                                                                        #
#python3 2020_enchant.py /Users/rajattan/venmo/dummy.csv ./transactions_date_wise.txt #
#=================================================================================================================#

import re
import sys
import csv
import time
import json
import nltk
import os.path
import datetime
import numpy as np
import pandas as pd
from nltk import tokenize
from nltk import word_tokenize, pos_tag, ne_chunk
from nltk.chunk import tree2conlltags
import enchant


d = enchant.Dict("en_US")
transactions = 0
textual_transactions = 0
transactions_date_wise = {}
english_ch = re.compile("[A-Za-z0-9]+")

CHUNKSIZE = 1000


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

if(len(sys.argv) != 3):
    print("==========================================================================")
    print("SORRY!! Please provide the path to the INPUT json file and the OUTPUT file")
    print("==========================================================================")
    print("Example: python3 2020_enchant.py ./dummy.json ./output.txt  ")
    print("==========================================================================")
    sys.exit()

print(sys.argv[1])
outputfile = open(sys.argv[2],"w")

def tokenize_word_text(text):
    tokens = nltk.word_tokenize(text)
    tokens = [token.strip() for token in tokens]
    return tokens

"""
Remove blancs on words
"""
def remove_blanc(tokens):
    tokens = [token.strip() for token in tokens]
    return(tokens)


for chunk in pd.read_csv(sys.argv[1], chunksize=CHUNKSIZE, error_bad_lines=False):
    for row in chunk.itertuples():
        transactions = transactions + 1
        try:
            
            if( len(row) < 9):
                continue
            timestampp = str(row[2])
            your_dt = datetime.datetime.fromtimestamp(float(timestampp))
            day = your_dt.strftime("%Y-%m-%dT")
            date = day.split("T")
            msg = row[1]
            msg = msg.strip()
            tokens = nltk.word_tokenize(msg)
            tokens = remove_blanc(tokens)
            tokens = remove_special(tokens)
            flag = "FALSE"
            for t in tokens:
                if(d.check(t)):
                    flag = "TRUE"
                    break
            x = tree2conlltags(ne_chunk(pos_tag(word_tokenize(msg))))
            nerf  = "N"
            for i in x:
                if(len(i) > 2 and not ("B-" in i[2] or "I-" in i[2] )):
                    nerf  = "S"
                    break
            if(flag == "TRUE" or nerf == "N"):
                if(date[0] not in transactions_date_wise):
                    transactions_date_wise[date[0]] = 0
                transactions_date_wise[date[0]] = transactions_date_wise[date[0]] + 1
                textual_transactions = textual_transactions + 1
        except:
            continue

outputfile.write("DATE #TEXTUAL_TRANSACTIONS \n")
for k,v in sorted(transactions_date_wise.items()):
    outputfile.write(str(k) + " " + str(v) + "\n")

outputfile.write("TOTAL NUMBER OF TRANSACTIONS ARE :" + str(transactions))
outputfile.write("\nTOTAL NUMBER OF TEXTUAL TRANSACTIONS IN ENGLISH ARE :" + str(textual_transactions))
outputfile.close()

