#!/bin/bash

rsync -avz --exclude 'tools' --exclude 'utilities' --exclude '.git' --exclude 'builds' --exclude 'extras' ../../ PythingsOS

docker build  -t pythingsos/buildchain .
./export_firmware.sh
