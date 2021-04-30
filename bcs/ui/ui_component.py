from appJar import gui


# from bcs.mqtt import message_component


class UI_Component:
    def __init__(self):
        '''
        UI driver for the application BCS.
        '''
        self.current_subwindow = None
        self.stm_component = None
        print("Created UI_component")

    def start(self):

        # All the incoming messages in the selected channel (type list of msg)
        # self.messagesInChannel = []
        # Title has the channel name in it, hence dynamic title, so cannot fetch sub window by name (type string)
        # self.selectedChannel = None

        self.app = gui()

        self.subwindow_standby_create()
        self.subwindow_mainmenu_create()
        # self.subwindow_toggleChannel_create()
        # self.subwindow_record_create()
        self.subwindow_stopRecording_create()
        # self.CreatePlaybackMessageWindow()
        # self.CreateNewMessagesPerMessageWindow()

        self.current_subwindow = "Standby"
        self.app.go(startWindow="Standby")

    def subwindow_standby_create(self):
        self.app.startSubWindow("Standby")
        self.app.addButton('Wake device', lambda: self.stm_component.stm.send("wakeword"))
        self.app.stopSubWindow()

    def subwindow_mainmenu_create(self):
        '''
        Waiting for command, for choosing all main functions. When receiving channels are chosen, 
        new messages should pop-up here.
        '''
        self.app.startSubWindow("Waiting for command")
        self.app.setSize(400, 200)

        self.app.startLabelFrame("Select mode", 0, 2)
        self.app.addRadioButton("mode", "Listen-mode")
        self.app.addRadioButton("mode", "Do not disturb-mode")
        self.app.addRadioButton("mode", "Loudness-mode")
        self.app.setRadioButtonChangeFunction("mode", self.button_chooseMode_mainmenu)
        self.app.stopLabelFrame()

        self.app.startLabelFrame("Select a command", 0, 1)
        self.app.addButton('Toggle receiving channels', lambda: self.stm_component.stm.send("toggle_channel"))
        self.app.addButton('Replay old messages', lambda: self.stm_component.stm.send("listen"))
        self.app.addNamedButton('Record message', 'Record message_btn', lambda: self.stm_component.stm.send("send"))
        self.app.stopLabelFrame()

        self.app.stopSubWindow()
        self.app.hideSubWindow("Waiting for command")

    def subwindow_toggleChannel_create(self):
        '''
        Select receiving channels for listening.
        '''

        channel_list = self.stm_component.mqtt.channel_list
        channel_list = [channel for channel in channel_list if "group" in channel.lower()]

        print("USERNAME" + self.stm_component.mqtt.user_name.lower())
        self.app.startSubWindow("Select receiving channels")
        self.app.startScrollPane("ChannelPane")

        self.app.startFrame("ChannelFrame", 0, 0)

        # Add app.setCheckBox() for checked
        for i, channel in enumerate(channel_list):
            if i % 2:  # TODO: For adding colors later maybe(?)
                self.app.addCheckBox(channel, i, 1)
            else:
                self.app.addCheckBox(channel, i, 1)
            self.app.setCheckBox(channel) if channel in self.stm_component.subscribed else None
        self.app.stopFrame()
        self.app.stopScrollPane()

        self.app.startFrame("ChannelButtons", 1, 1)
        self.app.addButton(
            "Submit", lambda: self.button_submit_toggleChannel(channel_list), len(channel_list), 0)
        self.app.addButton(
            "Cancel", lambda: self.cancel(), len(channel_list), 1)
        self.app.stopFrame()

        self.app.stopSubWindow()
        self.app.showSubWindow("Select receiving channels")

        # return None

    def subwindow_chooseRecipient_create(self):
        self.app.startSubWindow("Choose recipient")

        channel_list = self.stm_component.mqtt.channel_list

        self.app.startScrollPane("RecipientPane")
        self.app.startFrame("RecipientFrame", 0, 0)
        for i in range(len(channel_list)):
            self.app.addNamedCheckBox(
                channel_list[i], channel_list[i] + "_recipient", i, 1)

        self.app.stopFrame()
        self.app.stopScrollPane()

        self.app.startFrame("RecipientButtons", 1, 1)

        self.app.addNamedButton("Record", "RecipientRecord", lambda: self.button_submit_chooseRecipient(channel_list),
                                len(
                                    channel_list), 1)
        self.app.addNamedButton("Cancel", "RecipientCancel", lambda: self.cancel(), len(
            channel_list), 0)

        self.app.showSubWindow("Choose recipient")

    def stop_recording(self):
        print("UI is asking to stop the recording")
        self.stm_component.stm.send("finished")

    def subwindow_stopRecording_create(self):
        self.app.startSubWindow("Recording message")

        self.app.addNamedButton("Stop recording and send",
                                "StopRecordingAndSend", lambda: self.stm_component.stm.send('stop_message'))

        self.app.stopSubWindow()

    def subwindow_newMsgChannels_create(self):
        '''
        Displays a list of all channels with new messages
        '''
        print("CreateNewMessagesPerChannelWindow is called")
        # TODO: Fetch channels that have messages (set self.channelsWithMessages)
        # self.channelsWithMessages = self.stm_component.messages
        self.app.startSubWindow("New messages per channel")

        self.app.startLabelFrame("Select channel", 0, 0)
        self.app.startScrollPane("ChannelMessagesPane")

        for channel in self.stm_component.messages.keys():
            self.app.addNamedButton(channel, channel,
                                    lambda channel=channel: self.onViewMessagesWithNewMessages(channel))

        self.app.stopScrollPane()
        self.app.stopLabelFrame()

        self.app.addNamedButton("Cancel", "Cancel_MessagesPerChannel", lambda: self.cancel(),
                                len(self.stm_component.messages.keys()), 1)
        self.app.stopSubWindow()
        self.app.showSubWindow("New messages per channel")

    def subwindow_newMsgMessages_create(self):
        '''
        Displays a list of all new messages for the channel provided
        '''
        # TODO: Fetch incoming message(s) from selected channel

        # self.selectedChannel = channel
        self.app.startSubWindow("Messages from channel")

        self.app.startLabelFrame("Select message", 0, 0)
        self.app.startScrollPane("MessagesPane")

        print("displying all messages from channel{}".format(self.stm_component.chosen_channel))
        for msg in self.stm_component.messages[self.stm_component.chosen_channel]:
            self.app.addNamedButton("Message " + str(msg.ID), str(msg.ID) + "_message" + str(msg.ID),
                                    lambda: self.button_selectMessage_newMsgMessages(msg))

        self.app.stopScrollPane()
        self.app.stopLabelFrame()

        '''
        self.app.addNamedButton("Cancel", "Cancel_Messages2", Lambda: self.cancel(), len(
            self.stm_component.messages[self.stm_component.chosen_channel]), 1)
        '''

        self.app.stopSubWindow()
        self.app.showSubWindow("Messages from channel")

        return None

    def subwindow_playMessage_create(self, message=None):
        '''
        Plays back a selected message
        '''
        self.app.startSubWindow("Playing message")  # from channel {}".format(self.selectedChannel))
        self.app.setSize(400, 200)

        self.app.addLabel('l1', f'Playing message from {self.stm_component.chosen_channel}')
        self.app.stopSubWindow()
        self.app.showSubWindow("Playing message")

    def subwindow_replayControls_create(self, message=None):
        '''
        Plays back a selected message
        '''
        self.app.startSubWindow("Replay controls")  # from channel {}".format(self.selectedChannel))
        self.app.setSize(400, 200)
        self.app.startFrame("ReplayButtons", 1, 1)

        self.app.addNamedButton(
            "Cancel", "Cancel_replayControls", lambda: self.cancel(), 1, 1)
        if self.stm_component.mqtt.user_name.lower() != self.stm_component.chosen_channel.lower():
            self.app.addButton(
                "Answer", lambda: self.stm_component.stm.send("answer"), 1, 0)

        self.app.stopFrame()

        self.app.stopSubWindow()
        self.app.showSubWindow("Replay controls")

    def onViewMessagesWithNewMessages(self, channel=None):
        self.stm_component.chosen_channel = channel
        self.stm_component.stm.send('finished')

    def button_selectMessage_newMsgMessages(self, message):
        print("onViewMessage called")
        print(message)
        self.stm_component.chosen_message = message
        self.stm_component.stm.send('finished')

    def button_chooseMode_mainmenu(self):
        selected_radio_button = self.app.getRadioButton("mode")
        self.stm_component.operation_mode = selected_radio_button
        print("UI set to mode: {}".format(selected_radio_button))

    def OnError(self, errr_title, error_msg):
        self.app.errorBox(errr_title, error_msg)
        self.app.setSize(400, 200)

    # Subscribing channels
    def button_submit_toggleChannel(self, channel_list):
        for channel in channel_list:
            if self.app.getCheckBox(channel) and channel not in self.stm_component.subscribed:
                self.stm_component.subscribed.append(channel)
            # Remove if unticked checkbox that was already ticked when moved into subWindow
            elif not self.app.getCheckBox(channel) and channel in self.stm_component.subscribed:
                self.stm_component.subscribed.remove(channel)

        print(self.stm_component.subscribed)
        self.stm_component.stm.send("finished")

    # Sending channels
    def button_submit_chooseRecipient(self, channel_list):
        for channel in channel_list:
            if (self.app.getCheckBox(channel + "_recipient") and channel not in self.stm_component.recipientList):
                self.stm_component.recipientList.append(channel)
            elif not self.app.getCheckBox(channel + "_recipient") and channel in self.stm_component.recipientList:
                self.stm_component.recipientList.remove(channel)

        self.stm_component.stm.send("finished")

    '''
    def generate_channel_with_messages(self):
        # ONLY FOR DEBUGGING
        d = {}
        for i in range(5):
            d["kanal {}".format(str(i))] = []
            for j in range(5):
                    str(i)), "id_k{}_m{}".format(i, j), "some_url")
                d["kanal {}".format(str(i))].append(m)
        return d
    '''

    def update(self, sub_window, message=None, channel=None):
        print(f"UI tries to switch to subwindow {sub_window}")

        try:
            if sub_window != self.current_subwindow:
                print(f"updating window from {self.current_subwindow} to {sub_window}!")
                if sub_window == 'Choose recipient':
                    self.subwindow_chooseRecipient_create()
                elif sub_window == 'New messages per channel':
                    self.subwindow_newMsgChannels_create()
                elif sub_window == 'Replay controls':
                    self.subwindow_replayControls_create()
                elif sub_window == 'Select receiving channels':
                    self.subwindow_toggleChannel_create()
                elif sub_window == 'Messages from channel':
                    self.subwindow_newMsgMessages_create()
                elif sub_window == "Playing message":
                    self.subwindow_playMessage_create()
                # elif sub_window == 'Stop recording and send':

                else:
                    self.app.showSubWindow(sub_window)
                if self.current_subwindow in ['Choose recipient', 'New messages per channel', 'View Message',
                                              'Select receiving channels', 'Messages from channel', 'Playing message',
                                              'Replay controls']:
                    self.app.destroySubWindow(self.current_subwindow)
                else:
                    self.app.hideSubWindow(self.current_subwindow)
                self.current_subwindow = sub_window
        except AttributeError as err:
            print("app not defined yet")

    def cancel(self):
        self.stm_component.stm.send("cancel")


'''
channels = []
for i in range(50):
    channels.append("Test" + str(i))
'''
'''
test = UI_Component()
test.start()
'''
