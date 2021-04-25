import os

class Message:
    def __init__(self, channel_name, ID, audio_file_path):
        self.audio_file_path = audio_file_path
        self.channel_name = channel_name
        self.new = True
        self.ID = ID

    # destructor that deletes message file when message object is deleted
    def __del__(self):
        os.remove(self.audio_file_path)

    def play(self):
        self.new = False
        return self.audio_file_path
