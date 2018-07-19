#!/usr/bin/env python2
# -*-: coding utf-8 -*-

from hermes_python.hermes import Hermes
import hermes_python
from extract import Extract
from concierge import Concierge
from timer import Timer

MQTT_IP_ADDR = "localhost"
MQTT_PORT = 1883
MQTT_ADDR = "{}:{}".format(MQTT_IP_ADDR, str(MQTT_PORT))

lang = "EN"

def setAlarm(hermes, intent_message):
    every = Extract.value(intent_message.slots.recurence)
    day = Extract.value(intent_message.slots.weeday)
    time = Extract.timeSlot(intent_message.slots.time)
    siteId = intent_message.site_id
    hermes.skill.set_alarm(every, time, day, siteId)

def set_timer(hermes, intent_message):
    current_session_id = intent_message.session_id
    siteId = intent_message.site_id
    tag = Extract.values(intent_message.slots.timer_name)
    duration = Extract.duration(intent_message.slots.timer_duration)
    hermes.skill.set_timer(tag, duration,siteId)

def stopTimer(hermes, intent_message):
    current_session_id = intent_message.session_id
    hermes.skill.remove_alarm(extract_tag(intent_message))

if __name__ == "__main__":
    skill = Timer()
    lang = Concierge.getLang()
    Concierge.init(MQTT_IP_ADDR)
    with Hermes(MQTT_ADDR) as h:
        h.skill = skill
        h.subscribe_intent("snips-labs:setAlarm_" + lang, setAlarm) \
        .subscribe_intent("snips-labs:SetTimer_" + lang, set_timer) \
        .subscribe_intent("snips-labs:StopTimer_" + lang, stopTimer) \
        .loop_forever()
