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
MAP_WIDTH = 200
MAP_HEIGHT = 200

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

color_dark_wall = libtcod.Color(0, 0, 100)
color_light_wall = libtcod.Color(130, 110, 50)
color_dark_ground = libtcod.Color(50, 50, 150)
color_light_ground = libtcod.Color(200, 180, 50)






def read_config():
	global SCREEN_WIDTH, SCREEN_HEIGHT, LIMIT_FPS, CUSTOM_FONT, FULLSCREEN

	config = ConfigParser.ConfigParser()
	config.read('defaults.cfg')

	SCREEN_WIDTH 	= config.getint('ScreenSetup', 'SCREEN_WIDTH')
	SCREEN_HEIGHT	= config.getint('ScreenSetup', 'SCREEN_HEIGHT')
	LIMIT_FPS		= config.getint('ScreenSetup', 'LIMIT_FPS')
	FULLSCREEN		= config.getboolean('ScreenSetup', 'FULLSCREEN')
	CUSTOM_FONT		= config.get('TileSet', 'CUSTOM_FONT')

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
	# Write the config to a file 
	with open('defaults.cfg', 'wb') as configfile:
		config.write(configfile)
