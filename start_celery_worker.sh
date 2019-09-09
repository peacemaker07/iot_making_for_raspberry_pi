#!/bin/bash

cd /home/pi/iot_making_for_raspberry_pi
celery -A tasks worker --loglevel=info --uid pi
