import libtcodpy as libtcod
import config
import math

import gameobjects
import gamescreen
import gameactions
import gamemessages
import gamemap
import gamespells

key = libtcod.Key()
mouse = libtcod.Mouse()
game_state = 'loading'
path_recalc = True
draw_radius = 0
draw_radius_color = None
draw_radius_type = 1
slp = .01

def handle_keys():
	global mouse, key, game_state, path_recalc

	if key.vk == libtcod.KEY_ENTER and (key.lalt or key.ralt):
		#Alt+Enter: toggle fullscreen
		libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())

	elif key.vk == libtcod.KEY_ESCAPE:
		return 'exit'  #exit game

	if game_state == 'playing':
		#movement keys
		if key.vk == libtcod.KEY_UP or key.vk == libtcod.KEY_KP8:
			gameactions.player_move_or_attack(0, -1)
		elif key.vk == libtcod.KEY_DOWN or key.vk == libtcod.KEY_KP2:
			gameactions.player_move_or_attack(0, 1)
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
			path_recalc = True
			gamescreen.fov_recompute = True
			pass  #do nothing ie wait for the monster to come to you
		else:
			#test for other keys
			key_char = chr(key.c)
			
			if key_char.lower() == 'g' or key.vk == libtcod.KEY_KP0:
				#pick up an item
				grabbed = 0
				for object in gameobjects.objects:  #look for an item in the player's tile
					if object.x == gameobjects.player.x and object.y == gameobjects.player.y and object.item:
						object.item.pick_up()
						grabbed +=1
						#break
				if grabbed == 0:
					gamemessages.message('There is nothing to grab!',libtcod.dark_red)
					return 'no-turn'
				else:
					return 'grabbed'

			if key_char.lower() == 'i':
				#show the inventory; if an item is selected, use it
				chosen_item = gamescreen.inventory_menu('Press the key next to an item to use it, or any other to cancel.\n')
				if chosen_item is not None:
					chosen_item.use()

			if key_char.lower() == 'd':
				#show the inventory; if an item is selected, drop it
				chosen_item = gamescreen.inventory_menu('Press the key next to an item to drop it, or any other to cancel.\n')
				if chosen_item is not None:
					chosen_item.drop()
			if key_char.lower() == 'p':
				#show character information
				level_up_xp = config.LEVEL_UP_BASE + gameobjects.player.level * config.LEVEL_UP_FACTOR
				gamescreen.msgbox('Character Information\n\nLevel: ' + str(gameobjects.player.level) + '\nExperience: ' + str(gameobjects.player.fighter.xp) +
					   '\nExperience to level up: ' + str(level_up_xp) + '\n\nMaximum HP: ' + str(gameobjects.player.fighter.max_hp) +
					   '\nAttack: ' + str(gameobjects.player.fighter.power) + '\ndefence: ' + str(gameobjects.player.fighter.defence), 40)

			if key_char == '<':
				#go down stairs, if the player is on them
				for stair in gamemap.stairs:
					if stair.x == gameobjects.player.x and stair.y == gameobjects.player.y:
						gamemessages.message('You feel compelled to stay on the same floor as your mage!', libtcod.dark_red)
						#gameactions.next_level()
						
			if key_char == '?':
				gamescreen.help_menu()

			

			if key_char.lower() == 'z':
				#air ( yellow )
				did_turn = gameobjects.player.fighter.cast_air()
				if did_turn:
					slp = .2
					return 'cast_fire'
			if key_char.lower() == 'x':
				#spirit ( purple )
				did_turn = gameobjects.player.fighter.cast_spirit()
				if did_turn:
					slp = .2
					return 'cast_fire'
			if key_char.lower() == 'c':
				#water ( blue )
				did_turn = gameobjects.player.fighter.cast_water()
				if did_turn:
					slp = .2
					return 'cast_fire'
			if key_char.lower() == 'v':
				#fire ( red )
				did_turn = gameobjects.player.fighter.cast_fire()
				if did_turn:
					slp = .2
					return 'cast_fire'
			if key_char.lower() == 'b':
				#earth ( green )
				did_turn = gameobjects.player.fighter.cast_earth()
				if did_turn:
					slp = .2
					return 'cast_earth'
			if key_char == '`' or key_char == '~':
				if config.DEBUG_MODE:
					config.DEBUG_MODE = False
					gamemessages.message('DEBUG MODE OFF',libtcod.dark_red)
				else:
					config.DEBUG_MODE = True
					gamemessages.message('DEBUG MODE ON',libtcod.dark_red)

			if config.DEBUG_MODE:
				#cheats only allowed in debug mode
				if key_char == '1':
					gameobjects.player.fighter.add_el_power('air', 1)
				if key_char == '2':
					gameobjects.player.fighter.add_el_power('spirit', 1)
				if key_char == '3':
					gameobjects.player.fighter.add_el_power('water', 1)
				if key_char == '4':
					gameobjects.player.fighter.add_el_power('fire', 1)
				if key_char == '5':
					gameobjects.player.fighter.add_el_power('earth', 1)
				if key_char == '6':
					gameobjects.player.fighter.air = 0
					gameobjects.player.fighter.spirit = 0
					gameobjects.player.fighter.water = 0
					gameobjects.player.fighter.fire = 0
					gameobjects.player.fighter.earth = 0
				
				if key_char == '9':
					gameobjects.player.fighter.hp = 1
				if key_char == '0':
					gameobjects.mage.fighter.hp = 1
				


				if key_char == '/':
					#cheat mode!
					gameobjects.player.fighter.xp = (config.LEVEL_UP_BASE + gameobjects.player.level * config.LEVEL_UP_FACTOR) -1
					gamemessages.message('You suddenly feel VERY close to leveling... (You Big Cheater)',libtcod.dark_red)
				if key_char == '*':
					#cheat mode! superhealth
					gameobjects.player.fighter.hp=999
					gameobjects.player.fighter.base_max_hp=999
					gameobjects.player.fighter.mana=999
					gameobjects.player.fighter.base_max_mana=999
					gamemessages.message('You suddenly feel VERY healthy... (You Big Cheater)',libtcod.dark_red)
				if key_char == '-':
					#cheat mode! reveal map
					#every tile gets explored
					for y in range(config.MAP_HEIGHT):
						for x in range(config.MAP_WIDTH):
							gamemap.map[x][y].explored = True
					for object in gameobjects.objects:
						if object != gameobjects.player:
							object.always_visible = True
							object.location_seen = True
					#gamemap.map[map_x][map_y].explored = True
					gamemessages.message('The map suddenly becomes clear... (You Big Cheater)',libtcod.dark_red)
			return 'no-turn'

def get_names_under_mouse():
	global mouse
	names = []
	#return a string with the names of all objects under the mouse
	(x, y) = (mouse.cx, mouse.cy)
	(x, y) = (gamescreen.camera_x + x, gamescreen.camera_y + y)  #from screen to map coordinates
	print_y = 2
	
	#create a list with the names of all objects at the mouse's coordinates and in FOV
	for obj in gameobjects.objects:
		
		if print_y >= 6:
			libtcod.console_set_default_foreground(gamescreen.wor, libtcod.white)
			libtcod.console_print(gamescreen.wor, 1, 6, "And other items")
		
		elif obj.x == x and obj.y == y and (libtcod.map_is_in_fov(gamescreen.fov_map, obj.x, obj.y)  or (obj.always_visible and obj.location_seen)):
			libtcod.console_set_default_foreground(gamescreen.wor, obj.color)
			if obj.fighter is not None: 
				argColor = ''
				objName = obj.name
				objHealth = (float(obj.fighter.hp) / float(obj.fighter.max_hp))*100
				if objHealth == 100.0:
					objName += '(%cPerfect Health%c)'
					argColor += 'libtcod.COLCTRL_1,libtcod.COLCTRL_STOP'
				elif objHealth >= 80.0:
					objName += '(%cGood Health%c)'
					argColor += 'libtcod.COLCTRL_2,libtcod.COLCTRL_STOP'
				elif objHealth >= 60.0:
					objName += '(%cLightly Hurt%c)'
					argColor += 'libtcod.COLCTRL_3,libtcod.COLCTRL_STOP'
				elif objHealth >= 40.0:
					objName += '(%cBadly Wounded%c)'
					argColor += 'libtcod.COLCTRL_4,libtcod.COLCTRL_STOP'
				else:
					objName += '(%cAlmost Dead%c)'
					argColor += 'libtcod.COLCTRL_5,libtcod.COLCTRL_STOP'

				if isinstance(obj.ai, gameobjects.ChaseMonster):				
					if obj.ai.is_giving_chase and obj.ai.attack_target == gameobjects.player and obj.fighter.rooted==0:
						objName += '(%cAttacking You%c)'
						argColor += ',libtcod.COLCTRL_5,libtcod.COLCTRL_STOP'
					if obj.ai.is_giving_chase and obj.ai.attack_target == gameobjects.mage and obj.fighter.rooted==0:
						objName += '(%cAttacking Mage%c)'
						argColor += ',libtcod.COLCTRL_5,libtcod.COLCTRL_STOP'
					elif obj.fighter.rooted >0:
						objName += '(%cRooted!%c)'
						argColor += ',libtcod.COLCTRL_2,libtcod.COLCTRL_STOP'
					else:
						objName += '(%cIgnoring You%c)'
						argColor += ',libtcod.COLCTRL_1,libtcod.COLCTRL_STOP'
				elif isinstance(obj.ai, gameobjects.ConfusedMonster):
					objName += '(%cConfused!%c)'
					argColor += ',libtcod.COLCTRL_2,libtcod.COLCTRL_STOP'
				if config.DEBUG_MODE:
					objName += '(Dist:'+str(int(math.floor(obj.distance(gameobjects.player.x, gameobjects.player.y))))+')'
				libtcod.console_print(gamescreen.wor, 1, print_y, objName%( eval(argColor) ))
				print_y += 1
				libtcod.console_set_default_foreground(gamescreen.wor, libtcod.light_grey)
				libtcod.console_print(gamescreen.wor, 1, print_y, '  '+obj.desc)
				print_y += 1

			else:
				libtcod.console_print(gamescreen.wor, 1, print_y, obj.name)
				print_y += 1

	

	
	


def target_tile(max_range=None, radius=5, color='white'):
    #return the position of a tile left-clicked in player's FOV (optionally in a range), or (None,None) if right-clicked.
	global key, mouse, draw_radius, draw_radius_color, draw_radius_type
	while True:
		draw_radius = radius
		draw_radius_color = eval('libtcod.' + color)
		draw_radius_type = 1
		#render the screen. this erases the inventory and shows the names of objects under the mouse.
		libtcod.console_flush()
		libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS|libtcod.EVENT_MOUSE,key,mouse) 
		(x, y) = (mouse.cx, mouse.cy)
		(x, y) = (gamescreen.camera_x + x, gamescreen.camera_y + y)  #from screen to map coordinates

		gamescreen.render_all()

		if mouse.rbutton_pressed or key.vk == libtcod.KEY_ESCAPE:
			draw_radius = 0
			draw_radius_color = None
			return (None, None)  #cancel if the player right-clicked or pressed Escape

		#accept the target if the player clicked in FOV, and in case a range is specified, if it's in that range
		if (mouse.lbutton_pressed and libtcod.map_is_in_fov(gamescreen.fov_map, x, y) and
			(max_range is None or gameobjects.player.distance(x, y) <= max_range)):
			draw_radius = 0
			draw_radius_color = None
			return (x, y)
 
def target_monster(max_range=None, color='white'):
	#returns a clicked monster inside FOV up to a range, or None if right-clicked
	global key, mouse, draw_radius, draw_radius_color
	while True:
		draw_radius = 1
		draw_radius_color = eval('libtcod.' + color) 
		draw_radius_type = 1
		(x, y) = target_tile(max_range, 1, color)
		if x is None:  #player cancelled
			return None
 
		#return the first clicked monster, otherwise continue looping
		for obj in gameobjects.objects:
			if obj.x == x and obj.y == y and obj.fighter and obj != gameobjects.player:
				return obj
 
 