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

        self.channels = []  # All mqtt channels (type string)
        # Channels chosen for subscribing (type string)
        self.receivingChannels = []
        # Channels chosen for sending (type string)
        self.recipientChannels = []

        # Channels containing incoming messages (type dict, key=channel, val=msg)
        self.channelsWithMessages = []
        # All the incoming messages in the selected channel (type list of msg)
        self.messagesInChannel = []
        # Title has the channel name in it, hence dynamic title, so cannot fetch sub window by name (type string)
        self.selectedChannel = None

        self.app = gui()

        self.subwindow_standby_create()
        self.subwindow_mainmenu_create()
        self.subwindow_toggleChannel_create()
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
        Main menu, for choosing all main functions. When receiving channels are chosen, 
        new messages should pop-up here.
        '''
        self.app.startSubWindow("Main menu")
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
        self.app.hideSubWindow("Main menu")

    def subwindow_toggleChannel_create(self, channel_list):
        '''
        Select receiving channels for listening.
        '''

        for i in range(50):  # TODO: Remove before prod
            self.channels.append("Test" + str(i))

        # TODO: Call peer class to get channels, anwd set self.channels
        self.app.startSubWindow("Select receiving channels")
        self.app.startScrollPane("ChannelPane")

        self.app.startFrame("ChannelFrame", 0, 0)
        for c in range(len(self.channels)):
            if c % 2:  # TODO: For adding colors later maybe(?)
                self.app.addCheckBox(self.channels[c], c, 1)
            else:
                self.app.addCheckBox(self.channels[c], c, 1)
        self.app.stopFrame()
        self.app.stopScrollPane()

        self.app.startFrame("ChannelButtons", 1, 1)
        self.app.addButton(
            "Submit", self.button_submit_toggleChannel, len(self.channels), 0)
        self.app.addButton(
            "Cancel", self.cancel(), len(self.channels), 1)
        self.app.stopFrame()

        self.app.stopSubWindow()
        self.app.hideSubWindow("Select receiving channels")

    def subwindow_chooseRecipient_create(self):
        self.app.startSubWindow("Choose recipient")

        self.recipientChannels = []

        self.app.startScrollPane("RecipientPane")
        self.app.startFrame("RecipientFrame", 0, 0)
        for i in range(len(self.receivingChannels)):
            self.app.addNamedCheckBox(
                self.receivingChannels[i], self.receivingChannels[i] + "_recipient", i, 1)

        self.app.stopFrame()
        self.app.stopScrollPane()

        self.app.startFrame("RecipientButtons", 1, 1)
        self.app.addNamedButton("Submit", "RecipientSubmit", self.button_submit_chooseRecipient, len(
            self.receivingChannels), 0)
        self.app.addNamedButton("Cancel", "RecipientCancel", self.cancel(), len(
            self.receivingChannels), 1)

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
        self.channelsWithMessages = self.generate_channel_with_messages()
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
                                self.cancel(), len(self.channelsWithMessages.keys()), 1)
        self.app.stopSubWindow()
        self.app.showSubWindow("New messages per channel")

    def subwindow_newMsgMessages_create(self, channel=None):
        '''
        Displays a list of all new messages for the channel provided
        '''
        # TODO: Fetch incoming message(s) from selected channel

        self.selectedChannel = channel
        self.app.startSubWindow(
            "Messages from channel " + self.selectedChannel)

        self.app.startLabelFrame("Select message", 0, 0)
        self.app.startScrollPane("MessagesPane")

        print("displying all messages from channel{}".format(channel))
        for msg in self.channelsWithMessages[channel]:
            self.app.addNamedButton("Message " + msg.ID, msg.ID + "_message" + msg.ID,
                                    lambda x, i=msg.ID: self.onViewMessage(msg))

        self.app.stopScrollPane()
        self.app.stopLabelFrame()

        self.app.addNamedButton("Cancel", "Cancel_Messages", self.button_cancel_newMsgMessages, len(
            self.messagesInChannel), 1)

        self.app.stopSubWindow()
        self.app.showSubWindow("Messages from channel " + self.selectedChannel)

        return None

    def subwindow_message_create(self, message=None):
        '''
        Plays back a selected message
        '''
        self.app.startSubWindow(
            "Message from channel {}".format(self.selectedChannel))
        self.app.setSize(400, 200)
        self.app.startFrame("PlaybackButtons", 1, 1)
        # TODO update here too
        self.app.addButton(
            "Play message", lambda: self.OnPlayMessage(message), 0, 0)
        self.app.addNamedButton(
            "Cancel", "CancelPlayMessage", self.button_cancel_message, 0, 1)
        self.app.stopFrame()

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
        self.app.showSubWindow("Main menu")

    def button_replay_mainmenu(self):
        # Called from main menu, displays channels with new messages (calls CreateNewMessagesPerChannelWindow)
        print("onViewChannelsWithNewMessages called")
        # TODO: Fetch channels from peer class
        self.channelsWithMessages = ["Test1", "Test2"]
        self.app.hideSubWindow("Main menu")
        self.subwindow_newMsgChannels_create()

    def onViewMessagesWithNewMessages(self, channel=None):
        # Should be called on click fromCreateNewMessagesPerChannelWindow
        # Should fint the correct channles, and pass to CreateNewMessagesPerMessageWindow
        # Should close fromCreateNewMessagesPerChannelWindow
        # TODO: Fetch messages from peer class
        self.messagesInChannel = channel
        self.subwindow_newMsgMessages_create(channel)
        self.app.destroySubWindow("New messages per channel")

        return None

    def onViewMessage(self, message):
        print("onViewMessage called")
        self.app.destroySubWindow(
            "Messages from channel " + self.selectedChannel)
        self.subwindow_message_create(message)

        return None

    def button_stopRecording_stopRecord(self):
        # TODO: Stop recording, then send with mqtt
        self.subwindow_chooseRecipient_create() # TODO put this into function to call from stm
        self.SwitchWindow("Stop recording and send", "Main menu")
        self.app.destroySubWindow("Choose recipient")

    #def button_wakeDevice_standby(self):
        #self.stm_component.stm.send("wakeword")
        #self.SwitchWindow("Standby", "Main menu")

    def button_chooseMode_mainmenu(self):
        # TODO: Change mode in peer class (or skip)
        # two booleans
        print(self.app.getRadioButton("mode"))

    #def OnCancelMessagesPerChannelSubWindow(self):
    #    self.app.destroySubWindow("New messages per channel")
    #    self.app.showSubWindow("Main menu")

    def button_cancel_newMsgMessages(self):
        self.app.destroySubWindow(
            "Messages from channel " + self.selectedChannel)
        self.subwindow_newMsgChannels_create()

    def button_send_mainmenu(self):
        self.stm_component.stm.send("send")
        #if(len(self.receivingChannels) == 0):
        #    self.OnError("Not selected any channels",
        #                 "You have not selected any channels to subscribe to, please select receiving channels")
        #    return

        self.subwindow_chooseRecipient_create()
        self.SwitchWindow("Main menu", "Choose recipient")

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
    def button_submit_toggleChannel(self):
        # TODO
        for i in range(len(self.channels)):
            if(self.app.getCheckBox(self.channels[i]) and self.channels[i] not in self.receivingChannels):
                self.receivingChannels.append(self.channels[i])
            # Remove if unticked checkbox that was already ticked when moved into subWindow
            elif(self.app.getCheckBox(self.channels[i]) == False and self.channels[i] in self.receivingChannels):
                self.receivingChannels.remove(self.channels[i])

        print(self.receivingChannels)

        self.SwitchWindow("Select receiving channels", "Main menu")

        return None

    def button_cancel_toggleChannel(self):
        # If you untick checkboxes that are in active receiving channels and then cancel, set the checkboxes that are in active receiving channels to true again
        for i in range(len(self.channels)):
            if(self.app.getCheckBox(self.channels[i]) == False and self.channels[i] in self.receivingChannels):
                self.app.setCheckBox(self.channels[i], True, True)

        self.SwitchWindow("Select receiving channels", "Main menu")

    # Sending channels
    def button_submit_chooseRecipient(self):
        # TODO
        for i in range(len(self.receivingChannels)):
            if(self.app.getCheckBox(self.receivingChannels[i] + "_recipient")):
                self.recipientChannels.append(self.receivingChannels[i])

        print(self.recipientChannels)
        self.app.destroySubWindow("Choose recipient")
        self.app.showSubWindow("Record Message")

    #def button_cancel_chooseRecipient(self):
    #    self.app.destroySubWindow("Choose recipient")
    #    self.app.showSubWindow("Main menu")

    def OnNotifyStmToggleReceivingChannel(self):
        self.stm_component.stm.send("toggle_channel")

    def SwitchWindow(self, fromSubWindow, toSubWindow):
        self.app.hideSubWindow(fromSubWindow)
        self.app.showSubWindow(toSubWindow)

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

    def update(self, sub_window):
        print(f"UI tries to switch to subwindow {sub_window}")
        if sub_window != self.current_subwindow:
            print(f"updating window from {self.current_subwindow} to {sub_window}!")
            if sub_window in ['']:
                pass
                #self.subwindow_chooseRecipient_create()
                #subwindow_chooseRecipient_create
                #self.subwindow_newMsgChannels_create()
                #self.subwindow_message_create(message)
            else:
                self.app.showSubWindow(sub_window)
            if self.current_subwindow in ['Choose recipient', 'Messages from channel ' + self.selectedChannel, 'New messages per channel']:
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