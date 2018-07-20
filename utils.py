
def getMqttPlayTopic(siteId, requestId):
    return "hermes/audioServer/{}/playBytes/{}".format(siteId,requestId);

def play_wave(client,siteId, requestId, filename):
    topic = getMqttPlayTopic(siteId, requestId)
    with open(filename, "rb") as f:
        imagestring = f.read()
        f.close()
    payload = bytearray(imagestring)
    client.publish(topic, payload)
