#!/bin/bash
#==================================================================================#
# bash fan_in.sh                                                                   #
#==================================================================================#

PATH_TO_CSV_FILE="2020_data_test.csv"
PATH_TO_OUTPUT_FILE="FANS/csv"

COUNT=5
OFFSET=1

i=0
while [ $i -le $COUNT ] ; do
  echo "\\n Processing $i/$COUNT now !!!!"
  python3 Fan_in_2020.py $PATH_TO_CSV_FILE $PATH_TO_OUTPUT_FILE $i
  i=$(($i+$OFFSET))
done
