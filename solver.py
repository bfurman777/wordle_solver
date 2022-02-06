import string
import requests

WORDLE, NERDLEGAME = 0,1

# --------------------#
GAME_MODE = NERDLEGAME
# --------------------#

# all lowercase (position is the 0-indexed index):
known = {1:'1'}  # {position:letter}
maybes = {'3':[0], '=':[5], '7':[6]}  # {letter:[not_pos]}  # correct_letter_wrong_location
nots = set('+456')  # string of letters

results = []  # string outputs

'''
Solve the global word 'test_str'
@param i: current index we are checking
@param alphabet: string of valid characters to be in the result
@param buf: array of character of the length of the result
@return None: a list of solutions will be in the global results array
'''
def solve(i, alphabet, buf):
    # end case, we have a word canditate
    if i == len(buf):
        # check that we aquired all chars from correct_letter_wrong_location
        for c in maybes:
            if c not in buf:
                return  # end of this DFS
        results.append(''.join(buf))
        return
    # we know this index
    if i in known:
        buf[i] = known[i]
        solve(i+1, alphabet, buf)
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
        buf[i] = c
        solve(i+1, alphabet, buf)

if __name__ == '__main__':

    if GAME_MODE == WORDLE:
        WORD_LEN = 5
        ENGLISH_WORDS_LINK = 'https://raw.githubusercontent.com/dwyl/english-words/master/words.txt'

        with requests.get(ENGLISH_WORDS_LINK) as res:
            all_words = set(s.lower() for s in res.text.split('\n') if len(s) == WORD_LEN)

        solve(i=0, alphabet=string.ascii_lowercase, buf=[None for i in range(WORD_LEN)])

        actual_results = []
        for w in results:
            if w in all_words:
                actual_results.append(w)


    elif GAME_MODE == NERDLEGAME:
        WORD_LEN = 8

        solve(i=0, alphabet='0123456789+-*/=', buf=[None for i in range(WORD_LEN)])

        actual_results = []
        for w in results:
            if w.count('=') != 1:
                continue  # there has to be exaclty 1 '='
            left, right = w.split('=')
            # check for '//' and '**', which are valid in python but not real math
            illegal_operator = False
            for i in range(len(w)-1):
                if w[i] == w[i+1] and w[i] in '*/':
                    illegal_operator = True
            if illegal_operator: continue
            try: # try for leading zeros
                if eval(left) == eval(right):  # Note: false positive with '**'
                    actual_results.append(w)
            except: continue


    # print results
    print('actual results:', len(actual_results)) 
    print(actual_results)

    if (len(actual_results) == 0):
        print('results:', len(results)) 
        print(results)

