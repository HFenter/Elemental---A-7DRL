import libtcodpy as libtcod
import math

import config

import gamemap
import gamescreen
import gamemessages
import gameinput
import gameactions

inventory = []

class Object:
	#this is a generic object: the player, a monster, an item, the stairs...
	#it's always represented by a character on screen.
	def __init__(self, x, y, char, name, color, blocks=False, always_visible=False, fighter=None, ai=None, item=None, equipment=None):
		self.x = x
		self.y = y
		self.char = char
		self.name = name
		self.color = color
		self.blocks = blocks
		self.always_visible = always_visible
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
				#set the color and then draw the character that represents this object at its position
				libtcod.console_set_default_foreground(gamescreen.con, self.color)
				libtcod.console_put_char(gamescreen.con, x, y, self.char, libtcod.BKGND_NONE)
	def clear(self):
		#erase the character that represents this object
		(x, y) = gamescreen.to_camera_coordinates(self.x, self.y)
		if x is not None:
			libtcod.console_put_char(gamescreen.con, x, y, ' ', libtcod.BKGND_NONE)

class Item:
    #an item that can be picked up and used.
    def __init__(self, use_function=None):
        self.use_function = use_function
 
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
        gamemessages.message('You dropped a ' + self.owner.name + '.', libtcod.yellow)
 
    def use(self):

        #just call the "use_function" if it is defined
        if self.use_function is None:
            gamemessages.message('The ' + self.owner.name + ' cannot be used.')
        else:
            if self.use_function() != 'cancelled':
                inventory.remove(self.owner)  #destroy after use, unless it was cancelled for some reason
 





class Fighter:
	#combat-related properties and methods (monster, player, NPC).
	def __init__(self, hp, defense, power, xp, death_function=None):
		self.base_max_hp = hp
		self.hp = hp
		self.base_defense = defense
		self.base_power = power
		self.xp = xp
		self.death_function = death_function

	@property
	def power(self):  #return actual power, by summing up the bonuses from all equipped items
		bonus = 0#sum(equipment.power_bonus for equipment in get_all_equipped(self.owner))
		return self.base_power + bonus

	@property
	def defense(self):  #return actual defense, by summing up the bonuses from all equipped items
		bonus = 0#sum(equipment.defense_bonus for equipment in get_all_equipped(self.owner))
		return self.base_defense + bonus

	@property
	def max_hp(self):  #return actual max_hp, by summing up the bonuses from all equipped items
		bonus = 0#sum(equipment.max_hp_bonus for equipment in get_all_equipped(self.owner))
		return self.base_max_hp + bonus

	def attack(self, target):
		#a simple formula for attack damage
		damage = self.power - target.fighter.defense

		if damage > 0:
			#make the target take some damage
			gamemessages.message(self.owner.name.capitalize() + ' attacks ' + target.name + ' for ' + str(damage) + ' hit points.')
			target.fighter.take_damage(damage)
		else:
			gamemessages.message(self.owner.name.capitalize() + ' attacks ' + target.name + ' but it has no effect!')

	def take_damage(self, damage):
		#apply damage if possible
		if damage > 0:
			self.hp -= damage

		#check for death. if there's a death function, call it
		if self.hp <= 0:
			function = self.death_function
			if function is not None:
				function(self.owner)

			if self.owner != player:  #yield experience to the player
				player.fighter.xp += self.xp

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


def player_death(player):
    #the game ended!
    global game_state
    gamemessages.message('Hahah! You died!', libtcod.red)
    gameinput.game_state = 'dead'
 
    #for added effect, transform the player into a corpse!
    player.char = '%'
    player.color = libtcod.dark_red
 
def monster_death(monster):
    #transform it into a nasty corpse! it doesn't block, can't be
    #attacked and doesn't move
    gamemessages.message('The ' + monster.name + ' is dead! You gain ' + str(monster.fighter.xp) + ' experience points.', libtcod.orange)
    monster.char = '%'
    monster.color = libtcod.dark_red
    monster.blocks = False
    monster.fighter = None
    monster.ai = None
    monster.name = 'remains of ' + monster.name
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




def place_objects(room):
	global objects


	#this is where we decide the chance of each monster or item appearing.
	#maximum number of monsters per room
	max_monsters = from_dungeon_level([[2, 1], [3, 4], [5, 6]])

	#chance of each monster
	monster_chances = {}
	monster_chances['orc'] = 80  #orc always shows up, even if all other monsters have 0 chance
	monster_chances['troll'] = from_dungeon_level([[15, 1], [30, 3], [60, 5]])

	#maximum number of items per room
	max_items = from_dungeon_level([[2, 1], [4, 4]])

	#chance of each item (by default they have a chance of 0 at level 1, which then goes up)
	item_chances = {}
	item_chances['heal'] = 35  #healing potion always shows up, even if all other items have 0 chance
	item_chances['lightning'] = from_dungeon_level([[25, 1]])
	item_chances['fireball'] =  from_dungeon_level([[25, 6]])
	item_chances['confuse'] =   from_dungeon_level([[10, 2]])


	#choose random number of monsters
	num_monsters = libtcod.random_get_int(0, 0, max_monsters)


 
	for i in range(num_monsters):
		#choose random spot for this monster
		x = libtcod.random_get_int(0, room.x1, room.x2)
		y = libtcod.random_get_int(0, room.y1, room.y2)

		#only place it if the tile is not blocked
		if not gamemap.is_blocked(x, y):
			choice = random_choice(monster_chances)
			if choice == 'orc':
				#create an orc
				fighter_component = Fighter(hp=20, defense=0, power=4, xp=35, death_function=monster_death)
				ai_component = BasicMonster()
				monster = Object(x, y, 'o', 'Orc', libtcod.desaturated_green, blocks=True, fighter=fighter_component, ai=ai_component)

			elif choice == 'troll':
				#create a troll
				fighter_component = Fighter(hp=30, defense=2, power=8, xp=100, death_function=monster_death)
				ai_component = BasicMonster()
				monster = Object(x, y, 'T', 'troll', libtcod.darker_green, blocks=True, fighter=fighter_component, ai=ai_component)

			objects.append(monster)
 
	#choose random number of items
	num_items = libtcod.random_get_int(0, 0, max_items)

	for i in range(num_items):
		#choose random spot for this item
		x = libtcod.random_get_int(0, room.x1+1, room.x2-1)
		y = libtcod.random_get_int(0, room.y1+1, room.y2-1)

		#only place it if the tile is not blocked
		if not gamemap.is_blocked(x, y):
			choice = random_choice(item_chances)
			if choice == 'heal':
				#create a healing potion
				item_component = Item(use_function=gameactions.cast_heal)
				item = Object(x, y, '!', 'Healing Potion', libtcod.violet, item=item_component)

			elif choice == 'lightning':
				#create a lightning bolt scroll
				item_component = Item(use_function=gameactions.cast_heal)
				item = Object(x, y, '#', 'Scroll of Lightning Bolt', libtcod.light_yellow, item=item_component)

			elif choice == 'fireball':
				#create a fireball scroll
				item_component = Item(use_function=gameactions.cast_heal)
				item = Object(x, y, '#', 'Scroll of Fireball', libtcod.light_yellow, item=item_component)

			elif choice == 'confuse':
				#create a confuse scroll
				item_component = Item(use_function=gameactions.cast_heal)
				item = Object(x, y, '#', 'Scroll of Confusion', libtcod.light_yellow, item=item_component)

			objects.append(item)
			item.send_to_back()  #items appear below other objects
			item.always_visible = True  #items are visible even out-of-FOV, if in an explored area




def init_objects():
	#global objects container
	global objects, player
	
	#create object representing the player
	fighter_component = Fighter(hp=100, defense=1, power=2, xp=0, death_function=player_death)
	player = Object(0, 0, '@', 'player', libtcod.white, blocks=True, fighter=fighter_component)
	
	#the list of objects with those two
	objects = [player]