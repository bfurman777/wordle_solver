import time
import keyboard # pip3 install keyboard
from internet import *
import pyautogui
from tries import *
import math
from PIL import ImageGrab
from functools import partial
ImageGrab.grab = partial(ImageGrab.grab, all_screens=True)

WORDLE, NERDLEGAME, SQUABBLE = 0,1,2
BOT, PERSON = 0,1
pyautogui.PAUSE = 0.01

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
    print("Place mouse on the screen that has the game, and press ` (button above Tab)") # scale to screenshot
    mousePosition = ()
    while True:
        key = keyboard.read_key()
        if key == '`':
            mousePosition = pyautogui.position()
            #print(mousePosition)
            break
    myScreenshot = pyautogui.screenshot()
    
    width, height = myScreenshot.size
  
    for i in range(0,width):
        for j in range(0,height):
            vals = myScreenshot.getpixel((i,j))
            diff = math.sqrt(math.pow(emptyColor[0],2)+math.pow(emptyColor[1],2)+math.pow(emptyColor[2],2))
            if abs(math.sqrt(math.pow(vals[0],2)+math.pow(vals[1],2)+math.pow(vals[2],2)) - diff) < 8:
                #print("AT " + str(i) + " j: " + str(j))
                counter = 1
                while myScreenshot.getpixel((i + counter,j)) == emptyColor:
                    counter = counter + 1
                if counter == 1:
                    continue
                #print("counter: " + str(counter))
                grid = 1
                while myScreenshot.getpixel((i + counter + grid,j)) != emptyColor:
                    grid = grid + 1
                #print("grid: " + str(grid))
                if grid == 1:
                    continue
                print("GRID FOUND")
                #print(myScreenshot.getpixel((i + int(3 * counter / 2 + grid),j)) == emptyColor)

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
                    with open('grid.txt','w') as f:
                        f.write(str(i + int(counter / 2)) + '\n')
                        f.write(str(j + 5*(counter + grid)) + '\n')
                        f.write(str(counter + grid) + '\n')
                        f.write(str(mousePosition[0]) + '\n')
                        f.write(str(mousePosition[1]) + '\n')

                    return i + int(counter / 2), j, counter, grid, mousePosition[0], mousePosition[1]
    myScreenshot.save('grid.png')             
    return -1,-1,-1,-1
    
if __name__ == '__main__':
    PLAYER = -1
    known = {} # ex: {2:'i'}  # {position:letter}
    maybes = {} # ex: {'l':[1]}  # {letter:[not_pos]}  # correct_letter_wrong_location
    nots = set('') # ex: set('ave')  # string of letters

    startx = 692 
    endy = 777
    next = 75

    MOUSEX = 0
    MOUSEY = 0
    starty = 404
    blank = (167,113,248)
    green = (46,216,60)
    wrong = (155,93,247)
    yellow = (214,190,0)
    grid = (130,53,245)
    firstGuess = 'crane'
    
    game = input("reset Grid? ")
    if game == 'y' or game == "Y" or game == 'yes' or game == 'Yes' or game == 'YES':
        startx, starty, next, gridSpace, MOUSEX, MOUSEY = detectGrid(blank,grid)
        endy = starty + 5*(next + gridSpace)
        print("You only need to run this once as long as you play Squabble on the same screen in the same resolution")
        print("New Grid: ")
        print("startx: " + str(startx))
        print("endy: " + str(endy))
        #print(gridSpace)
        next = next + gridSpace
        print("next: " + str(next))
    else:
        with open('grid.txt','r') as f:
            lines = f.readlines()
            print(lines)
            startx = int(lines[0])
            endy = int(lines[1])
            next = int(lines[2])
            MOUSEX = int(lines[3])
            MOUSEY = int(lines[4])

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
    pyautogui.click(x=MOUSEX, y=MOUSEY)
    print("== NEW WORD ==")
    
    guessCount = 0
    myguess = ""
    tree = tri(firstGuess)
    myList = WORDLE_ANSWER_SET
    for i in myList:
        tree.insert(i, 0.1)
    myList = WORDLE_GUESS_SET
    for i in myList:
        tree.insert(i, 0)

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
                typed = tree.recursiveFind(tree.head, 0, "", tree.notLocated)[1]
                #print(typed)
                for l in typed:
                    pyautogui.press(l)
                pyautogui.press('enter')

            print('Word entered: ' + typed)
            # detect if word went through
            time.sleep(.2)
            myScreenshot = pyautogui.screenshot()
            #myScreenshot.save('afterGuess.png')
            #print("guess " + str(guessCount))
            #print( endy - (5 - guessCount) * next)

            if restartRound:
                break
            elif PLAYER == BOT and myScreenshot.getpixel((startx, endy - (5 ) * next)) == blank and myScreenshot.getpixel((startx + next, endy - (5 ) * next)) == blank and \
                myScreenshot.getpixel((startx + 2*next, endy - (5 ) * next)) == blank and myScreenshot.getpixel((startx + 3*next, endy - (5 ) * next)) == blank and \
                myScreenshot.getpixel((startx + 4*next, endy - (5 ) * next)) == blank:
                print("NEXT WORD!")
                restartRound = True
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
                tree.findAWordNoInput( typed, ['s'])
                typed = tree.recursiveFind(tree.head, 0, "", tree.notLocated)[1]
            else:
                validWord = True
                guessCount = guessCount + 1

        
        if restartRound:
            print("== NEW WORD ==")
            guessCount = 0
            tree.findAWordNoInput( typed, ['q'])
            typed = ""
            continue
        
        time.sleep(0.1)
        WORD_LEN = 5

        myScreenshot = pyautogui.screenshot()
        #myScreenshot.save('screen.png')
        #myScreenshot = Image.open("test.png")

        #TODO: detect on which screen and the resolution, better key release events
        colors = []
        for pos in range(0,6):
            if myScreenshot.getpixel((startx, endy - pos * next)) == blank:
                #print("is blank")
                if pos == 5 and guessCount != 0:
                    restartRound = True
                    break
            else:
                for i in range(0, WORD_LEN):
                    pixel = myScreenshot.getpixel((startx + i * next, endy - pos * next))
                    #print(pixel)
                    if pixel == green:
                        colors.append("G")
                        #print("is green")
                    if pixel == yellow:
                        colors.append("Y")
                        #print("is yellow")
                    if pixel == wrong:
                        colors.append("B")
                        #print("is wrong")
                break
        #print(colors)

        if restartRound or colors == ['G','G','G','G','G']:
            print("== NEW WORD ==")
            time.sleep(0.3)
            tree.findAWordNoInput( typed, ['q'])
            guessCount = 0
            typed = ""
            continue

        tree.findAWordNoInput( typed, colors)

        