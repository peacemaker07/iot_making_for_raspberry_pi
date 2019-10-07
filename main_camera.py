import time
from datetime import datetime
from subprocess import run

from utils.shadow import CameraShadowData
from utils.camera import Camera
from utils.comm_s3 import CommAwsS3
from utils.comm_mqtt import CommMqtt, CommMqttShadow
from utils.message import MsgTokenReq, MsgImages
from utils.comm_soracom import CommSoracom
from utils.helper import RedisClient
import tasks as tasks_mqtt

host = 'beam.soracom.io'
port = 1883


class SendImagesData:
    """
    カメラ画像送信データ
    """

    imsi = None  # imsi
    created = None  # 撮影日時
    cam_obj_key = None  # カメラオブジェクトキー
    image_path = None  # カメラ画像のファイルパス

    def __init__(self, imsi, camera_obj, cam_obj_key=None):

        self.imsi = imsi
        self.created = camera_obj.created
        self.cam_obj_key = cam_obj_key
        self.image_path = camera_obj.image_path


def main():

    # imsiを取得
    soracom = CommSoracom()
    imsi = soracom.get_imsi()

    # shadow get
    comm_mqtt_shadow = CommMqttShadow(host, port, imsi)
    json_str = comm_mqtt_shadow.shadow_get()
    camera_shadow = CameraShadowData(json_str)

    # shadow update
    if camera_shadow.delta_dict:
        update_payload = camera_shadow.get_payload_state_add_reported(camera_shadow.delta_dict)
        comm_mqtt_shadow.shadow_update(update_payload)

    redis_client = RedisClient()

    # カメラ撮影
    camera_obj = Camera(camera_shadow)
    if not camera_obj.is_shooting():
        return
    camera_obj.shooting()

    # tokenの取得要求
    msg_token_req = MsgTokenReq(imsi=imsi)

    # token取得するためsubscribe実行
    result_sub = tasks_mqtt.run_subscribe_by_mqtt.delay(host, port, msg_token_req.get_sub_topic())
    time.sleep(2)

    try:
        mqtt_client = CommMqtt(host, port)
        mqtt_client.connect()

        result = mqtt_client.publish(msg_token_req)

        mqtt_client.disconnect()
    except:
        print("error")

    while not result_sub.ready():
        time.sleep(1)

    value = redis_client.get('token')
    if not value:
        return

    payload_str = value.decode(encoding='utf-8')
    if not payload_str:
        return

    # 撮影画像をS3へputする
    send_images_data = SendImagesData(imsi, camera_obj)
    # TODO S3 bucket名を可変にする
    comm_aws_s3 = CommAwsS3('sample-iot-making-dev', [send_images_data])
    ok_list, ng_list = comm_aws_s3.put_s3(payload_str)

    # AWSへの送信処理
    mqtt_client = CommMqtt(host, port)
    mqtt_client.connect()
    sent_date_time = datetime.now()

    # 撮影情報を送信
    msg_images = MsgImages(imsi=imsi, sent_date_time=sent_date_time)
    mqtt_client.publish_for_send_list(msg_images, ok_list)

    mqtt_client.disconnect()

    camera_obj.image_remove()

    now = datetime.now()
    if now.hour == 22 and now.minute == 0:
        run(["sudo", "reboot"])


if __name__ == '__main__':

    main()
