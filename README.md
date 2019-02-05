# PythingsOS

### Requirements

Python version: Python 3 required

MicroPython version: MicroPython > 1.8.6 required


### How to draft a new release

Run the utilities/prepare_release.sh script, that will will update versions and generate files lists.

Then:

	git commit
	git push
    git tag -a v1.0.1
    git push origin v1.0.1
    
 In case of wrong release tags, use:
 
    git tag -d v1.0.1
    git push origin :refs/tags/v1.0.1

### How to generate the (firmware) builds

To generate the MicroPython + PythingsOS firmware builds (only esp8266 and esp8266_esp-12 supported), enter in the tools/buildchain directory and run ""./build.sh"

### Updateability

The hal.py is not updatable (it is supposed to be very "intimate" with the hardware), while sal.py it is. 