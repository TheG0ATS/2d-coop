from cmath import exp
from concurrent.futures import thread
from multiprocessing.dummy import connection
from random import random
import socket
import threading
import pickle
from constants import (

    SERVER,
    R_PORT,
    S_PORT,
    FORMAT,
    ADDRESS,

)

# SERVER = "192.168.0.41"
# R_PORT = 5555
# S_PORT = 5007
# FORMAT = 'utf-8'
# ADDRESS = (SERVER, R_PORT)

receiving_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
receiving_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
try:
    receiving_socket.bind((SERVER, R_PORT))
except:
    receiving_socket.bind((SERVER, R_PORT+1))


sending_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sending_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
try:
    sending_socket.bind((SERVER, S_PORT))
except:
    sending_socket.bind((SERVER, S_PORT+1))


players = {
    0: {
        "x": -800,
        "y": -800,
        "velocity_x": 0,
        "velocity_y": 0,
    },
    1: {
        "x": -800,
        "y": -800,
        "velocity_x": 0,
        "velocity_y": 0,
    },
}

def handle_client(connection_receiving, address_receiving, player_id):
    global players

    error_counter = 0
    max_error_count = 5
    while error_counter <= max_error_count:
        try:
            message = pickle.loads(connection_receiving.recv(2048))

            if message == "SETUP":
                connection_receiving.send(pickle.dumps(player_id))
                continue

            if message == "DISCONNECT":
                print("Player has disconnected")
                break
            
            players[player_id] = message

            error_counter -=1
            if error_counter < 0:
                error_counter = 0

        except Exception as e:
            error_counter +=1
            print("handle_client error:", e)

    players["player_id"] = {
        "x": -800,
        "y": -800,
        "velocity_x": 0,
        "velocity_y": 0,
    }

    print(f"Player {player_id} has left the game")

def send_server_data(connection_sending, address_sending, player_id):
    global players

    error_counter = 0
    max_error_count = 5
    while error_counter <= max_error_count:
        try:
            connection_sending.sendto(pickle.dumps(players), (SERVER, 5007))
            errot_counter -= 1
            if error_counter < 0:
                error_counter = 0
        
        except Exception as e:
            error_counter +=1
            print("send_server_data error:", e)

    players = {
    0: {
        "x": -800,
        "y": -800,
        "velocity_x": 0,
        "velocity_y": 0,
    },
    1: {
        "x": -800,
        "y": -800,
        "velocity_x": 0,
        "velocity_y": 0,
    },
    }

    print(f"Player {player_id} was reset")

def start():
    receiving_socket.listen(2)
    sending_socket.listen(2)
    print("Waiting for player to connect")

    player_id = 0
    while True:
        connection_receiving, address_receiving = receiving_socket.accept()
        connection_sending, address_sending = receiving_socket.accept()

        #  deal with players add

        thread = threading.Thread(target=send_server_data, args=(connection_sending, address_sending, player_id))
        thread.start()

        thread = threading.Thread(target=handle_client, args=(connection_receiving, address_receiving, player_id))
        player_id = (player_id + 1) % 2
        thread.start()

        print("New Player", connection_receiving)

if __name__ == "__main__":
    start()
