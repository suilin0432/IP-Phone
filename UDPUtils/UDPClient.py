import socket
import collections
from chardet import detect
import threading
import time

# 用UDP进行信息的发送
class UDPClient(threading.Thread):
    def __init__(self, S_HOST = "127.0.0.1", S_PORT = 44444, C_HOST = "127.0.0.1", C_PORT = 44445, RECV_SIZE = 1024, maxNumber = 1, maxLength = 1000):
        threading.Thread.__init__(self)
        self.S_HOST = S_HOST
        self.S_PORT = S_PORT
        self.C_HOST = C_HOST
        self.C_PORT = C_PORT
        self.S_ADDR = (S_HOST, S_PORT)
        self.RECV_SIZE = RECV_SIZE
        self.maxNumber = maxNumber
        self.maxLength = maxLength
        self.STATE = "WAITING"
        self.queue = collections.deque()

    def run(self):
        self.STATE = "CONNECTED"
        self.begin()

    def ending(self):
        self.s.close()
        self.STATE = "WAITING"

    def begin(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind((self.C_HOST, self.C_PORT))
        self.s = s
        print("开始发送数据")
        while True:
            if len(self.queue) > 0:
                s.sendto(self.queue.popleft(), self.S_ADDR)
