import os
from os import listdir
from os.path import isfile, join
import sys
import pickle

sender_final_stat = {}
receiver_final_stat = {}
userfields = [ 'ADULT_CONTENT', 'HEALTH', 'DRUGS_ALCOHOL_GAMBLING', 'RACE', 'VIOLENCE_CRIME', 'POLITICS', 'RELATION', 'LOCATION','AC','E','I','PH','AD','TO','O','S','P','T','A']

if(len(sys.argv) != 3):
    print("==================================================================================")
    print("SORRY!! Please provide the paths to the directories for reading and writing       ")
    print("==================================================================================")
    print("Example: python3 merge_updated_format.py checkpoint_folder_path  output_file_path ")
    print("==================================================================================")
    sys.exit()

read_path = sys.argv[1]	# i.e. '/venmo/read/'
write_path = sys.argv[2] # i.e. '/venmo/write/'

def updateStat(username, joined, sender, receiver):
    try:
        if sender:
            if username not in sender_final_stat:
                sender_final_stat[username] = {'joined': joined, 'dates': {}}
            for dt in sender: #date (year-month)
                if dt not in sender_final_stat[username]['dates']:
                    sender_final_stat[username]['dates'][dt] = {col:0 for col in userfields}
                for k in sender[dt]: #'S': sensitive, 'P': personal, 'T': total of senstive + personal, 'A': total notes
                    sender_final_stat[username]['dates'][dt][k] += sender[dt][k]

        if receiver:
            if username not in receiver_final_stat:
                receiver_final_stat[username] = {'joined': joined, 'dates': {}}
            for dt in receiver: #date (year-month)
                if dt not in receiver_final_stat[username]['dates']:
                    receiver_final_stat[username]['dates'][dt] = {col:0 for col in userfields}
                for k in receiver[dt]: #'S': sensitive, 'P': personal, 'T': total of senstive + personal, 'A': total notes
                    receiver_final_stat[username]['dates'][dt][k] += receiver[dt][k]
    except Exception as e:
        print(e)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)


#===============================================================#
#   READ & MERGE                                                #
#===============================================================#

files = [f for f in listdir(read_path) if isfile(join(read_path, f))]
for f in files:
    print(f)

print("==============================")
print(" PROCESSING INFORMATION       ")
print("==============================")
for f in files:
    if f[:11] == 'sender.txt.': # 'sender.txt.xxxx'
        print(f)
        with open(join(read_path, f), "rb") as myFile:
            sender_dict = pickle.load(myFile)
        for username in sender_dict:
            if 'joined' not in sender_dict[username]:
                continue
            joined = sender_dict[username]['joined']
            dates = sender_dict[username]['dates']
            updateStat(username, joined, dates, {})
    if f[:13] == 'receiver.txt.': # 'receiver.txt.xxxx'
        print(f)
        with open(join(read_path, f), "rb") as myFile:
            receiver_dict = pickle.load(myFile)
        for username in receiver_dict:
            if 'joined' not in receiver_dict[username]:
                continue
            joined = receiver_dict[username]['joined']
            dates = receiver_dict[username]['dates']
            updateStat(username, joined, {}, dates)

#===============================================================#
#   WRITE                                                       #
#===============================================================#

#   SENDER   #
outputfile = open(write_path + 'sender_summary.txt', "w")
scnt = -1

for k,v in sender_final_stat.items():
    if(v is None):
        continue
    scnt = scnt + 1
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
                    s = s + "," + str(kkk) + ":" +  str(vvv)
                s = s + ";"

        s = s + "|"
        if(k in receiver_final_stat and 'dates' in receiver_final_stat[k]):
            for kk,vv in receiver_final_stat[k]['dates'].items():
                s = s + str(kk)
                for kkk,vvv in sorted(vv.items()):
                    s = s + "," + str(kkk) + ":" +  str(vvv)
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
    rcnt = rcnt + 1
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
                    s = s + "," + str(kkk) + ":" +  str(vvv)
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
