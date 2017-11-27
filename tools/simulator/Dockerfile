FROM ubuntu:14.04
MAINTAINER Stefano Alberto Russo <stefano.russo@gmail.com>

# Install requirements
RUN apt-get update && apt-get -y install build-essential libreadline-dev libffi-dev pkg-config python-setuptools python-dev git

# Download and build MicroPython
WORKDIR /
RUN git clone https://github.com/micropython/micropython.git
WORKDIR /micropython/unix
RUN make axtls
RUN make
WORKDIR / 
RUN git clone https://github.com/micropython/micropython-lib.git
WORKDIR /micropython-lib
RUN make install
WORKDIR /micropython/unix
RUN ./micropython -m upip install micropython-os
RUN ./micropython -m upip install micropython-socket
RUN ./micropython -m upip install micropython-machine

# Download Pythings and checkout proper version
RUN git clone https://github.com/Pythings/PythingsOS.git /opt/PythingsOS
RUN cd /opt/PythingsOS && git pull && git checkout 4af8108 #ac4fa16 #02eb3c1 #42d31ea

# Build Pythings for the MicroPython system (consolidate symlinks)
RUN cd  /opt/PythingsOS/builds/MicroPython/ && ./build.sh


#RUN rsync -r --copy-links /root/PythingsOS/MicroPython/* /
#RUN rsync -r --copy-links /root/PythingsOS/MicroPython/.* / ; exit 0
#RUN rm -rf /common # Why we need this?! TODO: Investigate...
#RUN mkdir /pythings_data

# Create micropython symlink in /usr/bin
RUN ln -s /micropython/unix/micropython /usr/bin/micropython

# Set workdir for bash login
WORKDIR /opt/PythingsOS/builds/MicroPython/

# Copy and set entrypoint
COPY entrypoint.sh /entrypoint.sh
RUN chmod 755 /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
