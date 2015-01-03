import libtcodpy as libtcod

import gameobjects
import gamescreen

import gamemessages
import gamemap

import gameinput


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



def cast_heal():
	#heal the player
	if gameobjects.player.fighter.hp == gameobjects.player.fighter.max_hp:
		gamemessages.message('You are already at full health.', libtcod.red)
		return 'cancelled'
 
	gamemessages.message('Your wounds start to feel better!', libtcod.light_violet)
	gameobjects.player.fighter.heal(35)
 
def cast_lightning():
    #find closest enemy (inside a maximum range) and damage it
    monster = gameobjects.closest_monster(10)
    if monster is None:  #no enemy found within maximum range
        gamemessages.message('No enemy is close enough to strike.', libtcod.red)
        return 'cancelled'
 
    #zap it!
    gamemessages.message('A lighting bolt strikes the ' + monster.name + ' with a loud thunder! The damage is '
        + str(40) + ' hit points.', libtcod.light_blue)
    monster.fighter.take_damage(40)

def cast_fireball():
	#ask the player for a target tile to throw a fireball at
	gamemessages.message('Left-click a target tile for the fireball, or right-click to cancel.', libtcod.light_cyan)
	(x, y) = gameinput.target_tile()
	if x is None: return 'cancelled'
	gamemessages.message('The fireball explodes, burning everything within ' + str(10) + ' tiles!', libtcod.orange)
 
	for obj in gameobjects.objects:  #damage every fighter in range, including the player
		if obj.distance(x, y) <= 10 and obj.fighter:
			gamemessages.message('The ' + obj.name + ' gets burned for ' + str(30) + ' hit points.', libtcod.orange)
			obj.fighter.take_damage(30)

def cast_confuse():
	#ask the player for a target to confuse
	gamemessages.message('Left-click an enemy to confuse it, or right-click to cancel.', libtcod.light_cyan)
	monster = gameinput.target_monster(15)
	if monster is None: return 'cancelled'
 
	#replace the monster's AI with a "confused" one; after some turns it will restore the old AI
	old_ai = monster.ai
	monster.ai = gameobjects.ConfusedMonster(old_ai)
	monster.ai.owner = monster  #tell the new component who owns it
	gamemessages.message('The eyes of the ' + monster.name + ' look vacant, as he starts to stumble around!', libtcod.light_green)