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

sending_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sending_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
sending_socket.bind((SERVER, S_PORT))

receiving_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
receiving_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
receiving_socket.bind((SERVER, R_PORT))

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


