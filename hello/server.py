from flask import Flask
from os import environ
import socket
import threading
import os

HEADER = 64
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "DISCONNECT"
BLOCK_SIZE = 1024
FILE = "temp{}.wav"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)


def handle_client(connection: socket.socket, address: tuple) -> None:
    print(f"[NEW CONNECTION] {address} connected.")
    connected = True
    while connected:
        try:
            first_message = connection.recv(HEADER)
            if first_message:
                first_message = first_message.decode(FORMAT).strip()
                if DISCONNECT_MESSAGE == first_message:
                    connected = False
                    continue
                msg_length = int(first_message)
                print(f"[MESSAGE RECEIVED] Size: {msg_length}")
                writeFile(connection, msg_length)
                playWav()
                sendMessage = "true".encode(FORMAT)
                connection.send(sendMessage)
                print("[MESSAGE SENT]")
        except Exception as e:
            print(e.__class__)
            sendMessage = "false".encode(FORMAT)
            connection.send(sendMessage)
            print("[ERROR MESSAGE SENT]")
    print("[CONNECTION WAS CLOSED]")
    print("*"*80)
    connection.close()


def deleteTempFile():
    try:
        os.remove(FILE.format(threading.get_ident()))
    except Exception as e:
        print("Exception was thrown: ", e.__class__)
        print(e)


def writeFile(connection: socket.socket, length: int) -> None:
    try:
        wavfile = open(FILE.format(threading.get_ident()), mode="wb")
        soma = 0
        print(length)
        while soma < length:
            message = connection.recv(BLOCK_SIZE)
            soma += len(message)
            wavfile.write(message)
    except Exception as e:
        print("Exception was thrown", e.__class__)
    finally:
        wavfile.close()


def playWav():
    try:
        from playsound import playsound
        playsound(FILE.format(threading.get_ident()))
    except Exception as e:
        print("Exception was thrown: ", e.__class__)


def start() -> None:
    server.listen()
    print(ADDR)
    while True:
        connection, address = server.accept()
        thread = threading.Thread(
            target=handle_client, args=(connection, address))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}.")



app = Flask(__name__)
app.run(environ.get('PORT'))

print("[Starting] server is starting!")
start()
