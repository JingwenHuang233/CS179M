import os, copy, math
from datetime import datetime

class Ship:
    # REPRESENTATION
    def __init__(self, grid, bay):
        self.grid = grid
        self.bay = bay

    # OPERATORS
    # Where definitions for move, balance, and swap containers operators go.

    # OUTPUT
    # For terminal display visualization, decide how to display walls, empty spaces, and containers.
    # Should look like a grid.
    def __repr__(self):
        pass

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


class Node:
    # Representing each state of Ship & Buffer.
    pass

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


def loadManifest():
    path = input("Manifest File Path:")
    f = open(path, "r")
    lines = f.readlines()
    bay = []
    grid = []
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
    global ship
    ship = Ship(grid, bay)
    f.close()
    # print(bay) #for testing
    # print(len(grid)) #for testing


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


def queueing_function(nodes):
    nodes.sort(key=lambda x: x.fn)
    return nodes


def on_off_load():  # general search

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

def main():
    """
    test_container = Container(1, 2, 96, 'Cat')
    if (test_container.get_dist(0,0) != 3):
        print("ERROR: Manhatten Distance Formula wrong!")
        print("Expected: 3, Actual ", test_container.get_dist(0, 0))
    print(test_container)
    """
    login()
    loadManifest()
    on_off_load()

main()

