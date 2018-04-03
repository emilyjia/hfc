from scipy.stats import norm
import numpy as np
import matplotlib.pyplot as plt
import random
import math

# ------------------------------------------
# Provides task_skill matrix
# ------------------------------------------

def make_task_skill(total_skill_list, list_length):
  random.shuffle(total_task_count)
  task_skill = []
  for x in range(list_length):
    task_skill.append(total_task_count.pop())

def make_prob_list(distribution, skill_count, task_count):
  prob_list = []
  if distribution == "uniform":
    for x in range(task_count):
      prob_list.append(1.0/skill_count)
  if distribution == "normal":
    # get pdf from -2.5 to 2.5 ish
    jump = 5.0/(skill_count+1)
    for x in range(skill_count):
      prob_list.append(norm.pdf(-2.5 + jump*(x+1), loc=0, scale=1))
    prob_list = [x/sum(prob_list) for x in prob_list]
  if distribution == "chunk":
    part = 1.0/(math.floor(skill_count/2.0) + 2.0*math.ceil(skill_count/2.0))
    for x in range(int(math.floor(skill_count/2.0))):
      prob_list.append(part)
    for x in range(int(math.ceil(skill_count/2.0))):
      prob_list.append(2.0*part)
  return prob_list

def list_from_prob(prob_list, task_count):
  cum_sum = 0
  cum_lst = [0]
  task_lst = []
  for x in range(len(prob_list)):
    cum_sum += prob_list[x]
    cum_lst.append(cum_sum)
  for x in range(task_count):
    rand = random.random()
    print rand
    index = -1
    for y in range(1, len(cum_lst)):
      if rand >= cum_lst[y-1] and rand <= cum_lst[y]:
        index = y-1
    task_lst.append(index)
  print task_lst


# prob_list = make_prob_list("normal", 6, 1000)
# list_from_prob(prob_list, 10)

