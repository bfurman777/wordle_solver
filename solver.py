import string
import requests

WORDLE, NERDLEGAME = 0,1

# edit this:
# --------------------------------------------------------#
GAME_MODE = WORDLE

# all lowercase (position is the 0-indexed index):
known = {2:'i'}  # {position:letter}
maybes = {'l':[1]}  # {letter:[not_pos]}  # correct_letter_wrong_location
nots = set('ave')  # string of letters
# --------------------------------------------------------#


results = []  # global string outputs
legal_words = None  # global wordlist for game-specific checks

# different game modes need additional checks
def wordle_verify(buf):
    global legal_words
    if legal_words is None:
        ENGLISH_WORDS_LINK = 'https://raw.githubusercontent.com/dwyl/english-words/master/words.txt'
        with requests.get(ENGLISH_WORDS_LINK) as res:
            legal_words = set(s.lower() for s in res.text.split('\n') if len(s) == WORD_LEN)
    if ''.join(buf) in legal_words:
        return True
    return False

def nerdle_verify(buf):
    if buf.count('=') != 1:
        return False  # there has to be exaclty 1 '='
    for i in range(len(buf)-1): # check for '//' and '**', which are valid in python but not real math
        operators = '+-*/'
        if buf[i] in operators and buf[i+1] in operators:
            return False
    try: # try for leading zeros
        split_i = buf.index('=')
        left, right = ''.join(buf[:split_i]), ''.join(buf[split_i+1:])
        if eval(left) == eval(right):
            # print(left, '     ', right)
            return True
    except:
        return False

additional_verify = { 
    WORDLE: wordle_verify,
    NERDLEGAME: nerdle_verify
}

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
        # additional checks for the game mode
        if not additional_verify[GAME_MODE](buf):
            return
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
        solve(i=0, alphabet=string.ascii_lowercase, buf=[None for i in range(WORD_LEN)])

    elif GAME_MODE == NERDLEGAME:
        WORD_LEN = 8
        solve(i=0, alphabet='0123456789+-*/=', buf=[None for i in range(WORD_LEN)])

    print('results:', len(results)) 
    print(results)
    # print most vaired result
    try:
        best_str = results[0]
        best_unique = set(results[0])
        for r in results:
            unique = set(r)
            if len(unique) > len(best_unique):
                best_unique = unique
                best_str = r
        print()
        print(f'Most spread result: {best_str}')
    except: pass

