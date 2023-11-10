import json
import pyttsx3, vosk, pyaudio, requests
from PIL import Image
from io import BytesIO


class Assistant:
    def __init__(self, speaking=False, listening=False):
        self.speaking = speaking
        self.breed = None
        self.img = None
        self.content = None
        self.name = None
        self.url = None

        if speaking:
            self.tts = pyttsx3.init()
            voices = self.tts.getProperty('voices')
            self.tts.setProperty('voices', 'en')
            for voice in voices:
                if voice.name == 'Microsoft David Desktop - English (United States)':
                    self.tts.setProperty('voice', voice.id)

        if listening:
            vosk.SetLogLevel(-1)
            model = vosk.Model('E:/ITMO/Академка/ДизайнВещейБудущего/4/Voice assistant/vosk-model-small-en-us-0.15')
            self.record = vosk.KaldiRecognizer(model, 16000)
            pa = pyaudio.PyAudio()
            self.stream = pa.open(format=pyaudio.paInt16,
                                  channels=1,
                                  rate=16000,
                                  input=True,
                                  frames_per_buffer=8000)
            self.stream.start_stream()
            self.update()
            self.handle_voice()

    def listen(self):
        while True:
            data = self.stream.read(4000, exception_on_overflow=False)
            if self.record.AcceptWaveform(data) and len(data) > 0:
                answer = json.loads(self.record.Result())
                if answer['text']:
                    yield answer['text']

    def speak(self, msg):
        self.tts.say(msg)
        self.tts.runAndWait()

    def update(self):
        req = requests.get('https://dog.ceo/api/breeds/image/random')
        json = req.json()
        self.url = json['message']
        self.split_url()
        self.content = requests.get(self.url).content
        self.img = Image.open(BytesIO(self.content))
        self.log('\nPicture updated ✓')

    def show(self):
        self.img.show()

    def image_info(self):
        info = f'Format: {self.img.format}, size: {self.img.width} x {self.img.height}'
        self.log(info)

    def save(self):
        with open(self.name, 'wb') as handler:  # todo name
            handler.write(self.content)
            self.log('Picture is saved ✓')

    def close(self):
        self.log('Closing...')
        quit()

    def split_url(self):
        data = self.url.split("/")
        self.name = data[-1]
        self.breed = data[-2]

    def log(self, msg):
        print(msg)
        if self.speaking is True:
            self.speak(msg)

    def know_breed(self):
        self.log(f'Dog breed is {self.breed}')

    def handle_voice(self):
        self.log('Ready to listen')
        for text in self.listen():
            if text == 'close':
                self.close()
            elif text == 'next picture':
                self.update()
            elif text == 'show the picture':
                self.show()
            elif text == 'save the picture':
                self.save()
            elif text == 'dog breed':
                self.know_breed()
            elif text == 'picture info':
                self.image_info()
            else:
                pass


rec = Assistant()
rec.speak('Hello, Let`s watch at cute dogs!')
rec.update()
rec.show()
rec.save()
rec.know_breed()
rec.image_info()
rec.listen()
rec.close()
