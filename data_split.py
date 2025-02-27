import glob
from datetime import datetime
import numpy as np
import os
import pickle

virtual_data_root = 'dataset/raw_data_virtual_mohave/SIM_DAQ_BIN_LAND/SIM_CSV/*downsampled.csv'
real_data_root = 'dataset/raw_data_real_mohave/XRP_DAQ_BIN_LAND/XRP_CSV/*downsampled.csv'
SIM_data_list = glob.glob(virtual_data_root)
real_data_list = glob.glob(real_data_root)

config = dict()
config['batch_size'] = 32
config['train_rate'] = 0.7
config['test_rate'] = 0.3
config['historical_time_horizon'] = 2
config['prediction_target_time_horizon'] = 3
config['sampling_rate'] = 10 # max.20hz

now = datetime.now()
date = now.strftime("%Y_%m_%d")
time = now.strftime("%H_%M_%S")

config['data_split_date'] = date
config['data_split_time'] = time
config['data_source'] = 'both' # sim / real / both

if config['data_source'] == 'sim':
    data_list = SIM_data_list
elif config['data_source'] == 'real':
    data_list = real_data_list
elif config['data_source'] == 'both':
    data_list = SIM_data_list + real_data_list

cols = [i for i in range(14)]
cols.pop(2)

for i in data_list:
    data = np.loadtxt(i, delimiter=',', skiprows=1, usecols=cols)
    for j in range(config['sampling_rate'] * config['historical_time_horizon']-1,
                   len(data)-config['sampling_rate'] * config['prediction_target_time_horizon']):


