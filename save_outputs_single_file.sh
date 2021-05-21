#!/bin/bash
#==================================================================================#
# bash helper.sh                                                                   #
#==================================================================================#
CHECKPOINTFOLDER="checkpoint_MAY_1_2020/"
OUTPUT_FILES_PATH="tmp/out"

#Make tmp dir
mkdir -p $TEMPORARY_FOLDER_FOR_INTERMEDIATE_MERGES

#Count number of files in CHECKPOINTFOLDER
files=$(find $CHECKPOINTFOLDER  -maxdepth 1 -type f| grep sender.txt | awk -F 'sender.txt.' '{print $2}')
count=$(find $CHECKPOINTFOLDER  -maxdepth 1 -type f| grep sender.txt | wc -l)
echo $count
echo $files


for word in $files
do
    python3 merge_w_hashing.py $CHECKPOINTFOLDER  $OUTPUT_FILES_PATH $word
    echo "\n Processing of sender.txt.$word and reciever.txt.$word complete! \n"
done
