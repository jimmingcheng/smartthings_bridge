import boto3
import json
import time

from botocore.vendored import requests


SUPPORTED_CAPABILITIES = (
    'alarm',
    'accelerationSensor',
    'contactSensor',
    'doorControl',
    'energyMeter',
    'lock',
    'motionSensor',
    'powerMeter',
    'switch',
    'temperatureMeasurement',
)


def smartapp(event, context, device_event_handler=None):
    lifecycle = event['lifecycle']

    if lifecycle == 'PING':
        return _ping(event)
    elif lifecycle == 'CONFIGURATION':
        phase = event['configurationData']['phase']
        if phase == 'INITIALIZE':
            return _config_init(event)
        elif phase == 'PAGE':
            return _config_page(event)
    elif lifecycle == 'INSTALL':
        return _install(event, context)
    elif lifecycle == 'UPDATE':
        return _update(event, context)
    elif lifecycle == 'EVENT':
        return _event(event, device_event_handler)


def _ping(data):
    return {
        'pingData': data['pingData'],
    }


def _config_init(data):
    return {
        'configurationData': {
            'initialize': {
                'name': 'Permissions',
                'description': 'Permissions',
                'id': 'main',
                'permissions': [
                    'l:devices',
                    'r:devices:*',
                    'r:installedapps',
                    'r:installedapps:*',
                    'w:installedapps:*',
                ],
                'firstPageId': '1'
            }
        }
    }


def _config_page(data):
    sections = [
        {
            'name': 'Switches',
            'settings': [{
                'id': 'switches',
                'name': 'Switches',
                'description': 'Tap to set',
                'type': 'DEVICE',
                'required': False,
                'multiple': True,
                'capabilities': ['switch'],
                'permissions': ['r', 'w', 'x'],
            }],
        },
        {
            'name': 'Motion Sensors',
            'settings': [{
                'id': 'motion',
                'name': 'Motion Sensors',
                'description': 'Tap to set',
                'type': 'DEVICE',
                'required': False,
                'multiple': True,
                'capabilities': ['motionSensor'],
                'permissions': ['r', 'w', 'x'],
            }],
        },
        {
            'name': 'Doors',
            'settings': [{
                'id': 'doors',
                'name': 'Doors',
                'description': 'Tap to set',
                'type': 'DEVICE',
                'required': False,
                'multiple': True,
                'capabilities': ['contactSensor'],
                'permissions': ['r', 'w', 'x'],
            }],
        },
        {
            'name': 'Locks',
            'settings': [{
                'id': 'locks',
                'name': 'Locks',
                'description': 'Tap to set',
                'type': 'DEVICE',
                'required': False,
                'multiple': True,
                'capabilities': ['lock'],
                'permissions': ['r', 'w', 'x'],
            }],
        },
        {
            'name': 'Energy Meters',
            'settings': [{
                'id': 'energy_meters',
                'name': 'Energy Meters',
                'description': 'Tap to set',
                'type': 'DEVICE',
                'required': False,
                'multiple': True,
                'capabilities': ['energyMeter', 'powerMeter'],
                'permissions': ['r', 'w', 'x'],
            }],
        },
        {
            'name': 'Alarms',
            'settings': [{
                'id': 'alarms',
                'name': 'Alarms',
                'description': 'Tap to set',
                'type': 'DEVICE',
                'required': False,
                'multiple': True,
                'capabilities': ['alarm'],
                'permissions': ['r', 'w', 'x'],
            }],
        },
    ]

    sections = []

    return {
        'configurationData': {
            'page': {
                'pageId': '1',
                'name': 'Permissions',
                'nextPageId': None,
                'previousPageId': None,
                'complete': True,
                'sections': sections,
            }
        }
    }


def _install(data, context):
    _install_or_update(data['installData'], context)
    return {'installData': {}}


def _update(data, context):
    _install_or_update(data['updateData'], context)
    return {'updateData': {}}


def _install_or_update(data, context):
    location_id = data['installedApp']['locationId']
    app_id = data['installedApp']['installedAppId']
    auth_token = data['authToken']

    _unsubscribe_all(app_id, auth_token)

    _subscribe(app_id, auth_token, location_id, 'alarm', 'alarm')
    _subscribe(app_id, auth_token, location_id, 'accelerationSensor', 'acceleration')
    _subscribe(app_id, auth_token, location_id, 'contactSensor', 'contact')
    _subscribe(app_id, auth_token, location_id, 'doorControl', 'door')
    _subscribe(app_id, auth_token, location_id, 'energyMeter', 'energy')
    _subscribe(app_id, auth_token, location_id, 'lock', 'lock')
    _subscribe(app_id, auth_token, location_id, 'motionSensor', 'motion')
    _subscribe(app_id, auth_token, location_id, 'powerMeter', 'power')
    _subscribe(app_id, auth_token, location_id, 'switch', 'switch')
    _subscribe(app_id, auth_token, location_id, 'temperatureMeasurement', 'temperature')

    client = boto3.client('lambda')
    for capability in SUPPORTED_CAPABILITIES:
        client.invoke_async(
            FunctionName=context.function_name,
            InvokeArgs=json.dumps({
                'method': 'register_things_for_capability',
                'auth_token': auth_token,
                'capability': capability,
            }),
        )


def _event(data, device_event_handler=None):
    for event in data['eventData']['events']:
        if event.get('eventType') == 'DEVICE_EVENT':
            device_event = event['deviceEvent']

            if device_event_handler:
                device_event_handler(
                    device_event['deviceId'],
                    device_event['capability'],
                    device_event['attribute'],
                    device_event['value'],
                    int(time.time()),
                )

    return {'eventData': {}}


def _subscribe(app_id, auth_token, location_id, capability, attribute):
    requests.post(
        'https://api.smartthings.com/v1/installedapps/{}/subscriptions'.format(app_id),
        headers={
            'Authorization': 'Bearer ' + auth_token,
            'Content-type': 'application/json',
        },
        data=json.dumps({
            'sourceType': 'CAPABILITY',
            'capability': {
                'locationId': location_id,
                'capability': capability,
                'subscriptionName': attribute,
            },
        }),
    )


def _unsubscribe_all(app_id, auth_token):
    requests.delete(
        'https://api.smartthings.com/v1/installedapps/{}/subscriptions'.format(app_id),
        headers={
            'Authorization': 'Bearer ' + auth_token,
        },
    )


def _get_device(device_id, auth_token):
    return requests.get(
        'https://api.smartthings.com/v1/devices/{}'.format(device_id),
        headers={
            'Authorization': 'Bearer ' + auth_token,
            'Content-type': 'application/json',
        },
    ).json()
