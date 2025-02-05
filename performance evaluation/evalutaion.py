import glob
import numpy as np
import matplotlib
import os
matplotlib.use('pdf')

import matplotlib.pyplot as plt


trial = os.listdir('performance evaluation')[:-1]

for num in range(len(trial)):
    target = trial[num]
    eval_set_original = glob.glob('performance evaluation/'+target+'/*original*.csv')
    eval_set_sim = glob.glob('performance evaluation/'+target+'/*sim*.csv')

    for i in range(len(eval_set_original)):
        target_status = np.loadtxt(eval_set_original[i], delimiter=',', skiprows=1, usecols=[1, 3, 4, 7, 10, 11])
        # TODO : raw_control_data_injection.py 에서 초기 status를 잘못넣어서 첫번째 행 삭제함
        target_status_txyv = target_status[1:, :4]
        target_status_txyv[:,1:3] = target_status_txyv[:,1:3] - target_status_txyv[0,1:3]
        target_status_accbrk = target_status[1:, 4:]
        acc_brk_dual_idx = []
        for j in range(len(target_status_accbrk)):
            if target_status_accbrk[j,0] > 0.1 and target_status_accbrk[j,1] > 0.1:
                acc_brk_dual_idx.append(j)


        predicted_status = np.loadtxt(eval_set_sim[i], delimiter=',', skiprows=1, usecols=[1, 3, 4, 7, 10, 11])
        # TODO : raw_control_data_injection.py 에서 초기 status를 잘못넣어서 첫번째 행 삭제함
        predicted_status_txyv = predicted_status[1:, :]
        predicted_status_txyv[:, 1:3] = predicted_status_txyv[:, 1:3] - predicted_status_txyv[1, 1:3]
        predicted_status_accbrk = predicted_status[1:, 4:]


        x = target_status_txyv[:,0]
        y1 = target_status_txyv[:,3]
        y2 = predicted_status_txyv[:,3]

        plt.scatter(x,y1,c='r', label='vehicle')
        plt.scatter(x,y2,c='b', label='simulator')
        plt.scatter(x[acc_brk_dual_idx],y1[acc_brk_dual_idx],c='k', s=10, label='unrealistic data (accel + brake)')
        plt.xlabel('time (sec)')
        plt.ylabel('velocity (m/s)')
        plt.grid(True)
        plt.legend()
        plt.savefig('performance evaluation/' + target + '/'+str(i))
        plt.clf()

        plt.scatter(target_status_txyv[:,1],target_status_txyv[:,2],c='r', s=3, label='Trajectory')
        plt.grid(True)
        plt.legend()
        plt.axis('equal')
        plt.savefig('performance evaluation/' + target + '/path'+str(i))
        plt.clf()
