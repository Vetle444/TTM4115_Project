#from ui.ui_component import *
from mqtt.mqtt_component import *
from audio.record_component import *
from state_machine.state_machine_component import *
from audio.record_component import *
from audio.playback_component import *

# Create a ui_component object
#ui = UI_Component()

mqtt_client = MQTT_Client("erlend", "bla")
broker, port = "mqtt.item.ntnu.no", 1883

mqtt_client.start(broker, port)
recorder = Recorder(mqtt_client)
player = Player()

ui = None # missing
stm = StateMachine_Component(ui, mqtt_client, player, recorder)

