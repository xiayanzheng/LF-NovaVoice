import os
from pocketsphinx import LiveSpeech, get_model_path

model_path = get_model_path()

speech = LiveSpeech(
    verbose=False,
    sampling_rate=16000,
    buffer_size=2048,
    no_search=False,
    full_utt=False,
    # hmm=os.path.join(model_path, 'zh/zh_broadcastnews_ptm256_8000'),
    # lm=os.path.join(model_path, 'zh/zh_broadcastnews_64000_utf8.DMP'),
    # dic=os.path.join(model_path, 'zh/zh_broadcastnews_utf8.dic')
    hmm=os.path.join(model_path, 'en-us'),
    lm=os.path.join(model_path, 'en-us.lm.bin'),
    dic=os.path.join(model_path, 'cmudict-en-us.dict')
)
for phrase in speech:
    print("phrase:", phrase)
    input('结果是否接近？')
    # print(phrase.segments(detailed=True))
