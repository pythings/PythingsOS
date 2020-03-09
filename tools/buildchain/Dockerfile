from pythings/espopensdk

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
ENV VER="v1.1.0"

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

# Build for esp8266_sim800 (normal) # No, not enough space for the selfarchives. Maybe use pyminifier? 
#RUN cp -L /home/xtensa/PythingsOS/artifacts/selfarchives/esp8266_sim800/selfarchive.py /home/xtensa/micropython/$PORTS_DIR/esp8266/modules/
#RUN cd /home/xtensa/micropython/$PORTS_DIR/esp8266 && make clean
#RUN cd /home/xtensa/micropython/$PORTS_DIR/esp8266 && make axtls # Comment this line for > v1.9.4
#RUN cd /home/xtensa/micropython/$PORTS_DIR/esp8266 && make all
#RUN mv /home/xtensa/micropython/$PORTS_DIR/esp8266/build/firmware-combined.bin /home/xtensa/builds/PythingsOS_${VER}_esp8266_sim800.bin



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

# Add softuart 
COPY Makefile-1.11-softuart /home/xtensa/micropython-frozen/$PORTS_DIR/esp8266/Makefile
COPY modmachine.c /home/xtensa/micropython-frozen/$PORTS_DIR/esp8266/
COPY modmachine.h /home/xtensa/micropython-frozen/$PORTS_DIR/esp8266/
COPY esp8266_common.ld /home/xtensa/micropython-frozen/$PORTS_DIR/esp8266/
COPY softuart.c /home/xtensa/micropython-frozen/$PORTS_DIR/esp8266/
COPY softuart.h /home/xtensa/micropython-frozen/$PORTS_DIR/esp8266/

# Build for esp8266_sim800 (fozen)
RUN cp -L /home/xtensa/PythingsOS/esp8266_sim800/* /home/xtensa/micropython-frozen/$PORTS_DIR/esp8266/modules/
RUN cp -a /home/xtensa/PythingsOS/common/crypto* /home/xtensa/micropython-frozen/$PORTS_DIR/esp8266/modules/
RUN cd /home/xtensa/micropython-frozen/$PORTS_DIR/esp8266 && make clean
#RUN cd /home/xtensa/micropython-frozen/$PORTS_DIR/esp8266 && make axtls # Comment this line for > v1.9.4
RUN cd /home/xtensa/micropython-frozen/$PORTS_DIR/esp8266 && make all
RUN mv /home/xtensa/micropython-frozen/$PORTS_DIR/esp8266/build/firmware-combined.bin /home/xtensa/builds/PythingsOS_${VER}_esp8266_sim800.frozen.bin

#COPY build_bytecode.sh /home/xtensa/build_bytecode.sh
#RUN cd /home/xtensa/PythingsOS/esp8266_sim800 && bash /home/xtensa/build_bytecode.sh
#RUN mkdir /home/xtensa/builds/bytecode && cp -a /home/xtensa/PythingsOS/esp8266_sim800/*.mpy /home/xtensa/builds/bytecode/

#-------------------
#   Entrypoint,
#  volumes  & co
#-------------------

USER root
RUN mkdir /builds
COPY entrypoint.sh /entrypoint.sh
RUN chmod 755 /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
















