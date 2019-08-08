import json
import time
import paho.mqtt.client as mqtt
from datetime import datetime

from utils.grove_pi import GrovePi
from utils.unix_time import UnixTime

host = 'beam.soracom.io'
port = 1883
topic = 'environment'

client = mqtt.Client(protocol=mqtt.MQTTv311)

try:

    # 温度、湿度を取得
    temp, humi = GrovePi.get_temp_humi()
    # 照度を取得 ( http://wiki.seeedstudio.com/Grove-Digital_Light_Sensor/ )
    lux = GrovePi.get_lux()
    # Loudness Sensor ( http://wiki.seeedstudio.com/Grove-Loudness_Sensor/ )
    loudness_pi_mode = 0
    loudness = GrovePi.analog_read(loudness_pi_mode)
    # Air Quality Sensor ( http://wiki.seeedstudio.com/Grove-Air_Quality_Sensor_v1.3/ )
    air_pi_mode = 1
    air_quality = GrovePi.analog_read(air_pi_mode)
    # 水分量を取得
    # moisture = GrovePi.get_moisture()

    client.connect(host, port=port, keepalive=60)
    time.sleep(5)
    now = datetime.now()

    # センシング情報を送信
    json_dict = {
        'timestamp': UnixTime.date_time2unix_time(now),
        'temp': temp,
        'humi': humi,
        'lux': lux,
        'loudness': loudness,
        'air_quality': air_quality,
    }
    result = client.publish(topic, json.dumps(json_dict), qos=1)

except Exception as e:
    print(e)
    pass

client.disconnect()

