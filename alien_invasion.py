# -*- coding: utf-8 -*-
"""
Created on Fri Dec 13 09:35:28 2019

@author: Kdwing
"""

import sys
from time import sleep

import pygame

from settings import Settings
from game_stats import GameStats
from ship import Ship
from bullet import Bullet
from alien import Alien

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
        # screen size of 1200 x 800
        self.screen = pygame.display.set_mode(
            (self.settings.screen_width, self.settings.screen_height))
        # setting screen to full screen
        # self.screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
        # self.settings.screen_width = self.screen.get_rect().width
        # self.settings.screen_height = self.screen.get_rect().height
        pygame.display.set_caption("Alien Invasion")
        
        # Create an instance to store game statistics
        self.stats = GameStats(self)
        
        self.ship = Ship(self)
        self.bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()
        
        self._create_fleet()
        
    def run_game(self):
        '''
        Start the main loop of the game
        '''
        while True:
            # Watch for keyboard and mouse event
            self._check_events()
            # Update the status of the ship, aliens and bullet
            self.ship.update()
            self._update_bullets()
            self._update_aliens()
            # Redraw the screen during each pass through the loop
            self._update_screen()
            
    def _check_events(self):
        '''Respond to key presses and mouse events'''
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)
            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)

    
    def _check_keydown_events(self, event):
        '''Respond to keypresses'''
        if event.key == pygame.K_RIGHT:
            # Move the ship to the right
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True
        elif event.key == pygame.K_SPACE:
            self._fire_bullet()
        elif event.key == pygame.K_t:
            self._testing_key()
        elif event.key == pygame.K_q:
            pygame.quit()
            sys.exit()
    
    def _testing_key(self):
        '''Control the effect of a test key'''
        if self.settings.bullets_test:
            self.settings.bullet_width = 100
            self.settings.bullets_allowed = 10
            self.settings.bullets_test = False
        else:
            self.settings.bullet_width = 3
            self.settings.bullets_allowed = 3  
            
    def _check_keyup_events(self, event):
        '''Respond to key releases'''
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False
    
    def _fire_bullet(self):
        '''Create a bullet and add it to the bullets group'''
        if len(self.bullets) < self.settings.bullets_allowed:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)
            
    def _update_bullets(self):
        '''Update position of bullets and get rid of old bullets'''
        # Update bullet positions.
        self.bullets.update()
        # Get rid of bullets that have disappeared.
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)
        
        # Print statement to make sure all bullets are discarded
        # print(len(self.bullets))
        
        # Check for any bullets that have hit the aliens.
        # If so, get rid of the bullet and the alien.
        self._check_bullet_alien_collision()
    
    def _check_bullet_alien_collision(self):
        '''Respond to bullet-alien collision'''
        # Remove any bullets and aliens that have collided
        collisions = pygame.sprite.groupcollide(
            self.bullets, self.aliens, True, True)
        if not self.aliens:
            self.bullets.empty()
            self._create_fleet()
    
    def _update_aliens(self):
        '''
        Check if the fleet is at an edge,
        then update the positions of all aliens in the fleet.
        '''
        self._check_fleet_edges()
        self.aliens.update()
        
        # Look for alien-ship collisions.
        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            self._ship_hit()
                
    def _create_fleet(self):
        '''Create the fleet of aliens.'''
        # Create an alien and find the number of aliens in a row.
        # Spacing between each alien is equal to one alien width.
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        available_space_x = self.settings.screen_width - 2 * alien_width
        number_aliens_x = available_space_x // (2 * alien_width)
        
        # Determine the number of rows of aliens that fit on the screen.
        ship_height = self.ship.rect.height
        available_space_y = (self.settings.screen_height - 
                             (3 * alien_height) - ship_height)
        number_rows = available_space_y // (2 * alien_height)
        
        # Create the full fleet of aliens.
        for row_number in range(number_rows):
            for alien_number in range(number_aliens_x):
                self._create_alien(alien_number, row_number)
    
    def _check_fleet_edges(self):
        '''Respond appropriately if any aliens have reach an edge.'''
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break
    
    def _change_fleet_direction(self):
        '''Drop the entire fleet and change the fleet's direction'''
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1
            
    def _create_alien(self, alien_number, row_number):
        '''Create an alien and place it in the row'''
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        alien.x = alien_width + 2 * alien_width * alien_number
        alien.rect.x = alien.x
        alien.rect.y = alien.rect.height + 2 * alien.rect.height * row_number
        self.aliens.add(alien)
        
    def _ship_hit(self):
        '''Respnd to the ship being hit by an alien'''
        # Decrement ships_left
        self.stats.ship_left -= 1
        
        # Get rid of any remaining aliens and bullets
        self.aliens.empty()
        self.bullets.empty()
        
        # Create a new fleet and center the ship
        self._create_fleet()
        self.ship.center_ship()
        
        # Pause
        sleep(0.5)
    
    def _update_screen(self):
        '''Update images on the screen and flip to the new screen.'''
        self.screen.fill(self.settings.bg_color)
        self.ship.blitme()
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()
        self.aliens.draw(self.screen)
        # Make the most recently drawn screen visible
        pygame.display.flip()
   
if __name__ == "__main__":
    # Make a game instance, and run the game
    ai = AlienInvasion()
    ai.run_game()
















