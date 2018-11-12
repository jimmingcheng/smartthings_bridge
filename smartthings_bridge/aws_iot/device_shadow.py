from smartthings_bridge.aws_iot.mqtt import publish


TOPIC_TEMPLATE_FOR_UPDATE = '$aws/things/{}/shadow/update'


def update_shadow(thing_name, data):
    topic = TOPIC_TEMPLATE_FOR_UPDATE.format(thing_name)

    publish(
        topic,
        {'state': {'reported': data}}
    )
