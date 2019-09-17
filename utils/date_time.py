from datetime import datetime, timezone, timedelta


class TimeMeasure:
    """
    経過秒、タイムアウトなどを管理するクラス
    """

    start_time = None  # 開始時間
    time_out_sec = 0  # タイムアウト（秒）

    def __init__(self, time_out_sec=None):
        """
        初期化処理
        :param time_out_sec: タイムアウト（秒）
        """

        self.start_time = datetime.now()
        self.time_out_sec = time_out_sec

    def is_time_out(self):
        """
        タイムアウトチェック
        :return: チェック結果
        """

        if not self.time_out_sec:
            return False

        now = datetime.now()
        delta = now - self.start_time

        if self.time_out_sec < delta.seconds:
            return True

        return False

    def get_pass_sec(self):
        """
        経過時間を取得
        :return: 経過秒
        """

        now = datetime.now()
        delta = now - self.start_time

        return delta.seconds
