import os

import json
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient


_client = None


def get_client():
    global _client
    if not _client:
        _client = AWSIoTMQTTClient(os.environ['AWS_MQTT_CLIENT_ID'])
        _client.configureEndpoint(os.environ['AWS_MQTT_HOST'], int(os.environ['AWS_MQTT_PORT']))

        _client.configureCredentials(
            os.environ['AWS_MQTT_ROOT_CERT'],
            os.environ['AWS_MQTT_PRIVATE_KEY'],
            os.environ['AWS_MQTT_CERT'],
        )
        _client.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
        _client.configureDrainingFrequency(2)  # Draining: 2 Hz
        _client.configureConnectDisconnectTimeout(10)  # 10 sec
        _client.configureMQTTOperationTimeout(5)  # 5 sec
    return _client


def publish(topic, data):
    client = get_client()
    client.connect()
    client.publish(
        topic,
        json.dumps(data),
        0,
    )
    client.disconnect()
