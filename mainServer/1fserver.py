import socket
import threading
from config import config

global field, crossMove, isStarted

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

def outputHandler(field):
    s = ''
    for cell in field:
        s += str(cell)
    return s


def handle_player(client_socket, isCross):
    global crossMove, field, isStarted
    while not(isStarted):
        continue
    client_socket.send(str(int(isCross)).encode('utf-8'))
    client_socket.recv(1024)
    message = outputHandler(field)
    client_socket.send(message.encode('UTF-8'))
    while True:
        if(isCross == crossMove):
            message = outputHandler(field)

            client_socket.send(message.encode('UTF-8'))
        
            message = client_socket.recv(1024).decode('utf-8')
            
            
            if(not(message.isdigit())):
                client_socket.send('R'.encode('utf-8'))
                continue
            
            cellNumber = int(message)
            
            if(field[cellNumber] == 0):
                
                field[cellNumber] = int(crossMove) + 1    
                
                if(winCheck(field) != 0 or field.count(0) == 0):
                    field = [0,0,0,0,0,0,0,0,0]
                
                crossMove = not(crossMove)
                
                message = outputHandler(field)

                client_socket.send(message.encode('UTF-8'))
                
                
                
            else:
                client_socket.send('R'.encode('utf-8'))
                
def handle_backup(client_socket):
    global field,crossMove
    while not(isStarted):
        continue
    lastMessage = outputHandler(field)
    addrStr = (addreses[0][0]+':'+str(addreses[0][1])+';'+addreses[1][0]+':'+str(addreses[1][1])).encode('utf-8')
    client_socket.send(addrStr)
    while True:
        message = outputHandler(field) + str(int(crossMove))
        if(lastMessage != message):
            client_socket.recv(1024)
            client_socket.send(message.encode('UTF-8'))
            #lastMessage = message + str(int(crossMove))
            lastMessage = message
def backup_client(client_socket):
    global field,isStarted,crossMove
    
    def serverInputHandler(message):
        field = []
        for i in message:
            field.append(int(i))
        return field
    backupNum = 1
    while True:
        try:
            client_socket.send('+'.encode('utf-8'))
            message = client_socket.recv(1024).decode('utf-8')
            field = serverInputHandler(message[:-1])
            crossMove = bool(int(message[-1]))
        except:
            if(len(config['seniorServers']) == backupNum):
                isStarted = True
                break
            host = config['seniorServers'][backupNum][0]
            port = config['seniorServers'][backupNum][1]
            backupNum += 1
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((host, port))
            client_socket.send('backup'.encode('utf-8'))
            client_socket.recv(1024)
        
        

#field - игровое поле 0 - пусто, 1 - нолик, 2 - крестик.
field = [0,0,0,
        0,0,0,
        0,0,0]


crossMove = True
isStarted = False


players = []
backups = []
addreses = []



def run_server():
    global isStarted
    
    BACKUPSNEEDED = 1
    PLAYERSNEEDED = 2
    
    
    isMain = config['isMain']

    if(not(isMain)):
        
        host = config['seniorServers'][0][0]
        port = config['seniorServers'][0][1]
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((host, port))
        client_socket.send('backup'.encode('utf-8'))
        addrMessage = client_socket.recv(1024).decode('utf-8').split(';')
        
        for i in range(2):
            addr = addrMessage[i].split(':')
            addreses.append((addr[0],int(addr[1])))
        
        backup_thread = threading.Thread(target=backup_client, args=(client_socket,))
        backup_thread.start()
        
        print(addreses)
    
    
    # Создаем сокет
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Получаем имя хоста и порт
    host = config['serverIP']
    port = config['serverPort']

    # Привязываем сокет к адресу и порту
    server_socket.bind((host, port))

    # Слушаем входящие соединения
    server_socket.listen(5)
    print("Сервер запущен...")
    
    
    nextPlayerIsCross = True
    while True:
        
        # Принимаем входящее соединение
        client_socket, client_address = server_socket.accept()
        print(f"Подключен клиент {client_address}")
        
        message = client_socket.recv(1024).decode('utf-8')
        
            
            
        if(message == "client"):
                
            players.append(client_socket)
            if(isMain):
                client_thread = threading.Thread(target=handle_player, args=(client_socket, nextPlayerIsCross))
            else:
                client_thread = threading.Thread(target=handle_player, args=(client_socket, nextPlayerIsCross*crossMove))
            client_thread.start()
            nextPlayerIsCross = False
            if(isMain):
                addreses.append(client_address)
        if(message == "backup"):
            backups.append(client_socket)
            client_thread = threading.Thread(target=handle_backup, args=(client_socket,))
            client_thread.start()
        if(len(players) == PLAYERSNEEDED and len(backups) == BACKUPSNEEDED):
            isStarted = True
        

if __name__ == "__main__":
    run_server()