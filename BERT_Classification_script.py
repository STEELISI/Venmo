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
BATCH = 10000
TEST_BATCH = 32
transactions = 0
dates = [''] * BATCH
notes = [''] * BATCH
cnt = 0 # counter
textual_transactions = 0
transactions_date_wise = {}
MODEL_FILE = 'BERT_MODEL/checkpoint_EPOCHS_6a'
english_ch = re.compile("[A-Za-z0-9]+")
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
c0 = c1 = [' '] * BATCH
c2 = c3 = c4 = c5 = c6 = c7 = c8 = c9 = [0] * BATCH
cols_name = ['Date', 'Note', 'ADULT_CONTENT', 'HEALTH', 'DRUGS_ALCOHOL_GAMBLING', 'RACE', 'VIOLENCE_CRIME', 'POLITICS', 'RELATION', 'LOCATION']
#cols_name = ['Note', 'ADULT_CONTENT', 'HEALTH', 'DRUGS_ALCOHOL_GAMBLING', 'RACE', 'VIOLENCE_CRIME', 'POLITICS', 'RELATION', 'LOCATION']
label_cols = cols_name[2:]  # drop 'Date' & 'Note' (the 2 leftmost columns)

label_cols = ['ADULT_CONTENT', 'HEALTH', 'DRUGS_ALCOHOL_GAMBLING', 'RACE', 'VIOLENCE_CRIME', 'POLITICS', 'RELATION', 'LOCATION']

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
'''
def build_table(c1):
    table = zip( c1, c2, c3, c4, c5, c6, c7, c8, c9)
    table = list(table)
    return [list(r) for r in table]
'''
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
BERT encoder
"""
def encoder(notes, tokenizer):
    token_ids = []
    masks = []
    for msg in notes:
        print(msg)
        encoded_dict = tokenizer.encode_plus(
                            msg,    # note to encode.
                            add_special_tokens=True,    # Add '[CLS]' and '[SEP]'.
                            max_length=10,  # Pad & truncate all sentences.
                            padding='max_length',
                            return_attention_mask=True  # Construct attn. mask.
                        )
        token_ids.append(encoded_dict['input_ids'])
        masks.append(encoded_dict['attention_mask'])
    return token_ids, masks
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
#   MAIN FLOW                                                   #
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

        if len(tokens) > 50:
            continue
        note = ' '.join(tokens).strip()
        print(note, english_ch.search(note))
        if(english_ch.search(note) == None or len(note) == 0):
            continue
        if(date[0] not in transactions_date_wise):
            transactions_date_wise[date[0]] = 0
        transactions_date_wise[date[0]] = transactions_date_wise[date[0]] + 1
        textual_transactions = textual_transactions + 1
        dates[cnt] = date[0]
        notes[cnt] = note
        
        if cnt == BATCH:
            # form dataset
      
            table = build_table(dates, notes)
            #table = build_table(notes)
            test_preds = pd.DataFrame(np.array(table), columns=cols_name)
            input_ids, attention_masks = encoder(test_preds['Note'], tokenizer)
            test_dataset = create_dataset((input_ids, attention_masks), epochs=1, batch_size=16)
            # prediction
            for i, (token_ids, masks) in enumerate(test_dataset):
                start = i * TEST_BATCH
                end = (i+1) * TEST_BATCH - 1
                #test_preds.loc[start:end][label_cols] = predict(token_ids, masks)
                predictions = model(token_ids, attention_mask=masks).numpy()
                print(predictions)
                binary_predictions = np.where(predictions > 0.5, 1, 0)
                test_preds.loc[start:end][label_cols] = binary_predictions
            # update stats
            for index, row in test_preds.iterrows():
                update(row)
            # reset counter
            cnt = 0
            
        cnt = cnt + 1


    except TypeError:
        continue        
f.close()

# Last batch
if cnt != 0:
    # form dataset
    #table = build_table(dates, notes)
    #table = build_table(notes)
    del dates[cnt:]
    del notes[cnt:]
    c2 = c3 = c4 = c5 = c6 = c7 = c8 = c9 = [0] * cnt
    table = zip(dates, notes, c2, c3, c4, c5, c6, c7, c8, c9)
    #table = zip(notes, c2, c3, c4, c5, c6, c7, c8, c9)
    table = list(table)
    table = [list(r) for r in table]
    test_preds = pd.DataFrame(np.array(table), columns=cols_name)
    print("==== BEFORE ====")
    print(test_preds)
    print('Number of testing sentences: {}\n'.format(len(test_preds)))
    #input_ids, attention_masks = encoder(test_preds['Note'], tokenizer)
    #input_ids, attention_masks = encoder(test_preds['Note'], tokenizer)
    #print(input_ids, attention_masks)
    #print("FINE")
    #sys.exit()
    MAX_LEN = 10
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
    '''
    saved_model = BertClassifier(TFBertModel.from_pretrained(bert_model_name), len(label_cols))
    saved_model.load_weights(MODEL_FILE)
    '''


    #test_dataset = create_dataset((test_input_ids, test_attention_masks), epochs=1, batch_size=32)
    test_dataset = create_dataset((test_input_ids, test_attention_masks), epochs=1, batch_size=32, train=False)
    print(test_dataset)
    # prediction
    for i, (token_ids, masks) in enumerate(test_dataset):
        start = i * TEST_BATCH
        end = (i+1) * TEST_BATCH - 1
        print(" START " )
        print(start)
        print(" END ")
        print(end)
        #test_preds.loc[start:end][label_cols] = predict(token_ids, masks)
        predictions = saved_model(token_ids, attention_mask=masks).numpy()
        print(predictions)
        binary_predictions = np.where(predictions > 0.5, 1, 0)
        print(binary_predictions)
        test_preds.loc[start:end, label_cols] = binary_predictions
    print("==== AFTER ====")
    print(test_preds)
    test_preds.to_csv('dummy.txt', index=False)
    # update stat
    
    for index, row in test_preds.iterrows():
        update(row)
    # reset counter
    cnt = 0
    
# Write stats
df_stat = pd.DataFrame.from_dict(date_category_stat, orient='index', columns=label_cols)
df_stat = df_stat.rename_axis('Date').reset_index()
df_stat.to_csv('./result.csv', index=False)



outputfile.write("DATE #TEXTUAL_TRANSACTIONS \n")
for k,v in sorted(transactions_date_wise.items()):
    outputfile.write(str(k) + " " + str(v) + "\n")

outputfile.write("TOTAL NUMBER OF TRANSACTIONS ARE :" + str(transactions))
outputfile.write("\nTOTAL NUMBER OF TEXTUAL TRANSACTIONS IN ENGLISH ARE :" + str(textual_transactions))
outputfile.close()
