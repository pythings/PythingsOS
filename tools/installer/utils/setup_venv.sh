#!/bin/bash
virtualenv venv
source venv/bin/activate
curl https://bootstrap.pypa.io/get-pip.py | python
pip install esptool==2.2
pip install adafruit-ampy==1.0.7
deactivate
#rm -rf vierualenv
