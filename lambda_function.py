from smartthings_bridge import device_registry
from smartthings_bridge.smartthings.smartapp import smartapp
from smartthings_bridge.bridge import device_event_handler
from smartthings_bridge.bridge import register_things_for_capability


def lambda_handler(event, context):
    if 'lifecycle' in event:
        if event['lifecycle'] in ('INSTALL', 'UPDATE'):
            device_registry.clear_devices()
        return smartapp(event, context, device_event_handler=device_event_handler)
    elif 'method' in event and event['method'] == 'register_things_for_capability':
        return register_things_for_capability(event, context)
