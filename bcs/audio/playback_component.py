from stmpy import Machine, Driver
from os import system
import os
import time
import contextlib

import pyaudio
import wave

"""
THIS IS NOT USED ANYMORE
"""


class Player:
    def __init__(self):

        self.filename = None

    def play(self, filename):
        # Set chunk size of 1024 samples per data frame
        chunk = 1024

        # Open the sound file
        wf = wave.open(filename, 'rb')

        # Create an interface to PortAudio
        p = pyaudio.PyAudio()

        # Open a .Stream object to write the WAV file to
        # 'output = True' indicates that the sound will be played rather than recorded
        stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                        channels=wf.getnchannels(),
                        rate=wf.getframerate(),
                        output=True)

        # Read data in chunks
        data = wf.readframes(chunk)

        # Play the sound by writing the audio data to the stream
        while data:
            stream.write(data)
            data = wf.readframes(chunk)
        print("ferdig")  # Send done to other stm
        # Close and terminate the stream
        stream.close()
        p.terminate()

    def create_stm(self):
        t0 = {'source': 'initial', 'target': 'ready'}
        t1 = {'trigger': 'start', 'source': 'ready', 'target': 'playing'}
        t2 = {'trigger': 'done', 'source': 'playing', 'target': 'ready'}

        s_playing = {'name': 'playing', 'entry': 'play()'}
        s_ready = {'name': 'ready'}

        stm = Machine(name='stm', transitions=[t0, t1, t2], states=[
                      s_playing, s_ready], obj=player)
        self.stm = stm

        self.driver = Driver()
        self.driver.add_machine(stm)
        self.driver.start()

        print("driver started")

    def start_playback(self, filename):
        self.filename = filename
        self.driver.send('start', 'stm')

    def stop_playback(self):
        self.driver.send('done', 'stm')
        print("stop playback")


'''
#Example
player = Player()
player.create_stm()
player.start_playback("../recorded_message.wav")
time.sleep(2)
player.stop_playback()
'''
