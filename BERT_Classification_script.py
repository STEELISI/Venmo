#============================================================================================================#
#*******************************   HOW TO RUN?  ************************************************************ #
# python3 datewise_textual_transactions_count.py <path to the input json file>  <path to the output file>    #
#*********************************************************************************************************** #
# Example:                                                                                                   #
# python3 BERT_Classification_script.py /Users/rajattan/venmo/dummy.json ./transactions_date_wise.txt        #
#============================================================================================================#
import re
import sys
import json
import nltk
import numpy as np
import pandas as pd
import tensorflow as tf
from nltk import tokenize
from transformers import TFBertModel
from transformers import BertTokenizer
from tensorflow.keras.layers import Dense, Flatten

#===============================================================#
transactions = 0
textual_transactions = 0
transactions_date_wise = {}
pattern = re.compile("[A-Za-z0-9]+")
email = re.compile("[^@]+@[^@]+\.[^@]+")
phno = re.compile("\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4}")

#===============================================================#
class BertClassifier(tf.keras.Model):    
    def __init__(self, bert: TFBertModel, num_classes: int):
        super().__init__()
        self.bert = bert
        self.classifier = Dense(num_classes, activation='sigmoid')
        
    @tf.function
    def call(self, input_ids, attention_mask=None, token_type_ids=None, position_ids=None, head_mask=None):
        outputs = self.bert(input_ids,
                               attention_mask=attention_mask,
                               token_type_ids=token_type_ids,
                               position_ids=position_ids,
                               head_mask=head_mask)
        cls_output = outputs[1]
        cls_output = self.classifier(cls_output)
                
        return cls_output

#===============================================================#

BATCH = 10000
c1 = c2 = c3 = c4 = c5 = c6 = c7 = c8 = [0] * BATCH
cols_name = ['Date', 'Note', 'ADULT_CONTENT', 'HEALTH', 'DRUGS_ALCOHOL_GAMBLING', 'RACE', 'VIOLENCE_CRIME', 'POLITICS', 'RELATION', 'LOCATION']
label_cols = cols_name[2:]  # drop 'Date' & 'Note' (the 2 leftmost columns)

bert_model_name = 'bert-base-uncased'
tokenizer = BertTokenizer.from_pretrained(bert_model_name, do_lower_case=True)
model = BertClassifier(TFBertModel.from_pretrained(bert_model_name), len(label_cols))
#model.load_weights('')

date_category_stat = {}  # number of each category for each day

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
    pattern = re.compile(r"(.)\1{2,}")
    return [pattern.sub(r"\1\1", token) for token in tokens]
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
Phone number regex
"""
def contains_phn(note):
    if(phno.search(note)):
        return True
    return False
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
Preprocessing Work 
"""
def preprocessing(note):
    tokens = nltk.word_tokenize(note)
    tokens = convert_letters(tokens)
    tokens = reduce_lengthening(tokens)
    tokens = remove_special(tokens)
    tokens = remove_blanc(tokens)
    tokens = [t for t in tokens if len(t) != 0]
    return tokens
#===============================================================#
"""
Build prediction table
"""
def build_table(c0, c1):
    table = zip(c0, c1, c2, c3, c4, c5, c6, c7, c8, c9)
    table = list(table)
    return [list(r) for r in table]

#===============================================================#
"""
Build dataset
"""
def create_dataset(data_tuple, epochs=1, batch_size=32):
    dataset = tf.data.Dataset.from_tensor_slices(data_tuple)
    dataset = dataset.repeat(epochs)
    dataset = dataset.batch(batch_size)
    return dataset
#===============================================================#
"""
BERT encoder
"""
def encoder(notes, tokenizer):
    token_ids = []
    masks = []
    for msg in notes:
        encoded_dict = tokenizer.encode_plus(
                            msg,    # note to encode.
                            add_special_tokens=True,    # Add '[CLS]' and '[SEP]'.
                            max_length=12,  # Pad & truncate all sentences.
                            padding='max_length',
                            return_attention_mask=True  # Construct attn. mask.
                        )
        token_ids.append(encoded_dict['input_ids'])
        masks.append(encoded_dict['attention_mask'])
    return token_ids, masks
#===============================================================#


if(len(sys.argv) != 3):
    print("==========================================================================")
    print("SORRY!! Please provide the path to the INPUT json file and the OUTPUT file")
    print("==========================================================================")
    print("Example: python3 BERT_Classification_script.py ./dummy.json ./output.txt  ")
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
        tokens = preprocessing(note)

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
