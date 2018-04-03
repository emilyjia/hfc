from scipy.stats import norm
import numpy as np
import matplotlib.pyplot as plt
import random
import math
import pandas as pd

class Skill_assign:
  def __init__(self, file_name, team_count, task_count, skill_count, distribution):
    self.file_name = file_name
    self.team_count = team_count
    self.task_count = task_count
    self.skill_count = skill_count
    self.distribution = distribution
    self.skills = range(skill_count)
    self.teams = range(team_count)
    self.tasks = range(task_count)
    self.list_length = list_length
    self.team_skill_matrix = self.make_skill_from_file()
    self.prob_lst = self.make_prob_lst()
    self.task_skill_list = self.lst_from_prob()
    self.team_task = self.make_team_task()

  def make_skill_from_file(self):
    input = pd.read_csv(self.file_name)
    team_skill_matrix = np.zeros((self.team_count, self.skill_count))
    for team in self.teams:
      skill_row = input[input.team_no==team].sum()
      for skill in self.skills:
        skill_name = "knowcat_" + str(skill +1)
        team_skill_matrix[team][skill] = skill_row[skill_name]
    return team_skill_matrix

  def make_prob_lst(self):
    prob_lst = []
    if self.distribution == "uniform":
      for x in range(self.skill_count):
        prob_lst.append(1.0/self.skill_count)
    if self.distribution == "normal":
      # get pdf from -2.5 to 2.5 ish
      jump = 5.0/(self.skill_count+1)
      for x in skills:
        prob_lst.append(norm.pdf(-2.5 + jump*(x+1), loc=0, scale=1))
      prob_lst = [x/sum(self.prob_lst) for x in prob_lst]
    if self.distribution == "chunk":
      part = 1.0/(math.floor(self.skill_count/2.0) + 2.0*math.ceil(self.skill_count/2.0))
      for x in range(int(math.floor(self.skill_count/2.0))):
        prob_lst.append(part)
      for x in range(int(math.ceil(self.skill_count/2.0))):
        prob_lst.append(2.0*part)
    return prob_lst

  def lst_from_prob(self):
    cum_sum = 0
    cum_lst = [0]
    task_lst = []
    for x in range(len(self.prob_lst)):
      cum_sum += self.prob_lst[x]
      cum_lst.append(cum_sum)
    for x in self.tasks:
      rand = random.random()
      index = -1
      for y in range(1, len(cum_lst)):
        if rand >= cum_lst[y-1] and rand <= cum_lst[y]:
          index = y-1
      task_lst.append(index)
    return task_lst

  def make_team_task(self):
    team_task_matrix = np.zeros((self.team_count, self.task_count))
    for team in self.teams:
      for task in self.tasks:
        team_task_matrix[team][task] = self.team_skill_matrix[team][self.task_skill_list[task]]

  def get_next_team_task(self):
    self.task_skill_list = self.make_task_skill()
    self.team_task = self.make_team_task()


