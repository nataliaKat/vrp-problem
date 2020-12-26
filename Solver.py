import random
from VRP_Model import *
from SolutionDrawer import *

class Solution:
    def __init__(self):
        # το μέγιστο όλων των routes που αποτελεί τον ελάχιστο χρόνο ολοκλήρωσης της παραλαβής των προϊόντων
        self.time_cost = 0
        self.routes = []

class ServiceLocationInsertion(object):
    def __init__(self):
        self.serviceLocation = None
        self.route = None
        self.time = 10 ** 9

class Solver:
    def __init__(self, m):
        self.all_nodes = m.all_nodes
        self.service_locations = m.service_locations
        self.depot = m.all_nodes[0]
        self.time_matrix = m.time_matrix
        self.capacity = m.capacity
        self.total_vehicles = m.total_vehicles
        self.sol = None
        # self.bestSolution = None
        # self.overallBestSol = None
        self.rcl_size = 1 #isws gia arxh na to kaname 1

    def solve(self):
        self.setRoutedFlagToFalseForAllServiceLocations()
        self.applyNearestNeighborMethod()
        print("Time is", self.sol.time_cost)
        for r in self.sol.routes:
            r.printRoute()
        SolDrawer.draw(1, self.sol, self.all_nodes)

    def setRoutedFlagToFalseForAllServiceLocations(self):
        for i in range(0, len(self.service_locations)):
            self.service_locations[i].isRouted = False

    def getLastOpenRoute(self):
        if len(self.sol.routes) == 0:
            return None
        else:
            return self.sol.routes[-1]

    def identifyBest_NN_ofLastVisited(self, bestInsertion:ServiceLocationInsertion, rt, itr = 0):
        random.seed(itr)
        rcl = []
        for i in range(0, len(self.service_locations)):
            candidateLocation:Node = self.service_locations[i]
            if candidateLocation.isRouted is False:
                if rt.load + candidateLocation.demand <= rt.capacity:
                    #emeis ksekiname apo -1 epeidi den paei stin apothiki
                    lastNodePresentInTheRoute = rt.sequenceOfNodes[-1]
                    trialTime = self.time_matrix[lastNodePresentInTheRoute.id][candidateLocation.id]
                    # Update rcl list
                    if len(rcl) < self.rcl_size:
                        new_tup = (trialTime, candidateLocation, rt)
                        rcl.append(new_tup)
                        rcl.sort(key=lambda x: x[0])
                    elif trialTime < rcl[-1][0]:
                        rcl.pop(len(rcl) - 1)
                        new_tup = (trialTime, candidateLocation, rt)
                        rcl.append(new_tup)
                        rcl.sort(key=lambda x: x[0])
        if len(rcl) > 0:
            tup_index = random.randint(0, len(rcl) - 1)
            tpl = rcl[tup_index]
            bestInsertion.time = tpl[0]
            bestInsertion.serviceLocation = tpl[1]
            bestInsertion.route = tpl[2]

    def applyLocationInsertion(self, insertion):
        insLocation = insertion.serviceLocation
        rt = insertion.route
        #before the second depot occurrence
        #ena append tha kanoume
        # insIndex = len(rt.sequenceOfNodes) - 1
        # rt.sequenceOfNodes.insert(insIndex, insCustomer)
        rt.sequenceOfNodes.append(insLocation)

        beforeInserted = rt.sequenceOfNodes[-2]

        #costRemoved den yparxei gia mas
        timeAdded = self.time_matrix[beforeInserted.id][insLocation.id]

        rt.time += timeAdded
        #to cost tis antikeimenikis ypologizetai allios ++++ mipws na to ypologizoume sto telos tou ApplyNearestNeighbor????
        routes_sorted = self.sol.routes[:]
        routes_sorted.sort(key=lambda x: x.time)
        self.sol.time_cost = routes_sorted[-1].time

        rt.load += insLocation.demand

        insLocation.isRouted = True

    def applyNearestNeighborMethod(self, itr=0):
        modelIsFeasible = True
        self.sol = Solution()
        insertions = 0
        while (insertions < len(self.service_locations)):
            bestInsertion = ServiceLocationInsertion()
            lastOpenRoute: Route = self.getLastOpenRoute()

            if lastOpenRoute is not None:
                self.identifyBest_NN_ofLastVisited(bestInsertion, lastOpenRoute, itr)

            if (bestInsertion.serviceLocation is not None):
                self.applyLocationInsertion(bestInsertion)
                insertions += 1
            else:
                # If there is an empty available route
                # kai na elegxei an ksepername to total_vehicles
                if lastOpenRoute is not None and len(lastOpenRoute.sequenceOfNodes) == 1:
                    modelIsFeasible = False
                    break
                else:
                    if self.total_vehicles > len(self.sol.routes):
                        rt = Route(self.depot, self.capacity)
                        self.sol.routes.append(rt)
                    else:
                        modelIsFeasible = False

        if (modelIsFeasible == False):
            print('FeasibilityIssue')
            # reportSolution
