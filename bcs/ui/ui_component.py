from appJar import gui
#from bcs.mqtt import message_component


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
        self.messagesInChannel = []
        # Title has the channel name in it, hence dynamic title, so cannot fetch sub window by name (type string)
        self.selectedChannel = None

        self.app = gui()

        self.subwindow_standby_create()
        self.subwindow_mainmenu_create()
        #self.subwindow_toggleChannel_create()
        self.subwindow_record_create()
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
        self.app.addButton('Replay old messages',
                           self.button_replay_mainmenu)
        self.app.addButton('Record message', self.button_send_mainmenu)
        self.app.stopLabelFrame()

        self.app.stopSubWindow()
        self.app.hideSubWindow("Waiting for command")

    def subwindow_toggleChannel_create(self):
        '''
        Select receiving channels for listening.
        '''

        channel_list = self.stm_component.mqtt.channel_list

        #for i in range(50):  # TODO: Remove before prod
        #    self.channels.append("Test" + str(i))

        # TODO: Call peer class to get channels, anwd set self.channels
        self.app.startSubWindow("Select receiving channels")
        self.app.startScrollPane("ChannelPane")

        self.app.startFrame("ChannelFrame", 0, 0)
        for c in range(len(channel_list)):
            if c % 2:  # TODO: For adding colors later maybe(?)
                self.app.addCheckBox(channel_list[c], c, 1)
            else:
                self.app.addCheckBox(channel, i, 1)
            self.app.setCheckBox(channel) if channel in self.stm_component.subscribed else None
        self.app.stopFrame()
        self.app.stopScrollPane()

        self.app.startFrame("ChannelButtons", 1, 1)
        self.app.addButton(
            "Submit", lambda: self.button_submit_toggleChannel(channel_list), len(channel_list), 0)
        self.app.addButton(
            "Cancel", self.cancel, len(channel_list), 1)
        self.app.stopFrame()

        self.app.stopSubWindow()
        self.app.showSubWindow("Select receiving channels")

        return None

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
        self.app.addNamedButton("Submit", "RecipientSubmit", lambda: self.button_submit_chooseRecipient(channel_list), len(
            self.receivingChannels), 1)
        self.app.addNamedButton("Cancel", "RecipientCancel", self.cancel, len(
            self.receivingChannels), 0)

        self.app.showSubWindow("Choose recipient")

    def subwindow_record_create(self):
        self.app.startSubWindow("Record Message")
        self.app.setSize(400, 200)

        self.app.addButton("Start recording", self.button_record_record)
        self.app.addNamedButton("Cancel", "Cancel_Record", self.button_cancel_record)

        self.app.stopSubWindow()
        self.app.hideSubWindow("Record Message")

    def subwindow_stopRecording_create(self):
        self.app.startSubWindow("Stop recording and send")

        self.app.addNamedButton("Stop recording and send",
                                "StopRecordingAndSend", self.button_stopRecording_stopRecord)

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

        for channel in self.channelsWithMessages.keys():
            self.app.addNamedButton(channel, channel + "_withMessage",
                                    lambda x, i=channel: self.onViewMessagesWithNewMessages(channel))
            # TODO wat does this do and change, both
        self.app.stopScrollPane()
        self.app.stopLabelFrame()

        self.app.addNamedButton("Cancel", "Cancel_MessagesPerChannel",
                                self.cancel, len(self.stm_component.messages.keys()), 1)
        self.app.stopSubWindow()
        self.app.showSubWindow("New messages per channel")

    def subwindow_newMsgMessages_create(self, channel=None):
        '''
        Displays a list of all new messages for the channel provided
        '''
        # TODO: Fetch incoming message(s) from selected channel

        self.selectedChannel = channel
        self.app.startSubWindow("Messages from channel")

        self.app.startLabelFrame("Select message", 0, 0)
        self.app.startScrollPane("MessagesPane")

        print("displying all messages from channel{}".format(self.stm_component.chosen_channel))
        for msg in self.stm_component.messages[self.stm_component.chosen_channel]:
            self.app.addNamedButton("Message " + msg.ID, msg.ID + "_message" + msg.ID,
                                    lambda x, i=msg.ID: self.onViewMessage(msg))

        self.app.stopScrollPane()
        self.app.stopLabelFrame()

        self.app.addNamedButton("Cancel", "Cancel_Messages", self.button_cancel_newMsgMessages, len(
            self.messagesInChannel), 1)

        self.app.stopSubWindow()
        self.app.showSubWindow("Messages from channel")

        return None

    def subwindow_playMessage_create(self, message=None):
        '''
        Plays back a selected message
        '''
        self.app.startSubWindow(
            "View Message")# from channel {}".format(self.selectedChannel))
        self.app.setSize(400, 200)
        self.app.addLabel('l1', f'Playing message from {self.stm_component.chosen_channel}')
        #self.app.startFrame("PlaybackButtons", 1, 1)
        # TODO update here too
        #self.app.addButton(
        #    "Play message", lambda: self.OnPlayMessage(message), 0, 0)
        #self.app.addNamedButton(
        #    "Cancel", "CancelPlayMessage", self.button_cancel_message, 0, 1)
        #self.app.stopFrame()

        self.app.stopSubWindow()
        self.app.showSubWindow("Message from channel " + self.selectedChannel)

        return None

    def OnPlayMessage(self, message):
        # Should play the message
        # TODO: Play back message, call peer class
        print("Playing the message")
        print(message)
        return None

    def button_cancel_message(self):
        self.app.destroySubWindow(
            "Message from channel " + self.selectedChannel)
        self.app.showSubWindow("Waiting for command")

    def button_replay_mainmenu(self):
        # Called from Waiting for command, displays channels with new messages (calls CreateNewMessagesPerChannelWindow)
        print("onViewChannelsWithNewMessages called")
        # TODO: Fetch channels from peer class
        # self.channelsWithMessages = self.stm_component.messages.keys()
        self.app.hideSubWindow("Waiting for command")
        self.subwindow_newMsgChannels_create()

    def onViewMessagesWithNewMessages(self, channel=None):
        # Should be called on click fromCreateNewMessagesPerChannelWindow
        # Should fint the correct channles, and pass to CreateNewMessagesPerMessageWindow
        # Should close fromCreateNewMessagesPerChannelWindow
        # TODO: Fetch messages from peer class
        self.messagesInChannel = channel
        self.stm_component.recipient = channel
        #self.subwindow_newMsgMessages_create(channel)
        #self.app.destroySubWindow("New messages per channel")
        self.stm_component.stm.send('finished')
        return None

    def button_selectMessage_newMsgMessages(self, message):
        print("onViewMessage called")
        self.stm_component.chosen_message = message
        self.stm_component.stm.send('finished')
        #self.app.destroySubWindow(
        #    "Messages from channel")
        #self.subwindow_message_create(message)
        return None

    def button_stopRecording_stopRecord(self):
        # TODO: Stop recording, then send with mqtt
        self.subwindow_chooseRecipient_create() # TODO put this into function to call from stm
        self.SwitchWindow("Stop recording and send", "Waiting for command")
        self.app.destroySubWindow("Choose recipient")

    #def button_wakeDevice_standby(self):
        #self.stm_component.stm.send("wakeword")
        #self.SwitchWindow("Standby", "Waiting for command")

    def button_chooseMode_mainmenu(self):
        selected_radio_button = self.app.getRadioButton("mode")
        self.stm_component.operation_mode = selected_radio_button
        print("UI set to mode: {}".format(selected_radio_button))

    #def OnCancelMessagesPerChannelSubWindow(self):
    #    self.app.destroySubWindow("New messages per channel")
    #    self.app.showSubWindow("Waiting for command")

    def button_cancel_newMsgMessages(self):
        self.cancel()
        #self.app.destroySubWindow(
        #    "Messages from channel")
        #self.subwindow_newMsgChannels_create()

    def button_send_mainmenu(self):
        self.stm_component.stm.send("send")
        #if(len(self.receivingChannels) == 0):
        #    self.OnError("Not selected any channels",
        #                 "You have not selected any channels to subscribe to, please select receiving channels")
        #    return

        #self.subwindow_chooseRecipient_create()
        #self.SwitchWindow("Waiting for command", "Choose recipient")

    def OnError(self, errr_title, error_msg):
        self.app.errorBox(errr_title, error_msg)
        self.app.setSize(400, 200)

    def button_cancel_record(self):
        self.subwindow_chooseRecipient_create() # TODO: make this into function
        self.SwitchWindow("Record Message", "Choose recipient")

    # On record voice message
    def button_record_record(self):
        # TODO: Start voice recording
        self.SwitchWindow("Record Message", "Stop recording and send")

    # Subscribing channels
    def button_submit_toggleChannel(self, channel_list):
        for channel in channel_list:
            if self.app.getCheckBox(channel) and channel not in self.stm_component.subscribed:
                self.stm_component.subscribed.append(channel)
            # Remove if unticked checkbox that was already ticked when moved into subWindow
            elif(self.app.getCheckBox(channel_list[i]) == False and channel_list[i] in self.stm_component.subscribed):
                self.stm_component.subscribed.remove(channel_list[i])

        print(self.stm_component.subscribed)

        self.stm_component.stm.send("finished")
        return None

    def button_cancel_toggleChannel(self):
        # If you untick checkboxes that are in active receiving channels and then cancel, set the checkboxes that are in active receiving channels to true again
        for i in range(len(self.channels)):
            if(self.app.getCheckBox(self.channels[i]) == False and self.channels[i] in self.receivingChannels):
                self.app.setCheckBox(self.channels[i], True, True)

        self.SwitchWindow("Select receiving channels", "Waiting for command")

    # Sending channels
    def button_submit_chooseRecipient(self, channel_list):
        # TODO
        for i in range(len(channel_list)):
            if(self.app.getCheckBox(channel_list[i] + "_recipient")):
                self.stm_component.recipientList.append(channel_list[i])

        print(self.stm_component.recipientList)

        self.app.destroySubWindow("Choose recipient")
        self.app.showSubWindow("Record Message")

        self.stm_component.stm.send("finished")

    #def button_cancel_chooseRecipient(self):
    #    self.app.destroySubWindow("Choose recipient")
    #    self.app.showSubWindow("Waiting for command")

    def OnNotifyStmToggleReceivingChannel(self):
        self.stm_component.stm.send("toggle_channel")

    def SwitchWindow(self, fromSubWindow, toSubWindow):
        self.app.hideSubWindow(fromSubWindow)
        self.app.showSubWindow(toSubWindow)

    '''
    def generate_channel_with_messages(self):
        # ONLY FOR DEBUGGING
        d = {}
        for i in range(5):
            d["kanal {}".format(str(i))] = []
            for j in range(5):
                m = message_component.Message("channel {}".format(
                    str(i)), "id_k{}_m{}".format(i, j), "some_url")
                d["kanal {}".format(str(i))].append(m)
        return d
    '''

    def update(self, sub_window, message=None, channel=None):
        print(f"UI tries to switch to subwindow {sub_window}")

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
            else:
                self.app.showSubWindow(sub_window)
            if self.current_subwindow in ['Choose recipient', 'New messages per channel', 'View Message', 'Select receiving channels']:
                self.app.destroySubWindow(self.current_subwindow)
            else:
                self.app.hideSubWindow(self.current_subwindow)
            self.current_subwindow = sub_window

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