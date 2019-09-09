from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTShadowClient


class ShadowClient(object):

    client = None
    bot = None

    def __init__(self, client_id, end_point, root_ca, private_key, certificate):
        """

        :param client_id:
        :param end_point:
        :param root_ca:
        :param private_key:
        :param certificate:
        """
        self.client = AWSIoTMQTTShadowClient(client_id)
        self.client.configureEndpoint(end_point, 8883)
        self.client.configureCredentials(root_ca, private_key, certificate)
        self.client.configureAutoReconnectBackoffTime(2, 32, 20)
        self.client.configureConnectDisconnectTimeout(10)  # 10 sec
        self.client.configureMQTTOperationTimeout(5)  # 5 sec

    def connect(self):
        """
        接続処理
        :return: 結果（True：成功、False：失敗）
        """
        return self.client.connect()

    def create_shadow_handler_with_name(self, shadow_name):
        """
        デバイスShadowハンドラ作成
        :return: デバイスShadowオブジェクト
        """
        self.bot = self.client.createShadowHandlerWithName(shadow_name, True)

    def shadow_get(self, call_back):
        """
        Thing Shadowデータの最新データ取得
        :param call_back: レスポンスを取得するコールバック関数
        :return: なし
        """
        self.bot.shadowGet(call_back, 5)

    def shadow_update(self, payload, call_back):
        """
        Thing Shadowデータの更新
        :param payload: 送信データ
        :param call_back: レスポンスを取得するコールバック関数
        :return: なし
        """
        self.bot.shadowUpdate(payload, call_back, 5)

    def shadow_register_delta_callback(self, callback):
        """
        Thing Shadow deltaデータ発生時の処理登録
        :param callback: deltaデータ発生時のコールバック関数
        :return:
        """
        if self.bot:
            self.bot.shadowRegisterDeltaCallback(callback)

    def disconnect(self):
        """
        切断処理
        :return: 結果（True：成功、False：失敗）
        """
        return self.client.disconnect()
