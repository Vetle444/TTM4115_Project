import time

from stmpy import Machine, Driver
import pyaudio
import wave


class StateMachine_Component:

    def __init__(self):
        self.ui = None
        self.recorder = None
        self.mqtt = None
        self.ID = 0
        self.new_msg_queue = []  # play, List of new messages.
        self.messages = {}  # replay, Dictionary contains all saved messages
        self.chosen_message = None
        self.chosen_channel = None
        self.recipientList = []
        # Default operation_mode is "Listen-mode". Other options are "Loudness-mode" and "Do not disturb-mode"
        self.operation_mode = "Listen-mode"
        self.subscribed = []
        self.driver = None
        self.state_to_window = {
            # 'state': 'window',
            'standby': 'Standby',
            'waiting for command': 'Waiting for command',
            'toggle general channel': 'Select receiving channels',
            'choose state': 'window',
            # "Messages from channel " + self.selectedChannel doesnt correspond to a state
            'choose recipient listen': 'New messages per channel',
            'choose recipient send': 'Choose recipient',
            # "Stop recording and send" doesnt correspond to a state
            'record message': 'Record message',
            'replay message': 'window',
            'play message': f'Message from channel {self.chosen_channel}',
            'play action': 'window',  # no window?
            'replay action': 'window',  # no window?
        }

        t0 = {'source': 'initial',
              'target': 'standby',
              }

        t1 = {'trigger': 'wakeword',
              'source': 'standby',
              'target': 'waiting for command'
              }
        t2 = {'trigger': 't',
              'source': 'standby',
              'function': self.compound_transition_msg_queue
              }
        t3 = {'trigger': 'next',
              'source': 'play action',
              'target': 'play message',
              'effect': "delete_first_msg_queue"
              }
        t4 = {'trigger': 'repeat',
              'source': 'play action',
              'target': 'play message'
              }
        t5 = {'trigger': 'answer',
              'source': 'play action',
              'target': 'recording message',
              'effect': 'delete_first_msg_queue'}

        t6 = {'trigger': 'stop_message',
              'source': 'recording message',
              'target': 'waiting for command',
              'effect': 'stop_recording'

              }

        t8 = {'trigger': 'answer',
              'source': 'replay action',
              'target': 'recording message'
              }

        t10 = {'trigger': 'cancel',
               'source': 'play action',
               'target': 'standby',
               'effect': 'delete_first_msg_queue'
               }
        t11 = {'trigger': 'toggle_channel',
               'source': 'waiting for command',
               'target': 'toggle general channel'
               }

        t12 = {'trigger': 'cancel',
               'source': 'choose recipient listen',
               'target': 'waiting for command'
               }

        t14 = {'trigger': 'finished',
               'source': 'choose recipient listen',
               'target': 'choose message listen'
               }

        t7 = {'trigger': 'cancel',
              'source': 'choose message listen',
              'target': 'choose recipient listen'
              }

        t15 = {'trigger': 'finished',
               'source': 'choose message listen',
               'target': 'replay message'
               }

        t16 = {'trigger': 'send',
               'source': 'waiting for command',
               'target': 'choose recipient send'
               }

        t17 = {'trigger': 'cancel',
               'source': 'choose recipient send',
               'target': 'waiting for command'
               }

        t19 = {'trigger': 'finished',
               'source': 'choose recipient send',
               'target': 'recording message'
               }

        t20 = {'trigger': 'listen',
               'source': 'waiting for command',
               'target': 'choose recipient listen'
               }

        t21 = {'trigger': 'cancel',
               'source': 'toggle general channel',
               'target': 'waiting for command'
               }

        t22 = {'trigger': 'finished',
               'source': 'toggle general channel',
               'effect': 'toggle_channel_subscribe',
               'target': 'waiting for command'
               }

        t26 = {'trigger': 'cancel',
               'source': 'replay action',
               'target': 'choose recipient listen'
               }
        t27 = {'trigger': 'finished',
               'source': 'play message',
               'target': 'play action'
               }
        t28 = {'trigger': 'finished',
               'source': 'replay message',
               'target': 'replay action'
               }

        t29 = {'trigger': 'timeout',
               'source': 'waiting for command',
               'target': 'standby'}

        # the states:
        standby = {'name': 'standby',
                   'entry': 'start_timer("t", 3000); ui_show_standby'}

        waiting_for_command = {'name': 'waiting for command',
                               'entry': 'start_timer("timeout", 5000); ui_show_waitingForCommand'}

        toggle_general_channel = {'name': 'toggle general channel',
                                  'entry': 'ui_show_toggleGeneralChannels'}

        choose_recipient_listen = {'name': 'choose recipient listen',
                                   'entry': 'ui_show_recipient_listen'}

        choose_recipient_send = {'name': 'choose recipient send',
                                 'entry': 'ui_show_recipient_send'}

        record_message = {'name': 'recording message',
                          'entry': "ui_show_recording_message;start_recording()"}

        replay_message = {'name': 'replay message',
                          'entry': 'ui_show_replay_message;replay_message()'}

        play_message = {'name': 'play message',
                        'entry': 'ui_show_play_message;play_message_from_queue'}

        play_action = {'name': 'play action',
                       'entry': 'ui_show_play_action'}

        replay_action = {'name': 'replay action',
                         'entry': 'ui_show_replay_action'}

        choose_message_listen = {'name': 'choose message listen',
                                 'entry': 'ui_show_choose_message_listen'}

        # Change 4: We pass the set of states to the state machine
        self.stm = Machine(name='ui', transitions=[t0, t1, t2, t3, t4, t5, t6, t7, t8, t10, t11, t12, t14, t15, t16, t17, t19, t20, t21, t22, t26, t27, t28, t29], obj=self, states=[
                           standby, waiting_for_command, toggle_general_channel, choose_recipient_listen, choose_recipient_send, record_message, replay_message, play_message, play_action, replay_action, choose_message_listen])

    def compound_transition_msg_queue(self):
        if 0 < len(self.new_msg_queue) <= 5 and self.operation_mode == "Listen-mode":
            print(len(self.new_msg_queue))
            return 'play message'
        elif len(self.new_msg_queue) > 5:
            # Delete queue
            self.new_msg_queue = []
            # read
            return 'waiting for command'
        else:
            return 'standby'

    def delete_first_msg_queue(self):
        del self.new_msg_queue[0]

    def toggle_channel_subscribe(self):
        # get channels from the UI

        for channel in self.mqtt.channel_list:
            if channel != self.mqtt.user_name:
                self.mqtt.unsubscribe(channel)
        for channel in self.subscribed:
            self.mqtt.subscribe(channel)

    def add_message(self, message):
        self.new_msg_queue.append(message)
        if message.channel_name not in self.messages.keys():
            self.messages[message.channel_name] = []
        elif len(self.messages[message.channel_name]) > 30:
            del self.messages[message.channel_name][0]
        self.messages[message.channel_name].append(message)

    def play_message_from_queue(self):
        self.recipientList = [self.new_msg_queue[0].channel_name]
        self.playMessage(self.new_msg_queue[0].play())

    def replay_message(self):
        self.recipientList = [self.chosen_message.channel_name]
        self.playMessage(self.chosen_message.play())

    def getMessages(self):
        return self.messages

    def playMessage(self, filename):
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
        # Close and terminate the stream
        stream.close()
        p.terminate()
        self.driver.send('finished', 'ui')

    def update_ui(self):
        if self.stm.state != 'initial':
            print(
                f"STM asking UI to change subwindow to {self.state_to_window[self.stm.state]} because of state {self.stm.state}")
            self.ui.update(self.state_to_window[self.stm.state])
        # DOESNT WORK because stm.state is only updated after entry actions.. :(

    def ui_show_standby(self):
        # self.ui.start()
        self.ui.update('Standby')
        print("In standby")

    def ui_show_waitingForCommand(self):
        self.ui.update("Waiting for command")
        print("In waiting for command")

    def ui_show_toggleGeneralChannels(self):
        self.ui.update('Select receiving channels')
        print("In select receiving channels")

    def ui_show_play_message(self):
        self.chosen_channel = self.new_msg_queue[0].channel_name
        self.ui.update('Playing message')
        print("Playing message")

    def ui_show_playAction(self):
        pass
        # self.ui.update('window') # TODO does this have a window? tod   o

    def ui_show_chooseRecipientSend(self):
        self.ui.update('Choose recipient')

    def ui_show_recording_message(self):
        self.ui.update('Recording message')

    def ui_show_recipient_listen(self):
        self.ui.update('New messages per channel')

    def ui_show_recipient_send(self):
        self.ui.update('Choose recipient')

    def ui_show_replay_message(self):
        self.ui.update('Playing message')

    def ui_show_choose_message_listen(self):
        self.ui.update('Messages from channel')

    def ui_show_play_action(self):
        self.ui.update("Replay controls")

    def ui_show_replay_action(self):
        self.ui.update("Replay controls")

    def setUI(self, ui):
        self.ui = ui

    def setMQTT(self, mqtt):
        self.mqtt = mqtt

    def setRecorder(self, recorder):
        self.recorder = recorder

    def setDriver(self, driver):
        self.driver = driver

    def start_recording(self):
        self.recorder.start_recording(self.recipientList)

    def stop_recording(self):
        self.recorder.stop_recording()
