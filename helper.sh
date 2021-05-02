#!/bin/bash
#==================================================================================#
# bash helper.sh                                                                   #
#==================================================================================#
CHECKPOINTFOLDER="checkpoint/"
TEMPORARY_FOLDER_FOR_INTERMEDIATE_MERGES="tmp"
RANGE=1
OFFSET=1000

#Make tmp dir
mkdir -p $TEMPORARY_FOLDER_FOR_INTERMEDIATE_MERGES

#Count number of files in CHECKPOINTFOLDER
count=$(find $CHECKPOINTFOLDER  -maxdepth 1 -type f|wc -l)
echo $count


i=$RANGE
while [ $i -le $count ] ; do
  echo "Processing $i to $(($i+$OFFSET-1))"
  python3 merge_helper.py $CHECKPOINTFOLDER $TEMPORARY_FOLDER_FOR_INTERMEDIATE_MERGES $i $OFFSET
  i=$(($i+$OFFSET))
done
