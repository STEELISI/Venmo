#=================================================================================================================#
#*******************************   HOW TO RUN?  ***************************************************************** #
# python3 datewise_textual_transactions_count_2020.py <path to the input 2020 csv file>  <path to the output file>#
#*****************************************************************************************************************#
# Example:                                                                                                        #
#python3 datewise_textual_transactions_count_2020.py /Users/rajattan/venmo/dummy.csv ./transactions_date_wise.txt #
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

CHUNKSIZE = 1000
transactions = 0
transactions_all = {}
textual_transactions = 0
transactions_date_wise = {}
pattern = re.compile("[A-Za-z0-9]+")

if(len(sys.argv) != 3):
    print("==========================================================================")
    print("SORRY!! Please provide the path to the INPUT json file and the OUTPUT file")
    print("==========================================================================")
    print("Example: python3 BERT_Classification_script.py ./dummy.json ./output.txt  ")
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
            if( len(row) != 9):
                continue

            timestampp = str(row[2])
            your_dt = datetime.datetime.fromtimestamp(int(timestampp))
            day = your_dt.strftime("%Y-%m-%dT")
            date = day.split("T")
            msg = row[1]
            msg = msg.strip()
            tokens = nltk.word_tokenize(msg)
            tokens = remove_blanc(tokens)
            string = ""

            if(date[0] not in transactions_all):
                transactions_all[date[0]] = 0
            transactions_all[date[0]] = transactions_all[date[0]] + 1


            for t in tokens:
                t = re.sub('[\W_]+', '', t)
                if(not (t == " ")):
                    string = string + t
            if(date[0] not in transactions_date_wise):
                transactions_date_wise[date[0]] = 0
            if(string != "" and pattern.search(string)):
                transactions_date_wise[date[0]] = transactions_date_wise[date[0]] + 1
                textual_transactions = textual_transactions + 1
        except:
            continue        

outputfile.write("DATE #TEXTUAL_TRANSACTIONS #ENGLISH \n")
for k,v in sorted(transactions_all.items()):
    if(k in transactions_date_wise):
        outputfile.write(str(k) + " " + str(v) + " " + str(transactions_date_wise[k]) + "\n")
    else:
        outputfile.write(str(k) + " " + str(v) + " 0\n")

outputfile.write("TOTAL NUMBER OF TRANSACTIONS ARE :" + str(transactions))
outputfile.write("\nTOTAL NUMBER OF TEXTUAL TRANSACTIONS IN ENGLISH ARE :" + str(textual_transactions))
outputfile.close()


