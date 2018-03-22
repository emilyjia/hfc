import sys
import random
from itertools import cycle
import numpy as np
import unittest
import ip
import math

# ------------------------------------------
# Small_balance_test changes constants in ip.py
# Uses round_robin_test (non-random priority order)
# ip.assignment = round_robin_test output
# bal_sol = [y, z]
# exp_sol = expert assignment
# Maybe I could use a class?
# ------------------------------------------

def make_skill_test(team_count, task_count, skill_count, worker_count):
  ip.team_count = team_count
  ip.teams = range(team_count)
  ip.task_count = task_count
  ip.tasks = range(task_count)
  print ip.make_skill(skill_count, worker_count)

def small_balance_test(frac, rand, team_count, task_count, w):
  # sets constants... maybe I should use a class
  ip.frac = frac
  ip.rand = rand
  ip.team_count = team_count
  ip.teams = range(team_count)
  ip.task_count = task_count
  ip.tasks = range(task_count)
  ip.k1 = int(math.ceil(rand*frac*team_count))
  print rand
  print frac
  print team_count
  print ip.k1
  ip.k2 = int(math.ceil((1-rand)*frac*team_count))
  print ip.k2
  ip.assignment = round_robin_test(ip.team_count, ip.task_count, ip.k1)
  ip.L = [sum(ip.assignment[team]) for team in ip.teams]

  # gets [y, z]
  bal_sol = ip.balanced()
  z = bal_sol[1]
  z_floor = z-1
  z_ceil = z+1

  # gets expert assignment
  exp_sol = ip.expert(z_floor, z_ceil, w)

  return [ip.assignment, bal_sol, exp_sol]

# ------------------------------------------
# Priority order is teams in order of index
# ------------------------------------------

def round_robin_test(team_count, task_count, k1):
  tasks = range(task_count)
  assignment = np.zeros((team_count, task_count))
  order = cycle(ip.teams)
  for ifp in tasks:
    for k in range(0, k1):
      assignment[next(order), ifp] = 1
  return assignment

def tests():
  print "Starting Tests..."
  print "======================="
  assert np.all(round_robin_test(4, 2, 2) == [[1,0], [1,0], [0,1], [0,1]])
  print "Round Robin Test passed"

  a = np.zeros((8, 4))
  for i in range(4):
    a[i][i] = 1

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


  sol = small_balance_test(0.5, 0.25, 8, 4, w)
  assert np.all(sol[0] == a)
  print "Round Robin Test passed again"
  assert np.all(sol[1][0] == 2)
  print "y computed correctly"
  assert np.all(sol[1][1] == 2)
  print "z computed correctly"
  print w
  assert np.all(sol[2] == w)
  print "expert computed correctly"
  print "All tests done!"


tests()


