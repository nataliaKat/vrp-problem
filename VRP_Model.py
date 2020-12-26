import random
import math

class Model:

# instance variables
    def __init__(self):
        self.all_nodes = []
        self.service_locations = []
        self.time_matrix = []
        self.capacity = -1
        self.total_vehicles = -1

    def build_model(self):
        self.all_nodes = []
        self.service_locations = []
        depot = Node(0, 0, 0, 50, 50)
        self.capacity = 3000
        self.total_vehicles = 25
        self.all_nodes.append(depot)
        random.seed(1)

        for i in range(0, 200):
            id = i + 1
            tp = random.randint(1, 3)
            dem = random.randint(1, 5) * 100
            xx = random.randint(0, 100)
            yy = random.randint(0, 100)
            serv_node = Node(id, tp, dem, xx, yy)
            self.all_nodes.append(serv_node)
            self.service_locations.append(serv_node)

        self.time_matrix = [[0.0 for j in range(0, len(self.all_nodes))] for k in range(0, len(self.all_nodes))]
        for i in range(0, len(self.all_nodes)):
            for j in range(0, len(self.all_nodes)):
                source = self.all_nodes[i]
                target = self.all_nodes[j]
                dx_2 = (source.x - target.x) ** 2
                dy_2 = (source.y - target.y) ** 2
                dist = round(math.sqrt(dx_2 + dy_2))
                time = dist / 35
                if source.type == 0:
                    continue
                elif source.type == 1:
                    time += 1 / 12
                elif source.type == 2:
                    time += 1 / 4
                else:
                    time += 5 / 12
                self.time_matrix[i][j] = time


class Node:
    def __init__(self, id, tp, dem, xx, yy):
        self.id = id
        self.type = tp
        self.demand = dem
        self.x = xx
        self.y = yy
        self.isRouted = False

class Route:
    def __init__(self, dp, cap):
        self.sequenceOfNodes = []
        self.sequenceOfNodes.append(dp)
        # self.sequenceOfNodes.append(dp)
        self.time = 0
        self.capacity = cap
        self.load = 0

    def printRoute(self):
        nodes_string = ""
        for node in self.sequenceOfNodes:
            nodes_string += str(node.id) + ", "
        print(nodes_string)


