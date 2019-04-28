import socket
import collections
from chardet import detect
import time
import threading

# Client只用来发送数据并不进行数据的接收
class TCPClient(threading.Thread):
    def __init__(self, S_HOST="10.164.255.229", S_PORT=4399, C_HOST="10.164.255.229", C_PORT=44444, RECV_SIZE = 1024, maxNumber = 1, maxLength = 1000, waitTime=0.02):
        threading.Thread.__init__(self)
        self.S_HOST = S_HOST
        self.S_PORT = S_PORT
        self.C_HOST = C_HOST
        self.C_PORT = C_PORT
        self.RECV_SIZE = RECV_SIZE
        self.queue = collections.deque()
        self.maxNumber = maxNumber
        self.maxLength = maxLength
        self.waitTime = waitTime
        self.STATE_CONFIG()

    def STATE_CONFIG(self):
        self.STATE = "WAITING"
        self.EVENTMAP = {
            "ending":self.finishing,
            "start":self.start,
        }

    def start(self):
        self.STATE = "CONNECTED"
        # 发送建立连接的信息
        self.client.send(bytes("start", "utf-8"))

    def finishing(self):
        self.client.close()
        self.buffer = collections.deque()
        self.SUCCESS = 0
        self.FAIL = 0

    # 主动关闭时候(点击挂断按钮的时候)
    def closing(self, client, addr):
        self.client.send("ending")
        self.client.close()
        self.buffer = collections.deque()
        self.SUCCESS = 0
        self.FAIL = 0

    def run(self):
        self.connect()

    def connect(self):
        S_ADDR = (self.S_HOST, self.S_PORT)
        C_ADDR = (self.C_HOST, self.C_PORT)
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.bind(C_ADDR)
        client.connect(S_ADDR)
        self.client = client
        self.STATE = "CONNECTING"

        # 首先发送start状态
        client.send(bytes("start", "utf-8"))
        # 等待start的返回
        data = client.recv(self.RECV_SIZE)
        t = detect(data)["encoding"]
        data = data.decode(t)
        if data == "start":
            self.EVENTMAP[data]()
        else:
            # 如果收到的不是 start 那么就发送 ending 结束吧...
            self.EVENTMAP["ending"]()
        self.communication(client)

    # 正式开始通信
    def communication(self, client):
        while True:
            # 没有数据的话等待 0.02 s
            if self.STATE == "WAITING":
                break
            if not self.queue:
                time.sleep(self.waitTime)
                continue
            # 有数据就发送数据
            data = self.queue.popleft()
            # 因为音频就是二进制数据, 发送就好了
            client.send(data)
            # 然后等待确认数据回来
            data = client.recv(self.RECV_SIZE)
            if not data:
                continue
            t = detect(data)["encoding"]
            data = data.decode(t)
            if data == "ending":
                self.EVENTMAP["ending"]()
