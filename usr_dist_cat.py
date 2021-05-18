f ="D2_dataset/outputs"
f ="/Users/rajattandon/Documents/2k_2020.txt"
f ="/Users/rajattandon/Documents/combined_outputs_2020_sender_summary.txt"
f ="/Users/rajattandon/Documents/combined_outputssender_summary.txt"
f="/Users/rajattandon/Documents/combined_2020_maverick_sender_summary.txt"
#f="/Users/rajattandon/Documents/mini.txt"
f1="/Users/rajattandon/Documents/combined_2020_maverick_receiver_summary.txt"
#f1="/Users/rajattandon/Documents/mona.txt"
#f="checkpoint/xxsender_summary.txt"
#f ="/Users/rajattandon/Documents/third_BERT_classification_norm"
#f ="/Users/rajattandon/Documents/combined_outputssender_summary.txt"
#f ="D2_dataset/outputsrecv.output"

outpath = "date_wise_usr/D4/out"
#outpath = "prof_work/D2-Dataset/"
#0|2019-08-25|20-09,A:1,AC:0,AD:0,ADULT_CONTENT:0,DRUGS_ALCOHOL_GAMBLING:1,E:0,HEALTH:0,I:0,LOCATION:0,O:0,P:0,PH:0,POLITICS:0,RACE:0,RELATION:0,S:1,T:1,TO:0,VIOLENCE_CRIME:0;20-07,A:3,AC:0,AD:0,ADULT_CONTENT:1,DRUGS_ALCOHOL_GAMBLING:0,E:0,HEALTH:0,I:0,LOCATION:0,O:0,P:0,PH:0,POLITICS:0,RACE:0,RELATION:0,S:1,T:1,TO:0,VIOLENCE_CRIME:0;20-02,A:2,AC:0,AD:0,ADULT_CONTENT:0,DRUGS_ALCOHOL_GAMBLING:0,E:0,HEALTH:0,I:0,LOCATION:0,O:0,P:0,PH:0,POLITICS:0,RACE:0,RELATION:0,S:0,T:0,TO:0,VIOLENCE_CRIME:0;|
#sens_cols = ['ADULT_CONTENT', 'HEALTH', 'DRUGS_ALCOHOL_GAMBLING', 'RACE', 'VIOLENCE_CRIME', 'POLITICS', 'RELATION', 'LOCATION','T']

# Account, Email, Invoice, Personal, Address, Total, Overlap
#personal_cols = ['AC','E','I','PH','AD','TO','O']



userfields = [ 'ADULT_CONTENT', 'HEALTH', 'DRUGS_ALCOHOL_GAMBLING', 'RACE', 'VIOLENCE_CRIME', 'POLITICS', 'RELATION', 'LOCATION','AC','E','I','PH','AD','TO','O','S','P','T','A']


mcat0 = {}
mcat = {}

sen = 0
r = 0
both = 0
with open(f,'r') as fp:
    for l in fp:
        s=""
        pipe = l.split("|")
        if(len(pipe) > 3):
            st = pipe[0]
            t = pipe[2].split(";")
            m = {}
            senflag = 0
            for i in t:
                if("," in i):
                    pa = i.split(",")
                    dt = ""
                    for x in pa:
                        paa = x.split(":")
                        if(len(paa) > 1):
                            if(int(paa[1]) > 0 ):
                                mcat0[dt][paa[0]] += 1 
                                m[dt][paa[0]] = 1
                        else:
                            if( x not in mcat0):
                                mcat0[x] = {col:0 for col in userfields}
                            m[x] = {col:0 for col in userfields}
                            dt = x
             
            if(pipe[3] is not None and "," in pipe[3]):
                st = pipe[0]
                t = pipe[3].split(";")  
                bothf = 0
                for i in t:
                    if("," in i):
                        pa = i.split(",")
                        dt = ""
                        for x in pa:
                            paa = x.split(":")
                            if(len(paa) > 1):
                                if(int(paa[1]) > 0 and (x not in m or (m[dt][paa[0]] == 0))):
                                    mcat0[dt][paa[0]] += 1

                            else:
                                if( x not in mcat0):
                                    mcat0[x] = {col:0 for col in userfields}
                                dt = x


with open(f1,'r') as fp:
    for l in fp:
        s=""
        pipe = l.split("|")
        if(len(pipe) > 2):
            st = pipe[0]
            t = pipe[2].split(";")
            m = {}
            rf = 0
            for i in t:
                if("," in i):
                    pa = i.split(",")
                    dt = ""
                    for x in pa:
                        paa = x.split(":")
                        if(len(paa) > 1):
                            if(int(paa[1]) > 0 ):
                                mcat0[dt][paa[0]] += 1
                                m[dt][paa[0]] = 1


                        else:
                            if( x not in mcat0):
                                mcat0[x] = {col:0 for col in userfields}
                            m[x] = {col:0 for col in userfields}
                            dt = x




#print(sen, both, r)

outputfile = open(outpath ,"w")

#outputfile.write("DATE ADULT_CONTENT  HEALTH  DRUGS_ALCOHOL_GAMBLING  RACE  VIOLENCE_CRIME  POLITICS  RELATION  LOCATION AC E I PH AD TO O S P T A\n")
outputfile.write("DATE A AC AD ADULT_CONTENT  DRUGS_ALCOHOL_GAMBLING  E HEALTH  I LOCATION O P PH POLITICS  RACE  RELATION  S T TO VIOLENCE_CRIME\n")
for k,v in sorted(mcat0.items()):
    s = k + " "
    for kk,vv in sorted(v.items()):
        s = s  + str(vv) + " "        
    outputfile.write(s + "\n")
outputfile.close()

outputfile = open(outpath +".sen","w")
outputfile.write("DATE ADULT_CONTENT  HEALTH  DRUGS_ALCOHOL_GAMBLING  RACE  VIOLENCE_CRIME  POLITICS  RELATION  LOCATION\n")

sen = ['ADULT_CONTENT', 'HEALTH', 'DRUGS_ALCOHOL_GAMBLING', 'RACE', 'VIOLENCE_CRIME', 'POLITICS', 'RELATION', 'LOCATION']

for k,v in sorted(mcat0.items()):
    s = k + " "
    tot = 0
    for i in sen: 
        #tot += mcat0[k][i]
        s = s  + str(mcat0[k][i]) + " "      
    outputfile.write(s + "\n")
outputfile.close()

outputfile = open(outpath +".per","w")
outputfile.write("DATE AC E I PH AD\n")
per = ['AC','E','I','PH','AD']
for k,v in sorted(mcat0.items()):
    s = k + " "
    tot = 0
    for i in per: 
        #tot += mcat0[k][i]
        s = s  + str(mcat0[k][i]) + " "      
    outputfile.write(s + "\n")
outputfile.close()






