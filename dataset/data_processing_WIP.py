import json
import numpy as np
import csv
import pandas as pd
import random
from utils.utils import data_interpolation, DataExtractor
import glob
import torch
import os


with open('dataset/config.json') as f:
    config = json.load(f)

TimeGap = config['Time_Gap']
TimeHistory = config['Hitorical_Time_Horizon']
SamplingNumber = config['Sampling_Number']

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

    Input, Output, DataAll = DataExtractor(InterpolatedDataList, DataListIndex, InitFrameIndex, NumberOfHistory)
    InputList.append(Input)
    OutputList.append(Output)
    DataAllList.append(DataAll)

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