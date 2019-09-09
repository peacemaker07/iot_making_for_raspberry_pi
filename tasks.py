import paho.mqtt.client as mqtt
import time
import json
from celery import Celery
from celery.exceptions import SoftTimeLimitExceeded
from utils.helper import RedisClient
from aws_iot.shadow_client import ShadowClient

app = Celery('tasks',
             backend='redis://localhost:6379/0',
             broker='redis://localhost:6379/0')


@app.task
def run_shadow_by_aws_iot(client_id, host,
                          root_ca_path, private_key_path, certificate_path,
                          update_payload=None):

    redis_client = RedisClient()

    def custom_shadow_callback_update(payload, responseStatus, token):

        if responseStatus == "timeout":
            print("Update request " + token + " time out!")
        if responseStatus == "accepted":
            payload_dict = json.loads(payload)
            print("property: " + str(payload_dict["state"]))
        if responseStatus == "rejected":
            print("Update request " + token + " rejected!")

    def custom_shadow_callback_get(payload, response_status, token):
        payload_dict = json.loads(payload)
        print(payload_dict)
        redis_client.set('shadow_get_by_aws_iot', payload.encode())

    # Init AWSIoTMQTTShadowClient
    shadow_client = ShadowClient(client_id, host, root_ca_path, private_key_path, certificate_path)
    try:

        # Connect to AWS IoT
        shadow_client.connect()

        # Create a deviceShadow with persistent subscription
        shadow_client.create_shadow_handler_with_name(client_id)

        if update_payload:
            # shadow update
            shadow_client.shadow_update(update_payload, custom_shadow_callback_update)
        else:
            # shadow get
            shadow_client.shadow_get(custom_shadow_callback_get)

        # 待ち受け状態にする
        wait_time = 0
        while True:
            if wait_time > 15:
                break
            time.sleep(1)
            wait_time += 1
        time.sleep(2)
    except SoftTimeLimitExceeded:
        pass

    shadow_client.disconnect()
    return ''


@app.task
def run_subscribe_by_mqtt(host, port, topic):

    redis_client = RedisClient()

    def on_connect(client, userdata, flags, respons_code):
        print('status {0}'.format(respons_code))

        client.subscribe(topic)

    def on_message(client, userdata, msg):
        print(msg.topic + ' ' + str(msg.payload))
        try:
            json_str = msg.payload.decode(encoding='utf-8')
        except:
            json_str = ''

        redis_client.set('token', json_str)

        client.disconnect()

    try:
        redis_client.delete('token')

        client = mqtt.Client(protocol=mqtt.MQTTv311)

        client.on_connect = on_connect
        client.on_message = on_message

        client.connect(host, port=port, keepalive=60)

        # 待ち受け状態にする
        client.loop_forever()
    except SoftTimeLimitExceeded:
        return ''
