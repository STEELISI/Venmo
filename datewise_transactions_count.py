#====================================================================================================#
#*******************************   HOW TO RUN?  **************************************************** #
# python3 datewise_transactions_count.py <path to the input json file>  <path to the output file>    #
#*************************************************************************************************** #
# Example:                                                                                           #
#python3 datewise_transactions_count.py /Users/rajattan/venmo/dummy.json ./transactions_date_wise.txt#
#====================================================================================================#

import sys
import json

transactions = 0
transactions_date_wise = {}


if(len(sys.argv) != 3):
    print("==========================================================================")
    print("SORRY!! Please provide the path to the INPUT json file and the OUTPUT file")
    print("==========================================================================")
    print("Example: python3 datewise_transactions_count.py ./dummy.json ./output.txt ")
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
        if(date[0] not in transactions_date_wise):
            transactions_date_wise[date[0]] = 0
        transactions_date_wise[date[0]] = transactions_date_wise[date[0]] + 1
    except TypeError:
        continue        
f.close()

outputfile.write("DATE #TRANSACTIONS \n")
for k,v in sorted(transactions_date_wise.items()):
    outputfile.write(str(k) + " " + str(v) + "\n")

outputfile.write("TOTAL NUMBER OF TRANSACTIONS ARE :" + str(transactions))
outputfile.close()
