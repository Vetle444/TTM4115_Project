from stmpy import Machine, Driver

class StateMachine_Component:

    def __init__(self, ui, mqtt, player, recorder):
        self.ui = ui
        self.player = player
        self.recorder = recorder
        self.mqtt = mqtt
        self.ID = 0
        self.new_msg_queue = []
        self.messages = {}
        self.recipient = None

        t0 = {'source': 'initial',
              'target': 'standby',
              }

        t1 = {'trigger': 'wakeword',
              'source': 'standby',
              'target': 'waiting for command'
              }
        t2 = {'trigger': 't',
              'source': 'standby',
              'function': 'queue_transition'
              }
        t3 = {'trigger': 'next',
              'source': 'play message',
              'target': 'play message',
              'effect': "delete_first_msg_queue"
              }
        t4 = {'trigger': 'repeat',
              'source': 'play message',
              'target': 'play message'
              }
        t5 = {'trigger': 'answer',
              'source': 'play message',
              'target': 'recording message',
              'effect': 'delete_first_msg_queue'}

        t6 = {'trigger': 'stop_message',
              'source': 'recording message',
              'target': 'waiting for command',
              'effect': 'recorder.stop_recording(*)'
              }

  #      t7 = {'trigger': 't', # Starts timer on entry recording message if reaches 60s message is to long
   #           'source': 'recording message',
    #          'target': 'recording message',
     #         'effect': "recorded_message_too_long"}

        t8 = {'trigger': 'answer',
              'source': 'replay message',
              'target': 'recording message'
              }
        t9 = {'trigger': 'skip',
              'source': 'replay message',
              'function': 'replay_skip_function'
              }

        t10 = {'trigger': 'cancel',
              'source': 'play message',
              'target': 'waiting for command'
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
               #read here
               }

        t14 = {'trigger': 'channel_valid',
               'source': 'choose recipient listen',
               'target': 'replay message'
               }

        t15 = {'trigger': 'choose_mode',
               'source': 'waiting for command',
               'target': 'choose state'
               }
        t16 = {'trigger': 'send',
               'source': 'waiting for command',
               'target': 'choose recipient'
               }

        t17 = {'trigger': 'cancel',
               'source': 'choose recipient send',
               'target': 'waiting for command'
               }

        t18 = {'trigger': 'invalid',
               'source': 'choose recipient send',
               'target': 'choose recipient send'
               # read here
             }

        t19 = {'trigger': 'channel_valid',
               'source': 'choose recipient send',
               'target': 'replay message'
               }
        t20 = {'trigger': 'listen',
               'source': 'waiting for command',
               'target': 'choose recipient'
               }

        t21 = {'trigger': 'cancel',
               'source': 'toggle general channel',
               'target': 'waiting for command'
                }

        t22 = {'trigger': 'done',
               'source': 'toggle general channel',
               'function': 'toggle_channel_choice(*)'
               }

        t23 = {'trigger': 'cancel',
               'source': 'choose state',
               'target': 'waiting for command'
                }

        t24 = {'trigger': 'chosen',
               'source': 'choose state',
               'target': 'waiting for command'
               }

        t25 = {'trigger': 'cancel',
               'source': 'recording message',
               'target': 'waiting for command'
               }

        t26 = {'trigger': 'cancel',
               'source': 'replay message',
               'target': 'waiting for command'
               }

        # the states:
        standby = {'name': 'standby',
                    'entry': 'start_timer("t", 500)'}

        waiting_for_command = {'name': 'waiting for command',
                               'entry': 'start_timer("time_out", 500)'}

        toggle_general_channel = {'name': 'toggle general channel',
                   'entry': 'self.channel_name = self.ui.get_valid_new_channel_name'}

        choose_state = {'name': 'choose state',
                        'entry': 'self.ui.choose_state'}

        choose_recipient_and_message_listen = {'name': 'choose recipient listen',
                                   'do': 'choose_channel_from_received'}

        choose_recipient_send = {'name': 'choose recipient send',
                                 'do': 'choose_channel_from_list'}

        record_message = {'name': 'recording message',
                          'entry': "self.recorder.start_recording()",
                          }


        replay_message = {'name': 'replay message',
                          'entry': 'self.replay_message_from_dict()'}# TODO move to transition??

        play_message = {'name': 'play message',
                          'entry': 'self.play_message_from_queue()'}

        # Change 4: We pass the set of states to the state machine
        machine = Machine(name='stm_traffic', transitions=[t0, t1, t2, t3, t4, t5, t6, t8, t9, t10, t11, t12, t13, t14, t15, t16, t17, t18, t19, t20, t21, t22, t23, t24, t25, t26], obj=ui,
                          states=[standby, waiting_for_command, toggle_general_channel, choose_state, choose_recipient_and_message_listen, choose_recipient_send, record_message, replay_message, play_message])

    def queue_transition(self):
        if 0 < len(self.ui.new_msg_queue) <= 5 and not (self.ui.do_not_disturb or self.ui.loudness_mode):
            return 'play message'
        elif len(self.ui.new_msg_queue) > 5:
            self.ui.new_msg_queue = []
            # read
            return 'waiting_for_command'
        else:
            return 'play message'

    def replay_skip_function(self):
        if self.ID < self.ui.new_msg_queue[-1]:
            self.ID += 1
            return "replay message"
        else:
            print("All messages played") #read
            return "waiting for command"

    def delete_first_msg_queue(self):
        del self.new_msg_queue[0]

    def recorded_message_too_long(self):
        print("Message too long, try again") #read

    def toggle_channel_choice(self, channel_name):
        if channel_name == "invalid":
            print("A channel with this name does not exist!")
            return "toggle general channel"
        else:
            self.mqtt.subscribe(self.recipient)
            return "waiting for command"

    def add_message(self, message):
        self.new_msg_queue.append(message)
        if message.channel_name not in self.messages.keys():
            self.messages[message.channel_name] = []
        elif len(self.messages[message.channel_name]) > 30:
            del self.messages[message.channel_name][0]
        self.messages[message.channel_name].append(message)

    def play_message_from_queue(self):
        self.player.play(self.new_msg_queue[0].play())
        self.recipient = self.new_msg_queue[0].channel_name

    def replay_message_from_dict(self):
        index= self.ui.index  #RETRIEVE VARIABLE FROM UI COMPONENT
        self.player.play(self.messages[self.recipient][index].play())

    def choose_channel_from_all(self):
        self.recipient = self.ui.choose_channel(self.mqtt.channel_list)

    def choose_channel_from_received(self):
        self.recipient = self.ui.choose_channel([self.messages.keys()])