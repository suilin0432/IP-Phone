from AudioUtils import AudioRecorder, AudioListener
from TCPUtils import TCPService, TCPClient
from UDPUtils import UDPService, UDPClient
import pyaudio
import time


p = pyaudio.PyAudio()


# 纯 TCP连接 测试
# service = TCPService()
# client = TCPClient()
# recorder = AudioRecorder(client, p)
# listener = AudioListener(service, p)
# # print(p.get_device_info_by_index(0)['defaultSampleRate'])
# recorder.start()
# listener.start()
# service.start()
# client.start()
#
# recorder.join()
# listener.join()
# service.join()
# client.join()
#
# print("main finished")


# UDP 数据发送测试
service = TCPService(type="UDP")
client = TCPClient(type="UDP")
sendS = UDPService()
sendC = UDPClient()
recorder = AudioRecorder(sendC, p)
listener = AudioListener(sendS, p)

recorder.start()
listener.start()
service.start()
client.start()
time.sleep(0.1)
while True:
    time.sleep(0.1)
    print(service.STATE, client.STATE)
    if service.STATE == "CONNECTED" and client.STATE == "CONNECTED":
        break

sendS.start()
sendC.start()
recorder.join()
listener.join()
service.join()
client.join()
sendS.join()
sendC.join()
