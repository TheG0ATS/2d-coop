import arcade

from constants import (
    
    PLAYER_MOVEMENT_SPEED,
    PLAYER_JUMP_SPEED,
    

)

class Player(arcade.Sprite):
    def __init__(self, player_id=0):
        super().__init__()
        self.center_x = -800
        self.center_y = -800

        image_source = ":resources:images/animated_characters/female_adventurer/femaleAdventurer_idle.png"
        self.player_sprite = arcade.Sprite(image_source, 1)

    def update_with_server_data(self, server_data):

        self.center_x = server_data["server_center_x"]
        self.center_y = server_data["server_center_y"]
        self.change_x = server_data["server_change_x"]
        self.change_y = server_data["server_change_y"]


    def move_left(self):
        
        self.change_x = PLAYER_MOVEMENT_SPEED
    
    def move_right(self):
        
        self.change_x = -PLAYER_MOVEMENT_SPEED
    
    def jump(self):
        
        self.change_y = PLAYER_JUMP_SPEED

    def on_update(self, delta_time):
        pass
