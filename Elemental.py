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

		gameobjects.check_level_up()

		#erase all objects at their old locations, before they move
		for object in gameobjects.objects:
			object.clear()

		#handle keys and exit game if needed
		player_action = gameinput.handle_keys()
		if player_action == 'exit':
			save_game()
			break
		#let monsters take their turn
		#gamemessages.message('Last State ' + game_state, libtcod.blue)
		if gameinput.game_state == 'playing' and player_action != 'no-turn':
			for object in gameobjects.objects:
				if object.ai:
					object.ai.take_turn()
			gameinput.path_recalc = False


def new_game():
	
	gameobjects.init_objects()
	
	gamemap.dungeon_level = 1
	#generate map (at this point it's not drawn to the screen)
	gamemap.make_map()

	gamescreen.initialize_fov()

	gameinput.game_state = 'playing'
	gameobjects.inventory = []

	#create the list of game messages and their colors, starts empty
	gamemessages.game_msgs = []

	#a warm welcoming message!
	gamemessages.message('Welcome stranger! Prepare your butts.', libtcod.dark_green)
 
def save_game():
	#open a new empty shelve (possibly overwriting an old one) to write the game data
	file = shelve.open('savegame', 'n')
	file['map'] = gamemap.map
	file['objects'] = gameobjects.objects
	file['player_index'] = gameobjects.objects.index(gameobjects.player)  #index of player in objects list
	file['stairs_index'] = gameobjects.objects.index(gamemap.stairs)  #same for the stairs
	file['inventory'] = gameobjects.inventory
	file['game_msgs'] = gamemessages.game_msgs
	file['game_state'] = gameinput.game_state
	file['dungeon_level'] = gamemap.dungeon_level
	file.close()
 
def load_game():
	#open the previously saved shelve and load the game data

	file = shelve.open('savegame', 'r')
	gamemap.map = file['map']
	gameobjects.objects = file['objects']
	gameobjects.player = gameobjects.objects[file['player_index']]  #get index of player in objects list and access it
	gamemap.stairs = gameobjects.objects[file['stairs_index']]  #same for the stairs
	gameobjects.inventory = file['inventory']
	gamemessages.game_msgs = file['game_msgs']
	gameinput.game_state = file['game_state']
	gamemap.dungeon_level = file['dungeon_level']
	file.close()

	gamescreen.initialize_fov()

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
 
 











