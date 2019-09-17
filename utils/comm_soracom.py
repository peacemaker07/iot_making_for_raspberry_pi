import requests


class CommSoracom:
    """
    注意：metadataの取得は、コンソールのグループの「SORACOM Air 設定」で
         メタデータサービスを有効にする必要があります
         https://dev.soracom.io/jp/start/metadata/
    """

    metadata_url = 'http://metadata.soracom.io/v1/subscriber'
    metadata_dict = None

    def __init__(self):

        res = requests.get(self.metadata_url)
        self.metadata_dict = res.json()

    def get_imsi(self):

        return self.metadata_dict.get('imsi')
