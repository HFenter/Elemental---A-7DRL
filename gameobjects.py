import libtcodpy as libtcod
import math
import json
import time
from pprint import pprint

import config

import gamemap
import gamescreen
import gamemessages
import gameinput
import gameactions
import gamespells

inventory = []
numMonsters = 0
numItems = 0

class TargetLoc:
	def __init__(self, x, y):
		self.x = x
		self.y = y

class Object:
	#this is a generic object: the player, a monster, an item, the stairs...
	#it's always represented by a character on screen.
	def __init__(self, x, y, char, name, color, blocks=False, always_visible=False, fighter=None, ai=None, item=None, equipment=None, desc=''):
		self.x = x
		self.y = y
		self.char = char
		self.desc = desc
		if isinstance( self.char, int ) or len(self.char)>1:
			self.char = int(self.char)
		self.name = name
		self.color = color
		self.blocks = blocks
		self.always_visible = always_visible
		self.location_seen = False
		self.fighter = fighter
		if self.fighter:  #let the fighter component know who owns it
			self.fighter.owner = self

		self.ai = ai
		if self.ai:  #let the AI component know who owns it
			self.ai.owner = self

		self.item = item
		if self.item:  #let the Item component know who owns it
			self.item.owner = self


	def move(self, dx, dy):
		#move by the given amount, if the destination is not blocked
		if not gamemap.is_blocked(self.x + dx, self.y + dy):
			self.x += dx
			self.y += dy
		elif isinstance(self.fighter, Elemental):
			#if walking into blocking object, let them know (once)
			if mage.x == self.x + dx and mage.y == self.y + dy and  gamemessages.game_msgs[len(gamemessages.game_msgs)-1][0]!='Attacking Your Mage wouldn\'t be very nice!':
				gamemessages.message('Attacking Your Mage wouldn\'t be very nice!',libtcod.dark_red)
			elif gamemessages.game_msgs[len(gamemessages.game_msgs)-1][0]!='There is something in the way!':
				gamemessages.message('There is something in the way!',libtcod.dark_red)
			

	def move_towards(self, target_x, target_y):
		#vector from this object to the target, and distance
		dx = target_x - self.x
		dy = target_y - self.y
		distance = math.sqrt(dx ** 2 + dy ** 2)

		#normalize it to length 1 (preserving direction), then round it and
		#convert to integer so the movement is restricted to the map grid
		dx = int(round(dx / distance))
		dy = int(round(dy / distance))
		self.move(dx, dy)

	def move_away(self, target_x, target_y):
		#vector from this object to the target, and distance
		dx = target_x - self.x
		dy = target_y - self.y
		if dx == 0 and dy == 0:
			dx = 1
		distance = math.sqrt(dx ** 2 + dy ** 2)

		#normalize it to length 1 (preserving direction), then round it and
		#convert to integer so the movement is restricted to the map grid
		dx = int(round(dx / distance))
		dy = int(round(dy / distance))
		self.move(-dx, -dy)

	def distance_to(self, other):
		#return the distance to another object
		dx = other.x - self.x
		dy = other.y - self.y
		return math.sqrt(dx ** 2 + dy ** 2)

	def distance(self, x, y):
		#return the distance to some coordinates
		return math.sqrt((x - self.x) ** 2 + (y - self.y) ** 2)

	def send_to_back(self):
		#make this object be drawn first, so all others appear above it if they're in the same tile.
		global objects
		objects.remove(self)
		objects.insert(0, self)

	def draw(self):
		#only show if it's visible to the player
		if libtcod.map_is_in_fov(gamescreen.fov_map, self.x, self.y):
			(x, y) = gamescreen.to_camera_coordinates(self.x, self.y)
			if x is not None:
				#set this item as seen
				self.location_seen = True
				if isinstance(self.ai, ChaseMonster):
					self.ai.seen_player = True
				#set the color and then draw the character that represents this object at its position
				libtcod.console_set_default_foreground(gamescreen.con, self.color)
				libtcod.console_put_char(gamescreen.con, x, y, self.char, libtcod.BKGND_NONE)
		#always visible item, show it darker (out of FoV)
		elif self.always_visible and self.location_seen:
			(x, y) = gamescreen.to_camera_coordinates(self.x, self.y)
			if x is not None:
				#set the color as a lerp of the item color and dark ground
				tmp_color = libtcod.color_lerp( config.color_dark_ground, self.color,.5)
				libtcod.console_set_default_foreground(gamescreen.con, tmp_color)
				libtcod.console_put_char(gamescreen.con, x, y, self.char, libtcod.BKGND_NONE)

	def clear(self):
		#erase the character that represents this object
		(x, y) = gamescreen.to_camera_coordinates(self.x, self.y)
		if x is not None:
			libtcod.console_put_char(gamescreen.con, x, y, ' ', libtcod.BKGND_NONE)

class Item:
    #an item that can be picked up and used.
    def __init__(self, use_function=None, power1=0, power2=0, power3=0):
        self.use_function = use_function
        #pass some generic variables so we can use them in the use_function
        # ( I don't like this method, but i can fix it later )
        self.power1 = power1
        self.power2 = power2
        self.power3 = power3
 
    def pick_up(self):
        #add to the player's inventory and remove from the map
        if len(inventory) >= 26:
            gamemessages.message('Your inventory is full, cannot pick up ' + self.owner.name + '.', libtcod.red)
        else:
            inventory.append(self.owner)
            objects.remove(self.owner)
            gamemessages.message('You picked up a ' + self.owner.name + '!', libtcod.green)
 
 
    def drop(self):
        #add to the map and remove from the player's inventory. also, place it at the player's coordinates
        objects.append(self.owner)
        inventory.remove(self.owner)
        self.owner.x = player.x
        self.owner.y = player.y
        self.owner.location_seen = True
        gamemessages.message('You dropped a ' + self.owner.name + '.', libtcod.yellow)
 
    def use(self):

        #just call the "use_function" if it is defined
        if self.use_function is None:
            gamemessages.message('The ' + self.owner.name + ' cannot be used.')
        else:
            if self.use_function(self.power1, self.power2, self.power3) != 'cancelled':
                inventory.remove(self.owner)  #destroy after use, unless it was cancelled for some reason
 

# The player basically
class Elemental:
	def __init__(self, hp, mana, defence, power, xp, death_function=None):
		self.base_max_hp = hp
		self.hp = hp
		self.base_max_mana = mana
		self.mana = mana
		self.base_defence = defence
		self.base_power = power
		self.xp = xp
		self.death_function = death_function

		self.air = 0
		self.spirit = 0
		self.water = 0
		self.fire = 0
		self.earth = 0

	@property
	def el_power(self):  #return total power of all schools
		elp = self.air + self.spirit + self.water + self.fire + self.earth
		if elp == 0:
			elp =1
		return elp

	@property
	def power(self):  #return actual power, by summing up the bonuses from all bonus effects
		bonus = 0#sum(equipment.power_bonus for equipment in get_all_equipped(self.owner))
		return self.base_power + bonus

	@property
	def defence(self):  #return actual defence, by summing up the bonuses from all bonus effects
		bonus = 0#sum(equipment.defence_bonus for equipment in get_all_equipped(self.owner))
		return self.base_defence + bonus

	@property
	def max_hp(self):  #return actual max_hp, by summing up the bonuses from all bonus effects
		bonus = 0#sum(equipment.max_hp_bonus for equipment in get_all_equipped(self.owner))
		return self.base_max_hp + bonus
	@property
	def max_mana(self):  #return actual max_hp, by summing up the bonuses from all bonus effects
		bonus = 0#sum(equipment.max_hp_bonus for equipment in get_all_equipped(self.owner))
		return self.base_max_mana + bonus

	@property
	def dice(self):  #dice, based on 3 + level bonus
		bonus = math.ceil(self.owner.level /3)
		return int(3 + bonus)
	
	def find_greatest_power(self):
		lst = [self.air, self.spirit, self.water, self.fire,  self.earth]
		id = max((x,i) for i,x in enumerate(lst))[1]
		sm = 0
		for vl in lst:
			if vl == lst[id]:
				sm += 1
		if sm > 1:
			return 'nutr'
		elif id == 0:
			return 'air'
		elif id == 1:
			return 'spirit'
		elif id == 2:
			return 'water'
		elif id == 3:
			return 'fire'
		elif id == 4:
			return 'earth'
		else:
			return 'nutr'

	def add_el_power(self, pwr, amt):
		if pwr == 'air':
			self.air += amt
			gamemessages.message('You feel more in tune with the Realm of Air.', config.color_air_cr)
		elif pwr == 'spirit':
			self.spirit += amt
			gamemessages.message('You feel more in tune with the Realm of Spirit.', config.color_spirit_cr)
		elif pwr == 'water':
			self.water += amt
			gamemessages.message('You feel more in tune with the Realm of Water.', config.color_water_cr)
		elif pwr == 'fire':
			self.fire += amt
			gamemessages.message('You feel more in tune with the Realm of Fire.', config.color_fire_cr)
		elif pwr == 'earth':
			self.earth += amt
			gamemessages.message('You feel more in tune with the Realm of Earth.', config.color_earth_cr)

	def place_star(self):
		
		#find center
		#star cords 16,5 - 40,29
		# width = 25, height = 25
		tot = float(self.el_power)
		if tot < 100.0:
			tot = 100.0
		step = 12.0 / tot
		#print str(step)
		center_x = 13.0
		center_y = 13.0
		
		#air - up / left
		center_x = center_x - (self.air * step)
		center_y = center_y - (self.air * step)

		#spirit - up / right
		center_x = center_x + (self.spirit * step)
		center_y = center_y - (self.spirit * step)
		
		#water - down/2 / right
		center_x = center_x + (self.water * step)
		center_y = center_y + ((self.water * step)/2)
		#fire - down
		#center_x = center_x + (self.water * step)
		center_y = center_y + (self.fire * step)
		#earth - down/2 / left
		center_x = center_x - (self.earth * step)
		center_y = center_y + ((self.earth * step)/2)
		center_x = int(round(center_x, 0))+15
		center_y = int(round(center_y, 0))+4

		#print str(center_x)
		#print str(center_y)

		color = self.find_greatest_power()
		#print str(eval('config.color_'+color+'_cr'))

		libtcod.console_set_default_foreground(gamescreen.elm, eval('config.color_'+color+'_cr'))
		libtcod.console_put_char(gamescreen.elm, center_x, center_y-1, 10, libtcod.BKGND_NONE)
		libtcod.console_put_char(gamescreen.elm, center_x-1, center_y, 13, libtcod.BKGND_NONE)
		libtcod.console_put_char(gamescreen.elm, center_x, center_y, 9, libtcod.BKGND_NONE)
		libtcod.console_put_char(gamescreen.elm, center_x+1, center_y, 11, libtcod.BKGND_NONE)
		libtcod.console_put_char(gamescreen.elm, center_x, center_y+1, 12, libtcod.BKGND_NONE)

	def attack(self, target):
		
		# attack using the strongest school of power
		
		#base damage
		dmg_mult = libtcod.random_get_int(0, 50, (self.dice*100))
		dmg = math.floor( (self.power * dmg_mult)/100)

		#base enemy defence 
		den_mult = libtcod.random_get_int(0, 25, (target.fighter.dice*100))
		den = math.floor( (target.fighter.defence * den_mult)/100)
	
		#elemental attack/defence
		eldmg = 0
		pwrtype = self.find_greatest_power()
		if pwrtype is not 'nutr':
			defpw = eval('target.fighter.res_'+pwrtype)
			atpw = round(((eval('self.'+pwrtype)+25.0)/25),0)
			eldmg = atpw - defpw
			if eldmg > 20:
				eldmg = 20
			if eldmg < 0:
				eldmg =0
			eldmg = math.floor( (eldmg * dmg_mult)/100)
		damage = int(dmg - den + eldmg)
		if damage > 0:
			#make the target take some damage
			gamemessages.message(self.owner.name.capitalize() + ' attacks ' + target.name + ' for ' + str(damage) + ' hit points.')
			target.fighter.take_damage(damage, self.owner)
		else:
			gamemessages.message(self.owner.name.capitalize() + ' attacks ' + target.name + ' but it has no effect!')

	def take_damage(self, damage, attacker):
		#apply damage if possible
		if damage > 0:
			self.hp -= damage

		#check for death. if there's a death function, call it
		if self.hp <= 0:
			function = self.death_function
			if function is not None:
				function(self.owner)

	def heal(self, amount):
		#heal by the given amount, without going over the maximum
		self.hp += amount
		if self.hp > self.max_hp:
			self.hp = self.max_hp
	def heal_mana(self, amount):
		#heal by the given amount, without going over the maximum
		self.mana += amount
		if self.mana > self.max_mana:
			self.mana = self.max_mana

	@property
	def air_spell(self):  #return air spell name
		if self.air >= 1 and self.air <=25:
			return 'Puff'
		elif self.air >= 26 and self.air <=50:
			return 'Wind'
		elif self.air >= 51:
			return 'Tornado'
		else:
			return ' [ None ] '
	@property
	def spirit_spell(self):  #return spirit spell name
		if self.spirit >= 1 and self.spirit <=25:
			return 'Suggestion'
		elif self.spirit >= 26 and self.spirit <=50:
			return 'Confusion'
		elif self.spirit >= 51:
			return 'Insanity'
		else:
			return ' [ None ] '
	@property
	def water_spell(self):  #return water spell name
		if self.water >= 1 and self.water <=25:
			return 'Drip'
		elif self.water >= 26 and self.water <=50:
			return 'Flood'
		elif self.water >= 51:
			return 'Torrent'
		else:
			return ' [ None ] '
	@property
	def fire_spell(self):  #return fire spell name
		if self.fire >= 1 and self.fire <=25:
			return 'Spark'
		elif self.fire >= 26 and self.fire <=50:
			return 'Flame'
		elif self.fire >= 51:
			return 'Inferno'
		else:
			return ' [ None ] '
	@property
	def earth_spell(self):  #return earth spell name
		if self.earth >= 1 and self.earth <=25:
			return 'Hail of Pebbles'
		elif self.earth >= 26 and self.earth <=50:
			return 'Falling Rocks'
		elif self.earth >= 51:
			return 'Toss Boulder'
		else:
			return ' [ None ] '
	
	#Spell Schools
	def cast_air(self):
		#Air School
		#tier 1 (Puff - blow 1 enemy) (3 - 20 Air dmg x 1 target / move 1-3 squares back)
		did_turn = False
		mana_burn = int(round((self.air / 4 * self.owner.level), 0))+5
		print 'Using Mana:'+str(mana_burn)
		if self.mana >= mana_burn:
			if self.air >= 1 and self.air <=25:
				p1 = int(round(self.air * 1.65, 0))
				p2 = int(round(((self.air * .08)*(self.air * .08)), 0))
				if p1 < 3:
					p1 = 3
				if p1 > 20:
					p1 = 20
				if p2 < 1:
					p2 = 1
				if p2 > 3:
					p2 = 3
				did_turn = gamespells.cast_puff(p1, p2)
			#tier 2 (Wind - blow x squares around you) (15 - 30 air dmg x Targets in 1 - 4 squares of caster / move 1-3 squares back)
			elif self.air >= 26 and self.air <=50:
				p1 = int(round((self.air * .13)*(self.air * .13), 0))
				p2 = int(round(((self.air * .038)*(self.air * .038)), 0))
				p3 = p2
				# blow dmg
				if p1 < 15:
					p1 = 15
				if p1 > 40:
					p1 = 40
				# blow radius
				if p2 < 1:
					p2 = 1
				if p2 > 4:
					p2 = 4
				# blow range
				if p3 < 1:
					p3 = 1
				if p3 > 3:
					p3 = 3
				did_turn = gamespells.cast_wind(p1, p2, p3)
			#tier 3 (Tornado - blow x squares around target) (15 - 30 air dmg x Targets in 1 - 4 squares of pointer / move 1-3 squares back)
			elif self.air >= 51:
				p1 = int(round((self.air * .13)*(self.air * .13), 0))
				p2 = int(round(((self.air * .019)*(self.air * .019)), 0))+1
				p3 = int(round(((self.air * .019)*(self.air * .019)), 0))
				# blow dmg
				if p1 < 35:
					p1 = 35
				if p1 > 80:
					p1 = 80
				# blow radius
				if p2 < 2:
					p2 = 2
				if p2 > 5:
					p2 = 5
				# blow range
				if p3 < 1:
					p3 = 1
				if p3 > 3:
					p3 = 3
				did_turn = gamespells.cast_tornado(p1, p2, p3)
			#they don't have fire powers
			else:
				gamemessages.message('You don\'t have a connection to the Realm of Air!  Absorb some Essence Crystals to create a connection.', libtcod.dark_orange)
			if did_turn:
				self.mana -= mana_burn
			return did_turn
		else:
			gamemessages.message('You don\'t have enough Mana to cast an Air Spell!  Absorb some Essence Crystals to increase your mana.', libtcod.dark_orange)
			return False
		return False
	def cast_spirit(self):
		#Spirit School
		#tier 1 (Suggestion)
		did_turn = False
		mana_burn = int(round((self.spirit / 4 * self.owner.level), 0))+5
		print 'Using Mana:'+str(mana_burn)
		if self.mana >= mana_burn:
			if self.spirit >= 1 and self.spirit <=25:
				p1 = int(round(self.spirit * 1.65, 0))
				p2 = int(round(((self.spirit * .08)*(self.spirit * .08)), 0))
				if p1 < 3:
					p1 = 3
				if p1 > 20:
					p1 = 20
				if p2 < 1:
					p2 = 1
				if p2 > 3:
					p2 = 3
				did_turn = gamespells.cast_suggestion(p1, p2+1)
			#tier 2 (confusion)
			elif self.spirit >= 26 and self.spirit <=50:
				p1 = int(round((self.spirit * .13)*(self.spirit * .13), 0))
				p2 = int(round(((self.spirit * .038)*(self.spirit * .038)), 0))
				p3 = p2
				# blow dmg
				if p1 < 15:
					p1 = 15
				if p1 > 40:
					p1 = 40
				# blow radius
				if p2 < 1:
					p2 = 1
				if p2 > 4:
					p2 = 4
				# blow range
				if p3 < 1:
					p3 = 1
				if p3 > 3:
					p3 = 3
				did_turn = gamespells.cast_confusion(p1, p2, p3+2)
			#tier 3 (Insanity)
			elif self.spirit >= 51:
				p1 = int(round((self.spirit * .13)*(self.spirit * .13), 0))
				p2 = int(round(((self.spirit * .019)*(self.spirit * .019)), 0))+1
				p3 = int(round(((self.spirit * .019)*(self.spirit * .019)), 0))
				# blow dmg
				if p1 < 35:
					p1 = 35
				if p1 > 80:
					p1 = 80
				# blow radius
				if p2 < 2:
					p2 = 2
				if p2 > 5:
					p2 = 5
				# blow range
				if p3 < 1:
					p3 = 1
				if p3 > 3:
					p3 = 3
				did_turn = gamespells.cast_insanity(p1, p2, p3+3)
			#they don't have spirit powers
			else:
				gamemessages.message('You don\'t have a connection to the Realm of Spirit!  Absorb some Essence Crystals to create a connection.', libtcod.dark_orange)
			if did_turn:
				self.mana -= mana_burn
			return did_turn
		else:
			gamemessages.message('You don\'t have enough Mana to cast a Spirit Spell!  Absorb some Essence Crystals to increase your mana.', libtcod.dark_orange)
			return False
	def cast_water(self):
		#Water School
		#tier 1 (Drip - mimics Spirit Suggestion)
		did_turn = False
		mana_burn = int(round((self.water / 4 * self.owner.level), 0))+5
		print 'Using Mana:'+str(mana_burn)
		if self.mana >= mana_burn:
			if self.water >= 1 and self.water <=25:
				p1 = int(round(self.water * 1.65, 0))
				p2 = int(round(((self.water * .08)*(self.water * .08)), 0))
				if p1 < 3:
					p1 = 3
				if p1 > 20:
					p1 = 20
				if p2 < 1:
					p2 = 1
				if p2 > 3:
					p2 = 3
				did_turn = gamespells.cast_drip(p1, p2+1)
			#tier 2 (Flood - mimics Air Wind)
			elif self.water >= 26 and self.water <=50:
				p1 = int(round((self.water * .13)*(self.water * .13), 0))
				p2 = int(round(((self.water * .038)*(self.water * .038)), 0))
				p3 = p2
				# blow dmg
				if p1 < 15:
					p1 = 15
				if p1 > 40:
					p1 = 40
				# blow radius
				if p2 < 1:
					p2 = 1
				if p2 > 4:
					p2 = 4
				# blow range
				if p3 < 1:
					p3 = 1
				if p3 > 3:
					p3 = 3
				did_turn = gamespells.cast_flood(p1, p2, p3)
			#tier 3 (Torrent - mimics Earth Boulder)
			elif self.water >= 51:
				p1 = int(round((self.water * .13)*(self.water * .13), 0))
				p2 = int(round(((self.water * .019)*(self.water * .019)), 0))+1
				p3 = int(round(((self.water * .019)*(self.water * .019)), 0))
				# blow dmg
				if p1 < 35:
					p1 = 35
				if p1 > 80:
					p1 = 80
				# blow radius
				if p2 < 2:
					p2 = 2
				if p2 > 5:
					p2 = 5
				# blow range
				if p3 < 1:
					p3 = 1
				if p3 > 3:
					p3 = 3
				did_turn = gamespells.cast_torrent(p1, p2, p3+3)
			#they don't have Water powers
			else:
				gamemessages.message('You don\'t have a connection to the Realm of Water!  Absorb some Essence Crystals to create a connection.', libtcod.dark_orange)
			if did_turn:
				self.mana -= mana_burn
			return did_turn
		else:
			gamemessages.message('You don\'t have enough Mana to cast a Water Spell!  Absorb some Essence Crystals to increase your mana.', libtcod.dark_orange)
			return False

	def cast_fire(self):
		#Fire School
		#tier 1 (Ember - burn 1 enemy) (5 - 30 flame dmg x 1 target)
		did_turn = False
		mana_burn = int(round((self.fire / 4 * self.owner.level), 0))+5
		print 'Using Mana:'+str(mana_burn)
		if self.mana >= mana_burn:
			if self.fire >= 1 and self.fire <=25:
				p1 = self.fire*2
				if p1 < 5:
					p1 = 5
				if p1 > 30:
					p1 = 30
				did_turn = gamespells.cast_spark(p1, 15)
			#tier 2 (flame - burn x squares around you) (25 - 40 flame dmg x Targets in 1 - 4 squares of caster)
			elif self.fire >= 26 and self.fire <=50:
				p1 = int(self.fire * .85)
				p2 = int(round(((self.fire * .038)*(self.fire * .038)), 0))
				if p1 < 25:
					p1 = 25
				if p1 > 40:
					p1 = 40
				if p2 < 1:
					p2 = 1
				if p2 > 4:
					p2 = 4
				did_turn = gamespells.cast_flame(p1, p2)
			#tier 3 (fireball - burn x squares around a target)
			elif self.fire >= 51:
				p1 = int(self.fire * .85)
				p2 = int(self.fire * .062)
				if p1 < 35:
					p1 = 5
				if p1 > 60:
					p1 = 30
				if p2 < 3:
					p2 = 3
				if p2 > 6:
					p2 = 6
				did_turn = gamespells.cast_fireball(p1, p2)
			#they don't have fire powers
			else:
				gamemessages.message('You don\'t have a connection to the Realm of Fire!  Absorb some Essence Crystals to create a connection.', libtcod.dark_orange)
			if did_turn:
				self.mana -= mana_burn
			return did_turn
		else:
			gamemessages.message('You don\'t have enough Mana to cast a Fire Spell!  Absorb some Essence Crystals to increase your mana.', libtcod.dark_orange)
			return False
	
	def cast_earth(self):
		#Earth School
		#tier 1 (Pebble - hit 1 enemy) (3 - 20 Earth dmg x 1 target / rooted 1-3 turns)
		did_turn = False
		mana_burn = int(round((self.earth / 4 * self.owner.level), 0))+5
		print 'Using Mana:'+str(mana_burn)
		if self.mana >= mana_burn:
			if self.earth >= 1 and self.earth <=25:
				p1 = int(round(self.earth * 1.65, 0))
				p2 = int(round(((self.earth * .08)*(self.earth * .08)), 0))
				if p1 < 3:
					p1 = 3
				if p1 > 20:
					p1 = 20
				if p2 < 1:
					p2 = 1
				if p2 > 3:
					p2 = 3
				did_turn = gamespells.cast_pebble(p1, p2+1)
			#tier 2 (Rock - hit x squares around you) (15 - 30 earth dmg x Targets in 1 - 4 squares of caster / rooted 1-3 turns)
			elif self.earth >= 26 and self.earth <=50:
				p1 = int(round((self.earth * .13)*(self.earth * .13), 0))
				p2 = int(round(((self.earth * .038)*(self.earth * .038)), 0))
				p3 = p2
				# blow dmg
				if p1 < 15:
					p1 = 15
				if p1 > 40:
					p1 = 40
				# blow radius
				if p2 < 1:
					p2 = 1
				if p2 > 4:
					p2 = 4
				# blow range
				if p3 < 1:
					p3 = 1
				if p3 > 3:
					p3 = 3
				did_turn = gamespells.cast_rock(p1, p2, p3+2)
			#tier 3 (Tornado - blow x squares around target) (15 - 30 air dmg x Targets in 1 - 4 squares of pointer / move 1-3 squares back)
			elif self.earth >= 51:
				p1 = int(round((self.earth * .13)*(self.earth * .13), 0))
				p2 = int(round(((self.earth * .019)*(self.earth * .019)), 0))+1
				p3 = int(round(((self.earth * .019)*(self.earth * .019)), 0))
				# blow dmg
				if p1 < 35:
					p1 = 35
				if p1 > 80:
					p1 = 80
				# blow radius
				if p2 < 2:
					p2 = 2
				if p2 > 5:
					p2 = 5
				# blow range
				if p3 < 1:
					p3 = 1
				if p3 > 3:
					p3 = 3
				did_turn = gamespells.cast_boulder(p1, p2, p3+3)
			#they don't have fire powers
			else:
				gamemessages.message('You don\'t have a connection to the Realm of Earth!  Absorb some Essence Crystals to create a connection.', libtcod.dark_orange)
			if did_turn:
				self.mana -= mana_burn
			return did_turn
		else:
			gamemessages.message('You don\'t have enough Mana to cast an Earth Spell!  Absorb some Essence Crystals to increase your mana.', libtcod.dark_orange)
			return False



class MagePet:
	#combat-related properties and methods (monster, player, NPC).
	def __init__(self, hp, mana, defence, power, xp, death_function=None):
		self.base_max_hp = hp
		self.hp = hp
		self.base_max_mana = mana
		self.mana = mana
		self.base_defence = defence
		self.base_power = power
		self.xp = xp
		self.rooted = 0
		self.death_function = death_function


	@property
	def power(self):  #return actual power, by summing up the bonuses from all equipped items
		bonus = 0#sum(equipment.power_bonus for equipment in get_all_equipped(self.owner))
		return math.ceil(self.owner.level / 2) #self.base_power + bonus

	@property
	def defence(self):  #return actual defence, by summing up the bonuses from all equipped items
		bonus = 0#sum(equipment.defence_bonus for equipment in get_all_equipped(self.owner))
		return math.ceil(self.owner.level / 3)#self.base_defence + bonus

	@property
	def max_hp(self):  #return actual max_hp, by summing up the bonuses from all equipped items
		bonus = 0#sum(equipment.max_hp_bonus for equipment in get_all_equipped(self.owner))
		return self.base_max_hp + bonus
	@property
	def max_mana(self):  #return actual max_hp, by summing up the bonuses from all bonus effects
		bonus = 0#sum(equipment.max_hp_bonus for equipment in get_all_equipped(self.owner))
		return self.base_max_mana + bonus

	@property
	def dice(self):  #dice, based on 3 + level bonus
		bonus = math.ceil(self.owner.level /3)
		return int(1 + bonus)


	def attack(self, target):
		#a simple formula for attack damage
		
		#=FLOOR( ((CEILING(AH2/2, 1)*(1+CEILING(AH2/3, 1))*100)/100), 1)

		dmg_mult = libtcod.random_get_int(0, 50, (self.dice*100))
		dmg = math.floor( (self.power * dmg_mult)/100)
		den_mult = libtcod.random_get_int(0, 25, (target.fighter.dice*100))
		den = math.floor( (target.fighter.defence * den_mult)/100)

		damage = int(dmg - den)

		if damage > 0:
			#make the target take some damage
			gamemessages.message(self.owner.name + ' attacks ' + target.name + ' for ' + str(damage) + ' hit points.')
			target.fighter.take_damage(damage, self.owner)
		else:
			gamemessages.message(self.owner.name + ' attacks ' + target.name + ' but it has no effect!')

	def take_damage(self, damage, attacker):
		#attack attempt was made, they are now aggressive
		self.owner.ai.was_attacked = True
		#apply damage if possible
		if damage > 0:
			self.hp -= damage

		#check for death. if there's a death function, call it
		if self.hp <= 0:
			function = self.death_function
			if function is not None:
				function(self.owner)

	def heal(self, amount):
		#heal by the given amount, without going over the maximum
		self.hp += amount
		if self.hp > self.max_hp:
			self.hp = self.max_hp
	def heal_mana(self, amount):
		#heal by the given amount, without going over the maximum
		self.mana += amount
		if self.mana > self.max_mana:
			self.mana = self.max_mana

class MageDumb:
	def __init__(self):
		self.path = None
		self.was_attacked = False
		self.is_giving_chase = False
		self.chase_range = 15
		self.base_chase_dist = 100
		self.chase_dist = 100
		self.orig_x = 0
		self.orig_y = 0
		self.move_to_home = False
		self.mage_thoughts = 'Wonder what we\'ll find in this dungeon...'
		self.cur_target = None
		self.wait_stairs = 0
		#force him to explore a bit before going down stairs...
		self.mage_min_moves_floor = 400

	def take_turn(self):

		#TODO: Mage run when hurt
		self.mage_min_moves_floor -= 1
		if self.path is None:
			self.path = libtcod.path_new_using_map(gamescreen.fov_map)
		
		vis_targets = []
		#can he see an enemy?
		for object in objects:
			if object.fighter and not isinstance(object.fighter, Elemental) and not isinstance(object.fighter, MagePet) and libtcod.map_is_in_fov(gamescreen.fov_map_mage, object.x, object.y):
				vis_targets.append(object)
		
		if mage.fighter.mana > 10 and mage.fighter.hp < 20:
			#cast heal
			heal_mult = libtcod.random_get_int(0, 0, (self.owner.fighter.dice*100))
			heal = math.floor( ((self.owner.level*2) * heal_mult)/100)+5
			gamespells.cast_heal(heal)
			self.owner.fighter.mana -= 10
			
		elif len(vis_targets) > 0:
			print 'Can See:'
			for vt in vis_targets:
				print '  '+vt.name
			target = closest_monster_mage(self.chase_range)
			self.mage_thoughts = 'Look at that '+target.name+'.\nI should kill it!'
			
			
			if len(vis_targets) > 1 and mage.fighter.mana > 30:
				#multi targets and lots of mana, cast lightning storm
				dmg_mult = libtcod.random_get_int(0, 0, (self.owner.fighter.dice*100))
				dmg = math.floor( ((self.owner.level*3) * dmg_mult)/100)+2
				gamespells.cast_lightning(dmg, vis_targets)
				self.owner.fighter.mana -= 20
			elif len(vis_targets) == 1 and mage.fighter.mana > 20 and libtcod.random_get_int(0, 0, 10) > 7:
				if libtcod.random_get_int(0, 0, 1) > 1:
					#single target, good mana cast zap
					dmg_mult = libtcod.random_get_int(0, 0, (self.owner.fighter.dice*100))
					dmg = math.floor( ((self.owner.level*4) * dmg_mult)/100)+5
					gamespells.cast_zap(dmg, vis_targets)
					self.owner.fighter.mana -= 10
				elif not isinstance(vis_targets[0].ai, ConfusedMonster):
					#single target, good mana confuse them
					dmg = math.ceil((self.owner.level/4))+1
					gamespells.cast_confuse(dmg, vis_targets)
					self.owner.fighter.mana -= 10
				

			else:
				#move towards target if far away
				if gameinput.path_recalc:
					libtcod.path_compute(self.path, mage.x, mage.y, target.x, target.y)

				if mage.distance_to(target) >= 2 and mage.fighter.rooted < 1:
					path_px, path_py = libtcod.path_walk(self.path, True)
					if path_px is not None and path_py is not None:
						mage.move_towards(path_px, path_py)
						self.chase_dist -= 1
				#close enough, attack! (if the target is still alive.)
				elif target.fighter.hp > 0 and mage.distance_to(target) < 2:
					mage.fighter.attack(target)
					#they're fighting, so he'll chase further
					self.chase_dist += 2
					self.mage_thoughts = 'I\'m gonna get this '+target.name+'!'
		#just wander
		else:
			if self.mage_min_moves_floor > 0:
				#still need to explore some
				#choose some random unblocked location
				#in the northern area
				random_x = libtcod.random_get_int(0, (mage.x - 30), (mage.x + 30))
				random_y = libtcod.random_get_int(0, (mage.y - 30), (mage.y + 30))
				
				if random_x > config.MAP_WIDTH-5:
					random_x = config.MAP_WIDTH-5
				elif random_x < 5:
					random_x = 5
				if random_y > config.MAP_HEIGHT-5:
					random_y = config.MAP_HEIGHT-5
				elif random_y < 5:
					random_y = 5
				if self.cur_target is None or mage.distance_to(self.cur_target) < 5:
					#use the bsp map if still available
					if gamemap.bsp is not None:
						node = libtcod.bsp_find_node(gamemap.bsp, random_x, random_y )
						sx = libtcod.random_get_int(0, node.x, node.x+node.w-1)
						sy = libtcod.random_get_int(0, node.y, node.y+node.h-1)
						self.cur_target = TargetLoc(sx, sy)

						while not libtcod.bsp_is_leaf(node):
							random_x = libtcod.random_get_int(0, (mage.x - 30), (mage.x + 30))
							random_y = libtcod.random_get_int(0, (mage.y - 30), (mage.y + 30))
							if random_x > config.MAP_WIDTH-5:
								random_x = config.MAP_WIDTH-5
							elif random_x < 5:
								random_x = 5
							if random_y > config.MAP_HEIGHT-5:
								random_y = config.MAP_HEIGHT-5
							elif random_y < 5:
								random_y = 5
							node = libtcod.bsp_find_node(gamemap.bsp, random_x, random_y )
							sx = libtcod.random_get_int(0, node.x, node.x+node.w-1)
							sy = libtcod.random_get_int(0, node.y, node.y+node.h-1)
							self.cur_target = TargetLoc(sx, sy)
					else:
						random_x = libtcod.random_get_int(0, (mage.x - 50), (mage.x + 50))
						random_y = libtcod.random_get_int(0, (mage.y - 50), (mage.y + 50))
						if random_x > config.MAP_WIDTH-5:
							random_x = config.MAP_WIDTH-5
						elif random_x < 5:
							random_x = 5
						if random_y > config.MAP_HEIGHT-5:
							random_y = config.MAP_HEIGHT-5
						elif random_y < 5:
							random_y = 5
						while gamemap.is_blocked(random_x, random_y):
							random_x = libtcod.random_get_int(0, (mage.x - 50), (mage.x + 50))
							random_y = libtcod.random_get_int(0, (mage.y - 50), (mage.y + 50))
							if random_x > config.MAP_WIDTH-5:
								random_x = config.MAP_WIDTH-5
							elif random_x < 5:
								random_x = 5
							if random_y > config.MAP_HEIGHT-5:
								random_y = config.MAP_HEIGHT-5
							elif random_y < 5:
								random_y = 5
						self.cur_target = TargetLoc(random_x, random_y)

				
				self.mage_thoughts = 'Lets explore this floor a bit more... '
				
				
			
			else:
				#they've looked around enough, lets have them wander in the direction of the closest stairs
				self.cur_target = closest_stairs(mage.x, mage.y)
				self.mage_thoughts = 'Hmmm... I wonder where the stairs are...'
			
			
			if gameinput.path_recalc:
				libtcod.path_compute(self.path, mage.x, mage.y, self.cur_target.x, self.cur_target.y)			
			#move towards stairs
			if mage.distance_to(self.cur_target) >= 1 and mage.fighter.rooted < 1:
				path_px, path_py = libtcod.path_walk(self.path, True)
				if path_px is not None and path_py is not None:
					mage.move_towards(path_px, path_py)
			elif mage.distance_to(self.cur_target) < 1 and self.cur_target == closest_stairs(mage.x, mage.y):
				#go down?
				self.wait_stairs +=1
				self.mage_thoughts = 'Oh Look!  There\'s The Stairs!  Lets go Deeper!'
				if self.wait_stairs > 1:
					#down we go
					self.cur_target = None
					self.wait_stairs = 0
					#force him to explore a bit before going down stairs...
					self.mage_min_moves_floor = 400
					gameactions.next_level()
		#print self.mage_thoughts
		

			

		


		



class MonsterFighter:
	#combat-related properties and methods (monster, player, NPC).
	def __init__(self, hp, defence, power, xp, dice=4, death_function=None, essence=1, res_air=0, res_spirit=0, res_water=0, res_fire=0, res_earth=0):
		self.base_max_hp = hp
		self.hp = hp
		self.base_defence = defence
		self.base_power = power
		self.xp = xp
		self.dice = dice
		self.essence = essence
		self.rooted = 0
		self.death_function = death_function
		self.res_air=res_air
		self.res_spirit=res_spirit
		self.res_water=res_water
		self.res_fire=res_fire
		self.res_earth=res_earth

	@property
	def power(self):  #return actual power, by summing up the bonuses from all equipped items
		bonus = 0#sum(equipment.power_bonus for equipment in get_all_equipped(self.owner))
		return self.base_power + bonus

	@property
	def defence(self):  #return actual defence, by summing up the bonuses from all equipped items
		bonus = 0#sum(equipment.defence_bonus for equipment in get_all_equipped(self.owner))
		return self.base_defence + bonus

	@property
	def max_hp(self):  #return actual max_hp, by summing up the bonuses from all equipped items
		bonus = 0#sum(equipment.max_hp_bonus for equipment in get_all_equipped(self.owner))
		return self.base_max_hp + bonus

	def attack(self, target):
		#a simple formula for attack damage

		dmg_mult = libtcod.random_get_int(0, 50, (self.dice*100))
		dmg = math.floor( (self.power * dmg_mult)/100)
		den_mult = libtcod.random_get_int(0, 25, (target.fighter.dice*100))
		den = math.floor( (target.fighter.defence * den_mult)/100)

		damage = int(dmg - den)

		if damage > 0:
			#make the target take some damage
			gamemessages.message(self.owner.name + ' attacks ' + target.name + ' for ' + str(damage) + ' hit points.')
			target.fighter.take_damage(damage, self.owner)
		else:
			gamemessages.message(self.owner.name + ' attacks ' + target.name + ' but it has no effect!')

	def take_damage(self, damage, attacker):
		#attack attempt was made, they are now aggressive
		self.owner.ai.was_attacked = True
		#and they'll attack the person who tried to attack them last
		self.owner.ai.attack_target = attacker
		#apply damage if possible
		if damage > 0:
			self.hp -= damage

		#check for death. if there's a death function, call it
		if self.hp <= 0:
			function = self.death_function
			if attacker == player:  #yield experience to the player
				player.fighter.xp += self.xp
				if function is not None:
					function(self.owner, True)
			elif function is not None:
				function(self.owner, False)
				

	def heal(self, amount):
		#heal by the given amount, without going over the maximum
		self.hp += amount
		if self.hp > self.max_hp:
			self.hp = self.max_hp

class BasicMonster:
	def take_turn(self):
		monster = self.owner
		if libtcod.map_is_in_fov(gamescreen.fov_map, monster.x, monster.y):

			#move towards player if far away
			if monster.distance_to(player) >= 2:
				monster.move_towards(player.x, player.y)

			#close enough, attack! (if the player is still alive.)
			elif player.fighter.hp > 0:
				monster.fighter.attack(player)


class ChaseMonster:
	def __init__(self, seen_player=False, chase_range=20, chase_dist=100):
		self.seen_player = seen_player
		self.seen_mage = False
		self.path = None
		self.was_attacked = False
		self.is_giving_chase = False
		self.attack_target = None
		self.chase_range = chase_range
		self.base_chase_dist = chase_dist
		self.chase_dist = chase_dist
		self.orig_x = 0
		self.orig_y = 0
		self.move_to_home = False

	def take_turn(self):
		#TODO: Monster run when hurt
		monster = self.owner
		if self.path is None:
			self.path = libtcod.path_new_using_map(gamescreen.fov_map)
		
		if self.orig_x == 0:
			#create home location
			self.orig_x = monster.x
			self.orig_y = monster.y
		
		#check the monsters view range to set seen_player
		if monster.distance_to(player) <= self.chase_range:
			self.seen_player = True

		#player or mage
		if self.attack_target is None:
			self.attack_target = closest_player_or_pet(monster, self.chase_range)

		#chase up to chase_range squares away for a max of chase_dist from starting point
		if (self.attack_target is not None) and ((monster.distance_to(self.attack_target) <= self.chase_range) or (self.was_attacked)) and (self.seen_player or self.seen_mage) and self.chase_dist >= 1 and not self.move_to_home:
			#the monster has begun to give chase
			

			if not self.is_giving_chase:
				self.is_giving_chase = True
				if self.attack_target == player:
					gamemessages.message('The ' + monster.name + ' seems to have noticed you.', libtcod.dark_yellow)
				elif self.attack_target == mage:
					gamemessages.message('The ' + monster.name + ' seems to have noticed your mage.', libtcod.dark_yellow)
			#move towards target if far away
			if gameinput.path_recalc:
				libtcod.path_compute(self.path, monster.x, monster.y, self.attack_target.x, self.attack_target.y)
			if monster.distance_to(self.attack_target) >= 2 and monster.fighter.rooted < 1:
				path_px, path_py = libtcod.path_walk(self.path, True)
				if path_px is not None and path_py is not None:
					monster.move_towards(path_px, path_py)
					self.chase_dist -= 1
			#close enough, attack! (if the target is still alive.)
			elif self.attack_target.fighter.hp > 0 and monster.distance_to(self.attack_target) < 2:
				monster.fighter.attack(self.attack_target)
				#they're fighting, so he'll chase further
				self.chase_dist += 2
		elif self.attack_target is not None and self.chase_dist >= 1 and monster.distance_to(self.attack_target) > self.chase_range and not self.move_to_home and self.is_giving_chase:
			if self.attack_target == player:
				gamemessages.message('You seem to lose the ' + monster.name + '.', libtcod.dark_green)
			elif self.attack_target == mage:
				gamemessages.message('Your mage seems to lose the ' + monster.name + '.', libtcod.dark_green)
			self.move_to_home = True
			self.is_giving_chase = False
		elif self.chase_dist < 1 and not self.move_to_home and self.is_giving_chase:
			if self.attack_target == player:
				gamemessages.message('The ' + monster.name + ' seems to lose interest in persuing you and begins to wander back to its home.', libtcod.dark_green)
			elif self.attack_target == mage:
				gamemessages.message('The ' + monster.name + ' seems to lose interest in persuing your mage and begins to wander back to its home.', libtcod.dark_green)

			self.move_to_home = True
			self.is_giving_chase = False
		elif self.move_to_home:
			if gameinput.path_recalc:
				libtcod.path_compute(self.path, monster.x, monster.y, self.orig_x, self.orig_y)
			path_px, path_py = libtcod.path_walk(self.path, True)
			if path_px is not None and path_py is not None:
				monster.move_towards(path_px, path_py)
			elif path_px == monster.x and path_py == monster.y:
				#gamemessages.message('The ' + monster.name + ' is home.', libtcod.dark_blue)
				self.was_attacked = False
				self.move_to_home = False
				self.seen_player = False
				self.chase_dist = self.base_chase_dist
			else:
				#gamemessages.message('The ' + monster.name + ' is home.', libtcod.dark_blue)
				self.was_attacked = False
				self.move_to_home = False
				self.seen_player = False
				self.chase_dist = self.base_chase_dist
		if monster.fighter.rooted > 0:
			monster.fighter.rooted -= 1
			


class ConfusedMonster:
    #AI for a temporarily confused monster (reverts to previous AI after a while).
    def __init__(self, old_ai, num_turns=6):
        self.old_ai = old_ai
        self.num_turns = num_turns
 
    def take_turn(self):
        if self.num_turns > 0:  #still confused...
            #move in a random direction, and decrease the number of turns confused
			dx = libtcod.random_get_int(0, -1, 1)
			dy = libtcod.random_get_int(0, -1, 1)
			
			#try to find an attackable object there
			target = None
			for object in objects:
				if object.fighter and object.x == self.owner.x + dx and object.y == self.owner.y + dy:
					target = object
					break
			#attack
			if target is not None:
				self.owner.fighter.attack(target)
			elif gamemap.is_blocked(self.owner.x + dx, self.owner.y + dy):
				gamemessages.message('The ' + self.owner.name + ' stumbles into the wall!', libtcod.red)
			else:
				self.owner.move(dx, dy)
			self.num_turns -= 1
 
        else:  #restore the previous AI (this one will be deleted because it's not referenced anymore)
            self.owner.ai = self.old_ai
            gamemessages.message('The ' + self.owner.name + ' is no longer confused!', libtcod.red)
 
def check_level_up():
	#see if the player's experience is enough to level-up
	level_up_xp = config.LEVEL_UP_BASE + player.level * config.LEVEL_UP_FACTOR
	if player.fighter.xp >= level_up_xp:
		#it is! level up and ask to raise some stats
		player.level += 1
		player.fighter.xp -= level_up_xp
		gamemessages.message('Your connection with this Realm grows stronger! You reached level ' + str(player.level) + '!', libtcod.yellow)

		mage.level += 1
		gamemessages.message('You notice that your mage seems to have grown stronger as well!!', libtcod.yellow)
		mage.fighter.base_max_hp += 5
		mage.fighter.hp += 5
		mage.fighter.base_max_mana += 6
		mage.fighter.mana += 6
		mage.fighter.heal((4 * mage.level-1))
		mage.fighter.heal_mana((4 * mage.level-1))

		choice = None
		while choice == None:  #keep asking until a choice is made
			choice = gamescreen.menu('Level up! Choose a Plannar Realm Connection to Strengthen:\n',
				['Physical Connetion (+12 HP, from ' + str(player.fighter.max_hp) + ')',
				'Mental Connection (+12 Mana, from ' + str(player.fighter.max_mana) + ')'], 50)

		if choice == 0:
			player.fighter.base_max_hp += 12
			player.fighter.hp += 12
		elif choice == 1:
			player.fighter.base_max_mana += 12
			player.fighter.mana += 12
		player.fighter.heal((12 * player.level-1))
		player.fighter.heal_mana((12 * player.level-1))


def player_death(player):
	#the game ended!
	global game_state
	gamemessages.message('You were destroyed.  Your body fades from the physical realm and you are teleported back to the realm of Elementals.', libtcod.red)
	gamemessages.message('After a few seconds, your vision goes blurry again, and you feel yourself pulled back to the Physical Realm.', libtcod.red)
	gamemessages.message('When your vision clears, you see your mage standing next to you. ', libtcod.red)
	gamemessages.message('\"I wasn\'t quite done with you!\" he says, then turns back to his exploration of the Dungeon...', libtcod.red)
	#gameinput.game_state = 'dead'
	
	player.blocks = False
	new_x = libtcod.random_get_int(0, mage.x-1, mage.x+1)
	new_y = libtcod.random_get_int(0, mage.y-1, mage.y+1)
	while gamemap.is_blocked(new_x, new_y):	
		while gamemap.is_blocked(new_x, new_y):
			new_x = libtcod.random_get_int(0, mage.x-2, mage.x+2)
			new_y = libtcod.random_get_int(0, mage.y-2, mage.y+2)
	player.x = new_x
	player.y = new_y	
	player.blocks = True
	player.fighter.hp = player.fighter.max_hp
	player.fighter.mana = player.fighter.max_mana

	player.fighter.air = 0
	player.fighter.spirit = 0
	player.fighter.water = 0
	player.fighter.fire = 0
	player.fighter.earth = 0

	
	gamescreen.initialize_fov()



def mage_death(mage):
	#the game ended!
	global game_state
	gamemessages.message('Your Mage has died!  You have failed!  Press any key...', libtcod.red)
	gameinput.game_state = 'dead'

	#for added effect, transform the player into a corpse!
	mage.char = '%'
	mage.color = libtcod.dark_red
	#every tile gets explored
	for y in range(config.MAP_HEIGHT):
		for x in range(config.MAP_WIDTH):
			gamemap.map[x][y].explored = True
	for object in objects:
		if object != player:
			object.always_visible = True
			object.location_seen = True
	gamescreen.render_all()
	libtcod.console_flush()
	time.sleep(2)
	key = libtcod.console_wait_for_keypress(True)
	
 
def monster_death(monster, killed_by_player=False):
	#transform it into a nasty corpse! it doesn't block, can't be
	#attacked and doesn't move
	if killed_by_player:
		gamemessages.message('The ' + monster.name + ' is dead! You feel as though you understand combat in this plane of existance a little better.', libtcod.orange)
	else:
		gamemessages.message('The ' + monster.name + ' has been killed.', libtcod.orange)
	create_el_essence(monster.fighter.essence, monster.x, monster.y)
	monster.char = '%'
	monster.color = libtcod.dark_red
	monster.blocks = False
	monster.fighter = None
	monster.always_visible = True

	#drop an elemental shard
	gamemessages.message('The ' + monster.name + '\'s elemental essence has dropped to the ground.', libtcod.dark_orange)

	monster.ai = None
	monster.name = 'Remains of ' + monster.name
	monster.send_to_back()




def random_choice_index(chances):  #choose one option from list of chances, returning its index
    #the dice will land on some number between 1 and the sum of the chances
    dice = libtcod.random_get_int(0, 1, sum(chances))
 
    #go through all chances, keeping the sum so far
    running_sum = 0
    choice = 0
    for w in chances:
        running_sum += w
 
        #see if the dice landed in the part that corresponds to this choice
        if dice <= running_sum:
            return choice
        choice += 1
 
def random_choice(chances_dict):
    #choose one option from dictionary of chances, returning its key
    chances = chances_dict.values()
    strings = chances_dict.keys()
 
    return strings[random_choice_index(chances)]
 
def from_dungeon_level(table):
    #returns a value that depends on level. the table specifies what value occurs after each level, default is 0.
    for (value, level) in reversed(table):
        if gamemap.dungeon_level >= level:
            return value
    return 0

def closest_player_or_pet(monster, max_range):
	#find closest enemy, up to a maximum range, and in the player's FOV
	closest_pp = None
	closest_dist = max_range + 1  #start with (slightly more than) maximum range
 
	for object in objects:
		if object == mage or object == player:
			#calculate distance between this object and the player
			dist = monster.distance_to(object)
			if dist < closest_dist:  #it's closer, so remember it
				closest_pp = object
				closest_dist = dist
	return closest_pp

def closest_monster(max_range):
	#find closest enemy, up to a maximum range, and in the player's FOV
	closest_enemy = None
	closest_dist = max_range + 1  #start with (slightly more than) maximum range
 
	for object in objects:
		if object.fighter and not object == player and not object == mage and libtcod.map_is_in_fov(gamescreen.fov_map, object.x, object.y):
			#calculate distance between this object and the player
			dist = player.distance_to(object)
			if dist < closest_dist:  #it's closer, so remember it
				closest_enemy = object
				closest_dist = dist
	return closest_enemy


def closest_monster_mage(max_range):
	#find closest enemy, up to a maximum range, and in the mages's FOV
	closest_enemy = None
	closest_dist = max_range + 1  #start with (slightly more than) maximum range
 
	for object in objects:
		if object.fighter and not object == player and not object == mage and libtcod.map_is_in_fov(gamescreen.fov_map_mage, object.x, object.y):
			#calculate distance between this object and the player
			dist = mage.distance_to(object)
			if dist < closest_dist:  #it's closer, so remember it
				closest_enemy = object
				closest_dist = dist
	return closest_enemy

def closest_stairs(start_x, start_y):
	#find closest enemy, up to a maximum range, and in the mages's FOV
	closest_stairs = None
	closest_dist = 201  #start with (slightly more than) maximum range
	path = libtcod.path_new_using_map(gamescreen.fov_map_full)
 
	for stair in gamemap.stairs:
		#calculate distance between this object and the player
		dist = mage.distance_to(stair)
		if dist < closest_dist:  #it's closer, so remember it
			closest_stairs = stair
			closest_dist = dist
	return closest_stairs


def get_monster_types():
	global monster_list, monster_chances, max_monsters
	monster_chances = {}
	#maximum number of monsters per room
	max_monsters = from_dungeon_level([[2, 1], [3, 3], [4, 5],[3, 7]])
	
	json_data=open('data/monsters2.json')
	monster_list = json.load(json_data)
	json_data.close()
	for idx, monster in enumerate(monster_list["Monsters"]):
		print "Loading Monster: " + str(idx) + " " + monster["name"]
		monster_chances[idx] = from_dungeon_level(monster["chance_table"])


def create_monster(type_id, start_x, start_y):
	#create a monster from the monster list
	global monster_list, numMonsters
	base_hp = int(monster_list["Monsters"][type_id]["hp"])
	base_xp = int(monster_list["Monsters"][type_id]["xp"])
	HP_Deep = math.ceil((base_hp + (base_hp*((gamemap.dungeon_level * 10) / 100 ))))
	XP_Deep = math.ceil((base_xp + (base_xp*((gamemap.dungeon_level * 10) / 100 ))))
	
	fighter_component = MonsterFighter(
		hp=HP_Deep,
		defence=int(monster_list["Monsters"][type_id]["defence"]),
		power=int(monster_list["Monsters"][type_id]["power"]),
		xp=XP_Deep,
		dice = int(monster_list["Monsters"][type_id]["dice"]),
		death_function=eval(monster_list["Monsters"][type_id]["death_function"]), 
		essence=int(monster_list["Monsters"][type_id]["essence"]),
		res_air=int(monster_list["Monsters"][type_id]["res_air"]),
		res_spirit=int(monster_list["Monsters"][type_id]["res_spirit"]),
		res_water=int(monster_list["Monsters"][type_id]["res_water"]),
		res_fire=int(monster_list["Monsters"][type_id]["res_fire"]),
		res_earth=int(monster_list["Monsters"][type_id]["res_earth"])
		)
	
	mai = monster_list["Monsters"][type_id]["monster_ai"]
	cr = monster_list["Monsters"][type_id]["chase_range"]+1
	cd = monster_list["Monsters"][type_id]["chase_dist"]
	ai_component = eval(mai+'(chase_range='+str(cr)+',chase_dist='+str(cd)+')')


	monster = Object(
		start_x, 
		start_y, 
		str(monster_list["Monsters"][type_id]["char"]), 
		monster_list["Monsters"][type_id]["name"], 
		eval('libtcod.' + monster_list["Monsters"][type_id]["color"]), 
		blocks=True, 
		fighter=fighter_component, 
		ai=ai_component,
		desc=str(monster_list["Monsters"][type_id]["description"])
		)
	objects.append(monster)
	numMonsters += 1


def get_item_types():
	global item_list, item_chances, max_items
	item_chances = {}
	#maximum number of item per room
	max_items = from_dungeon_level([[1, 1], [2, 4], [4, 6]])
	
	json_data=open('data/items.json')
	item_list = json.load(json_data)
	json_data.close()
	for idx, item in enumerate(item_list["Items"]):
		print "Loading Items: " + str(idx) + " " + item["name"]
		item_chances[idx] = from_dungeon_level(item["chance_table"])

def create_el_essence(str, start_x, start_y):
	#create an essence item
	global item_list
	if str == 1:
		name = 'Weak Essence'
		color = libtcod.Color(60, 80, 60)
	elif str == 2:
		name = 'Small Essence'
		color = libtcod.Color(50, 80, 50)
	elif str == 3:
		name = 'Medium Essence'
		color = libtcod.Color(40, 80, 40)
	elif str == 4:
		name = 'Strong Essence'
		color = libtcod.Color(30, 80, 30)
	elif str >= 5:
		name = 'Godly Essence'
		color = libtcod.Color(20, 80, 20)

	item_component = Item(
		use_function=gameactions.addEssence,
		power1 = str,
		power2 = 0,
		power3 = 0	
		)
	item = Object(
		start_x, 
		start_y, 
		int(127), 
		name, 
		color, 
		item=item_component
		)

	objects.append(item)
	item.send_to_back()  #items appear below other objects
	item.always_visible = True  #items are visible even out-of-FOV, if in an explored area




def create_item(type_id, start_x, start_y):
	#create an item from the item list
	global item_list, numItems
	item_component = Item(
		use_function=eval(item_list["Items"][type_id]["use_function"]),
		power1 = item_list["Items"][type_id]["power1"],
		power2 = item_list["Items"][type_id]["power2"],
		power3 = item_list["Items"][type_id]["power3"]	
		)
	item = Object(
		start_x, 
		start_y, 
		str(item_list["Items"][type_id]["char"]), 
		str(item_list["Items"][type_id]["name"]), 
		eval('libtcod.' + item_list["Items"][type_id]["color"]), 
		item=item_component
		)

	objects.append(item)
	item.send_to_back()  #items appear below other objects
	item.always_visible = True  #items are visible even out-of-FOV, if in an explored area
	numItems += 1




def place_objects(room):
	global objects, monster_list, monster_chances, max_monsters, item_list, item_chances, max_items
	
	#choose random number of monsters
	num_monsters = libtcod.random_get_int(0, 0, max_monsters)
 
	for i in range(num_monsters):
		#choose random spot for this monster
		x = libtcod.random_get_int(0, room.x1, room.x2)
		y = libtcod.random_get_int(0, room.y1, room.y2)

		#only place it if the tile is not blocked
		if not gamemap.is_blocked(x, y):
			create_monster(random_choice(monster_chances), x, y)
 
	#choose random number of items
	#num_items = libtcod.random_get_int(0, 0, max_items)
	#disabled items for now
	num_items = 0

	for i in range(num_items):
		#choose random spot for this item
		x = libtcod.random_get_int(0, room.x1+1, room.x2-1)
		y = libtcod.random_get_int(0, room.y1+1, room.y2-1)

		#only place it if the tile is not blocked
		if not gamemap.is_blocked(x, y):
			create_item(random_choice(item_chances), x, y)
			



def init_objects():
	#global objects container
	global objects, player, mage
	
	#create object representing the player
	fighter_component = Elemental(hp=50, mana=50, defence=2, power=2, xp=0, death_function=player_death)
	player = Object(0, 0, '@', 'player', libtcod.dark_grey, blocks=True, fighter=fighter_component,
		desc='You.  A young Elemental ripped from your home. ')
	player.level = 1

	#create object representing the mage
	
	fighter_component = MagePet(hp=30, mana=50, defence=2, power=1, xp=0, death_function=mage_death)
	ai_component = MageDumb()
	mage = Object(
		0, 
		0, 
		4, 
		'Mage', 
		libtcod.dark_blue, 
		blocks=True, 
		fighter=fighter_component, 
		ai=ai_component,
		desc='Your Summoner, a meaty humanoid in a funny hat. '
		)
	mage.level = 1

	#the list of objects with those two
	objects = [player, mage]