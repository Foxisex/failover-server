import socket
import os
import sys

def drawField(f,message):
    field = f[:]
    for i in range(9):
        if field[i] == 2:
            field[i] = 'X'
        elif field[i] == 1:
            field[i] = 'O'
        else:
            field[i] = ' '
    p = f'''
    A   B   C
  -------------
1 | {field[0]} | {field[1]} | {field[2]} |
  -------------
2 | {field[3]} | {field[4]} | {field[5]} |
  -------------
3 | {field[6]} | {field[7]} | {field[8]} |
  -------------
  {message}'''
    return p

def winCheck(field):
    for i in range(0,9,3):
        if field[i] == field[i+1] == field[i+2] != 0:
            return field[i]
    for i in range(3):
        if field[i] == field[i+3] == field[i+6] != 0:
            return field[i]
    if(field[0] == field[4] == field[8] != 0):
        return field[0]
    elif(field[2] == field[4] == field[6] != 0):
        return field[2]
    return 0   

def userInputHandler(message):
    num = (int(message[1]) - 1)*3
    if(message[0] == 'B'):
        num += 1
    elif(message[0] == 'C'):
        num += 2
    return num

def serverInputHandler(message):    
    field = []
    for i in message:
        field.append(int(i))
    return field


playerInput = False

backups = [('localhost',2020),('127.0.0.2', 2021), ('127.0.0.2', 2022)]
backupsNum = 1
anus = 0
log = ''
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client_socket.connect(backups[0])
print("Подключено к серверу...")
while True:
    
    try:
        message = 'client' + log
        client_socket.send(message.encode('utf-8'))

        while True:
            if len(log) == 0:
                message = client_socket.recv(1024).decode('utf-8')

                print(message)
                
                cross = bool(int(message))
                print(cross)
                
                active = cross
                print(active)
                
                client_socket.send('+'.encode('utf-8'))
                inputMessage = client_socket.recv(1024).decode('utf-8')
                field = serverInputHandler(inputMessage)
                print(inputMessage)
            elif len(log) < 2:
                inputMessage = client_socket.recv(1024).decode('utf-8')
                field = serverInputHandler(inputMessage)
                os.system('cls')
                print(drawField(field,"Подождите хода опонента..."))
            else:
                inputMessage = client_socket.recv(1024).decode('utf-8')
                field = serverInputHandler(inputMessage)
                os.system('cls')
                print(drawField(field,"Подождите хода опонента..."))\

                
            while True:              
                if(winCheck(field) == int(cross)+1):
                    os.system('cls')
                    print(drawField(field,"ВЫ ПОБЕДИЛИ!"))
                    break
                elif(winCheck(field) == int(not(cross))+1):
                    os.system('cls')
                    print(drawField(field,"ВЫ ПРОИГРАЛИ!"))
                    break
                elif(field.count(0) == 0):
                    os.system('cls')
                    print(drawField(field,"НИЧЬЯ!"))
                    break
                
                if(active):
                    inputMessage = client_socket.recv(1024).decode('utf-8')
                    field = serverInputHandler(inputMessage)
                    if(winCheck(field) == int(cross)+1):
                        os.system('cls')
                        print(drawField(field,"ВЫ ПОБЕДИЛИ!"))
                        break
                    elif(winCheck(field) == int(not(cross))+1):
                        os.system('cls')
                        print(drawField(field,"ВЫ ПРОИГРАЛИ!"))
                        break
                    elif(field.count(0) == 0):
                        os.system('cls')
                        print(drawField(field,"НИЧЬЯ!"))
                        break
                    os.system('cls')
                    print(drawField(field,"Куда вы хотите походить:"))
                    
                    while True:
                    
                        if(playerInput == False):
                            playerInput = input()
                            
                        if((playerInput[0] == 'A' or playerInput[0] == 'B' or playerInput[0] == 'C') and 
                        ((playerInput[1] == '1' or playerInput[1] == '2' or playerInput[1] == '3'))):
                            outputMessage = userInputHandler(playerInput)
                            playerInput = False
                            if(field[outputMessage] == 0):
                                log = str(int(cross)) + str(outputMessage)
                                client_socket.send(str(outputMessage).encode('utf-8'))
                                inputMessage = client_socket.recv(1024).decode('utf-8')
                                if(inputMessage != 'R'):
                                    break
                                
                            else:
                                os.system('cls')
                                print(drawField(field,"Эта клетка уже занята! Повторите ввод:")) 
                                playerInput = False
                                continue
                        else:
                            os.system('cls')
                            print(drawField(field,"Неправильно введены данные(пример A1) повторите ввод:")) 
                            playerInput = False
                            continue
                        print(drawField(field,"Ошибка ввода:"))
                        playerInput = False
                    field = serverInputHandler(inputMessage)
                    log = str(int(cross))
                       
                else:
                    os.system('cls') 
                    print(drawField(field,"Подождите хода опонента..."))\
                
                active = not(active)
                
                
            input('Нажмите enter что бы начать следующую партию.')
    except ConnectionResetError:
        
        exc_type, exc_value, exc_traceback = sys.exc_info()
        print(f"Error code: {exc_type.__doc__}")
        
        
        client_socket.close()
        
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        
        client_socket.connect(backups[backupsNum])
        backupsNum += 1
        anus = 2