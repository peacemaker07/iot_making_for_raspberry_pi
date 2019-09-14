IoT Making for RaspberryPi
====

Raspberry Piを使って以下を行う場合の実装例を集めたリポジトリ

- センサからのデータ取得（Grove Systemを使用）
- クラウドへのデータ送信

## Description

### 使用するもの

- Raspberry Pi (必須)
  - Board : Raspberry Pi 3 Model B
  - OS : Raspbian Stretch Lite
  - Python : 3.5
- [SORACOM](https://www.amazon.co.jp/dp/B01G1GSYHW) (任意)
  - SIM
  - USBドングル AK-020
- GrovePi (任意)

### 実装例

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

インストールはこちらを参照
https://github.com/DexterInd/GrovePi/tree/master/Software/Python

### celeryを使用してShadowのやりとりを行う

#### 準備

```
# redis インストール
$ sudo apt-get install redis-server

# ライブラリインストール
$ cd [リポジトリルート]
$ pip3 install -r requirements.txt

# サービス化
$ sudo ln -s /home/pi/iot_making_for_raspberry_pi/celery_worker.service /etc/systemd/system/celery_worker.service
$ sudo systemctl enable celery_worker
```

#### 実行

```
$ python3 main_shadow_by_aws_iot.py -e [エンドポイント] -r [ルート証明書パス] -c [デバイス証明書パス] -k [プライベートキーパス] -id [client id]
```
