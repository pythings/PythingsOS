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

# Download and build MicroPython
RUN cd / && git clone https://github.com/micropython/micropython.git
RUN cd /micropython && git checkout 3053748 && git submodule update
RUN cd /micropython/unix && make axtls
RUN cd /micropython/unix && make
RUN cd / && git clone https://github.com/micropython/micropython-lib.git
RUN cd /micropython-lib && git checkout b89114c && git submodule update
#RUN cd /micropython-lib &&  make install # This will made modules like os in /root/.micropython/lib/

# Create micropython symlink in /usr/bin
RUN ln -s /micropython/unix/micropython /usr/bin/micropython


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

RUN cd /micropython-lib &&  make install # This will made modules like os in /home/pythings/.micropython/lib/

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









