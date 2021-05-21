#============================================================================================================#
#*******************************   HOW TO RUN?  ************************************************************ #
# python3 enchant.py <path to the input json file>  <path to the output file>    #
#*********************************************************************************************************** #
# Example:                                                                                                   #
#python3 enchant.py /Users/rajattan/venmo/dummy.json ./transactions_date_wise.txt#
#============================================================================================================#
#import enchant
import re
import sys
import json
import nltk
from nltk import word_tokenize, pos_tag, ne_chunk
from nltk.chunk import tree2conlltags
import enchant

d = enchant.Dict("en_US")
transactions = 0
textual_transactions = 0
transactions_date_wise = {}
english_ch = re.compile("[A-Za-z0-9]+")

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
    print("Example: python3 datewise_transactions_count.py ./dummy.json ./output.txt ")
    print("==========================================================================")
    sys.exit()



f = open(sys.argv[1])
outputfile = open(sys.argv[2],"w")

for line in f:
    data = json.loads(line)
    transactions = transactions + 1
    try:

        if(data is None or data['created_time'] is None):
            continue
        datetime = str(data['created_time'])
        date = datetime.split("T")
        if(data is None or data['message'] is None or data['message'] == ""):
            continue
        msg = str(data['message'])
        msg = msg.strip()
        if(len(msg) == 0 or  english_ch.search(msg) == None):
            continue
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
f.close()

outputfile.write("DATE #TEXTUAL_TRANSACTIONS \n")
for k,v in sorted(transactions_date_wise.items()):
    outputfile.write(str(k) + " " + str(v) + "\n")

outputfile.write("TOTAL NUMBER OF TRANSACTIONS ARE :" + str(transactions))
outputfile.write("\nTOTAL NUMBER OF TEXTUAL TRANSACTIONS IN ENGLISH ARE :" + str(textual_transactions))
outputfile.close()
