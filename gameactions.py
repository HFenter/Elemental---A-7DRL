import libtcodpy as libtcod

import gameobjects
import gamescreen

import gamemessages
import gamemap

import gameinput
import gamespells


def player_move_or_attack(dx, dy):
 
	#the coordinates the player is moving to/attacking
	x = gameobjects.player.x + dx
	y = gameobjects.player.y + dy
 
	#try to find an attackable object there
	target = None
	for object in gameobjects.objects:
		if object.fighter and object.x == x and object.y == y:
			target = object
			break
	#attack or move, or something else maybe
	if target is not None:
		gameobjects.player.fighter.attack(target)
	else:
		gameobjects.player.move(dx, dy)
		gameinput.path_recalc = True
	gamescreen.fov_recompute = True

def next_level():
	#advance to the next level
	gamemessages.message('You take a moment to rest, and recover your strength.', libtcod.light_violet)
	gameobjects.player.fighter.heal(gameobjects.player.fighter.max_hp / 2)  #heal the player by 50%

	gamemap.dungeon_level += 1
	gamemessages.message('After a rare moment of peace, you descend deeper into the heart of the dungeon...', libtcod.red)
	gameobjects.objects = [gameobjects.player]
	gamemap.make_map()  #create a fresh new level!
	gamescreen.initialize_fov()
