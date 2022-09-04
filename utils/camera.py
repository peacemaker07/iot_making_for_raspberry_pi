import os
import time
from datetime import datetime
from picamera import PiCamera, Color

from utils.unix_time import UnixTime
from utils.command import Command


class Camera:

    shadow = None  # カメラ関連の設定（shadow）
    image_path = None
    created = None

    def __init__(self, shadow):
        """
        各設定を読み込み初期化を行う
        """

        self.shadow = shadow

    def shooting(self):
        """
        撮影処理
        :return: カメラ画像オブジェクト
        """

        now = datetime.now()
        self.created = UnixTime.date_time2unix_time(now)

        self.image_path = self._shooting()

    def _shooting(self):
        """
        カメラ撮影を行う
        :param quality: 画像のクオリティ
        :return: 撮影した画像のファイルパス
        """

        # カメラデバイスが認識されているか確認する
        detected_num = self.get_camera_devices_detected_num()
        if detected_num == 0:
            # 認識されていないため処理終了
            return None

        camera = PiCamera()

        # 解像度を設定する
        camera.resolution = (self.shadow.resolution_width, self.shadow.resolution_height)

        # ISO感度を設定する
        camera.ISO = 1600
        # DRCを設定する
        camera.drc_strength = 'high'

        # 撮影日時取得を取得
        now = datetime.now()
        now_str = now.strftime("%Y%m%d_%H%M%S")

        # 画像のファイル名を生成
        image_name = self.get_file_name(now_str)
        image_path = self.shadow.tmp_dir + "/" + image_name

        # プレビュー開始
        camera.start_preview()

        # Camera warm-up time
        time.sleep(5)

        # 撮影
        camera.capture(image_path, quality=self.shadow.quality)

        # プレビュー終了しカメラクローズ
        camera.stop_preview()
        camera.close()

        return image_path

    def is_shooting(self):
        """
        撮影タイミングか判定を行う
        :return: 結果（True：撮影を行う、False：撮影しない）
        """

        if not self.shadow.is_shooting:
            return False

        now = datetime.now()
        if now.minute == 0:
            return True
        if now.minute / 10 % self.shadow.shoot_timing == 0:
            return True

        return False

    def get_file_name(self, now_str):
        """
        画像のファイル名を取得する
        :param now_str: 現在日付（YYYYMMDD_HHMMSS）
        :return: ファイル名
        """
        file_name = "camera_" + now_str + ".jpg"
        return file_name

    def image_remove(self):
        """
        画像の削除
        :param image_path: 削除する画像のファイルパス
        :return: 結果（True：成功、False：失敗）
        """
        if not self.image_path:
            return False

        # ファイルが存在するかチェック
        if not os.path.exists(self.image_path):
            return False

        # 削除実行
        os.remove(self.image_path)
        return True

    def get_camera_devices_detected_num(self):
        """
        カメラデバイスが認識されているか取得する
        :return: 認識されているカメラデバイスの数
        """

        detected_key = "detected"
        detected_num = 0

        retcd, stdout_bin, stderr_bin = Command.cmd_run(["vcgencmd", "get_camera"])
        stdout_data = stdout_bin.decode('utf-8') if retcd else None
        if not retcd:
            # 異常のため認識なしとする
            return detected_num

        if detected_key not in stdout_data:
            # 認識数がないため認識なしとする
            return detected_num

        try:
            stdout_list = stdout_data.split(" ")
            for stdout in stdout_list:
                stdout = stdout.replace('\n', "")
                if detected_key in stdout:
                    detected_str = stdout.split("=")[1]
                    detected_num = int(detected_str)
        except Exception as e:
            pass

        return detected_num
