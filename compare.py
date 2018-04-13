from task_assign import Task_assign
from skill_assign import Skill_assign
import numpy as np
import copy

# ------------------------------------------
# Using same skill matrix,
# do day to day assignment vs. hindsight
# ------------------------------------------

def simulation():
  total_days = 180
  task_per_day = 10
  task_count = task_per_day*total_days
  frac = 0.5
  rand = 0.2
  team_count = 22
  file_name = "skill_file.csv"
  skill_count = 6
  distribution = "uniform"
  timelimit = 10000

  sa = Skill_assign(file_name, team_count, task_count, skill_count, distribution)
  assignment = np.zeros((team_count, task_count))
  team_task = sa.team_task

  # ------------------------------------------
  # Hindsight assignment
  # ------------------------------------------

  ta_hindsight = Task_assign(assignment, task_count = task_count, skill = team_task)
  # random_assign = ta_hindsight.round_robin()
  # bal_mdl = ta_hindsight.build_balanced()
  # bal_sol = bal_mdl.solve(TimeLimit = timelimit)
  # z = bal_sol["z"]
  # exp_mdl = ta_hindsight.build_expert(z-1, z+1)
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
  # print team_skill_assignment

  # day to day assignments
  day_total_assignment = np.zeros((team_count, task_count))
  for day in range(total_days):
    print day
    day_ip = Task_assign(day_total_assignment, task_count = task_per_day, day = day, skill=team_task)
    day_random_assign = day_ip.round_robin()
    if day > 0:
      day_random_assign[:, range(day*task_per_day)] = 0
    # f_handle = file('random.csv', 'a')
    # np.savetxt(f_handle, day_random_assign, delimiter=",")
    # f_handle.close()
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
    f_handle = file('random.csv', 'a')
    np.savetxt(f_handle, day_random_assign, delimiter=",")
    f_handle.close()

  day_team_skill_assignment = np.zeros((team_count, skill_count))
  for team in ta_hindsight.teams:
    for task in ta_hindsight.tasks:
      if day_total_assignment[team][task] ==1:
        day_team_skill_assignment[team][sa.task_skill_lst[task]] += 1
  np.savetxt("count.csv", day_total_assignment, delimiter=",")


assignment = simulation()

