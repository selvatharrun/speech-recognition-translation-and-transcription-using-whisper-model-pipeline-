import sounddevice as sd #for recording audio
import wavio as wv #for writing on an audio file
import datetime
from transformers import pipeline #for importing model
import os

#first run pip install -r requirements.txt in ur terminal
#you additionally need torch and ffmpeg although u dont use it anywhere in the code, the tools that i have used need them for functioning

freq = 44100
duration = int(input("enter duration of recording: ")) #enter the time for recording, for example if u give 6, it will record for 6 seconds after u give input, only whatever in the recording willl be translateds

print('Recording')

while True:
    ts = datetime.datetime.now()

    # Start recorder with the given values of duration and sample frequency
    recording = sd.rec(int(duration * freq), samplerate=freq, channels=1)

    # Record audio for the given number of seconds
    sd.wait()

    # Convert the NumPy array to audio file
    wv.write(f"./audio.wav", recording, freq, sampwidth=2)

    sd.stop()
    break

model= pipeline('automatic-speech-recognition', model = 'openai/whisper-medium', device = 0) #we import the model using pipeline


text = model('audio.wav') #this is the transcription
print(text)

os.remove("audio.wav")#file will be deleted after transcripting

