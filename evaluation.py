import os
import glob
import numpy as np

scenario_list = glob.glob('dataset/raw_data_real_mohave/XRP_DAQ_BIN_LAND/XRP_CSV/*.csv')
target_scenario_id = 0
target_scenario = scenario_list[target_scenario_id]

cols = [i for i in range(24)]
cols.pop(1)

data = np.loadtxt(target_scenario, delimiter=',', skiprows=1, usecols=cols)

