import struct
import socket
import threading
import time

class EgoInfoReceiver():
    def __init__(self, ip, port):
        self.header = '#MoraiInfo$'
        # self.data_length = 132
        self.data_length = 152
        self.parsed_data = [0 for i in range(28)]

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((ip, port))
        threading.Thread(target=self.receive_data, daemon=True).start()

    def receive_data(self):
        while True:
            data_size = 65535
            raw_data, _ = self.sock.recvfrom(data_size)
            if self.header == raw_data[0:11].decode() and self.data_length == struct.unpack('i', raw_data[11:15])[0]:
                secs = struct.unpack('f', raw_data[27:31])[0]
                nsecs = struct.unpack('f', raw_data[31:35])[0]
                ctrl_mode = struct.unpack('b', raw_data[35:36])[0]
                gear = struct.unpack('b', raw_data[36:37])[0]
                signed_vel = struct.unpack('f', raw_data[37:41])[0]  # km/h
                map_id = struct.unpack('i', raw_data[41:45])[0]
                accel = struct.unpack('f', raw_data[45:49])[0]
                brake = struct.unpack('f', raw_data[49:53])[0]
                size_x, size_y, size_z = struct.unpack('fff', raw_data[53:65])
                overhang, wheelbase, rear_overhang = struct.unpack('fff', raw_data[65:77])
                pos_x, pos_y, pos_z = struct.unpack('fff', raw_data[77:89])
                roll, pitch, yaw = struct.unpack('fff', raw_data[89:101])
                vel_x, vel_y, vel_z = struct.unpack('fff', raw_data[101:113])
                ang_vel_x, ang_vel_y, ang_vel_z = struct.unpack('fff', raw_data[113:125])
                acc_x, acc_y, acc_z = struct.unpack('fff', raw_data[125:137])
                steer = struct.unpack('f', raw_data[137:141])[0]
                link_id = raw_data[141:179].decode()
                self.parsed_data = [
                    ctrl_mode, gear, signed_vel, map_id, accel, brake, size_x, size_y, size_z, overhang, wheelbase,
                    rear_overhang, pos_x, pos_y, pos_z, roll, pitch, yaw, vel_x, vel_y, vel_z, acc_x, acc_y, acc_z,
                    steer, ang_vel_x, ang_vel_y, ang_vel_z
                ]
            else:
                self.parsed_data = []
    def __del__(self):
        self.sock.close()

