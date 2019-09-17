import json
import time
import paho.mqtt.client as mqtt
from datetime import datetime
import logging

from utils.grove_pi import GrovePi
from utils.unix_time import UnixTime
from utils.comm_mqtt import CommMqttShadow
from utils.comm_soracom import CommSoracom
from utils.shadow import SensorShadowData

host = 'beam.soracom.io'
port = 1883
topic = 'environment'

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def main():

    client = mqtt.Client(protocol=mqtt.MQTTv311)

    try:

        # imsiを取得
        soracom_obj = CommSoracom()
        imsi = soracom_obj.get_imsi()

        mqtt_shadow = CommMqttShadow(host, port, imsi)
        # shadow get
        json_str = mqtt_shadow.shadow_get()
        # sensorのセクションを取得
        sensor_shadow = SensorShadowData(json_str)
        # 送信タイミングがチェック
        if not sensor_shadow.is_send():
            return

        client.connect(host, port=port, keepalive=60)
        time.sleep(5)

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
        result = client.publish(topic + '/' + imsi, json.dumps(json_dict), qos=1)

        # shadow update
        if sensor_shadow.delta_dict:
            update_payload = sensor_shadow.get_payload_state_add_reported(sensor_shadow.delta_dict)
            mqtt_shadow.shadow_update(update_payload)

    except Exception as e:
        logger.error(e)

    client.disconnect()


if __name__ == '__main__':
    main()

