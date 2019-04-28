import pyaudio
import threading
import time

# 音频录音器
class AudioRecorder(threading.Thread):
    def __init__(self, Client, CHUNK=128, FORMAT = pyaudio.paInt16, CHANNELS = 2, RATE = 2560):
        # 设置参数比如录制时间等
        # RATE: 一秒钟采样的点数
        # CHUNK: 一个Frame采样个数
        # 也就是 可以用这两个参数控制 一个片段的时间 预计 0.05秒传递一个片段 所以设置 CHUNK = RATE/20
        # paInt16 一个占据 4 bytes 所以 CHUNK * 4 = 512 没有超过 1024 限制, 所以先这么设置
        threading.Thread.__init__(self)
        self.Client = Client
        self.CHUNK = CHUNK
        self.FORMAT = FORMAT
        self.CHANNEL = CHANNELS
        self.RATE = RATE

    def run(self):
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=self.FORMAT,
                        channels=self.CHANNELS,
                        rate=self.RATE,
                        input=True,
                        frames_per_buffer=self.CHUNK)
        while self.Client.STATE != "CONNECTED":
            time.sleep(0.1)
        data = None
        while self.Client.STATE == "CONNECTED":
            data = self.stream.read(self.CHUNK)
            if len(self.Client.queue) < self.Client.maxLength:
                self.Client.queue.append(data)
            else:
                print("已经达到最大缓存长度, 开始丢包")
        # 关闭
        self.stream.close()
        self.p.close()