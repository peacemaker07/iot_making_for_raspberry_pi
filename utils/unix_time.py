import time


class UnixTime:
    """
    UnitTime関連のクラス
    """

    @staticmethod
    def date_time2unix_time(date_time, ms=0):
        """
        datetimeオブジェクトをUnixTimeに変換する
        :param date_time: 変換する日時
        :param ms: ミリ秒
        :return: unixtime（int）
        """

        millisecond = 1000
        unix_time = int(time.mktime(date_time.timetuple())) * millisecond + ms

        return unix_time
