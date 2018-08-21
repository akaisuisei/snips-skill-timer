import os
import re
import time
import threading
import concierge_python.utils as utils

DIR = os.path.dirname(os.path.realpath(__file__)) + '/alarm/'

class Timer:
    _id = 'snips-skill-timer'

    def __init__(self, concierge):
        self.timer = {}
        self.concierge = concierge
        self.concierge.subscribePing(self.on_ping)
        self.concierge.subscribeView(Timer._id, self.on_view)
        self._alive = 0

    def getView(self):
        items  = []
        for timers in self.timer.itervalues():
            print(timers)
            for timer in timers.itervalues():
                if (timer):
                    items.append(timer.getView())
        return items

    def call(self, siteId, tag):
        client = self.concierge._client
        utils.play_wave(client, siteId, siteId, DIR + "timer.wav")
        self.remove(tag)

    def _find_new_tag(self, tag):
        print(self.timer)
        print(tag)
        if tag not in self.timer or self.timer[tag] is None:
            return tag
        else:
            for x in range(0, 9):
                n_tag = tag + "({})".format(x)
                if n_tag not in self.timer[tag]:
                    return n_tag
        return "timer"

    def _add(self, tag_group, duration, siteId):
        tag_group = tag_group[0] if len(tag_group) else ""
        if (tag_group == ""):
            tag_group = "timer"
        tag = self._find_new_tag(tag_group)
        print("set timer:"+ tag)
        if tag_group not in self.timer or self.timer[tag_group] is None:
            self.timer[tag_group] = {}
        self.timer[tag_group][tag] = Data(tag, duration, siteId, self.call)
        self._alive += 1
        self.concierge.publishTimer(duration, siteId)
        print(self.timer)

    def add(self, tag_group, duration, siteId, room = None):
        site_ids = None
        if room is not None:
            site_ids = self.concierge.getIdFromRoom(room)
        if site_ids is None or not len(site_ids):
            site_ids = [siteId]
        for tmp in site_ids:
            self._add(tag_group, duration, tmp)

    def _find_timer_group(self, tag):
        tag_group = re.search(r'(.*)\(.*\)$',tag)
        tag_group = tag_group.group(1) if tag_group else tag
        if tag_group in self.timer and tag in self.timer[tag_group]:
            return  tag_group
        return None

    def remove(self, tag):
        if isinstance(tag, list):
            tag = tag[0] if len(tag) else ""
        print("remove timer stop:"+ tag)
        if tag == "":
            for timers in self.timer.itervalues():
                print(timers)
                for timer in timers.itervalues():
                    if (timer):
                        timer.cancel()
        else:
            tag_group = self._find_timer_group(tag)
            if (tag_group):
                self._alive -= 1
                t = self.timer[tag_group].get(tag, None)
                if (t):
                    t.cancel()
                self.concierge.publishStopLed()
                print(self.timer)
                print(self._alive)

    def on_ping(self):
        if self._alive <= 0:
            return
        self.concierge.publishPong(Timer._id)

    def on_view(self):
        self.concierge.publishView(Timer._id, self.getView())

class Data:
    def __init__(self, tag, duration, siteId, func):
        self.tag = tag
        self.due_time = time.time() + duration
        self.duration = duration
        self.siteId = siteId
        self.cancelled = False
        self.t = threading.Timer(duration, func, [siteId, tag])
        self.t.start()

    def cancel(self):
        self.t.cancel()
        self.cancelled = True

    def getView(self):
        return {
                'type': 'toggle',
                'title':self.duration,
                'subtitle': self.siteId,
                'value': not self.cancelled,
                'onValueChangeToOn': {
                    "intent": "snips-labs:setAlarm_EN",
                    "slots": [ { "timer_name": self.tag } ]
                },
                'onValueChangeToOff': {
                    "intent": "snips-labs:StopTimer_EN",
                    "slots": [ { "timer_name": self.tag } ]
                }
            }
