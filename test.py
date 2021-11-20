import sys
import numpy as np
import pandas as pd
import tensorflow as tf

model_version = 'BERT_MODEL/checkpoint_EPOCHS_6m'
label_cols = ['LGBTQ','ADULT_CONTENT', 'HEALTH', 'DRUGS_ALCOHOL_GAMBLING', 'RACE', 'VIOLENCE_CRIME', 'POLITICS', 'RELATION', 'LOCATION']
cols_to_use = ['Note','LGBTQ','ADULT_CONTENT', 'HEALTH', 'DRUGS_ALCOHOL_GAMBLING', 'RACE', 'VIOLENCE_CRIME', 'POLITICS', 'RELATION', 'LOCATION']

test_path = 'BERT_MODEL/Preprocessed_Testing.csv'
validate_path = 'Classification_Files/Classified_EPOCHS_6m.csv'
df_label_validate = pd.read_csv(test_path,  usecols= cols_to_use)



df_test = pd.read_csv(test_path,  usecols= cols_to_use)
print('Number of testing sentences: {}\n'.format(len(df_test)))

from transformers import BertTokenizer
from transformers import TFBertModel
from tensorflow.keras.layers import Dense, Flatten

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



bert_model_name = 'bert-base-uncased'
print('Loading BERT tokenizer...')
tokenizer = BertTokenizer.from_pretrained(bert_model_name, do_lower_case=True)

def create_dataset(data_tuple, epochs=1, batch_size=32, buffer_size=100, train=False):
    dataset = tf.data.Dataset.from_tensor_slices(data_tuple)
    if train:
        dataset = dataset.shuffle(buffer_size=buffer_size)
    dataset = dataset.repeat(epochs)
    dataset = dataset.batch(batch_size)
    if train:
        dataset = dataset.prefetch(1)
    
    return dataset

MAX_LEN = 10

test_input_ids = []
test_attention_masks = []

for sent in df_test['Note']:
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

save_model = BertClassifier(TFBertModel.from_pretrained(bert_model_name), len(label_cols))
save_model.load_weights(model_version)




TEST_BATCH_SIZE = 32
#test_steps = len(df_test) // TEST_BATCH_SIZE

test_dataset = create_dataset((test_input_ids, test_attention_masks), epochs=1, batch_size=32, train=False)
print(test_dataset)

df_result = pd.read_csv(test_path,  usecols= cols_to_use)

for i, (token_ids, masks) in enumerate(test_dataset):
    start = i * TEST_BATCH_SIZE
    end = (i+1) * TEST_BATCH_SIZE - 1
    '''
    print(" START " )
    print(start)
    print(" END ")
    print(end)
    '''

    predictions = save_model(token_ids, attention_mask=masks).numpy()
    #print(predictions)
    binary_predictions = np.where(predictions > 0.5, 1, 0)
    #print(binary_predictions)
    df_result.loc[start:end,label_cols] = binary_predictions


df_result.to_csv(validate_path, index=False)

df_validate = pd.read_csv(validate_path,usecols= cols_to_use)


for col in label_cols:
    c = 0
    n = len(df_validate)
    for index, value in df_validate[col].items():
        if df_validate[col][index] == df_label_validate[col][index]:
            c = c + 1
        #else:
          #print("Line:" + str(index))
    print('{} accuracy : {}/{} = {}'.format(col, c, n, str(c/n)))

cnt = 0
for col in label_cols:
    c = 0
    n = 0
    for index, value in df_validate[col].items():
        cnt = cnt + 1
        if df_label_validate[col][index] == 1:
            n = n + 1
            if df_validate[col][index] == df_label_validate[col][index]:
                c = c + 1
            #else:
              #print(col, index)
    print('=== {} ==='.format(col))
    print('true positive : {}/{} = {}'.format(c, n, str(c/n)))
    print('false negitive : {}/{} = {}'.format(n - c, n, str(1 - c/n)))
    

none_labelled = {}
none_test = {}
tot_lab = 0
tot_test = 0


for col in label_cols:
    for index, value in df_validate[col].items():
      if df_validate[col][index] == 0:
          if(index not in none_test):
              none_test[index] = 0
          none_test[index] = none_test[index] + 1
          if(none_test[index] == 8):
              #print(df_validate['Note'][index])
              tot_test = tot_test + 1

for col in label_cols:
    for index, value in df_label_validate[col].items():
      if df_label_validate[col][index] == 0:
          if(index not in none_labelled):
              none_labelled[index] = 0
          none_labelled[index] = none_labelled[index] + 1
          if(none_labelled[index] == 8):
              #print(df_label_validate['Note'][index])
              tot_lab = tot_lab + 1

print(tot_test, tot_lab)

tp = 0
for k,v in none_test.items():
    if(v == 8 and none_labelled[k] == 8):
      tp = tp + 1

print('=== None ===')
print("True positives : " + str(tp) + "/" + str(tot_lab) + " = " + str(tp/tot_lab))
print("True negatives : " + str((cnt - tot_lab) - (tot_test - tp)) + "/" + str(cnt - tot_lab) + " = " + str(((cnt - tot_lab) - (tot_test - tp))/(cnt - tot_lab)))
print("False positives : " + str((tot_test - tp)) + "/" + str(tot_lab) + " = " + str((tot_test - tp)/tot_lab))
print("False negatives : " + str((cnt - tot_lab) - (tot_test - tp) ) + "/" + str(tot_lab) + " = " + str(1- ((cnt - tot_lab) - (tot_test - tp))/(cnt - tot_lab)))


for col in label_cols:
    c = 0
    n = 0
    for index, value in df_validate[col].items():
        if df_label_validate[col][index] == 0:
            n = n + 1
            if df_validate[col][index] == df_label_validate[col][index]:
                c = c + 1
    print('=== {} ==='.format(col))
    print('true negative : {}/{} = {}'.format(c, n, str(c/n)))
    print('false positive : {}/{} = {}'.format(n - c, n, str(1 - c/n)))
