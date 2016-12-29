

# PythingsOS

***** WARNING: This is an early stage documentation stub *****

### Requirements

Python version: Python 3 required

MicroPython version: MicroPython > 1.8.6 required

### Logical structure
Note: still work in progress

* **common**

	* **Python**

	* **MicroPython**

		* **esp8266**
		
			* **esp8266_esp-12**
			
### Names

All settings across code and APIs calls are represented thought three letters abbreviations for saving bandwidth, memory and encryption/decryption time. We really wanted to avoid this but it turned ut to be impossible given the very limited resources of some systems we want to support (like the esp8266).

Here is an early-stage list:

- tid = Thing ID
- aid = Application ID
- tok = Session Token
- rav = Running App Version
- rpv = Running pythings version
- fzp = Frozen Pythings
- pln = Pool Name
- stg = Settings
- bea = Back End Address
- eph = Epoch (seconds)
- ssl = Secure Socket Layer
- pye = Payload Encryption
- key = Key (for payload encryption)
- kty = Key type (only Aes 128 ecb supported)
- ken = Key encoding (only RSA 1024 supported)
- apd = App Data
- did = (app) Data ID
- spv = Set Pythins Version
- sav = Set App Version
- mai = Managemnt Interval
- woi = Worker Interval
- mas = Management sync 
- wos = Worker Sync
- wst = Web Setup Timeout
- bop = Battery Operated



