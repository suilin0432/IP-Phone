import socket
import collections
from chardet import detect

# Service进程只用来进行消息的接受, 并不负责消息的发送
class TCPService(object):
    def __init__(self, HOST = "10.164.255.229", PORT = 4399, RECV_SIZE = 1024, maxNumber = 1, maxLength = 1000):
        self.HOST = HOST
        self.PORT = PORT
        self.ADDR = (HOST, PORT)
        # 最大同时连接数
        self.maxNumber = maxNumber
        self.buffer = collections.deque()
        # 允许 buffer 最大的长度
        self.maxLength = maxLength
        # 每一个数据包的数据大小
        self.RECV_SIZE = RECV_SIZE

        self.SUCCESS = 0
        self.FAIL = 0

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
        self.STATE = "WAITING"

    # 主动关闭时候(点击挂断按钮的时候)
    def closing(self, client, addr):
        self.client.send("ending")
        self.client.close()
        self.buffer = collections.deque()
        self.SUCCESS = 0
        self.FAIL = 0
        self.STATE = "WAITING"

    def listen(self):
        # AF_INET 表示 针对 IPV4
        # SOCK_STREAM 表示针对 面向流的TCP协议
        self.tcpServiceSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcpServiceSock.bind(self.ADDR)
        self.tcpServiceSock.listen(self.maxNumber)
        while True:
            print("等待连接")
            client, addr = self.tcpServiceSock.accept()
            self.client = client
            print("已经和 {0} 产生了连接, 可以开始通话了!!".format(addr))
            self.connectEvent(client, addr)
        self.tcpServiceSock.close()
    def connectEvent(self, client, addr):
        # 进行声音的录制 存入 buffer 中 然后 buffer 中的数据会被外部定时的取出然后播放
        self.STATE = "CONNECTING"
        while True:
            if self.STATE == "WAITING":
                break
            data = client.recv(self.RECV_SIZE)
            #对空数据进行跳过处理
            if not data:
                continue
            t = detect(data)["encoding"]
            data = data.decode(t)
            #对特殊状态事件参数进行匹配
            if data in self.EVENTMAP:
                self.EVENTMAP[data]()
            else:
                # 没有接受到开始信号的时候不进行任何消息的接受
                if self.STATE != "CONNECTED":
                    continue
                if len(self.buffer) < self.maxLength:
                    self.SUCCESS += 1
                    self.buffer.append(data)
                    print(self.buffer, len(self.buffer))
                else:
                    self.FAIL += 1
                    print("已经达到最大缓存长度, 开始丢包, 当前丢包率: {0}".format(
                        self.FAIL/(self.FAIL + self.SUCCESS)))
            # 返回一个接收信息
            client.send(bytes("ok", "utf-8"))



