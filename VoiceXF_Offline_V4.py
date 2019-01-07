from ctypes import *
import time
from glob import glob
import pyaudio
import wave


# 调用动态链接库
dll = windll.LoadLibrary("msc_x64.dll")
# 登录参数，apppid一定要和你的下载SDK对应
login_params = b"appid = 5c330a12, work_dir = ."

FRAME_LEN = 640  # Byte

MSP_SUCCESS = 0
# 返回结果状态
MSP_AUDIO_SAMPLE_FIRST = 1
MSP_AUDIO_SAMPLE_CONTINUE = 2
MSP_AUDIO_SAMPLE_LAST = 4
MSP_REC_STATUS_COMPLETE = 5
# 你的语音文件路径
filename = "E:\Resources\LF-NovaVoice\AUDIO_OUTPUT.wav"


class Msp:
    def __init__(self):
        pass

    def login(self):
        ret = dll.MSPLogin(None, None, login_params)
        # print('MSPLogin =>', ret)

    def logout(self):
        ret = dll.MSPLogout()
        # print('MSPLogout =>', ret)

    def isr(self, audiofile, session_begin_params):
        ret = c_int()
        sessionID = c_voidp()
        dll.QISRSessionBegin.restype = c_char_p
        sessionID = dll.QISRSessionBegin(None, session_begin_params, byref(ret))
        # print('QISRSessionBegin => sessionID:', sessionID, 'ret:', ret.value)

        # 每秒【1000ms】  16000 次 * 16 bit 【20B】 ，每毫秒：1.6 * 16bit 【1.6*2B】 = 32Byte
        # 1帧音频20ms【640B】 每次写入 10帧=200ms 【6400B】

        piceLne = FRAME_LEN * 20
        epStatus = c_int(0)
        recogStatus = c_int(0)

        wavFile = open(audiofile, 'rb')
        wavData = wavFile.read(piceLne)

        ret = dll.QISRAudioWrite(sessionID, wavData, len(wavData), MSP_AUDIO_SAMPLE_FIRST, byref(epStatus),
                                 byref(recogStatus))
        # print('len(wavData):', len(wavData), 'QISRAudioWrite ret:', ret, 'epStatus:', epStatus.value, 'recogStatus:', recogStatus.value)
        # time.sleep(0.2)
        while wavData:
            wavData = wavFile.read(piceLne)

            if len(wavData) == 0:
                break

            ret = dll.QISRAudioWrite(sessionID, wavData, len(wavData), MSP_AUDIO_SAMPLE_CONTINUE, byref(epStatus),
                                     byref(recogStatus))
            # print('len(wavData):', len(wavData), 'QISRAudioWrite ret:', ret, 'epStatus:', epStatus.value, 'recogStatus:', recogStatus.value)
            time.sleep(0.2)

        ret = dll.QISRAudioWrite(sessionID, None, 0, MSP_AUDIO_SAMPLE_LAST, byref(epStatus), byref(recogStatus))
        # print('len(wavData):', len(wavData), 'QISRAudioWrite ret:', ret, 'epStatus:', epStatus.value, 'recogStatus:', recogStatus.value)

        # -- 获取音频
        laststr = ''
        counter = 0
        while recogStatus.value != MSP_REC_STATUS_COMPLETE:
            ret = c_int()
            dll.QISRGetResult.restype = c_char_p
            retstr = dll.QISRGetResult(sessionID, byref(recogStatus), 0, byref(ret))
            if retstr is not None:
                laststr += retstr.decode()
                # print(laststr)
            # print('ret:', ret.value, 'recogStatus:', recogStatus.value)
            counter += 1
            time.sleep(0.2)
            counter += 1
            if counter == 500:
                laststr += '讯飞语音识别失败'
                break

        print(laststr)
        print(sessionID)
        # ret = dll.QISRSessionEnd(sessionID, "\0")
        # print('end ret: ', ret)
        return laststr

def audio_record(out_file, rec_time):
    CHUNK = 1024
    FORMAT = pyaudio.paInt16 #16bit编码格式
    CHANNELS = 1 #单声道
    RATE = 16000 #16000采样频率
    p = pyaudio.PyAudio()
    # 创建音频流
    stream = p.open(format=FORMAT, # 音频流wav格式
                    channels=CHANNELS, # 单声道
                    rate=RATE, # 采样率16000
                    input=True,
                    frames_per_buffer=CHUNK)
    print("Start Recording...")
    frames = [] # 录制的音频流
    # 录制音频数据
    for i in range(0, int(RATE / CHUNK * rec_time)):
        data = stream.read(CHUNK)
        frames.append(data)
    # 录制完成
    stream.stop_stream()
    stream.close()
    p.terminate()
    print("Recording Done...")
    # 保存音频文件
    wf = wave.open(out_file, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

def XF_text(filepath, audiorate):
    msp = Msp()
    msp.login()
    session_begin_params = b"sub = iat, ptt = 0, result_encoding = utf8, result_type = plain, domain = iat"
    if 16000 == audiorate:
        session_begin_params = b"sub = iat, aue=speex;7, auf=audio/L16;rate=8000, ptt = 0, result_encoding = utf8, result_type = plain, domain = iat"
    text = msp.isr(filepath, session_begin_params)
    msp.logout()
    return text


if __name__ == '__main__':
    # 8000为音频码率
    audio_record('AUDIO_OUTPUT.wav', 3)  # 录制语音指令
    res = XF_text(filename, 16000)