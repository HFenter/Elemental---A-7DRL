import libtcodpy as libtcod
import math
import textwrap
import shelve

import config
import gamescreen
import gamemap
import gameobjects
import gameinput

import gameactions

import gamemessages



config.read_config()



def game_loop():
	player_action = None
	
	(gamescreen.camera_x, gamescreen.camera_y) = (0, 0)
	gamescreen.initialize_fov()

	gameinput.game_state = 'playing'

	while not libtcod.console_is_window_closed():
		#render the screen
		libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS|libtcod.EVENT_MOUSE,gameinput.key,gameinput.mouse)
		gamescreen.render_all()

		libtcod.console_flush()

		#erase all objects at their old locations, before they move
		for object in gameobjects.objects:
			object.clear()

		#handle keys and exit game if needed
		player_action = gameinput.handle_keys()
		if player_action == 'exit':
			break
		#let monsters take their turn
		#gamemessages.message('Last State ' + game_state, libtcod.blue)
		if gameinput.game_state == 'playing' and player_action != 'no-turn':
			for object in gameobjects.objects:
				if object.ai:
					object.ai.take_turn()


def new_game():
	global game_state

	gameobjects.init_objects()

	#generate map (at this point it's not drawn to the screen)
	gamemap.make_map()

	gamescreen.initialize_fov()

	gameinput.game_state = 'playing'

	#create the list of game messages and their colors, starts empty
	gamemessages.game_msgs = []

	#a warm welcoming message!
	gamemessages.message('Welcome stranger! Prepare your butts.', libtcod.red)
	gamemessages.message('Message 1.', libtcod.red)
	gamemessages.message('Message 2', libtcod.red)
	gamemessages.message('Message 3.', libtcod.red)
	gamemessages.message('Message 4.', libtcod.red)
	gamemessages.message('Message 5.', libtcod.red)
	gamemessages.message('Message 6.', libtcod.red)
 


def main_menu():
    img = libtcod.image_load('ElementalMenu.png')
 
    while not libtcod.console_is_window_closed():
        #show the background image, at twice the regular console resolution
        libtcod.image_blit_2x(img, 0, 0, 0)
 
        #show the game's title, and some credits!
        libtcod.console_set_default_foreground(0, libtcod.light_yellow)
        #libtcod.console_print_ex(0, config.SCREEN_WIDTH/2, config.SCREEN_HEIGHT/2-4, libtcod.BKGND_NONE, libtcod.CENTER, 'Elemental')
        
        #show options and wait for the player's choice
        choice = gamescreen.menu('', ['Play a new game', 'Continue last game', 'Quit'], 24)
        if choice == 0:  #new game
            new_game()
            game_loop()
        if choice == 1:  #load last game
            try:
                load_game()
            except:
                gamescreen.msgbox('\n No saved game to load.\n', 34)
                continue
            game_loop()
        elif choice == 2:  #quit
            break  


#############################################
# Initialization & Main Loop
#############################################

gamescreen.main_init()
gamescreen.game_screen_init()

 



main_menu()
#play_game()
 
 











