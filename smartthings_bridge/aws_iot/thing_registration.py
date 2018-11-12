import boto3
import json
import os


_client = None


def get_client():
    global _client
    if not _client:
        _client = boto3.client('iot', region_name=os.environ['AWS_IOT_REGION'])
    return _client


def provisioning_template():
    return {
        'Parameters': {
            'device_id': {
                'Type': 'String',
            },
            'device_name': {
                'Type': 'String',
            },
            'capability': {
                'Type': 'String',
            },
        },
        'Resources': {
            'thing': {
                'Type': 'AWS::IoT::Thing',
                'Properties': {
                    'ThingName': {'Ref': 'device_id'},
                    'AttributePayload': {
                        'device_name': {'Ref': 'device_name'},
                        'capability': {'Ref': 'capability'},
                    },
                },
                'OverrideSettings': {
                    'AttributePayload': 'MERGE',
                },
            },
            'certificate': {
                'Type': 'AWS::IoT::Certificate',
                'Properties': {
                    'CertificateId': os.environ['AWS_IOT_CERT_ID'],
                },
                'OverrideSettings': {
                    'Status': 'DO_NOTHING',
                },
            },
            'policy': {
                'Type': 'AWS::IoT::Policy',
                'Properties': {
                    'PolicyName': os.environ['AWS_IOT_POLICY'],
                },
            },
        },
    }


def register_thing(device_id, device_name, capability):
    get_client().register_thing(
        templateBody=json.dumps(provisioning_template()),
        parameters={
            'device_id': device_id,
            'device_name': device_name.replace(' ', '_'),
            'capability': capability,
        },
    )
