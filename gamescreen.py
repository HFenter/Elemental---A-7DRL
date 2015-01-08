import libtcodpy as libtcod
import time

import config

import gamemap
import gameobjects
import gamemessages
import gameinput

camera_x = 0
camera_y = 0
pentImg = None

libtcod.console_set_color_control(libtcod.COLCTRL_1,libtcod.dark_green,libtcod.black)
libtcod.console_set_color_control(libtcod.COLCTRL_2,libtcod.dark_sky,libtcod.black)
libtcod.console_set_color_control(libtcod.COLCTRL_3,libtcod.dark_yellow,libtcod.black)
libtcod.console_set_color_control(libtcod.COLCTRL_4,libtcod.dark_orange,libtcod.black)
libtcod.console_set_color_control(libtcod.COLCTRL_5,libtcod.darker_red,libtcod.black)


def help_menu():
	#alot of this code was borrowed from "kitchenmaster"
    HELP_MENU_OPTIONS = 3
    HELP_MENU_1 = "About Elemental"
    HELP_MENU_2 = "Keyboard Commands"
    HELP_MENU_3 = "Credits"
    HELP_MENU_1_PATH = 'docs/about.txt'
    HELP_MENU_2_PATH = 'docs/keys.txt'
    HELP_MENU_3_PATH = 'docs/credits.txt'
    BIG_MSG_WIDTH = config.SCREEN_WIDTH-20
    BIG_MSG_HEIGHT = config.SCREEN_HEIGHT-20
    BIG_MSG_Y = config.SCREEN_HEIGHT / 2 - (BIG_MSG_HEIGHT + 6) / 2
    BIG_MSG_X = config.SCREEN_WIDTH / 2 - (BIG_MSG_WIDTH + 4) / 2
    file_list = []
    file_list.append(HELP_MENU_1)
    file_list.append(HELP_MENU_2)
    file_list.append(HELP_MENU_3)
    choice = menu('Help Menu', file_list, 24)
    if choice != None:
        if choice == 0:
            path = HELP_MENU_1_PATH
        elif choice == 1:
            path = HELP_MENU_2_PATH
        elif choice == 2:
            path = HELP_MENU_3_PATH
        else:
            path = ''
        if path != '':
            #now you have the path
            #do everything else
            f = open(path, 'r')
            helptext= ''
            flines = f.readlines()
            for line in flines:
                helptext = helptext + line
            #going to be hacky and assume that
            #the helpfile is written with good
            #textwrap
            #create an off-screen console that represents the menu's window
            libtcod.console_set_default_background(0, libtcod.black)
            libtcod.console_clear(0)
            window = libtcod.console_new(64, 46)
            libtcod.console_set_default_background(window, libtcod.white)
            title = 'Help Menu'
            libtcod.console_set_default_background(window, libtcod.darker_blue)
            libtcod.console_rect(window, 0, 0, BIG_MSG_WIDTH + 4, 3, False)
            libtcod.console_print_ex(window, (BIG_MSG_WIDTH + 4) / 2 - len(title) / 2, 1, libtcod.BKGND_NONE, libtcod.LEFT, title)
            libtcod.console_set_default_background(window, libtcod.Color(0,0,0))
            libtcod.console_set_default_foreground(window, libtcod.white)
            #also going to assume it fits in the space >.< bad writing could sink it
            libtcod.console_print_rect_ex(window, 2, 4, BIG_MSG_WIDTH  + 2, BIG_MSG_HEIGHT, libtcod.BKGND_NONE, libtcod.LEFT, helptext)
            #blit the contents of "window" to the root console
            libtcod.console_blit(window, 0, 0, BIG_MSG_WIDTH +4, BIG_MSG_HEIGHT + 6, 0, BIG_MSG_X, BIG_MSG_Y, 1.0, 1.0)
            #present the root console to the player and wait for a key-press
            libtcod.console_flush()
            time.sleep(.1)
            key = libtcod.console_wait_for_keypress(True)

    
    pass


def menu(header, options, width):
    if len(options) > 26: raise ValueError('Cannot have a menu with more than 26 options.')
 
    #calculate total height for the header (after auto-wrap) and one line per option
    header_height = libtcod.console_get_height_rect(con, 1, 1, width, config.SCREEN_HEIGHT, header)
    if header == '':
        header_height = 1
    height = len(options) + header_height +1
 
    #create an off-screen console that represents the menu's window
    window = libtcod.console_new(width, height)
 
    #print the header, with auto-wrap
    libtcod.console_set_default_foreground(window, libtcod.white)
    libtcod.console_print_rect_ex(window, 1, 1, width, height, libtcod.BKGND_NONE, libtcod.LEFT, header)
 
    #print all the options
    y = header_height
    letter_index = ord('a')
    for option_text in options:
        text = '(' + chr(letter_index) + ') ' + option_text
        libtcod.console_print_ex(window, 1, y, libtcod.BKGND_NONE, libtcod.LEFT, text)
        y += 1
        letter_index += 1
 
    #blit the contents of "window" to the root console
    x = config.SCREEN_WIDTH/2 - width/2
    y = config.SCREEN_HEIGHT/2 - height/2
    libtcod.console_print_frame(window,0, 0, width, height, clear=False)
    libtcod.console_blit(window, 0, 0, width, height, 0, x, y, 1.0, 0.7)
 
    

    #present the root console to the player and wait for a key-press
    libtcod.console_flush()
    time.sleep(.1)
    key = libtcod.console_wait_for_keypress(True)
 
    if key.vk == libtcod.KEY_ENTER and (key.lalt or key.ralt):
		#Alt+Enter: toggle fullscreen
        libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())
 
    #convert the ASCII code to an index; if it corresponds to an option, return it
    index = key.c - ord('a')
    if index >= 0 and index < len(options): return index
    return None

def menu_confirm(text, width=35):
    #special Menu to choose an elemental school
	#width = 35
	height = 8
	#create an off-screen console that represents the menu's window
	window = libtcod.console_new(width, height)

	#print the header, with auto-wrap
	libtcod.console_set_default_foreground(window, config.color_nutr_cr)
	libtcod.console_print_rect_ex(window, 17, 1, width, height, libtcod.BKGND_NONE, libtcod.CENTER, text )
	
	libtcod.console_set_default_foreground(window, libtcod.dark_green)
	libtcod.console_print_ex(window, 17, 4, libtcod.BKGND_NONE, libtcod.CENTER, 'Press Y to Confirm')
	libtcod.console_set_default_foreground(window, libtcod.dark_red)
	libtcod.console_print_ex(window, 17, 6, libtcod.BKGND_NONE, libtcod.CENTER, 'Press Any Other Key To Cancel')
	
	#blit the contents of "window" to the root console
	x = config.SCREEN_WIDTH/2 - width/2
	y = config.SCREEN_HEIGHT/2 - height/2 - 15
	libtcod.console_print_frame(window,0, 0, width, height, clear=False)
	libtcod.console_blit(window, 0, 0, width, height, 0, x, y, 1.0, 0.95)
 
    

	#present the root console to the player and wait for a key-press
	libtcod.console_flush()
	time.sleep(.25)
	key = libtcod.console_wait_for_keypress(True)

	if key.vk == libtcod.KEY_ENTER and (key.lalt or key.ralt):
	#Alt+Enter: toggle fullscreen
		libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())

	#convert the ASCII code to an index; if it corresponds to an option, return it
	key_char = chr(key.c)
	if key_char.lower() == 'y':
		return 1
	else:
		return None

def menu_elemental():
	#special Menu to choose an elemental school
	width = 35
	height = 14
	#create an off-screen console that represents the menu's window
	window = libtcod.console_new(width, height)

	#print the header, with auto-wrap
	libtcod.console_set_default_foreground(window, config.color_nutr_cr)
	libtcod.console_print_rect_ex(window, 17, 1, width, height, libtcod.BKGND_NONE, libtcod.CENTER, 'Which Elemental Plane Connection' )
	libtcod.console_print_rect_ex(window, 17, 2, width, height, libtcod.BKGND_NONE, libtcod.CENTER, 'Would You Like To Improve' )

	libtcod.console_set_default_foreground(window, config.color_air_cr)
	libtcod.console_print_ex(window, 12, 4, libtcod.BKGND_NONE, libtcod.LEFT, 'Z - Air')
	libtcod.console_set_default_foreground(window, config.color_spirit_cr)
	libtcod.console_print_ex(window, 12, 5, libtcod.BKGND_NONE, libtcod.LEFT, 'X - Spirit')
	libtcod.console_set_default_foreground(window, config.color_water_cr)
	libtcod.console_print_ex(window, 12, 6, libtcod.BKGND_NONE, libtcod.LEFT, 'C - Water')
	libtcod.console_set_default_foreground(window, config.color_fire_cr)
	libtcod.console_print_ex(window, 12, 7, libtcod.BKGND_NONE, libtcod.LEFT, 'V - Fire')
	libtcod.console_set_default_foreground(window, config.color_earth_cr)
	libtcod.console_print_ex(window, 12, 8, libtcod.BKGND_NONE, libtcod.LEFT, 'B - Earth')
	libtcod.console_set_default_foreground(window, config.color_nutr_cr)
	libtcod.console_print_ex(window, 12, 10, libtcod.BKGND_NONE, libtcod.LEFT, 'H - Physical (HP)')
	libtcod.console_print_ex(window, 12, 11, libtcod.BKGND_NONE, libtcod.LEFT, 'M - Mental (Mana)')
    

	#blit the contents of "window" to the root console
	x = config.SCREEN_WIDTH/2 - width/2
	y = config.SCREEN_HEIGHT/2 - height/2
	libtcod.console_print_frame(window,0, 0, width, height, clear=False)
	libtcod.console_blit(window, 0, 0, width, height, 0, x, y, 1.0, 0.95)
 
    

	#present the root console to the player and wait for a key-press
	libtcod.console_flush()
	time.sleep(.25)
	key = libtcod.console_wait_for_keypress(True)

	if key.vk == libtcod.KEY_ENTER and (key.lalt or key.ralt):
	#Alt+Enter: toggle fullscreen
		libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())

	#convert the ASCII code to an index; if it corresponds to an option, return it
	key_char = chr(key.c)
	if key_char.lower() == 'z':
		return 0
	elif key_char.lower() == 'x':
		return 1
	elif key_char.lower() == 'c':
		return 2
	elif key_char.lower() == 'v':
		return 3
	elif key_char.lower() == 'b':
		return 4
	elif key_char.lower() == 'h':
		return 5
	elif key_char.lower() == 'm':
		return 6
	else:
		return None



def msgbox(text, width=50):
	menu(text, [], width)  #use menu() as a sort of "message box"

def inventory_menu(header):
    #show a menu with each item of the inventory as an option
    if len(gameobjects.inventory) == 0:
        options = ['Inventory is empty.']
    else:
        options = []
        for item in gameobjects.inventory:
            text = item.name
            options.append(text)
 
    index = menu(header, options, (config.CAMERA_WIDTH - 20))
	
    #if an item was chosen, return it
    if index is None or len(gameobjects.inventory) == 0: return None
    return gameobjects.inventory[index].item




def move_camera(target_x, target_y):
	global camera_x, camera_y
 
	#new camera coordinates (top-left corner of the screen relative to the map)
	x = target_x - config.CAMERA_WIDTH / 2  #coordinates so that the target is at the center of the screen
	y = target_y - config.CAMERA_HEIGHT / 2
 
	#make sure the camera doesn't see outside the map
	if x < 0: x = 0
	if y < 0: y = 0
	if x > config.MAP_WIDTH - config.CAMERA_WIDTH - 1: x = config.MAP_WIDTH - config.CAMERA_WIDTH - 1
	if y > config.MAP_HEIGHT - config.CAMERA_HEIGHT - 1: y = config.MAP_HEIGHT - config.CAMERA_HEIGHT - 1
 
	if x != camera_x or y != camera_y: fov_recompute = True
 
	(camera_x, camera_y) = (x, y)
 
def to_camera_coordinates(x, y):
	#convert coordinates on the map to coordinates on the screen
	(x, y) = (x - camera_x, y - camera_y)
 
	if (x < 0 or y < 0 or x >= config.CAMERA_WIDTH or y >= config.CAMERA_HEIGHT):
		return (None, None)  #if it's outside the view, return nothing
 
	return (x, y)
 
def initialize_fov():
	global fov_recompute, fov_map, fov_map_mage, fov_map_full
	fov_recompute = True
 
	#create the FOV map, according to the generated map
	fov_map = libtcod.map_new(config.MAP_WIDTH, config.MAP_HEIGHT)
	fov_map_mage = libtcod.map_new(config.MAP_WIDTH, config.MAP_HEIGHT)
	fov_map_full = libtcod.map_new(config.MAP_WIDTH, config.MAP_HEIGHT)
	for y in range(config.MAP_HEIGHT):
		for x in range(config.MAP_WIDTH):
			#player view
			libtcod.map_set_properties(fov_map, x, y, not gamemap.map[x][y].block_sight, not gamemap.map[x][y].blocked)
			#mage view
			libtcod.map_set_properties(fov_map_mage, x, y, not gamemap.map[x][y].block_sight, not gamemap.map[x][y].blocked) 
			#full view, walls transparent
			libtcod.map_set_properties(fov_map_full, x, y, True, not gamemap.map[x][y].blocked)

	libtcod.console_clear(con)  #unexplored areas start black (which is the default background color)


def render_bar(x, y, total_width, name, value, maximum, bar_color, back_color, console):
	#render a bar (HP, experience, etc). first calculate the width of the bar
	bar_width = int(float(value) / maximum * total_width)
 
	#render the background first
	libtcod.console_set_default_background(console, back_color)
	libtcod.console_rect(console, x, y, total_width, 1, False, libtcod.BKGND_SCREEN)
 
	#now render the bar on top
	libtcod.console_set_default_background(console, bar_color)
	if bar_width > 0:
		libtcod.console_rect(console, x, y, bar_width, 1, False, libtcod.BKGND_SCREEN)
 
	#finally, some centered text with the values
	libtcod.console_set_default_foreground(console, libtcod.white)
	libtcod.console_print_ex(console, x + total_width / 2, y, libtcod.BKGND_NONE, libtcod.CENTER,
		name + ': ' + str(value) + '/' + str(maximum))
 
def render_bar_school(x, y, total_width, value, maximum, bar_color, back_color, console):
	#render a bar (HP, experience, etc). first calculate the width of the bar
	bar_width = int(float(value) / maximum * total_width)
 
	#render the background first
	libtcod.console_set_default_background(console, back_color)
	libtcod.console_rect(console, x, y, total_width, 1, False, libtcod.BKGND_SCREEN)
 
	#now render the bar on top
	libtcod.console_set_default_background(console, bar_color)
	if bar_width > 0:
		libtcod.console_rect(console, x, y, bar_width, 1, False, libtcod.BKGND_SCREEN)
 

noise = libtcod.noise_new(1)
fov_torchx = 0.0
def render_all():
	global fov_map, fov_map_mage, fov_map_full, fov_recompute, pentImg
	global fov_torchx

	libtcod.console_set_color_control(libtcod.COLCTRL_1,libtcod.dark_green,libtcod.black)
	libtcod.console_set_color_control(libtcod.COLCTRL_2,libtcod.dark_sky,libtcod.black)
	libtcod.console_set_color_control(libtcod.COLCTRL_3,libtcod.dark_yellow,libtcod.black)
	libtcod.console_set_color_control(libtcod.COLCTRL_4,libtcod.dark_orange,libtcod.black)
	libtcod.console_set_color_control(libtcod.COLCTRL_5,libtcod.darker_red,libtcod.black)
	
	move_camera(gameobjects.player.x, gameobjects.player.y)

	fov_torch = True
	SQUARED_TORCH_RADIUS = config.TORCH_RADIUS * config.TORCH_RADIUS
	dx = 0.0
	dy = 0.0
	di = 0.0
	tilecolor = None
 
	if fov_recompute:
		#recompute FOV if needed (the player moved or something)
		fov_recompute = False
		libtcod.map_compute_fov(fov_map, gameobjects.player.x, gameobjects.player.y, config.TORCH_RADIUS, config.FOV_LIGHT_WALLS, config.FOV_ALGO)

		libtcod.map_compute_fov(fov_map_mage, gameobjects.mage.x, gameobjects.mage.y, gameobjects.mage.ai.chase_range, config.FOV_LIGHT_WALLS, config.FOV_ALGO)

		libtcod.console_clear(con)
		
	if fov_torch:
		#get torch color based on active effects (elemental primary school)
		color = gameobjects.player.fighter.find_greatest_power()
		config.color_torch = eval('config.color_'+color+'_lt')
		gameobjects.player.color = eval('config.color_'+color+'_cr')
		# slightly change the perlin noise parameter
		fov_torchx += 0.05
		# randomize the light position between -1.5 and 1.5
		tdx = [fov_torchx + 20.0]
		dx = libtcod.noise_get(noise, tdx, libtcod.NOISE_SIMPLEX) * 1.01

		tdx[0] += 30.0
		dy = libtcod.noise_get(noise, tdx, libtcod.NOISE_SIMPLEX) * 1.01
		di = 0.2 * libtcod.noise_get(noise, [fov_torchx], libtcod.NOISE_SIMPLEX)

	#go through all tiles, and set their background color according to the FOV
	for y in range(config.CAMERA_HEIGHT):
		for x in range(config.CAMERA_WIDTH):
			(map_x, map_y) = (camera_x + x, camera_y + y)
			visible = libtcod.map_is_in_fov(fov_map, map_x, map_y)

			wall = gamemap.map[map_x][map_y].block_sight
			if not visible:
				#if it's not visible right now, the player can only see it if it's explored
				if gamemap.map[map_x][map_y].explored:
					if wall:
						tilecolor = libtcod.color_lerp( config.color_dark_wall, gamemap.map[map_x][map_y].color, .1 )
						libtcod.console_put_char_ex(con, x, y, gamemap.map[map_x][map_y].tile, tilecolor, config.color_dark_wall)
						#libtcod.console_set_char_background(con, x, y, config.color_dark_wall, libtcod.BKGND_SET)
					else:
						tilecolor = libtcod.color_lerp( config.color_dark_ground, gamemap.map[map_x][map_y].color, .1 )
						libtcod.console_put_char_ex(con, x, y, gamemap.map[map_x][map_y].tile, tilecolor, config.color_dark_ground)
						#libtcod.console_set_char_background(con, x, y, config.color_dark_ground, libtcod.BKGND_SET)
			else:
				#it's visible
				if wall:
					#libtcod.console_put_char_ex(con, x, y, 219, libtcod.white, config.color_light_wall)
					base = config.color_dark_wall
					light = config.color_torch
					# cell distance to torch (squared)
					r = float(camera_x + x - gameobjects.player.x + dx) * (camera_x + x - gameobjects.player.x + dx) + (camera_y + y - gameobjects.player.y + dy) * (camera_y + y - gameobjects.player.y + dy)
					if r < SQUARED_TORCH_RADIUS:
						l = ((SQUARED_TORCH_RADIUS - r) / SQUARED_TORCH_RADIUS + di)/2
						if l  < 0.0:
							l = 0.0
						elif l> 0.5:
							l = 0.5
						base = libtcod.color_lerp(base, light, l)
						tilecolor = libtcod.color_lerp( light, gamemap.map[map_x][map_y].color, .75 )
					libtcod.console_put_char_ex(con, x, y, gamemap.map[map_x][map_y].tile, tilecolor, base)
					if gameinput.draw_radius > 0:
						sqr_radius = gameinput.draw_radius * gameinput.draw_radius
						if gameinput.draw_radius_type == 1:
							r = float(x - gameinput.mouse.cx) * (x - gameinput.mouse.cx) + (y - gameinput.mouse.cy) * (y - gameinput.mouse.cy)
						if gameinput.draw_radius_type == 2:
							r = float(camera_x + x - gameobjects.player.x) * (camera_x + x - gameobjects.player.x) + (camera_y + y - gameobjects.player.y) * (camera_y + y - gameobjects.player.y)
							
						if r < sqr_radius:
							l = ((sqr_radius - r) / sqr_radius)/2
							if l  < 0.0:
								l = 0.0
							elif l> 0.5:
								l = 0.5
							base = libtcod.color_lerp(base, libtcod.darker_red, l)
							tilecolor = libtcod.color_lerp( libtcod.darker_red, gamemap.map[map_x][map_y].color, .75 )
							libtcod.console_put_char_ex(con, x, y, '#', tilecolor, base)
					
				else:
					base = config.color_dark_ground
					light = config.color_torch
					# cell distance to torch (squared)
					r = float(camera_x + x - gameobjects.player.x + dx) * (camera_x + x - gameobjects.player.x + dx) + (camera_y + y - gameobjects.player.y + dy) * (camera_y + y - gameobjects.player.y + dy)
					if r < SQUARED_TORCH_RADIUS:
						l = ((SQUARED_TORCH_RADIUS - r) / SQUARED_TORCH_RADIUS + di)/1.5
						if l  < 0.0:
							l = 0.0
						elif l> 0.75:
							l = 0.75
						base = libtcod.color_lerp(base, light, l)
						tilecolor = libtcod.color_lerp( light, gamemap.map[map_x][map_y].color, .75 )
					libtcod.console_put_char_ex(con, x, y, gamemap.map[map_x][map_y].tile, tilecolor, base)
					if gameinput.draw_radius > 0:
						sqr_radius = gameinput.draw_radius * gameinput.draw_radius
						if gameinput.draw_radius_type == 1:
							r = float(x - gameinput.mouse.cx) * (x - gameinput.mouse.cx) + (y - gameinput.mouse.cy) * (y - gameinput.mouse.cy)
						if gameinput.draw_radius_type == 2:
							r = float(camera_x + x - gameobjects.player.x) * (camera_x + x - gameobjects.player.x) + (camera_y + y - gameobjects.player.y) * (camera_y + y - gameobjects.player.y)
						if r < sqr_radius:
							l = ((sqr_radius - r) / sqr_radius)/2
							if l  < 0.0:
								l = 0.0
							elif l> 0.5:
								l = 0.5
							base = libtcod.color_lerp(base, gameinput.draw_radius_color, l)
							tilecolor = libtcod.color_lerp( libtcod.darker_red, gamemap.map[map_x][map_y].color, .75 )
							libtcod.console_put_char_ex(con, x, y, '#', tilecolor, base)
					
				



				#since it's visible, explore it
				gamemap.map[map_x][map_y].explored = True
 
	#draw all objects in the list, except the player. we want it to
	#always appear over all other objects! so it's drawn later.
	for object in gameobjects.objects:
		if object != gameobjects.player:
			object.draw()
	gameobjects.player.draw()

	#blit the contents of "con" to the root console
	libtcod.console_blit(con, 0, 0, config.MAP_WIDTH, config.MAP_HEIGHT, 0, 0, 0)

	#########################################
	# 	Message Panel						#
	#########################################
	libtcod.console_set_default_background(mes, libtcod.black)
	libtcod.console_clear(mes)
 	#print the game messages, one line at a time
	y = 1
	for (line, color) in gamemessages.game_msgs:
		libtcod.console_set_default_foreground(mes, color)
		libtcod.console_print_ex(mes, 2, y, libtcod.BKGND_NONE, libtcod.LEFT, line)
		y += 1
	libtcod.console_set_default_foreground(mes, libtcod.white)
	libtcod.console_print_frame(mes,0, 0, config.SCREEN_WIDTH, config.MESSAGE_BAR_HEIGHT, clear=False)
	libtcod.console_blit(mes, 0, 0, config.SCREEN_WIDTH, config.MESSAGE_BAR_HEIGHT, 0, 0, (config.SCREEN_HEIGHT - config.MESSAGE_BAR_HEIGHT))

	#########################################
	# 	World Info Panel					#
	#########################################
	libtcod.console_set_default_background(wor, libtcod.black)
	libtcod.console_clear(wor)
 	libtcod.console_set_default_foreground(wor, libtcod.blue)
	libtcod.console_print_ex(wor, 1, 1, libtcod.BKGND_NONE, libtcod.LEFT, 'World Info')
	if config.DEBUG_MODE:
		libtcod.console_set_default_foreground(wor, libtcod.darker_red)
		libtcod.console_print_ex(wor, config.INFO_BAR_WIDTH-2, 2, libtcod.BKGND_NONE, libtcod.RIGHT, 'Mouse Loc:'+str(gameinput.mouse.cx+camera_x)+':'+str(gameinput.mouse.cy+camera_y))
	#display names of objects under the mouse
	libtcod.console_set_default_foreground(wor, libtcod.white)
	gameinput.get_names_under_mouse()
	
	libtcod.console_set_default_foreground(wor, libtcod.dark_amber)
	libtcod.console_print_ex(wor, config.INFO_BAR_WIDTH-2, 1, libtcod.BKGND_NONE, libtcod.RIGHT, 'Dungeon Level ' + str(gamemap.dungeon_level))
	
	libtcod.console_set_default_foreground(wor, libtcod.white)
	libtcod.console_print_frame(wor,0, 0, config.INFO_BAR_WIDTH, 8, clear=False)
	libtcod.console_blit(wor, 0, 0, config.INFO_BAR_WIDTH, 8, 0, config.CAMERA_WIDTH, 0)

	#########################################
	# 	Elemental Info Panel				#
	#########################################
	libtcod.console_set_default_background(elm, libtcod.black)
	libtcod.console_clear(elm)

	if pentImg is None:
		pentImg = libtcod.image_load('ElementalStarTiny.png')
		libtcod.image_set_key_color(pentImg,libtcod.black)
	x = 16
	y = 5
	libtcod.image_blit_2x(pentImg, elm, x, y)

 	libtcod.console_set_default_foreground(elm, libtcod.blue)
	libtcod.console_print_ex(elm, 1, 1, libtcod.BKGND_NONE, libtcod.LEFT, 'Elemental Panel')

	libtcod.console_set_default_foreground(elm, gameobjects.player.color)
	libtcod.console_print_ex(elm, 1, 2, libtcod.BKGND_NONE, libtcod.LEFT, gameobjects.player.name)

	#show the player's stats
	libtcod.console_set_default_foreground(elm, libtcod.dark_blue)
	objHealth = (float(gameobjects.player.fighter.hp) / float(gameobjects.player.fighter.max_hp))*100
	if objHealth == 100.0:
		libtcod.console_print_ex(elm, config.INFO_BAR_WIDTH-2, 1, libtcod.BKGND_NONE, libtcod.RIGHT, '%cPerfect Health%c'%( libtcod.COLCTRL_1,libtcod.COLCTRL_STOP ))
	elif objHealth >= 80.0:
		libtcod.console_print_ex(elm, config.INFO_BAR_WIDTH-2, 1, libtcod.BKGND_NONE, libtcod.RIGHT, '(%cGood Health%c)'%( libtcod.COLCTRL_2,libtcod.COLCTRL_STOP ))
	elif objHealth >= 60.0:
		libtcod.console_print_ex(elm, config.INFO_BAR_WIDTH-2, 1, libtcod.BKGND_NONE, libtcod.RIGHT, '((%cLightly Hurt%c))'%( libtcod.COLCTRL_3,libtcod.COLCTRL_STOP ))
	elif objHealth >= 40.0:
		libtcod.console_print_ex(elm, config.INFO_BAR_WIDTH-2, 1, libtcod.BKGND_NONE, libtcod.RIGHT, '(((%cBadly Wounded%c)))'%( libtcod.COLCTRL_4,libtcod.COLCTRL_STOP ))
	elif gameobjects.player.fighter.hp > 0:
		libtcod.console_print_ex(elm, config.INFO_BAR_WIDTH-2, 1, libtcod.BKGND_NONE, libtcod.RIGHT, '((((%cAlmost Dead%c))))'%( libtcod.COLCTRL_5,libtcod.COLCTRL_STOP ))
	else:
		libtcod.console_print_ex(elm, config.INFO_BAR_WIDTH-2, 1, libtcod.BKGND_NONE, libtcod.RIGHT, 'XXX%cDead%cXXX'%( libtcod.COLCTRL_5,libtcod.COLCTRL_STOP ))

	objMana = (float(gameobjects.player.fighter.mana) / float(gameobjects.player.fighter.max_mana))*100
	if objMana == 100.0:
		libtcod.console_print_ex(elm, config.INFO_BAR_WIDTH-2, 2, libtcod.BKGND_NONE, libtcod.RIGHT, '%cFully Connected%c'%( libtcod.COLCTRL_1,libtcod.COLCTRL_STOP ))
	elif objMana >= 80.0:
		libtcod.console_print_ex(elm, config.INFO_BAR_WIDTH-2, 2, libtcod.BKGND_NONE, libtcod.RIGHT, '(%cWell Connected%c)'%( libtcod.COLCTRL_2,libtcod.COLCTRL_STOP ))
	elif objMana >= 60.0:
		libtcod.console_print_ex(elm, config.INFO_BAR_WIDTH-2, 2, libtcod.BKGND_NONE, libtcod.RIGHT, '((%cLightly Connected%c))'%( libtcod.COLCTRL_3,libtcod.COLCTRL_STOP ))
	elif objMana >= 40.0:
		libtcod.console_print_ex(elm, config.INFO_BAR_WIDTH-2, 2, libtcod.BKGND_NONE, libtcod.RIGHT, '(((%cBadly Connected%c)))'%( libtcod.COLCTRL_4,libtcod.COLCTRL_STOP ))
	elif gameobjects.player.fighter.mana > 0:
		libtcod.console_print_ex(elm, config.INFO_BAR_WIDTH-2, 2, libtcod.BKGND_NONE, libtcod.RIGHT, '((((%cDistant Connection%c))))'%( libtcod.COLCTRL_5,libtcod.COLCTRL_STOP ))
	else:
		libtcod.console_print_ex(elm, config.INFO_BAR_WIDTH-2, 2, libtcod.BKGND_NONE, libtcod.RIGHT, '(((((%cNo Connection%c)))))'%( libtcod.COLCTRL_5,libtcod.COLCTRL_STOP ))



	# Current Level
	libtcod.console_set_default_foreground(elm, libtcod.dark_amber)
	libtcod.console_print_ex(elm, config.INFO_BAR_WIDTH-2, 3, libtcod.BKGND_NONE, libtcod.RIGHT, 'Level ' + str(gameobjects.player.level))

	school_width = 12
	school_spacing = 5#(((config.CAMERA_WIDTH / 5) - 10)/2)
	school_first_y = 7

	libtcod.console_set_default_foreground(elm, config.color_air_lt)
	libtcod.console_print_ex(elm, 2, school_first_y-1, libtcod.BKGND_NONE, libtcod.LEFT, 'Z - Air')
	render_bar_school(2, school_first_y, school_width, gameobjects.player.fighter.air, gameobjects.player.fighter.el_power, config.color_air_lt, libtcod.darker_yellow, elm)
	libtcod.console_print_ex(elm, 3, school_first_y+1, libtcod.BKGND_NONE, libtcod.LEFT, gameobjects.player.fighter.air_spell)

	
	libtcod.console_set_default_foreground(elm, config.color_spirit_lt)
	libtcod.console_print_ex(elm, 2, school_first_y+(school_spacing*1)-1, libtcod.BKGND_NONE, libtcod.LEFT, 'X - Spirit')
	render_bar_school(2, school_first_y+(school_spacing*1), school_width, gameobjects.player.fighter.spirit, gameobjects.player.fighter.el_power, config.color_spirit_cr, libtcod.darker_purple, elm)
	libtcod.console_print_ex(elm, 3,  school_first_y+(school_spacing*1)+1, libtcod.BKGND_NONE, libtcod.LEFT, gameobjects.player.fighter.spirit_spell)

	libtcod.console_set_default_foreground(elm, config.color_water_lt)
	libtcod.console_print_ex(elm, 2, school_first_y+(school_spacing*2)-1, libtcod.BKGND_NONE, libtcod.LEFT, 'C - Water')
	render_bar_school(2, school_first_y+(school_spacing*2), school_width, gameobjects.player.fighter.water, gameobjects.player.fighter.el_power, config.color_water_cr, libtcod.darker_blue, elm)
	libtcod.console_print_ex(elm, 3,  school_first_y+(school_spacing*2)+1, libtcod.BKGND_NONE, libtcod.LEFT, gameobjects.player.fighter.water_spell)

	libtcod.console_set_default_foreground(elm, config.color_fire_lt)
	libtcod.console_print_ex(elm, 2, school_first_y+(school_spacing*3)-1, libtcod.BKGND_NONE, libtcod.LEFT, 'V - Fire')
	render_bar_school(2, school_first_y+(school_spacing*3), school_width, gameobjects.player.fighter.fire, gameobjects.player.fighter.el_power, config.color_fire_cr, libtcod.darker_red, elm)
	libtcod.console_print_ex(elm, 3,  school_first_y+(school_spacing*3)+1, libtcod.BKGND_NONE, libtcod.LEFT, gameobjects.player.fighter.fire_spell)

	libtcod.console_set_default_foreground(elm, config.color_earth_lt)
	libtcod.console_print_ex(elm, 2, school_first_y+(school_spacing*4)-1, libtcod.BKGND_NONE, libtcod.LEFT, 'B - Earth')
	render_bar_school(2, school_first_y+(school_spacing*4), school_width, gameobjects.player.fighter.earth, gameobjects.player.fighter.el_power, config.color_earth_cr, libtcod.darker_green, elm)
	libtcod.console_print_ex(elm, 3,  school_first_y+(school_spacing*4)+1, libtcod.BKGND_NONE, libtcod.LEFT, gameobjects.player.fighter.earth_spell)
	
	if config.DEBUG_MODE:
		# Debug Player X, Y cords
		libtcod.console_set_default_foreground(elm, libtcod.darkest_red)
		libtcod.console_print_ex(elm, config.INFO_BAR_WIDTH-2, config.CAMERA_HEIGHT - 24, libtcod.BKGND_NONE, libtcod.RIGHT, 'DEBUG:')
		libtcod.console_print_ex(elm, config.INFO_BAR_WIDTH-2, config.CAMERA_HEIGHT - 23, libtcod.BKGND_NONE, libtcod.RIGHT, 'Player Health: ' + str(gameobjects.player.fighter.hp)+' : ' + str(gameobjects.player.fighter.max_hp))
		libtcod.console_print_ex(elm, config.INFO_BAR_WIDTH-2, config.CAMERA_HEIGHT - 22, libtcod.BKGND_NONE, libtcod.RIGHT, 'Player Mana: ' + str(gameobjects.player.fighter.mana)+' : ' + str(gameobjects.player.fighter.max_mana))
		libtcod.console_print_ex(elm, config.INFO_BAR_WIDTH-2, config.CAMERA_HEIGHT - 21, libtcod.BKGND_NONE, libtcod.RIGHT, 'Player XP: ' + str(gameobjects.player.fighter.xp))
		libtcod.console_print_ex(elm, config.INFO_BAR_WIDTH-2, config.CAMERA_HEIGHT - 20, libtcod.BKGND_NONE, libtcod.RIGHT, 'Player Loc: ' + str(gameobjects.player.x)+':' + str(gameobjects.player.y))
		
		libtcod.console_set_default_foreground(elm, config.color_air_lt)
		libtcod.console_print_ex(elm, 14, 7, libtcod.BKGND_NONE, libtcod.RIGHT, str(gameobjects.player.fighter.air))
		libtcod.console_set_default_foreground(elm, config.color_spirit_lt)
		libtcod.console_print_ex(elm, 14, 12, libtcod.BKGND_NONE, libtcod.RIGHT, str(gameobjects.player.fighter.spirit))
		libtcod.console_set_default_foreground(elm, config.color_water_lt)
		libtcod.console_print_ex(elm, 14, 17, libtcod.BKGND_NONE, libtcod.RIGHT, str(gameobjects.player.fighter.water))
		libtcod.console_set_default_foreground(elm, config.color_fire_lt)
		libtcod.console_print_ex(elm, 14, 22, libtcod.BKGND_NONE, libtcod.RIGHT, str(gameobjects.player.fighter.fire))
		libtcod.console_set_default_foreground(elm, config.color_earth_lt)
		libtcod.console_print_ex(elm, 14, 27, libtcod.BKGND_NONE, libtcod.RIGHT, str(gameobjects.player.fighter.earth))




	#star cords 16,5 - 40,29
	gameobjects.player.fighter.place_star()
	

	libtcod.console_set_default_foreground(elm, libtcod.white)

	libtcod.console_print_frame(elm,0, 0, config.INFO_BAR_WIDTH, config.CAMERA_HEIGHT - 18, clear=False)
	libtcod.console_blit(elm, 0, 0, config.INFO_BAR_WIDTH, config.CAMERA_HEIGHT - 18, 0, config.CAMERA_WIDTH, 8)

	#########################################
	# 	Mage Info Panel				#
	#########################################
	libtcod.console_set_default_background(mag, libtcod.black)
	libtcod.console_clear(mag)
 	libtcod.console_set_default_foreground(mag, libtcod.green)
	libtcod.console_print_ex(mag, 1, 1, libtcod.BKGND_NONE, libtcod.LEFT, 'Mage Panel')
	libtcod.console_set_default_foreground(mag, gameobjects.mage.color)
	libtcod.console_print_ex(mag, 1, 2, libtcod.BKGND_NONE, libtcod.LEFT, gameobjects.mage.name)
	
	#show the mage's stats
	libtcod.console_set_default_foreground(mag, libtcod.dark_blue)
	objHealth = (float(gameobjects.mage.fighter.hp) / float(gameobjects.mage.fighter.max_hp))*100
	if objHealth == 100.0:
		libtcod.console_print_ex(mag, config.INFO_BAR_WIDTH-2, 1, libtcod.BKGND_NONE, libtcod.RIGHT, '%cPerfect Health%c'%( libtcod.COLCTRL_1,libtcod.COLCTRL_STOP ))
	elif objHealth >= 80.0:
		libtcod.console_print_ex(mag, config.INFO_BAR_WIDTH-2, 1, libtcod.BKGND_NONE, libtcod.RIGHT, '(%cGood Health%c)'%( libtcod.COLCTRL_2,libtcod.COLCTRL_STOP ))
	elif objHealth >= 60.0:
		libtcod.console_print_ex(mag, config.INFO_BAR_WIDTH-2, 1, libtcod.BKGND_NONE, libtcod.RIGHT, '((%cLightly Hurt%c))'%( libtcod.COLCTRL_3,libtcod.COLCTRL_STOP ))
	elif objHealth >= 40.0:
		libtcod.console_print_ex(mag, config.INFO_BAR_WIDTH-2, 1, libtcod.BKGND_NONE, libtcod.RIGHT, '(((%cBadly Wounded%c)))'%( libtcod.COLCTRL_4,libtcod.COLCTRL_STOP ))
	elif objHealth > 0:
		libtcod.console_print_ex(mag, config.INFO_BAR_WIDTH-2, 1, libtcod.BKGND_NONE, libtcod.RIGHT, '((((%cAlmost Dead%c))))'%( libtcod.COLCTRL_5,libtcod.COLCTRL_STOP ))
	else:
		libtcod.console_print_ex(mag, config.INFO_BAR_WIDTH-2, 1, libtcod.BKGND_NONE, libtcod.RIGHT, 'XXX%cDead%cXXX'%( libtcod.COLCTRL_5,libtcod.COLCTRL_STOP ))

	objMana = (float(gameobjects.mage.fighter.mana) / float(gameobjects.mage.fighter.max_mana))*100
	if objMana == 100.0:
		libtcod.console_print_ex(mag, config.INFO_BAR_WIDTH-2, 2, libtcod.BKGND_NONE, libtcod.RIGHT, '%cFull Mana%c'%( libtcod.COLCTRL_1,libtcod.COLCTRL_STOP ))
	elif objMana >= 80.0:
		libtcod.console_print_ex(mag, config.INFO_BAR_WIDTH-2, 2, libtcod.BKGND_NONE, libtcod.RIGHT, '(%cGood Mana%c)'%( libtcod.COLCTRL_2,libtcod.COLCTRL_STOP ))
	elif objMana >= 60.0:
		libtcod.console_print_ex(mag, config.INFO_BAR_WIDTH-2, 2, libtcod.BKGND_NONE, libtcod.RIGHT, '((%cSome Mana%c))'%( libtcod.COLCTRL_3,libtcod.COLCTRL_STOP ))
	elif objMana >= 40.0:
		libtcod.console_print_ex(mag, config.INFO_BAR_WIDTH-2, 2, libtcod.BKGND_NONE, libtcod.RIGHT, '(((%cLow Mana%c)))'%( libtcod.COLCTRL_4,libtcod.COLCTRL_STOP ))
	elif objMana > 0:
		libtcod.console_print_ex(mag, config.INFO_BAR_WIDTH-2, 2, libtcod.BKGND_NONE, libtcod.RIGHT, '((((%cAlmost No Mana%c))))'%( libtcod.COLCTRL_5,libtcod.COLCTRL_STOP ))
	else:
		libtcod.console_print_ex(mag, config.INFO_BAR_WIDTH-2, 2, libtcod.BKGND_NONE, libtcod.RIGHT, '(((((%cNo Mana%c)))))'%( libtcod.COLCTRL_5,libtcod.COLCTRL_STOP ))



	# Current Level
	libtcod.console_set_default_foreground(mag, libtcod.dark_amber)
	libtcod.console_print_ex(mag, config.INFO_BAR_WIDTH-2, 3, libtcod.BKGND_NONE, libtcod.RIGHT, 'Level ' + str(gameobjects.mage.level))


	text_height = libtcod.console_get_height_rect(mag, 2, 3, config.INFO_BAR_WIDTH-15, config.SCREEN_HEIGHT-22, gameobjects.mage.ai.mage_thoughts)
	libtcod.console_print_rect_ex(mag, 2, 3, config.INFO_BAR_WIDTH-15, text_height, libtcod.BKGND_NONE, libtcod.LEFT, gameobjects.mage.ai.mage_thoughts)

	if config.DEBUG_MODE:
		# Current Target
		libtcod.console_set_default_foreground(mag, libtcod.dark_red)
		if gameobjects.mage.ai.cur_target is not None:
			libtcod.console_print_ex(mag, 25, 1, libtcod.BKGND_NONE, libtcod.RIGHT, 'Target: ' + str(gameobjects.mage.ai.cur_target.x)+':'+ str(gameobjects.mage.ai.cur_target.x))
		libtcod.console_print_ex(mag, 25, 2, libtcod.BKGND_NONE, libtcod.RIGHT, 'Explore:'+ str(gameobjects.mage.ai.mage_min_moves_floor))
		

	libtcod.console_set_default_foreground(mag, libtcod.white)
	libtcod.console_print_frame(mag,0, 0, config.INFO_BAR_WIDTH, 10, clear=False)
	libtcod.console_blit(mag, 0, 0, config.INFO_BAR_WIDTH, 10, 0, config.CAMERA_WIDTH, config.CAMERA_HEIGHT-10)





def main_init():
    #initialise main items
	if config.FONT_GREYSCALE:
		libtcod.console_set_custom_font(config.CUSTOM_FONT, 4 | config.FONT_LAYOUT )
	else:
		libtcod.console_set_custom_font(config.CUSTOM_FONT, config.FONT_LAYOUT)
	
	
	libtcod.console_init_root(config.SCREEN_WIDTH, config.SCREEN_HEIGHT, 'Elemental', False, libtcod.RENDERER_SDL)
	libtcod.sys_set_fps(config.LIMIT_FPS)
	libtcod.console_set_fullscreen(config.FULLSCREEN)


def game_screen_init():
	global con, mes, elm, mag, wor
	#initialise game screens
	con = libtcod.console_new(config.MAP_WIDTH, config.MAP_HEIGHT) #main viewport - Top Left
	mes = libtcod.console_new(config.SCREEN_WIDTH, config.MESSAGE_BAR_HEIGHT) #Message bar - Bottom
	wor = libtcod.console_new(config.INFO_BAR_WIDTH, 8 ) #World Info - Right Top
	elm = libtcod.console_new(config.INFO_BAR_WIDTH, config.CAMERA_HEIGHT - 14) #Elemental Info (you) - Right Top
	mag = libtcod.console_new(config.INFO_BAR_WIDTH, 18) #Mage Info - Right Bottom


