import string
from this import d
import time
import requests
import keyboard # pip3 install keyboard
from internet import *
import pyautogui
from PIL import ImageGrab, Image
from functools import partial
ImageGrab.grab = partial(ImageGrab.grab, all_screens=True)

WORDLE, NERDLEGAME = 0,1

legal_words = None  # global wordlist for game-specific checks

# different game modes need additional checks. TODO does this support repeated letters?
def wordle_verify(buf):
    global legal_words
    if legal_words is None:
        legal_words = set(WORDLE_GUESS_SET + WORDLE_ANSWER_SET)
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
@return None: a list of solutions wi`ll be in the global results array
'''
def solve(i, alphabet, buf, dicts):
    known, maybes, nots = dicts
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
        solve(i+1, alphabet, buf, dicts)
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
        solve(i+1, alphabet, buf, dicts)

if __name__ == '__main__':
    results = []
    known = {} # ex: {2:'i'}  # {position:letter}
    maybes = {} # ex: {'l':[1]}  # {letter:[not_pos]}  # correct_letter_wrong_location
    nots = set('') # ex: set('ave')  # string of letters

    startx = 692 # TODO add ability to change screens
    endy = 775
    starty = 405
    next = 74
    blank = (167,113,248)
    green = (46,216,60)
    wrong = (155,93,247)
    yellow = (214,190,0)
    
    game = input("Would you like to play Wordle? ")
    if game == 'y' or game == "Y" or game == 'yes' or game == 'Yes' or game == 'YES':
        GAME_MODE = WORDLE
    else:
        game = input("Would you like to play Nerdle? ")
        if game == 'y' or game == "Y" or game == 'yes' or game == 'Yes' or game == 'YES':
            GAME_MODE = NERDLEGAME
        else:
            print('Then why the hell are you using this program?')
            exit()

    print("== NEW WORD ==")
    while GAME_MODE == WORDLE: #TODO: add nerdle support
        typed = ""
        restartRound = False
        while True:
            while len(typed) < 5:
                key = keyboard.read_key()
                if len(key) == 1 and key.isalpha():
                    typed += key
                    print("received " + key)
                    time.sleep(.2)
                if key == 'backspace':
                    typed = typed[:-1]
                    print('removed: ' + typed)
                    time.sleep(.2)
                if key == '`':
                    restartRound = True
                    break
            if restartRound:
                break
            key = keyboard.read_key()
            if key == 'backspace':
                typed = typed[:-1]
                print('removed: ' + typed)
                time.sleep(.2)
                break
            if key == 'enter':
                break
            if key == '`':
                restartRound = True
                break
        print('Word entered: ' + typed)
        if restartRound:
            print("== NEW WORD ==")
            known = {}  
            maybes = {}
            nots = set('')
            results = []
            continue
        
        time.sleep(0.5)
        WORD_LEN = 5

        myScreenshot = pyautogui.screenshot()
        myScreenshot.save('screen.png')
        #myScreenshot = Image.open("test.png")
        
        for pos in range(0,6):
            if myScreenshot.getpixel((startx, endy - pos * next)) == blank:
                print("is blank")
            else:
                for i in range(0, WORD_LEN):
                    pixel = myScreenshot.getpixel((startx + i * next, endy - pos * next))
                    print(pixel)
                    if pixel == green:
                        known[int(i)] = typed[i]
                        print("is green")
                    if pixel == yellow:
                        if typed[i] in maybes:
                            maybes[typed[i]].append(i)
                        else:
                            maybes[typed[i]] = [i]
                        print("is yellow")
                    if pixel == wrong:
                        nots.add(typed[i])
                        print("is wrong")
                break

        print(known)
        print(maybes)
        print(nots)
        
        solve(i=0, alphabet=string.ascii_lowercase, buf=[None for i in range(WORD_LEN)], dicts=(known,maybes,nots))
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
        results = []
