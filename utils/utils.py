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

def DataExtractor(Data, DataListIndex, InitFrameIndex, NumberOfHistory):

    #     Input
    DLStrAng = np.expand_dims(np.asarray(Data[DataListIndex]['SteeringAngle'][InitFrameIndex:InitFrameIndex + NumberOfHistory + 1]), axis=1)
    DLAccelPedalRatio = np.expand_dims(np.asarray(Data[DataListIndex]['AccelPedalRate'][InitFrameIndex:InitFrameIndex + NumberOfHistory + 1]), axis=1)
    DLBrakePedalRatio = np.expand_dims(np.asarray(Data[DataListIndex]['BrakePedalRate'][InitFrameIndex:InitFrameIndex + NumberOfHistory + 1]), axis=1)
    Input = np.expand_dims(np.concatenate((DLStrAng, DLAccelPedalRatio, DLBrakePedalRatio), axis=1), axis=0)

    #     Output
    DLDeltaVelocity = np.expand_dims(np.asarray(Data[DataListIndex]['Velocity'][InitFrameIndex + 1:InitFrameIndex + NumberOfHistory + 2]) - np.asarray(Data[DataListIndex]['Velocity'][InitFrameIndex:InitFrameIndex + NumberOfHistory + 1]), axis=1)
    DLDeltaYawRate = np.expand_dims(np.asarray(Data[DataListIndex]['YawRate'][InitFrameIndex + 1:InitFrameIndex + NumberOfHistory + 2]) - np.asarray(Data[DataListIndex]['YawRate'][InitFrameIndex:InitFrameIndex + NumberOfHistory + 1]), axis=1)
    DLDeltaRollRate = np.expand_dims(np.asarray(Data[DataListIndex]['RollRate'][InitFrameIndex + 1:InitFrameIndex + NumberOfHistory + 2]) - np.asarray(Data[DataListIndex]['RollRate'][InitFrameIndex:InitFrameIndex + NumberOfHistory + 1]), axis=1)
    DLDeltaPitchRate = np.expand_dims(np.asarray(Data[DataListIndex]['PitchRate'][InitFrameIndex + 1:InitFrameIndex + NumberOfHistory + 2]) - np.asarray(Data[DataListIndex]['PitchRate'][InitFrameIndex:InitFrameIndex + NumberOfHistory + 1]), axis=1)
    Output = np.expand_dims(np.concatenate((DLDeltaVelocity, DLDeltaYawRate, DLDeltaRollRate, DLDeltaPitchRate), axis=1), axis=0)

    #     DataAll
    DLTimeStamp = np.expand_dims(np.asarray(Data[DataListIndex]['TimeStamp'][InitFrameIndex:InitFrameIndex + NumberOfHistory + 2]), axis=1)
    DLStrAng = np.expand_dims(np.asarray(Data[DataListIndex]['SteeringAngle'][InitFrameIndex:InitFrameIndex + NumberOfHistory + 2]), axis=1)
    DLAccelPedalRatio = np.expand_dims(np.asarray(Data[DataListIndex]['AccelPedalRate'][InitFrameIndex:InitFrameIndex + NumberOfHistory + 2]), axis=1)
    DLBrakePedalRatio = np.expand_dims(np.asarray(Data[DataListIndex]['BrakePedalRate'][InitFrameIndex:InitFrameIndex + NumberOfHistory + 2]), axis=1)
    DLVelocity = np.expand_dims(np.asarray(Data[DataListIndex]['Velocity'][InitFrameIndex:InitFrameIndex + NumberOfHistory + 2]), axis=1)
    DLYawRate = np.expand_dims(np.asarray(Data[DataListIndex]['YawRate'][InitFrameIndex:InitFrameIndex + NumberOfHistory + 2]), axis=1)
    DLRollRate = np.expand_dims(np.asarray(Data[DataListIndex]['RollRate'][InitFrameIndex:InitFrameIndex + NumberOfHistory + 2]), axis=1)
    DLPitchRate = np.expand_dims(np.asarray(Data[DataListIndex]['PitchRate'][InitFrameIndex:InitFrameIndex + NumberOfHistory + 2]), axis=1)
    DLLocalX = np.expand_dims(np.asarray(Data[DataListIndex]['LocalX'][InitFrameIndex:InitFrameIndex + NumberOfHistory + 2]), axis=1)
    DLLocalY = np.expand_dims(np.asarray(Data[DataListIndex]['LocalY'][InitFrameIndex:InitFrameIndex + NumberOfHistory + 2]), axis=1)
    DLLocalZ = np.expand_dims(np.asarray(Data[DataListIndex]['LocalZ'][InitFrameIndex:InitFrameIndex + NumberOfHistory + 2]), axis=1)
    DLRoll = np.expand_dims(np.asarray(Data[DataListIndex]['Roll'][InitFrameIndex:InitFrameIndex + NumberOfHistory + 2]), axis=1)
    DLPitch = np.expand_dims(np.asarray(Data[DataListIndex]['Pitch'][InitFrameIndex:InitFrameIndex + NumberOfHistory + 2]), axis=1)
    DLYaw = np.expand_dims(np.asarray(Data[DataListIndex]['Yaw'][InitFrameIndex:InitFrameIndex + NumberOfHistory + 2]), axis=1)
    DataAll = np.expand_dims(np.concatenate((DLTimeStamp,
                                         DLStrAng,
                                         DLAccelPedalRatio,
                                         DLBrakePedalRatio,
                                         DLVelocity,
                                         DLYawRate,
                                         DLRollRate,
                                         DLPitchRate,
                                         DLLocalX,
                                         DLLocalY,
                                         DLLocalZ,
                                         DLRoll,
                                         DLPitch,
                                         DLYaw), axis=1), axis=0)

    return Input, Output, DataAll
