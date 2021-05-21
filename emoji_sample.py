import emoji
import enchant
import nltk
import re

english_ch = re.compile("[A-Za-z0-9]+")
#===================================================================================#
'''
Check if a token is an emoji
'''
def is_emoji(word):
    if any(char in emoji.UNICODE_EMOJI for char in word):
        return True
    return False
#===================================================================================#
"""
Remove all digits and special characters
"""
def remove_special(tokens):
  return [re.sub("(\\d|\\W)+", " ", token) for token in tokens]
#===============================================================#
"""
Remove blancs on words
"""
def remove_blanc(tokens):
    return [token.strip() for token in tokens]
#===============================================================#


s= ['😍😍😍', '🍕🍕', '🚕🚕🚕', '🥟🥟🥟', '😛🍖🍖🍖🍖🍖🍖🍗🍗🍗🍗🍗🍗', 'I\’m still not going but I\’m contributing bc I love u 👯<U+200D>♀️','Kamil’s baby 👶🚿', 'One medium set. Go Hannah💪', '🎉', '🚙 vroom-vroom', '2/2 lmao idk how to count','That favor bro 🎉💇', '🐔  pocket pesto', 'a','b','2323','thg','pkl']

conlyemoji = 0
conlytext = 0
ctextemoji = 0


for note in s:
    origtokens = nltk.word_tokenize(note)
    origtokens = remove_blanc(origtokens)
    english = 0
    if(english_ch.search(note) is not None):
        english = 1


    onlyemoji = 0
    for t in origtokens:
        if(is_emoji(t)):
            if(english == 1):
                print(note,"TEXT + EMOJI")
                ctextemoji += 1
                break 
            else:
                onlyemoji += 1
    if(onlyemoji ==  len(origtokens) and onlyemoji > 0):
        print(note,"ONLY EMOJI")
        conlyemoji += 1

conlytext = len(s) - ctextemoji - conlyemoji
print("########################")
print("ONLY EMOJI",conlyemoji)
print("TEXT + EMOJI",ctextemoji)
print("ONLY TEXT",conlytext)

