import pyaudio
import threading
import time

# 音频播放器
class AudioListener(threading.Thread):
    def __init__(self, Service, CHUNK=128, FORMAT = pyaudio.paInt16, CHANNELS = 2, RATE = 2560):
        threading.Thread.__init__(self)
        self.Service = Service
        self.CHUNK = CHUNK
        self.FORMAT = FORMAT
        self.CHANNEL = CHANNELS
        self.RATE = RATE

    def run(self):
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=self.FORMAT,
                        channels=self.CHANNELS,
                        rate=self.RATE,
                        output=True,
                        frames_per_buffer=self.CHUNK)
        while self.Service.STATE != "CONNECTED":
            time.sleep(0.1)
        data = None
        while self.Service.STATE == "CONNECTED":
            if len(self.Service.queue):
                data = self.Service.queue.popleft()
                self.stream.write(data)
            else:
                print("暂时没有数据可以读")
                time.sleep(0.02)
        # 关闭
        self.stream.close()
        self.p.close()