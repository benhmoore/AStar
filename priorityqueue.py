#
# From https://www.geeksforgeeks.org/priority-queue-in-python/
# A simple implementation of Priority Queue
# using Queue.
#

class PriorityQueue(object):
    def __init__(self):
        self.queue = []

    def __len__(self):
        return len(self.queue)
    
    def __str__(self):
        return str(self.queue)
  
    # for checking if the queue is empty
    def isEmpty(self):
        return len(self.queue) == 0
  
    # for inserting an element in the queue
    def insert(self, node):
        self.queue.append(node)

    def containsPosition(self, node):
        nodes = []
        for q_node in self.queue:
            if q_node.pos == node.pos:
                nodes.append(q_node)
        
        if len(nodes) < 1: return False

        try:
            min = 0
            for i in range(len(nodes)):
                if nodes[i].f < nodes[min].f:
                    min = i
            item = nodes[min]
            del nodes[min]
            return item
        except IndexError:
            print()
            exit()
  
    def popMin(self):
        cumulative_g = 0
        
        try:
            min = 0
            for i in range(len(self.queue)):
                if self.queue[i].f < self.queue[min].f:
                    min = i
            item = self.queue[min]
            del self.queue[min]
            return item
        except IndexError:
            print()
            exit()