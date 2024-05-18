import numpy as np

def data_interpolation(RawData, TimeGap):
    InterpolatedData = dict()
    for i in range(len(RawData)):
        InterpolatedData[list(RawData.keys())[i]] = [RawData[list(RawData.keys())[i]][0]]
    InterpolateDataIndex = 0


    while True:
        InterpolateDataIndex = InterpolateDataIndex + 1
        CurTime = TimeGap * InterpolateDataIndex

        RawIndexGuideForFitting = np.where(np.array(RawData['TimeStamp']) - CurTime<0)[0][-1]
        if RawIndexGuideForFitting == 0:
            for i in range(len(RawData)):
                if list(RawData.keys())[i] == 'TimeStamp':
                    InterpolatedData[list(RawData.keys())[i]].append(round(CurTime,2))
                elif list(RawData.keys())[i] == 'VehicleModel':
                    InterpolatedData[list(RawData.keys())[i]].append(InterpolatedData[list(RawData.keys())[i]][-1])
                else:
                    data = (RawData[list(RawData.keys())[i]][RawIndexGuideForFitting+1] - RawData[list(RawData.keys())[i]][RawIndexGuideForFitting]) * CurTime / (RawData['TimeStamp'][RawIndexGuideForFitting+1] - RawData['TimeStamp'][RawIndexGuideForFitting])
                    InterpolatedData[list(RawData.keys())[i]].append(data)
        elif RawIndexGuideForFitting > len(RawData['TimeStamp'])-3:
            break
        else:
            RawIndexesForFitting = [RawIndexGuideForFitting-1, RawIndexGuideForFitting, RawIndexGuideForFitting+1, RawIndexGuideForFitting+2]
            for i in range(len(RawData)):
                if list(RawData.keys())[i] == 'TimeStamp':
                    InterpolatedData[list(RawData.keys())[i]].append(round(CurTime,2))
                elif list(RawData.keys())[i] == 'VehicleModel':
                    InterpolatedData[list(RawData.keys())[i]].append(InterpolatedData[list(RawData.keys())[i]][-1])
                else:
                    TimeStamp = np.array(RawData['TimeStamp'])[RawIndexesForFitting]
                    Value = np.array(RawData[list(RawData.keys())[i]])[RawIndexesForFitting]
                    FittingCoef = np.polyfit(TimeStamp, Value, 3)

                    p = np.poly1d(FittingCoef)
                    InterpolatedValue = p(CurTime)
                    InterpolatedData[list(RawData.keys())[i]].append(InterpolatedValue)

    return InterpolatedData