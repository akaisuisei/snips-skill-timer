#!/usr/bin/env python2
# -*-: coding utf-8 -*-

from hermes_python.hermes import Hermes
import calendar
import os
import time
import playsound
import threading
import vlc
from crontab import CronTab
from datetime import datetime
CONFIGURATION_ENCODING_FORMAT = "utf-8"
CONFIG_INI = "config.ini"

MQTT_IP_ADDR = "localhost"
MQTT_PORT = 1883
MQTT_ADDR = "{}:{}".format(MQTT_IP_ADDR, str(MQTT_PORT))

DIR = os.path.dirname(os.path.realpath(__file__)) + '/alarm/'
def call_timer():
    p = vlc.MediaPlayer("file://" + DIR + 'timer.wav')
    p.play()
    return

class Skill:

    def __init__(self):
        self.cron = CronTab(user=True)
        self.timer = {}
        return
    

    def set_timer(self, tag, duration):
        if(len(tag)):
            tag= tag[0]
        else:
            tag = ""
        t = threading.Timer(duration, call_timer)
        t.start()
        if tag not in self.timer or self.timer[tag] is None:
            self.timer[tag] = [t]
        else:
            self.timer[tag] += [t]
        return 

    def set_alarm(self, every, time, day):
        job = self.cron.new(command='play ' + DIR + "alarm.wav", comment="alarm")  
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
        if(len(tag)):
            tag= tag[0]
        else:
            tag = ""
        print("alarm stop:"+ tag)
        self.cron.remove_all(comment=tag)  
        self.cron.write()
        if tag in self.timer:
            del self.timer[tag]

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
            print(type(duration))
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
            print(room.slot_value.value_type)
            if room.slot_value.value_type == "" :
                tag.append(room.slot_value.value.value)
    if len (tag):
        tmp = tag[0][:-7] 
        return datetime.strptime(tmp, '%Y-%m-%d %H:%M:%S')
    return None

def setAlarm(hermes, intent_message):
    every = extract_every(intent_message)
    day = extract_day(intent_message)
    time = extract_time(intent_message)
    hermes.skill.set_alarm(every, time, day) 

def set_timer(hermes, intent_message):
    current_session_id = intent_message.session_id
    hermes.skill.set_timer(extract_tag(intent_message),extract_duration(intent_message)) 

def stopTimer(hermes, intent_message):
    current_session_id = intent_message.session_id
    hermes.skill.remove_alarm(extract_tag(intent_message)) 

if __name__ == "__main__":
    skill = Skill()
    
    with Hermes(MQTT_ADDR) as h: 
        h.skill = Skill()
        h.subscribe_intent("akaisuisei:setAlarm", setAlarm) \
        .subscribe_intent("akaisuisei:SetTimer", set_timer) \
        .subscribe_intent("akaisuisei:StopTimer", stopTimer) \
         .loop_forever()
