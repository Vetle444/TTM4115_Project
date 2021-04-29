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
        self.recipientList = []
        self.loudnessMode = False
        self.doNotDisturbMode = False
        self.subscribed = []
        self.driver = None
        self.state_to_window = {
            #'state': 'window',
            'standby': 'Standby',
            'waiting for command': 'Waiting for command',
            'toggle general channel': 'Select receiving channels',
            'choose state': 'window',
            'choose recipient listen': 'New messages per channel', #"Messages from channel " + self.selectedChannel doesnt correspond to a state
            'choose recipient send': 'Choose recipient',
            'record message': 'Record Message', # "Stop recording and send" doesnt correspond to a state
            'replay message': 'window',
            'play message': f'Message from channel {self.chosen_channel}',
            'play action': 'window', # no window?
            'replay action': 'window', # no window?
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
              'effect': 'self.recorder.stop_recording(*)'
              }
              
        ''' deprecated
        t7 = {'trigger': 't',  # Starts timer on entry recording message if reaches 60s message is to long
              'source': 'recording message',
              'target': 'recording message',
              'effect': "recorded_message_too_long"}
        '''

        t8 = {'trigger': 'answer',
              'source': 'play action',
              'target': 'recording message'
              }
        """
        t9 = {'trigger': 'skip',
              'source': 'replay action',
              'function': 'replay_next_function'
              }
        """

        t10 = {'trigger': 'cancel',
               'source': 'play action',
               'target': 'waiting for command',
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

        t13 = {'trigger': 'invalid',
               'source': 'choose recipient listen',
               'target': 'choose recipient listen'
               # read here
               }

        t14 = {'trigger': 'finished',
               'source': 'choose recipient listen',
               'target': 'replay message'
               }

        t7 = {'trigger': 'cancel',
                'source': 'choose message listen',
                'target': 'choose recipient listen'
                }

        t15 = {'trigger': 'choose_mode',
               'source': 'waiting for command',
               'target': 'choose state'
               }
        t16 = {'trigger': 'send',
               'source': 'waiting for command',
               'target': 'choose recipient send'
               }

        t17 = {'trigger': 'cancel',
               'source': 'choose recipient send',
               'target': 'waiting for command'
               }
        """ deprecated
        t18 = {'trigger': 'invalid',
               'source': 'choose recipient send',
               'target': 'choose recipient send'
               }
        """
        t19 = {'trigger': 'finished',
               'source': 'choose recipient send',
               'target': 'recording message',
               'effect': 'start_recording(*)'
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

        t23 = {'trigger': 'cancel',
               'source': 'choose state',
               'target': 'waiting for command'
               }

        t24 = {'trigger': 'chosen',
               'source': 'choose state',
               'target': 'waiting for command'
               }

        t26 = {'trigger': 'cancel',
               'source': 'replay action',
               'target': 'waiting for command'
               }
        t27 = {'trigger': 'finished',
               'source': 'play message',
               'target': 'play action'
               }
        t28 = {'trigger': 'finished',
               'source': 'play message',
               'target': 'play action'
               }

        t29 = {'trigger': 'timeout',
                'source': 'waiting for command',
                'target': 'standby'}

        # the states:
        standby = {'name': 'standby',
                   'entry': 'start_timer("t", 3000); ui_show_standby'}

        waiting_for_command = {'name': 'waiting for command',
                               'entry': 'start_timer("timeout", 15000); ui_show_waitingForCommand'}

        toggle_general_channel = {'name': 'toggle general channel',
                                  'entry': 'ui_show_toggleGeneralChannels'}

        choose_state = {'name': 'choose state',
                        'entry': 'ui_show_chooseState'}

        choose_recipient_listen = {'name': 'choose recipient listen',
                                   'entry': 'ui_show_recipient_listen'}

        choose_recipient_send = {'name': 'choose recipient send',
                                 'entry': 'ui_show_recipient_send'}

        record_message = {'name': 'recording message',
                          'entry': "ui_show_recording_message"}

        replay_message = {'name': 'replay message',
                          'entry': 'ui_show_replay_message;replay_message()'}

        play_message = {'name': 'play message',
                        'entry': 'ui_show_play_message;self.play_message_from_queue()'}

        play_action = {'name': 'play action',
                       'entry': 'ui_show_play_action;'}

        replay_action = {'name': 'replay action',
                         'entry': 'ui_show_replay_action;'}

        # Change 4: We pass the set of states to the state machine
        self.stm = Machine(name='ui', transitions=[t0, t1, t2, t3, t4, t5, t6, t8, t10, t11, t12, t13, t14, t15, t16, t17, t19, t20, t21, t22, t23, t24, t26, t27, t28, t29], obj=self, states=[
                           standby, waiting_for_command, toggle_general_channel, choose_state, choose_recipient_listen, choose_recipient_send, record_message, replay_message, play_message, play_action, replay_action])

    def compound_transition_msg_queue(self):
        if 0 < len(self.new_msg_queue) <= 5 and not (self.doNotDisturbMode or self.loudnessMode):
            return 'play message'
        elif len(self.new_msg_queue) > 5:
            # Delete queue
            self.new_msg_queue = []
            # read
            return 'waiting for command'
        else:
            return 'standby'

    """
    def compound_transition_replay_end(self):
        if self.ID < self.ui.new_msg_queue[-1]:
            self.ID += 1
            return "replay message"
        else:
            print("All messages played")  # read
            return "waiting for command"
    """
    def delete_first_msg_queue(self):
        del self.new_msg_queue[0]

    """ deprecated
    def recorded_message_too_long(self):
        print("Message too long, try again")  # read
    """

    def toggle_channel_subscribe(self):
        # get channels from the UI
        """
        if channel_name == "invalid":
            print("A channel with this name does not exist!")
            return "toggle general channel"
        else:
            self.mqtt.subscribe(self.recipient)
            return "waiting for command"
        """

        for channel in self.mqtt.channel_list:
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
        self.play(self.new_msg_queue[0].play())
        self.chosen_channel = self.new_msg_queue[0].channel_name  # Used for answer

    def replay_message(self):
        self.play(self.chosen_message.play())

    """ deprecated
        def choose_channel_send(self):
        # ui chose channel returns a list of channels,
        self.recipient = self.ui.choose_channel(self.subscribed)
    """

    """ deprecated
        def choose_channel_replay(self):
        # ui chose channel returns a list of channels, used for replay
        self.recipient = self.ui.choose_channel()
    """

    def getMessages(self):
        return self.messages

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
        # Close and terminate the stream
        stream.close()
        p.terminate()
        self.driver.send('finished', 'stm')

    def update_ui(self):
        if self.stm.state != 'initial':
            print(f"STM asking UI to change subwindow to {self.state_to_window[self.stm.state]} because of state {self.stm.state}")
            self.ui.update(self.state_to_window[self.stm.state])
        # DOESNT WORK because stm.state is only updated after entry actions.. :(

    def ui_show_standby(self):
        #self.ui.start()
        self.ui.update('Standby')
        print("In standby")

    def ui_show_waitingForCommand(self):
        self.ui.update("Waiting for command")
        print("In waiting for command")

    def ui_show_toggleGeneralChannels(self):
        self.ui.update('Select receiving channels')
        print("In select receiving channels")

    def ui_show_playMessage(self):
        self.ui.update(f'Message from channel {self.chosen_channel}')
        print("Playing message")

    def ui_show_playAction(self):
        pass
        #self.ui.update('window') # TODO does this have a window? tod   o

    def ui_show_chooseRecipientSend(self):
        self.ui.update('Choose recipient')

    def ui_show_recordingMessage(self):
        self.ui.update('Record Message')

    def ui_show_chooseRecipientListen(self):
        self.ui.update('New messages per channel')

    def ui_show_recipient_send(self):
        self.ui.update('Choose recipient')

    def ui_show_ReplayMessage(self):
        pass # TODO
        #self.ui.update('window')

    def ui_show_ReplayAction(self):
        pass # TODO
        #self.ui.update('window')

    def ui_show_ChooseState(self):
        # TODO
        pass
        #self.ui.update('window')

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
