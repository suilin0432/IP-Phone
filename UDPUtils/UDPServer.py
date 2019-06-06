import socket
import collections
from chardet import detect
import threading
import time

# 用UDP进行信息的接收
class UDPService(threading.Thread):
    def __init__(self, HOST = "127.0.0.1", PORT = 44447, RECV_SIZE = 1024, maxNumber = 1, maxLength = 1000):
        threading.Thread.__init__(self)
        self.HOST = HOST
        self.PORT = PORT
        self.RECV_SIZE = RECV_SIZE
        self.maxNumber = maxNumber
        self.maxLength = maxLength
        self.STATE = "WAITING"
        self.queue = collections.deque()

    # 线程运行函数
    def run(self):
        self.STATE = "CONNECTED"
        self.begin()

    # 关闭
    def ending(self):
        self.s.close()
        self.STATE = "WAITING"

    # 开始等待接受数据
    def begin(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind((self.HOST, self.PORT))
        self.s = s
        print("开始等待接收数据")
        index = 0
        while True:
            index += 1
            data, addr = s.recvfrom(1024)
            if len(self.queue) < self.maxLength:
                self.queue.append(data)
                if index == 100:
                    print("当前队列长度: {0}".format(len(self.queue)))
                    index = 0