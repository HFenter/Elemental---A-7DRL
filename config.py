import libtcodpy as libtcod
import ConfigParser

#Global Config Options


#Defaults
SCREEN_WIDTH = 120
SCREEN_HEIGHT = 60
LIMIT_FPS = 30
CUSTOM_FONT = 'arial10x10.png'
FULLSCREEN = False

#Global Preset Configs
MAP_WIDTH = 100
MAP_HEIGHT = 100

CAMERA_WIDTH = 70
CAMERA_HEIGHT = 50


MESSAGE_BAR_HEIGHT = SCREEN_HEIGHT - CAMERA_HEIGHT
INFO_BAR_WIDTH = SCREEN_WIDTH - CAMERA_WIDTH

FOV_ALGO = 2  #default FOV algorithm
FOV_LIGHT_WALLS = True  #light walls or not
TORCH_RADIUS = 10

#parameters for dungeon generator
ROOM_MAX_SIZE = 40
ROOM_MIN_SIZE = 6
MAX_ROOMS = 30

color_dark_wall = libtcod.Color(5, 5, 30)
color_light_wall = libtcod.Color(130, 110, 50)
color_dark_ground = libtcod.Color(17, 6, 1)
color_light_ground = libtcod.Color(187, 167, 146)

#color_torch = libtcod.Color(200, 200, 200)

color_nutr_lt = libtcod.Color(200, 200, 200)
color_nutr_cr = libtcod.Color(250, 250, 250)

color_air_lt = libtcod.Color(228, 189, 73)
color_air_cr = libtcod.Color(200, 190, 5)

color_spirit_lt = libtcod.Color(171, 127, 182)
color_spirit_cr = libtcod.Color(190, 45, 210)

color_water_lt = libtcod.Color(118, 171, 224)
color_water_cr = libtcod.Color(30, 30, 255)

color_fire_lt = libtcod.Color(231, 113, 115)
color_fire_cr = libtcod.Color(255, 30, 30)

color_earth_lt = libtcod.Color(127, 210, 41)
color_earth_cr = libtcod.Color(30, 255, 30)

color_torch = color_nutr_lt

#experience and level-ups
LEVEL_UP_BASE = 200
LEVEL_UP_FACTOR = 150


DEBUG_MODE = True



def read_config():
	global SCREEN_WIDTH, SCREEN_HEIGHT, LIMIT_FPS, CUSTOM_FONT, FULLSCREEN, FONT_GREYSCALE, FONT_LAYOUT

	config = ConfigParser.ConfigParser()
	config.read('defaults.cfg')

	SCREEN_WIDTH 	= config.getint('ScreenSetup', 'SCREEN_WIDTH')
	SCREEN_HEIGHT	= config.getint('ScreenSetup', 'SCREEN_HEIGHT')
	LIMIT_FPS		= config.getint('ScreenSetup', 'LIMIT_FPS')
	FULLSCREEN		= config.getboolean('ScreenSetup', 'FULLSCREEN')
	CUSTOM_FONT		= config.get('TileSet', 'CUSTOM_FONT')
	FONT_GREYSCALE	= config.getboolean('TileSet', 'FONT_GREYSCALE')
	FONT_LAYOUT		= config.getint('TileSet', 'FONT_LAYOUT')

def write_config():
	global SCREEN_WIDTH, SCREEN_HEIGHT, LIMIT_FPS, CUSTOM_FONT, FULLSCREEN
	config = ConfigParser.ConfigParser()
	config.add_section('ScreenSetup')
	config.set('ScreenSetup', 'SCREEN_WIDTH', SCREEN_WIDTH)
	config.set('ScreenSetup', 'SCREEN_HEIGHT', SCREEN_HEIGHT)
	config.set('ScreenSetup', 'LIMIT_FPS', LIMIT_FPS)
	config.set('ScreenSetup', 'FULLSCREEN', FULLSCREEN)

	config.add_section('TileSet')
	config.set('TileSet', 'CUSTOM_FONT', CUSTOM_FONT)
	config.set('TileSet', 'FONT_GREYSCALE', FONT_GREYSCALE)
	config.set('TileSet', 'FONT_LAYOUT', FONT_LAYOUT)
	
	# Write the config to a file 
	with open('defaults.cfg', 'wb') as configfile:
		config.write(configfile)
