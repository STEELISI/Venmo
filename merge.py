from os import listdir
from os.path import isfile, join
import sys
import pickle

sender_final_stat = {}
receiver_final_stat = {}

if(len(sys.argv) != 3):
    print("===========================================================================")
    print("SORRY!! Please provide the paths to the directories for reading and writing")
    print("===========================================================================")
    print("Example: python3 merge.py checkpoint_folder_path  output_file_path         ")
    print("===========================================================================")
    sys.exit()

read_path = sys.argv[1]	# i.e. '/venmo/read/'
write_path = sys.argv[2] # i.e. '/venmo/write/'

def updateStat(username, joined, sender, receiver):
    if sender:
        if username not in sender_final_stat:
            sender_final_stat[username] = {'joined': joined, 'dates': {}}
        for dt in sender: #date (year-month)
            if dt not in sender_final_stat[username]['dates']:
                sender_final_stat[username]['dates'][dt] = {'S': 0, 'P': 0, 'T': 0, 'A': 0}
            for k in sender[dt]: #'S': sensitive, 'P': personal, 'T': total of senstive + personal, 'A': total notes
                sender_final_stat[username]['dates'][dt][k] += sender[dt][k]

    if receiver:
        if username not in receiver_final_stat:
            receiver_final_stat[username] = {'joined': joined, 'dates': {}}
        for dt in receiver: #date (year-month)
            if dt not in receiver_final_stat[username]['dates']:
                receiver_final_stat[username]['dates'][dt] = {'S': 0, 'P': 0, 'T': 0, 'A': 0}
            for k in receiver[dt]: #'S': sensitive, 'P': personal, 'T': total of senstive + personal, 'A': total notes
                receiver_final_stat[username]['dates'][dt][k] += receiver[dt][k]


#===============================================================#
#   READ & MERGE                                                #
#===============================================================#

files = [f for f in listdir(read_path) if isfile(join(read_path, f))]

for f in files:
    if f[:11] == 'sender.txt.': # 'sender.txt.xxxx'
        with open(join(read_path, f), "rb") as myFile:
            sender_dict = pickle.load(myFile)
        for username in sender_dict:
            if 'joined' not in sender_dict[username]:
                continue
            joined = sender_dict[username]['joined']
            dates = sender_dict[username]['dates']
            updateStat(username, joined, dates, {})
    if f[:13] == 'receiver.txt.': # 'receiver.txt.xxxx'
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
s_outputfile = open(write_path + 'sender_summary.txt', "w")
s_index = -1

for k,v in sender_final_stat.items():
    if(v is None):
        continue
    s_index = s_index + 1
    s = ""
    try:
        s = str(s_index) + "|"
        if('joined' in sender_final_stat[k]):
            s = s + str(sender_final_stat[k]['joined'])
        s = s + "|"

        if('dates' in sender_final_stat[k]):
            for kk,vv in sender_final_stat[k]['dates'].items():
                s = s + str(kk) + "," +  str(sender_final_stat[k]['dates'][kk]['S']) + "," + str(sender_final_stat[k]['dates'][kk]['P']) + "," + str(sender_final_stat[k]['dates'][kk]['T']) + "," + str(sender_final_stat[k]['dates'][kk]['A']) + ";"

        s = s + "|"
        if(k in receiver_final_stat and 'dates' in receiver_final_stat[k]):
            for kk,vv in receiver_final_stat[k]['dates'].items():
                s = s + str(kk) + "," +  str(receiver_final_stat[k]['dates'][kk]['S']) + "," + str(receiver_final_stat[k]['dates'][kk]['P']) + "," + str(receiver_final_stat[k]['dates'][kk]['T']) + "," + str(receiver_final_stat[k]['dates'][kk]['A']) + ";"
        s_outputfile.write(s + "\n")
    except:
        continue

s_outputfile.close()
##############

#  RECEIVER  #
r_outputfile = open(write_path + 'receiver_summary.txt', "w")
r_index = -1

for k,v in receiver_final_stat.items():
    if(v is None or k in sender_final_stat):
        continue
    r_index = r_index + 1
    s = ""
    try:
        s = str(r_index) + "|"
        if('joined' in receiver_final_stat[k]):
            s = s + str(receiver_final_stat[k]['joined'])
        s = s + "|"

        if('dates' in receiver_final_stat[k]):
            for kk,vv in receiver_final_stat[k]['dates'].items():
                s = s + str(kk) + "," +  str(receiver_final_stat[k]['dates'][kk]['S']) + "," + str(receiver_final_stat[k]['dates'][kk]['P']) + "," + str(receiver_final_stat[k]['dates'][kk]['T']) + "," + str(receiver_final_stat[k]['dates'][kk]['A']) + ";"
        r_outputfile.write(s + "\n")
    except:
        continue

r_outputfile.close()
##############
