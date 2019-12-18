# -*- coding: utf-8 -*-
"""
Created on Sat Dec 14 16:48:41 2019

@author: Kdwing
"""

class Settings:
    """ A class to store all settings for Alien Invasion"""
    
    def __init__(self):
        '''Initialize the game's settings.'''
        # Screen settings
        self.screen_width = 1200
        self.screen_height = 800
        self.bg_color = (230, 230, 230)
        
        # Ship settings
        self.ship_speed = 1.5
        