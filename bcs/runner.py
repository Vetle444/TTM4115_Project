from ui.ui_component import *
from mqtt.mqtt_component import *

# Create a ui_component object
#ui = UI_Component()

mqtt_client = MQTT_Client("erlend", "bla")
broker, port = "mqtt.item.ntnu.no", 1883

mqtt_client.start(broker, port)

mqtt_client.send_file("erlend", "C:/Users/erlen/PycharmProjects/TTM4115_Project/audio/audio.wav")
