#==============================================================================================================================================================#
#*******************************   HOW TO RUN?  ***************************************************************************************************************#
# python3 BERT_Classification_Checkpoints_distributed.py <path to the input json file> <path to the output file> <range-start> <range-end> <checkpoint path>   #
#**************************************************************************************************************************************************************#
# Example:                                                                                                                                                     #
# python3 BERT_Classification_Checkpoints_distributed.py /Users/rajattan/venmo/dummy.json outputfolder/samp 120000000 150000000 checkpoint_instance_1          #
#==============================================================================================================================================================#
import re
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
if(len(sys.argv) != 6):
    print("==================================================================================================================================================")
    print("SORRY!! Please provide the path to the INPUT json file, the OUTPUT file, start range, end range and checkpoint_path                               ")
    print("==================================================================================================================================================")
    print("Example: python3 BERT_Classification_Checkpoints.py /Users/rajattan/venmo/dummy.json outputfolder/samp 120000000 150000000 checkpoint_instance_1  ")
    print("==================================================================================================================================================")
    sys.exit()

#===============================================================#
MAX_LEN = 10
BATCH = 50000
INTERMEDIADTE = 10

#===============================================================#
current = 0
transactions = 0
myr = [''] * BATCH
dates = [''] * BATCH
notes = [''] * BATCH
uname = [''] * BATCH
tuname = [''] * BATCH
#===============================================================#
cnt = 0
sender = {}
receiver = {}
keywords = set()
stopwords = set()
date_category_stat = {}
date_personal_stat = {}
ending_point = int(str(sys.argv[4]))
starting_point = int(str(sys.argv[3]))

#===============================================================#
TEST_BATCH = 32
PATH_TO_STOPWORDS_LIST = "data/STOPWORDS.txt"
MODEL_FILE = "BERT_MODEL/checkpoint_EPOCHS_6a"
SENDER_FILE = str(sys.argv[5]) + "/sender.txt"
RECEIVER_FILE = str(sys.argv[5]) + "/receiver.txt"
CHECKPOINT_FILE = str(sys.argv[5]) + "/current.txt"
PATH_TO_KEYWORDS_LIST = "data/UNIQ_KEYWORDS_LIST.txt"
DATECAT_FILE = str(sys.argv[5]) + "/date_category_stat.txt"
DATEPER_FILE = str(sys.argv[5]) + "/date_personal_stat.txt"
#===============================================================#

pattern = re.compile(r"(.)\1{2,}")
pattern_rm1 = re.compile(r"(.)\1{1,}")
possible_personal = re.compile("\d")
english_ch = re.compile("[A-Za-z0-9]+")
email = re.compile("[^@]+@[^@]+\.[^@]+")
invc = re.compile("(((invoice|invc)(|s)|tracking)( \d|#|:| #| (\w)+\d))")
phno = re.compile("\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4}")
acnt = re.compile("( id \d)|(password|passwd|paswd|pswd|pswrd|pwd|code)(:| is)|username:|(username|user name)(|s) |id:")
#street = re.compile("\d+[ ](?:[A-Za-z0-9.-]+[ ]?)+(?:Avenue|Lane|Road|Boulevard|Drive|Street|Ave|Dr|Rd|Blvd|Ln|St)\.?")
adr = re.compile("( (Avenue|Lane|Road|Boulevard|Drive|Street|Ave|Dr|Rd|Blvd|Ln|St|Way)(,|.| ))|( (AL|AK|AS|AZ|AR|CA|CO|CT|DE|DC|FM|FL|GA|GU|HI|ID|IL|IN|IA|KS|KY|LA|ME|MH|MD|MA|MI|MN|MS|MO|MT|NE|NV|NH|NJ|NM|NY|NC|ND|MP|OH|OK|OR|PW|PA|PR|RI|SC|SD|TN|TX|UT|VT|VI|VA|WA|WV|WI|WY) \b\d{5}(?:-\d{4})?\b)")

#===============================================================#

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

print(current, starting_point, ending_point)
if(starting_point > current):
    current = starting_point

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
cols_name = ['Date', 'Note','myr','uname','tuname','ADULT_CONTENT', 'HEALTH', 'DRUGS_ALCOHOL_GAMBLING', 'RACE', 'VIOLENCE_CRIME', 'POLITICS', 'RELATION', 'LOCATION']
label_cols = cols_name[5:]  # drop 'Date' & 'Note' (the 2 leftmost columns)
sens_cols = ['ADULT_CONTENT', 'HEALTH', 'DRUGS_ALCOHOL_GAMBLING', 'RACE', 'VIOLENCE_CRIME', 'POLITICS', 'RELATION', 'LOCATION','T']

personal_cols = ['A','E','I','P','T']
userfields = ['S','P','T','A']


bert_model_name = 'bert-base-uncased'
tokenizer = BertTokenizer.from_pretrained(bert_model_name, do_lower_case=True)

saved_model = BertClassifier(TFBertModel.from_pretrained(bert_model_name), len(label_cols))
saved_model.load_weights(MODEL_FILE)
time.sleep(5)
print("\n MODEL LOADED\n\n\n\n\n")

c2 = c3 = c4 = c5 = c6 = c7 = c8 = c9 = [0] * (BATCH - 1)
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
        if(transactions > ending_point):
            break
        
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
        #print(sender[username]['dates'][month]['A'])

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

        
        if(len(origtokens) > 30):
            continue
 
        
        if(date[0] not in date_personal_stat):
            date_personal_stat[date[0]] = {col:0 for col in personal_cols}
        per_flag = 0


        if(possible_personal.search(note) or "@" in note or "#" in note):
            note = note.lower()
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

        if(contains_acc(note)):
            per_flag = 1
            if('A' not in date_personal_stat[date[0]]):
                date_personal_stat[date[0]]['A'] = 0
            date_personal_stat[date[0]]['A'] = date_personal_stat[date[0]]['A'] + 1

            
        note = ' '.join(tokens).strip()

        if(len(note) == 0 or  english_ch.search(note) == None):# or (not(detect(note) == "en"))):
            continue

        flag = 0
        for t in tokens:
            if(t in keywords):
                flag = 1
                break 

        if(per_flag == 1):
            date_personal_stat[date[0]]['T'] = date_personal_stat[date]['T'] + 1
            if(month not in sender[username]['dates']):
                sender[username]['dates'][month] = {col:0 for col in userfields}
            sender[username]['dates'][month]['P'] = sender[username]['dates'][month]['P'] + 1
            sender[username]['dates'][month]['T'] = sender[username]['dates'][month]['T'] + 1
            if(month not in receiver[tusername]['dates']):
                receiver[tusername]['dates'][month] = {col:0 for col in userfields}
            receiver[tusername]['dates'][month]['P'] = receiver[tusername]['dates'][month]['P'] + 1
            receiver[tusername]['dates'][month]['T'] = receiver[tusername]['dates'][month]['T'] + 1
            

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

        dates[cnt] = date[0]
        notes[cnt] = note
        myr[cnt] = month
        uname[cnt] = username
        tuname[cnt] = tusername
        if cnt == (BATCH-1):
            INTERMEDIADTE = INTERMEDIADTE + 1
            current = transactions
            cnt = -1
            table = zip(dates, notes, myr, uname, tuname, c2, c3, c4, c5, c6, c7, c8, c9)
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
                mon = str(row['myr'])

                if date not in date_category_stat:
                    date_category_stat[date] = {col:0 for col in sens_cols}
                for col in label_cols:
                    if row[col] == 0:
                        continue
                    date_category_stat[date][col] = date_category_stat[date][col] + 1
                    if(per_flag and (col == 'RELATION' or col == 'LOCATION')):
                        date_personal_stat[date]['T'] = date_personal_stat[date]['T'] + 1
                        per_flag = 0
                        if(mon not in sender[un]['dates']):
                            sender[un]['dates'][mon] = {col:0 for col in userfields}
                        sender[un]['dates'][mon]['P'] = sender[un]['dates'][mon]['P'] + 1
                        sender[un]['dates'][mon]['T'] = sender[un]['dates'][mon]['T'] + 1
                        if(date not in receiver[tun]['dates']):
                            receiver[tun]['dates'][mon] = {col:0 for col in userfields}
                        receiver[tun]['dates'][mon]['P'] = receiver[tun]['dates'][mon]['P'] + 1
                        receiver[tun]['dates'][mon]['T'] = receiver[tun]['dates'][mon]['T'] + 1



                    elif(sen_flag and not(col == 'RELATION' or col == 'LOCATION')):
                        date_category_stat[date]['T'] = date_category_stat[date]['T'] + 1
                        sen_flag = 0
                        if(mon not in sender[un]['dates']):
                            sender[un]['dates'][mon] = {col:0 for col in userfields}
                        sender[un]['dates'][mon]['S'] = sender[un]['dates'][mon]['S'] + 1
                        sender[un]['dates'][mon]['T'] = sender[un]['dates'][mon]['T'] + 1

                        if(mon not in receiver[tun]['dates']):
                            receiver[tun]['dates'][mon] = {col:0 for col in userfields}
                        receiver[tun]['dates'][mon]['S'] = receiver[tun]['dates'][mon]['S'] + 1
                        receiver[tun]['dates'][mon]['T'] = receiver[tun]['dates'][mon]['T'] + 1


            if(INTERMEDIADTE%3 == 0):
                '''
                with open("checkpoint/current.txt", "wb") as myFile:
                    pickle.dump(current, myFile,protocol=pickle.HIGHEST_PROTOCOL)
                with open("checkpoint/date_category_stat.txt", "wb") as myFile:
                    pickle.dump(date_category_stat, myFile,protocol=pickle.HIGHEST_PROTOCOL)
                with open("checkpoint/date_personal_stat.txt", "wb") as myFile:
                    pickle.dump(date_personal_stat, myFile,protocol=pickle.HIGHEST_PROTOCOL)
                with open("checkpoint/sender.txt", "wb") as myFile:
                    pickle.dump(sender, myFile,protocol=pickle.HIGHEST_PROTOCOL)
                with open("checkpoint/receiver.txt", "wb") as myFile:
                    pickle.dump(receiver, myFile,protocol=pickle.HIGHEST_PROTOCOL)
                '''

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
                recv = RECEIVER_FILE + strcurrent
                with open(recv, "wb") as myFile:
                    pickle.dump(receiver, myFile,protocol=pickle.HIGHEST_PROTOCOL)

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
                                s = s + str(kk) + "," +  str(sender[k]['dates'][kk]['S']) + "," + str(sender[k]['dates'][kk]['P']) + "," + str(sender[k]['dates'][kk]['T']) + "," + str(sender[k]['dates'][kk]['A']) + ";"

                        s = s + "|"
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
                            s = s + str(receiver[k]['joined'])
                        s = s + "|"

                        if('dates' in receiver[k]):
                            for kk,vv in receiver[k]['dates'].items():
                                s = s + str(kk) + "," +  str(receiver[k]['dates'][kk]['S']) + "," + str(receiver[k]['dates'][kk]['P']) + "," + str(receiver[k]['dates'][kk]['T']) + "," + str(receiver[k]['dates'][kk]['A']) + ";"

                        outputfile1.write(s + "\n")
                    except:
                        continue
       
                outputfile1.close()
                sender.clear()
                receiver.clear()

            # reset counter
            #cnt = -1
                 
        cnt = cnt + 1


    except:
        continue        
f.close()

# Last batch
if cnt != 0:
    del dates[cnt:]
    del notes[cnt:]
    c2 = c3 = c4 = c5 = c6 = c7 = c8 = c9 = [0] * cnt
    table = zip(dates, notes, myr, uname, tuname, c2, c3, c4, c5, c6, c7, c8, c9)
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
        mon = str(row['myr'])
        if date not in date_category_stat:
            date_category_stat[date] = {col:0 for col in sens_cols}
        for col in label_cols:
            if row[col] == 0:
                continue
            date_category_stat[date][col] = date_category_stat[date][col] + 1
            if(per_flag and (col == 'RELATION' or col == 'LOCATION')):
                date_personal_stat[date]['T'] = date_personal_stat[date]['T'] + 1
                per_flag = 0
                if(mon not in sender[un]['dates']):
                    sender[un]['dates'][mon] = {col:0 for col in userfields}
                sender[un]['dates'][mon]['P'] = sender[un]['dates'][mon]['P'] + 1
                sender[un]['dates'][mon]['T'] = sender[un]['dates'][mon]['T'] + 1
                if(mon not in receiver[tun]['dates']):
                    receiver[tun]['dates'][mon] = {col:0 for col in userfields}
                receiver[tun]['dates'][mon]['P'] = receiver[tun]['dates'][mon]['P'] + 1
                receiver[tun]['dates'][mon]['T'] = receiver[tun]['dates'][mon]['T'] + 1


            elif(sen_flag and not(col == 'RELATION' or col == 'LOCATION')):
                date_category_stat[date]['T'] = date_category_stat[date]['T'] + 1
                sen_flag = 0

                if(mon not in sender[un]['dates']):
                    sender[un]['dates'][mon] = {col:0 for col in userfields}
                sender[un]['dates'][mon]['S'] = sender[un]['dates'][mon]['S'] + 1
                sender[un]['dates'][mon]['T'] = sender[un]['dates'][mon]['T'] + 1

                if(mon not in receiver[tun]['dates']):
                    receiver[tun]['dates'][mon] = {col:0 for col in userfields}
                receiver[tun]['dates'][mon]['S'] = receiver[tun]['dates'][mon]['S'] + 1
                receiver[tun]['dates'][mon]['T'] = receiver[tun]['dates'][mon]['T'] + 1



    
# Write stats

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
                s = s + str(kk) + "," +  str(sender[k]['dates'][kk]['S']) + "," + str(sender[k]['dates'][kk]['P']) + "," + str(sender[k]['dates'][kk]['T']) + "," + str(sender[k]['dates'][kk]['A']) + ";"
        
        s = s + "|"
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
            s = s + str(receiver[k]['joined'])
        s = s + "|"

        if('dates' in receiver[k]):
            for kk,vv in receiver[k]['dates'].items():
                s = s + str(kk) + "," +  str(receiver[k]['dates'][kk]['S']) + "," + str(receiver[k]['dates'][kk]['P']) + "," + str(receiver[k]['dates'][kk]['T']) + "," + str(receiver[k]['dates'][kk]['A']) + ";"

        outputfile1.write(s + "\n")
    except:
        continue

outputfile1.close()
