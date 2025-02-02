import numpy as np

# from receiver.ego_info_receiver import EgoInfoReceiver
from MORAI_data_receiver.receiver.ego_info_receiver import EgoInfoReceiver
import os
import threading
import time
from math import sqrt
import pandas as pd
from datetime import datetime
import progressbar
from time import sleep


network = dict()
network['host_ip'] = '127.0.0.1'
network['ego_info_dst_port'] = 909
ego_info_receiver = EgoInfoReceiver(network['host_ip'], network['ego_info_dst_port'])

FrameNumber = 100000
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

bar = progressbar.ProgressBar(maxval=FrameNumber, widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
bar.start()

while True:
    ego_status = ego_info_receiver.parsed_data
    if np.asarray(ego_status).sum() == 0:
        pass
    else:
        #
        # [secs, nsecs, ctrl_mode, gear, signed_vel, map_id, accel, brake, size_x, size_y,
        #  size_z, overhang, wheelbase, rear_overhang, pos_x, pos_y, pos_z, roll, pitch, yaw,
        #  vel_x, vel_y, vel_z, ang_vel_x, ang_vel_y, ang_vel_z, acc_x, acc_y, acc_z, steer,
        #  link_id, tire_lateral_force_fl, tire_lateral_force_fr, tire_lateral_force_rl, tire_lateral_force_rr, side_slip_angle_fl, side_slip_angle_fr, side_slip_angle_rl, side_slip_angle_rr, tire_cornering_stiffness_fl,
        #  tire_cornering_stiffness_fr, tire_cornering_stiffness_rl, tire_cornering_stiffness_rr
        #
        bar.update(index + 1)
        if index == 0:
            now = datetime.now()
            start_date = now.strftime("%Y%m%d")
            start_time = now.strftime("%H%M%S")

            IndexID[index] = index + 1
            TimeStamp[index] = 0
            StartTime = time.time()

            TimeInfo_nsecs[index] = ego_status[1]

            LocalX[index] = ego_status[14]
            LocalY[index] = ego_status[15]
            LocalZ[index] = ego_status[16]

            Yaw[index] = ego_status[19]
            Velocity[index] = np.abs(ego_status[4]) / 3.6  # in meter per second
            EngineRPM[index] = 0

            SteeringAngle[index] = ego_status[
                29]  # steering angle of the tire in degree, left turn (-) , right turn (+)
            AccelPedalRate[index] = ego_status[6]  # activation ratio of the accel pedal, normalized to 0 ~ 1
            BrakePedalRate[index] = ego_status[7]  # activation ratio of the brake pedal, normalized to 0 ~ 1

            YawRate[index] = np.deg2rad(ego_status[27])  # radian per second, left turn (+), right turn (-)
            Roll[index] = ego_status[15]
            Pitch[index] = ego_status[16]

            VehicleModel[index] = 'MOHAVE'

            index = index + 1

        else:
            if ego_status[1] != TimeInfo_nsecs[index-1]:
                IndexID[index] = index + 1
                TimeStamp[index] = time.time() - StartTime
                TimeInfo_nsecs[index] = ego_status[1]

                LocalX[index] = ego_status[14]
                LocalY[index] = ego_status[15]
                LocalZ[index] = ego_status[16]

                Yaw[index] = ego_status[19]
                Velocity[index] = np.abs(ego_status[4]) / 3.6  # in meter per second
                EngineRPM[index] = 0

                SteeringAngle[index] = ego_status[
                    29]  # steering angle of the tire in degree, left turn (-) , right turn (+)
                AccelPedalRate[index] = ego_status[6]  # activation ratio of the accel pedal, normalized to 0 ~ 1
                BrakePedalRate[index] = ego_status[7]  # activation ratio of the brake pedal, normalized to 0 ~ 1

                YawRate[index] = np.deg2rad(ego_status[27])  # radian per second, left turn (+), right turn (-)
                Roll[index] = ego_status[15]
                Pitch[index] = ego_status[16]

                VehicleModel[index] = 'MOHAVE'
                index = index + 1

            else:
                pass


        if index > FrameNumber-1:
            now = datetime.now()
            end_date = now.strftime("%Y%m%d")
            end_time = now.strftime("%H%M%S")
            bar.finish()
            break
        time.sleep(0.001)



df = pd.DataFrame({'INDEX': IndexID,
                   'TimeStamp': TimeStamp,
                   'TimeInfo_nsecs': TimeInfo_nsecs,
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

root_name = 'dataset/raw_data_virtual_mohave/SIM_DAQ_BIN_LAND/SIM_CSV/'
file_name = 'SIM_ASC_FROM_'+start_date+'_'+start_time+'_TO_'+end_date+'_'+end_time+'.csv'

df.to_csv(root_name+file_name, index=False)
