import sys
import random
from itertools import cycle
import numpy as np
import docplex
import math
import itertools
from docplex.cp.model import CpoModel
from docplex.cp.config import context
from docplex.cp.solver.solver_listener import CpoSolverListener
context.solver.agent = 'local'
context.solver.local.execfile = '/Users/Emily/Documents/CPLEX_Studio128/cpoptimizer/bin/x86-64_osx/cpoptimizer'
context.solver.log_output = True
context.solver.verbose = 5
f = 0.5 # each ifp is assigned to some fraction of teams
r = 0.2 # some fraction is made at random
i = 150 # number of teams
j = 5 # number of tasks
assignment = np.zeros((i, j)) #matrix storing assignments
k1 = int(math.ceil(r*f*i)) # number of random assignments
l = range(0, i) # shuffled list of teams
random.shuffle(l) #random priority order

# round robin assignment to teams
o = cycle(l)
for ifp in range(0, j):
  for k in range(0, k1):
    assignment[next(o), ifp] = 1


# N is set of teams
# L IFP's assigned not closed
# L_i is number of IFP assigned to i \in N
# M is set of new IFP's to assign

# S_j are set of skills defined to be relevant for IFP j
# T_i is set of individuals on the team
# v_{uk} is value of individual u for skill k

# w_{ij} is qualification of team i for IFP j
# w_{ij} = sum_{k \in S_j} \sum{u \in T_i} v_{uk}
# sum of relevant skills over all users in the team

# assign each of the M new IFP's to k2 teams
k2 = int(math.ceil((1-r)*f*i))

# L_i is updated number of IFP's assigned to team i

# First solve
# x_{ij}: is task j assigned to team i
# y: max assignment over all teams
# z: min assignment over all teams
mdl = CpoModel()
teams = range(i)
tasks = range(j)
L = [sum(assignment[team]) for team in teams]
x = [[mdl.integer_var(min = 0, max = 1) for task in tasks] for team in teams]

def balanced():
  #L_i is number of IFP's assigned to i
  y = mdl.integer_var(0, j, "y")
  z = mdl.integer_var(0, j, "z")
  mdl.add(mdl.minimize(y-z))

  for team in teams:
     mdl.add(y >= (L[team] + mdl.sum(x[team][task] for task in tasks)))

  for team in teams:
    mdl.add(z <= (L[team] + mdl.sum(x[team][task] for task in tasks)))

  for task in tasks:
    mdl.add((mdl.sum(x[team][task] for team in teams)== k2))

  for team in teams:
    for task in tasks:
      if assignment[team][task] == 1 :
        mdl.add((x[team][task] == 0))

  #-----------------------------------------------------------------------------
  # Solve the model and display the result
  #-----------------------------------------------------------------------------
  print("\nSolving model....")
  msol = mdl.solve(log_output = True)

  # Print solution
  if msol:
      print ("Solution: " + msol.get_solve_status() + "\n")
      print msol[y]
      print msol[z]
      print ("Solve time: " + str(round(msol.get_solve_time(), 2)) + "s\n")
  else:
      print ("Search status: " + msol.get_solve_status() + "\n")


def expert():
  #z_floor = msol[z]-1
  z_floor = 2
  #z_ceil = msol[z]+1
  z_ceil = 3
  w = np.random.randint(5, size=(i, j)).tolist()
  x = [[mdl.integer_var(min = 0, max = 1) for task in tasks] for team in teams]
  def flatten(lst):
    return list(itertools.chain.from_iterable(lst))

  #mdl.add(mdl.maximize(sum([a*b for a,b in zip(flatten(w), flatten(x))])))
  lst = []
  for team in teams:
    lst.append(mdl.sum(x[team][task] * w[team][task] for task in tasks))

  mdl.add(mdl.maximize(mdl.sum(lst)))

  for team in teams:
    mdl.add(z_floor <= mdl.sum(x[team][task] for task in tasks) + L[team])
    mdl.add((mdl.sum(x[team][task] for task in tasks) + L[team])<= max(L[team], z_ceil))

  for task in tasks:
    mdl.add((mdl.sum(x[team][task] for team in teams)== k2))

  for team in teams:
    for task in tasks:
      if assignment[team][task] == 1 :
        mdl.add((x[team][task] == 0))

  mdl.solve(TimeLimit = (3600*3))


expert()



