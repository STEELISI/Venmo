#!/bin/bash
#================================================#
#  DOWNLOAD THE BELOW MODEL FILES FROM DROPBOX   #
#================================================#
mkdir BERT_MODEL
wget -O BERT_MODEL/checkpoint "https://www.dropbox.com/s/h87or3cdz19xxyh/checkpoint?dl=0"
wget -O BERT_MODEL/checkpoint_EPOCHS_6a.data-00000-of-00001 "https://www.dropbox.com/s/3sjby4vvc0ys7ot/checkpoint_EPOCHS_6a.data-00000-of-00001?dl=0"
wget -O BERT_MODEL/checkpoint_EPOCHS_6a.index "https://www.dropbox.com/s/1euvftchfq1u6as/checkpoint_EPOCHS_6a.index?dl=0"


