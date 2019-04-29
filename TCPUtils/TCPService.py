import socket
import collections
from chardet import detect
import threading
import time

# 纯粹的 TCP 的通信.
# Service进程只用来进行消息的接受, 并不负责消息的发送
class TCPService(threading.Thread):
    def __init__(self, HOST = "127.0.0.1", PORT = 44445, RECV_SIZE = 1024, maxNumber = 1, maxLength = 1000, type="TCP"):
        threading.Thread.__init__(self)
        self.HOST = HOST
        self.PORT = PORT
        self.ADDR = (HOST, PORT)
        # 最大同时连接数
        self.maxNumber = maxNumber
        self.queue = collections.deque()
        # 允许 buffer 最大的长度
        self.maxLength = maxLength
        # 每一个数据包的数据大小
        self.RECV_SIZE = RECV_SIZE

        self.SUCCESS = 0
        self.FAIL = 0
        self.TYPE = type

        self.STATE_CONFIG()


    def STATE_CONFIG(self):
        self.STATE = "WAITING"
        self.EVENTMAP = {
            "ending":self.finishing,
            "start":self.starting,
            # "success":self.success,
        }

    def starting(self):
        # 发送建立连接的信息
        if self.STATE == "CONNECTING":
            time.sleep(0.01)
            self.STATE = "CONNECTED"
            # print("Service 发送start信号")
            self.client.send(bytes("start", "utf-8"))

    def finishing(self):
        self.client.close()
        self.queue = collections.deque()
        self.SUCCESS = 0
        self.FAIL = 0
        self.STATE = "WAITING"

    # 主动关闭时候(点击挂断按钮的时候)
    def closing(self, client, addr):
        self.client.send("ending")
        self.client.close()
        self.queue = collections.deque()
        self.SUCCESS = 0
        self.FAIL = 0
        self.STATE = "WAITING"

    def run(self):
        self.listen()

    def listen(self):
        # AF_INET 表示 针对 IPV4
        # SOCK_STREAM 表示针对 面向流的TCP协议
        self.tcpServiceSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcpServiceSock.bind(self.ADDR)
        self.tcpServiceSock.listen(self.maxNumber)
        while True:
            # print("等待连接")
            client, addr = self.tcpServiceSock.accept()
            self.client = client
            # print("已经和 {0} 产生了连接, 可以开始通话了!!".format(addr))
            self.connectEvent(client, addr)
        self.tcpServiceSock.close()

    def connectEvent(self, client, addr):
        # 进行声音的录制 存入 queue 中 然后 queue 中的数据会被外部定时的取出然后播放
        self.STATE = "CONNECTING"
        # 首先接收start信号然后返回
        data = client.recv(self.RECV_SIZE)
        t = detect(data)["encoding"]
        if t == "ascii":
            data = data.decode(t)
        else:
            print("Service Client start信号接受失败")
            client.close()
            return
        if data == "start":
            time.sleep(0.01)
            self.EVENTMAP["start"]()
        else:
            self.EVENTMAP["ending"]()
            return

        if self.TYPE == "TCP" or self.TYPE == "tcp":
            print("开始TCP接收数据")
            self.communication(client, addr)
        elif self.TYPE == "UDP" or self.TYPE == "udp":
            self.control(client)


    def control(self, client):
        while True:
            data = client.recv(self.RECV_SIZE)


    def communication(self, client, addr):
        while True:
            if self.STATE == "WAITING":
                break
            data = client.recv(self.RECV_SIZE)
            #对空数据进行跳过处理
            if not data:
                time.sleep(0.02)
                continue
            t = detect(data)["encoding"]
            if t == "ascii":
                data = data.decode(t)
            #对特殊状态事件参数进行匹配
            if data in self.EVENTMAP:
                print("Service 接受到特殊状态: {0}".format(data))
                self.EVENTMAP[data]()
            else:
                # 没有接受到开始信号的时候不进行任何消息的接受
                # print("Service 接收到信息, 长度为: {0}".format(len(data)))
                if self.STATE != "CONNECTED":
                    # print("Service 等待 start信号")
                    time.sleep(0.02)
                    continue
                if len(self.queue) < self.maxLength:
                    # print("Service 成功接受数据")
                    self.SUCCESS += 1
                    self.queue.append(data)
                    # print(len(self.queue))
                else:
                    self.FAIL += 1
                    # print("已经达到最大缓存长度, 开始丢包, 当前丢包率: {0}".format(
                    #     self.FAIL/(self.FAIL + self.SUCCESS)))
                # 返回一个接收信息
                # print("Service 返回确认信息 ok")
                client.send(bytes("ok", "utf-8"))


