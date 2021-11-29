import os
from os import listdir
from os.path import isfile, join
import sys
import pickle

sender_final_stat = {}
receiver_final_stat = {}
#userfields = [ 'ADULT_CONTENT', 'HEALTH', 'DRUGS_ALCOHOL_GAMBLING', 'RACE', 'VIOLENCE_CRIME', 'POLITICS', 'RELATION', 'LOCATION','AC','E','I','PH','AD','TO','O','S','P','T','A']
userfields = ['LGBTQ', 'ADULT_CONTENT', 'HEALTH', 'DRUGS_ALCOHOL_GAMBLING', 'RACE', 'VIOLENCE_CRIME', 'POLITICS', 'RELATION', 'LOCATION','AC','E','I','PH','AD','P','T','A']

if(len(sys.argv) != 5):
    print("=========================================================================================================")
    print("SORRY!! Please provide the paths to the directories for reading and writing                              ")
    print("=========================================================================================================")
    print("Example: python3 merge_updated_format.py <checkpoint_folder_path>  <output_folder_path> <range> <offset> ")
    print("=========================================================================================================")
    sys.exit()

read_path = sys.argv[1]	# i.e. '/venmo/read/'
write_path = sys.argv[2] # i.e. '/venmo/write/'
rang = int(sys.argv[3])
offset = int(sys.argv[4])
SENDER_FILE = write_path + "/sender.txt."
#RECEIVER_FILE = write_path + "/receiver.txt."

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
        '''
        if receiver:
            if username not in receiver_final_stat:
                receiver_final_stat[username] = {'joined': joined, 'dates': {}}
            for dt in receiver: #date (year-month)
                if dt not in receiver_final_stat[username]['dates']:
                    receiver_final_stat[username]['dates'][dt] = {col:0 for col in userfields}
                for k in receiver[dt]: #'S': sensitive, 'P': personal, 'T': total of senstive + personal, 'A': total notes
                    receiver_final_stat[username]['dates'][dt][k] += receiver[dt][k]
        '''
    except Exception as e:
        print(e)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)


#===============================================================#
#   READ & MERGE                                                #
#===============================================================#

count = 0
start = rang
end = start + offset - 1
files = [f for f in sorted(listdir(read_path)) if isfile(join(read_path, f))]
print("==============================")
print(" PROCESSING INFORMATION       ")
print("==============================")
for f in files:
    count = count + 1
    if(not(count >= start and count <= end)):
        continue
    if f[:11] == 'sender.txt.': # 'sender.txt.xxxx'
        print(f)
        with open(join(read_path, f), "rb") as myFile:
            sender_dict = pickle.load(myFile)
        for username in sender_dict:
            joined = ""
            if 'joined' in sender_dict[username]:
                joined = sender_dict[username]['joined']
            dates = sender_dict[username]['dates']
            updateStat(username, joined, dates, {})
    '''
    if f[:13] == 'receiver.txt.': # 'receiver.txt.xxxx'
        print(f)
        with open(join(read_path, f), "rb") as myFile:
            receiver_dict = pickle.load(myFile)
        for username in receiver_dict:
            joined = ""
            if 'joined' in receiver_dict[username]:
                joined = receiver_dict[username]['joined']
            dates = receiver_dict[username]['dates']
            updateStat(username, joined, {}, dates)
    ''' 

#===============================================================#
#   DUMP                                                        #
#===============================================================#


send = SENDER_FILE + str(start) + "-" + str(end)
with open(send, "wb") as myFile:
    pickle.dump(sender_final_stat, myFile,protocol=pickle.HIGHEST_PROTOCOL)
'''
recv = RECEIVER_FILE + str(start) + "-" + str(end)
with open(recv, "wb") as myFile:
    pickle.dump(receiver_final_stat, myFile,protocol=pickle.HIGHEST_PROTOCOL)
'''
