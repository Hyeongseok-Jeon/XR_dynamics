import numpy as np
import csv
import pandas as pd
import random
from utils.utils import data_interpolation
import glob
import torch
import os


DataGroupList = os.listdir('dataset/')


TimeGap = 0.1
TimeHistory = 3
DataGroupIndex = 0
SamplingNumber = 100000

DataList = glob.glob('dataset/' + DataGroupList[DataGroupIndex] + '/*.csv')
InterpolatedDataList = []
NumberOfHistory = int(TimeHistory / TimeGap)

for datasample in range(len(DataList)):
    with open(DataList[datasample], newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
        init_row = 1
        for row in spamreader:
            if 'TimeStamp' in row[0]:
                Fields = row[0].split(',')
                RawData = dict()
                for i in range(len(Fields)):
                    RawData[Fields[i]] = []
            else:
                data = row[0].split(',')
                for i in range(len(data)):
                    if Fields[i] != 'VehicleModel':
                        if Fields[i] == 'TimeStamp' and init_row != 1:
                            RawData[Fields[i]].append(float(data[i]) + 0.1 * (0.5 - random.random()))
                        else:
                            init_row = 0
                            RawData[Fields[i]].append(float(data[i]))
                    else:
                        RawData[Fields[i]].append(data[i])
    InterpolatedData = data_interpolation(RawData, TimeGap)
    InterpolatedDataList.append(InterpolatedData)

InputList = []
OutputList = []
DataAllList = []
for i in range(SamplingNumber):
    print(i)
    DataListIndex = random.randint(0, len(DataList) - 1)
    InitFrameIndex = random.randint(0, len(InterpolatedDataList[DataListIndex]['TimeStamp']) - NumberOfHistory - 2)

    #     Input
    DLStrAng = np.expand_dims(np.asarray(InterpolatedDataList[DataListIndex]['SteeringAngle'][InitFrameIndex:InitFrameIndex + NumberOfHistory + 1]), axis=1)
    DLAccelPedalRatio = np.expand_dims(np.asarray(InterpolatedDataList[DataListIndex]['AccelPedalRate'][InitFrameIndex:InitFrameIndex + NumberOfHistory + 1]), axis=1)
    DLBrakePedalRatio = np.expand_dims(np.asarray(InterpolatedDataList[DataListIndex]['BrakePedalRate'][InitFrameIndex:InitFrameIndex + NumberOfHistory + 1]), axis=1)
    Input = np.expand_dims(np.concatenate((DLStrAng, DLAccelPedalRatio, DLBrakePedalRatio), axis=1), axis=0)
    InputList.append(Input)

    #     Output
    DLDeltaVelocity = np.expand_dims(np.asarray(InterpolatedDataList[DataListIndex]['Velocity'][InitFrameIndex + 1:InitFrameIndex + NumberOfHistory + 2]) - np.asarray(InterpolatedDataList[DataListIndex]['Velocity'][InitFrameIndex:InitFrameIndex + NumberOfHistory + 1]), axis=1)
    DLDeltaYawRate = np.expand_dims(np.asarray(InterpolatedDataList[DataListIndex]['YawRate'][InitFrameIndex + 1:InitFrameIndex + NumberOfHistory + 2]) - np.asarray(InterpolatedDataList[DataListIndex]['YawRate'][InitFrameIndex:InitFrameIndex + NumberOfHistory + 1]), axis=1)
    DLDeltaRollRate = np.expand_dims(np.asarray(InterpolatedDataList[DataListIndex]['RollRate'][InitFrameIndex + 1:InitFrameIndex + NumberOfHistory + 2]) - np.asarray(InterpolatedDataList[DataListIndex]['RollRate'][InitFrameIndex:InitFrameIndex + NumberOfHistory + 1]), axis=1)
    DLDeltaPitchRate = np.expand_dims(np.asarray(InterpolatedDataList[DataListIndex]['PitchRate'][InitFrameIndex + 1:InitFrameIndex + NumberOfHistory + 2]) - np.asarray(InterpolatedDataList[DataListIndex]['PitchRate'][InitFrameIndex:InitFrameIndex + NumberOfHistory + 1]), axis=1)
    Output = np.expand_dims(np.concatenate((DLDeltaVelocity, DLDeltaYawRate, DLDeltaRollRate, DLDeltaPitchRate), axis=1), axis=0)
    OutputList.append(Output)

    #     DataAll
    DLTimeStamp = np.expand_dims(np.asarray(InterpolatedDataList[DataListIndex]['TimeStamp'][InitFrameIndex:InitFrameIndex + NumberOfHistory + 2]), axis=1)
    DLStrAng = np.expand_dims(np.asarray(InterpolatedDataList[DataListIndex]['SteeringAngle'][InitFrameIndex:InitFrameIndex + NumberOfHistory + 2]), axis=1)
    DLAccelPedalRatio = np.expand_dims(np.asarray(InterpolatedDataList[DataListIndex]['AccelPedalRate'][InitFrameIndex:InitFrameIndex + NumberOfHistory + 2]), axis=1)
    DLBrakePedalRatio = np.expand_dims(np.asarray(InterpolatedDataList[DataListIndex]['BrakePedalRate'][InitFrameIndex:InitFrameIndex + NumberOfHistory + 2]), axis=1)
    DLVelocity = np.expand_dims(np.asarray(InterpolatedDataList[DataListIndex]['Velocity'][InitFrameIndex:InitFrameIndex + NumberOfHistory + 2]), axis=1)
    DLYawRate = np.expand_dims(np.asarray(InterpolatedDataList[DataListIndex]['YawRate'][InitFrameIndex:InitFrameIndex + NumberOfHistory + 2]), axis=1)
    DLRollRate = np.expand_dims(np.asarray(InterpolatedDataList[DataListIndex]['RollRate'][InitFrameIndex:InitFrameIndex + NumberOfHistory + 2]), axis=1)
    DLPitchRate = np.expand_dims(np.asarray(InterpolatedDataList[DataListIndex]['PitchRate'][InitFrameIndex:InitFrameIndex + NumberOfHistory + 2]), axis=1)
    DLLatitude = np.expand_dims(np.asarray(InterpolatedDataList[DataListIndex]['Latitude'][InitFrameIndex:InitFrameIndex + NumberOfHistory + 2]), axis=1)
    DLLongitude = np.expand_dims(np.asarray(InterpolatedDataList[DataListIndex]['Longitude'][InitFrameIndex:InitFrameIndex + NumberOfHistory + 2]), axis=1)
    DLHeight = np.expand_dims(np.asarray(InterpolatedDataList[DataListIndex]['Height'][InitFrameIndex:InitFrameIndex + NumberOfHistory + 2]), axis=1)
    DLRoll = np.expand_dims(np.asarray(InterpolatedDataList[DataListIndex]['Roll'][InitFrameIndex:InitFrameIndex + NumberOfHistory + 2]), axis=1)
    DLPitch = np.expand_dims(np.asarray(InterpolatedDataList[DataListIndex]['Pitch'][InitFrameIndex:InitFrameIndex + NumberOfHistory + 2]), axis=1)
    DLYaw = np.expand_dims(np.asarray(InterpolatedDataList[DataListIndex]['Yaw'][InitFrameIndex:InitFrameIndex + NumberOfHistory + 2]), axis=1)
    Etc = np.expand_dims(np.concatenate((DLTimeStamp,
                                         DLStrAng,
                                         DLAccelPedalRatio,
                                         DLBrakePedalRatio,
                                         DLVelocity,
                                         DLYawRate,
                                         DLRollRate,
                                         DLPitchRate,
                                         DLLatitude,
                                         DLLongitude,
                                         DLHeight,
                                         DLRoll,
                                         DLPitch,
                                         DLYaw), axis=1), axis=0)
    DataAllList.append(Etc)

BatchedInput = torch.from_numpy(np.concatenate(InputList, axis=0))
BatchedOutput = torch.from_numpy(np.concatenate(OutputList, axis=0))
BatchedDataAll = torch.from_numpy(np.concatenate(DataAllList, axis=0))

if os.path.isdir('dataset/' + DataGroupList[DataGroupIndex] + '_TorchTensor'):
    torch.save(BatchedInput, 'dataset/' + DataGroupList[DataGroupIndex] + '_TorchTensor' + '/BatchedInput.pt')
    torch.save(BatchedOutput, 'dataset/' + DataGroupList[DataGroupIndex] + '_TorchTensor' + '/BatchedOutput.pt')
    torch.save(BatchedDataAll, 'dataset/' + DataGroupList[DataGroupIndex] + '_TorchTensor' + '/BatchedDataAll.pt')
else:
    os.mkdir('dataset/' + DataGroupList[DataGroupIndex] + '_TorchTensor')
    torch.save(BatchedInput, 'dataset/' + DataGroupList[DataGroupIndex] + '_TorchTensor' + '/BatchedInput.pt')
    torch.save(BatchedOutput, 'dataset/' + DataGroupList[DataGroupIndex] + '_TorchTensor' + '/BatchedOutput.pt')
    torch.save(BatchedDataAll, 'dataset/' + DataGroupList[DataGroupIndex] + '_TorchTensor' + '/BatchedDataAll.pt')