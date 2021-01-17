# The PythingsOS

Pythings is a quick and easy way of programming IoT devices, directly from a web browser, in Python. It shines on microcontrollers like the ESP8266 and the ESP32, but it works nicely also on small Linux boards.

The PythingsOS is a minimal Operating System based on Python and MicroPython. It implements all the base functionalities required by an IoT device like network management, remote updates and security, so you don’t have to. Devices (Things) running PythingsOS are orchestrated by the [Pythings Cloud](https://github.com/pythings/PythingsCloud).

![Image of the PythingsOS](https://pythings.io/static/img/custom/PythingsOS.png)

This PythingsOS version is based on:

 - MicroPython version: v1.11

 - Python versions: 3.4-3.6

Please note that the code in this repository is *intentionally* very condensed and with limited comments in order to allow being interpreted by low-end microcontrollers (as the ESP8266), without requiring to be compiled into C modules.


## Quickstart



### Development

There are mainly two ways of working with this codebase:

- using the Docker simulators for Python and MicroPython, or
- building the codebase into artifacts.

To run the simulators just have a look at the `tools/pythonsimulator` and `tools/micropythonsimulator` folders, which provide build and run scripts. You can also modify the run scripts to mount the codebase as a volume (but it is not yet supportd out-of-the-box).

To instead build the artifacts, as the zipfiles, the installer and the firmware (which comes both with the code built-in as frozen C modules and as plain Python files to be interpreted by the microcontroller), you can have a look at the `utilities/draft_release.sh` script, that if run will, in turn:

- Update version in common and in the buildchain
- Create files lists for remote updates
- Clean the old artifacts
- Prepare the new artifacts:
  - the zipfiles;
  - the self extracting archives (selfarchives);
  - the firmwares, frozen and not;
  - the installer.

After the build, you can either directly use the artifacts in the "artifacts" folder (including the installer itself), or use the installer with the newly built firmwares and zifiles (if you did not build the installer):

     cd tools/installer
     ARTIFACTS_PATH="../../artifacts" ./installer.sh


### Code structure


- `Drivers`: this is a submodule intented to provide some generic MicroPython Drivers as the SIM800L cellular modem. See [pythings/Drivers](https://github.com/pythings/Drivers) for more info.
- `LICENSE`: the Apache Licence version 2 text.
- `MicroPython`: the generic MicroPython codebase.
- `Python`: the generic Python codebase.
- `README.md`: this file.
- `RaspberryPi`: the RaspberryPi codebase.
- `artifacts`: the folder where build artifacts, as the zipfiles, the installer and the firmware.
- `common`: common parts of the codebase (linked from the other folders)
- `esp32`: the ESP32 codebase.
- `esp32_sim800`: the ESP32 codebase with support for the SIM800 cellular modem.
- `esp8266`: the ESP8266 codebase.
- `esp8266_sim800`: the ESP8266 codebase with support for the SIM800 cellular modem.
- `tools`: code for the firmware buildchain, the installer, the Python and MicroPython simulators.
- `utilities`: various utility scripts.

Please note that every file inside the folder for a given platform (i.e. the ESP32) can be remotely updated when updatng PythingsOS (not-forzen), except for the `hal.py` file, which stands for Hardware Abstraction Layer and it is supposed to be very hardware-specific (i.e. Pins, leds, etc.).



## Licence


This software is licensed under the Apache Licence version 2.0, unless otherwise specificed.

