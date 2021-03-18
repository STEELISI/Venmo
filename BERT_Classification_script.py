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
from nltk import tokenize

transactions = 0
textual_transactions = 0
transactions_date_wise = {}
pattern = re.compile("[A-Za-z0-9]+")

"""
Convert all letters to lower or upper case (common : lower case)
"""
def convert_letters(tokens, style = "lower"):
    if (style == "lower"):
        return [token.lower() for token in tokens]
    else:
        return [token.upper() for token in tokens]

"""
Eliminate all continuous duplicate characters more than twice
"""
def reduce_lengthening(tokens):
    pattern = re.compile(r"(.)\1{2,}")
    return [pattern.sub(r"\1\1", token) for token in tokens]

"""
Remove all digits and special characters
"""
def remove_special(tokens):
  return [re.sub("(\\d|\\W)+", " ", token) for token in tokens]

"""
Remove blancs on words
"""
def remove_blanc(tokens):
    return [token.strip() for token in tokens]


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
        note = str(data['message'])
        tokens = nltk.word_tokenize(note)
        tokens = convert_letters(tokens)
        tokens = reduce_lengthening(tokens)
        tokens = remove_special(tokens)
        tokens = remove_blanc(tokens)
        tokens = [t for t in tokens if len(t) != 0]
        if len(tokens) > 30:
            continue
        note = ' '.join(tokens).strip()
        if len(note) == 0:
            continue
        if(pattern.search(note) == None):
            continue
        if(date[0] not in transactions_date_wise):
            transactions_date_wise[date[0]] = 0
        transactions_date_wise[date[0]] = transactions_date_wise[date[0]] + 1
        textual_transactions = textual_transactions + 1
        """
        msg = msg.strip()
        tokens = nltk.word_tokenize(msg)
        tokens = remove_blanc(tokens)
        string = ""
        for t in tokens:
            t = re.sub('[\W_]+', '', t)
            if(not (t == " ")):
                string = string + t
        if(date[0] not in transactions_date_wise):
            transactions_date_wise[date[0]] = 0
        if(string != "" and pattern.search(string)):
            transactions_date_wise[date[0]] = transactions_date_wise[date[0]] + 1
            textual_transactions = textual_transactions + 1
        """
    except TypeError:
        continue        
f.close()

outputfile.write("DATE #TEXTUAL_TRANSACTIONS \n")
for k,v in sorted(transactions_date_wise.items()):
    outputfile.write(str(k) + " " + str(v) + "\n")

outputfile.write("TOTAL NUMBER OF TRANSACTIONS ARE :" + str(transactions))
outputfile.write("\nTOTAL NUMBER OF TEXTUAL TRANSACTIONS IN ENGLISH ARE :" + str(textual_transactions))
outputfile.close()
