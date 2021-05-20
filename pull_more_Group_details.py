#============================================================================================================#
#*******************************   HOW TO RUN?  ************************************************************ #
# python3 pull_more_Group_details.py  <path to the output file>                                              #
#*********************************************************************************************************** #
# Example:                                                                                                   #
# python3 pull_more_Group_details.py ./output                                                                #
#============================================================================================================#

import os
import sys
import pickle
filter_users = {}
unique = {}
transactions = 0

UNIQUESENDERS = "checkpoint/unique.txt"
CHECKPOINT_FILE = "checkpoint/current.txt"
USERS_FILE = "checkpoint_part1/PARTIAL_OUTPUT.txt"



if(len(sys.argv) != 1):
    print("==========================================================================")
    print("SORRY!! Please provide the  OUTPUT file")
    print("==========================================================================")
    print("Example: python3 pull_more_Group_details.py  ./output.txt  ")
    print("==========================================================================")
    sys.exit()





if(os.path.exists(CHECKPOINT_FILE)):
    with open(CHECKPOINT_FILE, "rb") as myFile:
        current = pickle.load(myFile)
    print("RESUMING FROM " + str(current))

with open(USERS_FILE, "rb") as myFile:
    filter_users = pickle.load(myFile)

f = UNIQUESENDERS + "." + str(current)
with open(f, "rb") as myFile:
    unique = pickle.load(myFile)




outputfile1 = open(sys.argv[1] + "GAMBLING.txt","w")

gamcols = " USER ID (1)|#SENDERS (2)|Casino (3)| Email (4)| Gamble (5)| Lottery (6)| Money (7) | Non-Gambling (8) | Poker (9) | Total Transactions (10) | Total Gambling Transactions (11) | betting (12) | dates (13) | greeting/gratitude (14) | only emoji (15) | play (16) | Percentage of G Trans (17) | #SENDERS with no sensitive posts (18) | CATEGORY (19)"

outputfile1.write(gamcols + "\n")
scount = -1
for k,v in unique.items():
    tusername = k
    if("AA-U" in filter_users[tusername]['C'] or "AA-N" in filter_users[tusername]['C']):
        continue
    scount = scount + 1

    s = str(scount) + "|" + str(len(v)) + "|"
    tot = {'TG':0,'Poker':0,'Gamble':0, 'Casino':0, 'betting':0, 'play':0, 'Lottery':0, 'date':0, 'greeting/gratitude':0, 'only emoji':0, 'N':0,'T':0, 'Email':0, 'Money':0}

    senders_no_posts = 0
    for kk,vv in sorted(v.items()):
        for kkk, vvv in sorted(vv.items()):
            tot[kkk] += vvv
            if(kkk == 'TG' and vvv == 0):
                senders_no_posts += 1

    for key, val in sorted(tot.items()):
        s +=  str(val) + "|"

    per = int((tot['TG']/tot['T'])* 100.0)
    s += str(per) + "|"
    s += str(senders_no_posts) + "|"

    for l in filter_users[k]['C']:
        s += l + " "

    outputfile1.write(s + "\n")

outputfile1.close()


AAcols = " USER ID (1)|#SENDERS (2)|11 step (3)| AA (4)| Attitude (5)| Book Study (6)| Early Bird (7)| Eye Opener (8)| Lunch Bunch (9)| Non-AA Trans (10)| Other AA (11)| Total Transactions (12)| Total AA Transactions (13)| Tradition (14) | dates (15) | donation (16) | dues (17) | greeting/gratitude (18) | meeting (19) | only emoji (20) | Percentage of AA Trans (21) | #SENDERS with no sensitive posts (22) | CATEGORY (23)"

outputfile1 = open(sys.argv[1] + "AA.txt","w")

outputfile1.write(AAcols + "\n")

for k,v in unique.items():

    tusername = k
    if(not("AA-U" in filter_users[tusername]['C'] or "AA-N" in filter_users[tusername]['C'])):
        continue
    scount = scount + 1
    s = str(scount) + "|" + str(len(v)) + "|"
    tot = {'TAA':0, 'AA':0,'Tradition':0,'Lunch Bunch':0,'Book Study':0,'Early Bird':0,'Eye Opener':0, 'Attitude':0, 'O' : 0, 'N':0,'T':0, '11 step':0 ,'meeting':0, 'dues':0, 'donation':0, 'only emoji':0, 'greeting/gratitude':0 , 'date':0}

    senders_no_posts = 0
    for kk,vv in sorted(v.items()):
        for kkk, vvv in sorted(vv.items()):
            tot[kkk] += vvv
            if(kkk == 'TAA' and vvv == 0):
                senders_no_posts += 1

    for key, val in sorted(tot.items()):
        s += str(val) + "|"

    per = int((tot['TAA']/tot['T'])* 100.0)
    s += str(per) + "|"
    s += str(senders_no_posts) + "|"

    for l in filter_users[k]['C']:
        s += l + " "

    outputfile1.write(s + "\n")
outputfile1.close()
