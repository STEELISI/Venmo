#!/bin/bash
#==================================================================================#
#  RUNNING MULTIPLE INSTANCES IN PARALLEL                                          #
#==================================================================================#
# bash run_multiple_instances.sh <path to json file> <path to the output folder>   #
#==================================================================================#
# bash run_multiple_instances.sh dummy.json outputfiles                            #
#==================================================================================#

if [ $# -lt 2 ]; then
    echo "#=========================================================#"
    echo "Please mention the 2 arguments and re-run. Thanks!        #"
    echo "Eg: bash run_multiple_instances.sh dummy.json outputfiles #"
    echo "#=========================================================#"
    exit 1
fi



PATH_TO_THE_JSON=$1
PATH_TO_THE_OUTPUT_FOLDER=$2 
echo "$PATH_TO_THE_JSON"
echo "$PATH_TO_THE_OUTPUT_FOLDER"
NUMBER_OF_INSTANCES=10
PATH_TO_No_OF_NOTES_PROCESSED_BY_THE_OLD_SEQUENTIAL_SCRIPT="checkpoint/processed_till_now.txt"

output_of_helper="" 
python3 helper.py > $PATH_TO_No_OF_NOTES_PROCESSED_BY_THE_OLD_SEQUENTIAL_SCRIPT
echo "EXTRACTING THE NUMBER OF NOTES THAT HAVE ALREADY BEEN PROCESSED BY OUR SEQUENTIAL SCRIPT";
output_of_helper=$(cat $PATH_TO_No_OF_NOTES_PROCESSED_BY_THE_OLD_SEQUENTIAL_SCRIPT)
echo "$output_of_helper";
DIVISION_FOR_THE_REMAINING_NOTES=$(((341309788 - $output_of_helper)/10))
echo "$DIVISION_FOR_THE_REMAINING_NOTES"


if [ ! -d $PATH_TO_THE_OUTPUT_FOLDER ]; then
    mkdir -p $PATH_TO_THE_OUTPUT_FOLDER;
fi


i=1
first=$output_of_helper

while [ $i -le $NUMBER_OF_INSTANCES ] ; do
  if [ ! -d checkpoint_instance_$i ]; then
      mkdir -p checkpoint_instance_$i;
  fi
  last=$(($first + $DIVISION_FOR_THE_REMAINING_NOTES))
  
  echo "STARTING INSTANCE $i which is in the range $first - $last"
  python3 BERT_Classification_Checkpoints_distributed.py $PATH_TO_THE_JSON "$PATH_TO_THE_OUTPUT_FOLDER/$i" $first $last checkpoint_instance_$i &

  first=$(($last + 1))
  i=$(($i+1))
done

