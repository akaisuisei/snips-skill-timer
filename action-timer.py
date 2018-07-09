#!/usr/bin/env python2
# -*-: coding utf-8 -*-

from hermes_python.hermes import Hermes
import hermes_python
import calendar
import json
import os
import time
import threading
from crontab import CronTab
from datetime import datetime
import requests
import paho.mqtt.client as mqtt
CONFIGURATION_ENCODING_FORMAT = "utf-8"
CONFIG_INI = "config.ini"

MQTT_IP_ADDR = "localhost"
MQTT_PORT = 1883
MQTT_ADDR = "{}:{}".format(MQTT_IP_ADDR, str(MQTT_PORT))

DIR = os.path.dirname(os.path.realpath(__file__)) + '/alarm/'

appId = 'snips-skill-timer'
alive = 0;
lang = "EN"
client = None

liveTopic = 'concierge/apps/live'
liveTopicPing = '{}/ping'.format(liveTopic)
liveTopicPong = '{}/pong'.format(liveTopic)
viewTopic = 'concierge/apps/{}/view'.format(appId)
viewTopicPing = '{}/ping'.format(viewTopic)
viewTopicPong = '{}/pong'.format(viewTopic)
timerTopicSend = 'concierge/feedback/led/default/timer'

def getMqttPlayTopic(siteId, requestId):
    return "hermes/audioServer/{}/playBytes/{}".format(siteId,requestId);

def call_timer(siteId):
    global alive
    siteId = siteId
    topic = getMqttPlayTopic(siteId, siteId)
    print(topic)
    f = open(DIR + "timer.wav", "rb")
    imagestring = f.read()
    f.close()
    payload = bytearray(imagestring)
    client.publish(topic, payload)
    alive -= 1;
    if (alive <= 0):
        client.unsubscribe(liveTopicPing)
    return

class Skill:

    def __init__(self):
        self.cron = CronTab(user=True)
        self.timer = {}
        return

    def set_timer(self, tag, duration, siteId):
        global alive
        if(len(tag)):
            tag= tag[0]
        else:
            tag = ""
        t = threading.Timer(duration, call_timer, [siteId])
        t.start()
        if tag not in self.timer or self.timer[tag] is None:
            self.timer[tag] = [t]
        else:
            self.timer[tag] += [t]
        alive += 1
        client.subscribe(liveTopicPing)
        return  duration

    def set_alarm(self, every, time, day, siteId):
        topic = getMqttPlayTopic(siteId, siteId)
        command = "mosquitto_pub -t \"{}\" -f {}{}".format(topic, DIR, "alarm.wav")
        job = self.cron.new(command=command, comment="alarm")
        if time is not None:
            job.setall(time)
            dow = calendar.day_name[time.weekday()][:3].upper()
            job.dow.on(dow)
        if day != "":
            day = day[:3].upper()
            if(every == "every"):
                if day == 'WEE':
                    job.dow.during('MON', 'FRI')
                elif day != 'day' and day != 'DAY':
                    job.dow.on(day)
                else:
                    job.dow.during('MON', 'SUN')
        print(job)

        self.cron.write()
        return

    def remove_alarm(self, tag):
        global alive
        if(len(tag)):
            tag= tag[0]
        else:
            tag = ""
        print("alarm stop:"+ tag)
        self.cron.remove_all(comment=tag)
        self.cron.write()
        if tag in self.timer:
            alive -= 1
            if (alive <= 0):
                client.unsubscribe(liveTopicPing)
            for tmp in self.timer[tag]:
                tmp.cancel()
            del self.timer[tag]
            return True
        return False

def extract_tag(intent_message):
    tag = []
    if intent_message.slots.timer_name is not None:
        for room in intent_message.slots.timer_name:
            tag.append(room.slot_value.value.value)
    return tag

def extract_duration(intent_message):
    tag = []
    if intent_message.slots.timer_duration is not None:
        for room in intent_message.slots.timer_duration:
            duration = room.slot_value.value
            duration = duration.hours * 3600 + duration.minutes * 60 + duration.seconds
            print(duration)
            return duration
    return ""

def extract_day(intent_message):
    tag = []
    if intent_message.slots.weeday is not None:
        for room in intent_message.slots.weekday:
            tag.append(room.slot_value.value.value)
    if len (tag):
        return tag[0]
    return ''
def extract_every(intent_message):
    tag = []
    if intent_message.slots.recurrence is not None:
        for room in intent_message.slots.recurrence:
            tag.append(room.slot_value.value.value)
    if len (tag):
        return tag[0]
    return ''

def extract_time(intent_message):
    tag = []
    if intent_message.slots.time is not None:
        for room in intent_message.slots.time:
            if type(room.slot_value.value) == hermes_python.ontology.TimeIntervalValue :
                t0 = room.slot_value.value.from_date[:-7]
                t0 = datetime.strptime(t0, '%Y-%m-%d %H:%M:%S')
                t1 = room.slot_value.value.to_date[:-7]
                t1 = datetime.strptime(t1, '%Y-%m-%d %H:%M:%S')
                delta = t1 - t0
                tmp = t0 + delta / 2
                tag.append(tmp)
            if type(room.slot_value.value) == hermes_python.ontology.InstantTimeValue :
                tmp = room.slot_value.value.value[0][:-7]
                tmp = datetime.strptime(tmp, '%Y-%m-%d %H:%M:%S')
                tag.append(tmp)

    if len (tag):
        return tag[0]
    return None

def setAlarm(hermes, intent_message):
    every = extract_every(intent_message)
    day = extract_day(intent_message)
    time = extract_time(intent_message)
    siteId = intent_message.site_id
    hermes.skill.set_alarm(every, time, day, siteId)

def set_timer(hermes, intent_message):
    current_session_id = intent_message.session_id
    siteId = intent_message.site_id
    tmp = hermes.skill.set_timer(extract_tag(intent_message),extract_duration(intent_message),siteId)
    client.publish(timerTopicSend, '{"duration":%s}' % tmp)

def stopTimer(hermes, intent_message):
    current_session_id = intent_message.session_id
    able = hermes.skill.remove_alarm(extract_tag(intent_message))
    if (able):
        client.publish('concierge/feedback/led/default/stop', None)
def on_connect(client, userdata, flags, rc):
    # TEMP: make it appear as always live for now
    if (alive > 0) or True:
        client.subscribe(liveTopicPing)
    client.subscribe(viewTopicPing)

def on_message(client, userdata, msg):
    if msg.topic == liveTopicPing:
        client.publish(liveTopicPong, '{"result":"snips-skill-timer"}')
    elif msg.topic == viewTopicPing:
        client.publish(viewTopicPong, json.dumps({"result": generateView()}))

def generateView():
    alarms = [
        {'tag': 1, 'time': datetime.strptime('Jul 10 2018  6:30AM', '%b %d %Y %I:%M%p'), 'siteId': "bedroom"},
        {'tag': 2, 'time': datetime.strptime('Jul 10 2018  7:00AM', '%b %d %Y %I:%M%p'), 'siteId': "bedroom"},
        {'tag': 3, 'time': datetime.strptime('Jul 10 2018  8:00AM', '%b %d %Y %I:%M%p'), 'siteId': "living room"}
    ]
    items = []
    for alarm in alarms:
        viewItem = {
            'type': 'toggle',
            'title': alarm['time'].strftime("%H:%M"),
            'subtitle': alarm['siteId'].capitalize(),
            'value': True,
            'onValueChangeToOn': {
                "intent": "snips-labs:setAlarm_EN",
                "slots": [ { "timer_name": alarm['tag'] } ]
            },
            'onValueChangeToOff': {
                "intent": "snips-labs:StopTimer_EN",
                "slots": [ { "timer_name": alarm['tag'] } ]
            }
        }
        items.append(viewItem)
    return items

def getLang():
    try:
        res = requests.get("http://localhost:3000/assistant/lang").json;
        return res.response
    except :
        return "FR"

if __name__ == "__main__":
    skill = Skill()
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_IP_ADDR)
    client.loop_start()
    lang = getLang()

    with Hermes(MQTT_ADDR) as h:
        h.skill = skill
        h.subscribe_intent("snips-labs:setAlarm_" + lang, setAlarm) \
        .subscribe_intent("snips-labs:SetTimer_" + lang, set_timer) \
        .subscribe_intent("snips-labs:StopTimer_" + lang, stopTimer) \
        .loop_forever()
