import sys
import random
from itertools import cycle
import numpy as np
import unittest

# test round robin
# i = teams, j = tasks, k_1 = assignments
def round_robin(i, j, k_1):
  assignment = np.zeros((i, j))
  o = cycle(range(0, i))
  for ifp in range(0, j):
    for i in range(0, k_1):
      assignment[next(o), ifp] = 1
  return assignment

assert np.all(round_robin(4, 2, 2) == [[1,0], [1,0], [0,1], [0,1]])

