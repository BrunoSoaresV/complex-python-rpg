import pygame
import random

class World:
    def __init__(self):
        self.tile_size = 64
        self.map_width = 20
        self.map_height = 15
         		# Generate random terrain (0 = grass, 1 = water, 2 = mountain)																																										   	 	 	 	 	 	 	 	 	   ... (300 lines of world generation logic) ...