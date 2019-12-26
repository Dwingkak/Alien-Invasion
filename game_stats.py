# -*- coding: utf-8 -*-
"""
Created on Tue Dec 24 08:29:10 2019

@author: Kdwing
"""

class GameStats:
    '''Track statistics for Alien Invasion.'''
    def __init__(self, ai_game):
        '''Initialize statistics.'''
        self.settings = ai_game.settings
        self.reset_stats()
        # Start Alien Invasion in an inactive state.
        self.game_active = False
        self.play_button_clicked = False
    
    def reset_stats(self):
        '''Initialize statistics that can change during the game.'''
        self.ship_left = self.settings.ship_limit