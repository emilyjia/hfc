import random
from itertools import cycle
import numpy as np
import docplex
import math
from docplex.mp.model import Model

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
# Balanced Solution
# x[(i, j)]: is task j assigned to team i
# y: max assignment over all teams
# z: min assignment over all teams
# ------------------------------------------

def balanced():
  mdl = Model()
  mdl.context.solver.agent = 'local'
  mdl.context.solver.log_output = True
  timelimit = 10000
  L = [sum(assignment[team]) for team in teams]
  #L_i is number of IFP's assigned to i
  x = mdl.binary_var_matrix(team_count, task_count, name = "x")
  y = mdl.integer_var(0, task_count, "y")
  z = mdl.integer_var(0, task_count, "z")
  mdl.minimize(y-z)

  for team in teams:
     mdl.add_constraint(y >= (L[team] + mdl.sum(x[(team, task)] for task in tasks)))

  for team in teams:
    mdl.add_constraint(z <= (L[team] + mdl.sum(x[(team, task)] for task in tasks)))

  for task in tasks:
    mdl.add_constraint((mdl.sum(x[(team, task)] for team in teams)== k2))

  for team in teams:
    for task in tasks:
      if assignment[team][task] == 1 :
        mdl.add_constraint(x[(team, task)] == 0)

  msol = mdl.solve(TimeLimit = timelimit)

  print msol["y"]
  print msol["z"]
  return [msol["y"], msol["z"]]

# ------------------------------------------
# Expert Solution
# ------------------------------------------


def expert(z_floor, z_ceil, w):
  mdl = Model()
  mdl.context.solver.agent = 'local'
  mdl.context.solver.log_output = True
  timelimit = 10000
  L = [sum(assignment[team]) for team in teams]
  #L_i is number of IFP's assigned to i
  x = mdl.binary_var_matrix(team_count, task_count, name = "x")

  lst = []
  for team in teams:
    lst.append(mdl.sum(x[(team, task)] * w[team][task] for task in tasks))

  mdl.maximize(mdl.sum(lst))

  for team in teams:
    mdl.add_constraint(z_floor <= mdl.sum(x[(team, task)] for task in tasks) + L[team])
    mdl.add_constraint((mdl.sum(x[(team, task)] for task in tasks) + L[team])<= max(L[team], z_ceil))

  for task in tasks:
    mdl.add_constraint((mdl.sum(x[(team, task)] for team in teams)== k2))

  for team in teams:
    for task in tasks:
      if assignment[team][task] == 1 :
        mdl.add_constraint((x[(team, task)] == 0))

  msol = mdl.solve(TimeLimit = timelimit)

  x = np.zeros((team_count, task_count))
  for team in teams:
    for task in tasks:
      x[team][task] = msol["x_{}_{}".format(team, task)]

  return x


# ------------------------------------------
# Make the skill matrix
# ------------------------------------------

def make_skill(skill_count, worker_count):
  skills = range(skill_count)
  workers = range(worker_count)
  w = np.zeros((team_count, task_count))
  team_skill = np.zeros((team_count, skill_count))
  for team in teams:
    for skill in skills:
      skill_value = 0
      for worker in workers:
        skill_value += np.random.normal()
      team_skill[team][skill] = skill_value
  for task in tasks:
    skill = np.random.randint(skill_count)
    for team in teams:
      w[team][task] = team_skill[team][skill]
  return w

# ------------------------------------------
# Main
# ------------------------------------------

def main():
  round_robin()
  bal_sol = balanced()
  z = bal_sol[1]
  raw_input("Press Enter to continue...")
  w = make_skill(6, 5)
  x = expert(z-1, z+1, w)
  # print w
  # print x
  # print(np.dot(x.flatten(), w.flatten()))


if __name__ == "__main__":
    main()


