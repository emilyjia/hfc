from task_assign import Task_assign
import sys
import random
from itertools import cycle
import numpy as np
import unittest
import math

# ------------------------------------------
# Priority order is teams in order of index
# ------------------------------------------

def round_robin_test(team_count, task_count, k1):
  teams = range(team_count)
  tasks = range(task_count)
  assignment = np.zeros((team_count, task_count))
  order = cycle(teams)
  for ifp in tasks:
    for k in range(0, k1):
      assignment[next(order), ifp] = 1
  return assignment


# ------------------------------------------
# Checks the skill matrix reads file correctly
# ------------------------------------------

def make_skill_from_file_test():
  test_ip = Task_assign([], team_count = 4)
  skill_matrix = test_ip.make_skill_from_file("skill_file_test.csv", 3)
  assert np.all(skill_matrix == [[2,1,2],[1,1,1],[0,1,0],[2,2,1]])
  print "======================="
  print "Make skill from file passed"

# ------------------------------------------
# Checks a 2-day ip assignment
# ------------------------------------------

def ip_tests():
  print "Starting Tests..."
  print "======================="
  assert np.all(round_robin_test(4, 2, 2) == [[1,0], [1,0], [0,1], [0,1]])
  print "Round Robin Test passed"

  total_days = 2
  task_per_day = 4
  frac = 0.5
  rand = 0.25
  team_count = 8
  timelimit = 100
  total_tasks = total_days*task_per_day
  assignment = np.zeros((team_count, total_tasks))

  for day in range(total_days):
    day_ip = Task_assign(assignment, frac = frac, rand = rand, team_count = team_count, task_count = task_per_day, day = day)
    bal_mdl = day_ip.build_balanced()
    bal_sol = bal_mdl.solve(log_output = False)
    if day==0:
      assert (bal_sol["y"] == 2)
      assert (bal_sol["z"] == 1)
      print "===================="
      print "Balanced day0 passed!"
    if day==1:
      assert (bal_sol["y"] == 3)
      assert (bal_sol["z"] == 3)
      print "===================="
      print "Balanced day1 passed!"

    z = bal_sol["z"]

    # create skill matrix
    w = np.zeros((8, 4))
    for i in range(8):
      if i%2 == 0:
        w[i][0] = 1
        w[i][2] = 1
      else:
        w[i][1] = 1
        w[i][3] = 1
      for i in range(4):
        w[i][i] = 0

    exp_mdl = day_ip.build_expert(z-1, z+1, w)
    exp_sol = exp_mdl.solve(log_output = False)

    for team in day_ip.teams:
      for task_index in day_ip.task_indices:
        assignment[team][day_ip.tasks[task_index]] = exp_sol["x_{}_{}".format(team, task_index)]

    if day==0:
      day0 = np.zeros((8,8))
      for i in range(4):
        day0[:, i] = w[:, i]
      assert np.all(assignment==day0)
      print "===================="
      print "Expert day0 passed"
    if day==1:
      day1 = np.zeros((8,8))
      for i in range(4):
        day1[:, i] = w[:, i]
        day1[:, (i+4)] = w[:, i]
      assert np.all(assignment==day1)
      print "===================="
      print "Expert day1 passed!"

def main():
  ip_tests()
  make_skill_from_file_test()

if __name__ == "__main__":
    main()



