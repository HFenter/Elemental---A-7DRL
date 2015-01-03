#This is where spells live
import libtcodpy as libtcod
import config
import gameobjects
import gamescreen
import gamemessages
import gamemap
import gameinput


def cast_heal(power1=30, power2=0, power3=0):
	#heal the player
	if gameobjects.player.fighter.hp == gameobjects.player.fighter.max_hp:
		gamemessages.message('You are already at full health.', libtcod.red)
		return 'cancelled'
 
	gamemessages.message('Your wounds start to feel better!', libtcod.light_violet)
	gameobjects.player.fighter.heal(power1)

def cast_lightning(power1=40, power2=0, power3=0):
    #find closest enemy (inside a maximum range) and damage it
    monster = gameobjects.closest_monster(10)
    if monster is None:  #no enemy found within maximum range
        gamemessages.message('No enemy is close enough to strike.', libtcod.red)
        return 'cancelled'
    #zap it!
    gamemessages.message('A lighting bolt strikes the ' + monster.name + ' with a loud thunder! The damage is ' + str(power1) + ' hit points.', libtcod.light_blue)
    monster.fighter.take_damage(power1)

def cast_fireball(power1=30, power2=10, power3=0):
	#ask the player for a target tile to throw a fireball at
	gamemessages.message('Left-click a target tile for the fireball, or right-click to cancel.', libtcod.light_cyan)
	(x, y) = gameinput.target_tile()
	if x is None: 
		return 'cancelled'
	gamemessages.message('The fireball explodes, burning everything within ' + str(power2) + ' tiles!', libtcod.orange)
 
	for obj in gameobjects.objects:  #damage every fighter in range, including the player
		if obj.distance(x, y) <= power2 and obj.fighter:
			gamemessages.message(obj.name + ' gets burned for ' + str(power1) + ' hit points.', libtcod.orange)
			obj.fighter.take_damage(power1)

def cast_confuse(power1=4, power2=15, power3=0):
	#ask the player for a target to confuse
	gamemessages.message('Left-click an enemy to confuse it, or right-click to cancel.', libtcod.light_cyan)
	monster = gameinput.target_monster(power2)
	if monster is None:
		return 'cancelled'
 
	#replace the monster's AI with a "confused" one; after some turns it will restore the old AI
	old_ai = monster.ai
	monster.ai = gameobjects.ConfusedMonster(old_ai, power1)
	monster.ai.owner = monster  #tell the new component who owns it
	gamemessages.message('The eyes of the ' + monster.name + ' look vacant, as he starts to stumble around!', libtcod.light_green)