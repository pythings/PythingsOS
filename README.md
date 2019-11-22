# PythingsOS

### Requirements

MicroPython version: v1.9.4

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

### Updateability

The hal.py is not updatable (it is supposed to be very "intimate" with the hardware), while pal.py it is. 

### Development

To run the installer using the build artifacts, use:

    ARTIFACTS_PATH="../../artifacts" ./installer.sh




