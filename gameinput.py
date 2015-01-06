import libtcodpy as libtcod
import config

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

def handle_keys():
	global mouse, key, game_state

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
			pass  #do nothing ie wait for the monster to come to you
		else:
			#test for other keys
			key_char = chr(key.c)
			
			if key_char == 'g' or key.vk == libtcod.KEY_KP0:
				#pick up an item
				grabbed = 0
				for object in gameobjects.objects:  #look for an item in the player's tile
					if object.x == gameobjects.player.x and object.y == gameobjects.player.y and object.item:
						object.item.pick_up()
						grabbed +=1
						#break
				if grabbed == 0:
					gamemessages.message('There is nothing to grab!',libtcod.dark_red)

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
			if key_char == 'p':
				#show character information
				level_up_xp = config.LEVEL_UP_BASE + gameobjects.player.level * config.LEVEL_UP_FACTOR
				gamescreen.msgbox('Character Information\n\nLevel: ' + str(gameobjects.player.level) + '\nExperience: ' + str(gameobjects.player.fighter.xp) +
					   '\nExperience to level up: ' + str(level_up_xp) + '\n\nMaximum HP: ' + str(gameobjects.player.fighter.max_hp) +
					   '\nAttack: ' + str(gameobjects.player.fighter.power) + '\ndefence: ' + str(gameobjects.player.fighter.defence), 40)

			if key_char == '<':
				#go down stairs, if the player is on them
				for stair in gamemap.stairs:
					if stair.x == gameobjects.player.x and stair.y == gameobjects.player.y:
						gameactions.next_level()
			if key_char == '?':
				gamescreen.help_menu()

			if key_char == 'z':
				#air ( yellow )
				#config.color_torch = libtcod.Color(228, 189, 73)
				#gameobjects.player.color = libtcod.Color(200, 190, 5)
				gameobjects.player.fighter.add_el_power('air', 1)
				gameobjects.player.fighter.find_greatest_power()
			if key_char == 'x':
				#spirit ( purple )
				#config.color_torch = libtcod.Color(171, 127, 182)
				#gameobjects.player.color = libtcod.Color(190, 45, 210)
				gameobjects.player.fighter.add_el_power('spirit', 1)
			if key_char == 'c':
				#water ( blue )
				#config.color_torch = libtcod.Color(118, 171, 224)
				#gameobjects.player.color = libtcod.Color(30, 30, 255)
				gameobjects.player.fighter.add_el_power('water', 1)
			if key_char == 'v':
				#fire ( red )
				#config.color_torch = libtcod.Color(231, 113, 115)
				#gameobjects.player.color = libtcod.Color(255, 30, 30)
				gameobjects.player.fighter.add_el_power('fire', 1)
			if key_char == 'b':
				#earth ( green )
				#config.color_torch = libtcod.Color(127, 210, 41)
				#gameobjects.player.color = libtcod.Color(30, 255, 30)
				gameobjects.player.fighter.add_el_power('earth', 1)
			if key_char == 'n':
				config.color_torch = libtcod.Color(200, 200, 200)
				gameobjects.player.color = libtcod.Color(250, 250, 250)
				gameobjects.player.fighter.air = 0
				gameobjects.player.fighter.spirit = 0
				gameobjects.player.fighter.water = 0
				gameobjects.player.fighter.fire = 0
				gameobjects.player.fighter.earth = 0
				

			if key_char == '~':
				#cheat mode!
				gameobjects.player.fighter.xp = (config.LEVEL_UP_BASE + gameobjects.player.level * config.LEVEL_UP_FACTOR) -1
				gamemessages.message('You suddenly feel VERY close to leveling... (You Big Cheater)',libtcod.dark_red)
			if key_char == '*':
				#cheat mode! confuse
				gamespells.cast_confuse(power1=10, power2=20, power3=0)
			if key_char == '/':
				#cheat mode! superhealth
				gameobjects.player.fighter.hp=999
				gameobjects.player.fighter.base_max_hp=999
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
			libtcod.console_print(gamescreen.wor, 1, 6, "And other items")
		
		elif obj.x == x and obj.y == y and (libtcod.map_is_in_fov(gamescreen.fov_map, obj.x, obj.y)  or (obj.always_visible and obj.location_seen)):
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
					if obj.ai.is_giving_chase:
						objName += '(%cAttacking You%c)'
						argColor += ',libtcod.COLCTRL_5,libtcod.COLCTRL_STOP'
					else:
						objName += '(%cIgnoring You%c)'
						argColor += ',libtcod.COLCTRL_1,libtcod.COLCTRL_STOP'
				libtcod.console_print(gamescreen.wor, 1, print_y, objName%( eval(argColor) ))
				print_y += 1
			else:
				libtcod.console_print(gamescreen.wor, 1, print_y, obj.name)
				print_y += 1

	

	
	


def target_tile(max_range=None):
    #return the position of a tile left-clicked in player's FOV (optionally in a range), or (None,None) if right-clicked.
    global key, mouse
    while True:
        #render the screen. this erases the inventory and shows the names of objects under the mouse.
        libtcod.console_flush()
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS|libtcod.EVENT_MOUSE,key,mouse) 
        gamescreen.render_all()
        (x, y) = (mouse.cx, mouse.cy)
        (x, y) = (gamescreen.camera_x + x, gamescreen.camera_y + y)  #from screen to map coordinates
 
        if mouse.rbutton_pressed or key.vk == libtcod.KEY_ESCAPE:
            return (None, None)  #cancel if the player right-clicked or pressed Escape
 
        #accept the target if the player clicked in FOV, and in case a range is specified, if it's in that range
        if (mouse.lbutton_pressed and libtcod.map_is_in_fov(gamescreen.fov_map, x, y) and
			(max_range is None or gameobjects.player.distance(x, y) <= max_range)):
            return (x, y)
 
def target_monster(max_range=None):
	#returns a clicked monster inside FOV up to a range, or None if right-clicked
	while True:
		(x, y) = target_tile(max_range)
		if x is None:  #player cancelled
			return None
 
		#return the first clicked monster, otherwise continue looping
		for obj in gameobjects.objects:
			if obj.x == x and obj.y == y and obj.fighter and obj != gameobjects.player:
				return obj
 
 