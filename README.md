# PythingsOS

### Requirements

MicroPython version: v1.11

Python versions: 3.4-3.6


### How to draft a new release

Run the utilities/draft_release.sh script, that will:

- Update version in common and in the buildchain
- Create files lists for remote updates
- Clean the old artifacts
- Prepare the new artifacts:
  - the zipfiles;
  - the self extracting archives (selfarchives);
  - the firmwares, frozen and not;
  - the installer.

 After the build, you can either use the artifacts in the "artifacts" folder, or use the installer:

     cd tools/installer && python3 installer.py

### Updateability

Every file can be remotely updated except the hal.py, which it is supposed to be hardware-specific (i.e. Pins, leds, etc.)

### Development

To run the installer using the build artifacts, use:

    ARTIFACTS_PATH="../../artifacts" ./installer.sh




