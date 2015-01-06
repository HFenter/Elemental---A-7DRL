import libtcodpy as libtcod
import config

import gamescreen
import gameobjects

dungeon_level = 1
numRooms = 0

stairs = []

class Tile:
	#a tile of the map and its properties
	def __init__(self, blocked, block_sight = None):
		self.blocked = blocked

		#all tiles start unexplored
		self.explored = False
		
		crk = libtcod.random_get_int(0, 0, 100)
		if crk <= 80:
			self.tile = 1#'#'
		elif crk <= 90:
			self.tile = 2#'#'
		else:
			self.tile = 3#'#'

		# random tile color
		brt = libtcod.random_get_int(0, 150, 180)
		self.color = libtcod.Color(brt,brt,brt)
		#self.color = libtcod.Color(180, 180, 180)
			


		#by default, if a tile is blocked, it also blocks sight
		if block_sight is None: block_sight = blocked
		self.block_sight = block_sight
 
class Rect:
    #a rectangle on the map. used to characterize a room.
    def __init__(self, x, y, w, h):
        self.x1 = x
        self.y1 = y
        self.x2 = x + w
        self.y2 = y + h
 
    def center(self):
        center_x = (self.x1 + self.x2) / 2
        center_y = (self.y1 + self.y2) / 2
        return (center_x, center_y)
 
    def intersect(self, other):
        #returns true if this rectangle intersects with another one
        return (self.x1 <= other.x2 and self.x2 >= other.x1 and
                self.y1 <= other.y2 and self.y2 >= other.y1)


def is_blocked(x, y):
    #first test the map tile
    if map[x][y].blocked:
        return True
 
    #now check for any blocking objects
    for object in gameobjects.objects:
        if object.blocks and object.x == x and object.y == y:
            return True
 
    return False
 
def create_room(room):
	global map
	#go through the tiles in the rectangle and make them passable
	for x in range(room.x1 + 1, room.x2):
		for y in range(room.y1 + 1, room.y2):
			map[x][y].blocked = False
			map[x][y].block_sight = False
			map[x][y].tile = '.'

			# random tile type (boulders, grass, etc...)
			rnd = libtcod.random_get_int(0, 0, 100)
			if rnd <= 90:
				map[x][y].color = libtcod.Color(240, 230, 240)
				map[x][y].tile = '.'
			elif rnd <= 95:
				map[x][y].color = libtcod.Color(20, 230, 20)
				map[x][y].tile = '\''
			elif rnd <= 98:
				map[x][y].color = libtcod.Color(230, 240, 230)
				map[x][y].tile = '`'
			else:
				map[x][y].color = libtcod.Color(230, 225, 230)
				map[x][y].tile = '.'
			
 
def create_h_tunnel(x1, x2, y):
	global map
	#horizontal tunnel. min() and max() are used in case x1>x2
	for x in range(min(x1, x2), max(x1, x2) + 1):
		map[x][y].blocked = False
		map[x][y].block_sight = False
		map[x][y].tile = '.'

		# random tile type (boulders, grass, etc...)
		rnd = libtcod.random_get_int(0, 0, 4)
		if rnd == 1:
			map[x][y].color = libtcod.Color(240, 230, 240)
		elif rnd == 2:
			map[x][y].color = libtcod.Color(220, 215, 200)
		elif rnd == 3:
			map[x][y].color = libtcod.Color(230, 240, 230)
		else:
			map[x][y].color = libtcod.Color(230, 225, 230)
 
def create_v_tunnel(y1, y2, x):
	global map
	#vertical tunnel
	for y in range(min(y1, y2), max(y1, y2) + 1):
		map[x][y].blocked = False
		map[x][y].block_sight = False
		map[x][y].tile = '.'

		# random tile type (boulders, grass, etc...)
		rnd = libtcod.random_get_int(0, 0, 4)
		if rnd == 1:
			map[x][y].color = libtcod.Color(240, 230, 240)
		elif rnd == 2:
			map[x][y].color = libtcod.Color(220, 215, 200)
		elif rnd == 3:
			map[x][y].color = libtcod.Color(230, 240, 230)
		else:
			map[x][y].color = libtcod.Color(230, 225, 230)


 
def make_map():
    global map, stairs

    stairs = []
	#load the monsters and items for placing
    gameobjects.get_monster_types()
    gameobjects.get_item_types()

    gameobjects.numMonsters=0
    gameobjects.numItems=0
    numRooms=0

 
    #fill map with "blocked" tiles
    map = [[ Tile(True)
             for y in range(config.MAP_HEIGHT) ]
           for x in range(config.MAP_WIDTH) ]
 
    rooms = []
    num_rooms = 0
 
    for r in range(config.MAX_ROOMS):
        #random width and height
        w = libtcod.random_get_int(0, config.ROOM_MIN_SIZE, config.ROOM_MAX_SIZE)
        h = libtcod.random_get_int(0, config.ROOM_MIN_SIZE, config.ROOM_MAX_SIZE)
        #random position without going out of the boundaries of the map
        x = libtcod.random_get_int(0, 0, config.MAP_WIDTH - w - 1)
        y = libtcod.random_get_int(0, 0, config.MAP_HEIGHT - h - 1)
 
        #"Rect" class makes rectangles easier to work with
        new_room = Rect(x, y, w, h)
 
        #run through the other rooms and see if they intersect with this one
        failed = False
        for other_room in rooms:
            if new_room.intersect(other_room):
                failed = True
                break
 
        if not failed:
            #this means there are no intersections, so this room is valid
 
            #"paint" it to the map's tiles
            create_room(new_room)
 
            #add some contents to this room, such as monsters
            gameobjects.place_objects(new_room)
 
            #center coordinates of new room, will be useful later
            (new_x, new_y) = new_room.center()
 
            if num_rooms == 0:
                #this is the first room, where the player starts at
                gameobjects.player.x = new_x
                gameobjects.player.y = new_y
            else:
                #all rooms after the first:
                #connect it to the previous room with a tunnel
 
                #center coordinates of previous room
                (prev_x, prev_y) = rooms[num_rooms-1].center()
 
                #draw a coin (random number that is either 0 or 1)
                if libtcod.random_get_int(0, 0, 1) == 1:
                    #first move horizontally, then vertically
                    create_h_tunnel(prev_x, new_x, prev_y)
                    create_v_tunnel(prev_y, new_y, new_x)
                else:
                    #first move vertically, then horizontally
                    create_v_tunnel(prev_y, new_y, prev_x)
                    create_h_tunnel(prev_x, new_x, new_y)
 
            #finally, append the new room to the list
            rooms.append(new_room)
            num_rooms += 1
 
    #create x staircases down
	stair = gameobjects.Object(new_x, new_y, '<', 'Down Stairs', libtcod.white, always_visible=True)
    stairs.append(stair)
    gameobjects.objects.append(stair)
    stair.send_to_back()  #so it's drawn below the monsters





##################################
##			BSP Maps			##
##################################
bsp = None
bsp_depth = 10
bsp_min_room_size = 5
# a room fills a random part of the node or the maximum available space ?
bsp_random_room = True
# if true, there is always a wall on north & west side of a room
#bsp_room_walls = True
bsp_room_walls = False

	
# draw a vertical line
def vline(m, x, y1, y2):
	if y1 > y2:
		y1,y2 = y2,y1
	for y in range(y1,y2+1):
		m[x][y].blocked = False
		m[x][y].block_sight = False
		m[x][y].tile =  5#'.'

# draw a vertical line up until we reach an empty space
def vline_up(m, x, y):
	while y >= 0 and m[x][y].blocked:
		m[x][y].blocked = False
		m[x][y].block_sight = False
		m[x][y].tile =  5#'.'
		y -= 1

# draw a vertical line down until we reach an empty space
def vline_down(m, x, y):
	while y < config.MAP_HEIGHT and m[x][y].blocked:
		m[x][y].blocked = False
		m[x][y].block_sight = False
		m[x][y].tile =  5#'.'
		y += 1

# draw a horizontal line
def hline(m, x1, y, x2):
	if x1 > x2:
		x1,x2 = x2,x1
	for x in range(x1,x2+1):
		m[x][y].blocked = False
		m[x][y].block_sight = False
		m[x][y].tile =  5#'.'

# draw a horizontal line left until we reach an empty space
def hline_left(m, x, y):
	while x >= 0 and m[x][y].blocked:
		m[x][y].blocked = False
		m[x][y].block_sight = False
		m[x][y].tile =  5#'.'
		x -= 1

# draw a horizontal line right until we reach an empty space
def hline_right(m, x, y):
	while x < config.MAP_WIDTH and m[x][y].blocked:
		m[x][y].blocked = False
		m[x][y].block_sight = False
		m[x][y].tile =  5#'.'
		x += 1

# the class building the dungeon from the bsp nodes
def traverse_node(node, dat):
    global map, bsp_min_room_size, numRooms
    #print 'Traversing Map'
    if libtcod.bsp_is_leaf(node):
        # calculate the room size
        minx = node.x + 1
        maxx = node.x + node.w - 1
        miny = node.y + 1
        maxy = node.y + node.h - 1
        if not bsp_room_walls:
            if minx > 1:
                minx -= 1
            if miny > 1:
                miny -=1
        if maxx == config.MAP_WIDTH - 1:
            maxx -= 1
        if maxy == config.MAP_HEIGHT - 1:
            maxy -= 1
        if bsp_random_room:
            minx = libtcod.random_get_int(None, minx, maxx - bsp_min_room_size + 1)
            miny = libtcod.random_get_int(None, miny, maxy - bsp_min_room_size + 1)
            maxx = libtcod.random_get_int(None, minx + bsp_min_room_size - 1, maxx)
            maxy = libtcod.random_get_int(None, miny + bsp_min_room_size - 1, maxy)
        # resize the node to fit the room
        node.x = minx
        node.y = miny
        node.w = maxx-minx + 1
        node.h = maxy-miny + 1
        # dig the room
        new_room = Rect(minx, miny, maxx-minx + 1, maxy-miny + 1)
        for x in range(minx, maxx + 1):
            for y in range(miny, maxy + 1):
				map[x][y].blocked = False
				map[x][y].block_sight = False
				#map[x][y].tile = '.'
				#random floor tile

				rnfl = libtcod.random_get_int(0, 0, 100)
				if rnfl <= 94:
					map[x][y].tile = 5
				elif rnfl <= 96:
					map[x][y].tile = 6
				elif rnfl <= 98:
					map[x][y].tile = 7
				else:
					map[x][y].tile = 8


        numRooms += 1
        gameobjects.place_objects(new_room)
		
		#this is the first room, where the player starts at
        if gameobjects.player.x == 0:
            new_x = libtcod.random_get_int(0, minx, maxx)
            new_y = libtcod.random_get_int(0, miny, maxy)
            print 'placing player at: ' +str(new_x) + ' , '+str(new_x)
            gameobjects.player.x = libtcod.random_get_int(0, minx, maxx)
            gameobjects.player.y = libtcod.random_get_int(0, miny, maxy)

    else:
        # resize the node to fit its sons
        left = libtcod.bsp_left(node)
        right = libtcod.bsp_right(node)
        node.x = min(left.x, right.x)
        node.y = min(left.y, right.y)
        node.w = max(left.x + left.w, right.x + right.w) - node.x
        node.h = max(left.y + left.h, right.y + right.h) - node.y
        # create a corridor between the two lower nodes
        if node.horizontal:
            # vertical corridor
            if left.x + left.w - 1 < right.x or right.x + right.w - 1 < left.x:
                # no overlapping zone. we need a Z shaped corridor
                x1 = libtcod.random_get_int(None, left.x, left.x + left.w - 1)
                x2 = libtcod.random_get_int(None, right.x, right.x + right.w - 1)
                y = libtcod.random_get_int(None, left.y + left.h, right.y)
                vline_up(map, x1, y - 1)
                hline(map, x1, y, x2)
                vline_down(map, x2, y + 1)
            else:
                # straight vertical corridor
                minx = max(left.x, right.x)
                maxx = min(left.x + left.w - 1, right.x + right.w - 1)
                x = libtcod.random_get_int(None, minx, maxx)
                vline_down(map, x, right.y)
                vline_up(map, x, right.y - 1)
        else:
            # horizontal corridor
            if left.y + left.h - 1 < right.y or right.y + right.h - 1 < left.y:
                # no overlapping zone. we need a Z shaped corridor
                y1 = libtcod.random_get_int(None, left.y, left.y + left.h - 1)
                y2 = libtcod.random_get_int(None, right.y, right.y + right.h - 1)
                x = libtcod.random_get_int(None, left.x + left.w, right.x)
                hline_left(map, x - 1, y1)
                vline(map, x, y1, y2)
                hline_right(map, x + 1, y2)
            else:
                # straight horizontal corridor
                miny = max(left.y, right.y)
                maxy = min(left.y + left.h - 1, right.y + right.h - 1)
                y = libtcod.random_get_int(None, miny, maxy)
                hline_left(map, right.x - 1, y)
                hline_right(map, right.x, y)
    return True


def make_bsp_map(bd = 10, ms = 5, brw=False):
	global map, stairs
	global bsp, bsp_refresh
	global bsp_random_room, bsp_room_walls
	global bsp_depth, bsp_min_room_size
	global numRooms
    
	bsp_depth = bd
	bsp_min_room_size = ms
	bsp_room_walls = brw

	stairs = []
	
	#load the monsters and items for placing

	gameobjects.numMonsters=0
	gameobjects.numItems=0
	numRooms=0

	gameobjects.get_monster_types()
	gameobjects.get_item_types()

	print 'Starting BSP Map Build'

	#fill map with "blocked" tiles
	map = [[ Tile(True)
			 for y in range(config.MAP_HEIGHT) ]
		   for x in range(config.MAP_WIDTH) ]
	# dungeon generation
	if bsp is None:
		# create the bsp
		bsp = libtcod.bsp_new_with_size(0, 0, config.MAP_WIDTH-1, config.MAP_HEIGHT-1)
	else:
		# restore the nodes size
		libtcod.bsp_resize(bsp, 0, 0, config.MAP_WIDTH-1, config.MAP_HEIGHT-1)
	# build a new random bsp tree
	libtcod.bsp_remove_sons(bsp)
	libtcod.bsp_split_recursive(bsp, 0, bsp_depth, bsp_min_room_size + 1, bsp_min_room_size + 1, 1.5, 1.5)
	# create the dungeon from the bsp
	libtcod.bsp_traverse_inverted_level_order(bsp, traverse_node)
	

	#random spot on the map for the stairs, somewhere near the center
	#lets place 3 stairs per level
	# in the middle
	node = libtcod.bsp_find_node(bsp, (libtcod.random_get_int(0, ((config.MAP_WIDTH-1)/2)-25, ((config.MAP_WIDTH-1)/2)+25)) , (libtcod.random_get_int(0, ((config.MAP_HEIGHT-1)/2)-25, ((config.MAP_HEIGHT-1)/2)+25)) )
	while not libtcod.bsp_is_leaf(node):
		node = libtcod.bsp_find_node(bsp, (libtcod.random_get_int(0, ((config.MAP_WIDTH-1)/2)-25, ((config.MAP_WIDTH-1)/2)+25)) , (libtcod.random_get_int(0, ((config.MAP_HEIGHT-1)/2)-25, ((config.MAP_HEIGHT-1)/2)+25)) )
	sx = libtcod.random_get_int(0, node.x, node.x+node.w-1)
	sy = libtcod.random_get_int(0, node.y, node.y+node.h-1)
	stair = gameobjects.Object(sx, sy, '<', 'Down Stairs', libtcod.white, always_visible=True)
	print 'Placed stair 1 at:'+str(sx)+','+str(sy)

	stairs.append(stair)
	gameobjects.objects.append(stair)
	stair.send_to_back()  #so it's drawn below the monsters

	#in the northern area
	node = libtcod.bsp_find_node(bsp, (libtcod.random_get_int(0, 5, (config.MAP_WIDTH-5))) , (libtcod.random_get_int(0, 5, (config.MAP_HEIGHT/5))) )
	while not libtcod.bsp_is_leaf(node):
		node = libtcod.bsp_find_node(bsp, (libtcod.random_get_int(0, 5, (config.MAP_WIDTH-5))) , (libtcod.random_get_int(0, 5, (config.MAP_HEIGHT/5))) )
	sx = libtcod.random_get_int(0, node.x, node.x+node.w-1)
	sy = libtcod.random_get_int(0, node.y, node.y+node.h-1)
	stair = gameobjects.Object(sx, sy, '<', 'Down Stairs', libtcod.white, always_visible=True)
	print 'Placed stair 2 at:'+str(sx)+','+str(sy)

	stairs.append(stair)
	gameobjects.objects.append(stair)
	stair.send_to_back()  #so it's drawn below the monsters

	#in the southern area
	node = libtcod.bsp_find_node(bsp, (libtcod.random_get_int(0, 5, (config.MAP_WIDTH-5))) , (libtcod.random_get_int(0, config.MAP_HEIGHT-(config.MAP_HEIGHT/4), config.MAP_HEIGHT-5)) )
	while not libtcod.bsp_is_leaf(node):
		node = libtcod.bsp_find_node(bsp, (libtcod.random_get_int(0, 5, (config.MAP_WIDTH-5))) , (libtcod.random_get_int(0, config.MAP_HEIGHT-(config.MAP_HEIGHT/4), config.MAP_HEIGHT-5)) )
	sx = libtcod.random_get_int(0, node.x, node.x+node.w-1)
	sy = libtcod.random_get_int(0, node.y, node.y+node.h-1)
	stair = gameobjects.Object(sx, sy, '<', 'Down Stairs', libtcod.white, always_visible=True)
	print 'Placed stair 3 at:'+str(sx)+','+str(sy)

	stairs.append(stair)
	gameobjects.objects.append(stair)
	stair.send_to_back()  #so it's drawn below the monsters

	print 'Map Done:'
	print '  Monsters: '+str(gameobjects.numMonsters)
	print '  Items: '+str(gameobjects.numItems)
	print '  Rooms: '+str(numRooms)

		

