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
from scoreboard import Scoreboard
from button import Button
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
        # and create a scoreboard
        self.stats = GameStats(self)
        self.sb = Scoreboard(self)
        
        self.ship = Ship(self)
        self.bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()
        
        self._create_fleet()
        
        # Make the button.
        self.play_button = Button(self, "Play")
        self.easy_button = Button(self, "Easy", "left", 100)
        self.medium_button = Button(self, "Medium", position_y = 100)
        self.hard_button = Button(self, "Hard", "right", 100)
        
    def run_game(self):
        '''
        Start the main loop of the game
        '''
        while True:
            # Watch for keyboard and mouse event
            self._check_events()
            if self.stats.game_active:
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
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self._check_play_button(mouse_pos)
                self._check_difficulty_button(mouse_pos)
                
    def _check_play_button(self, mouse_pos):
        '''Start a new game whtn the player clikcs play'''
        button_clicked = self.play_button.rect.collidepoint(mouse_pos)
        if button_clicked and not self.stats.game_active:
            self.stats.play_button_clicked = True
    
    def _check_difficulty_button(self, mouse_pos):
        '''Choose a difficulty for the game'''
        easy_clicked = self.easy_button.rect.collidepoint(mouse_pos)
        medium_clicked = self.medium_button.rect.collidepoint(mouse_pos)
        hard_clicked = self.hard_button.rect.collidepoint(mouse_pos)
        if easy_clicked and self.stats.play_button_clicked:
            self.stats.play_button_clicked = False
            self._start_game("easy")
        elif medium_clicked and self.stats.play_button_clicked:
            self.stats.play_button_clicked = False
            self._start_game("medium")
        elif hard_clicked and self.stats.play_button_clicked:
            self.stats.play_button_clicked = False
            self._start_game("hard")
            
    def _start_game(self, difficulty):
        '''Start the game with everthing reset to initial state'''
        # Reset the game statistics
        self.stats.reset_stats()
        if difficulty == "easy":
            self.settings.initialize_dynamic_settings()
        elif difficulty == "medium":
            self.settings.medium_difficulty_mode()
        elif difficulty == "hard":
            self.settings.hard_difficulty_mode()
        self.stats.game_active = True
        self.sb.prep_score()
        self.sb.prep_level()
        self.sb.prep_ships()
        
        # Get rid of any remaining aliens and bullets.
        self.aliens.empty()
        self.bullets.empty()
        
        # Create a new fleet and center the ship.
        self._create_fleet()
        self.ship.center_ship()
        
        # Hide the mouse cursor.
        pygame.mouse.set_visible(False)
    
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
        elif event.key == pygame.K_p:
            if not self.stats.game_active:
                self.stats.play_button_clicked = True
        elif event.key == pygame.K_q:
            pygame.quit()
            sys.exit()
    
    def _testing_key(self):
        '''Control the effect of a test key'''
        if self.settings.bullets_test:
            self.settings.bullet_width = 300
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
        
        if collisions:
            for aliens in collisions.values():
                self.stats.score += self.settings.alien_points
            self.sb.prep_score()
            self.sb.check_high_score()
        
        if not self.aliens:
            self.bullets.empty()
            self._create_fleet()
            self.settings.increase_speed()
            
            # Increase level.
            self.stats.level += 1
            self.sb.prep_level()
    
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
            
        # Look for aliens hitting the bottom of the screen.
        self._check_aliens_bottom()
                
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
        
    def _check_aliens_bottom(self):
        '''Check if any aliens have reached the bottom of the screen'''
        screen_rect = self.screen.get_rect()
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= screen_rect.bottom:
                # Treat this the same as if the ship got hit.
                self._ship_hit()
                break
        
    def _ship_hit(self):
        '''Respnd to the ship being hit by an alien'''
        if self.stats.ship_left > 0:
            # Decrement ships_left and update scoreboard
            self.stats.ship_left -= 1
            self.sb.prep_ships()
            
            # Get rid of any remaining aliens and bullets
            self.aliens.empty()
            self.bullets.empty()
            
            # Create a new fleet and center the ship
            self._create_fleet()
            self.ship.center_ship()
            
            # Pause
            sleep(0.5)
        else:
            self.stats.game_active = False
            self.stats.play_button_clicked = False
            pygame.mouse.set_visible(True)
    
    def _update_screen(self):
        '''Update images on the screen and flip to the new screen.'''
        self.screen.fill(self.settings.bg_color)
        self.ship.blitme()
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()
        self.aliens.draw(self.screen)
        
        # Draw the score information.
        self.sb.show_score()
        
        # Draw the play button if the game is inactive.
        if not self.stats.game_active and not self.stats.play_button_clicked:
            self.play_button.draw_button()
        
        # Draw the difficulty buttons when play button is clicked
        if self.stats.play_button_clicked:       
            self.easy_button.draw_button()
            self.medium_button.draw_button()
            self.hard_button.draw_button()
        # Make the most recently drawn screen visible
        pygame.display.flip()
   
if __name__ == "__main__":
    # Make a game instance, and run the game
    ai = AlienInvasion()
    ai.run_game()
















