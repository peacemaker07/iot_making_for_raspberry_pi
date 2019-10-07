import json
import boto3

from utils.date_time import TimeMeasure

import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


class BaseCommAwsS3:

    bucket_name = None

    def __init__(self, bucket_name):
        """
        初期化処理
        """

        self.bucket_name = bucket_name

    def put_obj(self, put_path, obj):
        """
        S3へのput処理
        :param put_path: put対象のファイルパス
        :param obj: Bucketオブジェクト
        :return: 結果（True：成功、False：失敗）、オブジェクトキー（タプル）
        """

        logger.debug('put path [%s]' % put_path)

        # アップロード画像を読み込み
        with open(put_path, "rb") as f:
            body_obj = f.read()

        # S3へput
        response = obj.put(
            Body=body_obj,
            ContentEncoding="utf-8",
            ContentType="text/plane"
        )
        # レスポンスをチェック
        response_metadata = response.get('ResponseMetadata', {})
        http_status_code = response_metadata.get('HTTPStatusCode', None)
        if http_status_code and http_status_code == 200:
            return True, obj.key

        logger.error(response)
        return False, None

    def get_obj(self, bucket, key_name, file_name):
        """
        S3からダウンロード
        :param bucket: bucketオブジェクト
        :param key_name: ファイルパス
        :param file_name: ファイル名
        :return: 結果（True：成功、False：失敗）、オブジェクトキー（タプル）
        """

        logger.debug("S3 key_name: %s" % key_name)
        logger.debug("S3 file_name: %s" % file_name)

        obj = bucket.Object(file_name)
        bucket.download_file(key_name, file_name)

        return obj.key


class CommAwsS3(BaseCommAwsS3):
    """
    S3との通信処理を行うクラス
    """

    send_image_list = None  # 送信する画像のリスト

    def __init__(self, bucket_name, send_image_list):
        """
        送信データの設定を行う
        :param send_image_list: 送信する画像のリスト
        :param serial: シリアルNo
        """
        super().__init__(bucket_name)

        self.send_image_list = send_image_list

    def put_s3(self, s3_token_payload_str):
        """
        S3へのアップロード処理
        :param s3_token_payload_str
        :return: S3へのアップロード成功、失敗リスト（タプル）
        """

        logger.debug("S3 upload: start")

        try:
            # アクセストークンを取得しS3リソースを生成する
            token = json.loads(s3_token_payload_str)

            s3 = boto3.resource(
                's3',
                aws_access_key_id=token["AccessKeyId"],
                aws_secret_access_key=token["SecretAccessKey"],
                aws_session_token=token["SessionToken"]
            )

            # bucketオブジェクトを生成する
            bucket = s3.Bucket(self.bucket_name)
        except Exception as e:
            logger.error("failed boto3 resource")
            logger.error("type:{0}".format(type(e)))
            logger.error("args:{0}".format(e.args))
            logger.error("{0}".format(e))
            return [], self.send_image_list

        # 再送信データが大量にあると通信が長引いてしまうため
        # 一定時間、送信処理が続いた場合は次回の起動時に送信するようにする
        time_measure = TimeMeasure(time_out_sec=60)

        # アップロード成功リスト
        ok_list = []
        # アップロード成功リスト
        ng_list = []

        for send_image in self.send_image_list:

            if time_measure.is_time_out():
                # タイムアウトした場合は次回送信する
                ng_list.append(send_image)
                continue

            # 送信
            try:
                # S3へアップロード
                result, obj_key = self._put_s3(bucket, send_image.imsi, send_image.image_path)
                # アップロードした画像のオブジェクトキーを取得
                send_image.cam_obj_key = obj_key
            except Exception as e:
                logger.error("failed camera put s3")
                logger.error("type:{0}".format(type(e)))
                logger.error("args:{0}".format(e.args))
                logger.error("{0}".format(e))
                result = False

            if result:
                ok_list.append(send_image)
            else:
                ng_list.append(send_image)

        logger.debug("S3 upload: end")

        return ok_list, ng_list

    def _put_s3(self, bucket, imsi, image_path):
        """
        S3へアップロード
        :param bucket: バケットオブジェクト
        :param image_path: アップロードするファイルパス
        :return: 結果（True：成功、False：失敗）、オブジェクトキー（タプル）
        """
        # ファイルパスが存在しない場合は使用していない想定なので成功とする
        if not image_path:
            return True, None

        # ファイルパスからファイル名を取得しS3へ保存時のファイル名とする
        image_name = image_path.split("/")[-1]
        obj = bucket.Object(imsi + "/camera/" + image_name)

        result, obj_key = self.put_obj(image_path, obj)
        return result, obj_key
