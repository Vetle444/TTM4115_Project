import os
from pathlib import Path


class Message:
    """
    Class that contains a voice message
    will delete audiofile when object is deleted

    Functions:
    play(): - sets self.new to False to indicate message has been played atleast once
            - returns patho to audio file for playback

    """

    def __init__(self, channel_name, ID, audio_file_path):
        self.audio_file_path = Path(audio_file_path).resolve()
        self.channel_name = channel_name
        self.new = True
        self.ID = ID

    # destructor that deletes message file when message object is deleted
    def __del__(self):
        print(f"deleted message {self.ID}")
        os.remove(self.audio_file_path)

    def __str__(self):
        s = "ID is: {}\nIs new: {}\nChannel name: {}\nAudio file path: {}".format(
            self.id, self.new, self.channel_name, self.audio_file_path)
        return s

    def play(self):
        self.new = False
        return self.audio_file_path

    def id(self):
        return self.ID
