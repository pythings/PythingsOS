#!/bin/bash
echo "Now exporting firmware to firmware folder..."
CWD=$(pwd)
docker run -v $PWD/firmware:/firmware -i -t pythings/toolchain
