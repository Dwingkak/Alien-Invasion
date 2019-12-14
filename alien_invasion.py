# -*- coding: utf-8 -*-
"""
Created on Fri Dec 13 09:35:28 2019

@author: Kdwing
"""

import sys
import pygame
from settings import Settings

class AlienInvasion:
    '''
    Overall class to manage game assets and behaviour
    '''
    
    def __init__(self):
        '''
        Initialize the game, and create game resources
        '''
        pygame.init()
        self.settings = Settings()
        self.screen = pygame.display.set_mode(
            (self.settings.screen_width, self.settings.screen_height))
        pygame.display.set_caption("Alien Invasion")
        
        # Set the background colour.
        self.bg_color = (230, 230, 230)
        
    def run_game(self):
        '''
        Start the main loop of the game
        '''
        while True:
            # Watch for keyboard and mouse event
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            
            # Redraw the screen during each pass through the loop
            self.screen.fill(self.settings.bg_color)
            
            # Make the most recently drawn screen visible
            pygame.display.flip()

if __name__ == "__main__":
    # Make a game instance, and run the game
    ai = AlienInvasion()
    ai.run_game()