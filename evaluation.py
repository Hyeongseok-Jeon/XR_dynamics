import os
import glob
import numpy as np

scenario_list = glob.glob('dataset/raw_data_real_mohave/*/*.csv')
target_scenario_id = 10
target_scenario = scenario_list[target_scenario_id]

data = np.loadtxt(target_scenario, delimiter=',', skiprows=1)

