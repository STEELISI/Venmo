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
min_date_wise = {}
max_date_wise = {}


if(len(sys.argv) != 3):
    print("==========================================================================")
    print("SORRY!! Please provide the path to the INPUT json file and the OUTPUT file")
    print("==========================================================================")
    print("Example: python3 transaction_pub_vs_pri.py ./dummy.json ./output.txt      ")
    print("==========================================================================")
    sys.exit()



f = open(sys.argv[1])
outputfile = open(sys.argv[2],"w")

for line in f:
    data = json.loads(line)
    transactions = transactions + 1
    try:
        if(data is None or data['created_time'] is None or data['payment_id'] is None):
            continue
        datetime = str(data['created_time'])
        date = datetime.split("T")
        payment_id = int(str(data['payment_id']))
        if(date[0] not in transactions_date_wise):
            transactions_date_wise[date[0]] = 0
            max_date_wise[date[0]] = payment_id
            min_date_wise[date[0]] = payment_id
        else:
            if(payment_id > max_date_wise[date[0]]):
                max_date_wise[date[0]] = payment_id
            if(payment_id < min_date_wise[date[0]]):
                min_date_wise[date[0]] = payment_id
        transactions_date_wise[date[0]] = transactions_date_wise[date[0]] + 1
    except:
        continue        
f.close()

outputfile.write("DATE #TRANSACTIONS #MIN_ID #MAX_ID\n")
for k,v in sorted(transactions_date_wise.items()):
    try:
        outputfile.write(str(k) + " " + str(v) + " " + str(min_date_wise[k]) + " " + str(max_date_wise[k]) + "\n")
    except:
        continue

outputfile.write("TOTAL NUMBER OF TRANSACTIONS ARE :" + str(transactions))
outputfile.close()
