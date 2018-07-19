import os
import threading
import re

DIR = os.path.dirname(os.path.realpath(__file__)) + '/alarm/'

class Timer:
    _id = 'snips-skill-timer'
    _alive = 0

    def __init__(self):
        self.timer = {}

    def getView(self):
        items  = []
        for timers in self.timer.itervalues():
            for timer in timers:
                items.append(timer.getView())
        return items

    @staticmethod
    def call(siteId):
        siteId = siteId
        utils.play_wave(Concierge._client, siteId, siteId, DIR + "timer.wav")
        Timer._alive -= 1;
        if (Timer._alive <= 0):
            Concierge.unsubscribe(liveTopicPing)

    def _find_new_tag(self, tag):
        if tag not in self.timer or self.timer[tag] is None:
            return tag
        else:
            for x in range(0, 9):
                n_tag = tag + "({})".format(x)
                if n_tag not in self.timer[tag].keys:
                    return n_tag
        return ""

    def set(self, tag_group, duration, siteId):
        tag_group = tag_group[0] if len(tag) else ""
        print("set timer:"+ tag_group)
        tag = self._find_new_tag(tag_group)
        if tag_group not in self.timer or self.timer[tag_group] is None:
            self.timer[tag_group] = {}
        self.timer[tag_group][tag] = Timer.Data(tag, duration)
        Timer._alive += 1
        Concierge.subscribe(liveTopicPing)
        Concierge.publishTimer(duration)

    def _find_timer_group(self, tag):
        tag_group = re.search(r'(.*)\(.*\)$',tag)
        tag_group = tmp.group(1) if tmp else tag
        elt = None
        if tag_group in self.timer:
            for tmp in self.timer[tag_group]:
                if (tmp.tag == tag):
                    elt = tag_group
                    break
        return elt

    def remove(self, tag):
        tag = tag[0] if len(tag) else ""
        print("remove timer stop:"+ tag)
        t = self._find_timer_group(tag)
        if (t):
            Timer._alive -= 1
            t = self.timer[tag_group].pop(tag, None)
            if (t):
                t.cancel()
            if (Timer._alive <= 0):
                client.unsubscribe(liveTopicPing)
            Concierge.publishStopLed()

class Data:
    def __init__(self, tag, duration, siteId):
        self.tag = tag
        self.due_time = time.time() + duration
        self.duration = duration
        self.siteId = siteId
        self.t = threading.Timer(duration, Timer.call, [siteId])
        self.t.start()

    def cancel(self):
        self.t.cancel()

    def getView(data):
        return {
                'type': 'toggle',
                'title':self.duration,
                'subtitle': self.siteId,
                'value': True,
                'onValueChangeToOn': {
                    "intent": "snips-labs:setAlarm_EN",
                    "slots": [ { "timer_name": self.tag } ]
                },
                'onValueChangeToOff': {
                    "intent": "snips-labs:StopTimer_EN",
                    "slots": [ { "timer_name": self.tag } ]
                }
            }
