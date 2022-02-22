import string
from this import d
import time
import requests
import keyboard # pip3 install keyboard
from internet import *
import pyautogui
import math
from PIL import ImageGrab, Image
from functools import partial
ImageGrab.grab = partial(ImageGrab.grab, all_screens=True)

WORDLE, NERDLEGAME, SQUABBLE = 0,1,2
BOT, PERSON = 0,1

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
    NERDLEGAME: nerdle_verify,
    SQUABBLE: wordle_verify
}


def detectGrid(emptyColor,gridColor):
    '''
    print("Place mouse in top left corner of all screens and press ` (button above Tab)") # scale to screenshot
    absolutetop = ()
    top = ()
    bottom = ()
    while True:
        key = keyboard.read_key()
        if key == '`':
            absolutetop = pyautogui.position()
            print(absolutetop)
            break
    time.sleep(.5)
    print("Place mouse in top left corner of grid and press ` (button above Tab)")
    while True:
        key = keyboard.read_key()
        if key == '`':
            top = pyautogui.position()
            print(top)
            break
    time.sleep(.5)
    print("Place mouse in bottom right corner of grid and press ` (button above Tab)")
    while True:
        key = keyboard.read_key()
        if key == '`':
            bottom = pyautogui.position()
            print(bottom)
            break

    x = top[0] - absolutetop[0]
    return x, top[1], (bottom[0] - absolutetop[0] - x) / 4, (bottom[1] - top[1]) / 5
    '''
    myScreenshot = pyautogui.screenshot()
    
    width, height = myScreenshot.size
  
    for i in range(0,width):
        for j in range(0,height):
            vals = myScreenshot.getpixel((i,j))
            diff = math.sqrt(math.pow(emptyColor[0],2)+math.pow(emptyColor[1],2)+math.pow(emptyColor[2],2))
            if abs(math.sqrt(math.pow(vals[0],2)+math.pow(vals[1],2)+math.pow(vals[2],2)) - diff) < 8:
                print("AT " + str(i) + " j: " + str(j))
                counter = 1
                while myScreenshot.getpixel((i + counter,j)) == emptyColor:
                    counter = counter + 1
                if counter == 1:
                    continue
                print("counter: " + str(counter))
                grid = 1
                while myScreenshot.getpixel((i + counter + grid,j)) != emptyColor:
                    grid = grid + 1
                print("grid: " + str(grid))
                if grid == 1:
                    continue
                print("NOT A FAIL")
                print(myScreenshot.getpixel((i + int(3 * counter / 2 + grid),j)) == emptyColor)

                if myScreenshot.getpixel((i + int(3 * counter / 2 + grid),j)) == emptyColor and myScreenshot.getpixel((i + 2 * counter + int(3 * grid / 2),j)) == gridColor and \
                   myScreenshot.getpixel((i + int(5 * counter / 2 + 2 * grid),j)) == emptyColor and myScreenshot.getpixel((i + 3 * counter + int(5 * grid / 2),j)) == gridColor and \
                   myScreenshot.getpixel((i + int(7 * counter / 2 + 3 * grid),j)) == emptyColor and myScreenshot.getpixel((i + 4 * counter + int(7 * grid / 2),j)) == gridColor and \
                   myScreenshot.getpixel((i + int(9 * counter / 2 + 4 * grid),j)) == emptyColor and myScreenshot.getpixel((i + 5 * counter + int(9 * grid / 2),j)) == gridColor:
                    myScreenshot.putpixel((i , j), (255, 0, 0))
                    myScreenshot.putpixel((i + int(counter / 2), j), (255, 0, 0))
                    myScreenshot.putpixel((i+ int(3 * counter / 2 + grid), j), (255, 0, 0))
                    myScreenshot.putpixel((i+ int(5 * counter / 2 + 2*grid), j), (255, 0, 0))
                    myScreenshot.putpixel((i+ int(7 * counter / 2 + 3*grid), j), (255, 0, 0))
                    myScreenshot.putpixel((i+ int(9 * counter / 2 + 4*grid), j), (255, 0, 0))
                    myScreenshot.putpixel((i+ int(counter / 2) , j + counter + grid), (255, 0, 0))
                    myScreenshot.putpixel((i+ int(counter / 2) , j + 2*(counter + grid)), (255, 0, 0))
                    myScreenshot.putpixel((i+ int(counter / 2) , j + 3*(counter + grid)), (255, 0, 0))
                    myScreenshot.putpixel((i+ int(counter / 2) , j + 4*(counter + grid)), (255, 0, 0))
                    myScreenshot.putpixel((i+ int(counter / 2) , j + 5*(counter + grid)), (255, 0, 0))
                    myScreenshot.save('grid.png')
                    return i + int(counter / 2), j, counter, grid
    myScreenshot.save('grid.png')             
    return -1,-1,-1,-1
    

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
    PLAYER = -1
    results = []
    known = {} # ex: {2:'i'}  # {position:letter}
    maybes = {} # ex: {'l':[1]}  # {letter:[not_pos]}  # correct_letter_wrong_location
    nots = set('') # ex: set('ave')  # string of letters

    startx = 692 # TODO add ability to change screens
    endy = 777
    starty = 404
    next = 75
    blank = (167,113,248)
    green = (46,216,60)
    wrong = (155,93,247)
    yellow = (214,190,0)
    grid = (130,53,245)
    firstGuess = 'crane'
    
    game = input("reset Grid? ")
    if game == 'y' or game == "Y" or game == 'yes' or game == 'Yes' or game == 'YES':
        startx, starty, next, gridSpace = detectGrid(blank,grid)
        endy = starty + 5*(next + gridSpace)
        print("New Grid: ")
        print(startx)
        print(endy)
        print(next)
        print(gridSpace)
        next = next + gridSpace

    game = input("Would you like to play Squable? ")
    if game == 'y' or game == "Y" or game == 'yes' or game == 'Yes' or game == 'YES':
        GAME_MODE = SQUABBLE
        game = input("Do you want the bot to play for you? ")
        if game == 'y' or game == "Y" or game == 'yes' or game == 'Yes' or game == 'YES':
            PLAYER = BOT
    else:
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

    time.sleep(1)
    print("== NEW WORD ==")
    
    #pyautogui.press('w')
    guessCount = 0
    myguess = ""
    guesses = []
    while GAME_MODE == SQUABBLE: #TODO: add nerdle and wordle support
        
        typed = ""
        restartRound = False
        
        validWord = False
        while not validWord:
            if PLAYER == PERSON:
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
            elif PLAYER == BOT:
                if guessCount == 0:
                    typed = firstGuess
                else:
                    typed = myguess
                for l in typed:
                    pyautogui.press(l)
                pyautogui.press('enter')

            print('Word entered: ' + typed)
            # detect if word went through
            time.sleep(.2)
            myScreenshot = pyautogui.screenshot()
            myScreenshot.save('afterGuess.png')
            print("guess " + str(guessCount))
            #print( endy - (5 - guessCount) * next)

            if restartRound:
                break
            elif PLAYER == BOT and myScreenshot.getpixel((startx, endy - (5 ) * next)) == blank and myScreenshot.getpixel((startx + next, endy - (5 ) * next)) == blank and \
                myScreenshot.getpixel((startx + 2*next, endy - (5 ) * next)) == blank and myScreenshot.getpixel((startx + 3*next, endy - (5 ) * next)) == blank and \
                myScreenshot.getpixel((startx + 4*next, endy - (5 ) * next)):
                print("NEXT WORD!")
                break
            elif myScreenshot.getpixel((startx, endy - (5 - guessCount) * next)) == blank and myScreenshot.getpixel((startx + next, endy - (5 - guessCount) * next)) == blank and \
                myScreenshot.getpixel((startx + 2*next, endy - (5 - guessCount) * next)) == blank and myScreenshot.getpixel((startx + 3*next, endy - (5 - guessCount) * next)) == blank and \
                myScreenshot.getpixel((startx + 4*next, endy - (5 - guessCount) * next)):
                print("WORD DOES NOT EXIST TRY ANOTHER GUESS!")
                pyautogui.press('backspace')
                pyautogui.press('backspace')
                pyautogui.press('backspace')
                pyautogui.press('backspace')
                pyautogui.press('backspace')
                if typed in guesses:
                    guesses.remove(typed)
                if typed in legal_words:
                    legal_words.remove(typed)
                typed = ""
                myguess = guesses[0]
            else:
                validWord = True
                guessCount = guessCount + 1

        
        if restartRound:
            print("== NEW WORD ==")
            guessCount = 0
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

        #TODO: detect on which screen and the resolution, better key release events
        
        for pos in range(0,6):
            if myScreenshot.getpixel((startx, endy - pos * next)) == blank:
                print("is blank")
                if (5 - pos) < guessCount:
                    restartRound = True
                    break
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
        
        if restartRound:
            print("== NEW WORD ==")
            guessCount = 0
            known = {}  
            maybes = {}
            nots = set('')
            results = []
            continue

        print(known)
        print(maybes)
        print(nots)
        
        solve(i=0, alphabet=string.ascii_lowercase, buf=[None for i in range(WORD_LEN)], dicts=(known,maybes,nots))
        print('results:', len(results)) 
        guesses = results
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
            myguess = best_str
        except: pass
        results = []
