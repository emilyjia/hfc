import sys
import random
from itertools import cycle
import numpy as np
import unittest
import ip

def small_balance_test(frac, rand, team_count, task_count)
  ip.frac = frac
  ip.rand = rand
  ip.team_count = team_count
  ip.task_count = task_count
  ip.assignment = round_robin_test()
  balanced()

# to do: instead of printing output, turn into matrix

def round_robin_test(team_count, task_count, k1):
  tasks = range(task_count)
  assignment = np.zeros((team_count, task_count))
  order = cycle(ip.teams)
  for ifp in tasks:
    for k in range(0, k1):
      assignment[next(order), ifp] = 1
  return assignment

assert np.all(round_robin_test(4, 2, 2) == [[1,0], [1,0], [0,1], [0,1]])



