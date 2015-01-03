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
 
    if key.vk == libtcod.KEY_ENTER and (key.lalt or key.ralt):  #(special case) Alt+Enter: toggle fullscreen
        libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen)
 
    #convert the ASCII code to an index; if it corresponds to an option, return it
    index = key.c - ord('a')
    if index >= 0 and index < len(options): return index
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
	global fov_recompute, fov_map
	fov_recompute = True
 
	#create the FOV map, according to the generated map
	fov_map = libtcod.map_new(config.MAP_WIDTH, config.MAP_HEIGHT)
	for y in range(config.MAP_HEIGHT):
		for x in range(config.MAP_WIDTH):
			libtcod.map_set_properties(fov_map, x, y, not gamemap.map[x][y].blocked, not gamemap.map[x][y].block_sight)
 
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
 


def render_all():
	global fov_map, fov_recompute, pentImg

	move_camera(gameobjects.player.x, gameobjects.player.y)
 
	if fov_recompute:
		#recompute FOV if needed (the player moved or something)
		fov_recompute = False
		libtcod.map_compute_fov(fov_map, gameobjects.player.x, gameobjects.player.y, config.TORCH_RADIUS, config.FOV_LIGHT_WALLS, config.FOV_ALGO)
		libtcod.console_clear(con)
 
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
							libtcod.console_set_char_background(con, x, y, config.color_dark_wall, libtcod.BKGND_SET)
						else:
							libtcod.console_set_char_background(con, x, y, config.color_dark_ground, libtcod.BKGND_SET)
				else:
					#it's visible
					if wall:
						libtcod.console_set_char_background(con, x, y, config.color_light_wall, libtcod.BKGND_SET )
					else:
						libtcod.console_set_char_background(con, x, y, config.color_light_ground, libtcod.BKGND_SET )
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

	#display names of objects under the mouse
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

	#show the player's stats

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

	# Current Level
	libtcod.console_set_default_foreground(elm, libtcod.dark_amber)
	libtcod.console_print_ex(elm, config.INFO_BAR_WIDTH-2, 2, libtcod.BKGND_NONE, libtcod.RIGHT, 'Level ' + str(gameobjects.player.level))


	#OLD Status Bars
	#render_bar(2, 5, (config.INFO_BAR_WIDTH-4), 'HP', gameobjects.player.fighter.hp, gameobjects.player.fighter.max_hp, libtcod.light_red, libtcod.darker_red, elm)

	#level_up_xp = config.LEVEL_UP_BASE + gameobjects.player.level * config.LEVEL_UP_FACTOR
	#render_bar(2, 7, (config.INFO_BAR_WIDTH-4), 'XP', gameobjects.player.fighter.xp, level_up_xp, libtcod.light_green, libtcod.darker_green, elm)
	
	
	school_width = 12
	school_spacing = 5#(((config.CAMERA_WIDTH / 5) - 10)/2)
	school_first_y = 7

	libtcod.console_set_default_foreground(elm, libtcod.darker_yellow)
	libtcod.console_print_ex(elm, 2, school_first_y-1, libtcod.BKGND_NONE, libtcod.LEFT, '1) Air')
	render_bar_school(2, school_first_y, school_width, 2, 5, libtcod.yellow, libtcod.darker_yellow, elm)
	
	libtcod.console_set_default_foreground(elm, libtcod.darker_purple)
	libtcod.console_print_ex(elm, 2, school_first_y+(school_spacing*1)-1, libtcod.BKGND_NONE, libtcod.LEFT, '2) Spirit')
	render_bar_school(2, school_first_y+(school_spacing*1), school_width, 2, 5, libtcod.purple, libtcod.darker_purple, elm)

	libtcod.console_set_default_foreground(elm, libtcod.darker_blue)
	libtcod.console_print_ex(elm, 2, school_first_y+(school_spacing*2)-1, libtcod.BKGND_NONE, libtcod.LEFT, '3) Water')
	render_bar_school(2, school_first_y+(school_spacing*2), school_width, 1, 5, libtcod.blue, libtcod.darker_blue, elm)

	libtcod.console_set_default_foreground(elm, libtcod.darker_red)
	libtcod.console_print_ex(elm, 2, school_first_y+(school_spacing*3)-1, libtcod.BKGND_NONE, libtcod.LEFT, '4) Fire')
	render_bar_school(2, school_first_y+(school_spacing*3), school_width, 3, 5, libtcod.red, libtcod.darker_red, elm)

	libtcod.console_set_default_foreground(elm, libtcod.darker_green)
	libtcod.console_print_ex(elm, 2, school_first_y+(school_spacing*4)-1, libtcod.BKGND_NONE, libtcod.LEFT, '5) Earth')
	render_bar_school(2, school_first_y+(school_spacing*4), school_width, 4, 5, libtcod.green, libtcod.darker_green, elm)

	libtcod.console_set_default_foreground(elm, libtcod.black)
	libtcod.console_set_default_background(elm, libtcod.black)

	
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
	
	libtcod.console_set_default_foreground(mag, libtcod.white)
	libtcod.console_print_frame(mag,0, 0, config.INFO_BAR_WIDTH, 10, clear=False)
	libtcod.console_blit(mag, 0, 0, config.INFO_BAR_WIDTH, 10, 0, config.CAMERA_WIDTH, config.CAMERA_HEIGHT-10)





def main_init():
    #initialise main items
	if config.FONT_GREYSCALE:
		libtcod.console_set_custom_font(config.CUSTOM_FONT, 4 | config.FONT_LAYOUT )
	else:
		libtcod.console_set_custom_font(config.CUSTOM_FONT, config.FONT_LAYOUT)
	
	
	libtcod.console_init_root(config.SCREEN_WIDTH, config.SCREEN_HEIGHT, 'Elemental', False)
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


