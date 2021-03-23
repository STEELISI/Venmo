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
MAX_LEN = 10
BATCH = 10000
TEST_BATCH = 32
transactions = 0
dates = [''] * BATCH
notes = [''] * BATCH
cnt = 0 # counter
keywords = set()
textual_transactions = 0
transactions_date_wise = {}
transactions_ph = {}
transactions_email = {}
transactions_acc = {}
transactions_invoice = {}
MODEL_FILE = 'BERT_MODEL/checkpoint_EPOCHS_6a'
PATH_TO_KEYWORDS_LIST = 'data/UNIQ_KEYWORDS_LIST.txt'
english_ch = re.compile("[A-Za-z0-9]+")
email = re.compile("[^@]+@[^@]+\.[^@]+")
phno = re.compile("\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4}")

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
cols_name = ['Date', 'Note', 'ADULT_CONTENT', 'HEALTH', 'DRUGS_ALCOHOL_GAMBLING', 'RACE', 'VIOLENCE_CRIME', 'POLITICS', 'RELATION', 'LOCATION']
label_cols = cols_name[2:]  # drop 'Date' & 'Note' (the 2 leftmost columns)

#label_cols = ['ADULT_CONTENT', 'HEALTH', 'DRUGS_ALCOHOL_GAMBLING', 'RACE', 'VIOLENCE_CRIME', 'POLITICS', 'RELATION', 'LOCATION']

bert_model_name = 'bert-base-uncased'
tokenizer = BertTokenizer.from_pretrained(bert_model_name, do_lower_case=True)

saved_model = BertClassifier(TFBertModel.from_pretrained(bert_model_name), len(label_cols))
saved_model.load_weights(MODEL_FILE)
print("\n MODEL LOADED\n\n\n\n\n")

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
"""
Update stats
"""
def update(row):
    date = str(row['Date'])
    if date not in date_category_stat:
        date_category_stat[date] = {col:0 for col in label_cols}
    for col in label_cols:
        if row[col] == 0:
            continue
        date_category_stat[date][col] = date_category_stat[date][col] + 1


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

        if(data is None or data['created_time'] is None):
            continue
        datetime = str(data['created_time'])
        date = datetime.split("T")
        if(data is None or data['message'] is None or data['message'] == ""):
            continue
        note = str(data['message'])
        tokens = nltk.word_tokenize(note)
        tokens = preprocessing(note)

        if len(tokens) > 50:
            continue
        if(contains_phn(note)):
            if(date[0] not in transactions_ph):
                transactions_ph[date[0]] = 0
            transactions_ph[date[0]] = transactions_ph[date[0]] + 1

        if(contains_email(note)):
            if(date[0] not in transactions_email):
                transactions_email[date[0]] = 0
            transactions_email[date[0]] = transactions_email[date[0]] + 1

        if(contains_acc(note)):
            if(date[0] not in transactions_acc):
                transactions_acc[date[0]] = 0
            transactions_acc[date[0]] = transactions_acc[date[0]] + 1

        if(contains_invoice(note)):
            if(date[0] not in transactions_invoice):
                transactions_invoice[date[0]] = 0
            transactions_invoice[date[0]] = transactions_invoice[date[0]] + 1

        note = ' '.join(tokens).strip()
        if(english_ch.search(note) == None or len(note) == 0):
            continue

        bigrams = [' '.join(list(t)) for t in list(nltk.bigrams(tokens))]
        flag = 0
        for t in tokens:
            if(t == "id" or t == "code"):
                if(date[0] not in transactions_acc):
                    transactions_acc[date[0]] = 0
                transactions_acc[date[0]] = transactions_acc[date[0]] + 1
            if(t in keywords):
                flag = 1
                break 
        
        if(flag == 0):
            for bi in bigrams:
                if(bi in keywords):
                    flag = 1
                    break
        if(flag == 0):
            continue

        if(date[0] not in transactions_date_wise):
            transactions_date_wise[date[0]] = 0
        transactions_date_wise[date[0]] = transactions_date_wise[date[0]] + 1
        textual_transactions = textual_transactions + 1
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
                date = str(row['Date'])
                if date not in date_category_stat:
                    date_category_stat[date] = {col:0 for col in label_cols}
                for col in label_cols:
                    if row[col] == 0:
                        continue
                    date_category_stat[date][col] = date_category_stat[date][col] + 1
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
        #update(row)
        date = str(row['Date'])
        if date not in date_category_stat:
            date_category_stat[date] = {col:0 for col in label_cols}
        for col in label_cols:
            if row[col] == 0:
                continue
            date_category_stat[date][col] = date_category_stat[date][col] + 1

    # reset counter
    cnt = 0
    
# Write stats
df_stat = pd.DataFrame.from_dict(date_category_stat, orient='index', columns=label_cols)
df_stat = df_stat.rename_axis('Date').reset_index()
df_stat.to_csv(sys.argv[2] + ".output", index=False)



outputfile.write("DATE #TEXTUAL_TRANSACTIONS \n")
for k,v in sorted(transactions_date_wise.items()):
    outputfile.write(str(k) + " " + str(v) + "\n")

outputfile.write("TOTAL NUMBER OF TRANSACTIONS ARE :" + str(transactions))
outputfile.write("\nTOTAL NUMBER OF TEXTUAL TRANSACTIONS IN ENGLISH ARE :" + str(textual_transactions))

outputfile.write("\nDATE #EMAILS \n")
for k,v in sorted(transactions_email.items()):
    outputfile.write(str(k) + " " + str(v) + "\n")

outputfile.write("DATE #PHONE \n")
for k,v in sorted(transactions_ph.items()):
    outputfile.write(str(k) + " " + str(v) + "\n")

outputfile.write("DATE #ACCOUNT \n")
for k,v in sorted(transactions_acc.items()):
    outputfile.write(str(k) + " " + str(v) + "\n")

outputfile.write("DATE #INVOICE \n")
for k,v in sorted(transactions_invoice.items()):
    outputfile.write(str(k) + " " + str(v) + "\n")

outputfile.close()
