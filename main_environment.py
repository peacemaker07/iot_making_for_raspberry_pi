import json
import time
import paho.mqtt.client as mqtt
from datetime import datetime

from utils.unix_time import UnixTime

host = 'beam.soracom.io'
port = 1883
topic = 'environment'

client = mqtt.Client(protocol=mqtt.MQTTv311)

try:

    # 温度、湿度を取得
    # temp, humi = GrovePi.get_temp_humi()
    # 照度を取得
    # lux = GrovePi.get_lux()
    # 水分量を取得
    # moisture = GrovePi.get_moisture()

    client.connect(host, port=port, keepalive=60)
    time.sleep(5)
    now = datetime.now()

    # センシング情報を送信
    json_dict = {
        'timestamp': UnixTime.date_time2unix_time(now)
    }
    result = client.publish(topic, json.dumps(json_dict), qos=1)
    print(result)

except Exception as e:
    print(e)
    pass

client.disconnect()

