FROM ubuntu:18.04
MAINTAINER Stefano Alberto Russo <stefano.russo@gmail.com>

ENV DEBIAN_FRONTEND=noninteractive

#----------------------------------
# Dependencies
#----------------------------------

# Always start with an apt-get update 
RUN apt-get update

# Install build requirements
RUN apt-get update && apt-get -y install build-essential libreadline-dev libffi-dev pkg-config python-setuptools python-dev git
RUN apt-get install python3 -y

# Download MicroPython and dependencies
RUN cd / && git clone https://github.com/micropython/micropython.git
RUN cd /micropython && git pull && git checkout v1.11 && git submodule update

# Build dependencies
RUN cd /micropython/ports/unix && make axtls
RUN cd /micropython/mpy-cross && make

# Enable dupterm for the MicroPython Unix port
RUN mv /micropython/ports/unix/mpconfigport.h /micropython/ports/unix/mpconfigport.h.or
RUN echo "#define MICROPY_PY_OS_DUPTERM (2)" > /micropython/ports/unix/mpconfigport.h
RUN cat /micropython/ports/unix/mpconfigport.h.or >> /micropython/ports/unix/mpconfigport.h

# Build MicroPython
RUN cd /micropython/ports/unix && make

# Download the Micropython-lib
RUN cd / && git clone https://github.com/micropython/micropython-lib.git
RUN cd /micropython-lib && git checkout b89114c && git submodule update

# Download the Pycopy-lib (Micropython-lib fork)
#RUN cd / && git clone https://github.com/pfalcon/pycopy-lib.git
#RUN cd /pycopy-lib && git pull && git checkout 27ca006  && git submodule update

# Create micropython symlink in /usr/bin
RUN ln -s /micropython/ports/unix/micropython /usr/bin/micropython


#----------------------------------
# Pythings user
#----------------------------------

# Add pythings user
RUN useradd pythings -m -s /bin/bash


#----------------------------------
# PythingsOS configuration
#----------------------------------

# Switch to "pythings" user
USER pythings

# Create conf dir
RUN mkdir /home/pythings/.pythings

# Set default pool
RUN echo "development" >  /home/pythings/.pythings/pool

# Create log files dir
RUN mkdir /tmp/logs

# Install the micropython-lib for the pythings user
RUN cd /micropython-lib &&  make install # This will made modules like os in /home/pythings/.micropython/lib/

# Install the pycopy-lib for the pythings user
#RUN cd /pycopy-lib &&  make install # This will made modules like os in /home/pythings/.micropython/lib/

# Switch back to "root" user
USER root


#----------------------------------
# Entrypoint
#----------------------------------

# Copy, give right permissions and set entrypoint
COPY entrypoint.sh /entrypoint.sh
RUN chmod 755 /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]

# Default user once the container starts
USER pythings
WORKDIR /opt/PythingsOS/MicroPython









