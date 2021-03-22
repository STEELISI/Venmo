import numpy as np
import pandas as pd
import tensorflow as tf


BATCH_SIZE = 32
NR_EPOCHS = 6

train_path = 'BERT_MODEL/Preprocessed_Final_Training_Set.csv'
label_cols = ['ADULT_CONTENT', 'HEALTH', 'DRUGS_ALCOHOL_GAMBLING', 'RACE', 'VIOLENCE_CRIME', 'POLITICS', 'RELATION', 'LOCATION']
cols_to_use = ['Note','ADULT_CONTENT', 'HEALTH', 'DRUGS_ALCOHOL_GAMBLING', 'RACE', 'VIOLENCE_CRIME', 'POLITICS', 'RELATION', 'LOCATION']

df_train = pd.read_csv(train_path, usecols= cols_to_use)
sentences = df_train['Note']
labels =  df_train[label_cols].values

from transformers import BertTokenizer

bert_model_name = 'bert-base-uncased'
print('Loading BERT tokenizer...')
tokenizer = BertTokenizer.from_pretrained(bert_model_name, do_lower_case=True)

max_len = 0
n = 0
s = 0

for sent in sentences:

    input_ids = tokenizer.encode(sent, add_special_tokens=True)
    s = s + len(input_ids)
    max_len = max(max_len, len(input_ids))
    n = n + 1

print('Number of sentences: ', n)
print('Max sentence length: ', max_len)
print('Avg sentence length: ', s/n)

MAX_LEN = 10

input_ids = []
attention_masks = []

for sent in sentences:
    encoded_dict = tokenizer.encode_plus(
                        sent,                      # Sentence to encode.
                        add_special_tokens = True, # Add '[CLS]' and '[SEP]'
                        truncation = 'longest_first',
                        max_length = MAX_LEN,           # Pad & truncate all sentences.
                        # pad_to_max_length = True,
                        padding = 'max_length',
                        return_attention_mask = True,   # Construct attn. masks.
                        # return_tensors = 'tf',     # Return tensorflow tensor.
                   )
    input_ids.append(encoded_dict['input_ids'])
    attention_masks.append(encoded_dict['attention_mask'])

print(input_ids[:5])
print(attention_masks[:5])

from sklearn.model_selection import train_test_split

train_inputs, validation_inputs, train_labels, validation_labels = train_test_split(input_ids, labels, random_state=39, test_size=0.001)
train_masks, validation_masks, _, _ = train_test_split(attention_masks, labels, random_state=39, test_size=0.001)

train_size = len(train_inputs)
print('Training size: ', train_size)
validation_size = len(validation_inputs)
print('Validation size: ', validation_size)

def create_dataset(data_tuple, epochs=1, batch_size=32, buffer_size=100, train=True):
    dataset = tf.data.Dataset.from_tensor_slices(data_tuple)
    if train:
        dataset = dataset.shuffle(buffer_size=buffer_size)
    dataset = dataset.repeat(epochs)
    dataset = dataset.batch(batch_size)
    if train:
        dataset = dataset.prefetch(1)
    
    return dataset

train_dataset = create_dataset((train_inputs, train_masks, train_labels), epochs=1, batch_size=32)
print(type(train_dataset))
validation_dataset = create_dataset((validation_inputs, validation_masks, validation_labels), epochs=1, batch_size=32)

label_cols = ['ADULT_CONTENT', 'HEALTH', 'DRUGS_ALCOHOL_GAMBLING', 'RACE', 'VIOLENCE_CRIME', 'POLITICS', 'RELATION', 'LOCATION']

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

model = BertClassifier(TFBertModel.from_pretrained(bert_model_name), len(label_cols))

import time


steps_per_epoch = train_size // BATCH_SIZE
validation_steps = validation_size // BATCH_SIZE

# | Loss Function
loss_object = tf.keras.losses.BinaryCrossentropy(from_logits=False)
train_loss = tf.keras.metrics.Mean(name='train_loss')
validation_loss = tf.keras.metrics.Mean(name='test_loss')

# | Optimizer (with 1-cycle-policy)
optimizer = tf.keras.optimizers.Adam(learning_rate=2e-5, epsilon=1e-8)

# | Metrics
train_auc_metrics = [tf.keras.metrics.AUC() for i in range(len(label_cols))]
validation_auc_metrics = [tf.keras.metrics.AUC() for i in range(len(label_cols))]

@tf.function
def train_step(model, token_ids, masks, labels):
    labels = tf.dtypes.cast(labels, tf.float32)

    with tf.GradientTape() as tape:
        predictions = model(token_ids, attention_mask=masks)
        loss = loss_object(labels, predictions)

    gradients = tape.gradient(loss, model.trainable_variables)
    optimizer.apply_gradients(zip(gradients, model.trainable_variables))

    train_loss(loss)

    for i, auc in enumerate(train_auc_metrics):
        auc.update_state(labels[:,i], predictions[:,i])

@tf.function
def validation_step(model, token_ids, masks, labels):
    labels = tf.dtypes.cast(labels, tf.float32)

    predictions = model(token_ids, attention_mask=masks, training=False)
    v_loss = loss_object(labels, predictions)

    validation_loss(v_loss)
    for i, auc in enumerate(validation_auc_metrics):
        auc.update_state(labels[:,i], predictions[:,i])

def train(model, train_dataset, val_dataset, train_steps_per_epoch, val_steps_per_epoch, epochs):
    for epoch in range(epochs):
        print('=' * 50, f"EPOCH {epoch}", '=' * 50)
        print('step = {}'.format(str(train_steps_per_epoch)))

        start = time.time()

        #for i, (token_ids, masks, labels) in enumerate(train_dataset, train_steps_per_epoch):
        for i, (token_ids, masks, labels) in enumerate(train_dataset):
            #print(model, token_ids, masks, labels)
            train_step(model, token_ids, masks, labels)
            if i % 50 == 0:
                print(f'\nTrain Step: {i}, Loss: {train_loss.result()}')
                for i, label_name in enumerate(label_cols):
                    print(f"{label_name} roc_auc {train_auc_metrics[i].result()}")
                    train_auc_metrics[i].reset_states()
        #for i, (token_ids, masks, labels) in enumerate(val_dataset, val_steps_per_epoch):
        for i, (token_ids, masks, labels) in enumerate(val_dataset):
            validation_step(model, token_ids, masks, labels)

        print(f'\nEpoch {epoch+1}, Validation Loss: {validation_loss.result()}, Time: {time.time()-start}\n')

        for i, label_name in enumerate(label_cols):
            print(f"{label_name} roc_auc {validation_auc_metrics[i].result()}")
            validation_auc_metrics[i].reset_states()

        print('\n')

train(model, train_dataset, validation_dataset, train_steps_per_epoch=steps_per_epoch, val_steps_per_epoch=validation_steps, epochs=NR_EPOCHS)

model.save_weights('BERT_MODEL/checkpoint_EPOCHS_6a')
print("DONE!")
