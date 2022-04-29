#
# This module contains Maze, a class that generates and stores a maze represented by a matrix.
#

import random, math, json
from enum import IntEnum

# Used for pretty console output
from colorama import Fore, Back, Style

print(Fore.RESET, Back.RESET)

class Block(IntEnum):
    """
        This enumeration is used within the Maze class for describing block types.
    """
    WALL = 0
    PATH = 1
    GOAL = 2
    HIGHLIGHT_1 = 3
    HIGHLIGHT_2 = 4
    HIGHLIGHT_3 = 5

class Direction(IntEnum):
    """
        This enumeration is used within the Maze class for generating paths.
    """
    NORTH = 0
    EAST = 1
    SOUTH = 2
    WEST = 3

class Maze:
    """Maze
        This class encapsulates a 2D matrix with helper functions for generating mazes.
    """
    def __init__(self):
      pass  
    
    def generate(self, dimensions, start, end):
        """ Generates a new maze of certain dimensions. """

        self.width = dimensions[1]
        self.height = dimensions[0]
        
        grid = self.__generate_matrix(self.width, self.height)

        # Tuples are used as parameters for consistency, but certain internal operations are easier on lists.
        start = list(start)
        end = list(end)
        
        init_start = start[:]
        init_end = end[:]

        self.matrix = self.__generate_maze(grid, start, end)
       

        # Set block types for start and end.
        self.matrix[init_start[1]][init_start[0]] = Block.GOAL
        self.matrix[init_end[1]][init_end[0]] = Block.GOAL

    def save(self, filename):
        """ Saves a generated maze to the filesystem. """

        matrix_int = self.matrix[:]
        for row in range(0, len(self.matrix)):
            for col in range(0, len(self.matrix[0])):
                matrix_int[row][col] = int(self.matrix[row][col])
        matrix_json = json.dumps(matrix_int)
       
        with open(filename, 'w') as file:
            file.write(matrix_json)
        return True

    def load(self, filename):
        """ Loads a pre-generated maze from the filesystem. """
        with open(filename) as file:
            matrix_json = file.read()
            self.matrix = json.loads(matrix_json)
        
        return True

    def print(self):
        """ Outputs the matrix to the console, using colorama for formatting. """

        result = ""
        for row in self.matrix:
            for col in row:
                if col == Block.PATH:
                    result += Fore.WHITE
                    result += Back.WHITE
                elif col == Block.WALL:
                    result += Fore.BLACK
                    result += Back.BLACK
                elif col == Block.GOAL:
                    result += Fore.WHITE
                
                if col == Block.HIGHLIGHT_1:
                    result += Fore.CYAN

                if col == Block.HIGHLIGHT_2:
                    result += Fore.BLUE
                    result += Back.BLUE
                
                if col == Block.HIGHLIGHT_3:
                    result += Fore.MAGENTA
                    result += Back.MAGENTA

                result += "■"
                result += Style.RESET_ALL

            result += "\n"
        print(result)

    def calculate_global_mp(self):
        """ Calculates midpoint of maze. """

        width = len(self.matrix[0])
        height = len(self.matrix)

        x_mid = width // 2
        y_mid = height // 2

        if self.matrix[y_mid][x_mid] == Block.PATH:
            return (x_mid, y_mid)

        search_area_bounds = 1
        found_path = False
        while not found_path:
            min_row = y_mid - search_area_bounds
            max_row = y_mid + search_area_bounds

            min_col = x_mid - search_area_bounds
            max_col = x_mid + search_area_bounds

            for y in range(min_row, max_row):
                for x in range(min_col, max_col):
                    try:
                        if self.matrix[y][x] == Block.PATH: return (x, y)
                    except IndexError:
                        break

            search_area_bounds += 1
        

    def calculate_mp(self, start, end):
        """ Calculates midpoint between two points. """

        x_offset = end[0] - start[0]
        y_offset = end[1] - start[1]

        abs_midpoint_rows = round(y_offset // 2)
        abs_midpoint_cols = round(x_offset // 2)

        abs_mp = [abs_midpoint_rows, abs_midpoint_cols]

        if self.matrix[abs_mp[0]][abs_mp[1]] == Block.PATH:
            return (abs_mp[1], abs_mp[0])

        search_area_bounds = 1
        found_path = False
        while not found_path:
            min_row = abs_mp[0] - search_area_bounds
            max_row = abs_mp[0] + search_area_bounds

            min_col = abs_mp[1] - search_area_bounds
            max_col = abs_mp[1] + search_area_bounds

            for y in range(min_row, max_row):
                for x in range(min_col, max_col):
                    try:
                        if self.matrix[y][x] == Block.PATH: return (x, y)
                    except IndexError:
                        break

            search_area_bounds += 1

    def calculate_sl(self, start, end):
        """ Calculates straight line distance between two points. """
        
        # Use the formula, y = mx + c
        x_offset = end[0] - start[0]
        y_offset = end[1] - start[1]

        m = y_offset / x_offset

        # Find c by using the x and y values of end[]
        c = end[1] - (m * end[0])

        # Pick the largest offset to calculate a path of sufficient resolution
        path_length = abs(x_offset) if abs(x_offset) > abs(y_offset) else abs(y_offset)
        path = []

        for i in range(0, path_length + 1):
            temp_element = [-1,-1]

            if path_length == abs(x_offset): # Use x offset to calculate y offset
                temp_element[0] = start[0] + i
                temp_element[1] = round(m * (start[0] + i) + c)
            elif path_length == abs(y_offset): # Use y offset to calculate x offset
                temp_element[1] = start[1] + i
                temp_element[0] = round(((start[1] + i) - c) / m)
            path.append(temp_element)
        return path

    def calculate_sl_dist(self, start, end):
        x_offset = end[0] - start[0]
        y_offset = end[1] - start[1]
        return math.sqrt(x_offset**2 + y_offset**2)
        
    def draw_path(self, path, color):
        for pos in path:
            self.matrix[pos[1]][pos[0]] = color

    def __generate_matrix(self, width, height):
        """ Returns a nested list of the size specified by *width* and *height*.
            The outer list represents rows, and the inner list represents columns.
        """
        return [[Block.WALL for col in range(0,height)] for row in range(0, width)]

    def __generate_maze(self, matrix, start, end):
        """ Generates a randomized maze using the given matrix. 
            
            Parameters
            __________
            start: (int, int)
                the start position of the maze
            end: (int, int)
                the end position of the maze
        """
    
        position = start

        # Set the current position in the maze to a path block.
        self.__make_path(matrix, position)

        debug_iterations = 0

        path_history = [] # used for back-tracking

        while position != end:

            path_history.append(position)

            debug_iterations += 1
            if debug_iterations > 100000:
                print("Could not find end block within 100,000 iterations.")
                break
            
            # From the start position, determine the direction the path should take.
            # To do this, find all possible directions we could travel:
            valid_move_iterations = 0

            valid_move = False
            while valid_move != True:

                new_position = position[:]

                valid_move_iterations += 1
                if valid_move_iterations > 5: 
                    # If we've tried over 50 randomization attempts to find a valid direction,
                    # back-track a random number of elements and try again.
                    new_position = random.choice(path_history)

                # Randomly back-track to create a more varied maze.
                if random.randint(0,3) == 0: new_position = random.choice(path_history)
                    

                possible_directions = set([Direction.NORTH, Direction.EAST, Direction.SOUTH, Direction.WEST])

                # If the position is at the west edge of the maze, we shouldn't move farther west.
                if new_position[0] <= 0: possible_directions.remove(Direction.WEST)
                # If the position is at the east edge of the maze, we shouldn't move farther east.
                if new_position[0] >= len(matrix[0]) - 1: possible_directions.remove(Direction.EAST)
                # If the position is at the north edge of the maze, we shouldn't move farther north.
                if new_position[1] <= 0: possible_directions.remove(Direction.NORTH)
                # If the position is at the south edge of the maze, we shouldn't move farther south.
                if new_position[1] >= len(matrix) - 1: possible_directions.remove(Direction.SOUTH)

                # Once we have determines the available directions, select one at random.
                possible_directions = list(possible_directions)
                direction = random.choice(possible_directions)

                # Now, increment or decrement the appropriate coordinate of new_position[].
                if direction == Direction.NORTH:
                    new_position[1] -= 1
                elif direction == Direction.SOUTH:
                    new_position[1] += 1
                elif direction == Direction.EAST:
                    new_position[0] += 1
                elif direction == Direction.WEST:
                    new_position[0] -= 1
                
                # Do not allow the path to collide with an earlier segment of the path
                if direction == Direction.NORTH:
                    try:
                        if matrix[new_position[1] - 1][new_position[0]] == Block.PATH: continue
                    except IndexError:
                        pass
                elif direction == Direction.SOUTH:
                    try:
                        if matrix[new_position[1] + 1][new_position[0]] == Block.PATH: continue
                    except IndexError:
                        pass
                elif direction == Direction.EAST:
                    try:
                        if matrix[new_position[1]][new_position[0] + 1] == Block.PATH: continue
                    except IndexError:
                        pass
                elif direction == Direction.WEST:
                    try:
                        if matrix[new_position[1]][new_position[0] - 1] == Block.PATH: continue
                    except IndexError:
                        pass
                
                valid_move = True
            position = new_position

            # Set the current position in the maze to a path block.
            self.__make_path(matrix, position)

        return matrix

    def __make_path(self, matrix, position):
        try:
            matrix[position[1]][position[0]] = Block.PATH
        except IndexError:
            print(f"Could not set {position} to a path block, as it is outside the bounds of the maze.")    

    def __make_wall(self, matrix, position):
        try:
            matrix[position[1]][position[0]] = Block.WALL
        except IndexError:
            print(f"Could not set {position} to a wall block, as it is outside the bounds of the maze.")