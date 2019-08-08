IoT Making for RaspberryPi
====

Raspberry Pi, SORACOMを使っての

## Description

- Raspberry Pi
  - Board : Raspberry Pi 3 Model B
  - OS : Raspbian Stretch Lite
  - Python : 3.5
- [SORACOM](https://www.amazon.co.jp/dp/B01G1GSYHW)
  - SIM
  - USBドングル AK-020

## Demo

## Requirement

## Install

### SORACOM関連

#### ドングルの設定

- [wvdial](https://dev.soracom.io/jp/start/device_setting/#raspi_usb)
- [pppd](https://qiita.com/CLCL/items/95693f6a8daefc73ddaa)

## Usage

### カメラモジュールを使用する

[Raspberry Pi Camera Module V2 カメラモジュール (Daylight - element14)](https://www.amazon.co.jp/gp/product/B01ER2SKFS/ref=ppx_yo_dt_b_asin_title_o01_s00?ie=UTF8&psc=1)

```bash
# カメラモジュールを有効化
$ sudo raspi-config

「5 Interfacing Options」->「P1 Camera」->「Yes」を選択
再起動

# 認識されているかチェック
$ vcgencmd get_camera
supported=1 detected=1

両方「1」になっていればOK

# 撮影テスト
$ sudo raspistill -o image.jpg
```

### GrovePi

Github : https://github.com/DexterInd/GrovePi

```
# Install
$ pwd
/home/pi
$ curl -kL dexterindustries.com/update_grovepi | bash
...

$ cd Firmware
bash firmware_update.sh
```
