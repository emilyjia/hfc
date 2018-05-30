from task_assign import Task_assign
from skill_assign import Skill_assign
import numpy as np
import copy
import sys
import random

# ------------------------------------------
# Using same skill matrix,
# do day to day assignment vs. hindsight
# ------------------------------------------

def simulation(batch):
  total_days = 180/batch
  task_per_day = 10*batch
  task_count = task_per_day*total_days
  frac = 0.5
  rand = 0.2
  team_count = 22
  file_name = "skill_file.csv"
  skill_count = 6
  distribution = "uniform"
  timelimit = 10000

  average_hindsight = np.zeros((team_count, skill_count))
  average_day = np.zeros((team_count, skill_count))
  gap = 0
  total_skill = 0

  for trial in range(1):
    print "=========================="
    print "trial number" + str(trial)
    sa = Skill_assign(file_name, team_count, task_count, skill_count, distribution)
    assignment = np.zeros((team_count, task_count))
    task_skill_lst = sa.task_skill_lst
    team_task = sa.team_task
    task_per_skill = [sa.task_skill_lst.count(skill)+0.0 for skill in range(skill_count)]

    day_total_assignment = np.zeros((team_count, task_count))

    # ------------------------------------------
    # Greedy assignment
    # ------------------------------------------
    def greedy(day):
      cutoff = 3
      day_tasks = task_skill_lst[task_per_day*day: task_per_day*(day+1)]
      day_skills = team_task[:, range(task_per_day*day, task_per_day*(day+1))]
      for i in range(task_per_day):
        for team in sa.teams:
          task = day_tasks[i]
          if day_skills[team][task] > cutoff:
            day_total_assignment[team][i + task_per_day*day] = 1
      # randomly assign the rest
      for i in range(task_per_day):
        assignment = day_total_assignment[:, i + task_per_day*day]
        assigned = sum(assignment)
        indices = np.nonzero(assignment)[0]
        while (assigned < frac*team_count):
          rand_assign = random.randint(0, team_count-1)
          while (rand_assign in indices):
            rand_assign = random.randint(0, team_count-1)
          assignment[rand_assign] = 1
          indices = np.append(indices, rand_assign)
          assigned = sum(assignment)
        day_total_assignment[:, i+task_per_day*day] = assignment

    # ------------------------------------------
    # Day to day assignment
    # ------------------------------------------
    def day_to_day(day):
      day_ip = Task_assign(day_total_assignment, task_count = task_per_day, day = day, skill=team_task)
      day_random_assign = day_ip.round_robin()

      if day > 0:
        day_random_assign[:, range(day*task_per_day)] = 0
      bal_mdl = day_ip.build_balanced()
      bal_sol = bal_mdl.solve(log_output = False)
      z = bal_sol["z"]
      y = bal_sol["y"]
      exp_mdl = day_ip.build_expert(z-1, y)
      exp_sol = exp_mdl.solve(log_output = False)
      for team in day_ip.teams:
        for task_index in day_ip.task_indices:
          day_total_assignment[team][day_ip.tasks[task_index]] = exp_sol["x_{}_{}".format(team, task_index)]
      day_total_assignment = day_total_assignment + day_random_assign

    for day in range(total_days):
      if day%50==0 and day > 0:
          print day
      greedy(day)
      team_assignment_count = np.sum(day_total_assignment, axis=1)
      print gap
      gap += max(team_assignment_count) - min(team_assignment_count)

    day_team_skill_assignment = np.zeros((team_count, skill_count))
    for team in sa.teams:
      for task in sa.tasks:
        if day_total_assignment[team][task] ==1:
          day_team_skill_assignment[team][sa.task_skill_lst[task]] += 1

    # get total skill
    temp_skill = 0
    for team in sa.teams:
      for skill in sa.skills:
        temp_skill += day_team_skill_assignment[team][skill]*sa.team_skill_matrix[team][skill]
        total_skill += day_team_skill_assignment[team][skill]*sa.team_skill_matrix[team][skill]

    print temp_skill / 180.0

    # for team in sa.teams:
    #   for skill in sa.skills:
    #     day_team_skill_assignment[team][skill] /= task_per_skill[skill]
    # average_day = average_day + day_team_skill_assignment

  gap /= (trial + 1.0)
  gap /= total_days
  # gap /= total_days
  print "gap"
  print gap

  total_skill /= (trial + 1.0)
  total_skill /= total_days
  # total_skill /= total_days
  print "total skill"
  print total_skill

  # average_hindsight /= (trial+1.0)
  # average_day /= (trial+1.0)
  # np.savetxt("uni_hind.csv", average_hindsight, delimiter=",")
  # np.savetxt("uni_day.csv", average_day, delimiter=",")
    # np.savetxt("day.csv", day_team_skill_assignment, delimiter=",")

simulation(int(sys.argv[1]))

# ------------------------------------------
# Hindsight assignment, but hindsight is just a special case of day to day
# ------------------------------------------
  # ta_hindsight = Task_assign(assignment, task_count = task_count, skill = team_task)
  # random_assign = ta_hindsight.round_robin()
  # bal_mdl = ta_hindsight.build_balanced()
  # bal_sol = bal_mdl.solve(TimeLimit = timelimit)
  # y = bal_sol["y"]
  # z = bal_sol["z"]
  # exp_mdl = ta_hindsight.build_expert(z-1, y)
  # exp_sol = exp_mdl.solve(TimeLimit = timelimit)
  # for team in ta_hindsight.teams:
  #     for task_index in ta_hindsight.task_indices:
  #       assignment[team][ta_hindsight.tasks[task_index]] = exp_sol["x_{}_{}".format(team, task_index)]
  # all_assignment = assignment+random_assign

  # # get the number of assignments by team per skill
  # team_skill_assignment = np.zeros((team_count, skill_count))
  # for team in ta_hindsight.teams:
  #   for task in ta_hindsight.tasks:
  #     if all_assignment[team][task] == 1:
  #       team_skill_assignment[team][sa.task_skill_lst[task]] += 1
  # for team in sa.teams:
  #   for skill in sa.skills:
  #     team_skill_assignment[team][skill] /= task_per_skill[skill]
  # # np.savetxt("hindsight.csv", team_skill_assignment, delimiter=",")
  # average_hindsight = average_hindsight + team_skill_assignment



