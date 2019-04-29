import pyaudio
import threading
import time
import collections

# 音频录音器
class AudioRecorder(threading.Thread):
    def __init__(self, Client, p, CHUNK=256, FORMAT = pyaudio.paInt16, CHANNELS = 2, RATE = 2560):
        # 设置参数比如录制时间等
        # RATE: 一秒钟采样的点数
        # CHUNK: 一个Frame采样个数
        # 也就是 可以用这两个参数控制 一个片段的时间 预计 0.05秒传递一个片段 所以设置 CHUNK = RATE/20
        # paInt16 一个占据 4 bytes 所以 CHUNK * 4 = 512 没有超过 1024 限制, 所以先这么设置
        threading.Thread.__init__(self)
        self.Client = Client
        self.CHUNK = CHUNK
        self.FORMAT = FORMAT
        self.CHANNELS = CHANNELS
        self.RATE = RATE
        self.p = p

    def run(self):
        stream = self.p.open(format=self.FORMAT,
                        channels=self.CHANNELS,
                        rate=self.RATE,
                        input=True,
                        frames_per_buffer=self.CHUNK)
        # print("Recorder", self.Client.STATE)
        while self.Client.STATE != "CONNECTED":
            time.sleep(0.1)
        # print("Recorder", self.Client.STATE)
        index = 0
        print("AudioRecorder 开始")
        while self.Client.STATE == "CONNECTED":
            # print("Recorder", self.Client.STATE)
            index += 1
            if index == 10:
                time.sleep(0.05)
                index = 0
            data = stream.read(self.CHUNK, exception_on_overflow = False)
            # print(len(data))
            # block.append(data)
            # self.Client.queue.append(test[index*128:(index+1)*128])
            # index = (index+1)%10

            if len(self.Client.queue) < self.Client.maxLength:
                # print("加入队列消息, 当前队列长度: {0}".format(len(self.Client.queue)))
                if len(self.Client.queue) > 10:
                    time.sleep(0.02)
                self.Client.queue.append(data)
            else:
                pass
                # print("已经达到最大缓存长度, 开始丢包")
        # 关闭
        self.stream.close()
        self.p.close()