

class Message:
    def __init__(self, channel_name, ID, audio_file_path):
        self.audio_file = audio_file_path
        self.channel_name = channel_name
        self.new = True
        self.ID = ID

    #TODO: destructor that deletes message file
