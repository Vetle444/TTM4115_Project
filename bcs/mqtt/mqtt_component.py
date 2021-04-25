import os
from threading import Thread
from .message_component import Message
import paho.mqtt.client as mqtt
import json


class MQTT_Client:
    """
    Class to handle mqtt connections, wraps mqtt.client

    Functions:
    send_channel_list: - simulates server component sending channel list
                         (sends comma separated string of channel names)
    on_message:        - handles incoming messages depending on source channel:
                          - messages on channel_list are split and saved as channel_list
                          - messages on other channels are saved as message object
    subscribe:         - subscribes to specified mqtt topic
    send_message:      - publishes string as mqtt message on specified topic
    send_file:         - publishes audiofile as bytes as mqtt message on specified topic
    start:             - starts connection to specified mqtt broker and starts second thread
                         to check for incoming messages, also subscribes to topics channel_list and user_name
    """

    def __init__(self, user_name, ui_stm):
        self.count = 0
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.user_name = user_name
        self.prefix = "/group17/"
        self.message_count = 0
        self.ui_stm = ui_stm
        self.channel_list = []
        self.message_storage = "./messages/"
        if not os.path.exists(os.path.dirname(self.message_storage)):
            try:
                os.makedirs(os.path.dirname(self.message_storage))
            except OSError as exc:  # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise

    def send_channel_list(self):
        # sending hard coded channel list to simulate server component
        payload = "Test,Erlend,Group 1,Group 2"
        try:
            self.client.publish(self.prefix + "channel_list", payload)
        except Exception as e:
            print(e)

    def on_connect(self, client, userdata, flags, rc):
        print("on_connect(): {}".format(mqtt.connack_string(rc)))
        #self.client.subscribe(self.prefix + self.user_name)
        #self.client.subscribe(self.prefix + "channel_list")

    def on_message(self, client, userdata, msg):
        #check if channel is channel_list channel
        print("on_message(): topic: {}".format(msg.topic))
        topic = msg.topic.split("/")[-1]
        if topic == "channel_list":
            self.channel_list = str(msg.payload).split(",")
        else:
            self.message_count += 1

            # Adding ".wav" for all messages# not from "channel_list"
            file_extension = ".wav"# if topic != "channel_list" else ""
            file_object = open(self.message_storage + topic +
                               str(self.message_count) + file_extension, "wb")
            file_object.write(msg.payload)
            file_object.close()
            message = Message(topic, self.message_count,
                              self.message_storage + topic + str(self.message_count) + file_extension)
            # self.ui_stm.new_msg_queue_add(message)

    def subscribe(self, channel_name):
        self.client.subscribe(self.prefix + channel_name)

    def send_message(self, channel_name, file):
        try:
            self.client.publish(self.prefix + channel_name, payload)
        except Exception as e:
            print(e)

    def send_file(self, channel_name, file_location):
        f = open(file_location, "rb")
        audiostring = f.read()
        f.close()
        byteArray = bytearray(audiostring)

        try:
            self.client.publish(self.prefix + channel_name, byteArray)
        except Exception as e:
            print(e)

    def start(self, broker, port):
        print("Connecting to {}:{}".format(broker, port))
        self.client.connect(broker, port)

        self.client.subscribe(self.prefix + self.user_name)
        self.client.subscribe(self.prefix + "channel_list")

        try:
            # line below should not have the () after the function!
            thread = Thread(target=self.client.loop_forever)
            thread.start()
        except KeyboardInterrupt:
            print("Interrupted")
            self.client.disconnect()
