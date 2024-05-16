import numpy as np
import csv
import pandas as pd

with open('dataset/sample.csv', newline='') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
    for row in spamreader:
        if 'TimeStamp' in row[0]:
            Fields = row[0].split(',')
            RawData = dict()



RawData = csv