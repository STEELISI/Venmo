#!/bin/bash
#==================================================================================#
# bash fan_in.sh                                                                   #
#==================================================================================#

PATH_TO_JSON_FILE="dummy_plus.json"
PATH_TO_OUTPUT_FILE="FANS/outp"

COUNT=5
OFFSET=1

i=0
while [ $i -le $COUNT ] ; do
  echo "\\n Processing $i/$COUNT now !!!!"
  python3 Fan_in.py $PATH_TO_JSON_FILE $PATH_TO_OUTPUT_FILE $i
  i=$(($i+$OFFSET))
done
