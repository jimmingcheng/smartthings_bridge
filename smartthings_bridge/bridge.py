from botocore.vendored import requests

from smartthings_bridge.aws_iot.device_shadow import update_shadow
from smartthings_bridge.aws_iot.mqtt import publish
from smartthings_bridge.aws_iot.thing_registration import register_thing
from smartthings_bridge import device_registry


DEVICE_EVENT_TOPIC = 'house/device_event'


def register_things_for_capability(event, context):
    auth_token = event['auth_token']
    capability = event['capability']

    devices = requests.get(
        'https://api.smartthings.com/v1/devices?capability={}'.format(capability),
        headers={
            'Authorization': 'Bearer ' + auth_token,
            'Content-type': 'application/json',
        },
    ).json()['items']

    for device in devices:
        register_thing(
            device_id=device['deviceId'],
            device_name=device['label'],
            capability=capability,
        )

        device_registry.upsert_device(
            device_id=device['deviceId'],
            device_name=device['label'],
        )


def device_event_handler(device_id, capability, attribute, value, timestamp):
    update_shadow(
        device_id,
        {attribute: value}
    )

    publish(
        DEVICE_EVENT_TOPIC,
        {
            'device_id': device_id,
            'capability': capability,
            'attribute': attribute,
            'value': value,
            'timestamp': timestamp,
        },
    )
