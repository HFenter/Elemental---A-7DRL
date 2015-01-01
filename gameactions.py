import libtcodpy as libtcod

import gameobjects
import gamescreen

import gamemessages


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
	
	gameobjects.player.move(dx, dy)
	gamescreen.fov_recompute = True



def cast_heal():
	#heal the player
	if gameobjects.player.fighter.hp == gameobjects.player.fighter.max_hp:
		gamemessages.message('You are already at full health.', libtcod.red)
		return 'cancelled'
 
	gamemessages.message('Your wounds start to feel better!', libtcod.light_violet)
	gameobjects.player.fighter.heal(5)
 