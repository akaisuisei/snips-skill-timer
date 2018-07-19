
def getMqttPlayTopic(siteId, requestId):
    return "hermes/audioServer/{}/playBytes/{}".format(siteId,requestId);

def play_wave(client,siteId, requestID, fileName):
    topic = getMqttPlayTopic(siteId, siteId)
    with open(DIR + "timer.wav", "rb") as f:
        imagestring = f.read()
        f.close()
    payload = bytearray(imagestring)
    client.publish(topic, payload)
