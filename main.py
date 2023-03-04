import os, copy, math

class Ship:
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
        self.xPos   = xPos
        self.yPos   = yPos
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

def main():
    """    
    test_container = Container(1, 2, 96, 'Cat')
    if (test_container.get_dist(0,0) != 3):
        print("ERROR: Manhatten Distance Formula wrong!")
        print("Expected: 3, Actual ", test_container.get_dist(0, 0))
    print(test_container)
    """
main()