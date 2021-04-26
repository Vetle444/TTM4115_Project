from stmpy import Machine, Driver

class StateMachine_Component:

    def __init__(self, ui, broker, port): #object is UI
        self.ui = ui
        t0 = {'source': 'initial',
              'target': 'standby',
              'effect': f'mqtt.start({broker},{port})'
              }

        t1 = {'trigger': 'wakeword',
              'source': 'standby',
              'target': 'waiting_for_command'
              }
        t2 = {'trigger': 't',
              'source': 'standby',
              'function': 'que_transition'
              }
        t3 = {'trigger': 'skip',
              'source': 'play message',
              'target': 'play message',
              'effect': "delete_first_msg_que"
              }
        t5 = {'trigger': 'repeat',
              'source': 'play message',
              'target': 'play message'
              }
        t5 = {'trigger': 'answer',
              'source': 'play message',
              'target': 'recording message',
              'effect': 'delete_first_msg_que; turn_red_on'}

        # the states:
        standby = {'name': 'standby',
                    'entry': 'start_timer("t", 500)'}

        waiting_for_command = {'name': 'waiting for command'}

        toggle_general_channel = {'name': 'toggle general channel',
                   'entry': 'self.ui.get_valid_new_channel_name'}

        choose_state = {'name': 'choose state',
                        'entry': 'self.ui.choose_state'}

        choose_recipient_listen = {'name': 'choose recipient listen',
                        'entry': 'self.ui.choose_channel'}

        choose_recipient_send = {'name': 'choose recipient send',
                                   'entry': 'self.ui.choose_channel'}

        record_message = {'name': 'recording message',
                        'entry': start recording here}

        send_message = {'name': 'sending message',
                          'entry': start sending here}

        replay_message = {'name': 'replay message',
                          'entry': replay message here}

        play_message = {'name': 'play message',
                          'entry': play message here}

        # Change 4: We pass the set of states to the state machine
        machine = Machine(name='stm_traffic', transitions=[t0, t1, t2, t3, t4, t5], obj=ui,
                          states=[standby, waiting_for_command, toggle_general_channel, choose_state, choose_recipient_listen, choose_recipient_send, record_message, send_message, replay_message, play_message])

    def que_transition(self):
        if  0 < len(self.ui.new_msg_queue) <= 5 and not (self.ui.doNotDisturb or self.ui.loudnessMode):
            return 'play message'
        elif len(self.ui.new_msg_queue) > 5:
            self.ui.new_msg_queue = []
            # read
            return 'waiting_for_command'
        else:
            return 'play message'

    def delete_first_msg_que(self):
        del self.ui.new_msg_queue[0]

