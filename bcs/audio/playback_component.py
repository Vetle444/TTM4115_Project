from stmpy import Machine, Driver
from os import system
import os
import time
import contextlib

import pyaudio
import wave

"""
How to use:
Initiate Player class
Call create stm function
Call start playback
Call stop playback
"""

        
class Player:
    def __init__(self):

        self.filename=None

    def play(self):
        # Set chunk size of 1024 samples per data frame
        chunk = 1024  

        # Open the sound file 
        wf = wave.open(self.filename, 'rb')

        # Create an interface to PortAudio
        p = pyaudio.PyAudio()

        # Open a .Stream object to write the WAV file to
        # 'output = True' indicates that the sound will be played rather than recorded
        stream = p.open(format = p.get_format_from_width(self.wf.getsampwidth()),
                        channels = self.wf.getnchannels(),
                        rate = self.wf.getframerate(),
                        output = True)

        # Read data in chunks
        data = wf.readframes(chunk)

        # Play the sound by writing the audio data to the stream
        self.stop = False
        while data != '':
            #if self.stop:
            #    break
            stream.write(data)
            data = wf.readframes(chunk)

        # Close and terminate the stream
        stream.close()
        p.terminate()

    def stop(self):
        print("stop")
        self.stop = True
        #self.wf.close()

    def create_stm(self):
        t0 = {'source': 'initial', 'target': 'ready'}
        t1 = {'trigger': 'start', 'source': 'ready', 'target': 'playing'}
        t2 = {'trigger': 'done', 'source': 'playing', 'target': 'ready'}

        s_playing = {'name': 'playing', 'do': 'play()', 'stop': 'stop()'}

        stm = Machine(name='stm', transitions=[t0, t1, t2], states=[s_playing], obj=player)
        self.stm = stm

        self.driver = Driver()
        self.driver.add_machine(stm)
        self.driver.start()

        print("driver started")

    def start_playback(self,filename):
        self.filename=filename
        self.driver.send('start', 'stm')

    def stop_playback(self):
        self.driver.send('stop', 'stm')
        print("driver stopped?")

"""
#Example
player = Player()
player.create_stm()
player.start_playback("../recorded_message.wav")
player.stop_playback()
"""