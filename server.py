# first of all import the socket library
import socket  
import pyautogui     
pyautogui.PAUSE = 0.01

# next create a socket object
s = socket.socket()        
print ("Socket successfully created")
port = 12345               
s.bind(('', port))        
print ("socket binded to %s" %(port))
 
# put the socket into listening mode
s.listen(5000)    
print("socket is listening")           
 
# a forever loop until we interrupt it or
# an error occurs
c, addr = s.accept() 
while True:
 
# Establish connection with client.   
    print('Got connection from', addr )
    
    data = c.recv(2048).decode()
    # send a thank you message to the client. encoding to send byte type.
    #c.send(('Server received ' + data).encode())

    print(data)
    if data == 'END':
        print('received End server signal.')
        c.close()
        break
    elif len(data) == 5:
        for ch in data:
            print(ch)
            pyautogui.press(ch)
        pyautogui.press('enter')
    elif data == 'ERRORS':
        for i in range(6):
            for ch in 'ERROR':
                #print(ch)
                pyautogui.press(ch)
            pyautogui.press('enter')

