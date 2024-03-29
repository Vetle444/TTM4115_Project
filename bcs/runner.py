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

# Create components
ui = UI_Component()
mqtt_client = MQTT_Client("santhosh")
broker, port = "mqtt.item.ntnu.no", 1883
recorder = Recorder(mqtt_client)
stm_component = StateMachine_Component()
print("runner: Objects created")

# Pass objects to other objects
stm_component.setDriver(driver)
stm_component.setMQTT(mqtt_client)
stm_component.setRecorder(recorder)
stm_component.setUI(ui)

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
driver.start()
ui.start()
