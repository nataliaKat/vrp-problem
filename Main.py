from Solver import *
from VRP_Model import Model

m = Model()
m.build_model()
s = Solver(m)
sol = s.solve()

