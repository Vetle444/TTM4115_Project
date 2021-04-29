from stmpy import Machine, Driver
from os import system
import os
import time

import pyaudio
import wave


class Recorder:
    '''
    This class provides audio recording. Make sure pyaudio is installed (both from pip 
    and possible via a packet manager as well).

    How to use:
    Initiate the object.
    Use create_stm() to create the state machine.
    Use recording() to start a recording.
    '''

    def __init__(self, mqtt):
        self.recording = False
        self.chunk = 1024  # Record in chunks of 1024 samples
        self.sample_format = pyaudio.paInt16  # 16 bits per sample
        self.channels = 2
        self.fs = 44100  # Record at 44100 samples per second
        self.filename = "recorded_message.wav"
        self.p = pyaudio.PyAudio()
        self.mqtt=mqtt
        self.channel_names=[]

        # Make recorder state machine
        t0 = {'source': 'initial', 'target': 'record_ready'}
        t1 = {'trigger': 'start', 'source': 'record_ready', 'target': 'recording'}
        t2 = {'trigger': 'done', 'source': 'recording', 'target': 'processing'}
        t3 = {'trigger': 'done', 'source': 'processing', 'target': 'record_ready'}


# TODO no ready state, stuck after processing: FIXED??

        s_ready = {'name': 'record_ready'}
        s_recording = {'name': 'recording', 'do': 'record()', "stop": "stop()"}
        s_processing = {'name': 'processing', 'do': 'process()'}

        record_stm = Machine(name='record_stm', transitions=[t0, t1, t2, t3], states=[
            s_recording, s_processing, s_ready], obj=self)
        self.record_stm = record_stm

        self.driver=None

    def record(self):
        print("recording")
        stream = self.p.open(format=self.sample_format,
                             channels=self.channels,
                             rate=self.fs,
                             frames_per_buffer=self.chunk,
                             input=True)
        self.frames = []  # Initialize array to store frames
        # Store data in chunks for 3 seconds
        self.recording = True
        while self.recording:
            data = stream.read(self.chunk)
            self.frames.append(data)
        print("recording done")

        # Stop and close the stream
        stream.stop_stream()
        stream.close()

        print("stream closed")

    def stop(self):
        print("stop")
        self.recording = False

    def process(self):
        print("processing")
        # Save the recorded data as a WAV file
        wf = wave.open(self.filename, 'wb')
        wf.setnchannels(self.channels)
        wf.setsampwidth(self.p.get_sample_size(self.sample_format))
        wf.setframerate(self.fs)
        wf.writeframes(b''.join(self.frames))
        wf.close()
        print("processing done")
        for channel in self.channel_names:
            self.mqtt.send_file(channel, self.filename)

    #def stop_stm(self):
    #    self.driver.stop()
    #    print("driver stopped")

    def start_recording(self, channel_name):
        self.channel_names = channel_name
        self.driver.send('start', 'record_stm')

    def stop_recording(self):
        self.driver.send('stop', 'record_stm')

    def setDriver(self,driver):
        self.driver=driver


# Example code
"""
recorder = Recorder()
recorder.create_stm()
recorder.start_recording([])8
time.sleep(30)
recorder.stop_recording()
time.sleep(2)
# recorder.stop_stm()
"""