#!/usr/bin/python
#
import sys
import argparse
import re
import string
import aspell
import time

table = string.maketrans("","")
exclude = set(string.punctuation)
speller = aspell.Speller('lang', 'en')

def test_trans(s):
    return s.translate(table, string.punctuation)

def ignoreword(s):
    match1 = re.search('@[A-Z0-9.-]+',s)        # @[A-Z0-9.-]+ -- at-sign and rest of CAPS WORD
    match2 = re.search('^[0-9],[a-zA-Z]+',s)    # ^[0-9],[a-zA-Z]+ -- numbercomma and rest of word 
    match3 = re.search('^[0-9],\"[a-zA-Z]+',s)      # ^[0-9],\"[a-zA-Z]+ -- numbercommadoublequote
    if (match1 or match2 or match3):
        ignoreword = True
    else:
        ignoreword = False
#    print "Checking ignoreword:", s, "was", ignoreword, "checks made", match1, match2, match3
    return ignoreword


parser = argparse.ArgumentParser(description='Used to automatically fix mis-spelled words',
    prog='autoaspell')
parser.add_argument('--version', action='version',
    version='%(prog)s 0.1')
parser.add_argument('infile', nargs='?',
    help='the name of the text file to parse.',
    default=sys.stdin)
parser.add_argument('outfile', nargs='?',
    help='the name of the text file to output.',
    default=sys.stdout)
args = vars(parser.parse_args())

journal = []
journal.append(('word','parrsed_word','suggest_word'))

with open(args['infile'],'rb') as fin:
    for line in fin:
        for word in line.split():
            parsedword = word.translate(table, string.punctuation)
            if not speller.check(parsedword):                       # if not found in dictionary 
                if not ignoreword(word):                            # if not an ignoreword
                    suggword = speller.suggest(parsedword)[0]       # then get a suggestion
                    print word, ",", parsedword, ",", suggword
                    journal.append((word, parsedword, suggword))
#                time.sleep(.5)

#            else:
#                print word

#print journal

#    with open(args['journalfile'],'wb') as jfo:
#        writer = csv.writer(jfo, delimiter='|', quoting=csv.QUOTE_NONNUMERIC)
#        writer.writerows(journal)


#with open(args['manifestfile'], 'wb') as fout:
#    for key in sorted(manifestdict):
#        fout.write(key + " " + ''.join(manifestdict[key]) + "\n")
