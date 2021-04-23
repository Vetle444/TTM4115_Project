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
    Use start_recording() to start a recording.
    Use stop_recording() to stop a recording.
    '''

    def __init__(self):
        self.recording = False
        self.chunk = 1024  # Record in chunks of 1024 samples
        self.sample_format = pyaudio.paInt16  # 16 bits per sample
        self.channels = 2
        self.fs = 44100  # Record at 44100 samples per second
        self.filename = "recorded_message.wav"
        self.p = pyaudio.PyAudio()

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
        # Terminate the PortAudio interface
        self.p.terminate()
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

    def create_stm(self):
        t0 = {'source': 'initial', 'target': 'ready'}
        t1 = {'trigger': 'start', 'source': 'ready', 'target': 'recording'}
        t2 = {'trigger': 'done', 'source': 'recording', 'target': 'processing'}
        t3 = {'trigger': 'done', 'source': 'processing', 'target': 'ready'}

        s_recording = {'name': 'recording', 'do': 'record()', "stop": "stop()"}
        s_processing = {'name': 'processing', 'do': 'process()'}

        stm = Machine(name='stm', transitions=[t0, t1, t2, t3], states=[
                      s_recording, s_processing], obj=self)
        self.stm = stm

        self.driver = Driver()
        self.driver.add_machine(stm)
        self.driver.start()
        print("driver started")

    def stop_stm(self):
        self.driver.stop()
        print("driver stopped")

    def start_recording(self):
        self.driver.send('start', 'stm')

    def stop_recording(self):
        self.driver.send('stop', 'stm')


# Example code
'''
recorder = Recorder()
recorder.create_stm()
recorder.start_recording()
time.sleep(3)
recorder.stop_recording()
recorder.stop_stm()
'''