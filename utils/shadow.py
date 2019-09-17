import json
import math
import copy
from datetime import datetime
from json import JSONDecodeError

import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


class BaseShadowData:

    key = None  # Shadowのフィールドキー

    payload_dict = None  # Shadowから取得したペイロード（dict）

    delta_dict = None  # desiredとreportedの差分（dict）
    desired_dict = None  # desired部分のデータ（dict）
    reported_dict = None # 各フィールドキーごとのreportedデータ（dict）

    delta_key_dict = None  # 各フィールドキーごとの差分データ（dict）
    desired_key_dict = None  # 各フィールドキーごとのdesiredデータ（dict）
    reported_key_dict = None  # 各フィールドキーごとのreportedデータ（dict）

    def __init__(self, payload):

        # ペイロード（Json）をdictに変換し各クラス変数に設定する
        # ペイロード全体
        self.set_payload_dict(payload)
        # delta
        self.set_delta_dict()
        # desired
        self.set_desired_dict()
        # reported
        self.set_reported_dict()

        if self.key:
            # 各フィールドキーごとのdelta、desired、reportedをクラス変数に設定する
            self.delta_key_dict = self.delta_dict.get(self.key, {})
            self.desired_key_dict = self.desired_dict.get(self.key, {})
            self.reported_key_dict = self.reported_dict.get(self.key, {})

    def set_payload_dict(self, payload):
        """
        ペイロード（Json）をdictに変換しクラス変数に設定する
        :param payload: ペイロード（Json）
        :return: なし
        """
        try:
            # Json→dictに変換
            self.payload_dict = json.loads(payload)
        except TypeError as e:
            logger.error("shadow TypeError error")
            logger.error("type:{0}".format(type(e)))
            logger.error("args:{0}".format(e.args))
            logger.error("{0}".format(e))
            self.payload_dict = {}
        except JSONDecodeError as e:
            logger.error("shadow JSONDecodeError error")
            logger.error("type:{0}".format(type(e)))
            logger.error("args:{0}".format(e.args))
            logger.error("{0}".format(e))
            self.payload_dict = {}

    def set_delta_dict(self):
        """
        ペイロード（dict）からdeltaを取得しクラス変数に設定する
        :return: なし
        """
        self.delta_dict = self.get_payload_state_section().get('delta', {})

    def set_desired_dict(self):
        """
        ペイロード（dict）からdesiredを取得しクラス変数に設定する
        :return: なし
        """
        self.desired_dict = self.get_payload_state_section().get('desired', {})

    def set_reported_dict(self):
        """
        ペイロード（dict）からreportedを取得しクラス変数に設定する
        :return: なし
        """
        self.reported_dict = self.get_payload_state_section().get('reported', {})

    def get_payload_state_section(self):
        """
        ペイロード（dict）からstateを取得する
        :return: ペイロードのsate部分（dict）
        """
        return self.payload_dict.get('state', {})

    def get_payload_state_add_reported(self, reported_dict):
        """
        パラメータのreportedデータ（dict）をstate、reported（dict）に
        設定したデータを取得する
        :param reported_dict:
        :return: dict
        """
        return {'state': {'reported': reported_dict}}

    def is_delta_key(self, key_name):

        if not self.delta_key_dict:
            return False

        if key_name in list(self.delta_key_dict.keys()):
            return True

        return False

    def get_update_payload(self):

        if not self.delta_dict:
            return {}

        update_dict = copy.deepcopy(self.delta_dict)
        update_payload = self.get_payload_state_add_reported(update_dict)
        return update_payload


class SensorShadowData(BaseShadowData):

    key = "sensor"  # Shadowのキー

    sense = None

    interval = None

    def __init__(self, payload):
        super().__init__(payload)

        if self.desired_key_dict:
            self.interval = self.desired_key_dict.get('interval', 10)

    def is_send(self):

        now = datetime.now()
        return (now.minute % self.interval) == 0


class CameraShadowData(BaseShadowData):

    key = "camera"  # Shadowのキー

    quality = 10  # カメラのクオリティ
    shoot_timing = 1  # 時間起動時の撮影タイミング
    resolution_width = 800  # 解像度（幅）
    resolution_height = 600  # 解像度（高さ）
    tmp_dir = '/tmp'  # 画像の一時保存フォルダ
    is_shooting = False  # 撮影可否

    def __init__(self, payload):
        super().__init__(payload)

        if self.desired_key_dict:
            self.quality = self.desired_key_dict.get('quality', 10)
            self.shoot_timing = self.desired_key_dict.get('shoot_timing', 1)
            self.resolution_width = self.desired_key_dict.get('resolution_width', 1024)
            self.resolution_height = self.desired_key_dict.get('resolution_height', 768)
            self.tmp_dir = self.desired_key_dict.get('tmp_dir', '/tmp')
            self.is_shooting = self.desired_key_dict.get('is_shooting', False)
