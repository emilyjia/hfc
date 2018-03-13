import random
from itertools import cycle
import numpy as np
import docplex
import math
from docplex.cp.model import CpoModel
from docplex.cp.config import context

# ------------------------------------------
# Use local cplex solver
# Print cplex output
# Set number of seconds to solve for
# ------------------------------------------

context.solver.agent = 'local'
context.solver.local.execfile = '/Users/Emily/Documents/CPLEX_Studio128/cpoptimizer/bin/x86-64_osx/cpoptimizer'
context.solver.log_output = True
context.solver.verbose = 5
timelimit = 10

# ------------------------------------------
# Constants
# ------------------------------------------

# each ifp is assigned to some fraction of teams
frac = 0.5
# some fraction is made at random
rand = 0.2
# total number of teams
team_count = 150
teams = range(team_count)
# number of tasks
task_count = 5
tasks = range(task_count)
assignment = np.zeros((team_count, task_count))

# number of random assignments
k1 = int(math.ceil(rand*frac*team_count))
# number of non-random assignments
k2 = int(math.ceil((1-rand)*frac*team_count))

# ------------------------------------------
# Round robin assignment
# ------------------------------------------

def round_robin():
  priority_order = range(team_count)
  random.shuffle(priority_order) #random priority order
  order = cycle(priority_order)
  for ifp in tasks:
    for k in range(0, k1):
      assignment[next(order), ifp] = 1



# ------------------------------------------
# Set up the model
# L is the number of tasks already assigned
# x is indicator of assignment in this round
# ------------------------------------------

mdl = CpoModel()
L = [sum(assignment[team]) for team in teams]


# ------------------------------------------
# Balanced Solution
# x_{ij}: is task j assigned to team i
# y: max assignment over all teams
# z: min assignment over all teams
# ------------------------------------------

def balanced():
  #L_i is number of IFP's assigned to i
  x = [[mdl.integer_var(min = 0, max = 1, name="x{}_{}".format(task, team)) for task in tasks] for team in teams]
  y = mdl.integer_var(0, task_count, "y")
  z = mdl.integer_var(0, task_count, "z")
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

  print("\nSolving model....")
  msol = mdl.solve(TimeLimit = timelimit)
  return msol[z]

# ------------------------------------------
# Expert Solution
# ------------------------------------------

def expert(z_floor, z_ceil):
  w = np.random.randint(5, size=(team_count, task_count)).tolist()
  x = [[mdl.integer_var(min = 0, max = 1, name="x{}_{}".format(task, team)) for task in tasks] for team in teams]

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

  mdl.solve(TimeLimit = timelimit)

# ------------------------------------------
# Main
# ------------------------------------------

def main():
  round_robin()
  z = balanced()
  expert(z-1, z+1)

if __name__ == "__main__":
    main()


