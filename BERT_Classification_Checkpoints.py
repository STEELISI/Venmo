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
import pickle
import numpy as np
import pandas as pd
import tensorflow as tf
from nltk import tokenize
from transformers import TFBertModel
from transformers import BertTokenizer
from tensorflow.keras.layers import Dense, Flatten

#===============================================================#
MAX_LEN = 10
BATCH = 50000
TEST_BATCH = 32
transactions = 0
dates = [''] * BATCH
notes = [''] * BATCH
uname = [''] * BATCH
tuname = [''] * BATCH

cnt = 0 # counter
keywords = set()
date_category_stat = {}  # number of each category for each day
date_personal_stat = {}
sender = {}
receiver = {}

CHECKPOINT_INTERVAL = 100000
MODEL_FILE = 'BERT_MODEL/checkpoint_EPOCHS_6a'
PATH_TO_KEYWORDS_LIST = 'data/UNIQ_KEYWORDS_LIST.txt'

english_ch = re.compile("[A-Za-z0-9]+")
email = re.compile("[^@]+@[^@]+\.[^@]+")
phno = re.compile("\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4}")
add = re.compile("\d+[ ](?:[A-Za-z0-9.-]+[ ]?)+(?:Avenue|Lane|Road|Boulevard|Drive|Street|Ave|Dr|Rd|Blvd|Ln|St)\.?")

#===============================================================#

if(len(sys.argv) != 3):
    print("==========================================================================")
    print("SORRY!! Please provide the path to the INPUT json file and the OUTPUT file")
    print("==========================================================================")
    print("Example: python3 BERT_Classification_script.py ./dummy.json ./output.txt  ")
    print("==========================================================================")
    sys.exit()

f = open(sys.argv[1])

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
c0 = c1 = [' '] * BATCH
c2 = c3 = c4 = c5 = c6 = c7 = c8 = c9 = [0] * BATCH
cols_name = ['Date', 'Note','uname','tuname','ADULT_CONTENT', 'HEALTH', 'DRUGS_ALCOHOL_GAMBLING', 'RACE', 'VIOLENCE_CRIME', 'POLITICS', 'RELATION', 'LOCATION']
label_cols = cols_name[4:]  # drop 'Date' & 'Note' (the 2 leftmost columns)
sens_cols = ['ADULT_CONTENT', 'HEALTH', 'DRUGS_ALCOHOL_GAMBLING', 'RACE', 'VIOLENCE_CRIME', 'POLITICS', 'RELATION', 'LOCATION','T']

personal_cols = ['A','E','I','L','P','T']
userfields = ['S','P','T','A']


bert_model_name = 'bert-base-uncased'
tokenizer = BertTokenizer.from_pretrained(bert_model_name, do_lower_case=True)

saved_model = BertClassifier(TFBertModel.from_pretrained(bert_model_name), len(label_cols))
saved_model.load_weights(MODEL_FILE)
print("\n MODEL LOADED\n\n\n\n\n")


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
Contains address
"""
def contains_address(note):
    if(add.search(note)):
        return True
    return False
#===============================================================#
"""
Account Details
"""
def contains_acc(note):
    if("password" in note or "passwd" in note or "user id" in note or "userid" in note or "username" in note):
        return True
    return False
#===============================================================#
"""
Invoice Details
"""
def contains_invoice(note):
    if("invoice" in note or "tracking" in note):
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
Build dataset
"""
'''
def create_dataset(data_tuple, epochs=1, batch_size=32):
    dataset = tf.data.Dataset.from_tensor_slices(data_tuple)
    dataset = dataset.repeat(epochs)
    dataset = dataset.batch(batch_size)
    return dataset
'''

def create_dataset(data_tuple, epochs=1, batch_size=32, buffer_size=100, train=False):
    dataset = tf.data.Dataset.from_tensor_slices(data_tuple)
    if train:
        dataset = dataset.shuffle(buffer_size=buffer_size)
    dataset = dataset.repeat(epochs)
    dataset = dataset.batch(batch_size)
    if train:
        dataset = dataset.prefetch(1)

    return dataset

#===============================================================#
with open(PATH_TO_KEYWORDS_LIST,'r') as fp:
    for l in fp:
        keywords.add(''.join(convert_letters(l.strip())))


#===============================================================#
#   MAIN FLOW                                                   #
#===============================================================#

for line in f:
    data = json.loads(line)
    transactions = transactions + 1
    try:
        if(transactions%CHECKPOINT_INTERVAL == 0):
            with open("checkpoint/datewise_transactions.txt", "wb") as myFile:
                pickle.dump(date_category_stat, myFile)
        if(data is None or data['created_time'] is None):
            continue
        datetime = str(data['created_time'])
        date = datetime.split("T")
        if(data is None or data['message'] is None or data['message'] == ""):
            continue
        note = str(data['message'])
        tokens = nltk.word_tokenize(note)
        tokens = preprocessing(note)

        if('actor' not in data or 'username' not in data['actor'] or 'transactions' not in data or data['transactions'] is None  or 'target' not in data['transactions'][0] or 'username' not in data['transactions'][0]['target']):
            continue

        username = data['actor']['username']
        tusername = data['transactions'][0]['target']['username']


        if(username not in sender):
            sender[username] = {}
            if('date_created' in data['actor']):
                s = str(data['actor']['created_time'])
                d = s.split("T")
                sender[username]['joined'] = d[0]
            sender[username]['dates'] = {}
            if(date[0] not in sender[username]['dates']):
                sender[username]['dates'][date[0]] = {col:0 for col in userfields}
            sender[username]['dates'][date[0]]['A'] = sender[username]['dates'][date[0]]['A'] + 1


        if(tusername not in receiver):
            receiver[tusername] = {}
            if('date_created' in data['transactions'][0]['target']):
                s = str(data['transactions'][0]['target']['created_time'])
                d = s.split("T")
                receiver[tusername]['joined'] = d[0]
            receiver[tusername]['dates'] = {}
            if(date[0] not in receiver[tusername]['dates']):
                receiver[tusername]['dates'][date[0]] = {col:0 for col in userfields}
            receiver[tusername]['dates'][date[0]]['A'] = receiver[tusername]['dates'][date[0]]['A'] + 1

        if(len(tokens) > 50):
            continue
  


        if(date[0] not in date_personal_stat):
            date_personal_stat[date[0]] = {col:0 for col in personal_cols}
        per_flag = 0

        if(contains_phn(note)):
            per_flag = 1
            if('P' not in date_personal_stat[date[0]]):
                date_personal_stat[date[0]]['P'] = 0
            date_personal_stat[date[0]]['P'] = date_personal_stat[date[0]]['P'] + 1

        if(contains_email(note)):
            per_flag = 1
            if('E' not in date_personal_stat[date[0]]):
                date_personal_stat[date[0]]['E'] = 0
            date_personal_stat[date[0]]['E'] = date_personal_stat[date[0]]['E'] + 1

        if(contains_acc(note)):
            per_flag = 1
            if('A' not in date_personal_stat[date[0]]):
                date_personal_stat[date[0]]['A'] = 0
            date_personal_stat[date[0]]['A'] = date_personal_stat[date[0]]['A'] + 1


        if(contains_invoice(note)):
            per_flag = 1
            if('I' not in date_personal_stat[date[0]]):
                date_personal_stat[date[0]]['I'] = 0
            date_personal_stat[date[0]]['I'] = date_personal_stat[date[0]]['I'] + 1

        if(contains_address(note)):
            per_flag = 1
            if('L' not in date_personal_stat[date[0]]):
                date_personal_stat[date[0]]['L'] = 0
            date_personal_stat[date[0]]['L'] = date_personal_stat[date[0]]['L'] + 1



        note = ' '.join(tokens).strip()
        if(english_ch.search(note) == None or len(note) == 0):
            continue

        bigrams = [' '.join(list(t)) for t in list(nltk.bigrams(tokens))]
        flag = 0
        for t in tokens:
            if(t == "id" or t == "code"):
                per_flag = 1
                if('A' not in date_personal_stat[date[0]]):
                    date_personal_stat[date[0]]['A'] = 0
                date_personal_stat[date[0]]['A'] = date_personal_stat[date[0]]['A'] + 1
         

            if(t in keywords):
                flag = 1
                break 


        if(per_flag):
            date_personal_stat[date[0]]['T'] = date_personal_stat[date]['T'] + 1
            if(date[0] not in sender[username]['dates']):
                sender[username]['dates'][date[0]] = {col:0 for col in userfields}
            sender[username]['dates'][date[0]]['P'] = sender[username]['dates'][date[0]]['P'] + 1
            sender[username]['dates'][date[0]]['T'] = sender[username]['dates'][date[0]]['T'] + 1
            if(date[0] not in receiver[tusername]['dates']):
                receiver[tusername]['dates'][date[0]] = {col:0 for col in userfields}
            receiver[tusername]['dates'][date[0]]['P'] = receiver[tusername]['dates'][date[0]]['P'] + 1
            receiver[tusername]['dates'][date[0]]['T'] = receiver[tusername]['dates'][date[0]]['T'] + 1
            
            

        if(flag == 0):
            for bi in bigrams:
                if(bi in keywords):
                    flag = 1
                    break
        if(flag == 0):
            continue

        dates[cnt] = date[0]
        notes[cnt] = note
        
        if cnt == (BATCH-1):
            # form dataset
            c2 = c3 = c4 = c5 = c6 = c7 = c8 = c9 = [0] * cnt
            table = zip(dates, notes, c2, c3, c4, c5, c6, c7, c8, c9)
            table = list(table)
            table = [list(r) for r in table]
            test_preds = pd.DataFrame(np.array(table), columns=cols_name)

            test_input_ids = []
            test_attention_masks = []

            for sent in test_preds['Note']:
                encoded_dict = tokenizer.encode_plus(
                                    sent,                      # Sentence to encode.
                                    add_special_tokens = True, # Add '[CLS]' and '[SEP]'
                                    truncation='longest_first',
                                    max_length = MAX_LEN,           # Pad & truncate all sentences.
                                    pad_to_max_length = True,
                                    return_attention_mask = True,   # Construct attn. masks.
                                    # return_tensors = 'tf',     # Return tensorflow tensor.
                               )
                test_input_ids.append(encoded_dict['input_ids'])
                test_attention_masks.append(encoded_dict['attention_mask'])

            test_dataset = create_dataset((test_input_ids, test_attention_masks), epochs=1, batch_size=32, train=False)
            # prediction
            for i, (token_ids, masks) in enumerate(test_dataset):
                start = i * TEST_BATCH
                end = (i+1) * TEST_BATCH - 1
                predictions = saved_model(token_ids, attention_mask=masks).numpy()
                binary_predictions = np.where(predictions > 0.5, 1, 0)
                test_preds.loc[start:end, label_cols] = binary_predictions

            # update stats
            for index, row in test_preds.iterrows():
                #update(row)
                sen_flag = 1
                per_flag = 1
                date = str(row['Date'])
                un = str(row['uname'])
                tun = str(row['tuname'])

                if date not in date_category_stat:
                    date_category_stat[date] = {col:0 for col in sens_cols}
                for col in label_cols:
                    if row[col] == 0:
                        continue
                    date_category_stat[date][col] = date_category_stat[date][col] + 1
                    if(per_flag and (col == 'RELATION' or col == 'LOCATION')):
                        date_personal_stat[date]['T'] = date_personal_stat[date]['T'] + 1
                        per_flag = 0
                        if(date not in sender[un]['dates']):
                            sender[un]['dates'][date] = {col:0 for col in userfields}
                        sender[un]['dates'][date]['P'] = sender[un]['dates'][date]['P'] + 1
                        sender[un]['dates'][date]['T'] = sender[un]['dates'][date]['T'] + 1
                        if(date not in receiver[tun]['dates']):
                            receiver[tun]['dates'][date] = {col:0 for col in userfields}
                        receiver[tun]['dates'][date]['P'] = receiver[tun]['dates'][date]['P'] + 1
                        receiver[tun]['dates'][date]['T'] = receiver[tun]['dates'][date]['T'] + 1



                    elif(sen_flag and not(col == 'RELATION' or col == 'LOCATION')):
                         date_category_stat[date]['T'] = date_category_stat[date]['T'] + 1
                         sen_flag = 0
                        if(date not in sender[un]['dates']):
                            sender[un]['dates'][date] = {col:0 for col in userfields}
                        sender[un]['dates'][date]['S'] = sender[un]['dates'][date]['S'] + 1
                        sender[un]['dates'][date]['T'] = sender[un]['dates'][date]['T'] + 1

                        if(date not in receiver[tun]['dates']):
                            receiver[tun]['dates'][date] = {col:0 for col in userfields}
                        receiver[tun]['dates'][date]['S'] = receiver[tun]['dates'][date]['S'] + 1
                        receiver[tun]['dates'][date]['T'] = receiver[tun]['dates'][date]['T'] + 1
                    
            # reset counter
            cnt = -1
            
        cnt = cnt + 1


    except:
        continue        
f.close()

# Last batch
if cnt != 0:
    del dates[cnt:]
    del notes[cnt:]
    c2 = c3 = c4 = c5 = c6 = c7 = c8 = c9 = [0] * cnt
    table = zip(dates, notes, c2, c3, c4, c5, c6, c7, c8, c9)
    table = list(table)
    table = [list(r) for r in table]
    test_preds = pd.DataFrame(np.array(table), columns=cols_name)
    test_input_ids = []
    test_attention_masks = []

    for sent in test_preds['Note']:
        encoded_dict = tokenizer.encode_plus(
                            sent,                      # Sentence to encode.
                            add_special_tokens = True, # Add '[CLS]' and '[SEP]'
                            truncation='longest_first',
                            max_length = MAX_LEN,           # Pad & truncate all sentences.
                            pad_to_max_length = True,
                            return_attention_mask = True,   # Construct attn. masks.
                            # return_tensors = 'tf',     # Return tensorflow tensor.
                       )
        test_input_ids.append(encoded_dict['input_ids'])
        test_attention_masks.append(encoded_dict['attention_mask'])


    test_dataset = create_dataset((test_input_ids, test_attention_masks), epochs=1, batch_size=32, train=False)
    # prediction
    for i, (token_ids, masks) in enumerate(test_dataset):
        start = i * TEST_BATCH
        end = (i+1) * TEST_BATCH - 1
        predictions = saved_model(token_ids, attention_mask=masks).numpy()
        binary_predictions = np.where(predictions > 0.5, 1, 0)
        test_preds.loc[start:end, label_cols] = binary_predictions
    # update stat
    for index, row in test_preds.iterrows():
        sen_flag = 1
        per_flag = 1
        date = str(row['Date'])
        un = str(row['uname'])
        tun = str(row['tuname'])
        if date not in date_category_stat:
            date_category_stat[date] = {col:0 for col in sens_cols}
        for col in label_cols:
            if row[col] == 0:
                continue
            date_category_stat[date][col] = date_category_stat[date][col] + 1
            if(per_flag and (col == 'RELATION' or col == 'LOCATION')):
                date_personal_stat[date]['T'] = date_personal_stat[date]['T'] + 1
                per_flag = 0
                if(date not in sender[un]['dates']):
                    sender[un]['dates'][date] = {col:0 for col in userfields}
                sender[un]['dates'][date]['P'] = sender[un]['dates'][date]['P'] + 1
                sender[un]['dates'][date]['T'] = sender[un]['dates'][date]['T'] + 1
                if(date not in receiver[tun]['dates']):
                    receiver[tun]['dates'][date] = {col:0 for col in userfields}
                receiver[tun]['dates'][date]['P'] = receiver[tun]['dates'][date]['P'] + 1
                receiver[tun]['dates'][date]['T'] = receiver[tun]['dates'][date]['T'] + 1


            elif(sen_flag and not(col == 'RELATION' or col == 'LOCATION')):
                date_category_stat[date]['T'] = date_category_stat[date]['T'] + 1
                sen_flag = 0

                if(date not in sender[un]['dates']):
                    sender[un]['dates'][date] = {col:0 for col in userfields}
                sender[un]['dates'][date]['S'] = sender[un]['dates'][date]['S'] + 1
                sender[un]['dates'][date]['T'] = sender[un]['dates'][date]['T'] + 1

                if(date not in receiver[tun]['dates']):
                    receiver[tun]['dates'][date] = {col:0 for col in userfields}
                receiver[tun]['dates'][date]['S'] = receiver[tun]['dates'][date]['S'] + 1
                receiver[tun]['dates'][date]['T'] = receiver[tun]['dates'][date]['T'] + 1



    
# Write stats
df_stat = pd.DataFrame.from_dict(date_category_stat, orient='index', columns=sens_cols)
df_stat = df_stat.rename_axis('Date').reset_index()
df_stat.to_csv(sys.argv[2] + "sen.output", index=False)


df_stat = pd.DataFrame.from_dict(date_personal_stat, orient='index', columns=personal_cols)
df_stat = df_stat.rename_axis('Date').reset_index()
df_stat.to_csv(sys.argv[2] + "per.output", index=False)

outputfile = open(sys.argv[2],"w")

scnt=-1
for k,v in sender.items():
    if(v is None):
        continue
    scnt = scnt + 1
    s = ""
    try:
        s = str(scnt) + "|"
        if('joined' in sender[k]):
            s = s + str(sender[username]['joined'])
        s = s + "|"

        if('dates' in sender[k]):
            for kk,vv in sender[k]['dates'].items():
                s = s + str(kk) + "," +  str(sender[k]['dates'][kk]['S']) + "," + str(sender[k]['dates'][kk]['P']) + "," + str(sender[k]['dates'][kk]['T']) + "," + str(sender[k]['dates'][kk]['A']) + ";"
        
        if(k in receiver and 'dates' in receiver[k]):
            for kk,vv in receiver[k]['dates'].items():
                s = s + str(kk) + "," +  str(receiver[k]['dates'][kk]['S']) + "," + str(receiver[k]['dates'][kk]['P']) + "," + str(receiver[k]['dates'][kk]['T']) + "," + str(receiver[k]['dates'][kk]['A']) + ";"
    
        
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
            s = s + str(receiver[username]['joined'])
        s = s + "|"

        if('dates' in receiver[k]):
            for kk,vv in receiver[k]['dates'].items():
                s = s + str(kk) + "," +  str(receiver[k]['dates'][kk]['S']) + "," + str(receiver[k]['dates'][kk]['P']) + "," + str(receiver[k]['dates'][kk]['T']) + "," + str(receiver[k]['dates'][kk]['A']) + ";"