class Extract:

    @staticmethod
    def _getFirst(slots, default, func):
        tmp = func(slots)
        if len (tmp):
            return tmp[0]
        return default

    @staticmethod
    def durations(slots):
        tag = []
        if slots is not None:
            for tmp in slots:
                duration = tmp.slot_value.value
                duration = duration.hours * 3600 + duration.minutes * 60 + duration.seconds
                tag += [duration]
        return tag

    @staticmethod
    def duration(slots, default = ""):
        return Extract._getFirst(slots, default, Extract.durations)

    @staticmethod
    def values(slots):
        tag = []
        if slots is not None:
            for tmp in slots:
                tag.append(tmp.slot_value.value.value)
        return tag

    @staticmethod
    def value(slots, default = ''):
        return Extract._getFirst(slots, default, Extract.values)

    @staticmethod
    def timeSlots(slots):
        tag = []
        if slots is not None:
            for slot in slots:
                value = slot.slot_value.value
                if type(value) == hermes_python.ontology.TimeIntervalValue :
                    t0 = value.from_date[:-7]
                    t0 = datetime.strptime(t0, '%Y-%m-%d %H:%M:%S')
                    t1 = value.to_date[:-7]
                    t1 = datetime.strptime(t1, '%Y-%m-%d %H:%M:%S')
                    delta = t1 - t0
                    tmp = t0 + delta / 2
                    tag.append(tmp)
                if type(value) == hermes_python.ontology.InstantTimeValue :
                    tmp = value.value[0][:-7]
                    tmp = datetime.strptime(tmp, '%Y-%m-%d %H:%M:%S')
                    tag.append(tmp)
        return tag

    @staticmethod
    def timeSlot(slots, default = None):
        return Extract._getFirst(slots, default, Extract.timeSlot)
