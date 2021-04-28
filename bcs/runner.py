#from ui.ui_component import *
from mqtt.mqtt_component import *
from audio.record_component import *
from state_machine.state_machine_component import *
from audio.record_component import *
from audio.playback_component import *

driver = Driver()

# Create a ui_component object
#ui = UI_Component()
placeholder="placeholer"
mqtt_client = MQTT_Client("erlend", placeholder)
broker, port = "mqtt.item.ntnu.no", 1883

mqtt_client.start(broker, port, placeholder)
recorder = Recorder(mqtt_client, driver)

ui = None # missing
stm = StateMachine_Component(ui, mqtt_client, recorder)
driver.add_machine(stm.stm)
driver.add_machine(recorder.stm)
driver.start()
stm.setDriver(driver)
recorder.setDriver(driver)
mqtt_client.setStm(stm)
stm.setMQTT(mqtt_client)
stm.setRecorder(recorder)
stm.setUI(ui)



