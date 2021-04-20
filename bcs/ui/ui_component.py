from appJar import gui

class UI_Component:
    def __init__(self):
        self.channels = []

        for i in range(50):
            self.channels.append("Test" + str(i))

        self.selectedChannels = []
        self.recipientChannels = []

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
        self.app.addButton('Toggle channel', self.OnToggleChannel)
        self.app.addButton('Listen', self.OnListen)
        self.app.addButton('Record message', self.OnSend)
        self.app.stopLabelFrame()

        self.app.hideSubWindow("Main menu")


    def CreateChannelSubWindow(self):
        self.app.startSubWindow("Select channels")
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

        self.app.hideSubWindow("Select channels")


    def CreateChooseRecipientSubWindow(self):
        self.app.startSubWindow("Choose recipient")

        self.app.startScrollPane("RecipientPane")
        self.app.startFrame("RecipientFrame", 0, 0)
        for i in range(len(self.selectedChannels)):
            self.app.addCheckBox(self.selectedChannels[i], i, 1)
        
        self.app.stopFrame()
        self.app.stopScrollPane()

        self.app.startFrame("RecipientButtons", 1, 1)
        self.app.addNamedButton("Submit", "RecipientSubmit", self.OnSubmitChooseRecipient, len(self.selectedChannels), 0)
        self.app.addNamedButton("Cancel", "RecipientCancel", self.OnCancelChooseRecipient, len(self.selectedChannels), 0)


        self.app.hideSubWindow("Choose recipient")

    def CreateRecordSubWindow(self):
        self.app.startSubWindow("Record Message")

        self.app.addButton("HEI", None)

        self.app.hideSubWindow("Record Message")



    def OnWake(self):
        self.app.hideSubWindow("Standby")
        self.app.showSubWindow("Main menu")

        return None

    def OnToggleChannel(self):
        self.app.hideSubWindow("Main menu")
        self.app.showSubWindow("Select channels")


    def OnChooseMode(self):

        print(self.app.getRadioButton("mode"))

        return None

    def OnListen(self):
        return None

    def OnSend(self):
        self.app.showSubWindow("Choose recipient")
        self.app.hideSubWindow("Main menu")

    def OnSubmitChooseChannel(self):
        
        for i in range(len(self.channels)):
            if(self.app.getCheckBox(self.channels[i])):
                self.selectedChannels.append(self.channels[i])

        print(self.selectedChannels)

        self.app.hideSubWindow("Select channels")
        self.app.showSubWindow("Main menu")

        return None
    
    def OnCancelChooseChannel(self):
        self.app.clearAllCheckBoxes()


        self.app.hideSubWindow("Select channels")
        self.app.showSubWindow("Main menu")
        return None

    def OnSubmitChooseRecipient(self):
        


        for i in range(len(self.selectedChannels)):
            if(self.app.getCheckBox(self.selectedChannels[i])):
                self.selectedChannels.append(self.selectedChannels[i])

        print(self.selectedChannels)

        self.app.hideSubWindow("Select channels")
        self.app.showSubWindow("Record Message")

        return None
    
    def OnCancelChooseRecipient(self):
        self.app.clearAllCheckBoxes()


        self.app.hideSubWindow("Choose recipient")
        self.app.showSubWindow("Main menu")
        return None

    def create_gui(self):
        self.app = gui()

        self.CreateStandbySubWindow()
        self.CreateCommandSubWindow()
        self.CreateChannelSubWindow()
        self.CreateRecordSubWindow()
        self.CreateChooseRecipientSubWindow()

        self.app.go(startWindow="Standby")

