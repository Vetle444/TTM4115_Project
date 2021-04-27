from appJar import gui


class UI_Component:
    def __init__(self, channels):
        self.channels = channels  # All mqtt channels
        self.receivingChannels = []  # Channels chosen for subscribing
        self.recipientChannels = []  # Channels chosen for sending

        self.channelsWithMessages = ["Channel 1", "Channel 2"]
        self.messages = ["Message 1", "Message 2"]


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

    def CreatePlaybackMessageWindow(self, message="Msg 1", channel="Chnl 1"):
        '''
        Plays back message stored as chosenChannelForPlayback.

        self.app.startSubWindow("Playback message")
        # TODO: Use change view function to go to main menu
        self.app.addButton("View old messages", None)
        self.app.addNamedButton("Main Menu", "GotoMainMenuFromPlayback",
                                lambda: self.SwitchWindow("Playback message", "Main menu"))
        self.app.stopSubWindow()
        '''
        return None


    def CreateNewMessagesPerMessageWindow(self, channel=None):
        self.app.startSubWindow("Unread messages in channel")
        self.app.showSubWindow("Unread messages in channel")
        self.app.addLabel("Here are the messages for channel: {}".format(channel))
        self.app.addButton("Some button xyz", lambda: None)
        print("CreateNewMessagesPerChannelWindow called")
        #self.app.stopSubWindow()

    def CreateNewMessagesPerChannelWindow(self):
        self.app.startSubWindow("Unread messages per channel")
        self.app.showSubWindow("Unread messages per channel")
        self.app.addLabel("Here are the channels")
        self.app.addButton("Some button 123", self.onViewMessagesWithNewMessages)
        print("CreateNewMessagesPerChannelWindow called")
        #self.app.stopSubWindow()

    def onViewChannelsWithNewMessages(self):
        # Should be called on click from main menu
        # Should find the correct channels, and pass to CreateNewMessagesPerChannelWindow
        # Should close main menu
        print("onViewChannelsWithNewMessages called")
        self.CreateNewMessagesPerChannelWindow()


        #self.app.hideSubWindow("Main menu")
        #self.app.showSubWindow("New messages per channel")
        #self.SwitchWindow("Main menu", "New messages per channel")

    def onViewMessagesWithNewMessages(self):
        # Should be called on click fromCreateNewMessagesPerChannelWindow
        # Should fint the correct channles, and pass to CreateNewMessagesPerMessageWindow
        # Should close fromCreateNewMessagesPerChannelWindow
        print("onViewMessagesWithNewMessages called")
        self.CreateNewMessagesPerMessageWindow()
        self.app.destroySubWindow("Unread messages per channel")
        #self.app.hideSubWindow("New messages per channel")
        #self.app.showSubWindow("New messages per message")

    def onViewPlaybackMessage(self):
        self.app.hideSubWindow("New messages per message")
        self.app.showSubWindow("Playback message")

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

    # def OnReplayOld(self):
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
        #self.CreatePlaybackMessageWindow()
        #self.CreateNewMessagesPerMessageWindow()
        #self.CreateNewMessagesPerChannelWindow()

        self.app.go(startWindow="Standby")

    def SwitchWindow(self, fromSubWindow, toSubWindow):
        self.app.hideSubWindow(fromSubWindow)
        self.app.showSubWindow(toSubWindow)


channels = []
for i in range(50):
    channels.append("Test" + str(i))
test = UI_Component(channels)
