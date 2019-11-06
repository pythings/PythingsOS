#!/bin/bash
CWD=$(pwd)
docker run -v $CWD/firmware:/firmware -i -t pythings/buildchain bash
