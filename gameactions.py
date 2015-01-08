import libtcodpy as libtcod
import config
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
		if object.fighter and not isinstance(object.ai, gameobjects.MageDumb) and object.x == x and object.y == y:
			target = object
			break
	#attack or move, or something else maybe
	if target is not None:
		gameobjects.player.fighter.attack(target)
		gameinput.path_recalc = True
	else:
		gameobjects.player.move(dx, dy)
		gameinput.path_recalc = True
	gamescreen.fov_recompute = True

def next_level():
	#advance to the next level
	gamemessages.message('You feel yourself being pulled downwards.  It looks like your mage has gone downstairs!', libtcod.light_violet)
	gamemessages.message('You both take a moment to rest, and recover your strength.', libtcod.light_violet)
	gameobjects.player.fighter.heal(gameobjects.player.fighter.max_hp / 4)  #heal the player by 25%
	gameobjects.mage.fighter.heal(gameobjects.mage.fighter.max_hp / 4)  #heal the player by 25%
	gameobjects.player.fighter.heal_mana(gameobjects.player.fighter.max_mana / 4)  #mana too
	gameobjects.mage.fighter.heal_mana(gameobjects.mage.fighter.max_mana / 4)

	gamemap.dungeon_level += 1
	gamemessages.message('After a rare moment of peace, you continue to explore the dungeon...', libtcod.red)
	gameobjects.objects = [gameobjects.player, gameobjects.mage]
	#gamemap.make_map()  #create a fresh new level!
	#add a little randomality to the types of maps (BSP tree basically)
	bspd = libtcod.random_get_int(0, 6, 12)
	rsize = libtcod.random_get_int(0, 2, 10)
	forcewall = libtcod.random_get_int(0, 1, 2) > 1
	gamemap.make_bsp_map(bspd, rsize, forcewall)
	#move the player as close to their current x,y as possible, but not in a wall...
	mx = 1
	my = 1
	gameobjects.player.blocks = False
	gameobjects.mage.blocks = False
	while gamemap.is_blocked(gameobjects.player.x, gameobjects.player.y):
		print 'Moving player '+str(mx)+':'+str(my)
		gameobjects.player.x += mx
		gameobjects.player.y += my
		if gameobjects.player.x > config.MAP_WIDTH-2:
			mx = -1
			gameobjects.player.x += mx
		elif gameobjects.player.x < 2:
			mx = 1
			gameobjects.player.x += mx
		if gameobjects.player.y > config.MAP_HEIGHT-2:
			my = -1
			gameobjects.player.y += my
		elif gameobjects.player.y < 2:
			my = 1
			gameobjects.player.y += my
		print '  New Loc: '+str(gameobjects.player.x)+':'+str(gameobjects.player.y)
		#place the mage nearby
	gameobjects.player.blocks = True

	new_x = libtcod.random_get_int(0, gameobjects.player.x-1, gameobjects.player.x+1)
	new_y = libtcod.random_get_int(0, gameobjects.player.y-1, gameobjects.player.y+1)
	while gamemap.is_blocked(new_x, new_y):	
		while gamemap.is_blocked(new_x, new_y):
			new_x = libtcod.random_get_int(0, gameobjects.player.x-2, gameobjects.player.x+2)
			new_y = libtcod.random_get_int(0, gameobjects.player.y-2, gameobjects.player.y+2)
			print '  Trying: ' +str(new_x) + ' , '+str(new_x)
		print '  Placing Mage at: ' +str(new_x) + ' , '+str(new_x)
	gameobjects.mage.x = new_x
	gameobjects.mage.y = new_y	
	gameobjects.mage.blocks = True
	gameobjects.mage.ai.cur_target = None
	gameobjects.mage.ai.path = None
	
	gamescreen.initialize_fov()

def addEssence(str=1, a=0, b=0):
	#ask the player to choose a school, then add str essence to that school

	#show options and wait for the player's choice
	choice = gamescreen.menu_elemental()
	if choice == 0:  #air
		gamemessages.message('You absorb the Essence Crystal.', config.color_air_cr)
		gameobjects.player.fighter.add_el_power('air', str)
	elif choice == 1:  #spirit
		gamemessages.message('You absorb the Essence Crystal.', config.color_spirit_cr)
		gameobjects.player.fighter.add_el_power('spirit', str)
	elif choice == 2:  #water
		gamemessages.message('You absorb the Essence Crystal.', config.color_water_cr)
		gameobjects.player.fighter.add_el_power('water', str)
	elif choice == 3:  #fire
		gamemessages.message('You absorb the Essence Crystal.', config.color_fire_cr)
		gameobjects.player.fighter.add_el_power('fire', str)
	elif choice == 4:  #earth
		gamemessages.message('You absorb the Essence Crystal.', config.color_earth_cr)
		gameobjects.player.fighter.add_el_power('earth', str)
	elif choice == 5:  #health
		gamemessages.message('Absorbing the crystal makes you feel a little better.', config.color_nutr_cr)
		gameobjects.player.fighter.heal((str*20))
	elif choice == 6:  #mana
		gamemessages.message('Absorbing the crystal helps your mind to clear a bit.', config.color_nutr_cr)
		gameobjects.player.fighter.heal_mana((str*20))
	else:  #cancel
		return 'cancelled'
	#gameobjects.player.fighter.heal((str*20))
	#gameobjects.player.fighter.heal_mana((str*20))
	#gamemessages.message('Absorbing the crystal makes you feel a little better.', config.color_nutr_cr)
