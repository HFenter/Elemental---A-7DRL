#This is where spells live
import libtcodpy as libtcod
import time
import math

import config
import gameobjects
import gamescreen
import gamemessages
import gamemap
import gameinput


#####################
#	Fire Spells		#
#####################
def cast_spark(power1=15, power2=15, power3=0):
	#ask the player for a target to burn
	gamemessages.message('Left-click an enemy to target it for the Spark spell, or right-click to cancel.', libtcod.light_cyan)
	monster = gameinput.target_monster(max_range=power2,color='dark_orange')
	if monster is None:
		return False
	elif monster == gameobjects.mage:
		#Heal / Buff should happen
		gamemessages.message('You use your Elemental powers to heal your mage, improving his health and mana by '+str(power1)+'!', libtcod.light_orange)
		gameobjects.mage.fighter.heal(power1)
		gameobjects.mage.fighter.heal_mana(power1)
		return True
	else:
		if monster.fighter.res_fire > 0:
			defpw = 1 - (float(monster.fighter.res_fire) / 10)
		else:
			defpw = 1
		rndm = ( libtcod.random_get_float(0, -.1, .1) * power1)
		spell_dmg = int(round((power1 * (defpw + rndm)), 0))
		if spell_dmg <= 0:
			gamemessages.message(monster.name + ' resists the Spark Spell.', libtcod.dark_orange)
		else:
			gamemessages.message('A small flame burns the ' + monster.name + ' for '+ str(spell_dmg) +' hit points and the smell of burning flesh permeates the air!', libtcod.dark_orange)
			monster.fighter.take_damage(spell_dmg, gameobjects.player)
	 

		return True
	

def cast_flame(power1=30, power2=3, power3=0):
	#burn everything power2 squares around player
	x = gameobjects.player.x
	y = gameobjects.player.y
	gameinput.draw_radius = power2 + 1
	gameinput.draw_radius_color = libtcod.dark_blue
	gameinput.draw_radius_type = 2
	gamescreen.render_all()
	sts = gamescreen.menu_confirm('Are you sure you want to cast Flame?', 40)
	if sts is None:
		gamemessages.message('You change your mind about casting Flame.', libtcod.red)
		gameinput.draw_radius = 0
		gameinput.draw_radius_color = None
		gameinput.draw_radius_type = 1
		return False
	else:
		gamemessages.message('You burst into flames, burning everything within ' + str(power2) + ' tiles!', libtcod.dark_orange)
		for obj in gameobjects.objects:  #damage every fighter in range
			if obj != gameobjects.player and int(math.floor(obj.distance(x, y))) <= power2 and obj.fighter:
				if obj == gameobjects.mage:
					#Heal / Buff should happen
					gamemessages.message('The spell hits your mage, but has a healing effect on him, improving his health and mana by '+str(power1)+'!', libtcod.light_orange)
					gameobjects.mage.fighter.heal(power1)
					gameobjects.mage.fighter.heal_mana(power1)
				else:
					if obj.fighter.res_fire > 0:
						defpw = 1 - (float(obj.fighter.res_fire) / 10)
					else:
						defpw = 1
					rndm = ( libtcod.random_get_float(0, -.1, .1) * power1)
					spell_dmg = int(round((power1 * (defpw + rndm)), 0))
					if spell_dmg <= 0:
						gamemessages.message(obj.name + ' resists the Flame Spell.', libtcod.dark_orange)
					else:
						gamemessages.message(obj.name + ' gets burned for ' + str(spell_dmg) + ' hit points.', libtcod.dark_orange)
						obj.fighter.take_damage(spell_dmg, gameobjects.player)
		gameinput.draw_radius = 0
		gameinput.draw_radius_color = None
		gameinput.draw_radius_type = 1
		return True


def cast_fireball(power1=30, power2=3, power3=0):
	#ask the player for a target tile to throw a fireball at
	gamemessages.message('Left-click a target tile for the Inferno spell, or right-click to cancel.', libtcod.light_cyan)
	(x, y) = gameinput.target_tile(max_range=None, radius=power2, color='dark_red')
	if x is None: 
		return False
	gamemessages.message('The Inferno explodes, burning everything within ' + str(power2) + ' tiles!', libtcod.dark_orange)
 
	for obj in gameobjects.objects:  #damage every fighter in range
		if obj != gameobjects.player and int(math.floor(obj.distance(x, y))) <= power2-1 and obj.fighter:
			if obj == gameobjects.mage:
				#Heal / Buff should happen
				gamemessages.message('The spell hits your mage, but has a healing effect on him, improving his health and mana by '+str(power1)+'!', libtcod.light_orange)
				gameobjects.mage.fighter.heal(power1)
				gameobjects.mage.fighter.heal_mana(power1)
			else:
				if obj.fighter.res_fire > 0:
					defpw = 1 - (float(obj.fighter.res_fire) / 10)
				else:
					defpw = 1
				rndm = ( libtcod.random_get_float(0, -.1, .1) * power1)
				spell_dmg = int(round((power1 * (defpw + rndm)), 0))
				if spell_dmg <= 0:
					gamemessages.message(obj.name + ' resists the Inferno Spell.', libtcod.dark_orange)
				else:
					gamemessages.message(obj.name + ' gets burned for ' + str(spell_dmg) + ' hit points.', libtcod.dark_orange)
					obj.fighter.take_damage(spell_dmg, gameobjects.player)
	return True


#####################
#	Air Spells		#
#####################
def cast_puff(power1=15, power2=1, power3=0):
	#ask the player for a target to blow
	gamemessages.message('Left-click an enemy to target it for the Puff spell, or right-click to cancel.', libtcod.light_cyan)
	monster = gameinput.target_monster(max_range=15,color='dark_yellow')
	if monster is None:
		return False
	elif monster == gameobjects.mage:
		#Heal / Buff should happen
		gamemessages.message('You use your Elemental powers to heal your mage, improving his health and mana by '+str(power1)+'!', libtcod.light_yellow)
		gameobjects.mage.fighter.heal(power1)
		gameobjects.mage.fighter.heal_mana(power1)
		return True
	else:
		if monster.fighter.res_air > 0:
			defpw = 1 - (float(monster.fighter.res_air) / 10)
		else:
			defpw = 1
		rndm = ( libtcod.random_get_float(0, -.1, .1) * power1)
		spell_dmg = int(round((power1 * (defpw + rndm)), 0))
		if spell_dmg <= 0:
			gamemessages.message(monster.name + ' resists the Puff Spell.', libtcod.dark_orange)
		else:
			gamemessages.message('A gust of wind blows the ' + monster.name + ' '+str(power2)+' squares back and hits it for '+ str(spell_dmg) +' hit points!', libtcod.dark_yellow)
			wind_dist=0
			while wind_dist < power2:
				monster.move_away(gameobjects.player.x, gameobjects.player.y)
				wind_dist +=1
			gameinput.path_recalc = True
			monster.fighter.take_damage(spell_dmg, gameobjects.player)
		return True


def cast_wind(power1=30, power2=1, power3=1):
	#blow everything power2 squares around player
	x = gameobjects.player.x
	y = gameobjects.player.y
	gameinput.draw_radius = power2 + 1
	gameinput.draw_radius_color = libtcod.dark_blue
	gameinput.draw_radius_type = 2
	gamescreen.render_all()
	sts = gamescreen.menu_confirm('Are you sure you want to cast Wind?', 40)
	if sts is None:
		gamemessages.message('You change your mind about casting Wind.', libtcod.red)
		gameinput.draw_radius = 0
		gameinput.draw_radius_color = None
		gameinput.draw_radius_type = 1
		return False
	else:
		gamemessages.message('You emit a mighty Wind, blowing everything near you ' + str(power3) + ' tiles away!', libtcod.dark_yellow)
		for obj in gameobjects.objects:  #damage every fighter in range
			if obj != gameobjects.player and int(math.floor(obj.distance(x, y))) <= power2 and obj.fighter:
				if obj == gameobjects.mage:
					#Heal / Buff should happen
					gamemessages.message('The spell hits your mage, but has a healing effect on him, improving his health and mana by '+str(power1)+'!', libtcod.light_yellow)
					gameobjects.mage.fighter.heal(power1)
					gameobjects.mage.fighter.heal_mana(power1)
				else:
					if obj.fighter.res_air > 0:
						defpw = 1 - (float(obj.fighter.res_air) / 10)
					else:
						defpw = 1
					rndm = ( libtcod.random_get_float(0, -.1, .1) * power1)
					spell_dmg = int(round((power1 * (defpw + rndm)), 0))
					if spell_dmg <= 0:
						gamemessages.message(obj.name + ' resists the Wind Spell.', libtcod.dark_yellow)
					else:
						gamemessages.message(obj.name + ' gets blown for ' + str(spell_dmg) + ' hit points.', libtcod.dark_yellow)
						wind_dist=0
						while wind_dist < power3:
							obj.move_away(gameobjects.player.x, gameobjects.player.y)
							wind_dist +=1
						gameinput.path_recalc = True
						obj.fighter.take_damage(spell_dmg, gameobjects.player)
		gameinput.draw_radius = 0
		gameinput.draw_radius_color = None
		gameinput.draw_radius_type = 1
		return True

def cast_tornado(power1=30, power2=1, power3=1):
	#blow everything power2 squares around target

	#ask the player for a target tile to throw a tornado at
	gamemessages.message('Left-click a target tile for the Tornado spell, or right-click to cancel.', libtcod.light_cyan)
	(x, y) = gameinput.target_tile(max_range=None, radius=power2, color='dark_blue')
	if x is None: 
		return False
	gamemessages.message('The Tornado twists to life, blowing everything within ' + str(power2) + ' tiles!', libtcod.dark_yellow)
 
	for obj in gameobjects.objects:  #damage every fighter in range
		if obj != gameobjects.player and int(math.floor(obj.distance(x, y))) <= power2-1 and obj.fighter:
			if obj == gameobjects.mage:
				#Heal / Buff should happen
				gamemessages.message('The spell hits your mage, but has a healing effect on him, improving his health and mana by '+str(power1)+'!', libtcod.light_yellow)
				gameobjects.mage.fighter.heal(power1)
				gameobjects.mage.fighter.heal_mana(power1)
			else:
				if obj.fighter.res_air > 0:
					defpw = 1 - (float(obj.fighter.res_air) / 10)
				else:
					defpw = 1
				rndm = ( libtcod.random_get_float(0, -.1, .1) * power1)
				spell_dmg = int(round((power1 * (defpw + rndm)), 0))
				if spell_dmg <= 0:
					gamemessages.message(obj.name + ' resists the Tornado Spell.', libtcod.dark_yellow)
				else:
					gamemessages.message(obj.name + ' gets blown for ' + str(spell_dmg) + ' hit points.', libtcod.dark_yellow)
					wind_dist=0
					while wind_dist < power3:
						obj.move_away(x, y)
						wind_dist +=1
					gameinput.path_recalc = True
					obj.fighter.take_damage(spell_dmg, gameobjects.player)
	return True





#####################
#	Earth Spells	#
#####################
def cast_pebble(power1=15, power2=1, power3=0):
	#ask the player for a target to blow
	gamemessages.message('Left-click an enemy to target it for the Hail of Pebbles spell, or right-click to cancel.', libtcod.light_cyan)
	monster = gameinput.target_monster(max_range=15,color='dark_green')
	if monster is None:
		return False
	elif monster == gameobjects.mage:
		#Heal / Buff should happen
		gamemessages.message('You use your Elemental powers to heal your mage, improving his health and mana by '+str(power1)+'!', libtcod.light_green)
		gameobjects.mage.fighter.heal(power1)
		gameobjects.mage.fighter.heal_mana(power1)
		return True
	else:
		if monster.fighter.res_earth > 0:
			defpw = 1 - (float(monster.fighter.res_earth) / 10)
		else:
			defpw = 1
		rndm = ( libtcod.random_get_float(0, -.1, .1) * power1)
		spell_dmg = int(round((power1 * (defpw + rndm)), 0))
		if spell_dmg <= 0:
			gamemessages.message(monster.name + ' resists the Hail of Pebbles Spell.', libtcod.dark_green)
		else:
			gamemessages.message('A hail of pebbles flies at the ' + monster.name + ' hitting it for '+ str(spell_dmg) +' and preventing it from moving for '+ str(power2) +' turn!', libtcod.dark_green)
			monster.fighter.rooted = power2
			monster.fighter.take_damage(spell_dmg, gameobjects.player)
		return True


def cast_rock(power1=30, power2=1, power3=1):
	#blow everything power2 squares around player
	x = gameobjects.player.x
	y = gameobjects.player.y
	gameinput.draw_radius = power2 + 1
	gameinput.draw_radius_color = libtcod.dark_blue
	gameinput.draw_radius_type = 2
	gamescreen.render_all()
	sts = gamescreen.menu_confirm('Are you sure you want to cast Falling Rocks?', 40)
	if sts is None:
		gamemessages.message('You change your mind about casting Wind.', libtcod.red)
		gameinput.draw_radius = 0
		gameinput.draw_radius_color = None
		gameinput.draw_radius_type = 1
		return False
	else:
		gamemessages.message('Huge rocks rain down all around you, crushing everything within ' + str(power2) + ' tiles and burying their feet, rooting them for ' + str(power3) + ' turns!', libtcod.dark_green)
		for obj in gameobjects.objects:  #damage every fighter in range
			if obj != gameobjects.player and int(math.floor(obj.distance(x, y))) <= power2 and obj.fighter:
				if obj == gameobjects.mage:
					#Heal / Buff should happen
					gamemessages.message('The spell hits your mage, but has a healing effect on him, improving his health and mana by '+str(power1)+'!', libtcod.light_green)
					gameobjects.mage.fighter.heal(power1)
					gameobjects.mage.fighter.heal_mana(power1)
				else:
					if obj.fighter.res_earth > 0:
						defpw = 1 - (float(obj.fighter.res_earth) / 10)
					else:
						defpw = 1
					rndm = ( libtcod.random_get_float(0, -.1, .1) * power1)
					spell_dmg = int(round((power1 * (defpw + rndm)), 0))
					if spell_dmg <= 0:
						gamemessages.message(obj.name + ' resists the Falling Rocks Spell.', libtcod.dark_green)
					else:
						gamemessages.message(obj.name + ' gets hit for ' + str(spell_dmg) + ' and rooted for '+str(power3)+' turns.', libtcod.dark_green)
						obj.fighter.rooted = power3
						obj.fighter.take_damage(spell_dmg, gameobjects.player)
		gameinput.draw_radius = 0
		gameinput.draw_radius_color = None
		gameinput.draw_radius_type = 1
		return True

def cast_boulder(power1=30, power2=1, power3=1):
	#blow everything power2 squares around target

	#ask the player for a target tile to throw a tornado at
	gamemessages.message('Left-click a target tile for the Toss Boulder spell, or right-click to cancel.', libtcod.light_cyan)
	(x, y) = gameinput.target_tile(max_range=None, radius=power2, color='dark_green')
	if x is None: 
		return False
	gamemessages.message('You toss a huge Boulder, damaging and stunning everything within ' + str(power2) + ' tiles!', libtcod.dark_green)
 
	for obj in gameobjects.objects:  #damage every fighter in range
		if obj != gameobjects.player and int(math.floor(obj.distance(x, y))) <= power2-1 and obj.fighter:
			if obj == gameobjects.mage:
				#Heal / Buff should happen
				gamemessages.message('The spell hits your mage, but has a healing effect on him, improving his health and mana by '+str(power1)+'!', libtcod.light_green)
				gameobjects.mage.fighter.heal(power1)
				gameobjects.mage.fighter.heal_mana(power1)
			else:
				if obj.fighter.res_earth > 0:
					defpw = 1 - (float(obj.fighter.res_earth) / 10)
				else:
					defpw = 1
				rndm = ( libtcod.random_get_float(0, -.1, .1) * power1)
				spell_dmg = int(round((power1 * (defpw + rndm)), 0))
				if spell_dmg <= 0:
					gamemessages.message(obj.name + ' resists the Boulders Effects.', libtcod.dark_green)
				else:
					gamemessages.message(obj.name + ' gets hit for ' + str(spell_dmg) + ' and stunned for ' + str(power3) + ' turns.', libtcod.dark_green)
					obj.fighter.rooted = power3
					obj.fighter.take_damage(spell_dmg, gameobjects.player)
	return True



#####################
#	Water Spells	#
#####################
def cast_drip(power1=15, power2=1, power3=0):
	#ask the player for a target to blow
	gamemessages.message('Left-click an enemy to target it for the Drip spell, or right-click to cancel.', libtcod.light_cyan)
	monster = gameinput.target_monster(max_range=15,color='dark_blue')
	if monster is None:
		return False
	elif monster == gameobjects.mage:
		#Heal / Buff should happen
		gamemessages.message('You use your Elemental powers to heal your mage, improving his health and mana by '+str(power1)+'!', libtcod.light_blue)
		gameobjects.mage.fighter.heal(power1)
		gameobjects.mage.fighter.heal_mana(power1)
		return True
	else:
		if monster.fighter.res_water > 0:
			defpw = 1 - (float(monster.fighter.res_water) / 10)
		else:
			defpw = 1
		rndm = ( libtcod.random_get_float(0, -.1, .1) * power1)
		spell_dmg = int(round((power1 * (defpw + rndm)), 0))
		if spell_dmg <= 0:
			gamemessages.message(monster.name + ' resists the Drip Spell.', libtcod.dark_blue)
		else:
			gamemessages.message('The ' + monster.name + ' begins to drown, causing it to panic for '+ str(power2) +' turns and take '+ str(spell_dmg) +' damage!', libtcod.dark_blue)
			#replace the monster's AI with a "confused" one; after some turns it will restore the old AI
			old_ai = monster.ai
			monster.ai = gameobjects.ConfusedMonster(old_ai, power2)
			monster.ai.owner = monster  #tell the new component who owns it
			monster.fighter.take_damage(spell_dmg, gameobjects.player)
		return True


def cast_flood(power1=30, power2=1, power3=1):
	#blow everything power2 squares around player
	x = gameobjects.player.x
	y = gameobjects.player.y
	gameinput.draw_radius = power2 + 1
	gameinput.draw_radius_color = libtcod.dark_blue
	gameinput.draw_radius_type = 2
	gamescreen.render_all()
	sts = gamescreen.menu_confirm('Are you sure you want to cast Flood?', 40)
	if sts is None:
		gamemessages.message('You change your mind about casting Flood.', libtcod.red)
		gameinput.draw_radius = 0
		gameinput.draw_radius_color = None
		gameinput.draw_radius_type = 1
		return False
	else:
		gamemessages.message('A Flood of Water flows from you, pushing everything near you ' + str(power3) + ' tiles away!', libtcod.dark_blue)
		for obj in gameobjects.objects:  #damage every fighter in range
			if obj != gameobjects.player and int(math.floor(obj.distance(x, y))) <= power2 and obj.fighter:
				if obj == gameobjects.mage:
					#Heal / Buff should happen
					gamemessages.message('The spell hits your mage, but has a healing effect on him, improving his health and mana by '+str(power1)+'!', libtcod.light_blue)
					gameobjects.mage.fighter.heal(power1)
					gameobjects.mage.fighter.heal_mana(power1)
				else:
					if obj.fighter.res_water > 0:
						defpw = 1 - (float(obj.fighter.res_water) / 10)
					else:
						defpw = 1
					rndm = ( libtcod.random_get_float(0, -.1, .1) * power1)
					spell_dmg = int(round((power1 * (defpw + rndm)), 0))
					if spell_dmg <= 0:
						gamemessages.message(obj.name + ' resists the Flood Spell.', libtcod.dark_blue)
					else:
						gamemessages.message(obj.name + ' gets pushed ' + str(power3) + ' for ' + str(spell_dmg) + ' hit points.', libtcod.dark_blue)
						wind_dist=0
						while wind_dist < power3:
							obj.move_away(gameobjects.player.x, gameobjects.player.y)
							wind_dist +=1
						gameinput.path_recalc = True
						obj.fighter.take_damage(spell_dmg, gameobjects.player)
		gameinput.draw_radius = 0
		gameinput.draw_radius_color = None
		gameinput.draw_radius_type = 1
		return True

def cast_torrent(power1=30, power2=1, power3=1):
	#blow everything power2 squares around target

	#ask the player for a target tile to throw a tornado at
	gamemessages.message('Left-click a target tile for the Torrent spell, or right-click to cancel.', libtcod.light_cyan)
	(x, y) = gameinput.target_tile(max_range=None, radius=power2, color='dark_blue')
	if x is None: 
		return False
	gamemessages.message('You create a huge Torrent of Water, damaging and stunning everything within ' + str(power2) + ' tiles!', libtcod.dark_blue)
 
	for obj in gameobjects.objects:  #damage every fighter in range
		if obj != gameobjects.player and int(math.floor(obj.distance(x, y))) <= power2-1 and obj.fighter:
			if obj == gameobjects.mage:
				#Heal / Buff should happen
				gamemessages.message('The spell hits your mage, but has a healing effect on him, improving his health and mana by '+str(power1)+'!', libtcod.light_blue)
				gameobjects.mage.fighter.heal(power1)
				gameobjects.mage.fighter.heal_mana(power1)
			else:
				if obj.fighter.res_water > 0:
					defpw = 1 - (float(obj.fighter.res_water) / 10)
				else:
					defpw = 1
				rndm = ( libtcod.random_get_float(0, -.1, .1) * power1)
				spell_dmg = int(round((power1 * (defpw + rndm)), 0))
				if spell_dmg <= 0:
					gamemessages.message(obj.name + ' resists the Torrents effects.', libtcod.dark_blue)
				else:
					gamemessages.message(obj.name + ' gets hit for ' + str(spell_dmg) + ' and stunned for ' + str(power3) + ' turns.', libtcod.dark_blue)
					obj.fighter.rooted = power3
					obj.fighter.take_damage(spell_dmg, gameobjects.player)
	return True



#####################
#	Spirit Spells	#
#####################
def cast_suggestion(power1=15, power2=1, power3=0):
	#ask the player for a target to blow
	gamemessages.message('Left-click an enemy to target it for the Suggestion spell, or right-click to cancel.', libtcod.light_cyan)
	monster = gameinput.target_monster(max_range=15,color='dark_purple')
	if monster is None:
		return False
	elif monster == gameobjects.mage:
		#Heal / Buff should happen
		gamemessages.message('You use your Elemental powers to heal your mage, improving his health and mana by '+str(power1)+'!', libtcod.light_purple)
		gameobjects.mage.fighter.heal(power1)
		gameobjects.mage.fighter.heal_mana(power1)
		return True
	else:
		if monster.fighter.res_spirit > 0:
			defpw = 1 - (float(monster.fighter.res_spirit) / 10)
		else:
			defpw = 1
		rndm = ( libtcod.random_get_float(0, -.1, .1) * power1)
		spell_dmg = int(round((power1 * (defpw + rndm)), 0))
		if spell_dmg <= 0:
			gamemessages.message(monster.name + ' resists the Suggestion Spell.', libtcod.dark_purple)
		else:
			gamemessages.message('The ' + monster.name + ' writhes in mental agony,  causing '+ str(spell_dmg) +' damage and confusing it for '+str(power2)+' turns!', libtcod.dark_purple)
			#replace the monster's AI with a "confused" one; after some turns it will restore the old AI
			old_ai = monster.ai
			monster.ai = gameobjects.ConfusedMonster(old_ai, power2)
			monster.ai.owner = monster  #tell the new component who owns it
			monster.fighter.take_damage(spell_dmg, gameobjects.player)
		return True
def cast_confusion(power1=15, power2=1, power3=0):
	#blow everything power2 squares around player
	x = gameobjects.player.x
	y = gameobjects.player.y
	gameinput.draw_radius = power2 + 1
	gameinput.draw_radius_color = libtcod.dark_purple
	gameinput.draw_radius_type = 2
	gamescreen.render_all()
	sts = gamescreen.menu_confirm('Are you sure you want to cast Confusion?', 40)
	if sts is None:
		gamemessages.message('You change your mind about casting Confusion.', libtcod.red)
		gameinput.draw_radius = 0
		gameinput.draw_radius_color = None
		gameinput.draw_radius_type = 1
		return False
	else:
		gamemessages.message('You cause intense mental anguish to everything in the area, hurting and confusing it!', libtcod.dark_purple)
		for obj in gameobjects.objects:  #damage every fighter in range
			if obj != gameobjects.player and int(math.floor(obj.distance(x, y))) <= power2 and obj.fighter:
				if obj == gameobjects.mage:
					#Heal / Buff should happen
					gamemessages.message('The spell hits your mage, but has a healing effect on him, improving his health and mana by '+str(power1)+'!', libtcod.light_purple)
					gameobjects.mage.fighter.heal(power1)
					gameobjects.mage.fighter.heal_mana(power1)
				else:
					if obj.fighter.res_spirit > 0:
						defpw = 1 - (float(obj.fighter.res_spirit) / 10)
					else:
						defpw = 1
					rndm = ( libtcod.random_get_float(0, -.1, .1) * power1)
					spell_dmg = int(round((power1 * (defpw + rndm)), 0))
					if spell_dmg <= 0:
						gamemessages.message(obj.name + ' resists the effects of Insanity.', libtcod.dark_purple)
					else:
						gamemessages.message(obj.name + ' writhes in mental agony,  causing '+ str(spell_dmg) +' damage and confusing it for '+str(power3)+' turns!', libtcod.dark_purple)
						old_ai = obj.ai
						obj.ai = gameobjects.ConfusedMonster(old_ai, power3)
						obj.ai.owner = obj  #tell the new component who owns it
						obj.fighter.take_damage(spell_dmg, gameobjects.player)
		gameinput.draw_radius = 0
		gameinput.draw_radius_color = None
		gameinput.draw_radius_type = 1
		return True

def cast_insanity(power1=15, power2=1, power3=0):
	#ask the player for a target tile to throw a tornado at
	gamemessages.message('Left-click a target tile for the Insanity spell, or right-click to cancel.', libtcod.light_cyan)
	(x, y) = gameinput.target_tile(max_range=None, radius=power2, color='dark_purple')
	if x is None: 
		return False
	gamemessages.message('You cause intense mental anguish to everything in the area, hurting and confusing it!', libtcod.dark_purple)
 
	for obj in gameobjects.objects:  #damage every fighter in range
		if obj != gameobjects.player and int(math.floor(obj.distance(x, y))) <= power2-1 and obj.fighter:
			if obj == gameobjects.mage:
				#Heal / Buff should happen
				gamemessages.message('The spell hits your mage, but has a healing effect on him, improving his health and mana by '+str(power1)+'!', libtcod.light_purple)
				gameobjects.mage.fighter.heal(power1)
				gameobjects.mage.fighter.heal_mana(power1)
			else:
				if obj.fighter.res_spirit > 0:
					defpw = 1 - (float(obj.fighter.res_spirit) / 10)
				else:
					defpw = 1
				rndm = ( libtcod.random_get_float(0, -.1, .1) * power1)
				spell_dmg = int(round((power1 * (defpw + rndm)), 0))
				if spell_dmg <= 0:
					gamemessages.message(obj.name + ' resists the effects of Insanity.', libtcod.dark_purple)
				else:
					gamemessages.message(obj.name + ' writhes in mental agony,  causing '+ str(spell_dmg) +' damage and confusing it for '+str(power3)+' turns!', libtcod.dark_purple)
					old_ai = obj.ai
					obj.ai = gameobjects.ConfusedMonster(old_ai, power3)
					obj.ai.owner = obj  #tell the new component who owns it
					obj.fighter.take_damage(spell_dmg, gameobjects.player)
	return True

#################
#  mage spells	#
#################

def cast_heal(power1=30):
	#heal the mage
	gamemessages.message(gameobjects.mage.name + ' casts a spell to heal his meaty flesh body!', libtcod.light_violet)
	gameobjects.mage.fighter.heal(int(power1))

def cast_lightning(power1, targets):
	#find closest enemy (inside a maximum range) and damage it
	gamemessages.message('Your Mage casts a Lightning Storm, hitting nearby targets with massive bolts of lightning.', libtcod.light_blue)
	for monster in targets:
		gamemessages.message('A lighting bolt strikes the ' + monster.name + ' with a loud thunder! The damage is ' + str(int(power1)) + ' hit points.', libtcod.light_blue)
		monster.fighter.take_damage(power1, gameobjects.mage)
def cast_zap(power1, targets):
	#find closest enemy (inside a maximum range) and damage it
	for monster in targets:
		gamemessages.message('Your mage casts a Zap spell, striking the ' + monster.name + ' with a crack of energy! The damage is ' + str(int(power1)) + ' hit points.', libtcod.light_blue)
		monster.fighter.take_damage(power1, gameobjects.mage)
    


def cast_confuse(turns, targets):
	#ask the player for a target to confuse
	for monster in targets:
		#replace the monster's AI with a "confused" one; after some turns it will restore the old AI
		old_ai = monster.ai
		monster.ai = gameobjects.ConfusedMonster(old_ai, turns)
		monster.ai.owner = monster  #tell the new component who owns it
		gamemessages.message('Your mage casts Sparkle at the ' + monster.name + '.  His eyes look vacant, as he starts to stumble around!', libtcod.light_green)