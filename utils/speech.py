from gtts import gTTS
import pygame
import os

pygame.mixer.init()

FILENAME = "temp_voice.mp3"

def speak(text):
    tts = gTTS(text=text, lang="en")
    tts.save(FILENAME)

    pygame.mixer.music.load(FILENAME)
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        continue

    pygame.mixer.music.unload()
    os.remove(FILENAME)