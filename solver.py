import string
from unittest import result
import requests

WORD_LEN = 5
ENGLISH_WORDS_LINK = 'https://raw.githubusercontent.com/dwyl/english-words/master/words.txt'

# all lowercase (position is the 0-indexed index):
known = {2:'i'}  # {position:letter}
maybes = {'l':[1,2], 's':[4,3]}  # {letter:[not_pos]}  # correct_letter_wrong_location
nots = set(c for c in 'abortfpweh')  # [letters]

alphabet = string.ascii_lowercase

test_str = [None for i in range(WORD_LEN)]
results = []  # string outputs

with requests.get(ENGLISH_WORDS_LINK) as res:
    all_words = set([s.lower() for s in res.text.split('\n') if len(s) == 5])

'''
Solve the global word 'test_str'
@param current index we are checking
@return a list of solutions
'''
def solve(i):
    # end case, we have a word canditate
    if i == WORD_LEN:
        # check that we aquired all chars from correct_letter_wrong_location
        for c in maybes:
            if c not in test_str:
                return  # end of this DFS
        results.append(''.join(test_str))
        return
    # we know this index
    if i in known:
        test_str[i] = known[i]
        solve(i+1)
        return
    # try every character in this index
    for c in alphabet:
        if c in nots:  # we shouldn't use this letter at all
            continue 
        if c in maybes: 
            not_pos = maybes[c]
            if i in not_pos:  # we know this letter should be somewhere else
                continue
         # dfs down this path
        test_str[i] = c
        solve(i+1)

solve(0)
actual_results = []
for w in results:
    if w in all_words:
        actual_results.append(w)
print('actual results:', len(actual_results)) 
print(actual_results)

if (len(actual_results) == 0):
    print('results:', len(results)) 
    print(results)
