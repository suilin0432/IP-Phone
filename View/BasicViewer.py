from tkinter import *
from TCPUtils import TCPService, TCPClient
from UDPUtils import UDPService, UDPClient
from AudioUtils import AudioRecorder, AudioListener
import pyaudio
import time
import threading

class Application(Frame):
    def createWidgets(self):
        # 标题
        self.titleFm = Frame(self)
        self.titleLable = Label(self.titleFm, text = "IP Phone")
        self.titleLable.pack()
        self.titleFm.pack(side=TOP)

        # 本地ip，端口 拨打目标电话的部分
        self.functionFm = Frame(self)
        self.functionFmUp = Frame(self.functionFm)
        self.functionFmLeft = Frame(self.functionFmUp)
        self.functionFmRight = Frame(self.functionFmUp)
        self.functionFmBottom = Frame(self.functionFm)

        self.localLabel = Label(self.functionFmLeft, text = "local IP:port ")
        self.localLabel.pack(side=TOP)
        self.targetLabel = Label(self.functionFmLeft, text = "target IP:port ")
        self.targetLabel.pack(side=TOP)
        self.functionFmLeft.pack(side=LEFT)

        self.localText = Entry(self.functionFmRight)
        self.localText.insert(0, "{0}:{1}".format(self.server.HOST, self.server.PORT))
        self.localText.pack(side=TOP)
        self.targetText = Entry(self.functionFmRight)
        self.targetText.pack(side=TOP)
        self.functionFmRight.pack(side=LEFT)

        self.functionFmUp.pack(side=TOP)

        self.connectButton = Button(self.functionFmBottom, text="CONNECT")
        self.connectButton["fg"] = "red"
        self.connectButton["command"] = self.connect
        self.connectButton.pack(side=LEFT)
        # self.cutButton = Button(self.functionFmBottom, text="Hang Up")
        # self.cutButton["fg"]="red"
        # self.cutButton["command"] = self.hangUp
        # self.cutButton.pack(side = LEFT)
        self.QUIT = Button(self.functionFmBottom)
        self.QUIT["text"] = "QUIT"
        self.QUIT["fg"] = "red"
        self.QUIT["command"] = self.quit
        self.QUIT.pack({"side": "left"})
        self.functionFmBottom.pack(side=BOTTOM)

        self.functionFm.pack(side=TOP)

        # 状态信息标题
        self.subTitleFm = Frame(self)
        self.subTitle = Label(self.subTitleFm, text="\nState Message\n")
        self.subTitle.pack()
        self.subTitleFm.pack(side=TOP)

        # 状态信息描述
        self.stateMessageFm = Frame(self)
        self.stateMessageFmLeft = Frame(self.stateMessageFm)
        self.stateMessageFmRight = Frame(self.stateMessageFm)

        # 本地IP信息
        self.localIpLabel = Label(self.stateMessageFmLeft, text="local IP message: ")
        self.localIpLabel.pack(side=TOP)
        # 目标IP信息
        self.targetIpLabel = Label(self.stateMessageFmLeft, text="target IP message: ")
        self.targetIpLabel.pack(side=TOP)
        # 服务器状态
        self.serverState = Label(self.stateMessageFmLeft, text="server state: ")
        self.serverState.pack(side=TOP)
        # 客户端状态
        self.clientState = Label(self.stateMessageFmLeft, text="client state: ")
        self.clientState.pack(side=TOP)


        self.localIpVT = StringVar()
        self.localIpVT.set("{0}:{1}".format(self.server.HOST, self.server.PORT))
        self.localIPMessage = Label(self.stateMessageFmRight, textvariable=self.localIpVT)
        self.localIPMessage.pack(side=TOP)
        self.targetIpVT = StringVar()
        self.targetIpVT.set("not connected")
        self.targetIPMessage = Label(self.stateMessageFmRight, textvariable=self.targetIpVT)
        self.targetIPMessage.pack(side=TOP)
        self.serverStateVT = StringVar()
        self.serverStateVT.set(self.server.STATE)
        self.serverStateMessage = Label(self.stateMessageFmRight, textvariable=self.serverStateVT)
        self.serverStateMessage.pack(side=TOP)
        self.clientStateVT = StringVar()
        self.clientStateVT.set("not connected")
        self.clientStateMessage = Label(self.stateMessageFmRight, textvariable=self.clientStateVT)
        self.clientStateMessage.pack(side=TOP)


        self.stateMessageFmLeft.pack(side=LEFT)
        self.stateMessageFmRight.pack(side=RIGHT)
        self.stateMessageFm.pack(side=TOP)


    # def hangUp(self):
    #     # try:
    #     print("HANG UP")
    #     self.client.closing()
    #     # except:
    #     #     pass

    def __init__(self, master=None):
        Frame.__init__(self, master)

        threading._start_new_thread(self.serverInit, ())

        # 监听线程, 每隔一段时间进行一次状态的更新

        self.pack()
        self.createWidgets()
        self.timer = threading.Timer(0.1, self.stateUpdate)
        self.timer.start()

    def stateUpdate(self):
        print("state update")
        try:
            self.serverStateVT.set(self.server.STATE)
        except:
            pass
        try:
            self.clientStateVT.set(self.client.STATE)
            self.targetIpVT.set("{0}:{1}".format(self.client.C_HOST, self.client.C_PORT))
        except:
            self.clientStateVT.set("not connected")
            self.targetIpVT.set("not connected")
        self.timer = threading.Timer(0.2, self.stateUpdate)
        self.timer.start()

    def connect(self):
        try :
            self.client
            return
        except:
            pass
        targetIP, port = self.targetText.get().split(":")
        print(targetIP, port)
        threading._start_new_thread(self.clientInit, (targetIP, port))

        print("connect")
        pass

    def clientInit(self, targetIP, port):
        self.client = TCPClient(S_HOST = targetIP, S_PORT = int(port), C_HOST = "127.0.0.1", C_PORT = 44446, type="UDP")
        self.sendC = UDPClient()
        self.recorder = AudioRecorder(self.sendC, self.p)
        self.recorder.start()
        self.client.start()
        self.targetIpVT.set("{0}:{1}".format(self.client.C_HOST, self.client.C_PORT))
        time.sleep(0.1)
        self.sendC.start()

        self.recorder.join()
        self.client.join()
        self.sendC.join()

    def quit(self):
        try:
            self.server.closing()
        except:
            pass
        try:
            self.client.closing()
        except:
            pass
        try:
            self.client.finishing()
        except:
            pass
        try:
            self.server.finishing()
        except:
            pass
        super().quit()
        self.timer.cancel()

    def serverInit(self):
        # 需要初始化服务器, 客户端是在连接的时候进行初始化的
        self.server = TCPService(HOST="127.0.0.1", PORT=44445, type="UDP")
        self.sendS = UDPService()
        self.p = pyaudio.PyAudio()
        self.listener = AudioListener(self.sendS, self.p)
        self.listener.start()
        self.server.start()
        time.sleep(0.1)
        self.sendS.start()

        self.listener.join()
        self.server.join()
        self.sendS.join()

root = Tk()
app = Application(master=root)
app.mainloop()
root.destroy()