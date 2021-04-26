from appJar import gui

class UI_Component:
    def __init__(self):
        self.channels = []

        for i in range(50):
            self.channels.append("Test" + str(i))

        self.receivingChannels = [] # Channels chosen for subscribing
        self.recipientChannels = [] # Channels chosen for sending

        self.create_gui()


    def CreateStandbySubWindow(self):
        self.app.startSubWindow("Standby")
        self.app.addButton('Wake device', self.OnWake)


    def CreateCommandSubWindow(self):
        self.app.startSubWindow("Main menu")
        self.app.setSize(400,200)

        self.app.startLabelFrame("Select mode", 0, 2)
        self.app.addRadioButton("mode", "Listen-mode")
        self.app.addRadioButton("mode", "Do not disturb-mode")
        self.app.addRadioButton("mode", "Loudness-mode")
        self.app.setRadioButtonChangeFunction("mode", self.OnChooseMode)
        self.app.stopLabelFrame()

        self.app.startLabelFrame("Select a command", 0, 1)
        self.app.addButton('Toggle receiving channels', self.OnToggleReceivingChannel)
        self.app.addButton('Listen', self.OnListen)
        self.app.addButton('Record message', self.OnChooseRecipient)
        self.app.stopLabelFrame()

        self.app.hideSubWindow("Main menu")


    def CreateChannelSubWindow(self):
        self.app.startSubWindow("Select receiving channels")
        self.app.startScrollPane("ChannelPane")

        self.app.startFrame("ChannelFrame", 0, 0)
        for i in range(len(self.channels)):
            if i % 2: #TODO: For adding colors later maybe
                self.app.addCheckBox(self.channels[i], i, 1)
            else:
                self.app.addCheckBox(self.channels[i], i, 1)
        self.app.stopFrame()
        self.app.stopScrollPane()

        self.app.startFrame("ChannelButtons", 1, 1)
        self.app.addButton("Submit", self.OnSubmitChooseChannel, len(self.channels), 0)
        self.app.addButton("Cancel", self.OnCancelChooseChannel, len(self.channels), 1)

        self.app.hideSubWindow("Select receiving channels")


    def CreateChooseRecipientSubWindow(self):
        self.app.startSubWindow("Choose recipient")

        self.app.startScrollPane("RecipientPane")
        self.app.startFrame("RecipientFrame", 0, 0)
        for i in range(len(self.receivingChannels)):
            self.app.addNamedCheckBox(self.receivingChannels[i], self.receivingChannels[i] + "_recipient", i, 1)

        self.app.stopFrame()
        self.app.stopScrollPane()

        self.app.startFrame("RecipientButtons", 1, 1)
        self.app.addNamedButton("Submit", "RecipientSubmit", self.OnSubmitChooseRecipient, len(self.receivingChannels), 0)
        self.app.addNamedButton("Cancel", "RecipientCancel", self.OnCancelChooseRecipient, len(self.receivingChannels), 1)


        self.app.hideSubWindow("Choose recipient")

    def CreateRecordSubWindow(self):
        self.app.startSubWindow("Record Message")

        self.app.addButton("Start recording", None)
        self.app.addButton("Stop recording", None)
        self.app.addButton("Send message", None)

        self.app.hideSubWindow("Record Message")

    def OnWake(self):
        self.app.hideSubWindow("Standby")
        self.app.showSubWindow("Main menu")

        return None

    def OnToggleReceivingChannel(self):
        self.app.hideSubWindow("Main menu")
        self.app.showSubWindow("Select receiving channels")


    def OnChooseMode(self):

        print(self.app.getRadioButton("mode"))

        return None

    def OnListen(self):
        return None

    def OnChooseRecipient(self):
        self.CreateChooseRecipientSubWindow()
        self.app.showSubWindow("Choose recipient")
        self.app.hideSubWindow("Main menu")

    # On record voice message
    def OnRecord(self):
        return None
    
    # On send reorded message
    def onSend(self):
        return None

    # Subscribing channels
    def OnSubmitChooseChannel(self):
        
        for i in range(len(self.channels)):
            if(self.app.getCheckBox(self.channels[i])):
                self.receivingChannels.append(self.channels[i])

        print(self.receivingChannels)

        self.app.hideSubWindow("Select receiving channels")
        self.app.showSubWindow("Main menu")

        return None
    
    def OnCancelChooseChannel(self):
        self.app.clearAllCheckBoxes()


        self.app.hideSubWindow("Select receiving channels")
        self.app.showSubWindow("Main menu")
        return None

    # Sending channels
    def OnSubmitChooseRecipient(self):
        for i in range(len(self.receivingChannels)):
            if(self.app.getCheckBox(self.receivingChannels[i])):
                self.recipientChannels.append(self.receivingChannels[i])

        print(self.recipientChannels)

        self.app.hideSubWindow("Select receiving channels")
        self.app.showSubWindow("Record Message")

        self.app.destroySubWindow("Choose recipient")

        return None
    
    def OnCancelChooseRecipient(self):
        self.app.clearAllCheckBoxes()


        self.app.hideSubWindow("Choose recipient")
        self.app.showSubWindow("Main menu")

        self.app.destroySubWindow("Choose recipient")

        return None

    def create_gui(self):
        self.app = gui()

        self.CreateStandbySubWindow()
        self.CreateCommandSubWindow()
        self.CreateChannelSubWindow()
        self.CreateRecordSubWindow()

        self.app.go(startWindow="Standby")

test = UI_Component()

