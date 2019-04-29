from AudioUtils import AudioRecorder, AudioListener
from TCPUtils import TCPService, TCPClient
import pyaudio

# 测试一下, 开一个线程为TCPService

p = pyaudio.PyAudio()
service = TCPService()
client = TCPClient()
recorder = AudioRecorder(client, p)
listener = AudioListener(service, p)
# print(p.get_device_info_by_index(0)['defaultSampleRate'])
recorder.start()
listener.start()
service.start()
client.start()

recorder.join()
listener.join()
service.join()
client.join()

print("main finished")