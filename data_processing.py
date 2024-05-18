import numpy as np
import csv
import pandas as pd
import random
from utils.utils import data_interpolation

with open('dataset/sample.csv', newline='') as csvfile:
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
                        RawData[Fields[i]].append(float(data[i])+0.1*(0.5-random.random()))
                    else:
                        init_row = 0
                        RawData[Fields[i]].append(float(data[i]))
                else:
                    RawData[Fields[i]].append(data[i])



TimeGap = 0.1
TimeHistory = 3
SamplingNumberPerHour = 1000

InterpolatedData = data_interpolation(RawData, TimeGap)

NumberOfHistory = int(TimeHistory / TimeGap)


