import socket
import collections
from chardet import detect
import time
import threading

# Client只用来发送数据并不进行数据的接收
class TCPClient(threading.Thread):
    def __init__(self, S_HOST="127.0.0.1", S_PORT=44445, C_HOST="127.0.0.1", C_PORT=44446, RECV_SIZE = 1024, maxNumber = 1, maxLength = 1000, waitTime=0.02, type="TCP"):
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
        self.TYPE = type

    def STATE_CONFIG(self):
        self.STATE = "WAITING"
        self.EVENTMAP = {
            "ending":self.finishing,
            "start":self.starting,
            # "success":self.success,
        }

    def starting(self):
        # 发送建立连接的信息
        self.client.send(bytes("start", "utf-8"))

    def finishing(self):
        self.client.close()
        self.buffer = collections.deque()
        self.SUCCESS = 0
        self.FAIL = 0
        self.STATE = "WAITING"
        # UDP 数据传递的时候返回TCP连接不成功使得无法进行信息的建立

    # 主动关闭时候(点击挂断按钮的时候)
    def closing(self, client, addr):
        self.client.send("ending")
        self.client.close()
        self.buffer = collections.deque()
        self.SUCCESS = 0
        self.FAIL = 0
        self.STATE = "WAITING"

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

        # 首先发送start状态 / success状态
        print("Client 发送 start")
        time.sleep(1)
        client.send(bytes("start", "utf-8"))
        # 等待start的返回
        data = client.recv(self.RECV_SIZE)
        t = detect(data)["encoding"]
        if t == "ascii":
            data = data.decode(t)
        else:
            #认为连接失败
            print("Client 接收 start 连接信号失败")
            client.close()
            return
        if data == "start":
            print("Client 接受到 start")
            time.sleep(0.01)
            self.STATE = "CONNECTED"
        else:
            # 如果收到的不是 start 那么就发送 ending 结束吧...
            print("Client 接收 start 连接信号失败")
            self.EVENTMAP["ending"]()

        # 如果
        if self.TYPE == "TCP" or self.TYPE == "tcp":
            print("开始TCP发送数据")
            self.communication(client)
        elif self.TYPE == "UDP" or self.TYPE == "udp":
            # 如果是UDP的话就开始发送数据了, client 占用但是并不进行任何传输, 用来进行信号控制??, 所以还是要进行连接的, 但是并不会主动释放, 定时发送一个连接保持包
            self.control(client)


    def control(self, client):
        while True:
            data = input()
            if not data:
                continue
            client.send(bytes(data, "utf-8"))


    # 正式开始通信
    def communication(self, client):
        while True:
            # 没有数据的话等待 0.02 s
            if self.STATE == "WAITING":
                break
            if not self.queue:
                time.sleep(self.waitTime)
                # print("TCPClient waiting")
                continue
            # 有数据就发送数据
            data = self.queue.popleft()
            # 因为音频就是二进制数据, 发送就好了
            client.send(data)
            # print("Client 发送数据, 数据长度: {0}".format(len(data)))
            # 然后等待确认数据回来
            data = client.recv(self.RECV_SIZE)
            if not data:
                time.sleep(self.waitTime)
                continue
            t = detect(data)["encoding"]
            data = data.decode(t)
            # print("Client 接收到确认数据 {0}".format(data))
            if data == "ending":
                self.EVENTMAP["ending"]()
