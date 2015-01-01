import libtcodpy as libtcod

import gameobjects
import gamescreen
import gameactions
import gamemessages

key = libtcod.Key()
mouse = libtcod.Mouse()
game_state = 'loading'

def handle_keys():
	global mouse, key, game_state

	if key.vk == libtcod.KEY_ENTER and libtcod.KEY_ALT:
		#Alt+Enter: toggle fullscreen
		libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())

	elif key.vk == libtcod.KEY_ESCAPE:
		return 'exit'  #exit game

	if game_state == 'playing':
		#movement keys
		if key.vk == libtcod.KEY_UP or key.vk == libtcod.KEY_KP8:
			gameactions.player_move_or_attack(0, -1)
			gamemessages.message('You Move North.', libtcod.green)
		elif key.vk == libtcod.KEY_DOWN or key.vk == libtcod.KEY_KP2:
			gameactions.player_move_or_attack(0, 1)
			gamemessages.message('You Move South.', libtcod.green)
		elif key.vk == libtcod.KEY_LEFT or key.vk == libtcod.KEY_KP4:
			gameactions.player_move_or_attack(-1, 0)
		elif key.vk == libtcod.KEY_RIGHT or key.vk == libtcod.KEY_KP6:
			gameactions.player_move_or_attack(1, 0)
		elif key.vk == libtcod.KEY_HOME or key.vk == libtcod.KEY_KP7:
			gameactions.player_move_or_attack(-1, -1)
		elif key.vk == libtcod.KEY_PAGEUP or key.vk == libtcod.KEY_KP9:
			gameactions.player_move_or_attack(1, -1)
		elif key.vk == libtcod.KEY_END or key.vk == libtcod.KEY_KP1:
			gameactions.player_move_or_attack(-1, 1)
		elif key.vk == libtcod.KEY_PAGEDOWN or key.vk == libtcod.KEY_KP3:
			gameactions.player_move_or_attack(1, 1)
		elif key.vk == libtcod.KEY_KP5:
			pass  #do nothing ie wait for the monster to come to you
		else:
			#test for other keys
			key_char = chr(key.c)
			
			if key_char == 'g':
				#pick up an item
				for object in gameobjects.objects:  #look for an item in the player's tile
					if object.x == gameobjects.player.x and object.y == gameobjects.player.y and object.item:
						object.item.pick_up()
						break

			if key_char == 'i':
				#show the inventory; if an item is selected, use it
				chosen_item = gamescreen.inventory_menu('Press the key next to an item to use it, or any other to cancel.\n')
				if chosen_item is not None:
					chosen_item.use()

			if key_char == 'd':
				#show the inventory; if an item is selected, drop it
				chosen_item = gamescreen.inventory_menu('Press the key next to an item to drop it, or any other to cancel.\n')
				if chosen_item is not None:
					chosen_item.drop()
			
			return 'no-turn'

def get_names_under_mouse():
    global mouse
 
	#return a string with the names of all objects under the mouse
    (x, y) = (mouse.cx, mouse.cy)
    (x, y) = (gamescreen.camera_x + x, gamescreen.camera_y + y)  #from screen to map coordinates
 
	#create a list with the names of all objects at the mouse's coordinates and in FOV
    names = [obj.name for obj in gameobjects.objects
        if obj.x == x and obj.y == y and libtcod.map_is_in_fov(gamescreen.fov_map, obj.x, obj.y)]
 
    names = ', '.join(names)  #join the names, separated by commas
    return names.capitalize()
 