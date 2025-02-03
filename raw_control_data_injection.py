import os
import glob
import numpy as np
from MORAI_data_receiver.receiver.ego_info_receiver import EgoInfoReceiver
import threading
import time
from math import sqrt
import pandas as pd
from datetime import datetime
import progressbar
from time import sleep


scenario_list = glob.glob('dataset/raw_data_real_mohave/XRP_DAQ_BIN_LAND/XRP_CSV/*_processed.csv')
target_scenario_id = 0
target_scenario = scenario_list[target_scenario_id]

cols = [i for i in range(14)]
cols.pop(3)

data = np.loadtxt(target_scenario, delimiter=',', skiprows=1, usecols=cols)

zero_idx = np.where(data[:,7] == 0)[0]
seg_ind = []

for i in range(len(zero_idx)):
    if i == 0:
        pass
    else:
        if zero_idx[i] - zero_idx[i-1] != 1:
            seg_ind.append([zero_idx[i-1], zero_idx[i]])

data_segment = []
data_segment_lowfreq = []
target_framerate = 20
for i in range(len(seg_ind)):
    data_sub = data[seg_ind[i][0]:seg_ind[i][1],:]
    data_sub[:,1] = data_sub[:,1] - data_sub[0,1]
    data_segment.append(data_sub)

for i in range(data_segment):
    data_tmp = data_segment[i]




network = dict()
network['host_ip'] = '127.0.0.1'
network['ego_info_dst_port'] = 909
ego_info_receiver = EgoInfoReceiver(network['host_ip'], network['ego_info_dst_port'])

FrameNumber = len(data)
IndexID = [0 for i in range(FrameNumber)]
TimeStamp = [0 for i in range(FrameNumber)]
TimeInfo_nsecs = [0 for i in range(FrameNumber)]
LocalX = [0 for i in range(FrameNumber)]
LocalY = [0 for i in range(FrameNumber)]
LocalZ = [0 for i in range(FrameNumber)]
Yaw = [0 for i in range(FrameNumber)]
Velocity = [0 for i in range(FrameNumber)]
EngineRPM = [0 for i in range(FrameNumber)]
SteeringAngle = [0 for i in range(FrameNumber)]
AccelPedalRate = [0 for i in range(FrameNumber)]
BrakePedalRate = [0 for i in range(FrameNumber)]
YawRate = [0 for i in range(FrameNumber)]
Roll = [0 for i in range(FrameNumber)]
Pitch = [0 for i in range(FrameNumber)]
VehicleModel = [0 for i in range(FrameNumber)]
index = 0

ego_status = ego_info_receiver.parsed_data
