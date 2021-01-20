import random
from VRP_Model import *
from SolutionDrawer import *

class Solution:
    def __init__(self):
        # το μέγιστο όλων των routes που αποτελεί τον ελάχιστο χρόνο ολοκλήρωσης της παραλαβής των προϊόντων
        self.time_cost = 0
        self.max_route = None
        self.routes = []

class ServiceLocationInsertion(object):
    def __init__(self):
        self.serviceLocation = None
        self.route = None
        self.time = 10 ** 9

class ServiceLocationInsertionAllPositions(object):
    def __init__(self):
        self.serviceLocation = None
        self.route = None
        self.insertionPosition = None
        self.time = 10 ** 9

class RelocationMove(object):
    def __init__(self):
        self.originRoutePosition = None
        self.targetRoutePosition = None
        self.originNodePosition = None
        self.targetNodePosition = None
        self.costChangeOriginRt = None
        self.costChangeTargetRt = None
        self.moveCost = None
        self.maxOriginRoutePosition = None
        self.maxTargetRoutePosition = None
        self.maxOriginNodePosition = None
        self.maxTargetNodePosition = None
        self.maxCostChangeOriginRt = None
        self.maxCostChangeTargetRt = None
        self.moveCostForMax = None

    def Initialize(self):
        self.originRoutePosition = None
        self.targetRoutePosition = None
        self.originNodePosition = None
        self.targetNodePosition = None
        self.costChangeOriginRt = None
        self.costChangeTargetRt = None
        self.moveCost = 10 ** 9
        self.maxOriginRoutePosition = None
        self.maxTargetRoutePosition = None
        self.maxOriginNodePosition = None
        self.maxTargetNodePosition = None
        self.maxCostChangeOriginRt = None
        self.maxCostChangeTargetRt = None
        self.moveCostForMax = 10 ** 9

class SwapMove(object):
    def __init__(self):
        self.positionOfFirstRoute = None
        self.positionOfSecondRoute = None
        self.positionOfFirstNode = None
        self.positionOfSecondNode = None
        self.costChangeFirstRt = None
        self.costChangeSecondRt = None
        # self.moveCost = None
    def Initialize(self):
        self.positionOfFirstRoute = None
        self.positionOfSecondRoute = None
        self.positionOfFirstNode = None
        self.positionOfSecondNode = None
        self.costChangeFirstRt = None
        self.costChangeSecondRt = None
        # self.moveCost = 10 ** 9


class CustomerInsertion(object):
    def __init__(self):
        self.customer = None
        self.route = None
        self.cost = 10 ** 9

class CustomerInsertionAllPositions(object):
    def __init__(self):
        self.customer = None
        self.route = None
        self.insertionPosition = None
        self.cost = 10 ** 9

class TwoOptMove(object):
    def __init__(self):
        self.positionOfFirstRoute = None
        self.positionOfSecondRoute = None
        self.positionOfFirstNode = None
        self.positionOfSecondNode = None
        self.costchange1 = None
        self.costchange2 = None
        # self.moveCost = None
    def Initialize(self):
        self.positionOfFirstRoute = None
        self.positionOfSecondRoute = None
        self.positionOfFirstNode = None
        self.positionOfSecondNode = None
        self.costchange1 = None
        self.costchange2 = None
        # self.moveCost = 10 ** 9

class Solver:
    def __init__(self, m):
        self.all_nodes = m.all_nodes
        self.service_locations = m.service_locations
        self.depot = m.all_nodes[0]
        self.no_cost_node = m.all_nodes[201]
        self.time_matrix = m.time_matrix
        self.capacity = m.capacity
        self.total_vehicles = m.total_vehicles
        self.sol = None
        self.bestSolution = None
        self.overallBestSol = None
        self.rcl_size = 5 #isws gia arxh na to kaname 1
        self.try_to_put_in_route=[False for r in range(self.total_vehicles)]
        self.minTabuTenure = 10
        self.maxTabuTenure = 50
        self.tabuTenure = 30
        self.searchTrajectory = []

    def solve(self):
        solutions = set()
        for i in range(50):
            self.setRoutedFlagToFalseForAllServiceLocations()
            self.minimumInsertions(i)
            # self.applyNearestNeighborMethod(i)
            self.addNoCostNode()
            cc = self.sol.time_cost
            if cc in solutions:
                continue
            solutions.add(cc)
            # self.setRoutedFlagToFalseForAllServiceLocations()
            # self.minimumInsertions(i*20)
            # # self.applyNearestNeighborMethod(i*20)
            # cc = self.sol.time_cost
            # # for r in self.sol.routes:
            # #     r.printRoute()
            print("Time is", self.sol.time_cost)
            # SolDrawer.draw('minimuminsertions', self.sol, self.all_nodes)
            # self.ReportSolution(self.sol)
            # self.LocalSearch(1)
            # self.VND()
            self.VND()
            if self.overallBestSol == None or self.overallBestSol.time_cost > self.sol.time_cost:
                self.overallBestSol = self.cloneSolution(self.sol)
            print('Cost: ', cc, ' LS:', self.sol.time_cost, 'BestOverall: ', self.overallBestSol.time_cost)
        SolDrawer.draw('localsearch', self.overallBestSol, self.all_nodes)

    def addNoCostNode(self):
        for rt in self.sol.routes:
            rt.sequenceOfNodes.append(self.no_cost_node)

    def LocalSearch(self, operator):
        solution_cost_trajectory = []

        self.bestSolution = self.cloneSolution(self.sol)
        terminationCondition = False
        localSearchIterator = 0

        rm = RelocationMove()
        sm = SwapMove()
        top = TwoOptMove()

        while terminationCondition is False:

            self.InitializeOperators(rm, sm, top)
            # SolDrawer.draw(localSearchIterator, self.sol, self.allNodes)

            # Relocations
            if operator == 0:
                self.FindBestRelocationMove(rm, localSearchIterator)
                if rm.originRoutePosition is not None or rm.maxOriginRoutePosition is not None:
                    # μηπως να κανεις συνεχως apply
                    print(rm.originRoutePosition, rm.targetRoutePosition, rm.originNodePosition, rm.targetNodePosition, rm.moveCost, rm.moveCostForMax)
                    if rm.moveCost < 0 and rm.moveCostForMax <= 0:
                        self.ApplyRelocationMove(rm, localSearchIterator)
                    else:
                        terminationCondition = True
            # Swaps
            elif operator == 1:
                self.FindBestSwapMove(sm)
                if sm.positionOfFirstRoute is not None:
                    self.ApplySwapMove(sm)
                else:
                        terminationCondition = True
                        operator = 2
            elif operator == 2:
                self.FindBestTwoOptMove(top)
                if top.positionOfFirstRoute is not None:
                    # if top.moveCost < 0:
                    self.ApplyTwoOptMove(top)
                else:
                    # terminationCondition = True
                    operator = 0

            self.TestSolution()
            solution_cost_trajectory.append(self.sol.time_cost)


            if (self.sol.time_cost < self.bestSolution.time_cost):
                self.bestSolution = self.cloneSolution(self.sol)
            if localSearchIterator > 5000:
                terminationCondition = True
            localSearchIterator = localSearchIterator + 1

        self.sol = self.bestSolution

    def VND(self):
        self.bestSolution = self.cloneSolution(self.sol)
        VNDIterator = 0
        kmax = 2
        rm = RelocationMove()
        sm = SwapMove()
        top = TwoOptMove()
        k = 0
        draw = True
        solution_cost_trajectory = []

        while k <= kmax:

            self.InitializeOperators(rm, sm, top)
            if k == 1:
                self.FindBestRelocationMove(rm, VNDIterator)
                if rm.originRoutePosition is not None or rm.maxOriginRoutePosition is not None:
                    # μηπως να κανεις συνεχως apply
                    print(rm.originRoutePosition, rm.targetRoutePosition, rm.originNodePosition, rm.targetNodePosition, rm.moveCost, rm.moveCostForMax)
                    if rm.moveCost < 0 and rm.moveCostForMax <= 0:
                        self.ApplyRelocationMove(rm, VNDIterator)
                        VNDIterator = VNDIterator + 1

                        self.searchTrajectory.append(self.sol.time_cost)
                        k = 0
                    else:
                        k += 1

            elif k == 2:
                self.FindBestSwapMove(sm)
                if sm.positionOfFirstRoute is not None:  #and sm.moveCost < 0:
                    self.ApplySwapMove(sm)
                    # if draw:
                        # SolDrawer.draw(VNDIterator, self.sol, self.all_nodes)
                    VNDIterator = VNDIterator + 1
                    self.searchTrajectory.append(self.sol.time_cost)
                    k = 0
                else:
                    k += 1
            elif k == 0:
                self.FindBestTwoOptMove(top)
                if top.positionOfFirstRoute is not None: #and top.moveCost < 0:
                    self.ApplyTwoOptMove(top)
                    # if draw:
                    #     SolDrawer.draw(VNDIterator, self.sol, self.all_nodes)
                    VNDIterator = VNDIterator + 1
                    self.searchTrajectory.append(self.sol.time_cost)
                    k = 0
                else:
                    k += 1
            solution_cost_trajectory.append(self.sol.time_cost)

            if (self.sol.time_cost < self.bestSolution.time_cost):
                self.bestSolution = self.cloneSolution(self.sol)
        # SolDrawer.drawTrajectory(self.searchTrajectory)


    def VNDrandom(self):
        self.bestSolution = self.cloneSolution(self.sol)
        VNDIterator = 0
        kmax = 2
        rm = RelocationMove()
        sm = SwapMove()
        top = TwoOptMove()
        random.seed(1)
        k = 1
        draw = True
        done=0

        while done<3:
            self.InitializeOperators(rm, sm, top)
            if k == 1:
                self.FindBestRelocationMove(rm)
                if rm.originRoutePosition is not None: # and rm.moveCost < 0:
                    self.ApplyRelocationMove(rm)
                    # if draw:
                    #     SolDrawer.draw(VNDIterator, self.sol, self.all_nodes)
                    VNDIterator = VNDIterator + 1
                    self.searchTrajectory.append(self.sol.time_cost)
                    print(self.sol.time_cost)
                    k = random.randint(0,2)
                else:
                    done +=1
            elif k == 2:
                self.FindBestSwapMove(sm)
                if sm.positionOfFirstRoute is not None:  #and sm.moveCost < 0:
                    self.ApplySwapMove(sm)
                    # if draw:
                        # SolDrawer.draw(VNDIterator, self.sol, self.all_nodes)
                    VNDIterator = VNDIterator + 1
                    self.searchTrajectory.append(self.sol.time_cost)
                    print(self.sol.time_cost)
                    k = random.randint(0,2)
                else:
                    done +=1
            elif k == 0:
                self.FindBestTwoOptMove(top)
                if top.positionOfFirstRoute is not None: #and top.moveCost < 0:
                    self.ApplyTwoOptMove(top)
                    # if draw:
                    #     SolDrawer.draw(VNDIterator, self.sol, self.all_nodes)
                    VNDIterator = VNDIterator + 1
                    self.searchTrajectory.append(self.sol.time_cost)
                    print(self.sol.time_cost)
                    k = random.randint(0,2)
                else:
                    done +=1

            if (self.sol.time_cost < self.bestSolution.time_cost):
                self.bestSolution = self.cloneSolution(self.sol)

        # SolDrawer.drawTrajectory(self.searchTrajectory)

    def cloneRoute(self, rt:Route):
        cloned = Route(self.depot, self.capacity)
        cloned.time = rt.time
        cloned.load = rt.load
        cloned.sequenceOfNodes = rt.sequenceOfNodes.copy()
        return cloned

    def cloneSolution(self, sol: Solution):
        cloned = Solution()
        for i in range (0, len(sol.routes)):
            rt = sol.routes[i]
            clonedRoute = self.cloneRoute(rt)
            cloned.routes.append(clonedRoute)
        cloned.time_cost = self.sol.time_cost
        cloned.max_route = self.cloneRoute(self.sol.max_route)
        return cloned

    def FindBestRelocationMove(self, rm, iterator):
        for originRouteIndex in range(0, len(self.sol.routes)):
            rt1:Route = self.sol.routes[originRouteIndex]
            for targetRouteIndex in range (0, len(self.sol.routes)):
                rt2:Route = self.sol.routes[targetRouteIndex]
                for originNodeIndex in range (1, len(rt1.sequenceOfNodes) - 1):
                    for targetNodeIndex in range (0, len(rt2.sequenceOfNodes) - 1):
                        if originRouteIndex == targetRouteIndex and (targetNodeIndex == originNodeIndex or targetNodeIndex == originNodeIndex - 1):
                            continue
                        #if γιατι δεν επιστρεφει αποθηκη
                        A = rt1.sequenceOfNodes[originNodeIndex - 1]
                        B = rt1.sequenceOfNodes[originNodeIndex]
                        C = rt1.sequenceOfNodes[originNodeIndex + 1]

                        F = rt2.sequenceOfNodes[targetNodeIndex]
                        G = rt2.sequenceOfNodes[targetNodeIndex + 1]

                        if rt1 != rt2:
                            if rt2.load + B.demand > rt2.capacity:
                                continue

                        costAdded = self.time_matrix[A.id][C.id] + self.time_matrix[F.id][B.id] + self.time_matrix[B.id][G.id]
                        costRemoved = self.time_matrix[A.id][B.id] + self.time_matrix[B.id][C.id] + self.time_matrix[F.id][G.id]
                        originRtCostChange = self.time_matrix[A.id][C.id] - self.time_matrix[A.id][B.id] - self.time_matrix[B.id][C.id]
                        targetRtCostChange = self.time_matrix[F.id][B.id] + self.time_matrix[B.id][G.id] - self.time_matrix[F.id][G.id]
                        #λαθος σκεψη για εμας πρεπει να το κανουμε καπως αλλιως γιατι εμεις δεν υπολογιζουμε ετσι τον μιν του μαξ χρονο
                        moveCost = costAdded - costRemoved
                        moveCostForMax = moveCost if (self.sol.routes[originRouteIndex] is self.sol.max_route) else 0

                        if self.MoveIsTabu(B, iterator, moveCost) or self.MoveIsTabu(B, iterator, moveCostForMax):
                            print("node is", B)
                            continue

                        if moveCostForMax < rm.moveCostForMax:
                            self.StoreBestMaxRelocationMove(originRouteIndex, targetRouteIndex, originNodeIndex,
                                                            targetNodeIndex, originRtCostChange, targetRtCostChange, rm,
                                                            moveCostForMax)
                        if moveCost < rm.moveCost:
                            self.StoreBestRelocationMove(originRouteIndex, targetRouteIndex, originNodeIndex,
                                                         targetNodeIndex, originRtCostChange, targetRtCostChange, rm,
                                                         moveCost)

    def ApplyRelocationMove(self, rm: RelocationMove, iterator):
        # rm.moveCostForMax != 10**9
        if rm.targetNodePosition == 18 or rm.originRoutePosition == 18:
            print()
        if rm.moveCostForMax < 0:
            originRt = self.sol.routes[rm.maxOriginRoutePosition]
            targetRt = self.sol.routes[rm.maxTargetRoutePosition]
            B = originRt.sequenceOfNodes[rm.maxOriginNodePosition]

            if originRt == targetRt:
                del originRt.sequenceOfNodes[rm.maxOriginNodePosition]
                if rm.maxOriginNodePosition < rm.maxTargetNodePosition:
                    targetRt.sequenceOfNodes.insert(rm.maxTargetNodePosition, B)
                else:
                    targetRt.sequenceOfNodes.insert(rm.maxTargetNodePosition + 1, B)
                originRt.time += rm.moveCostForMax
            else:
                # print('hello')
                del originRt.sequenceOfNodes[rm.maxOriginNodePosition]
                targetRt.sequenceOfNodes.insert(rm.maxTargetNodePosition + 1, B)
                originRt.time += rm.maxCostChangeOriginRt
                targetRt.time += rm.maxCostChangeTargetRt
                originRt.load -= B.demand
                targetRt.load += B.demand
            # debuggingOnly
            # print('n', newCost, 'o', oldCost, 'mc', rm.moveCostForMax)
            # if abs((newCost - oldCost) - rm.moveCostForMax) > 0.0001:
            #     print('Cost Issue max')
            print("max setting tabu for", B.id, "iterator", iterator)

            self.SetTabuIterator(B, iterator)

        elif rm.moveCostForMax == 0 and rm.moveCost < 0:
            print("entering second")
            originRt = self.sol.routes[rm.originRoutePosition]
            targetRt = self.sol.routes[rm.targetRoutePosition]
            B = originRt.sequenceOfNodes[rm.originNodePosition]

            if originRt == targetRt:
                del originRt.sequenceOfNodes[rm.originNodePosition]
                if (rm.originNodePosition < rm.targetNodePosition):
                    targetRt.sequenceOfNodes.insert(rm.targetNodePosition, B)
                else:
                    targetRt.sequenceOfNodes.insert(rm.targetNodePosition + 1, B)
                originRt.time += rm.moveCost
            else:
                # print('hello')
                del originRt.sequenceOfNodes[rm.originNodePosition]
                targetRt.sequenceOfNodes.insert(rm.targetNodePosition + 1, B)
                originRt.time += rm.costChangeOriginRt
                targetRt.time += rm.costChangeTargetRt
                originRt.load -= B.demand
                targetRt.load += B.demand
            print("setting tabu for", B.id, "iterator", iterator)
            self.SetTabuIterator(B, iterator)

        # debuggingOnly
        #     print('n', newCost, 'o', oldCost, 'mc', rm.moveCost)
            # if abs((newCost - oldCost) - rm.moveCost) > 0.0001:
                # print('Cost Issue')


    def FindBestSwapMove(self, sm):
        oldcost, oldtimes = self.CalculateTotalCost(self.sol)
        for firstRouteIndex in range(0, len(self.sol.routes)):
            rt1:Route = self.sol.routes[firstRouteIndex]
            for secondRouteIndex in range (firstRouteIndex, len(self.sol.routes)):
                rt2:Route = self.sol.routes[secondRouteIndex]
                for firstNodeIndex in range (1, len(rt1.sequenceOfNodes) - 1):
                    startOfSecondNodeIndex = 1
                    if rt1 == rt2:
                        startOfSecondNodeIndex = firstNodeIndex + 1
                    for secondNodeIndex in range (startOfSecondNodeIndex, len(rt2.sequenceOfNodes) - 1):
                        a1 = rt1.sequenceOfNodes[firstNodeIndex - 1]
                        b1 = rt1.sequenceOfNodes[firstNodeIndex]
                        c1 = rt1.sequenceOfNodes[firstNodeIndex + 1]

                        a2 = rt2.sequenceOfNodes[secondNodeIndex - 1]
                        b2 = rt2.sequenceOfNodes[secondNodeIndex]
                        c2 = rt2.sequenceOfNodes[secondNodeIndex + 1]

                        moveCost = None
                        costChangeFirstRoute = None
                        costChangeSecondRoute = None

                        if rt1 == rt2:
                            if firstNodeIndex == secondNodeIndex - 1:
                                costRemoved = self.time_matrix[a1.id][b1.id] + self.time_matrix[b1.id][b2.id] + self.time_matrix[b2.id][c2.id]
                                costAdded = self.time_matrix[a1.id][b2.id] + self.time_matrix[b2.id][b1.id] + self.time_matrix[b1.id][c2.id]
                                costChangeFirstRoute = costAdded - costRemoved
                                costChangeSecondRoute = 0
                                # moveCost = costAdded - costRemoved
                                newsol = self.cloneSolution(self.sol)
                                newsol.routes[firstRouteIndex].time += costAdded - costRemoved
                                newcost,times = self.CalculateTotalCost(newsol)
                            else:

                                costRemoved1 = self.time_matrix[a1.id][b1.id] + self.time_matrix[b1.id][c1.id]
                                costAdded1 = self.time_matrix[a1.id][b2.id] + self.time_matrix[b2.id][c1.id]
                                costRemoved2 = self.time_matrix[a2.id][b2.id] + self.time_matrix[b2.id][c2.id]
                                costAdded2 = self.time_matrix[a2.id][b1.id] + self.time_matrix[b1.id][c2.id]
                                # moveCost = costAdded1 + costAdded2 - (costRemoved1 + costRemoved2)
                                costChangeFirstRoute = costAdded1 + costAdded2 - (costRemoved1 + costRemoved2)
                                newsol = self.cloneSolution(self.sol)
                                # print(newsol.routes[originRouteIndex].time , 'ochange',originRtCostChange )
                                # print(newsol.routes[targetRouteIndex].time , 'tchange',targetRtCostChange )
                                newsol.routes[firstRouteIndex].time += costAdded1 - costRemoved1
                                newsol.routes[secondRouteIndex].time += costAdded2 - costRemoved2
                                newcost,times = self.CalculateTotalCost(newsol)
                        else:
                            if rt1.load - b1.demand + b2.demand > self.capacity:
                                continue
                            if rt2.load - b2.demand + b1.demand > self.capacity:
                                continue

                            costRemoved1 = self.time_matrix[a1.id][b1.id] + self.time_matrix[b1.id][c1.id]
                            costAdded1 = self.time_matrix[a1.id][b2.id] + self.time_matrix[b2.id][c1.id]
                            costRemoved2 = self.time_matrix[a2.id][b2.id] + self.time_matrix[b2.id][c2.id]
                            costAdded2 = self.time_matrix[a2.id][b1.id] + self.time_matrix[b1.id][c2.id]

                            costChangeFirstRoute = costAdded1 - costRemoved1
                            costChangeSecondRoute = costAdded2 - costRemoved2
                            newsol = self.cloneSolution(self.sol)
                            # print(newsol.routes[originRouteIndex].time , 'ochange',originRtCostChange )
                            # print(newsol.routes[targetRouteIndex].time , 'tchange',targetRtCostChange )
                            newsol.routes[firstRouteIndex].time += costAdded1 - costRemoved1
                            newsol.routes[secondRouteIndex].time += costAdded2 - costRemoved2
                            newcost,times = self.CalculateTotalCost(newsol)

                            # moveCost = costAdded1 + costAdded2 - (costRemoved1 + costRemoved2)
                        # print(newcost)
                        if (oldcost > newcost or (oldcost == newcost and times < oldtimes)):
                            # print('oc', oldcost, 'nc', newcost)
                            oldcost = newcost
                            oldtimes = times
                            self.StoreBestSwapMove(firstRouteIndex, secondRouteIndex, firstNodeIndex, secondNodeIndex, costChangeFirstRoute, costChangeSecondRoute, sm)

    def ApplySwapMove(self, sm):
       oldCost = self.CalculateTotalCost(self.sol)
       rt1 = self.sol.routes[sm.positionOfFirstRoute]
       rt2 = self.sol.routes[sm.positionOfSecondRoute]
       b1 = rt1.sequenceOfNodes[sm.positionOfFirstNode]
       b2 = rt2.sequenceOfNodes[sm.positionOfSecondNode]
       rt1.sequenceOfNodes[sm.positionOfFirstNode] = b2
       rt2.sequenceOfNodes[sm.positionOfSecondNode] = b1

       if (rt1 == rt2):
           rt1.time += sm.costChangeFirstRt
       else:
           rt1.time += sm.costChangeFirstRt
           rt2.time += sm.costChangeSecondRt
           rt1.load = rt1.load - b1.demand + b2.demand
           rt2.load = rt2.load + b1.demand - b2.demand

       self.sol.time_cost,times = self.CalculateTotalCost(self.sol)
       # print(self.sol.time_cost)
       newCost = self.CalculateTotalCost(self.sol)
       # debuggingOnly
       # if abs((newCost - oldCost) - sm.moveCost) > 0.0001:
       #     print('Cost Issue')

    def InitializeOperators(self, rm, sm, top):
        rm.Initialize()
        sm.Initialize()
        top.Initialize()

    # moveCost
    def StoreBestRelocationMove(self, originRouteIndex, targetRouteIndex, originNodeIndex, targetNodeIndex, originRtCostChange, targetRtCostChange, rm:RelocationMove, moveCost):
        rm.originRoutePosition = originRouteIndex
        rm.originNodePosition = originNodeIndex
        rm.targetRoutePosition = targetRouteIndex
        rm.targetNodePosition = targetNodeIndex
        rm.costChangeOriginRt = originRtCostChange
        rm.costChangeTargetRt = targetRtCostChange
        rm.moveCost = moveCost

    # maxMoveCost
    def StoreBestMaxRelocationMove(self, originRouteIndex, targetRouteIndex, originNodeIndex, targetNodeIndex,
                                originRtCostChange, targetRtCostChange, rm: RelocationMove, moveCost):
        rm.maxOriginRoutePosition = originRouteIndex
        rm.maxOriginNodePosition = originNodeIndex
        rm.maxTargetRoutePosition = targetRouteIndex
        rm.maxTargetNodePosition = targetNodeIndex
        rm.maxCostChangeOriginRt = originRtCostChange
        rm.maxCostChangeTargetRt = targetRtCostChange
        rm.moveCostForMax = moveCost

    def StoreBestSwapMove(self, firstRouteIndex, secondRouteIndex, firstNodeIndex, secondNodeIndex,costChangeFirstRoute, costChangeSecondRoute, sm):
        sm.positionOfFirstRoute = firstRouteIndex
        sm.positionOfSecondRoute = secondRouteIndex
        sm.positionOfFirstNode = firstNodeIndex
        sm.positionOfSecondNode = secondNodeIndex
        sm.costChangeFirstRt = costChangeFirstRoute
        sm.costChangeSecondRt = costChangeSecondRoute
        # sm.moveCost = moveCost

    def CalculateTotalCost(self, sol):
        c = 0
        routes_sorted = sol.routes[:]
        routes_sorted.sort(key=lambda x: x.time)
        c = routes_sorted[-1].time
        j = 0
        for i in routes_sorted:
            if c == i.time:
                j = j + 1
        return c, j

    def MoveIsTabu(self, n: Node, iterator, moveCost):
        # print("sol", self.sol.time_cost, "best solution", self.bestSolution.time_cost)
        if moveCost + self.sol.time_cost < self.bestSolution.time_cost - 0.001:
            return False
        if iterator < n.isTabuTillIterator:
            return True
        return False

    def SetTabuIterator(self, n: Node, iterator):
        n.isTabuTillIterator = iterator + self.tabuTenure
        print(1)
        # n.isTabuTillIterator = iterator + random.randint(self.minTabuTenure, self.maxTabuTenure)

    def ReportSolution(self, sol):
        for i in range(0, len(sol.routes)):
            rt = sol.routes[i]
            for j in range (0, len(rt.sequenceOfNodes)):
                print(rt.sequenceOfNodes[j].id, end=' ')
            print(rt.time)
        print (self.sol.time_cost)

    def FindBestTwoOptMove(self, top):
        oldcost, oldtimes = self.CalculateTotalCost(self.sol)
        for rtInd1 in range(0, len(self.sol.routes)):
            rt1:Route = self.sol.routes[rtInd1]
            for rtInd2 in range(rtInd1, len(self.sol.routes)):
                rt2:Route = self.sol.routes[rtInd2]
                for nodeInd1 in range(0, len(rt1.sequenceOfNodes) - 1):
                    start2 = 0
                    if (rt1 == rt2):
                        start2 = nodeInd1 + 2

                    for nodeInd2 in range(start2, len(rt2.sequenceOfNodes) - 1):
                        # moveCost = 10 ** 9

                        A = rt1.sequenceOfNodes[nodeInd1]
                        B = rt1.sequenceOfNodes[nodeInd1 + 1]
                        K = rt2.sequenceOfNodes[nodeInd2]
                        L = rt2.sequenceOfNodes[nodeInd2 + 1]

                        if rt1 == rt2:
                            if nodeInd1 == 0 and nodeInd2 == len(rt1.sequenceOfNodes) - 2:
                                continue
                            # costAdded = self.time_matrix[A.id][K.id] + self.time_matrix[B.id][L.id]
                            # costRemoved = self.time_matrix[A.id][B.id] + self.time_matrix[K.id][L.id]
                            # moveCost = costAdded - costRemoved
                            time_cost = 0
                            for i in range(0, nodeInd1):
                                n = rt1.sequenceOfNodes[i]
                                n1 = rt1.sequenceOfNodes[i + 1]
                                time_cost += self.time_matrix[n.id][n1.id]
                            if ( nodeInd2 ==  nodeInd1 + 2):
                                time_cost += self.time_matrix[A.id][K.id] + self.time_matrix[K.id][B.id]
                            else:
                                time_cost += self.time_matrix[A.id][K.id] + self.time_matrix[K.id][(rt2.sequenceOfNodes[nodeInd2 - 1]).id]

                            for i in range(nodeInd2 -1, nodeInd1 + 2, -1):
                                n = rt1.sequenceOfNodes[i]
                                n1 = rt1.sequenceOfNodes[i - 1]
                                time_cost += self.time_matrix[n.id][n1.id]
                            if (nodeInd2 == nodeInd1 + 2):
                                time_cost += self.time_matrix[B.id][L.id]
                            else:
                                time_cost += self.time_matrix[B.id][L.id] + self.time_matrix[rt2.sequenceOfNodes[nodeInd1 + 2].id][B.id]
                            for i in range(nodeInd2 + 1, len(rt1.sequenceOfNodes) -1):
                                n = rt1.sequenceOfNodes[i]
                                n1 = rt1.sequenceOfNodes[i + 1]
                                time_cost += self.time_matrix[n.id][n1.id]

                            newsol = self.cloneSolution(self.sol)
                            newsol.routes[rtInd1].time = time_cost
                            cost1 = time_cost
                            cost2 = 0
                        else:
                            if nodeInd1 == 0 and nodeInd2 == 0:
                                continue
                            if nodeInd1 == len(rt1.sequenceOfNodes) - 2 and  nodeInd2 == len(rt2.sequenceOfNodes) - 2:
                                continue

                            if self.CapacityIsViolated(rt1, nodeInd1, rt2, nodeInd2):
                                continue
                            newsol = self.cloneSolution(self.sol)
                            # costAdded = self.time_matrix[A.id][L.id] + self.time_matrix[B.id][K.id]
                            # costRemoved = self.time_matrix[A.id][B.id] + self.time_matrix[K.id][L.id]
                            rt1FirstSegmentTime = 0
                            for i in range(0, nodeInd1):
                                n = rt1.sequenceOfNodes[i]
                                n1 = rt1.sequenceOfNodes[i+1]
                                rt1FirstSegmentTime += self.time_matrix[n.id][n1.id]
                            rt1SecondSegmentTime = newsol.routes[rtInd1].time - rt1FirstSegmentTime -self.time_matrix[A.id][B.id]

                            rt2FirstSegmentTime = 0
                            for i in range(0, nodeInd2):
                                n = rt2.sequenceOfNodes[i]
                                n1 = rt2.sequenceOfNodes[i + 1]
                                rt2FirstSegmentTime += self.time_matrix[n.id][n1.id]
                            rt2SecondSegmentTime = newsol.routes[rtInd2].time - rt2FirstSegmentTime -self.time_matrix[K.id][L.id]

                            rt1time = rt1FirstSegmentTime + rt2SecondSegmentTime + self.time_matrix[A.id][L.id]
                            rt2time = rt2FirstSegmentTime + rt1SecondSegmentTime + self.time_matrix[K.id][B.id]

                            newsol.routes[rtInd1].time = rt1time
                            newsol.routes[rtInd2].time = rt2time
                            cost1 = rt1time
                            cost2 = rt2time
                        newcost,times = self.CalculateTotalCost(newsol)
                        if (oldcost > newcost or (oldcost == newcost and times < oldtimes)):
                            # print('oc', oldcost, 'nc', newcost)
                            oldcost = newcost
                            oldtimes = times
                            self.StoreBestTwoOptMove(rtInd1, rtInd2, nodeInd1, nodeInd2, top, cost1, cost2)

    def CapacityIsViolated(self, rt1, nodeInd1, rt2, nodeInd2):

            rt1FirstSegmentLoad = 0
            for i in range(0, nodeInd1 + 1):
                n = rt1.sequenceOfNodes[i]
                rt1FirstSegmentLoad += n.demand
            rt1SecondSegmentLoad = rt1.load - rt1FirstSegmentLoad

            rt2FirstSegmentLoad = 0
            for i in range(0, nodeInd2 + 1):
                n = rt2.sequenceOfNodes[i]
                rt2FirstSegmentLoad += n.demand
            rt2SecondSegmentLoad = rt2.load - rt2FirstSegmentLoad

            if (rt1FirstSegmentLoad + rt2SecondSegmentLoad > rt1.capacity):
                return True
            if (rt2FirstSegmentLoad + rt1SecondSegmentLoad > rt2.capacity):
                return True

            return False


    def StoreBestTwoOptMove(self, rtInd1, rtInd2, nodeInd1, nodeInd2, top, costchange1, costchange2):
        top.positionOfFirstRoute = rtInd1
        top.positionOfSecondRoute = rtInd2
        top.positionOfFirstNode = nodeInd1
        top.positionOfSecondNode = nodeInd2
        top.costchange1 = costchange1
        top.costchange2 = costchange2
        # top.moveCost = moveCost

    def ApplyTwoOptMove(self, top):
        rt1: Route = self.sol.routes[top.positionOfFirstRoute]
        rt2: Route = self.sol.routes[top.positionOfSecondRoute]

        if rt1 == rt2:
            # reverses the nodes in the segment [positionOfFirstNode + 1,  top.positionOfSecondNode]
            reversedSegment = reversed(rt1.sequenceOfNodes[top.positionOfFirstNode + 1: top.positionOfSecondNode + 1])
            # lst = list(reversedSegment)
            # lst2 = list(reversedSegment)
            rt1.sequenceOfNodes[top.positionOfFirstNode + 1: top.positionOfSecondNode + 1] = reversedSegment

            # reversedSegmentList = list(reversed(rt1.sequenceOfNodes[top.positionOfFirstNode + 1: top.positionOfSecondNode + 1]))
            # rt1.sequenceOfNodes[top.positionOfFirstNode + 1: top.positionOfSecondNode + 1] = reversedSegmentList
            rt1.time = top.costchange1
            # rt1.cost += top.moveCost
            # print("same route")

        else:
            # slice with the nodes from position top.positionOfFirstNode + 1 onwards
            relocatedSegmentOfRt1 = rt1.sequenceOfNodes[top.positionOfFirstNode + 1:]

            # slice with the nodes from position top.positionOfFirstNode + 1 onwards
            relocatedSegmentOfRt2 = rt2.sequenceOfNodes[top.positionOfSecondNode + 1:]

            del rt1.sequenceOfNodes[top.positionOfFirstNode + 1:]
            del rt2.sequenceOfNodes[top.positionOfSecondNode + 1:]

            rt1.sequenceOfNodes.extend(relocatedSegmentOfRt2)
            rt2.sequenceOfNodes.extend(relocatedSegmentOfRt1)

            self.UpdateRouteCostAndLoad(rt1)
            self.UpdateRouteCostAndLoad(rt2)
            # print("diff route")
        self.sol.time_cost, caltim = self.CalculateTotalCost(self.sol)
        # self.sol.cost += top.moveCost

    def UpdateRouteCostAndLoad(self, rt: Route):
        tc = 0
        tl = 0
        for i in range(0, len(rt.sequenceOfNodes) - 1):
            A = rt.sequenceOfNodes[i]
            B = rt.sequenceOfNodes[i+1]
            tc += self.time_matrix[A.id][B.id]
            tl += B.demand
        rt.load = tl
        rt.time = tc

    def TestSolution(self):
        routes = []
        for r in range (0, len(self.sol.routes)):
            rt: Route = self.sol.routes[r]
            rtCost = 0
            rtLoad = 0
            for n in range(0, len(rt.sequenceOfNodes) - 1):
                A = rt.sequenceOfNodes[n]
                B = rt.sequenceOfNodes[n + 1]
                rtCost += self.time_matrix[A.id][B.id]
                rtLoad += B.demand
            if abs(rtCost - rt.time) > 0.0001:
                print ('Route Cost problem', "ypol", rtCost,"apoth", rt.time)
            if rtLoad != rt.load:
                print ('Route Load problem','L', rtLoad,'l', rt.load)
            routes.append(rt)
        max_route = max(routes, key=lambda x: x.time)
        totalSolCost = max_route.time

        if abs(totalSolCost - self.sol.time_cost) > 0.0001:
            print('Solution Cost problem', "testcost", totalSolCost, "cost", self.sol.time_cost)

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
        rt.sequenceOfNodes.append(insLocation)
        beforeInserted = rt.sequenceOfNodes[-2]
        #costRemoved den yparxei gia mas
        timeAdded = self.time_matrix[beforeInserted.id][insLocation.id]

        rt.time += timeAdded
        #to cost tis antikeimenikis ypologizetai allios ++++ mipws na to ypologizoume sto telos tou ApplyNearestNeighbor????
        self.sol.max_route = max(self.sol.routes, key=lambda x: x.time)
        self.sol.time_cost = self.sol.max_route.time
        rt.load += insLocation.demand

        insLocation.isRouted = True

    def applyNearestNeighborMethod(self, itr=0):
        modelIsFeasible = True
        self.sol = Solution()
        insertions = 0
        self.openAllPaths()
        while (insertions < len(self.service_locations)):
            bestInsertion = ServiceLocationInsertion()
            shortestroute: Route = self.getShortestRoute()

            # if lastOpenRoute is not None:
            self.identifyBest_NN_ofLastVisited(bestInsertion, shortestroute, itr)

            if (bestInsertion.serviceLocation is not None):
                self.applyLocationInsertion(bestInsertion)
                self.try_to_put_in_route=[False for r in range(self.total_vehicles)]
                insertions += 1
            else:
                # If there is an empty available route
                # kai na elegxei an ksepername to total_vehicles
                if shortestroute is not None and len(shortestroute.sequenceOfNodes) == 1:
                    modelIsFeasible = False
                    break
        if (modelIsFeasible == False):
            print('FeasibilityIssue')
            # reportSolution

    def openAllPaths(self):
        for i in range(self.total_vehicles):
            rt = Route(self.depot, self.capacity)
            self.sol.routes.append(rt)

    def getShortestRoute(self):
        # shortestroute = min(self.sol.routes, key = lambda k: k.time)
        shortestroutetime = 10**9
        index = -1
        for i in range(self.total_vehicles):
            if self.try_to_put_in_route[i] == False:
                if self.sol.routes[i].time < shortestroutetime:
                    index = i
                    shortestroutetime = self.sol.routes[i].time
        self.try_to_put_in_route[index] = True
        shortestroute = self.sol.routes[index]
        # print("shortestroute:",shortestroute.printRoute())
        return shortestroute

    def minimumInsertions(self, itr=0):
        modelIsFeasible = True
        self.sol = Solution()
        insertions = 0
        self.openAllPaths()
        while (insertions < len(self.service_locations)):
            bestInsertion = ServiceLocationInsertionAllPositions()
            lastOpenRoute: Route = self.getShortestRoute()
            if lastOpenRoute is not None:
                self.identifyBestInsertionAllPositions(bestInsertion, lastOpenRoute, itr)

            if (bestInsertion.serviceLocation is not None):
                self.applyLocationInsertionAllPositions(bestInsertion)
                self.try_to_put_in_route = [False for r in range(self.total_vehicles)]
                insertions += 1

            if (modelIsFeasible == False):
                print('FeasibilityIssue')
                # reportSolution


    def identifyBestInsertionAllPositions(self, bestInsertion, rt, itr = 0):
        random.seed(itr)
        rcl = []
        for i in range(0, len(self.service_locations)):
            candidateServLoc: Node = self.service_locations[i]
            if candidateServLoc.isRouted is False:
                if rt.load + candidateServLoc.demand <= rt.capacity:
                    if len(rt.sequenceOfNodes) == 1:
                        trialTime = self.time_matrix[0][candidateServLoc.id]
                        bestInsertion.time = trialTime
                        bestInsertion.serviceLocation = candidateServLoc
                        bestInsertion.route = rt
                        bestInsertion.insertionPosition = 1
                        return
                    for j in range(0, len(rt.sequenceOfNodes)-1):
                        A = rt.sequenceOfNodes[j]
                        B = rt.sequenceOfNodes[j + 1]
                        timeAdded = self.time_matrix[A.id][candidateServLoc.id] + self.time_matrix[candidateServLoc.id][B.id]
                        timeRemoved = self.time_matrix[A.id][B.id]
                        trialTime = timeAdded - timeRemoved

                        if len(rcl) < self.rcl_size:
                            new_tup = (trialTime, candidateServLoc, rt, j)
                            rcl.append(new_tup)
                            rcl.sort(key=lambda x: x[0])
                        elif trialTime < rcl[-1][0]:
                            rcl.pop(len(rcl) - 1)
                            new_tup = (trialTime, candidateServLoc, rt, j)
                            rcl.append(new_tup)
                            rcl.sort(key=lambda x: x[0])
        if len(rcl) > 0:
            tup_index = random.randint(0, len(rcl)-1)
            tpl = rcl[tup_index]
            bestInsertion.time = tpl[0]
            bestInsertion.serviceLocation = tpl[1]
            bestInsertion.route = tpl[2]
            bestInsertion.insertionPosition = tpl[3]

    def applyLocationInsertionAllPositions(self, insertion):
        insLocation = insertion.serviceLocation
        rt = insertion.route
        # before the second depot occurrence
        insIndex = insertion.insertionPosition
        rt.sequenceOfNodes.insert(insIndex + 1, insLocation)
        rt.time += insertion.time
        self.CalculateTotalCost(self.sol)
        rt.load += insLocation.demand
        insLocation.isRouted = True

    def testSolution(self, filename):
        f = open(filename)
        lines = f.read().splitlines()
        f.close()
        file_obj = -1
        file_sol = Solution()
        depot = Node(0, 0, 0, 50, 50)
        for i in range(len(lines)):
            if i == 0:
                file_sol.time_cost = float(lines[i])
            else:
                rt = Route(depot, 3000)
                file_sol.routes.append(rt)
                ids = lines[i].split(",")
                for i in range(len(ids)):
                    if i != 0:#gia na min valei tin apothiki
                        id = int(ids[i])
                        rt.sequenceOfNodes.append(self.all_nodes[id])
                rt.printRoute()
        for route in file_sol.routes:
            route.time = 0
            for i in range(len(route.sequenceOfNodes) - 1):
                current = route.sequenceOfNodes[i]
                print("current", current.id)
                next = route.sequenceOfNodes[i + 1]
                print("next", next.id)
                route.time += self.time_matrix[current.id][next.id]

        routes_sorted = file_sol.routes[:]
        routes_sorted.sort(key=lambda x: x.time)
        print("---------")
        print(routes_sorted)
        file_sol.time_cost = routes_sorted[-1].time
        print("Time is", file_sol.time_cost)
