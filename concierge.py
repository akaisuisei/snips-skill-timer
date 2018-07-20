import requests
import paho.mqtt.client as mqtt

class Topic():

    live = 'concierge/apps/live'
    view = 'concierge/apps/{}/view'
    livePing = '{}/ping'.format(live)
    livePong = '{}/pong'
    viewPing = '{}/ping'.format(view)
    viewPong = '{}/pong'.format(view)
    timerLed = 'concierge/feedback/led/default/timer'
    timeLed = 'concierge/feedback/led/default/timer'
    @staticmethod
    def getViewPong(appId):
        return Topic.viewPong.format(appId)

    @staticmethod
    def getViewPing(appId):
        return Topic.viewPing.format(appId)

class Concierge:
    def __init__(self, hostname):
        self._client = mqtt.Client()
        self._client.on_connect = self.on_connect
        self._client.on_message = self.on_message
        self._client.connect(hostname)
        self._client.loop_start()
        self.topics = []
        self.subscribe(Topic.livePing, self.on_ping)

    def subscribe(self, topic, func = None):
        self._client.subscribe(topic)
        self.topics += [topic]
        if (func):
            self._client.message_callback_add(topic, func)
    def subscribePing(self, func = None):
        if (func):
            self._client.message_callback_add(Topic.livePing, func)

    def unsubscribe(self, topic):
        self._client.unsubscribe(topic)

    def publish(self, topic, msg):
        self._client.publish(topic, msg)

    def publishTimer(self, duration):
        self.publish(Topic.timerLed, '{"duration":%s}' % duration)

    def publishPong(self, app):
        self.publish(Topic.livePong, app)
    def publishTime(self, value):
        self.publish(Topic.timeLed, '{"duration":%s}' % value)

    def publishStopLed(self):
        self.publish('concierge/feedback/led/default/stop', '')

    def on_connect(self, client, userdata, flags, rc):
        for t in self.topics:
            client.subscribe(t)

    def on_ping(self, client, userdata, msg):
        print(msg.payload)

    def on_message(self, client, userdata, msg):
        print(msg.topic)

    @staticmethod
    def getLang(default = "FR"):
        try:
            res = requests.get("http://localhost:3000/assistant/lang").json;
            return res.response
        except :
            return default

