#
# This module contains SearchableMaze, a class which converts a Maze into a matrix of nodes that can be traversed with a search algorithm more easily.
#

from operator import itemgetter
from maze import Block
from priorityqueue import PriorityQueue
import threading, random, time

class Node:

    def __init__(self, pos=[-1,-1], block=Block.PATH):
        self.pos = pos[:]

        # self.label = ','.join(str(v) for v in label)
        self.neighbors = []
        self.block = Block.PATH

        self.h = float('inf')
        self.g = 1
        self.f = 0

        self.parent = None

    def print_path(self):
        if self.parent:
            return f"{self.pos} -> {self.parent.print_path()}"

    def get_path(self):
        """ Returns an array representing the path to this node. """
        path = [self.pos]
        temp = self.parent
        while temp != None:
            path.append(temp.pos)
            temp = temp.parent
        
        return path

class SearchableMaze:
    def __init__(self, maze):
        self.maze = maze
        self.node_matrix = self.generate_node_matrix(maze.matrix)
        

    def generate_node_matrix(self, matrix):
        node_matrix = []

        # Generate nodes
        for y in range(0, len(matrix)):
            node_row = []
            for x in range(0, len(matrix[y])):
                block_type = matrix[y][x]
                node_row.append(Node([x, y], block_type))
            node_matrix.append(node_row)

        # Calculate and store neighbors for all nodes
        for row in node_matrix:
            for node in row:
                node.neighbors = self.calculate_neighbors(node_matrix, node)
                # print(node.pos, [node.pos for node in node.neighbors])

        return node_matrix[:]    

    def calculate_sl_distances(self, to_point):
        """ Calculates the straight line distances of each node in the matrix to the point specified. """
        for y in range(0, len(self.node_matrix)):
            for x in range(0, len(self.node_matrix[y])):
                distance = self.maze.calculate_sl_dist((x, y), to_point)
                self.node_matrix[y][x].h = round(distance,2)

    def calculate_neighbors(self, node_matrix, node):
        node_x = node.pos[0]
        node_y = node.pos[1]

        neighbors = []
        if (node_x + 1) < len(node_matrix[0]):
            if self.maze.matrix[node_y][node_x + 1] != Block.WALL:
                neighbors.append(node_matrix[node_y][node_x + 1])
        if (node_x - 1) >= 0:
            if self.maze.matrix[node_y][node_x - 1] != Block.WALL:
                neighbors.append(node_matrix[node_y][node_x - 1])

        if (node_y + 1) < len(node_matrix):
            if self.maze.matrix[node_y + 1][node_x] != Block.WALL:
                neighbors.append(node_matrix[node_y + 1][node_x])
        if (node_y - 1) >= 0:
            if self.maze.matrix[node_y - 1][node_x] != Block.WALL:
                neighbors.append(node_matrix[node_y - 1][node_x])

        return neighbors

    def find_bidirectional_path(self, a_point, b_point):

        a_matrix = self.generate_node_matrix(self.maze.matrix)
        b_matrix = self.generate_node_matrix(self.maze.matrix)

        a_node = a_matrix[a_point[1]][a_point[0]]
        b_node = b_matrix[b_point[1]][b_point[0]]

        a_open_nodes = PriorityQueue()
        a_open_nodes.insert(a_node)

        b_open_nodes = PriorityQueue()
        b_open_nodes.insert(b_node)

        a_closed_nodes = PriorityQueue()
        b_closed_nodes = PriorityQueue()


        iterations = 0
        path = False


        timing_start = time.perf_counter() # for statistics

        while not path and iterations < 10000:
            if iterations % 2 == 0: # Calculate next move for A path
                path = self.find_next_move(a_open_nodes, a_closed_nodes, b_closed_nodes, b_node)
            else: # Calculate next move for B path
                path = self.find_next_move(b_open_nodes, b_closed_nodes, a_closed_nodes, a_node)
            iterations += 1      

        timing_end = time.perf_counter() # for statistics

        return {
            "paths": path,
            "iterations": iterations,
            "duration": timing_end - timing_start
        }

    def find_next_move(self, open_nodes, closed_nodes, ext_closed_nodes, to_node):

        q = open_nodes.popMin()
        closed_nodes.insert(q)

        if q == to_node:
            return q.get_path()
        else:
            for n in ext_closed_nodes.queue:
                if q.pos == n.pos:
                    b_path = n.get_path()
                    return [q.get_path(), b_path]

        for neighbor in q.neighbors:
            
            # Skip nodes already in closed nodes list
            if closed_nodes.containsPosition(neighbor): continue

            existing_node = open_nodes.containsPosition(neighbor)
            if not existing_node:
                neighbor.parent = q
                neighbor.g = q.g + 1
                neighbor.f = neighbor.g + neighbor.h
                open_nodes.insert(neighbor)
            else:
                if existing_node.g < q.g:
                    existing_node.parent = q
                    existing_node.g = q.g - 1
                    existing_node.f = existing_node.g + existing_node.h

            if neighbor.g < q.g:
                existing_node = closed_nodes.containsPosition(neighbor)
                if existing_node:
                    neighbor.parent = existing_node
            elif neighbor.g > q.g:
                existing_node = open_nodes.containsPosition(neighbor)
                if existing_node:
                    existing_node.parent = q
            elif not open_nodes.containsPosition(neighbor) and not closed_nodes.containsPosition(neighbor):
                open_nodes.insert(q)

        return False

    def find_novel_path(self, from_point, to_point):
        """ Uses our approach to bi-directional A* search to find the shortest path passing through the midpoint. """
        
        mp = self.maze.calculate_mp(from_point, to_point)
        total_iterations = 0 # for statistics

        timing_start = time.perf_counter() # for statistics

        # Calculate path from midpoint to start
        path_to_start, iterations = self.find_path(mp, from_point)
        total_iterations += iterations

        # Calculate path from midpoint to goal
        path_to_goal, iterations = self.find_path(mp, to_point)
        total_iterations += iterations

        timing_end = time.perf_counter() # for statistics

        return {
            "paths": [path_to_start, path_to_goal],
            "iterations": total_iterations,
            "duration": timing_end - timing_start
        }

    def find_path(self, from_point, to_point):

        # Calculate and store straight line distances to destination
        self.calculate_sl_distances(to_point)

        # Keep track of the start and end nodes
        from_node = self.node_matrix[from_point[1]][from_point[0]]
        to_node = self.node_matrix[to_point[1]][to_point[0]]

        # Keep track of all "open" nodes
        open_nodes = PriorityQueue()
        open_nodes.insert(from_node)
        
        closed_nodes = PriorityQueue()

        iterations = 0

        while len(open_nodes) > 0 and iterations < 10000:
            iterations += 1

            q = open_nodes.popMin()
            closed_nodes.insert(q)
            
            if q == to_node:
                return (q.get_path(), iterations)

            for neighbor in q.neighbors:
                
                # Skip nodes already in closed nodes list
                if closed_nodes.containsPosition(neighbor): continue

                existing_node = open_nodes.containsPosition(neighbor)
                if not existing_node:
                    neighbor.parent = q
                    neighbor.g = q.g + 1
                    neighbor.f = neighbor.g + neighbor.h
                    open_nodes.insert(neighbor)
                else:
                    if existing_node.g < q.g:
                        existing_node.parent = q
                        existing_node.g = q.g - 1
                        existing_node.f = existing_node.g + existing_node.h

                if neighbor.g < q.g:
                    existing_node = closed_nodes.containsPosition(neighbor)
                    if existing_node:
                        neighbor.parent = existing_node
                elif neighbor.g > q.g:
                    existing_node = open_nodes.containsPosition(neighbor)
                    if existing_node:
                        existing_node.parent = q
                elif not open_nodes.containsPosition(neighbor) and not closed_nodes.containsPosition(neighbor):
                    open_nodes.insert(q)