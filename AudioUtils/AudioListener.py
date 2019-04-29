import pyaudio
import threading
import time

# 音频播放器
class AudioListener(threading.Thread):
    def __init__(self, Service, p, CHUNK=256, FORMAT = pyaudio.paInt16, CHANNELS = 2, RATE = 2560):
        threading.Thread.__init__(self)
        self.Service = Service
        self.CHUNK = CHUNK
        self.FORMAT = FORMAT
        self.CHANNELS = CHANNELS
        self.RATE = RATE
        self.p = p

    def run(self):
        self.stream = self.p.open(format=self.FORMAT,
                        channels=self.CHANNELS,
                        rate=self.RATE,
                        output=True,
                        frames_per_buffer=self.CHUNK)
        # print("Listener", self.Service.STATE)
        while self.Service.STATE != "CONNECTED":
            time.sleep(0.1)
        data = None
        # print("Listener", self.Service.STATE)
        print("AudioListener 开始")
        while self.Service.STATE == "CONNECTED":
            if len(self.Service.queue):
                # time.sleep(0.1)
                if len(self.Service.queue) > 10:
                    self.Service.queue.popleft()
                data = self.Service.queue.popleft()
                # print("Listening Data, 还有 {0} 可以读".format(len(self.Service.queue)))
                self.stream.write(data)
            else:
                # print("暂时没有数据可以读")
                time.sleep(0.05)
        # 关闭
        self.stream.close()
        self.p.close()