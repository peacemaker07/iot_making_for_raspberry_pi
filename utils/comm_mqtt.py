import json
import time
from utils.helper import RedisClient

from paho.mqtt.client import MQTT_ERR_SUCCESS
import paho.mqtt.client as mqtt

from utils.date_time import TimeMeasure
import tasks as tasks_mqtt
from utils.message import MsgShadowGet, MsgShadowUpdate

import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


class CommMqtt:

    host = None
    port = None

    client = None

    def __init__(self, host, port):

        self.host = host
        self.port = port

        self.client = mqtt.Client(protocol=mqtt.MQTTv311)

    def connect(self):

        try:
            result = self.client.connect(self.host, port=self.port, keepalive=60)
            time.sleep(5)
        except:
            return False

        return True if result == MQTT_ERR_SUCCESS else False

    def disconnect(self):

        time.sleep(1)
        self.client.disconnect()

    def publish_for_send_list(self, msg_obj, buf_list):
        """
        Publish処理
        送信データのリストを1件ずつPublishする
        :param msg_obj: 送信メッセージのオブジェクト
        :param buf_list: 送信するデータのリスト
        :return: 送信成功送信バッファリスト、送信失敗送信バッファリスト（タプル）
        """

        # 送信成功リスト
        send_ok_buf_list = []
        # 送信失敗リスト
        send_ng_buf_list = []

        # 再送信データが大量にあると通信が長引いてしまうため
        # 一定時間、送信処理が続いた場合は次回の送信時に送信するようにする
        time_measure = TimeMeasure(time_out_sec=60)

        for idx, buf in enumerate(buf_list):

            if time_measure.is_time_out():
                # 次回起動時に送信する
                send_ng_buf_list.append(buf)
                continue

            # Publish
            result = self.publish(msg_obj, buf=buf, idx=idx)
            if result:
                send_ok_buf_list.append(buf)
            else:
                send_ng_buf_list.append(buf)

        return send_ok_buf_list, send_ng_buf_list

    def publish(self, msg_obj, buf=None, idx=0):
        """
        Publishの実行
        :param msg_obj: 送信メッセージオブジェクト
        :param idx: 送信データのindex
        :param buf: 送信データ
        :return: 結果（True：成功、False：失敗）
        """

        # Publishするトピック名を取得する
        topic = msg_obj.get_pub_topic()
        if not topic:
            return False

        # 送信メッセージを取得する
        send_data = msg_obj.create_pub_data(buf, idx) if buf else {}
        logger.debug('publish send_data:[%s]' % send_data)

        try:
            # Publish実行
            result = self.client.publish(topic, json.dumps(send_data), qos=1)
        except Exception as e:
            logger.error("failed publish")
            logger.error("type:{0}".format(type(e)))
            logger.error("args:{0}".format(e.args))
            logger.error("{0}".format(e))
            result = False

        return result


class CommMqttShadow(CommMqtt):

    imsi = None

    def __init__(self, host, port, imsi):
        super().__init__(host, port)

        self.imsi = imsi

    def shadow_get(self):

        redis_client = RedisClient()
        msg_shadow_get = MsgShadowGet(imsi=self.imsi)

        result_sub = tasks_mqtt.run_subscribe_by_mqtt.delay(self.host, self.port, msg_shadow_get.get_sub_topic())
        time.sleep(2)

        try:
            self.connect()
            result = self.publish(msg_shadow_get)
            self.disconnect()
        except Exception as e:
            logger.error(e)

        while not result_sub.ready():
            time.sleep(1)

        value = redis_client.get('token')
        if not value:
            return ''

        payload_str = value.decode(encoding='utf-8')
        if not payload_str:
            return ''

        return payload_str

    def shadow_update(self, update_dict):

        msg_shadow_update = MsgShadowUpdate(imsi=self.imsi)
        time.sleep(2)

        try:
            self.connect()
            result = self.publish(msg_shadow_update, buf=update_dict)
            self.disconnect()
        except Exception as e:
            logger.error(e)
