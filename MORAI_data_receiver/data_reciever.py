import numpy as np

from MORAI_data_receiver.receiver import EgoInfoReceiver
import os
import threading
import time
from math import sqrt


class UdpManager:
    def __init__(self, autonomous_driving):
        self.autonomous_driving = autonomous_driving

        self.config = Config()
        self.config.update_config(os.path.join(os.path.dirname(__file__), 'config.json'))
        self.traffic_light_control = self.config['map']['traffic_light_control']
        self.sampling_time = 1/float(self.config['common']['sampling_rate'])

        self.vehicle_state = None
        self.object_info_list = []
        self.traffic_light = []

        self.prev_x = 0
        self.prev_y = 0

        self.path_list_x = []
        self.path_list_y = []


        self.vehicle_max_steering_data = 36.25

    def execute(self):
        print('start simulation')
        self._set_protocol()
        self._main_loop()

    def _set_protocol(self):
        network = self.config['network']

        # receiver
        self.ego_info_receiver = EgoInfoReceiver(
            network['host_ip'], network['ego_info_dst_port'], self._ego_info_callback
        )

    def _main_loop(self):

        while True:
            start_time = time.perf_counter()
            compen_time = 0
            if self.vehicle_state:


                control_input, _ = self.autonomous_driving.execute(
                    self.vehicle_state, self.object_info_list, self.traffic_light
                )

                steering_input = -np.rad2deg(control_input.steering)/self.vehicle_max_steering_data

                self.ctrl_cmd_sender.send_data([control_input.accel, control_input.brake, steering_input])

                end_time = time.perf_counter()
                self._print_info(control_input)
                compen_time = float((end_time - start_time))
            if((1/30 - compen_time) > 0):
                time.sleep(1/30 - compen_time)

    def _ego_info_callback(self, data):
        if data:
            self.vehicle_state = VehicleState(data[12], data[13], np.deg2rad(data[17]), data[18]/3.6)
            self.vehicle_currenty_steer = data[-1]
        else:
            self.vehicle_state = None
