import os
import glob
import numpy as np
import progressbar
import datetime
import utm
import pandas as pd
import time
scenario_list_tot = glob.glob('dataset/raw_data_real_mohave/XRP_DAQ_BIN_LAND/XRP_CSV/*.csv')
scenario_list_processed = [scenario_list_tot[i] for i in range(len(scenario_list_tot)) if "processed" in scenario_list_tot[i]]
scenario_list = []
steering_ratio = 11.84210526315789

for i in range(len(scenario_list_tot)):
    if scenario_list_tot[i] in scenario_list_processed:
        pass
    else:
        basename = scenario_list_tot[i][:scenario_list_tot[i].find(".csv")]
        if basename+"_processed.csv" in scenario_list_processed:
            pass
        else:
            scenario_list.append(scenario_list_tot[i])

if len(scenario_list) == 0:
    pass
else:
    target_scenario_id = 0
    target_scenario = scenario_list[target_scenario_id]

    cols = [i for i in range(24)]
    cols.pop(1)

    data = np.loadtxt(target_scenario, delimiter=',', skiprows=1, usecols=cols)
    MaxFrameNumber = len(data)

    IndexID = [0 for i in range(MaxFrameNumber)]
    TimeStamp = [0 for i in range(MaxFrameNumber)]
    Duplicated_Sign = [0 for i in range(MaxFrameNumber)]
    LocalX = [0 for i in range(MaxFrameNumber)]
    LocalY = [0 for i in range(MaxFrameNumber)]
    LocalZ = [0 for i in range(MaxFrameNumber)]
    Yaw = [0 for i in range(MaxFrameNumber)]
    Velocity = [0 for i in range(MaxFrameNumber)]
    EngineRPM = [0 for i in range(MaxFrameNumber)]
    SteeringAngle = [0 for i in range(MaxFrameNumber)]
    AccelPedalRate = [0 for i in range(MaxFrameNumber)]
    BrakePedalRate = [0 for i in range(MaxFrameNumber)]
    YawRate = [0 for i in range(MaxFrameNumber)]
    Roll = [0 for i in range(MaxFrameNumber)]
    Pitch = [0 for i in range(MaxFrameNumber)]
    VehicleModel = [0 for i in range(MaxFrameNumber)]
    targetindex = 0
    sourceindex = 100

    bar = progressbar.ProgressBar(maxval=MaxFrameNumber, widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
    bar.start()
    #
    # LocalX[index] = ego_status[14]  # in meter
    # LocalY[index] = ego_status[15]  # in meter
    # LocalZ[index] = ego_status[16]  # in meter
    #
    # Yaw[index] = ego_status[19]  # south : -90 deg, east: 0 deg (-180 ~ 180 deg)
    # Velocity[index] = np.abs(ego_status[4]) / 3.6  # in meter per second
    # EngineRPM[index] = 0
    #
    # SteeringAngle[index] = ego_status[29]  # steering angle of the tire in degree, left turn (+) , right turn (-)
    # AccelPedalRate[index] = ego_status[6]  # activation ratio of the accel pedal, normalized to 0 ~ 1
    # BrakePedalRate[index] = ego_status[7]  # activation ratio of the brake pedal, normalized to 0 ~ 1
    #
    # YawRate[index] = np.deg2rad(ego_status[25])  # radian per second, left turn (+), right turn (-)
    # Roll[index] = roll  # degree, left up & right down (+) , left down & right up (-)
    # Pitch[index] = pitch  # degree, climb (+) , downhill (-)
    #
    # VehicleModel[index] = 'MOHAVE'
    #

    while True:
        bar.update(sourceindex + 1)
        if targetindex == 0:
            start_date = target_scenario[target_scenario.find("FROM")+5:target_scenario.find("FROM")+13]
            start_time = target_scenario[target_scenario.find(start_date)+9:target_scenario.find(start_date)+15]

            IndexID[targetindex] = targetindex + 1
            TimeStamp[targetindex] = 0

            StartTime = datetime.datetime(year=int(start_date[0:4]),
                                          month=int(start_date[4:6]),
                                          day=int(start_date[6:8]),
                                          hour=int(data[sourceindex, 11]),
                                          minute=int(data[sourceindex, 12]),
                                          second=int(data[sourceindex, 13]),
                                          microsecond=1000*int(data[sourceindex, 14])).timestamp()

            Duplicated_Sign[targetindex] = data[sourceindex, 22]

            utm_x, utm_y, _, _ = utm.from_latlon(data[sourceindex, 5], data[sourceindex, 6])
            LocalOrigin_X = utm_x
            LocalOrigin_Y = utm_y
            LocalOrigin_Z = data[sourceindex, 7]

            LocalX[targetindex] = 0
            LocalY[targetindex] = 0
            LocalZ[targetindex] = 0

            Yaw[targetindex] = 90 - data[sourceindex, 8]
            Velocity[targetindex] = data[sourceindex, 9]
            EngineRPM[targetindex] = 0

            SteeringAngle[targetindex] = -0.1 * data[sourceindex, 16] / steering_ratio
            AccelPedalRate[targetindex] = data[sourceindex, 17] * 0.01
            BrakePedalRate[targetindex] = data[sourceindex, 18] * 0.01

            YawRate[targetindex] = np.deg2rad(data[sourceindex, 19])
            Roll[targetindex] = data[sourceindex, 20]
            Pitch[targetindex] = data[sourceindex, 21]
# TODO
# Roll data의 부호 및 단위를 SIM Data와 통일해야함
# Pitch data의 부호 및 단위를 SIM Data와 통일해야함

            VehicleModel[targetindex] = 'MOHAVE'

            targetindex = targetindex + 1
            sourceindex = sourceindex + 1

        else:
            if data[sourceindex, 22] != Duplicated_Sign[targetindex-1]:
                IndexID[targetindex] = targetindex + 1
                currentTime = datetime.datetime(year=int(start_date[0:4]),
                                              month=int(start_date[4:6]),
                                              day=int(start_date[6:8]),
                                              hour=int(data[sourceindex, 11]),
                                              minute=int(data[sourceindex, 12]),
                                              second=int(data[sourceindex, 13]),
                                              microsecond=1000*int(data[sourceindex, 14])).timestamp()

                TimeStamp[targetindex] = currentTime - StartTime
                Duplicated_Sign[targetindex] = data[sourceindex, 22]

                utm_x, utm_y, _, _ = utm.from_latlon(data[sourceindex, 5], data[sourceindex, 6])

                LocalX[targetindex] = utm_x - LocalOrigin_X
                LocalY[targetindex] = utm_y - LocalOrigin_Y
                LocalZ[targetindex] = data[sourceindex, 7] - LocalOrigin_Z

                Yaw[targetindex] = 90 - data[sourceindex, 8]
                Velocity[targetindex] = data[sourceindex, 9]  # in meter per second
                EngineRPM[targetindex] = 0

                SteeringAngle[targetindex] = -0.1 * data[sourceindex, 16] / steering_ratio
                AccelPedalRate[targetindex] = data[sourceindex, 17] * 0.01
                BrakePedalRate[targetindex] = data[sourceindex, 18] * 0.01

                YawRate[targetindex] = np.deg2rad(data[sourceindex, 19])

                # TODO
                # Roll data의 부호 및 단위를 SIM Data와 통일해야함
                # Pitch data의 부호 및 단위를 SIM Data와 통일해야함

                Roll[targetindex] = data[sourceindex, 20]
                Pitch[targetindex] = data[sourceindex, 21]

                VehicleModel[targetindex] = 'MOHAVE'
                targetindex = targetindex + 1
                sourceindex = sourceindex + 1

            else:
                sourceindex = sourceindex + 1
                pass


        if sourceindex == MaxFrameNumber:
            end_date = target_scenario[target_scenario.find("TO") + 3:target_scenario.find("TO") + 11]
            end_time = target_scenario[target_scenario.find("TO") + 12:target_scenario.find("TO") + 18]
            IndexID = IndexID[:targetindex]
            TimeStamp = TimeStamp[:targetindex]
            Duplicated_Sign = Duplicated_Sign[:targetindex]
            LocalX = LocalX[:targetindex]
            LocalY = LocalY[:targetindex]
            LocalZ = LocalZ[:targetindex]
            Yaw = Yaw[:targetindex]
            Velocity = Velocity[:targetindex]
            EngineRPM = EngineRPM[:targetindex]
            SteeringAngle = SteeringAngle[:targetindex]
            AccelPedalRate = AccelPedalRate[:targetindex]
            BrakePedalRate = BrakePedalRate[:targetindex]
            YawRate = YawRate[:targetindex]
            Roll = Roll[:targetindex]
            Pitch = Pitch[:targetindex]
            VehicleModel = VehicleModel[:targetindex]

            bar.finish()
            break


    df = pd.DataFrame({'INDEX': IndexID,
                       'TimeStamp': TimeStamp,
                       'Duplicated_Sign': Duplicated_Sign,
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

    root_name = 'dataset/raw_data_real_mohave/XRP_DAQ_BIN_LAND/XRP_CSV/'
    file_name = 'XRP_ASC_FROM_'+start_date+'_'+start_time+'_TO_'+end_date+'_'+end_time+'_processed.csv'

    df.to_csv(root_name+file_name, index=False)
