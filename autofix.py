#!/usr/bin/python
#
import sys
import argparse
import re
import string
import aspell
import time
import csv

table = string.maketrans("","")
exclude = set(string.punctuation)
speller = aspell.Speller('lang', 'en')

def test_trans(s):
    return s.translate(table, string.punctuation)

def ignoreword(s):
    match1 = re.search('@[A-Z0-9.-]+',s)        # @[A-Z0-9.-]+ -- at-sign and rest of CAPS WORD
    match2 = re.search('^[0-9],[a-zA-Z]+',s)    # ^[0-9],[a-zA-Z]+ -- numbercomma and rest of word 
    match3 = re.search('^[0-9],\"[a-zA-Z]+',s)      # ^[0-9],\"[a-zA-Z]+ -- numbercommadoublequote
    match4 = re.search('^[A-Z]+',s)      # ^[A-Z]+ -- all CAPS 
    if (match1 or match2 or match3 or match4):
        ignoreword = True
    else:
        ignoreword = False
#    print "Checking ignoreword:", s, "was", ignoreword, "checks made", match1, match2, match3, match4
    return ignoreword

def dashrepl(matchobj):
    if matchobj.group(0) == '-': return ' '
    else: return '-'


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
parser.add_argument('-j','--journalfile',
    help='File where changes should be journaled.',
    default="autoaspell_journal.txt",
    required=False)

args = vars(parser.parse_args())

journal = []
lineno = 0
wordno = 0
journal.append(('line_number','word_number','word_in_file','parrsed_word','best_suggested_word')) # set header row

print "Parsing..."

with open(args['infile'],'rb') as fin:
    for line in fin:
        lineno = lineno + 1
        newline = line
#        parsedword = ''

        for word in line.split():
            wordno = wordno + 1
            parsedword = word.translate(table, string.punctuation)

            if not speller.check(parsedword):                       # if not found in dictionary 
                if not ignoreword(word):                            # if not an ignoreword
                    suggwords = speller.suggest(parsedword)         # get suggestions
                    if (len(suggwords) > 0):
                        bestword = suggwords[0]                     # if suggestions exist, pick best
                    else:
                        bestword = parsedword                     # if no suggestion, set to self
                    journal.append((lineno, wordno, word, parsedword, bestword))

                    if not speller.check(parsedword):
#                        print line
#                        print word, parsedword, bestword
                        newline = re.sub(parsedword, bestword, newline)
#                        print newline
#                        time.sleep(1)

        wordno = 0

        with open(args['outfile'], 'a') as myfile:
            myfile.write(newline)

with open(args['journalfile'],'wb') as jfo:
    writer = csv.writer(jfo, delimiter='|', quoting=csv.QUOTE_NONNUMERIC)
    writer.writerows(journal)
