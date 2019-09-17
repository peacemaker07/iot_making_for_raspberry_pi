from utils.unix_time import UnixTime


class BaseMessage:
    """
    送信メッセージを管理する基本クラス
    """

    sent_date_time = None  # 送信日時
    imsi = None
    pub_topic = None
    sub_topic = None

    def __init__(self, imsi=None, sent_date_time=None):
        """
        送信データの設定を行う
        :param sent_date_time:
        """
        self.imsi = imsi
        self.sent_date_time = sent_date_time

    def get_pub_topic(self):

        return self.pub_topic.format(self.imsi)

    def get_sub_topic(self):

        return self.sub_topic.format(self.imsi)

    def create_pub_data(self, buf, idx):
        """
        送信メッセージの作成処理
        :param buf: 送信データ
        :param idx: 送信データのindex
        :return: 送信メッセージ（dict）
        """
        raise NotImplementedError


class MsgTokenReq(BaseMessage):

    pub_topic = 'token/req/{}'
    sub_topic = 'token/res/{}'

    def create_pub_data(self, buf, idx):
        """
        カメラ画像送信メッセージクラス
        :param buf:
        :param idx: 送信データのindex
        :return:
        """
        # 送信メッセージの各項目に送信データを設定する
        send_data = {}

        return send_data


class MsgEnvironment(BaseMessage):

    pub_topic = 'environment/{}'

    def create_pub_data(self, buf, idx):

        # 送信メッセージの各項目に送信データを設定する
        send_data = {
            "timestamp": UnixTime.date_time2unix_time(self.sent_date_time, ms=idx),
            'temp': buf.temp,
            'humi': buf.humi,
            'lux': buf.lux,
            'pressure': buf.pressure,
            'moisture': buf.moisture,
            'position': buf.position,
        }

        return send_data


class MsgImages(BaseMessage):
    """
    カメラ画像送信メッセージクラス
    """

    pub_topic = "cam/images/{}"

    def create_pub_data(self, buf, idx):
        """
        カメラ画像送信メッセージクラス
        :param buf: カメラ画像送信データ
        :param idx: 送信データのindex
        :return: カメラ画像送信データ
        """
        # 送信メッセージの各項目に送信データを設定する
        send_data = {
            "timestamp": UnixTime.date_time2unix_time(self.sent_date_time, ms=idx),
            "created": buf.created,
            "cam_obj_key": buf.cam_obj_key if buf.cam_obj_key else None,
        }

        return send_data


class MsgShadowGet(BaseMessage):

    pub_topic = '$aws/things/{}/shadow/get'
    sub_topic = '$aws/things/{}/shadow/get/accepted'

    def create_pub_data(self, buf, idx):

        send_data = {}

        return send_data


class MsgShadowUpdate(BaseMessage):

    pub_topic = '$aws/things/{}/shadow/update'
    sub_topic = '$aws/things/{}/shadow/update/accepted'

    def create_pub_data(self, buf, idx):

        return buf
