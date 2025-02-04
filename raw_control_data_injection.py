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
import time
import sys
from pathlib import Path
import ctypes

sys.path.append(str(Path(__file__).resolve().parents[2]))

from MORAI_data_receiver.sender.UDP import Sender
from MORAI_data_receiver.sender.EgoCtrlCmd import EgoCtrlCmd

IP = '127.0.0.1'
PORT = 9093

# Protocol정보
# https://help-morai-sim.scrollhelp.site/ko/morai-sim-drive/24.R2/ros-1#id-(24.R2-ko)통신메시지프로토콜-EgoCtrlCmd.1
"""
Ego Ghost Mode를 사용하기 위해서 Network setting > Cmd Control을 MoraiGhostCmdController로 Connect 해야함
'Q' 를 눌러 Ego Controller를 AV- ExternalCtrl로 설정 해야 동작함.
아래 예제는 특정 주차공간에 Ego 차량을 Ghost Mode로 위치 시켰지만
Log 파일이나, 다른 실시간 데이터를 받아 위치/자세 값을 반복적으로 송신하면 차량이 주행하는 것처럼 보임.
"""

ego_ctrl = Sender(IP, PORT)
cmd = EgoCtrlCmd()
cmd.ctrl_mode = 2  # 1 : Keyboard   2 : AutoMode
cmd.gear = 4
cmd.cmd_type = 1

scenario_list = glob.glob('dataset/raw_data_real_mohave/XRP_DAQ_BIN_LAND/XRP_CSV/*_downsampled.csv')
target_scenario_id = 0
target_scenario = scenario_list[target_scenario_id]

cols = [i for i in range(14)]
cols.pop(2)

data = np.loadtxt(target_scenario, delimiter=',', skiprows=1, usecols=cols)

zero_idx = np.where(data[:, 6] < 0.02)[0]
seg_ind = []

for i in range(len(zero_idx)):
    if i == 0:
        pass
    else:
        if zero_idx[i] - zero_idx[i - 1] != 1:
            if zero_idx[i] - zero_idx[i - 1] > 100:
                seg_ind.append([zero_idx[i - 1], zero_idx[i]])

data_segment = []
for i in range(len(seg_ind)):
    data_sub = data[seg_ind[i][0]:seg_ind[i][1], :]
    data_sub[:, 1] = data_sub[:, 1] - data_sub[0, 1]
    data_segment.append(data_sub)

network = dict()
network['host_ip'] = '127.0.0.1'
network['ego_info_dst_port'] = 909
ego_info_receiver = EgoInfoReceiver(network['host_ip'], network['ego_info_dst_port'])

for i in range(len(data_segment)):
    if i == 0:
        pass

    data_tmp = data_segment[i]

    FrameNumber = len(data_tmp)
    IndexID = [0 for i in range(FrameNumber)]
    TimeStamp = [0 for i in range(FrameNumber)]
    VehicleModel = ['MOHAVE' for i in range(FrameNumber)]
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
    Pitch = [0 for i in range(FrameNumber)]

    init_time = time.time()
    frame_id = 0
    while True:
        if frame_id == 0:
            for ii in range(3, 0, -1):
                sys.stdout.write(str(ii) + ' ')
                sys.stdout.flush()
                time.sleep(1)
            sys.stdout.write('start!')
            sys.stdout.flush()
            time.sleep(1)
            cmd.accel = data_tmp[frame_id, 9]
            cmd.brake = data_tmp[frame_id, 10]
            cmd.steer = -data_tmp[frame_id, 8] / 38  # -1 ~ 1
            ego_ctrl.send(cmd)

        cur_time = time.time()
        if cur_time - init_time > 0.05:

            if frame_id == 0:
                IndexID[frame_id] = data_tmp[frame_id, 0]
                TimeStamp[frame_id] = data_tmp[frame_id, 1]
                LocalX[frame_id] = data_tmp[frame_id, 2]
                LocalY[frame_id] = data_tmp[frame_id, 3]
                LocalZ[frame_id] = data_tmp[frame_id, 4]
                Yaw[frame_id] = data_tmp[frame_id, 5]
                Velocity[frame_id] = data_tmp[frame_id, 6]
                EngineRPM[frame_id] = data_tmp[frame_id, 7]
                SteeringAngle[frame_id] = data_tmp[frame_id, 8]
                AccelPedalRate[frame_id] = data_tmp[frame_id, 9]
                BrakePedalRate[frame_id] = data_tmp[frame_id, 10]
                YawRate[frame_id] = data_tmp[frame_id, 11]
                Pitch[frame_id] = data_tmp[frame_id, 12]
            else:
                ego_status = ego_info_receiver.parsed_data
                IndexID[frame_id] = data_tmp[frame_id, 0]
                TimeStamp[frame_id] = data_tmp[frame_id, 1]
                LocalX[frame_id] = ego_status[14]
                LocalY[frame_id] = ego_status[15]
                LocalZ[frame_id] = ego_status[16]
                Yaw[frame_id] = ego_status[19]
                Velocity[frame_id] = np.abs(ego_status[4]) / 3.6
                EngineRPM[frame_id] = 0
                SteeringAngle[frame_id] = ego_status[29]
                AccelPedalRate[frame_id] = ego_status[6]
                BrakePedalRate[frame_id] = ego_status[7]
                YawRate[frame_id] = np.deg2rad(ego_status[25])
                if ego_status[18] > 300:
                    pitch = 360 - ego_status[18]
                else:
                    pitch = - ego_status[18]
                Pitch[frame_id] = pitch

            frame_id = frame_id + 1
            cmd.accel = data_tmp[frame_id, 9]
            cmd.brake = data_tmp[frame_id, 10]
            cmd.steer = -data_tmp[frame_id, 8] / 38  # -1 ~ 1
            ego_ctrl.send(cmd)

            init_time = time.time()

        if frame_id == FrameNumber - 1:
            break
        time.sleep(0.001)

    df_new = pd.DataFrame({'INDEX': IndexID,
                           'TimeStamp': TimeStamp,
                           'VehicleModel': VehicleModel,
                           'LocalX': LocalX,
                           'LocalY': LocalY,
                           'LocalZ': LocalZ,
                           'Yaw': Yaw,
                           'Velocity': Velocity,
                           'EngineRPM': EngineRPM,
                           'SteeringAngle': SteeringAngle,
                           'AccelPedalRate': AccelPedalRate,
                           'BrakePedalRate': BrakePedalRate,
                           'YawRate': YawRate,
                           'Pitch': Pitch})
    name = 'performance evaluation/' + target_scenario[target_scenario.find("\\")+1:-4] + '_VPP_injection_from_sim_' + str(i) +'_.csv'
    df_new.to_csv(name, index=False, mode='x')

    df_original = pd.DataFrame({'INDEX': list(data_tmp[:, 0]),
                                'TimeStamp': list(data_tmp[:, 1]),
                                'VehicleModel': VehicleModel,
                                'LocalX': list(data_tmp[:, 2]),
                                'LocalY': list(data_tmp[:, 3]),
                                'LocalZ': list(data_tmp[:, 4]),
                                'Yaw': list(data_tmp[:, 5]),
                                'Velocity': list(data_tmp[:, 6]),
                                'EngineRPM': list(data_tmp[:, 7]),
                                'SteeringAngle': list(data_tmp[:, 8]),
                                'AccelPedalRate': list(data_tmp[:, 9]),
                                'BrakePedalRate': list(data_tmp[:, 10]),
                                'YawRate': list(data_tmp[:, 11]),
                                'Pitch': list(data_tmp[:, 12])})
    name = 'performance evaluation/' + target_scenario[target_scenario.find("\\")+1:-4] + '_VPP_injection_original_' + str(i) +'_.csv'
    df_original.to_csv(name, index=False, mode='x')

# todo
# from_sim데이터 초기값, 기어비 차이로 인한 steer angle값 등등 체크 필요 