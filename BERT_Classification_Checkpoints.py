#============================================================================================================#
#*******************************   HOW TO RUN?  ************************************************************ #
# python3 BERT_Classification_Checkpoints.py <path to the input json file>  <path to the output file>    #
#*********************************************************************************************************** #
# Example:                                                                                                   #
# python3 BERT_Classification_Checkpoints.py /Users/rajattan/venmo/dummy.json ./transactions_date_wise.txt   #
#============================================================================================================#
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

#===============================================================#
MAX_LEN = 30
BATCH = 50000
CHECKPOINT_INTERVAL = 10

#===============================================================#
current = 0
numbatch = 0
transactions = 0
myr = [''] * BATCH
dates = [''] * BATCH
notes = [''] * BATCH
uname = [''] * BATCH
tuname = [''] * BATCH
#===============================================================#
cnt = 0
sender = {}
#receiver = {}
keywords = set()
stopwords = set()
date_category_stat = {}
date_personal_stat = {}

#===============================================================#
TEST_BATCH = 32
SENDER_FILE = "checkpoint/sender.txt"
#RECEIVER_FILE = "checkpoint/receiver.txt"
CHECKPOINT_FILE = "checkpoint/current.txt"
PATH_TO_STOPWORDS_LIST = "data/STOPWORDS.txt"
MODEL_FILE = "BERT_MODEL/checkpoint_EPOCHS_6a"
DATECAT_FILE = "checkpoint/date_category_stat.txt"
DATEPER_FILE = "checkpoint/date_personal_stat.txt"
PATH_TO_KEYWORDS_LIST = "data/UNIQ_KEYWORDS_LIST.txt"
#===============================================================#

pattern = re.compile(r"(.)\1{2,}")
pattern_rm1 = re.compile(r"(.)\1{1,}")
possible_personal = re.compile("\d")
english_ch = re.compile("[A-Za-z0-9]+")
email = re.compile("[^@]+@[^@]+\.[^@]+")
invc = re.compile("(((invoice|invc)(|s)|tracking)( \d|#|:| #| (\w)+\d))")
phno = re.compile("\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4}")
#acnt = re.compile("( id \d)|(password|passwd|paswd|pswd|pswrd|pwd|code)(:| is)|username:|(username|user name)(|s) |id:")
acnt = re.compile("((password|passwd|paswd|pswd|pswrd|pwd|code|username|user name|userid|user id|: password )(:| is |: | : | to (my|his|her|their| the) |\? | \? |! |!! )([a-zA-Z0-9$#~!@%^&*]+))|((([a-zA-Z0-9$#~!@%^&*]+) is ((my|his|her|their| the) (password|passwd|paswd|pswd|pswrd|pwd|code|username|user name|userid|user id))))")
#street = re.compile("\d+[ ](?:[A-Za-z0-9.-]+[ ]?)+(?:Avenue|Lane|Road|Boulevard|Drive|Street|Ave|Dr|Rd|Blvd|Ln|St)\.?")
adr = re.compile("( (avenue|lane|road|boulevard|drive|street|ave|dr|rd|blvd|ln|st|way)(,|\.| ))|( (al|ak|as|az|ar|ca|co|ct|de|dc|fm|fl|ga|gu|hi|id|il|in|ia|ks|ky|la|me|mh|md|ma|mi|mn|ms|mo|mt|ne|nv|nh|nj|nm|ny|nc|nd|mp|oh|ok|or|pw|pa|pr|ri|sc|sd|tn|tx|ut|vt|vi|va|wa|wv|wi|wy) \b\d{5}(?:-\d{4})?\b)")

#===============================================================#

if(len(sys.argv) != 3):
    print("==========================================================================")
    print("SORRY!! Please provide the path to the INPUT json file and the OUTPUT file")
    print("==========================================================================")
    print("Example: python3 BERT_Classification_script.py ./dummy.json ./output.txt  ")
    print("==========================================================================")
    sys.exit()

f = open(sys.argv[1])

if(os.path.exists(CHECKPOINT_FILE)):
    with open(CHECKPOINT_FILE, "rb") as myFile:
        current = pickle.load(myFile)
    print("RESUMING FROM " + str(current))
    if(current > 0):
        datecat = DATECAT_FILE
        with open(datecat, "rb") as myFile:
            date_category_stat = pickle.load(myFile)

        dateper = DATEPER_FILE
        with open(dateper, "rb") as myFile:
            date_personal_stat = pickle.load(myFile)

        '''
        send = SENDER_FILE + "." + str(current)
        if(not(os.path.exists(send))):
            send = SENDER_FILE
        with open(send, "rb") as myFile:
            sender = pickle.load(myFile)
        recv = RECEIVER_FILE + "." + str(current)
        if(not(os.path.exists(recv))):
            recv = RECEIVER_FILE
        with open(recv, "rb") as myFile:
            receiver = pickle.load(myFile)
        '''

        if(len(date_category_stat) == 0 or len(date_category_stat) == 0): # or len(sender) == 0 or len(receiver) == 0):
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
with open(PATH_TO_STOPWORDS_LIST,'r') as fp:
    for l in fp:
        stopwords.add(l.strip())


#===============================================================#
#c0 = c1 = [' '] * BATCH
cols_name = ['Date', 'Note','myr','uname','tuname','LGBTQ','ADULT_CONTENT', 'HEALTH', 'DRUGS_ALCOHOL_GAMBLING', 'RACE', 'VIOLENCE_CRIME', 'POLITICS', 'RELATION', 'LOCATION']
label_cols = cols_name[5:]  # drop 'Date' & 'Note' (the 2 leftmost columns)
sens_cols = ['LGBTQ','ADULT_CONTENT', 'HEALTH', 'DRUGS_ALCOHOL_GAMBLING', 'RACE', 'VIOLENCE_CRIME', 'POLITICS', 'RELATION', 'LOCATION','T']

# Account, Email, Invoice, Personal, Address, Total, Overlap
personal_cols = ['AC','E','I','PH','AD','P']
userfields = ['LGBTQ', 'ADULT_CONTENT', 'HEALTH', 'DRUGS_ALCOHOL_GAMBLING', 'RACE', 'VIOLENCE_CRIME', 'POLITICS', 'RELATION', 'LOCATION','AC','E','I','PH','AD','P','T','A']


bert_model_name = 'bert-base-uncased'
tokenizer = BertTokenizer.from_pretrained(bert_model_name, do_lower_case=True)

saved_model = BertClassifier(TFBertModel.from_pretrained(bert_model_name), len(label_cols))
saved_model.load_weights(MODEL_FILE)
time.sleep(5)
print("\n MODEL LOADED\n\n\n\n\n")

c2 = c3 = c4 = c5 = c6 = c7 = c8 = c9 = c10 = [0] * (BATCH - 1)
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
    if(adr.search(note)):
        return True
    return False
#===============================================================#
"""
Account Details
"""
def contains_acc(note):
    if(acnt.search(note)):
        return True
    return False
#===============================================================#
"""
Invoice Details
"""
def contains_invoice(note):
    if(invc.search(note)):
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
        if(transactions < current):
            continue
        
        #print(transactions,CHECKPOINT_INTERVAL)

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

        note = str(data['message'])
        origtokens = nltk.word_tokenize(note)
        tokens_partial = preprocessing(origtokens)
        tokens = preprocessing_cntd(tokens_partial)


        
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
        '''
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
        '''
        
        if(len(origtokens) > 30):
            continue
 
        
        if(month not in date_personal_stat):
            date_personal_stat[month] = {col:0 for col in personal_cols}
        per_flag = 0
        #overlap = 0


        if(possible_personal.search(note) or "@" in note or "#" in note or ":" in note):
            note = note.lower()
            if(contains_phn(note)):
                per_flag = 1
                #overlap = overlap + 1
                if('PH' not in date_personal_stat[month]):
                    date_personal_stat[month]['PH'] = 0
                date_personal_stat[month]['PH'] = date_personal_stat[month]['PH'] + 1
                sender[username]['dates'][month]['PH'] = sender[username]['dates'][month]['PH'] + 1

            if(contains_email(note)):
                per_flag = 1
                #overlap = overlap + 1
                if('E' not in date_personal_stat[month]):
                    date_personal_stat[month]['E'] = 0
                date_personal_stat[month]['E'] = date_personal_stat[month]['E'] + 1
                sender[username]['dates'][month]['E'] = sender[username]['dates'][month]['E'] + 1

            if(contains_invoice(note)):
                per_flag = 1
                #overlap =  overlap + 1
                if('I' not in date_personal_stat[month]):
                    date_personal_stat[month]['I'] = 0
                date_personal_stat[month]['I'] = date_personal_stat[month]['I'] + 1
                sender[username]['dates'][month]['I'] = sender[username]['dates'][month]['I'] + 1

            if(contains_address(note)):
                per_flag = 1
                #overlap = overlap + 1
                if('AD' not in date_personal_stat[month]):
                    date_personal_stat[month]['AD'] = 0
                date_personal_stat[month]['AD'] = date_personal_stat[month]['AD'] + 1
                sender[username]['dates'][month]['AD'] = sender[username]['dates'][month]['AD'] + 1

        if(contains_acc(note)):
            per_flag = 1
            #overlap = overlap + 1
            if('AC' not in date_personal_stat[month]):
                date_personal_stat[month]['AC'] = 0
            date_personal_stat[month]['AC'] = date_personal_stat[month]['AC'] + 1
            sender[username]['dates'][month]['AC'] = sender[username]['dates'][month]['AC'] + 1

            
        note = ' '.join(tokens).strip()

        if(len(note) == 0 or  english_ch.search(note) == None):# or (not(detect(note) == "en"))):
            continue

        flag = 0
        for t in tokens:
            if(t in keywords):
                flag = 1
                break 

        if(per_flag == 1):
            date_personal_stat[month]['P'] = date_personal_stat[month]['P'] + 1
            '''
            if(overlap > 1):
                date_personal_stat[month]['O'] = date_personal_stat[month]['O'] + 1      
            '''
            if(month not in sender[username]['dates']):
                sender[username]['dates'][month] = {col:0 for col in userfields}
            sender[username]['dates'][month]['P'] = sender[username]['dates'][month]['P'] + 1
            #sender[username]['dates'][month]['TO'] = sender[username]['dates'][month]['TO'] + 1

        if(flag == 0 and len(tokens) > 1):
            bigrams = [' '.join(list(t)) for t in list(nltk.bigrams(tokens))]
            for bi in bigrams:
                if(bi in keywords):
                    flag = 1
                    break
            tokens_partial = reduce_lengthening_rm1(tokens_partial)
            for t in tokens_partial:
                if(t in keywords):
                    flag = 1
                    break

        if(flag == 0):
            continue

        dates[cnt] = month
        notes[cnt] = note
        myr[cnt] = month
        uname[cnt] = username
        tuname[cnt] = tusername
        if cnt == (BATCH-1):
            current = transactions
            numbatch = numbatch + 1
            cnt = -1
            table = zip(dates, notes, myr, uname, tuname, c2, c3, c4, c5, c6, c7, c8, c9, c10)
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
                sen_flag = 1
                date = str(row['Date'])
                un = str(row['uname'])
                tun = str(row['tuname'])
                mon = str(row['myr'])

                if date not in date_category_stat:
                    date_category_stat[date] = {col:0 for col in sens_cols}
                for col in label_cols:
                    if row[col] == 0:
                        continue
                    date_category_stat[date][col] = date_category_stat[date][col] + 1

                    if(mon not in sender[un]['dates']):
                        sender[un]['dates'][mon] = {col:0 for col in userfields}
                    '''
                    if(mon not in receiver[tun]['dates']):
                        receiver[tun]['dates'][mon] = {col:0 for col in userfields}
                    '''
                    sender[un]['dates'][mon][col] = sender[un]['dates'][mon][col] + 1
                    #receiver[tun]['dates'][mon][col] = receiver[tun]['dates'][mon][col] + 1


                    if(sen_flag):
                        date_category_stat[date]['T'] = date_category_stat[date]['T'] + 1
                        sen_flag = 0
                        #sender[un]['dates'][mon]['S'] = sender[un]['dates'][mon]['S'] + 1
                        sender[un]['dates'][mon]['T'] = sender[un]['dates'][mon]['T'] + 1
                        '''
                        receiver[tun]['dates'][mon]['S'] = receiver[tun]['dates'][mon]['S'] + 1
                        receiver[tun]['dates'][mon]['T'] = receiver[tun]['dates'][mon]['T'] + 1
                        '''


            if(numbatch % CHECKPOINT_INTERVAL == 0):

                strcurrent = "." + str(current)
                datecat = DATECAT_FILE
                dateper  = DATEPER_FILE
                with open(CHECKPOINT_FILE, "wb") as myFile:
                    pickle.dump(current, myFile,protocol=pickle.HIGHEST_PROTOCOL)
                with open(datecat, "wb") as myFile:
                    pickle.dump(date_category_stat, myFile,protocol=pickle.HIGHEST_PROTOCOL)
                with open(dateper, "wb") as myFile:
                    pickle.dump(date_personal_stat, myFile,protocol=pickle.HIGHEST_PROTOCOL)
                send = SENDER_FILE + strcurrent
                with open(send, "wb") as myFile:
                    pickle.dump(sender, myFile,protocol=pickle.HIGHEST_PROTOCOL)
                '''
                recv = RECEIVER_FILE + strcurrent
                with open(recv, "wb") as myFile:
                    pickle.dump(receiver, myFile,protocol=pickle.HIGHEST_PROTOCOL)
                '''
                df_stat = pd.DataFrame.from_dict(date_category_stat, orient='index', columns=sens_cols)
                df_stat = df_stat.rename_axis('Date').reset_index()
                df_stat.to_csv(sys.argv[2] + "sen.output", index=False)


                df_stat = pd.DataFrame.from_dict(date_personal_stat, orient='index', columns=personal_cols)
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
                        '''
                        s = s + "|"
                        if(k in receiver and 'dates' in receiver[k]):
                            for kk,vv in receiver[k]['dates'].items():
                                s = s + str(kk) 
                                for kkk,vvv in sorted(vv.items()):
                                    s = s + "," + str(kkk) + ":" +  str(vvv)
                                s = s + ";"                                
                        ''' 
                        outputfile.write(s + "\n")
                    except:
                        continue

                outputfile.close()
                '''
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
                '''
                sender.clear()
                #receiver.clear()

        cnt = cnt + 1


    except Exception as e:
        print(e)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        continue        
f.close()

# Last batch
if cnt != 0:
    del dates[cnt:]
    del notes[cnt:]
    c2 = c3 = c4 = c5 = c6 = c7 = c8 = c9 = c10 = [0] * cnt
    table = zip(dates, notes, myr, uname, tuname, c2, c3, c4, c5, c6, c7, c8, c9, c10)
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

    for index, row in test_preds.iterrows():
        sen_flag = 1
        date = str(row['Date'])
        un = str(row['uname'])
        tun = str(row['tuname'])
        mon = str(row['myr'])

        if date not in date_category_stat:
            date_category_stat[date] = {col:0 for col in sens_cols}
        for col in label_cols:
            if row[col] == 0:
                continue
            date_category_stat[date][col] = date_category_stat[date][col] + 1

            if(mon not in sender[un]['dates']):
                sender[un]['dates'][mon] = {col:0 for col in userfields}
            '''
            if(mon not in receiver[tun]['dates']):
                receiver[tun]['dates'][mon] = {col:0 for col in userfields}
            '''
            sender[un]['dates'][mon][col] = sender[un]['dates'][mon][col] + 1
            #receiver[tun]['dates'][mon][col] = receiver[tun]['dates'][mon][col] + 1


            if(sen_flag):
                date_category_stat[date]['T'] = date_category_stat[date]['T'] + 1
                sen_flag = 0
                #sender[un]['dates'][mon]['S'] = sender[un]['dates'][mon]['S'] + 1
                sender[un]['dates'][mon]['T'] = sender[un]['dates'][mon]['T'] + 1
                #receiver[tun]['dates'][mon]['S'] = receiver[tun]['dates'][mon]['S'] + 1
                #receiver[tun]['dates'][mon]['T'] = receiver[tun]['dates'][mon]['T'] + 1

strcurrent = "." + str(transactions)
datecat = DATECAT_FILE
dateper  = DATEPER_FILE
with open(CHECKPOINT_FILE, "wb") as myFile:
    pickle.dump(transactions, myFile,protocol=pickle.HIGHEST_PROTOCOL)
with open(datecat, "wb") as myFile:
    pickle.dump(date_category_stat, myFile,protocol=pickle.HIGHEST_PROTOCOL)
with open(dateper, "wb") as myFile:
    pickle.dump(date_personal_stat, myFile,protocol=pickle.HIGHEST_PROTOCOL)
send = SENDER_FILE + strcurrent
with open(send, "wb") as myFile:
    pickle.dump(sender, myFile,protocol=pickle.HIGHEST_PROTOCOL)
'''
recv = RECEIVER_FILE + strcurrent
with open(recv, "wb") as myFile:
    pickle.dump(receiver, myFile,protocol=pickle.HIGHEST_PROTOCOL)
'''    
# Write stats

df_stat = pd.DataFrame.from_dict(date_category_stat, orient='index', columns=sens_cols)
df_stat = df_stat.rename_axis('Date').reset_index()
df_stat.to_csv(sys.argv[2] + "sen.output", index=False)


df_stat = pd.DataFrame.from_dict(date_personal_stat, orient='index', columns=personal_cols)
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
        '''
        s = s + "|"
        if(k in receiver and 'dates' in receiver[k]):
            for kk,vv in receiver[k]['dates'].items():
                s = s + str(kk)
                for kkk,vvv in sorted(vv.items()):
                    s = s + "," + str(kkk) + ":" +  str(vvv)
                s = s + ";"
        '''
        outputfile.write(s + "\n")
    except:
        continue

outputfile.close()

'''
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
'''
