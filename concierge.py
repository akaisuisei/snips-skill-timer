import paho.mqtt.client as mqtt

class Topic():

    live = 'concierge/apps/live'
    view = 'concierge/apps/{}/view'.format(appId)
    livePing = '{}/ping'.format(liveTopic)
    livePong = '{}/pong'
    viewPing = '{}/ping'.format(viewTopic)
    viewPong = '{}/pong'.format(viewTopic)
    timerLed = 'concierge/feedback/led/default/timer'
    @staticmethod
    def getViewPong(appId):
        return Topic.viewPong.format(appId)

    @staticmethod
    def getViewPing(appId):
        return Topic.viewPing.format(appId)


class Concierge:
    _client = None
    @staticmethod
    def init(hostname):
        Concierge._client = mqtt.Client()
        Concierge._client.on_connect = on_connect
        Concierge._client.on_message = on_message
        Concierge._client.connect(hostname)
        Concierge._client.loop_start()

    @staticmethod
    def unsubscribe(topic):
            Concierge._client.unsubscribe(topic)

    @staticmethod
    def subscribe(topic):
            Concierge._client.subscribe(topic)

    @staticmethod
    def getLang(default = "FR"):
        try:
            res = requests.get("http://localhost:3000/assistant/lang").json;
            return res.response
        except :
            return default

    def publish(topic, msg):
        Concierge._client.publish(topic, msg)

    def publishTimer(duration):
        Concierge.publish(Topic.timerSend, '{"duration":%s}' % duration)

    def pusblishStopLed():
        Concierge.publish('concierge/feedback/led/default/stop', '')

    @staticmethod
    def on_connect(client, userdata, flags, rc):
        # TODO: make it appear as always live for now
        if (alive > 0) or True:
            client.subscribe(liveTopicPing)
        client.subscribe(viewTopicPing)

    @staticmethod
    def on_message(client, userdata, msg):
        if msg.topic == liveTopicPing:
            client.publish(liveTopicPong, '{"result":"snips-skill-timer"}')
        elif msg.topic == viewTopicPing:
            client.publish(viewTopicPong, json.dumps({"result": generateView()}))
