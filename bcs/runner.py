#from ui.ui_component import *
from bcs.ui.ui_component import UI_Component
from mqtt.mqtt_component import *
from audio.record_component import *
from state_machine.state_machine_component import *
from audio.record_component import *


driver = Driver()  # Driver for stm


# Create components
ui = UI_Component()
mqtt_client = MQTT_Client("erlend")
broker, port = "mqtt.item.ntnu.no", 1883
recorder = Recorder(mqtt_client)
stm = StateMachine_Component()

print("runner: Objects created")

# Pass objects to other objects
stm.setDriver(driver)
stm.setMQTT(mqtt_client)
stm.setRecorder(recorder)
stm.setUI(ui)
ui.stm = stm
recorder.setDriver(driver)
driver.add_machine(stm.stm)
driver.add_machine(recorder.stm)
mqtt_client.setStm(stm)


print("runner: Setup complete, starting system...")
# Start components
driver.start()
mqtt_client.start(broker, port)
