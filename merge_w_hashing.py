import os
from os import listdir
from os.path import isfile, join
import sys
import pickle

sender_final_stat = {}
receiver_final_stat = {}
userfields = [ 'ADULT_CONTENT', 'HEALTH', 'DRUGS_ALCOHOL_GAMBLING', 'RACE', 'VIOLENCE_CRIME', 'POLITICS', 'RELATION', 'LOCATION','AC','E','I','PH','AD','TO','O','S','P','T','A']

NUMBER_1 = 5 #set this to any number of your choice between 1 and 9 of your choice
NUMBER_2 = 371 #set this to any number of your choice between 1 and 999 of your choice 
NUMBER_3 = 4 #set this to any number of your choice between 1 and 9 of your choice 
NUMBER_4 = 4 #set this to any number of your choice between 1 and 1000000 of your choice

if(len(sys.argv) != 3):
    print("==================================================================================")
    print("SORRY!! Please provide the paths to the directories for reading and writing       ")
    print("==================================================================================")
    print("Example: python3 merge_updated_format.py checkpoint_folder_path  output_file_path ")
    print("==================================================================================")
    sys.exit()

read_path = sys.argv[1]	# i.e. '/venmo/read/'
write_path = sys.argv[2] # i.e. '/venmo/write/'
merge_version = sys.argv[3] # i.e. Number e.g. 34567, as in sender.txt.34567

#===============================================================#
#   READ & MERGE                                                #
#===============================================================#

sender_path = sys.argv[1] + "/sender.txt." + str(merge_version)
recv_path = sys.argv[1] + "/receiver.txt." + str(merge_version)

print("==============================")
print(" PROCESSING INFORMATION       ")
print("==============================")
with open(join(sender_path, f), "rb") as myFile:
    sender_final_stat = pickle.load(myFile)
with open(join(recv_path, f), "rb") as myFile:
    receiver_final_stat = pickle.load(myFile)
#===============================================================#
#   WRITE                                                       #
#===============================================================#

#   SENDER   #
outputfile = open(write_path + 'sender_summary.txt', "w")
scnt = -1

for k,v in sender_final_stat.items():
    if(v is None):
        continue

    x = ""
    y = 1
    for c in k:
        x += str((int(int(ord(c))/NUMBER_1) + NUMBER_2))
    y = int(x)*NUMBER_3
    scnt = (y + NUMBER_4)
    s = ""
    try:
        s = str(scnt) + "|"
        if('joined' in sender_final_stat[k]):
            s = s + str(sender_final_stat[k]['joined'])
        s = s + "|"

        if('dates' in sender_final_stat[k]):
            for kk,vv in sender_final_stat[k]['dates'].items():
                s = s + str(kk)
                for kkk,vvv in sorted(vv.items()):
                    s = s + "," +  str(vvv)
                s = s + ";"

        s = s + "|"
        if(k in receiver_final_stat and 'dates' in receiver_final_stat[k]):
            for kk,vv in receiver_final_stat[k]['dates'].items():
                s = s + str(kk)
                for kkk,vvv in sorted(vv.items()):
                    s = s + "," +  str(vvv)
                s = s + ";"
        outputfile.write(s + "\n")
    except Exception as e:
        print(e)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        continue
outputfile.close()

##############

#  RECEIVER  #
outputfile1 = open(write_path + 'receiver_summary.txt', "w")
rcnt = -1

for k,v in receiver_final_stat.items():
    if(v is None or k in sender_final_stat):
        continue

    x = ""
    y = 1
    for c in k:
        x += str((int(int(ord(c))/NUMBER_1) + NUMBER_2))
    y = int(x)*NUMBER_3
    rcnt = (y + NUMBER_4)

    s = ""
    try:
        s = str(rcnt) + "|"
        if('joined' in receiver_final_stat[k]):
            s = s + str(receiver_final_stat[k]['joined'])
        s = s + "|"

        if('dates' in receiver_final_stat[k]):
            for kk,vv in receiver_final_stat[k]['dates'].items():
                s = s + str(kk)
                for kkk,vvv in sorted(vv.items()):
                    s = s + "," +  str(vvv)
                s = s + ";"

        outputfile1.write(s + "\n")

    except Exception as e:
        print(e)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        continue


outputfile1.close()
##############
