import json
import numpy as np
import csv
import pandas as pd
import random
from utils.utils import data_interpolation, DataExtractor
import glob
import torch
import os


def interpolation(time_cur, time_prev, time_next, value_prev, value_next):
    value_cur = value_prev + ((time_cur - time_prev) / (time_next - time_prev)) * (value_next - value_prev)
    return value_cur


TimeGap = 0.05

DataList = (glob.glob('dataset/raw_data_real_mohave/XRP_DAQ_BIN_LAND/XRP_CSV/*_processed.csv') +
            glob.glob('dataset/raw_data_virtual_mohave/SIM_DAQ_BIN_LAND/SIM_CSV/*_processed.csv') +
            glob.glob('raw_data_real_mohave/XRP_DAQ_BIN_LAND/XRP_CSV/*_processed.csv') +
            glob.glob('raw_data_virtual_mohave/SIM_DAQ_BIN_LAND/SIM_CSV/*_processed.csv'))

cols = [i for i in range(15)]
cols.pop(3)
vehicle_name = 'MOHAVE'
for dataid in range(len(DataList)):
    data = np.loadtxt(DataList[dataid], delimiter=',', skiprows=1, usecols=cols)
    downsampled_frame_num = int(data[-1, 1] / 0.05)

    IndexID = [0 for i in range(downsampled_frame_num)]
    TimeStamp = [0 for i in range(downsampled_frame_num)]
    LocalX = [0 for i in range(downsampled_frame_num)]
    LocalY = [0 for i in range(downsampled_frame_num)]
    LocalZ = [0 for i in range(downsampled_frame_num)]
    Yaw = [0 for i in range(downsampled_frame_num)]
    Velocity = [0 for i in range(downsampled_frame_num)]
    EngineRPM = [0 for i in range(downsampled_frame_num)]
    SteeringAngle = [0 for i in range(downsampled_frame_num)]
    AccelPedalRate = [0 for i in range(downsampled_frame_num)]
    BrakePedalRate = [0 for i in range(downsampled_frame_num)]
    YawRate = [0 for i in range(downsampled_frame_num)]
    Roll = [0 for i in range(downsampled_frame_num)]
    Pitch = [0 for i in range(downsampled_frame_num)]
    VehicleModel = ['MOHAVE' for i in range(downsampled_frame_num)]

    for targetindex in range(downsampled_frame_num):
        if targetindex == 0:
            IndexID[targetindex] = targetindex + 1
            TimeStamp[targetindex] = data[targetindex, 1]
            LocalX[targetindex] = data[targetindex, 3]
            LocalY[targetindex] = data[targetindex, 4]
            LocalZ[targetindex] = data[targetindex, 5]
            Yaw[targetindex] = data[targetindex, 6]
            Velocity[targetindex] = data[targetindex, 7]
            EngineRPM[targetindex] = data[targetindex, 8]

            SteeringAngle[targetindex] = data[targetindex, 9]
            AccelPedalRate[targetindex] = data[targetindex, 10]
            BrakePedalRate[targetindex] = data[targetindex, 11]

            YawRate[targetindex] = data[targetindex, 12]
            Pitch[targetindex] = data[targetindex, 13]
        else:
            IndexID[targetindex] = targetindex + 1
            TimeStamp[targetindex] = targetindex * TimeGap

            tmp = data[:, 1] - (targetindex * TimeGap)
            prev_index = np.argmax(tmp[tmp<0])
            LocalX[targetindex] = interpolation(targetindex * TimeGap, data[prev_index, 1], data[prev_index+1,1], data[prev_index, 3], data[prev_index+1,3])
            LocalY[targetindex] = interpolation(targetindex * TimeGap, data[prev_index, 1], data[prev_index+1,1], data[prev_index, 4], data[prev_index+1,4])
            LocalZ[targetindex] = interpolation(targetindex * TimeGap, data[prev_index, 1], data[prev_index+1,1], data[prev_index, 5], data[prev_index+1,5])
            Yaw[targetindex] = interpolation(targetindex * TimeGap, data[prev_index, 1], data[prev_index+1,1], data[prev_index, 6], data[prev_index+1,6])
            Velocity[targetindex] = interpolation(targetindex * TimeGap, data[prev_index, 1], data[prev_index+1,1], data[prev_index, 7], data[prev_index+1,7])
            EngineRPM[targetindex] = interpolation(targetindex * TimeGap, data[prev_index, 1], data[prev_index+1,1], data[prev_index, 8], data[prev_index+1,8])

            SteeringAngle[targetindex] = interpolation(targetindex * TimeGap, data[prev_index, 1], data[prev_index+1,1], data[prev_index, 9], data[prev_index+1,9])
            AccelPedalRate[targetindex] = interpolation(targetindex * TimeGap, data[prev_index, 1], data[prev_index+1,1], data[prev_index, 10], data[prev_index+1,10])
            BrakePedalRate[targetindex] = interpolation(targetindex * TimeGap, data[prev_index, 1], data[prev_index+1,1], data[prev_index, 11], data[prev_index+1,11])

            YawRate[targetindex] = interpolation(targetindex * TimeGap, data[prev_index, 1], data[prev_index+1,1], data[prev_index, 12], data[prev_index+1,12])
            Pitch[targetindex] = interpolation(targetindex * TimeGap, data[prev_index, 1], data[prev_index+1,1], data[prev_index, 13], data[prev_index+1,13])


    for i in range(len(TimeStamp)):
        if i == 0 or i == len(TimeStamp)-1:
            Velocity[i] = np.NAN
        else:
            prev_pos = np.asarray([LocalX[i-1], LocalY[i-1], LocalZ[i-1]])
            cur_pos = np.asarray([LocalX[i], LocalY[i], LocalZ[i]])
            next_pos = np.asarray([LocalX[i+1], LocalY[i+1], LocalZ[i+1]])
            dist_prev =np.sqrt(np.sum((cur_pos-prev_pos)**2, axis=0))
            dist_next =np.sqrt(np.sum((next_pos - cur_pos)**2, axis=0))
            Velocity[i] = ((dist_prev + dist_next) / TimeGap)/2

    data_downsampled_final = [i+1 for i in range(len(Velocity)-2)]
    df = pd.DataFrame({'INDEX': [IndexID[i] for i in data_downsampled_final],
                       'TimeStamp': [TimeStamp[i] for i in data_downsampled_final],
                        # Duplicated mode 삭제
                       'VehicleModel': [vehicle_name for i in data_downsampled_final],
                       'LocalX': [LocalX[i] for i in data_downsampled_final],
                       'LocalY': [LocalY[i] for i in data_downsampled_final],
                       'LocalZ': [LocalZ[i] for i in data_downsampled_final],
                       'Yaw': [Yaw[i] for i in data_downsampled_final],
                       'Velocity': [Velocity[i] for i in data_downsampled_final],
                       'EngineRPM': [EngineRPM[i] for i in data_downsampled_final],
                       'SteeringAngle': [SteeringAngle[i] for i in data_downsampled_final],
                       'AccelPedalRate': [AccelPedalRate[i] for i in data_downsampled_final],
                       'BrakePedalRate': [BrakePedalRate[i] for i in data_downsampled_final],
                       'YawRate': [YawRate[i] for i in data_downsampled_final],
                       'Pitch': [Pitch[i] for i in data_downsampled_final]})

    name = DataList[dataid][:DataList[dataid].find("processed")-1] + "_downsampled.csv"
    df.to_csv(name, index=False, mode='x')

