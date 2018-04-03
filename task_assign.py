import random
from itertools import cycle
import numpy as np
import pandas as pd
import docplex
import math
from docplex.mp.model import Model

class Task_assign:
  def __init__(self, assignment, frac = 0.5, rand = 0.2, team_count = 1500, task_count = 10, task_skill = [], day = 0):
    self.frac = frac
    self.rand = rand
    self.team_count = team_count
    self.task_count = task_count
    self.day = day
    self.assignment = assignment
    self.skill = np.zeros((team_count, task_count))
    # get rid of expired tasks
    for i in range(self.day-30):
      self.assignment[:, i] = np.zeros(self.team_count)

    self.teams = range(self.team_count)
    # tasks does not start at 0
    self.tasks = range(self.day*self.task_count, (self.day+1)*self.task_count)
    self.task_indices = range(self.task_count)
    # number of random assignments
    self.k1 = int(math.ceil(rand*frac*team_count))
    # number of non-random assignments
    self.k2 = int(math.ceil((1-rand)*frac*team_count))


# ------------------------------------------
# Round robin assignment
# ------------------------------------------

  def round_robin(self):
    # we use the actual task numbers
    priority_order = range(self.team_count)
    random.shuffle(priority_order) #random priority order
    order = cycle(priority_order)
    for task in self.tasks:
      for k in range(0, self.k1):
        self.assignment[next(order), task] = 1

# ------------------------------------------
# Balanced Solution
# x[(i, j)]: is task j assigned to team i
# y: max assignment over all teams
# z: min assignment over all teams
# for assignment we use actual task number
# ------------------------------------------

  def build_balanced(self):
    mdl = Model()
    mdl.context.solver.agent = 'local'
    mdl.context.solver.log_output = True
    timelimit = 10000
    #L_i is number of IFP's assigned to i
    L = [sum(self.assignment[team]) for team in self.teams]

    x = mdl.binary_var_matrix(self.team_count, self.task_count, name = "x")
    y = mdl.integer_var(0, self.task_count, "y")
    z = mdl.integer_var(0, self.task_count, "z")
    mdl.minimize(y-z)

    for team in self.teams:
       mdl.add_constraint(y >= (L[team] + mdl.sum(x[(team, task_index)] for task_index in self.task_indices)))

    for team in self.teams:
      mdl.add_constraint(z <= (L[team] + mdl.sum(x[(team, task_index)] for task_index in self.task_indices)))

    for task_index in self.task_indices:
      mdl.add_constraint((mdl.sum(x[(team, task_index)] for team in self.teams)== self.k2))

    for team in self.teams:
      for task_index in self.task_indices:
        if self.assignment[team][self.tasks[task_index]] == 1 :
          mdl.add_constraint(x[(team, task_index)] == 0)

    return mdl

  def build_expert(self, z_floor, z_ceil, skill):
    mdl = Model()
    mdl.context.solver.agent = 'local'
    mdl.context.solver.log_output = True
    timelimit = 10000
    L = [sum(self.assignment[team]) for team in self.teams]
    #L_i is number of IFP's assigned to i
    x = mdl.binary_var_matrix(self.team_count, self.task_count, name = "x")

    lst = []
    for team in self.teams:
      lst.append(mdl.sum(x[(team, task_index)] * skill[team][task_index] for task_index in self.task_indices))

    mdl.maximize(mdl.sum(lst))

    for team in self.teams:
      mdl.add_constraint(z_floor <= mdl.sum(x[(team, task_index)] for task_index in self.task_indices) + L[team])
      mdl.add_constraint((mdl.sum(x[(team, task_index)] for task_index in self.task_indices) + L[team])<= max(L[team], z_ceil))

    for task_index in self.task_indices:
      mdl.add_constraint((mdl.sum(x[(team, task_index)] for team in self.teams)== self.k2))

    for team in self.teams:
      for task_index in self.task_indices:
        if self.assignment[team][self.tasks[task_index]] == 1 :
          mdl.add_constraint((x[(team, task_index)] == 0))

    return mdl


  # ------------------------------------------
  # Make the skill matrix
  # ------------------------------------------

  def make_skill(self, skill_count, worker_count):
    skills = range(skill_count)
    workers = range(worker_count)
    w = np.zeros((self.team_count, self.task_count))
    team_skill = np.zeros((self.team_count, skill_count))
    for team in self.teams:
      for skill in skills:
        skill_value = 0
        for worker in workers:
          skill_value += np.random.normal()
        team_skill[team][skill] = skill_value
    for task in self.tasks:
      skill = np.random.randint(skill_count)
      for team in self.teams:
        w[team][task] = team_skill[team][skill]
    return w

  # ------------------------------------------
  # Team by skill
  # ------------------------------------------

  def make_skill_from_file(self, file_name, skill_count):
    input = pd.read_csv(file_name)
    team_skill_matrix = np.zeros((self.team_count, skill_count))
    for team in self.teams:
      skill_row = input[input.team_no==team].sum()
      for skill in range(skill_count):
        skill_name = "knowcat_" + str(skill +1)
        team_skill_matrix[team][skill] = skill_row[skill_name]
    return team_skill_matrix

  def make_team_task(self, team_skill_matrix, task_skill_list, skill_count):
    team_task_matrix = np.zeros(self.team_count, self.task_count)
    for team in self.teams:
      for task in self.tasks:
        team_task_matrix[team][task] = team_skill_matrix[team][task_skill_list[task]]

def main():
  total_days = 1
  task_per_day = 10
  total_tasks = total_days*task_per_day
  team_count = 1500
  assignment = np.zeros((team_count, total_tasks))
  timelimit = 10000
  skill_count = 6
  worker_count = 5

  for day in range(total_days):
    day_ip = Task_assign(assignment, team_count = team_count, task_count = task_per_day, day = day)
    day_ip.round_robin()
    bal_mdl = day_ip.build_balanced()
    bal_sol = bal_mdl.solve(TimeLimit = timelimit)

    skill = day_ip.make_skill(skill_count, worker_count)

    z = bal_sol["z"]
    exp_mdl = day_ip.build_expert(z-1, z+1, skill)
    exp_sol = exp_mdl.solve(TimeLimit = timelimit)

    for team in day_ip.teams:
      for task_index in day_ip.task_indices:
        assignment[team][day_ip.tasks[task_index]] = exp_sol["x_{}_{}".format(team, task_index)]


if __name__ == "__main__":
    main()














