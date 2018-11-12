import boto3


def get_device_table():
    return boto3.resource('dynamodb', region_name='us-west-1').Table('device')


def clear_devices():
    device_table = get_device_table()
    for item in device_table.scan()['Items']:
        device_table.delete_item(Key={'id': item['id']})


def upsert_device(device_id, device_name):
    device_table = get_device_table()

    device_table.put_item(Item={
        'id': device_id,
        'name': device_name,
    })
