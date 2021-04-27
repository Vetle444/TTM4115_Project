from appJar import gui


class UI_Component:
    def __init__(self, channels):
        self.channels = channels  # All mqtt channels
        self.receivingChannels = []  # Channels chosen for subscribing
        self.recipientChannels = []  # Channels chosen for sending

        # Used as storage when playingback of old messages
        self.chosenChannelForPlayback = ""
        # Used as storage when playingback of old messages and new messages
        self.chosenMessageForPlayback = ""

        # Channels containing incoming messages
        self.channelsWithMessages = ["Test1", "Test2"]
        # All the incoming messages containing in the channel selected
        self.messagesInChannel = ["Hei", "Halloen"]

        # Title has the channel name in it, hence dynamic title, so cannot fetch sub window by name
        self.selectedChannel = None

        self.create_gui()


    def CreateStandbySubWindow(self):
        self.app.startSubWindow("Standby")
        self.app.addButton('Wake device', self.OnWake)

        self.app.stopSubWindow()

    def CreateCommandSubWindow(self):
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
        self.app.setRadioButtonChangeFunction("mode", self.OnChooseMode)
        self.app.stopLabelFrame()

        self.app.startLabelFrame("Select a command", 0, 1)
        self.app.addButton('Toggle receiving channels', lambda: self.SwitchWindow(
            "Main menu", "Select receiving channels"))
        #self.app.addButton('Replay old messages', lambda: self.SwitchWindow("Main menu", "Playback message"))
        self.app.addButton('Replay old messages',
                           self.onViewChannelsWithNewMessages)
        self.app.addButton('Record message', self.OnChooseRecipient)
        self.app.stopLabelFrame()

        self.app.stopSubWindow()
        self.app.hideSubWindow("Main menu")

    def CreateChannelSubWindow(self):
        self.app.startSubWindow("Select receiving channels")
        self.app.startScrollPane("ChannelPane")

        self.app.startFrame("ChannelFrame", 0, 0)
        for i in range(len(self.channels)):
            if i % 2:  # TODO: For adding colors later maybe
                self.app.addCheckBox(self.channels[i], i, 1)
            else:
                self.app.addCheckBox(self.channels[i], i, 1)
        self.app.stopFrame()
        self.app.stopScrollPane()

        self.app.startFrame("ChannelButtons", 1, 1)
        self.app.addButton(
            "Submit", self.OnSubmitChooseChannel, len(self.channels), 0)
        self.app.addButton(
            "Cancel", self.OnCancelChooseChannel, len(self.channels), 1)
        self.app.stopFrame()

        self.app.stopSubWindow()
        self.app.hideSubWindow("Select receiving channels")

    def CreateChooseRecipientSubWindow(self):
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
        self.app.addNamedButton("Submit", "RecipientSubmit", self.OnSubmitChooseRecipient, len(
            self.receivingChannels), 0)
        self.app.addNamedButton("Cancel", "RecipientCancel", self.OnCancelChooseRecipient, len(
            self.receivingChannels), 1)

    def CreateRecordSubWindow(self):
        self.app.startSubWindow("Record Message")
        self.app.setSize(400, 200)

        self.app.addButton("Start recording", self.OnRecord)
        self.app.addNamedButton("Cancel", "Cancel_Record", self.OnCancelRecord)

        self.app.stopSubWindow()
        self.app.hideSubWindow("Record Message")

    def CreateStopRecordSubWindow(self):
        self.app.startSubWindow("Stop recording and send")

        self.app.addNamedButton("Stop recording and send",
                                "StopRecordingAndSend", self.onStopRecording)

        self.app.stopSubWindow()

    def CreatePlaybackMessageWindow(self):
        '''
        Plays back message stored as chosenChannelForPlayback.
        '''
        self.app.startSubWindow("Playback message")
        # TODO: Use change view function to go to main menu
        self.app.addButton("View old messages", None)
        self.app.addNamedButton("Main Menu", "GotoMainMenuFromPlayback",
                                lambda: self.SwitchWindow("Playback message", "Main menu"))
        self.app.stopSubWindow()

    def CreateNewMessagesPerChannelWindow(self):
        '''
        Displays a list of all channels (with new messages?)
        Flow: Main menu -> CreateNewMessagesPerChannelWindow (THIS)
        -> CreateNewMessagesPerMessageWindow -> CreatePlaybackMessageWindow
        Stores chosen channel in object variable chosenChannelForPlayback.
        '''
        print("CreateNewMessagesPerChannelWindow is called")
        self.app.startSubWindow("New messages per channel")

        # TODO: Create some view
        # TODO: Fetch channels that have messages

        self.app.startLabelFrame("Select channel", 0, 0)
        self.app.startScrollPane("ChannelMessagesPane")

        for i in range(len(self.channelsWithMessages)):
            self.app.addNamedButton(self.channelsWithMessages[i], self.channelsWithMessages[i] + "_withMessage", 
            lambda x, i=i: self.onViewMessagesWithNewMessages(self.channelsWithMessages[i]))

        self.app.stopScrollPane()
        self.app.stopLabelFrame()


        self.app.addNamedButton("Cancel", "Cancel_MessagesPerChannel", self.OnCancelMessagesPerChannelSubWindow, len(self.channelsWithMessages), 1)

        self.app.stopSubWindow()

        self.app.showSubWindow("New messages per channel")

    def CreateNewMessagesPerMessageWindow(self, channel=None):
        '''
        Displays a list of all messages for the channel stored in object variable chosenMessageForPlayback.
        Flow: Main menu -> CreateNewMessagesPerChannelWindow
        -> CreateNewMessagesPerMessageWindow (THIS) -> CreatePlaybackMessageWindow
        Stores chosen message in object variable chosenMessageForPlayback.
        '''
        #TODO: Fetch incoming message(s) from selected channel

        self.selectedChannel = channel
        self.app.startSubWindow("Messages from channel " + self.selectedChannel)

        self.app.startLabelFrame("Select message", 0, 0)
        self.app.startScrollPane("MessagesPane")

        for i in range(len(self.messagesInChannel)):
            self.app.addNamedButton("Message " + str(i), self.messagesInChannel[i] + "_message" + str(i), 
            lambda x, i=i: self.onViewMessage(self.channelsWithMessages[i]))

        self.app.stopScrollPane()
        self.app.stopLabelFrame()

        self.app.addNamedButton("Cancel", "Cancel_Messages", self.OnCancelMessagesSubWindow, len(self.messagesInChannel), 1)
        
        self.app.stopSubWindow()
        self.app.showSubWindow("Messages from channel " + self.selectedChannel)

        return None

    def CreateMessageSubWindow(self, message=None):
        '''
        Displays a list of all messages for a given channel
        Flow: Main menu -> CreateNewMessagesPerChannelWindow
        -> CreateNewMessagesPerMessageWindow (THIS) -> CreatePlaybackMessageWindow
        '''
        #TODO: Play incoming message

        self.app.startSubWindow("Message from channel " + self.selectedChannel)

        self.app.setSize(400, 200)

        self.app.startFrame("PlaybackButtons", 1, 1)
        self.app.addButton("Play message", lambda: self.OnPlayMessage(message), 0, 0)
        self.app.addNamedButton("Cancel", "CancelPlayMessage", self.OnCancelPlayMessage, 0, 1)
        self.app.stopFrame()

        self.app.stopSubWindow()
        self.app.showSubWindow("Message from channel " + self.selectedChannel)

        return None

    def OnPlayMessage(self, message):
        # Should play the message

        print("Playing message")

        return None

    def OnCancelPlayMessage(self):
        self.app.destroySubWindow("Message from channel " + self.selectedChannel)
        self.app.showSubWindow("Main menu")

    
    def onViewChannelsWithNewMessages(self):
        # Should be called on click from main menu
        # Should find the correct channels, and pass to CreateNewMessagesPerChannelWindow
        # Should close main menu
        print("onViewChannelsWithNewMessages called")
        self.app.hideSubWindow("Main menu")
        self.CreateNewMessagesPerChannelWindow()

    def onViewMessagesWithNewMessages(self, channel=None):
        # Should be called on click fromCreateNewMessagesPerChannelWindow
        # Should fint the correct channles, and pass to CreateNewMessagesPerMessageWindow
        # Should close fromCreateNewMessagesPerChannelWindow

        self.CreateNewMessagesPerMessageWindow(channel)
        self.app.destroySubWindow("New messages per channel")

        return None

    def onViewMessage(self, message):
        self.app.destroySubWindow("Messages from channel " + self.selectedChannel)
        self.CreateMessageSubWindow(message)

        return None

    def onStopRecording(self):
        # TODO: Stop recording, then send with mqtt
        self.CreateChooseRecipientSubWindow()
        self.SwitchWindow("Stop recording and send", "Main menu")
        self.app.destroySubWindow("Choose recipient")

    def OnWake(self):
        self.SwitchWindow("Standby", "Main menu")

    # def OnToggleReceivingChannel(self):
    #    self.SwitchWindow("Main menu", "Select receiving channels")

    def OnChooseMode(self):
        print(self.app.getRadioButton("mode"))


    def OnCancelMessagesPerChannelSubWindow(self): 
        self.app.destroySubWindow("New messages per channel")
        self.app.showSubWindow("Main menu")
    
    def OnCancelMessagesSubWindow(self):
        self.app.destroySubWindow("Messages from channel " + self.selectedChannel)
        self.CreateNewMessagesPerChannelWindow()

    #def OnReplayOld(self):
        #self.OnError("Not implemented", "This function is not implemented yet")
        #self.SwitchWindow("Main menu", "Playback message")

    def OnChooseRecipient(self):
        if(len(self.receivingChannels) == 0):
            self.OnError("Not selected any channels",
                         "You have not selected any channels to subscribe to, please select receiving channels")
            return

        self.CreateChooseRecipientSubWindow()

        self.SwitchWindow("Main menu", "Choose recipient")

    def OnError(self, errr_title, error_msg):
        self.app.errorBox(errr_title, error_msg)
        self.app.setSize(400, 200)

    def OnCancelRecord(self):
        self.CreateChooseRecipientSubWindow()
        self.SwitchWindow("Record Message", "Choose recipient")

    # On record voice message
    def OnRecord(self):
        # TODO: Start voice recording
        self.SwitchWindow("Record Message", "Stop recording and send")

    # On send reorded message
    def onSend(self):
        return None

    # Subscribing channels
    def OnSubmitChooseChannel(self):

        for i in range(len(self.channels)):
            if(self.app.getCheckBox(self.channels[i]) and self.channels[i] not in self.receivingChannels):
                self.receivingChannels.append(self.channels[i])
            # Remove if unticked checkbox that was already ticked when moved into subWindow
            elif(self.app.getCheckBox(self.channels[i]) == False and self.channels[i] in self.receivingChannels):
                self.receivingChannels.remove(self.channels[i])

        print(self.receivingChannels)

        self.SwitchWindow("Select receiving channels", "Main menu")

        return None

    def OnCancelChooseChannel(self):
        # If you untick checkboxes that are in active receiving channels and then cancel, set the checkboxes that are in active receiving channels to true again
        for i in range(len(self.channels)):
            if(self.app.getCheckBox(self.channels[i]) == False and self.channels[i] in self.receivingChannels):
                self.app.setCheckBox(self.channels[i], True, True)

        self.SwitchWindow("Select receiving channels", "Main menu")

    # Sending channels
    def OnSubmitChooseRecipient(self):
        for i in range(len(self.receivingChannels)):
            if(self.app.getCheckBox(self.receivingChannels[i] + "_recipient")):
                self.recipientChannels.append(self.receivingChannels[i])

        print(self.recipientChannels)

        self.app.destroySubWindow("Choose recipient")

        self.app.showSubWindow("Record Message")

    def OnCancelChooseRecipient(self):
        # self.app.clearAllCheckBoxes()

        self.app.destroySubWindow("Choose recipient")
        self.app.showSubWindow("Main menu")

    def create_gui(self):
        self.app = gui()

        self.CreateStandbySubWindow()
        self.CreateCommandSubWindow()
        self.CreateChannelSubWindow()
        self.CreateRecordSubWindow()
        self.CreateStopRecordSubWindow()
        self.CreatePlaybackMessageWindow()
        #self.CreateNewMessagesPerMessageWindow()

        self.app.go(startWindow="Standby")

    def SwitchWindow(self, fromSubWindow, toSubWindow):
        self.app.hideSubWindow(fromSubWindow)
        self.app.showSubWindow(toSubWindow)


channels = []
for i in range(50):
    channels.append("Test" + str(i))
test = UI_Component(channels)

print("LUL")
