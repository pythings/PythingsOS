#!/bin/bash

aid="$1"
tid="$2"
be="$3"

if [ -z "$1" ]; then
    echo "Usage: ./run.sh AID TID (BACKEND)"
    echo "       ./run.sh bash"
    exit 1
fi

if [ -z "$2}" ]; then
    echo "Usage: ./run.sh AID TID (BACKEND)"
    echo "       ./run.sh bash"
    exit 1
fi

if [[ "x$3" == "xlocal" ]] ; then
    
    # Get first network interface IP address as backend
    be=$(ifconfig | grep -Eo 'inet (addr:)?([0-9]*\.){3}[0-9]*' | grep -Eo '([0-9]*\.){3}[0-9]*' | grep -v '127.0.0.1' | head -n 1)
    
    if [[ "x$be" == "x" ]] ; then
        echo "Error: you set \"local\" as backend but I cannot find any local IP address (?)."
        echo ""
        exit
    fi
fi

docker run -v $PWD/../../:/opt/PythingsOS -eINTERACTIVE=True -it pythingsos/micropythonsimulator $1 $tid $be
