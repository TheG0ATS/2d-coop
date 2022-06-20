import arcade
import socket
import pickle
import threading
from pyglet.gl.gl import GL_NEAREST
from constants import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    SCREEN_TITLE,
    CHARACTER_SCALING,
    TILE_SCALING,
    GRAVITY,
    PLAYER_MOVEMENT_SPEED,
    PLAYER_JUMP_SPEED,
    SERVER,
    R_PORT,
    S_PORT,
    FORMAT,
    ADDRESS,

)

ADDRESS = (SERVER, R_PORT)

from player import Player

# R_port = port

try:
    sending_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sending_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    sending_socket.connect((SERVER, R_PORT))
except:
    sending_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sending_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    sending_socket.connect((SERVER, R_PORT+1))

try:
    receiving_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    receiving_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    receiving_socket.connect((SERVER, S_PORT))
except:
    receiving_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    receiving_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    receiving_socket.connect((SERVER, S_PORT+1))


received_list = None

def get_server_data():
    global received_list
    while True:
        try:
            received = receiving_socket.recv(2048)

            data = pickle.load(received)
            if isinstance(data, dict) and set(data.keys()) == {0,1}:
                received_list = data
            else:
                print("This is not the data you are looking for: ", data)

        except Exception as e:
                print("get_server_data error", e)


class Game(arcade.Window):
    def __init__(self):
        super().__init__(width=SCREEN_WIDTH, height=SCREEN_HEIGHT, title=SCREEN_TITLE)

        self.scene = None
        self.player = None
        self.physics_engine = None
        self.players_list = None
        self.current_level = None

    def setup(self):

        self.map_name = ":resources:tiled_maps/map.json"
        layer_options = {
            "Platforms": {
                "use_spatial_hash": True,
            },
        }


        self.current_level = arcade.load_tilemap(self.map_name,TILE_SCALING, layer_options)
        self.scene = arcade.Scene.from_tilemap(self.current_level)
    

    def setup_player(self):

        self.send_to_server("SETUP")
        player_number = pickle.loads(sending_socket.recv(2048))
        self.player = Player(player_id=player_number)

    def setup_remote_players(self, number_of_players=2):
        self.players_list = arcade.SpriteList()
        for x in range(number_of_players):
            self.players_list.append(sprite=Player())

    def setup_physics_engine(self, walls, ):
        self.physics_engine= arcade.PhysicsEnginePlatformer(self.player, GRAVITY, walls=walls)
        
    def quit_game(self):
        self.send_to_server("DISCONNECT")
        arcade.exit()

    def on_key_press(self):

        handle_key_press = {
            arcade.key.RIGHT: self.player.move_right,
            arcade.key.LEFT: self.player.move_left,
            arcade.key.UP: self.player.jump,
            arcade.key.ESCAPE: self.quit_game,
        }

        

    def on_key_release(self, symbol):

        if symbol in [arcade.key.RIGHT,arcade.key.LEFT,]:
            self.player.change_x = 0

    def on_draw(self):

        self.clear()
        self.scene.draw(filter=GL_NEAREST)

        if not self.player:
            self.setup()

        for player in self.players_list:
            player.draw()

        self.player.draw()

    # dig deeper here
    @staticmethod
    def player_connected(player):
        return player.center_y > -800

    def send_to_server(self, msg):
        try:
            message = pickle.dumps(msg)
            sending_socket.send(message)
        except Exception as e:
            print("Error in sending to server: ", e)

    # Send location of player to server
    def update_server(self):
        local_player_data ={
            "x": self.player.center_x,
            "y": self.player.center_y,
            "velocity_x": self.player.change_x,
            "velocity_y": self.player.change_y,
        }

        self.send_to_server(local_player_data)

    # Gets location of other player from server
    def update_player_data(self):
        try:
            for index, player in enumerate(self.players_list):
                server_data = {
                    'server_center_x': float(received_list[index]['x']),
                    'server_center_y': float(received_list[index]['y']),
                    'server_change_x': float(received_list[index]['velocity_x']),
                    'server_change_y': float(received_list[index]['velocity_y']),
                    'player_id': index,
                }
                player.player_id = index
                if index == self.player.player_id:
                    pass
                else:
                    player.update_with_server_data(server_data)
                
                # TODO Handle health or other variables we might want
                # for key, value in received_list.items():
                #     if index == self.player.player_id:
                #         pass
                #     player
        except Exception as e:
            print('Error in players list loop: ', e)

    def on_update(self, delta_time):
        if not self.player:
            self.setup()
        self.player.update()
        self.player.on_update(delta_time)
        self.physics_engine.update()
        self.update_server()
        self.update_player_data()
        self.players_list.update()
        self.players_list.on_update()

def main():
    thread = threading.Thread(target=get_server_data, args=())
    thread.start()
    window = Game()
    window.setup()
    arcade.run()

if __name__ == '__main__':
    main()

        
