import sys
import numpy as np

from docplex.mp.model import CpoModel
mdl = CpoModel()

from docplex.mp.model import Model
m = Model(name='hfc')

# each ifp is assigned to some fraction of teams
f = 0.5

# some fraction is made at random
r = 0.2

assignments =
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
k2 = ceiling((1-r)*f*N)

# L_i is updated number of IFP's assigned to team i

# First solve
# x_{ij}: is task j assigned to team i
# y: max assignment over all teams
# z: min assignment over all teams

# not sure how to initialize L
L = [0]*i

x = mdl.binary_var_matrix(range(1, i+1), range(1,j+1), "x", None)
y = md.integer_var(0, j,"y")
z = md.integer_var(0, j, "z")


mdl.add(mdl.minimize(y-z))

for team in range(1, i+1):
  mdl.add(y >= L[i-1] + (mdl.sum(x[i][j] for i = team))

for team in range(1, i+1):
  mdl.add(y >= L[i-1] + mdl.sum(x[i][j] for i = team))

for skill in range(1, j+1):
  mdl.add((mdl.sum(x[i][j] for j = skill) = k2)

for team in range(1, i+1):
  for skill in range(1, j+1):
    x[i][j]


# for every
for i in range()

