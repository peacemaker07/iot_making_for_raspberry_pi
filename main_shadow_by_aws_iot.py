import json
import time
import argparse
import tasks as tasks_shadow
from utils.helper import RedisClient


def main():

    # Read in command-line parameters
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--endpoint", action="store", required=True, dest="host", help="Your AWS IoT custom endpoint")
    parser.add_argument("-r", "--rootCA", action="store", required=True, dest="rootCAPath", help="Root CA file path")
    parser.add_argument("-c", "--cert", action="store", dest="certificatePath", help="Certificate file path")
    parser.add_argument("-k", "--key", action="store", dest="privateKeyPath", help="Private key file path")
    parser.add_argument("-id", "--clientId", action="store", dest="clientId", default="basicShadowUpdater", help="Targeted client id")

    args = parser.parse_args()
    host = args.host
    root_ca_path = args.rootCAPath
    certificate_path = args.certificatePath
    private_key_path = args.privateKeyPath
    client_id = args.clientId

    if not args.certificatePath or not args.privateKeyPath:
        parser.error("Missing credentials for authentication.")
        exit(2)

    # Shadow GET
    result_get = tasks_shadow.run_shadow_by_aws_iot.delay(client_id,
                                                          host,
                                                          root_ca_path,
                                                          private_key_path,
                                                          certificate_path)
    while not result_get.ready():
        time.sleep(1)

    redis_client = RedisClient()
    value = redis_client.get('shadow_get_by_aws_iot')
    if not value:
        return

    payload_str = value.decode(encoding='utf-8')
    if not payload_str:
        return
    payload_dict = json.loads(payload_str)
    # {
    #     "metadata": {
    #         "desired": {
    #             "sensor": {
    #                 "interval": {
    #                     "timestamp": 1567956165
    #                 }
    #             }
    #         }
    #     },
    #     "timestamp": 1567960792,
    #     "state": {
    #         "desired": {
    #             "sensor": {
    #                 "interval": 10
    #             }
    #         },
    #         "delta": {
    #             "sensor": {
    #                 "interval": 10
    #             }
    #         }
    #     },
    #     "version": 2,
    #     "clientToken": "fc7e803c-a83f-40bd-b352-aca5d30c98d1"
    # }

    # shadow update
    state_dict = payload_dict.get('state')
    if state_dict and state_dict.get('delta'):
        update_payload = {
            "state": {
                "reported": state_dict['delta']
            }
        }
        result_update = tasks_shadow.run_shadow_by_aws_iot.delay(client_id,
                                                                 host,
                                                                 root_ca_path,
                                                                 private_key_path,
                                                                 certificate_path,
                                                                 json.dumps(update_payload))
        while not result_get.ready():
            time.sleep(1)


if '__main__' == __name__:

    main()
