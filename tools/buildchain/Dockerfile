############################################################
# Dockerfile to build ESPOpen toolchain
# Based on Ubuntu 14.04
############################################################

FROM ubuntu:14.04

# Don't ask user options when installing
env DEBIAN_FRONTEND noninteractive
RUN echo APT::Install-Recommends "0"; >> /etc/apt/apt.conf
RUN echo APT::Install-Suggests "0"; >> /etc/apt/apt.conf

#-------------------
# Install toolchain
#-------------------

# multiverse is required by unrar
RUN apt-get -y update && apt-get install -y \
    git \ 
    software-properties-common \
    python-software-properties \
    && add-apt-repository -y "deb http://archive.ubuntu.com/ubuntu precise multiverse" 
    
RUN apt-get update && apt-get install -y \
    unrar \
    make \
    autoconf \
    automake \
    libtool \
    gcc \
    g++ \ 
    gperf \
    flex \
    bison \
    texinfo \
    gawk \
    ncurses-dev \
    libexpat-dev \
    python \
    python-serial \
    sed \
    python-dev \
    unzip \
    bash \
    wget \
    nano \
    help2man

## Clean apt cache
RUN apt-get -y autoremove && \
    apt-get -y clean && \
    rm -rf /var/lib/apt/lists/* && \
    rm -rf /tmp/*

# create user xtensa - toolchain cannot be built as root...
RUN useradd -ms /bin/bash xtensa
USER xtensa
WORKDIR /home/xtensa

ENV PATH /home/xtensa/esp-open-sdk/xtensa-lx106-elf/bin:$PATH

# GIT checkout and make toolchain
RUN git clone --recursive https://github.com/pfalcon/esp-open-sdk.git
RUN cd esp-open-sdk && git checkout e8d757b && git submodule update
WORKDIR /home/xtensa/esp-open-sdk
RUN make

# Checkout Micropython & checkout commit
WORKDIR /home/xtensa
RUN git clone --recursive https://github.com/micropython/micropython.git
# Use v1.8.6 (5a1d63f) or v1.9.4 (421b84a) or v1.10 (3e25d61) or v1.11 (6f75c4f)
RUN cd /home/xtensa/micropython && git checkout 6f75c4f && git submodule update

# Copy strucutre for allowing building frozen version
RUN cp -a /home/xtensa/micropython /home/xtensa/micropython-frozen

# Add PythingsOS code
COPY PythingsOS /home/xtensa/PythingsOS
USER root
RUN chown -R xtensa:xtensa /home/xtensa/PythingsOS
USER xtensa


#-------------------
# Prepare build
#-------------------

# Set version
ENV VER="v1.0.0-rc3"

# Use the following for MicroPython <= v1.8.6
#ENV PORTS_DIR="" 
# Use the following for MicroPython > v1.8.6
ENV PORTS_DIR="ports"

# Prepare dir 
RUN mkdir /home/xtensa/builds 


#-------------------
# Build Normal
#-------------------

# Build mpy-cross
RUN cd /home/xtensa/micropython && make -C mpy-cross

# Disable Berkeley DB to make more space for PythingsOS (required for MicroPython > 1.9.4)
COPY Makefile-1.11 /home/xtensa/micropython/$PORTS_DIR/esp8266/Makefile

# Load edited main.c to call the self-extracting archives before the boot.py
#COPY main.c-1.8.6 /home/xtensa/micropython/$PORTS_DIR/esp8266/main.c
#COPY main.c-1.9.4 /home/xtensa/micropython/$PORTS_DIR/esp8266/main.c 
COPY main.c-1.11 /home/xtensa/micropython/$PORTS_DIR/esp8266/main.c

# Build for esp8266 (normal)
RUN cp -L /home/xtensa/PythingsOS/artifacts/selfarchives/esp8266/selfarchive.py /home/xtensa/micropython/$PORTS_DIR/esp8266/modules/
RUN cd /home/xtensa/micropython/$PORTS_DIR/esp8266 && make clean
#RUN cd /home/xtensa/micropython/$PORTS_DIR/esp8266 && make axtls # Comment this line for > v1.9.4
RUN cd /home/xtensa/micropython/$PORTS_DIR/esp8266 && make all
RUN mv /home/xtensa/micropython/$PORTS_DIR/esp8266/build/firmware-combined.bin /home/xtensa/builds/PythingsOS_${VER}_esp8266.bin

# Build for esp8266_esp-12 (normal)
RUN cp -L /home/xtensa/PythingsOS/artifacts/selfarchives/esp8266_esp-12/selfarchive.py /home/xtensa/micropython/$PORTS_DIR/esp8266/modules/
RUN cd /home/xtensa/micropython/$PORTS_DIR/esp8266 && make clean
#RUN cd /home/xtensa/micropython/$PORTS_DIR/esp8266 && make axtls # Comment this line for > v1.9.4
RUN cd /home/xtensa/micropython/$PORTS_DIR/esp8266 && make all
RUN mv /home/xtensa/micropython/$PORTS_DIR/esp8266/build/firmware-combined.bin /home/xtensa/builds/PythingsOS_${VER}_esp8266_esp-12.bin



#-------------------
# Build Frozen
#-------------------

# Build mpy-cross
RUN cd /home/xtensa/micropython-frozen && make -C mpy-cross

# Disable Berkeley DB to make more space for PythingsOS (required for MicroPython > 1.9.4)
COPY Makefile-1.11 /home/xtensa/micropython-frozen/$PORTS_DIR/esp8266/Makefile

# Build for esp8266 (frozen)
RUN cp -L /home/xtensa/PythingsOS/esp8266/* /home/xtensa/micropython-frozen/$PORTS_DIR/esp8266/modules/
RUN cp -a /home/xtensa/PythingsOS/common/crypto* /home/xtensa/micropython-frozen/$PORTS_DIR/esp8266/modules/
RUN cd /home/xtensa/micropython-frozen/$PORTS_DIR/esp8266 && make clean
#RUN cd /home/xtensa/micropython-frozen/$PORTS_DIR/esp8266 && make axtls # Comment this line for > v1.9.4
RUN cd /home/xtensa/micropython-frozen/$PORTS_DIR/esp8266 && make all
RUN mv /home/xtensa/micropython-frozen/$PORTS_DIR/esp8266/build/firmware-combined.bin /home/xtensa/builds/PythingsOS_${VER}_esp8266.frozen.bin

# Build for esp8266-esp-12 (fozen)
RUN cp -L /home/xtensa/PythingsOS/esp8266_esp-12/* /home/xtensa/micropython-frozen/$PORTS_DIR/esp8266/modules/
RUN cp -a /home/xtensa/PythingsOS/common/crypto* /home/xtensa/micropython-frozen/$PORTS_DIR/esp8266/modules/
RUN cd /home/xtensa/micropython-frozen/$PORTS_DIR/esp8266 && make clean
#RUN cd /home/xtensa/micropython-frozen/$PORTS_DIR/esp8266 && make axtls # Comment this line for > v1.9.4
RUN cd /home/xtensa/micropython-frozen/$PORTS_DIR/esp8266 && make all
RUN mv /home/xtensa/micropython-frozen/$PORTS_DIR/esp8266/build/firmware-combined.bin /home/xtensa/builds/PythingsOS_${VER}_esp8266_esp-12.frozen.bin

#COPY build_bytecode.sh /home/xtensa/build_bytecode.sh
#RUN cd /home/xtensa/PythingsOS/esp8266_esp-12 && bash /home/xtensa/build_bytecode.sh
#RUN mkdir /home/xtensa/builds/bytecode && cp -a /home/xtensa/PythingsOS/esp8266_esp-12/*.mpy /home/xtensa/builds/bytecode/

#-------------------
#   Entrypoint,
#  volumes  & co
#-------------------

USER root
RUN mkdir /builds
COPY entrypoint.sh /entrypoint.sh
RUN chmod 755 /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
















