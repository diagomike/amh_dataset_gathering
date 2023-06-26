import time
import pygame
import pyautogui as pg
import pyperclip
import soundfile as sf
import numpy as np
import ffmpeg

#TODO Make sure to download source.wav and vad.json to current dir before run

SAMPLE_RATE = 16000

def single_30(audio, segments, filename):
    concatenated_audio = []
    padding = np.zeros(int(SAMPLE_RATE)) # 1 second padding
    for seg in segments['segments']:
        f1 = int(seg[0] * SAMPLE_RATE)
        f2 = int(seg[1] * SAMPLE_RATE)
        concatenated_audio.append(audio[f1:f2])
        concatenated_audio.append(padding)
    concatenated_audio = np.concatenate(concatenated_audio)
    sf.write(filename, concatenated_audio, SAMPLE_RATE)

def load_audio(file: str, sr: int = SAMPLE_RATE):
    """Open an audio file and read as mono waveform, resampling as necessary"""
    try:
        # This launches a subprocess to decode audio while down-mixing and resampling as necessary.
        # Requires the ffmpeg CLI and `ffmpeg-python` package to be installed.
        print(file)
        out, _ = (
            ffmpeg.input(file, threads=0)
            .output("-", format="s16le", acodec="pcm_s16le", ac=1, ar=sr)
            .run(cmd=["ffmpeg", "-nostdin"], capture_stdout=True, capture_stderr=True)
        )
    except ffmpeg.Error as e:
        raise RuntimeError(f"Failed to load audio: {e.stderr.decode()}") from e

    return np.frombuffer(out, np.int16).flatten().astype(np.float32) / 32768.0

# load vad file
import json
segments = json.loads(open('vad.json','r').read())
filename = 'C:/Users/diago/Desktop/docs/temp.wav'
main = load_audio('C:/Users/diago/Desktop/docs/source.wav', SAMPLE_RATE)

import librosa 
ss = librosa.load('source.wav',sr=SAMPLE_RATE)

pygame.init()
pygame.mixer.init()
time.sleep(10)

for idx, segment_30 in enumerate(segments):
    single_30(main,segment_30,filename)
    print(f'Writing {idx}')

    pg.typewrite(f'\n{idx}|')
    time.sleep(1)

    pg.hotkey('ctrl', 'shift', 's')
    time.sleep(3)

    print(f'Playing {filename}')

    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        continue
    pg.press('esc')
    time.sleep(2)

# Finished Dataset Generation, Loading to Json
pg.hotkey('ctrl','a')
time.sleep(3)
pg.hotkey('ctrl', 'c')

text_data = pyperclip.paste()
transcriptions = [line.strip().split('|') for line in text_data]

# Load the JSON data
with open('vad.json', 'r',encoding='utf8') as f:
    segments = json.load(f)

# Create a dictionary to map file names to transcriptions
transcription_dict = {segment_id: transcription for segment_id, transcription in transcriptions}

# Add the transcriptions to the JSON data
for segment_id, utterance in enumerate(segments):
    utterance['text'] = transcription_dict[segment_id]

# Save the updated JSON data
with open('segments.json', 'w',encoding='utf8') as f:
    json.dump(segments, f, indent=4,ensure_ascii=False)

#TODO Now Take Back the segments.json file to Colab and Continue Run