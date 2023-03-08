import os, copy, math, queue
from datetime import datetime
from queue import PriorityQueue

class Ship:
    # REPRESENTATION
    def __init__(self, width, height, grid, bay):
        onlist = []
        offlist = []
        
        self.width  = width
        self.height = height
        self.grid   = grid
        self.bay    = bay

    # OPERATORS
    # Where definitions for move, balance, and swap containers operators go.
    def swap(self, x_1, y_1, x_2, y_2):
        index_1 = (y_1 - 1) + ((x_1 -1) * 12)
        index_2 = (y_2 - 1) + ((x_2 -1) * 12)

        tmp_container = copy.deepcopy(self.grid[index_1])
        self.grid[index_1] = self.grid[index_2]
        self.grid[index_1].xPos = x_1
        self.grid[index_1].yPos = y_1

        self.grid[index_2] = tmp_container
        self.grid[index_2].xPos = x_2
        self.grid[index_2].yPos = y_2



        # TODO: Change position values for moved containers in self.bay too

    # OUTPUT
    # For terminal display visualization. Useful for displaying each state.
    # Invalid slots (NAN) are displayed as '█'.
    # Empty slots (UNUSED) are displayed as '-'.
    # Containers are displayed as the first letter of their name.
    def __repr__(self):
        ret_str = ''
        for y in range(self.height - 1, -1, -1):
            for x in range(0, self.width):
                index = x + (y*12)
                curr_container = self.grid[index]
                if (curr_container.name == 'NAN'):
                    ret_str += '█ '
                elif (curr_container.name == 'UNUSED'):
                    ret_str += '- '
                else:
                    ret_str += ((curr_container.name[0]) + ' ')

                pass
            if (y != 0):
                ret_str += '\n'
        return ret_str

class Buffer:
    # REPRESENTATION
    def __init__(self):
        pass

    # OPERATORS
    # Where definitions for move, balance, and swap containers operators go.

    # OUTPUT
    # For terminal display visualization, decide how to display walls, empty spaces, and containers.
    # Should look like a grid.
    def __repr__(self):
        pass

class Container:
    # REPRESENTATION
    def __init__(self, xPos, yPos, weight, name):
        self.xPos   = xPos  #row
        self.yPos   = yPos  #column
        self.weight = weight
        self.name   = name

    # OPERATORS
    def get_dist(self, xPos_new, yPos_new):
        # Manhatten Distance
        return (abs(xPos_new - self.xPos) + abs(yPos_new - self.yPos))

    def cost(self):
        pass

    def is_target(self, xPos, yPos):
        if ((xPos == self.xPos) and (yPos == self.yPos)):
            return True
        return False

    # OUTPUT
    # Used for outputting to new Manifest.
    def __repr__(self) -> str:
        ret_str =   ('['+(str(self.xPos).zfill(2))
                    +','+(str(self.yPos).zfill(2))+']'+", "
                    +'{'+(str(self.weight).zfill(5))+'}'+", "
                    +self.name)
        return ret_str

def addLogComment(str):
    f = open("log.txt", "a")
    now = datetime.now()
    time_str = now.strftime("%B %d %Y: %H:%M")
    f.write(time_str + " " + str)
    f.close()

def login():
    print("""===========================================
                Log In
===========================================""")
    name = input("Your Full Name: ")
    str = name + " signs in\n"
    addLogComment(str)
    
def loadManifest(manifest_file_path):
    #path = input("Manifest File Path:")
    f           = open(manifest_file_path, "r")
    lines       = f.readlines()

    bay         = []
    grid        = []

    for line in lines:
        temp = line.split(", ")
        pos_str = temp[0].strip("[]").split(",")
        xPos = int(pos_str[0])
        yPos = int(pos_str[1])
        weight = int(temp[1].strip("{}"))
        name = temp[2].strip("\n")
        container = Container(xPos, yPos, weight, name)

        if name != "NAN" and name != "UNUSED":
            bay.append(container)

        # print(xPos, yPos, weight, name)
        grid.append(container)  # index = (xPos-1)*12+(yPos-1)

    ret_ship    = Ship(12, 8, grid, bay)
    f.close()
    return ret_ship

class OnOffNode:
    # Representing each state of Ship & Buffer.
    def __init__(self, curr_grid, onlist, offlist, parent, operation, cost, fn):
        self.grid = curr_grid    # list of containers
        self.onlist = onlist
        self.offlist = offlist
        self.parent = parent
        self.operation_from_parent = operation  # string
        self.estimated_time = cost
        self.fn = fn

    def checkTop(self, index):  # return all boxes on top of the container (with this index) and the top box
        curX = self.grid[index].xPos
        curY = self.grid[index].yPos
        boxes = []
        topBox = index
        for i in range(curX+1, 9):  # from curX+1(spot on top) to 8
            if self.grid[(i-1)*12+(curY-1)].name != "UNUSED":
                boxes.append((i-1)*12+(curY-1))
                topBox = (i-1)*12+(curY-1)
        return boxes, topBox

    def available_spot(self):
        available_spots = []
        for i in range(12):
            row = 1
            while self.grid[(row-1)*12 + i].name != "UNUSED" and row <= 8:
                row = row + 1

            if row == 9:
                pass
            elif self.grid[(row-1)*12 + i].name == "UNUSED":
                available_spots.append((row-1)*12 + i)

        return  available_spots

    def nearest_available_spot(self, x, y):  # from x, y to nearest empty spot that's not on top of boxes need to be removed
        spots = self.available_spot()
        nearest = spots[0]
        minDist = self.grid[spots[0]].get_dist(x, y)
        for i in range(len(spots)):
            dist = self.grid[spots[i]].get_dist(x, y)
            if dist < minDist:
                minDist = dist
                nearest = spots[i]
        return minDist, nearest     # return the minimum distance and the index of the nearest spot in grid

    def box_with_least_cost(self, boxes):   # the index of the box_with_least_cost and the cost
        minCost = 100000   # a very large number
        box_to_remove = boxes[0]
        for i in range(len(boxes)):
            x = self.grid[boxes[i]].xPos
            y = self.grid[boxes[i]].yPos
            if boxes[i] in self.offlist:   # from current pos to {9,1} + 2 mins
                cost = abs(9 - x) + abs(1 - y)
                cost = cost + 2     # transfer between truck and ship, so +2 mins
                if cost < minCost:
                    minCost = cost
                    box_to_remove = boxes[i]
            else:   # not target box
                minDist, nearest = self.nearest_available_spot(x, y)
                cost = minDist
                if cost < minCost:
                    minCost = cost
                    box_to_remove = boxes[i]

        return minCost, box_to_remove

    # 2 operations:
    # (1) load to nearest available spot (load)
    # (2) remove the one with the least cost (offload)
    def expand(self):
        box_can_be_removed = []     #box can be moved
        boxes_on_top = []
        ops = []
        for i in range(len(self.offlist)):
            boxes, topbox = self.checkTop(self.offlist[i])
            box_can_be_removed.append(topbox)
            boxes_on_top.extend(boxes)
        # operation 1:
        if len(self.onlist) > 0:
            new_onlist = copy.deepcopy(self.onlist)
            new_offlist = copy.deepcopy(self.offlist)
            new_grid = copy.deepcopy(self.grid)
            temp = new_onlist.pop(0)   # container
            onDist, dest = self.nearest_available_spot(9, 1)    # virtual pink spot, problem slide pg32
            hn = len(new_onlist) + len(new_offlist) + len(boxes_on_top)  # current state to goal state
            gn = 2 + onDist   # cost to get to this node
            fn = hn+gn
            new_grid[dest].name = temp.name
            new_grid[dest].weight = temp.weight
            operation_str = "Load \'" + temp.name + "\' to {" + str(new_grid[dest].xPos) + ", " + str(new_grid[dest].yPos) + "}"

            op1 = OnOffNode(new_grid, new_onlist, new_offlist, self, operation_str, gn, fn)
            ops.append(op1)

        # operation 2:
        if len(self.offlist) > 0:
            new_onlist = copy.deepcopy(self.onlist)
            new_offlist = copy.deepcopy(self.offlist)
            new_grid = copy.deepcopy(self.grid)
            cost, temp = self.box_with_least_cost(box_can_be_removed)
            if temp in new_offlist:     # if it's target box
                new_offlist.remove(temp)
                gn = cost
                hn = len(new_onlist) + len(new_offlist) + len(boxes_on_top)
                fn = gn + hn
                operation_str = "Remove \'" + new_grid[temp].name + "\' from {" + str(new_grid[temp].xPos) + ", " + str(new_grid[temp].yPos) + "}"
                new_grid[temp].name = "UNUSED"
                new_grid[temp].weight = 0
                op2 = OnOffNode(new_grid, new_onlist, new_offlist, self, operation_str, gn, fn)
            else:
                gn = cost
                hn = len(new_onlist) + len(new_offlist) + len(boxes_on_top) - 1    # remove 1 from boxes_on_top
                fn = gn + hn
                offDist, dest = self.nearest_available_spot(new_grid[temp].xPos, new_grid[temp].yPos)   # temp -> target
                operation_str = "Move \'" + new_grid[temp].name + "\' from {" + str(new_grid[temp].xPos) + ", " + str(new_grid[temp].yPos) + "} to {" + str(new_grid[dest].xPos) + ", " + str(new_grid[dest].yPos) + "}"
                new_grid[dest].name = new_grid[temp].name
                new_grid[dest].weight = new_grid[temp].weight
                new_grid[temp].name = "UNUSED"
                new_grid[temp].weight = 0
                op2 = OnOffNode(new_grid, new_onlist, new_offlist, self, operation_str, gn, fn)
            ops.append(op2)

        return ops

def OnOff_goal_test(node):
    if len(node.onlist) == 0 and len(node.offlist) == 0:
        return True
    else:
        return False

class BalanceNode:
    def __init__(self, ship=None, parent=None, children=[], operation='', cost=0, depth=0):
        self.ship       = ship
        self.parent     = parent
        self.children   = children
        self.operation  = operation
        self.cost       = cost
        self.depth      = depth
        
    # Get mass on left-hand side of the ship.
    def get_port_mass(self):
        port_mass = 0
        for y in range(0, self.ship.height):
            for x in range (0, int(self.ship.width/2)):
                index = x + (y*12)
                curr_container = self.ship.grid[index]
                port_mass += curr_container.weight
        return port_mass

    # Get mass on right-hand side of the ship.
    def get_starboard_mass(self):
        starboard_mass = 0
        for y in range(0, self.ship.height):
            for x in range (int(self.ship.width/2), self.ship.width):
                index = x + (y*12)
                curr_container = self.ship.grid[index]
                starboard_mass += curr_container.weight
        return starboard_mass

    # Return all valid positions to move a container to.
    def available_spots(self):
        arr_available_spots = []
        for x in range(self.ship.width):
            y = 0
            curr_index = x + (y*12)
            while((self.ship.grid[curr_index].name != "UNUSED") and (y < self.ship.height)):
                y += 1
                if (y != self.ship.height):
                    curr_index = x + (y*12)
            available_spot = self.ship.grid[curr_index]
            if (available_spot.name == "UNUSED"):
                arr_available_spots.append(available_spot)
        return arr_available_spots
    
    # Return containers at the top of each column, if any.
    def accessable_containers(self):
        arr_accessable_containers = []
        for x in range(self.ship.width): 
            y = 0
            curr_index = x + (y*12)
            curr_container = self.ship.grid[curr_index]
            while((curr_container.name != "UNUSED") and (y < (self.ship.height - 1))):
                if (self.ship.grid[x + ((y+1) * 12)].name != "UNUSED"):
                    y += 1
                    if (y != self.ship.height):
                        curr_index = x + (y*12)
                    curr_container = self.ship.grid[curr_index]
                else:
                    break
            if (curr_container.name != "UNUSED" and curr_container.name != "NAN"):
                arr_accessable_containers.append(curr_container)
        return arr_accessable_containers

    def expand(self, selected_container):
        expanded_nodes = []
        arr_available_spots         = self.available_spots()
        
        x_1 = selected_container.xPos
        y_1 = selected_container.yPos

        for spot in arr_available_spots:
            x_2 = spot.xPos
            y_2 = spot.yPos

            child = BalanceNode(copy.deepcopy(self.ship))
            child.parent = self
            child.ship.swap(x_1, y_1, x_2, y_2)
            
            child.operation =   ("Move Container \'"
                                + selected_container.name
                                +"\' at ["+str(x_1).zfill(2)+","+str(y_1).zfill(2)
                                +"] to ["
                                +str(x_2).zfill(2)+","+str(y_2).zfill(2)+"]")

            distance_heursitic  = selected_container.get_dist(x_2, y_2)
            balance_heuristic   = abs(child.get_port_mass() - child.get_starboard_mass())

            child.cost = distance_heursitic + balance_heuristic
            child.depth = self.depth + 1

            expanded_nodes.append(child)                
        self.children = expanded_nodes
        return expanded_nodes
    
    def balance_goal_test(self):
        if (len(self.ship.bay) <= 1):
            return True
        elif((self.get_port_mass() >= (self.get_starboard_mass() * 0.9)) and
                (self.get_port_mass() <= (self.get_starboard_mass() * 1.1))):
                return True

        return False

    def __lt__(self, other):
        return self.cost < other.cost

def queueing_function(nodes):
    nodes.sort(key=lambda x: x.fn)
    return nodes

def traceback_solution(terminal_node):
    traceback_queue = queue.LifoQueue()

    curr_node = terminal_node
    traceback_queue.put(curr_node)
    while(curr_node.parent != None):
        traceback_queue.put(curr_node.parent)
        curr_node = curr_node.parent

    while(traceback_queue.empty() == False):
        curr_node = traceback_queue.get()
        print(curr_node.operation)
        print('')

def on_off_load(ship):  # general search
    count = 0
    onlist = [Container(9, 1, 120, "test1"), Container(9, 1, 350, "test2")]     # list of containers
    offlist = [2]    # index (int) in grid
    global on_off_nodes
    new_grid = copy.deepcopy(ship.grid)
    on_off_nodes = [OnOffNode(new_grid, onlist, offlist, None, "first node", 0, 0)]
    node = on_off_nodes.pop(0)
    while not OnOff_goal_test(node):
        expanded_nodes = node.expand()    # 2 operations so 2 new nodes
        for i in range(len(expanded_nodes)):
            on_off_nodes.append(expanded_nodes[i])

        on_off_nodes = queueing_function(on_off_nodes)
        node = on_off_nodes.pop(0)

    operation_sequence = ""
    while node != None:
        operation_sequence = node.operation_from_parent + "\n" + operation_sequence
        node = node.parent

    print(operation_sequence)

def balance_ship(init_ship_state):
    # HANGS ON ShipCase4.txt
    # TODO: Optimize to prevent creation of unncessary nodes.
    # Try eliminating child nodes with same heuristic score in node.expand()?

    node            = BalanceNode(init_ship_state)
    frontier        = PriorityQueue()
    explored        = []
    max_queue_size  = 0
    expand_count    = 0

    frontier.put(node)
    while (frontier.qsize() > 0):
        if (frontier.empty()):
            print("ERROR: Failure.")
            return False
        node = frontier.get()
        if (node.balance_goal_test()):
            # Found solution!
            # Return sequence of operations.
            traceback_solution(node)
            return node
        
        explored.append(str(node.ship))
        arr_accessable_containers   = node.accessable_containers()
        # Expand node and get children.
        node_children = []
        for container in arr_accessable_containers:
            node_children += node.expand(container)

        expand_count    += 1
        max_queue_size  = max(max_queue_size, frontier.qsize())
        # Check if children already explored
        # If not explored, put into frontier.
        for child_node in node_children:
            if (str(child_node.ship) not in explored):
                frontier.put(child_node)
            else:
                pass

    pass

def main():
    #login()
    #path = input("Manifest File Path: ")
    init_ship_state = loadManifest('tests/ShipCase2.txt')
    print(init_ship_state)
    print("Port mass: ", BalanceNode(init_ship_state).get_port_mass())
    print("Starboard mass: ", BalanceNode(init_ship_state).get_starboard_mass())
    print("Balanced: ", BalanceNode(init_ship_state).balance_goal_test())

    final_state = (balance_ship(init_ship_state).ship)
    print(final_state)
    print("Port mass: ", BalanceNode(final_state).get_port_mass())
    print("Starboard mass: ", BalanceNode(final_state).get_starboard_mass())
    print("Balanced: ", BalanceNode(final_state).balance_goal_test())

    #print(test_node.accessable_containers())
    
    #on_off_load(init_ship_state)

main()