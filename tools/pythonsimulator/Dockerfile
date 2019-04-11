FROM ubuntu:18.04
MAINTAINER Stefano Alberto Russo <stefano.russo@gmail.com>

ENV DEBIAN_FRONTEND=noninteractive

# Always start with an apt-get update 
RUN apt-get update

# Curl
RUN apt-get install curl -y

# Install get-pip script
RUN curl -O https://bootstrap.pypa.io/get-pip.py

# Install Python3 and Pip3 (python3-distutils required for pip3)
RUN apt-get install python3 python3-distutils -y 
RUN python3 get-pip.py 'pip==10.0.1'


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
WORKDIR /opt/PythingsOS











