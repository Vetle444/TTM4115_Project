#from ui.ui_component import *
import logging
import time
from mqtt.message_component import *
from ui.ui_component import UI_Component
from mqtt.mqtt_component import *
from audio.record_component import *
from state_machine.state_machine_component import *
from audio.record_component import *
import threading

driver = Driver()  # Driver for stm

debug_channels = {}
debug_msg_queue = []
for c in range(5):
    debug_channels["channel {}".format(c)] = []
    for m in range(5):
        msg = Message("channel {}".format(c), "c:{}_id:{}".format(c, m), "C:/Users/marti/PycharmProjects/TTM4115_Project/bcs/audio/recorded_message.wav")
        debug_msg_queue.append(msg) if m == c else None
        debug_channels["channel {}".format(c)].append(msg)

# Create components
ui = UI_Component()
mqtt_client = MQTT_Client("erlend")
broker, port = "mqtt.item.ntnu.no", 1883
recorder = Recorder(mqtt_client)
stm_component = StateMachine_Component()
print("runner: Objects created")

# Pass objects to other objects
stm_component.setDriver(driver)
stm_component.setMQTT(mqtt_client)
stm_component.setRecorder(recorder)
stm_component.setUI(ui)

#Example messages dictionary
stm_component.messages = debug_channels

#Example new messages list
#stm_components.new_msg_queue = debug_msg_queue

ui.stm_component = stm_component
recorder.setDriver(driver)
driver.add_machine(stm_component.stm)
driver.add_machine(recorder.record_stm)
mqtt_client.setStm(stm_component)

print("runner: Setup complete, starting system...")
# Start components
driver._logger.setLevel(logging.DEBUG)
mqtt_client.start(broker, port)
mqtt_client.create_channel_list()
#ui.start()
#x = threading.Thread(target=ui.start)
driver.start()
ui.start()
#x.start()
