import libtcodpy as libtcod
import textwrap

import config


import gameobjects
import gamescreen

game_msgs = []

def message(new_msg, color = libtcod.white):
	global game_msgs
	#split the message if necessary, among multiple lines
	new_msg_lines = textwrap.wrap(new_msg, config.SCREEN_WIDTH)
 
	for line in new_msg_lines:
		#if the buffer is full, remove the first line to make room for the new one
		if len(game_msgs) == config.MESSAGE_BAR_HEIGHT-2:
			del game_msgs[0]
 
		#add the new line as a tuple, with the text and the color
		game_msgs.append( (line, color) )