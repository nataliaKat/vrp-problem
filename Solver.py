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
        self.moveCostForMax = None

    def Initialize(self):
        self.moveCosts = set()
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
        self.moveCost = None
    def Initialize(self):
        self.positionOfFirstRoute = None
        self.positionOfSecondRoute = None
        self.positionOfFirstNode = None
        self.positionOfSecondNode = None
        self.costChangeFirstRt = None
        self.costChangeSecondRt = None
        self.moveCost = 10 ** 9


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
        self.moveCost = None
    def Initialize(self):
        self.positionOfFirstRoute = None
        self.positionOfSecondRoute = None
        self.positionOfFirstNode = None
        self.positionOfSecondNode = None
        self.moveCost = 10 ** 9

class Solver:
    def __init__(self, m):
        self.all_nodes = m.all_nodes
        self.service_locations = m.service_locations
        self.depot = m.all_nodes[0]
        self.time_matrix = m.time_matrix
        self.capacity = m.capacity
        self.total_vehicles = m.total_vehicles
        self.sol = None
        self.bestSolution = None
        self.overallBestSol = None
        self.rcl_size = 1 #isws gia arxh na to kaname 1
        self.try_to_put_in_route=[False for r in range(self.total_vehicles)]

    def solve(self):
        self.setRoutedFlagToFalseForAllServiceLocations()
        self.minimumInsertions()
        # self.applyNearestNeighborMethod()
        cc = self.sol.time_cost
        print("Time is", self.sol.time_cost)
        for r in self.sol.routes:
            r.printRoute()
        SolDrawer.draw('minimuminsertions', self.sol, self.all_nodes)
        self.TestSolution()
        # self.ReportSolution(self.sol)
        self.LocalSearch(0)
        if self.overallBestSol == None or self.overallBestSol.cost > self.sol.time_cost:
            self.overallBestSol = self.cloneSolution(self.sol)
        print('Cost: ', cc, ' LS:', self.sol.time_cost, 'BestOverall: ', self.overallBestSol.time_cost)
        # SolDrawer.draw('localsearch', self.sol, self.all_nodes)

    def LocalSearch(self, operator):
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
                self.FindBestRelocationMove(rm)
                if rm.originRoutePosition is not None or rm.maxOriginRoutePosition is not None:
                    if rm.moveCost < 0 or rm.moveCostForMax <= 0:
                        self.ApplyRelocationMove(rm)
                else:
                    terminationCondition = True
                if rm.originRoutePosition is not None and rm.maxOriginRoutePosition is not None:
                    if rm.moveCost < 0 or rm.moveCostForMax < 0:
                        self.ApplyRelocationMove(rm)
                    else:
                        terminationCondition = True
            # Swaps
            elif operator == 1:
                self.FindBestSwapMove(sm)
                if sm.positionOfFirstRoute is not None:
                    if sm.moveCost < 0:
                        self.ApplySwapMove(sm)
                    else:
                        terminationCondition = True
            elif operator == 2:
                self.FindBestTwoOptMove(top)
                if top.positionOfFirstRoute is not None:
                    if top.moveCost < 0:
                        self.ApplyTwoOptMove(top)
                    else:
                        terminationCondition = True

            self.TestSolution()

            if (self.sol.time_cost < self.bestSolution.time_cost):
                self.bestSolution = self.cloneSolution(self.sol)

            localSearchIterator = localSearchIterator + 1

        self.sol = self.bestSolution

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
        return cloned

    def FindBestRelocationMove(self, rm):
        oldcost = self.sol.time_cost
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
                        # newsol = self.cloneSolution(self.sol)
                        moveCost = costAdded - costRemoved

                        moveCostForMax = moveCost if (self.sol.routes[originRouteIndex] is self.sol.max_route) else 0

                        # print(newsol.routes[originRouteIndex].time , 'ochange',originRtCostChange )
                        # print(newsol.routes[targetRouteIndex].time , 'tchange',targetRtCostChange )
                        # newsol.routes[targetRouteIndex].time = newsol.routes[targetRouteIndex].time + targetRtCostChange
                        # newsol.routes[originRouteIndex].time = newsol.routes[originRouteIndex].time + originRtCostChange
                        # print('oldorigin', self.sol.routes[originRouteIndex].time, 'neworigin', newsol.routes[originRouteIndex].time, newsol.routes[originRouteIndex].time , 'ochange',originRtCostChange )
                        # print('oldtarget', self.sol.routes[targetRouteIndex].time, 'newtarget', newsol.routes[targetRouteIndex].time, newsol.routes[targetRouteIndex].time , 'tchange',targetRtCostChange  )


                       # newcost = self.CalculateTotalCost(newsol)
                        #λαθος σκεψη για εμας πρεπει να το κανουμε καπως αλλιως γιατι εμεις δεν υπολογιζουμε ετσι τον μιν του μαξ χρονο
                        # moveCost = costAdded - costRemoved
                        if moveCostForMax < rm.moveCostForMax:
                            self.StoreBestMaxRelocationMove(originRouteIndex, targetRouteIndex, originNodeIndex,
                                                            targetNodeIndex, originRtCostChange, targetRtCostChange, rm,
                                                            moveCostForMax)
                        if moveCost < rm.moveCost:
                            self.StoreBestRelocationMove(originRouteIndex, targetRouteIndex, originNodeIndex,
                                                         targetNodeIndex, originRtCostChange, targetRtCostChange, rm,
                                                         moveCost)

                        # if (oldcost > newcost):
                        #     # print('oc', oldcost, 'nc', newcost)
                        #     oldcost = newcost
                        #     # print("newsol routes")
                        #     # for r in newsol.routes:
                        #     #     r.printRoute()
                        #     # print("oldsol routes")
                        #     # for r in self.sol.routes:
                        #     #     r.printRoute()
                        #     # print('newcost', newcost, originRouteIndex, targetRouteIndex, originNodeIndex, targetNodeIndex, originRtCostChange, targetRtCostChange, rm)
                        #     # print('route change',rt2.printRoute())
                        #     self.StoreBestRelocationMove(originRouteIndex, targetRouteIndex, originNodeIndex, targetNodeIndex, originRtCostChange, targetRtCostChange, rm)


    def ApplyRelocationMove(self, rm: RelocationMove):
        oldCost = self.CalculateTotalCost(self.sol)
        # rm.moveCostForMax != 10**9
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
                # print("Demand is", B.demand)
                # originRt.time += rm.moveCostForMax
        else:
            originRt = self.sol.routes[rm.originRoutePosition]
            targetRt = self.sol.routes[rm.targetRoutePosition]
            B = originRt.sequenceOfNodes[rm.originNodePosition]

            if originRt == targetRt:
                del originRt.sequenceOfNodes[rm.originNodePosition]
                if (rm.originNodePosition < rm.targetNodePosition):
                    targetRt.sequenceOfNodes.insert(rm.targetNodePosition, B)
                else:
                    targetRt.sequenceOfNodes.insert(rm.targetNodePosition + 1, B)
                #     originRt.time = originRt.time + self.time_matrix[A.id][C.id] - self.time_matrix[A.id][B.id] - self.time_matrix[B.id][C.id] +self.time_matrix[F.id][B.id] + self.time_matrix[B.id][G.id] - self.time_matrix[F.id][G.id]
                # print(rm.moveCost)
                originRt.time += rm.moveCost
            else:
                # print('hello')
                del originRt.sequenceOfNodes[rm.originNodePosition]
                targetRt.sequenceOfNodes.insert(rm.targetNodePosition + 1, B)
                # print(rm.costChangeOriginRt, rm.costChangeTargetRt)
                originRt.time += rm.costChangeOriginRt
                targetRt.time += rm.costChangeTargetRt
                originRt.load -= B.demand
                targetRt.load += B.demand
                # print("Demand is", B.demand)

        # oldCost = self.CalculateTotalCost(self.sol)
        #
        # originRt = self.sol.routes[rm.originRoutePosition]
        # targetRt = self.sol.routes[rm.targetRoutePosition]
        #
        # B = originRt.sequenceOfNodes[rm.originNodePosition]
        # if originRt == targetRt:
        #     # print("same rt")
        #     A = originRt.sequenceOfNodes[rm.originNodePosition - 1]
        #     B = originRt.sequenceOfNodes[rm.originNodePosition]
        #     C = originRt.sequenceOfNodes[rm.originNodePosition + 1]
        #     F = targetRt.sequenceOfNodes[rm.targetNodePosition]
        #     G = targetRt.sequenceOfNodes[rm.targetNodePosition + 1]
        #     del originRt.sequenceOfNodes[rm.originNodePosition]
        #     if (rm.originNodePosition < rm.targetNodePosition):
        #         targetRt.sequenceOfNodes.insert(rm.targetNodePosition, B)
        #     else:
        #         targetRt.sequenceOfNodes.insert(rm.targetNodePosition + 1, B)
        #
        #     originRt.time = originRt.time + self.time_matrix[A.id][C.id] - self.time_matrix[A.id][B.id] - self.time_matrix[B.id][C.id] +self.time_matrix[F.id][B.id] + self.time_matrix[B.id][G.id] - self.time_matrix[F.id][G.id]
        # else:
        #     # print("different rt")
        #     del originRt.sequenceOfNodes[rm.originNodePosition]
        #     targetRt.sequenceOfNodes.insert(rm.targetNodePosition + 1, B)
        #     originRt.time += rm.costChangeOriginRt
        #     targetRt.time += rm.costChangeTargetRt
        #     originRt.load -= B.demand
        #     targetRt.load += B.demand

        #
        # self.sol.time_cost += rm.moveCost

        newCost = self.CalculateTotalCost(self.sol)
        #debuggingOnly
        print('n', newCost, 'o', oldCost, 'mc', rm.moveCost)
        if abs((newCost - oldCost) - rm.moveCost) > 0.0001:
            print('Cost Issue')

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

    def CalculateTotalCost(self, sol):
        sol.max_route = max(sol.routes, key=lambda x: x.time)
        sol.time_cost = sol.max_route.time
        return sol.time_cost

    def TestSolution(self):
        totalSolCost = 0
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
                print ('Route Cost problem')
            if rtLoad != rt.load:
                print ('Route Load problem','L', rtLoad,'l', rt.load)
            routes.append(rt)
        routes.sort(key=lambda x: x.time)
        totalSolCost = routes[-1].time

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
        self.sol.max_route_id = rt.id
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
        shortestroutetime=10**9
        index=-1
        for i in range(self.total_vehicles):
            if self.try_to_put_in_route[i] == False:
                if self.sol.routes[i].time < shortestroutetime:
                    index = i
                    shortestroutetime = self.sol.routes[i].time
        self.try_to_put_in_route[index] = True
        shortestroute = self.sol.routes[index]
        print("shortestroute:",shortestroute.printRoute())
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
            # else:
            # If there is an empty available route
            # kai na elegxei an ksepername to total_vehicles
            # if lastOpenRoute is not None and len(lastOpenRoute.sequenceOfNodes) == 1:
            #     print("hi1")
            #     modelIsFeasible = False
            #     break
            # else:
            # If there is an empty available route
            # kai na elegxei an ksepername to total_vehicles
            # if lastOpenRoute is not None and len(lastOpenRoute.sequenceOfNodes) == 1:
            #     modelIsFeasible = False
            #     print("hi2")
            #     break
            # else:
            #     if self.total_vehicles > len(self.sol.routes):
            #         rt = Route(self.depot, self.capacity)
            #         self.sol.routes.append(rt)
            #     else:
            #         print("hi3")
            #         modelIsFeasible = False

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
                    if len(rt.sequenceOfNodes)==1:
                        trialTime=self.time_matrix[0][candidateServLoc.id]
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
        routes_sorted = self.sol.routes[:]
        routes_sorted.sort(key=lambda x: x.time)
        self.sol.time_cost = routes_sorted[-1].time
        rt.load += insLocation.demand
        insLocation.isRouted = True
