import numpy as np

from MORAI_data_receiver.receiver.ego_info_receiver import EgoInfoReceiver
import os
import threading
import time
from math import sqrt
import pandas as pd


network = dict()
network['host_ip'] = '127.0.0.1'
network['ego_info_dst_port'] = 909
ego_info_receiver = EgoInfoReceiver(network['host_ip'], network['ego_info_dst_port'])

FrameNumber = 1500
SteeringAngle = [0 for i in range(1500)]
AccelPedalRate = [0 for i in range(1500)]
BrakePedalRate = [0 for i in range(1500)]
Velocity = [0 for i in range(1500)]
RollRate = [0 for i in range(1500)]
PitchRate = [0 for i in range(1500)]
YawRate = [0 for i in range(1500)]
LocalX = [0 for i in range(1500)]
LocalY = [0 for i in range(1500)]
LocalZ = [0 for i in range(1500)]
Roll = [0 for i in range(1500)]
Pitch = [0 for i in range(1500)]
Yaw = [0 for i in range(1500)]
TimeStamp = [0 for i in range(1500)]
VehicleModel = [0 for i in range(1500)]

index = 0
while True:
    ego_status = ego_info_receiver.parsed_data
    if np.asarray(ego_status).sum() == 0:
        pass
    else:
        print(index)
        SteeringAngle[index] = ego_status[24] # steering angle of the tire in degree, left turn (-) , right turn (+)
        AccelPedalRate[index] = ego_status[4] # activation ratio of the accel pedal, normalized to 0 ~ 1
        BrakePedalRate[index] = ego_status[5] # activation ratio of the brake pedal, normalized to 0 ~ 1

        Velocity[index] = np.abs(ego_status[2]) / 3.6 # in meter per second
        RollRate[index] = np.deg2rad(ego_status[25]) # radian per second, left turn (+), right turn (-)
        PitchRate[index] = np.deg2rad(ego_status[26]) # radian per second, brake (+), accel (-)
        YawRate[index] = np.deg2rad(ego_status[27]) # radian per second, left turn (+), right turn (-)

        LocalX[index] = ego_status[12]
        LocalY[index] = ego_status[13]
        LocalZ[index] = ego_status[14]
        Roll[index] = ego_status[15]
        Pitch[index] = ego_status[16]
        Yaw[index] = ego_status[17]
        if index == 0:
            TimeStamp[index] = 0
            StartTime = time.time()
            init = 0
        else:
            TimeStamp[index] = time.time() - StartTime

        VehicleModel[index] = 'IONIQ_HEV'
        index = index + 1
        if index > FrameNumber-1:
            break
        time.sleep(0.1)


df = pd.DataFrame({'TimeStamp': TimeStamp,
                   'VehicleModel': VehicleModel,
                   'SteeringAngle': SteeringAngle,
                   'AccelPedalRate': AccelPedalRate,
                   'BrakePedalRate': BrakePedalRate,
                   'Velocity': Velocity,
                   'YawRate': YawRate,
                   'RollRate': RollRate,
                   'PitchRate': PitchRate,
                   'LocalX': LocalX,
                   'LocalY': LocalY,
                   'LocalZ': LocalZ,
                   'Roll': Roll,
                   'Pitch': Pitch,
                   'Yaw': Yaw})

DataGroupList = os.listdir('dataset/')
index = [int(DataGroupList[i][DataGroupList[i].find("Group")+5]) for i in range(len(DataGroupList))]

os.mkdir('dataset/Group' + str(np.max(index)+1))
df.to_csv('dataset/Group' + str(np.max(index)+1) + '/sample.csv', index=False)
