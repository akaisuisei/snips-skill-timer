#!/usr/bin/env python2
# -*-: coding utf-8 -*-

from concierge_python.concierge import Concierge
from concierge_python.extract import Extract
from hermes_python.hermes import Hermes
from timer import Timer

MQTT_IP_ADDR = "localhost"
MQTT_PORT = 1883
MQTT_ADDR = "{}:{}".format(MQTT_IP_ADDR, str(MQTT_PORT))

lang = "EN"

def set_timer(hermes, intent_message):
    current_session_id = intent_message.session_id
    siteId = intent_message.site_id
    tag = Extract.values(intent_message.slots.timer_name)
    duration = Extract.duration(intent_message.slots.timer_duration)
    room = Extract.value(intent_message.slots.timer_room, None)
    hermes.timer.add(tag, duration, siteId, room)

def stopTimer(hermes, intent_message):
    current_session_id = intent_message.session_id
    tag = Extract.values(intent_message.slots.tag)
    hermes.timer.remove(tag)

if __name__ == "__main__":
    lang = Concierge.getLang()
    c = Concierge(MQTT_IP_ADDR)
    t = Timer(c)
    with Hermes(MQTT_ADDR) as h:
        h.timer = t
        h.subscribe_intent("snips-labs:SetTimer_" + lang, set_timer) \
        .subscribe_intent("snips-labs:StopTimer_" + lang, stopTimer) \
        .loop_forever()
