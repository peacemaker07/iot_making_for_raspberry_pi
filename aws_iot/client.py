from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient


class Client:

    client = None

    def __init__(self, client_id, end_point, root_ca, private_key, certificate):
        """

        :param client_id:
        :param end_point:
        :param root_ca:
        :param private_key:
        :param certificate:
        """
        self.client = AWSIoTMQTTClient(client_id)
        self.client.configureEndpoint(end_point, 8883)
        self.client.configureCredentials(root_ca, private_key, certificate)
        self.client.configureAutoReconnectBackoffTime(2, 32, 20)
        self.client.configureOfflinePublishQueueing(-1)
        self.client.configureDrainingFrequency(2)
        self.client.configureConnectDisconnectTimeout(10)
        self.client.configureMQTTOperationTimeout(5)

    def connect(self):
        """
        接続処理
        :return: 結果（True：成功、False：失敗）
        """
        return self.client.connect()

    def publish(self, topic, payload):
        """
        Publish処理
        :param topic: トピック名
        :param payload: 送信データ
        :return: 結果（True：成功、False：失敗）
        """
        return self.client.publish(topic, payload, 1)

    def subscribe(self, topic, cb):
        """
        Subscribe処理
        :param topic: トピック名
        :param cb: コールバック関数
        :return: 結果（True：成功、False：失敗）
        """
        return self.client.subscribe(topic, 1, cb)

    def unsubscribe(self, topic):
        """
        Unsubscribe処理
        :param topic: トピック名
        :return: 結果（True：成功、False：失敗）
        """
        return self.client.unsubscribe(topic)

    def disconnect(self):
        """
        切断処理
        :return: 結果（True：成功、False：失敗）
        """
        return self.client.disconnect()
