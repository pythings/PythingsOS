import re
import sys
sys.path.append('deps')
import glob
import serial
import subprocess
import time
import os
import zipfile
from collections import namedtuple
from os import listdir
from os.path import isfile, join
import platform

# Defaults
DEFAULT_VERSION          = 'v1.0.0'
DEFAULT_CHOOSE_OPERATION = False
DEFAULT_INTERACTIVE      = False
DEFAULT_DEBUG            = False
DEFAULT_SILENT           = True
DEFAULT_HOST             = 'https://pythings.io'
DEFAULT_ARTIFACTS_PATH   = 'artifacts'
DEFAULT_ALLOW_DOWNLOAD   = False
DEFAULT_EXPERIMENTAL     = False

# Default Python
try:
    # Can we use "python3"?
    if subprocess.call(['python3', '--version'], stdout=open(os.devnull, 'w'), stderr=subprocess.STDOUT):
        raise OSError
except OSError:
    try:
        # Can we use "py"?
        if subprocess.call(['py', '--version'], stdout=open(os.devnull, 'w'), stderr=subprocess.STDOUT):
            raise OSError
    except OSError as e:
        # Fallback on a generic Python
        DEFAULT_PYTHON='python'
    else:
        # Use Py
        DEFAULT_PYTHON='py'
else:
    # Use Python3
    DEFAULT_PYTHON='python3'

# Platform-specific
if platform.system() == 'Windows':
    PLATFORM_SAFE_QUOTE='"'
else:
    PLATFORM_DEFAULT_PYTHON='python'
    PLATFORM_SAFE_QUOTE='\''

# Booleanize utility
def booleanize(var):
    if isinstance(var, bool):
        return var
    elif isinstance(var, str):
        if var.lower()=='false':
            return False
        else:
            return True
    elif isinstance(var, int) or isinstance(var, float):
        if var == 0 :
            return False
        else:
            return True
    else:
        print('')
        print('Value "{}" is not valid'.format(var))
        print('')
        sys.exit(1)

# Overrides from env vars
VERSION          = os.environ.get('VERSION', DEFAULT_VERSION)
CHOOSE_OPERATION = booleanize(os.environ.get('CHOOSE_OPERATION', DEFAULT_CHOOSE_OPERATION))
INTERACTIVE      = booleanize(os.environ.get('INTERACTIVE', DEFAULT_INTERACTIVE))
DEBUG            = booleanize(os.environ.get('DEBUG', DEFAULT_DEBUG))
SILENT           = booleanize(os.environ.get('SILENT', DEFAULT_SILENT))
PYTHON           = os.environ.get('PYTHON', DEFAULT_PYTHON)
HOST             = os.environ.get('HOST', DEFAULT_HOST)
ARTIFACTS_PATH   = os.environ.get('ARTIFACTS_PATH', DEFAULT_ARTIFACTS_PATH)
ALLOW_DOWNLOAD   = booleanize(os.environ.get('ALLOW_DOWNLOAD', DEFAULT_ALLOW_DOWNLOAD))
EXPERIMENTAL     = booleanize(os.environ.get('EXPERIMENTAL', DEFAULT_EXPERIMENTAL))
 
# Extra external settings
PORT      = os.environ.get('PORT', None)
PLATFORM  = os.environ.get('PLATFORM', None)
OPERATION = os.environ.get('OPERATION', None)
FROZEN    = os.environ.get('FROZEN', None)
if FROZEN is not None:
    FROZEN = booleanize(FROZEN)

# Support vars
only_console = False
serial_port = None

# Do we have command line arguments?
for arg in sys.argv:
    if arg.endswith('.py'):
        continue
    
    if arg == '--console':
        only_console = True
    else:
        if serial_port:
            raise ValueError('Two serial port arguments given or unrecognized option "{}"'.format(arg))
        if serial_port and PORT:
            raise ValueError('Cannot set port both via env var and command line arguments')            
        serial_port = arg  

# Set serial port if given via env var
if PORT:
    serial_port = PORT

#========================
#  Utility functions
#========================

def sanitize_file_chars(string):
    '''Quote a string so it can be used as an argument in a  posix shell

       According to: http://www.unix.org/single_unix_specification/
          2.2.1 Escape Character (Backslash)

          A backslash that is not quoted shall preserve the literal value
          of the following character, with the exception of a <newline>.

          2.2.2 Single-Quotes

          Enclosing characters in single-quotes ( '' ) shall preserve
          the literal value of each character within the single-quotes.
          A single-quote cannot occur within single-quotes.

    '''

    return "{}".format(PLATFORM_SAFE_QUOTE).join(PLATFORM_SAFE_QUOTE + p + PLATFORM_SAFE_QUOTE for p in string.split("'"))


def serial_ports():
    '''Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    '''

    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result


def valid(line):
    #print('Checking line validity: "{}"'.format(line))
    if not line:
        validity = False
    else:    
        if 'INFO' in line or 'DEBUG' in line or 'ERROR' in line or 'WARNING' in line or 'CRITICAL' in line:
            #print('Condition1')
            validity = True
        elif 'Version:' in line or 'Platform' in line or 'Thing ID' in line or '|-------' in line or 'Starting' in line:
            #print('Condition2')
            validity = True
        elif 'Error' in line or 'Exception' in line or 'File' in line:
            #print('Condition3')
            validity = True
        elif 'Cannot' in line:
            #print('Condition4')
            validity = True
        else:
            validity = False
    #print('Validity="{}"'.format(validity))
    return validity


def sanitize_encoding(text):
    return text.encode("utf-8", errors="ignore")


def format_shell_error(stdout, stderr, exit_code):
    
    string  = '\n#---------------------------------'
    string += '\n# Shell exited with exit code {}'.format(exit_code)
    string += '\n#---------------------------------\n'
    string += '\nStandard output: "'
    string += str(sanitize_encoding(stdout))
    string += '"\n\nStandard error: "'
    string += str(sanitize_encoding(stderr)) +'"\n\n'
    string += '#---------------------------------\n'
    string += '# End Shell output\n'
    string += '#---------------------------------\n'

    return string


def os_shell(command, capture=False, verbose=False, interactive=False, silent=False):
    '''Execute a command in the os_shell. By default prints everything. If the capture switch is set,
    then it returns a namedtuple with stdout, stderr, and exit code.'''
    
    if capture and verbose:
        raise Exception('You cannot ask at the same time for capture and verbose, sorry')

    # Log command
    if DEBUG:
        print('Executing command: {}'.format(command))

    # Execute command in interactive mode    
    if verbose or interactive:
        exit_code = subprocess.call(command, shell=True)
        if exit_code == 0:
            return True
        else:
            return False

    # Execute command getting stdout and stderr
    # http://www.saltycrane.com/blog/2008/09/how-get-stdout-and-stderr-using-python-subprocess-module/
    
    process          = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    (stdout, stderr) = process.communicate()
    exit_code        = process.wait()

    # Convert to str (Python 3)
    stdout = stdout.decode(encoding='UTF-8')
    stderr = stderr.decode(encoding='UTF-8')

    # Formatting..
    stdout = stdout[:-1] if (stdout and stdout[-1] == '\n') else stdout
    stderr = stderr[:-1] if (stderr and stderr[-1] == '\n') else stderr

    # Output namedtuple
    Output = namedtuple('Output', 'stdout stderr exit_code')

    if exit_code != 0:
        if capture:
            return Output(stdout, stderr, exit_code)
        else:
            print(format_shell_error(stdout, stderr, exit_code))      
            return False    
    else:
        if capture:
            return Output(stdout, stderr, exit_code)
        elif not silent:
            # Just print stdout and stderr cleanly
            print(stdout)
            print(stderr)
            return True
        else:
            return True


def abort(msg):
    print('')
    print(msg)
    print('')
    if (not OPERATION) or INTERACTIVE: 
        print('')
        print('Press any key to exit')
        try:
            raw_input()
        except:
            input()
        print('')
    sys.exit(1)


def download(url, dest=''):
    if not ALLOW_DOWNLOAD:
        abort('Sorry, I could not find the file within the installer and I am not allowed to download.')
    file_name = url.split('/')[-1]
    try:
        import urllib2
        # Python 2
        response = urllib2.urlopen(url)
        f = open(dest+file_name, 'wb')
        f.write(response.read())
        f.close()
       
    except ImportError:
        import urllib.request
        # Python3
        response = urllib.request.urlopen(url)
        data = response.read()
        with open(dest+file_name, 'wb') as f:
            f.write(data)


#========================
#  Main
#========================

try:
    if not only_console:
        
        if not OPERATION:
            print('')
            print('-----------------------------------------------')
            print('  Welcome to PythingsOS {} installer    '.format(VERSION))
            print('-----------------------------------------------')
            
            print('')
            print('Notes:')
            #print(' * An active Internet connection is required.')
            print(' * An active serial connection to your board is required.')
            print('    - Most common USB-to-serial drivers here: {}/downloads.'.format(HOST))
            print('    - Some boards require quality USB cables, switch cable in case of problems.')
            print(' * On Linux, run this program as root (i.e. "sudo installer.sh")')
            print('')
            
        # Create tmp dir if not already present
        if not os.path.isdir('tmp'):
            os.mkdir('tmp')
        
        if not PLATFORM:
        
            print('On which platform do you want to install?')
            print('')
            print(' 1) Esp8266')
            print(' 2) Esp32')
            print(' 3) Esp32 + SIM800')
            if EXPERIMENTAL:
                print(' 4) Esp8266 + SIM800 (experimental)')

            print('')
            
            sys.stdout.write('Your choice (number): ')
        
            try:
                platform_id  = input()
            except:
                abort('Error, please type a valid numerical choice')
            
            platforms={}
            platforms[1] = 'esp8266'
            platforms[2] = 'esp32'
            platforms[3] = 'esp32_sim800'
            if EXPERIMENTAL:
                platforms[4] = 'esp8266_sim800'
           
            try:
                platform_id = int(platform_id)
                platform    = platforms[platform_id]
            except:
                abort('Error, please type a valid numerical choice')
        else:
            if not PLATFORM in ['esp8266', 'esp8266_sim800', 'esp32', 'esp32_sim800']:
                abort('Error, got unsupported platform "{}"'.format(PLATFORM))            
            platform = PLATFORM
    else:
        platform_id = None
        platform   = None
    
    if (not only_console) and CHOOSE_OPERATION:
        print('')
        print('What operation do you want to perform?')
        print('')
        print(' 1) Flash and install PythingsOS')
        print(' 2) Only install PythingsOS')
        print(' 3) Open a serial console')
        print('')
        sys.stdout.write('Your choice (number): ')
    
        try:
            operation  = int(input())
            if not operation in [1,2,3]:
                raise
        except:
            abort('Error, please type a valid numerical choice')
    
    else:
        if only_console:
            operation=3
        else:
            operation=1
    print('----------')
    print(platform)
    
    #==========================
    #  Set operations
    #==========================
    if OPERATION:
        if OPERATION == 'flash':
            flash   = True
            copy    = False
            console = False
        elif  OPERATION == 'copy':
            flash   = False
            copy    = True
            console = False
        elif OPERATION == 'console':
            flash   = False
            copy    = False
            console = True
        else:
            abort('Error, got invalid OPERATION: "{}"'.format(OPERATION))
    
    else:
        # Set steps
        if operation == 1:
            flash   = True
            copy    = True
            console = True
            
        elif operation == 2:
            flash   = False
            copy    = True
            console = True
        
        elif operation == 3:
            flash   = False
            copy    = False
            console = True
        else:
            abort('Consistency exception')
    
    
    # Ask also if frozen or non frozen for esp8266
    frozen = False
    
    if flash and platform=='esp8266_sim800':
            print('')
            print('')
            print('PythingsOS for the Esp8266 + SIM800 platform only comes in frozen version.')
            print('')
            print('With a frozen version you will not be able to update PythingsOS')
            print('remotely as it will be frozen into the firmware, but you will')
            print('have more memory for your Apps and SSL plus SIM800 support.')
            print('')    
            print('Press any key to continue')
            frozen = True
            try:
                raw_input()
            except:
                input()

    if flash and platform=='esp8266':
        if FROZEN is None:
            print('')
            print('')
            print('Do you want a standard or a frozen PythingsOS version?')
            print('')
            print('With a frozen version you will not be able to update PythingsOS')
            print('remotely as it will be frozen into the firmware, but you will')
            print('have more memory for your Apps and SSL support.')
            print('')
            print(' 1) Standard')
            print(' 2) Frozen')
            print('')
            #print(' 3) Raspberry PI')
            
            sys.stdout.write('Your choice (number): ')
            
            try:
                frozen_choice  = int(input())
            except:
                abort('Error, please type a valid numerical choice')
        
            if frozen_choice == 1:
                frozen = False
            elif frozen_choice == 2:
                frozen = True
            else:
                abort('Error, please type a valid choice')
        else:
            frozen = FROZEN
    
    
    # Ask for serial port if not already set
    if not serial_port:
        print('')
        print('Scanning serial ports...')
        serial_ports = serial_ports()
        print('Done.')
        print('')
        print('On which serial port is the board connected?')
        print('')
        port_ids = [] 
        for i, port in enumerate(serial_ports):
            port_ids.append(i+1)
            print(' {}) {}'.format(i+1,port))
        if not port_ids:
            abort('No serial ports found. Have you installed the drivers and do you have rights to access serial ports?')
        print('')
        sys.stdout.write('Your choice (number): ')
        try:
            port_id  = int(input())
            if not operation in port_ids:
                raise
        except:
            abort('Error, please type a valid numerical choice')
        
        serial_port_raw = serial_ports[port_id-1]
        serial_port = sanitize_file_chars(serial_ports[port_id-1])
    else:
        serial_port_raw = serial_port
    
    print('Using "{}"'.format(serial_port))
    print('')
    
    
    if flash:
        
        # Step 0: download firmware
        use_local = False
    
        
        if platform in ['esp8266', 'esp8266_sim800']:
            if frozen:
                if os.path.isfile('{}/firmware/PythingsOS_{}_{}.frozen.bin'.format(ARTIFACTS_PATH, VERSION, platform)):
                    if ARTIFACTS_PATH != DEFAULT_ARTIFACTS_PATH:
                        print('WARNING: found and using local firmware file  in "artifacts/firmware/PythingsOS_{}_esp8266.frozen.bin"'.format(ARTIFACTS_PATH, VERSION))
                    use_local=True
                else:
                    print('')
                    print('Downloading firmware...')
                    download('{}/static/PythingsOS/firmware/PythingsOS_{}_{}.frozen.bin'.format(HOST,VERSION, platform), 'tmp/')
                    print('Done.')
                    print('')
            else:
                if os.path.isfile('{}/firmware/PythingsOS_{}_{}.bin'.format(ARTIFACTS_PATH, VERSION, platform)):
                    if ARTIFACTS_PATH != DEFAULT_ARTIFACTS_PATH:
                        print('WARNING: found and using local firmware file  in "artifacts/firmware/PythingsOS_{}_esp8266.bin"'.format(ARTIFACTS_PATH, VERSION))
                    use_local=True
                else:
                    print('')
                    print('Downloading firmware...')
                    download('{}/static/PythingsOS/firmware/PythingsOS_{}_{}.bin'.format(HOST,VERSION, platform), 'tmp/')
                    print('Done.')
                    print('')
                
        elif platform in ['esp32', 'esp32_sim800']:
            if os.path.isfile('{}/firmware/esp32-20190529-v1.11.bin'.format(ARTIFACTS_PATH)):
                if ARTIFACTS_PATH != DEFAULT_ARTIFACTS_PATH:
                    print('WARNING: found and using local firmware file  in "{}/firmware/esp32-20190529-v1.11.bin"'.format(ARTIFACTS_PATH))
                use_local=True
            else:
                print('Downloading firmware...')
                download('{}/static/MicroPython/esp32-20190529-v1.11.bin'.format(HOST), 'tmp/')
                print('Done.')
                print('')
        else:
            abort('Consistency Exception (Unknown platform "{}")'.format(platform))
    
    
        if not OPERATION:
            print('')
            print('Please put your board in programming mode. Most of the boards')
            print('switch automatically, but some don\'t and you will have to do it')        
            print('manually. After switching manually, detach and re-attach the board.')
            print('')
            print('Press any key to continue')
            try:
                raw_input()
            except:
                input()
        
        # Step 1: Erease flash
        if platform in ['esp8266', 'esp8266_sim800']:
            command = '{} deps/esptool.py --port {} erase_flash'.format(PYTHON, serial_port)
        elif platform in ['esp32', 'esp32_sim800']:
            command =  '{} deps/esptool.py --port {} erase_flash'.format(PYTHON, serial_port)  
        else:
            abort('Consistency Exception (Unknown platform "{}")'.format(platform))
    
        print('Erasing flash... (about 10 secs)')
        if not(os_shell(command, interactive=INTERACTIVE, silent=SILENT)):
            abort('Error (see output above)')
        time.sleep(3)
        print('Done.')
        print('')
    
        if not OPERATION:
            print('')
            print('Please put again your board in programming mode. If you')
            print('are switching manually, detach and re-attach the board.')
            print('')
            print('Press any key to continue')
            try:
                raw_input()
            except:
                input()
    
        # Step 2: Flash MicroPython firmware
        if platform in ['esp8266', 'esp8266_sim800']:
            if frozen:
                if use_local:
                    command = '{} deps/esptool.py --port {} --baud 115200 write_flash --flash_size=detect -fm dio 0 {}/firmware/PythingsOS_{}_{}.frozen.bin'.format(PYTHON, serial_port, ARTIFACTS_PATH, VERSION, platform)
                else:
                    command = '{} deps/esptool.py --port {} --baud 115200 write_flash --flash_size=detect -fm dio 0 tmp/PythingsOS_{}_{}.frozen.bin'.format(PYTHON, serial_port, VERSION, platform)
            else:
                if use_local:
                    command = '{} deps/esptool.py --port {} --baud 115200 write_flash --flash_size=detect -fm dio 0 {}/firmware/PythingsOS_{}_{}.bin'.format(PYTHON, serial_port, ARTIFACTS_PATH, VERSION, platform)
                else:
                    command = '{} deps/esptool.py --port {} --baud 115200 write_flash --flash_size=detect -fm dio 0 tmp/PythingsOS_{}_{}.bin'.format(PYTHON, serial_port, VERSION, platform)
    
        elif platform in ['esp32', 'esp32_sim800']:
                if use_local:
                    command = '{} deps/esptool.py --chip esp32 --port {} write_flash -z 0x1000 {}/firmware/esp32-20190529-v1.11.bin'.format(PYTHON, serial_port, ARTIFACTS_PATH)
                else:
                    command = '{} deps/esptool.py --chip esp32 --port {} write_flash -z 0x1000 tmp/esp32-20190529-v1.11.bin'.format(PYTHON, serial_port)
        else:
            abort('Consistency Exception (Unknown platform "{}")'.format(platform))
            
        print('Flashing firmware... (about a minute)')
        if not(os_shell(command, interactive=INTERACTIVE, silent=SILENT)):
            abort('Error (see output above)')
        time.sleep(5)
        print('Done.')
        print('')
    
        if INTERACTIVE:
            print('')
            print('Press any key to continue')
            try:
                raw_input()
            except:
                input()
    
        # Step 3: Check ampy and successful MicroPython install
        if platform in ['esp32', 'esp32_sim800']:
            print('Checking...')
            attempt_count=0
            while True:
                attempt_count+=1
                output = os_shell('{} deps/ampy.py -p {} ls'.format(PYTHON, serial_port), interactive=INTERACTIVE, silent=SILENT, capture=True)
                if output.exit_code != 0:
                    if attempt_count > 3:
                        print(format_shell_error(output.stdout, output.stderr, output.exit_code))
                        abort('Error, could not communicate with the board (see output above)')
                    else:
                        time.sleep(2)
                else:
                    time.sleep(2)
                    break
    
            print('Done.')
            print('')
    
    if not OPERATION:
        print('')
        print('Please put the board back in normal operation mode. If you')
        print('are switching manually, detach and re-attach the board.')
        print('')
        print('Press any key to continue')
        try:
            raw_input()
        except:
            input()
    
    if (copy and platform in ['esp32', 'esp32_sim800']) or operation == 2:
        
        # Step 3: (Download) and extract PythingsOS
        if os.path.isfile('{}/zips/PythingsOS_{}_{}.zip'.format(ARTIFACTS_PATH, VERSION, platform)):
            if ARTIFACTS_PATH != DEFAULT_ARTIFACTS_PATH:
                print('WARNING: found and using local zip file in "{}/zips/PythingsOS_{}_{}.zip"'.format(ARTIFACTS_PATH, VERSION, platform))
            use_local_zip=True
        else:
            print('Downloading PythingsOS...')
            url = '{}/static/PythingsOS/zips/PythingsOS_{}_{}.zip'.format(HOST, VERSION, platform)
            #print ('Downloading {}'.format(url))
            download(url, 'tmp/')
            print('Done.')
            use_local_zip=False
        print('')
    
        # (now extract)
        if not use_local_zip:
            zip_ref = zipfile.ZipFile('tmp/PythingsOS_{}_{}.zip'.format(VERSION, platform), 'r')
        else:
            zip_ref = zipfile.ZipFile('{}/zips/PythingsOS_{}_{}.zip'.format(ARTIFACTS_PATH, VERSION, platform), 'r')
        zip_ref.extractall('tmp/extracted')
        zip_ref.close()
    
        # Step 4: Copy over all files
        files_path = 'tmp/extracted/{}'.format(platform)
        files = [f for f in listdir(files_path) if isfile(join(files_path, f))]
    
        print('Installing PythingsOS... (about two minutes)')
        for file in files:
            if file.endswith('.py'):
                while True:
                    if DEBUG:
                        print('Now copying {}/{} ...'.format(files_path,file))
                    if not os_shell('{} deps/ampy.py -p {} put {}/{}'.format(PYTHON, serial_port,files_path,file), interactive=INTERACTIVE, silent=SILENT):
                        print('Failed, retrying...')
                        time.sleep(2)
                    else:
                        time.sleep(2)
                        break
    
        print('Done.')
        print('')
        
        if INTERACTIVE:
            print('')
            print('Press any key to continue')
            try:
                raw_input()
            except:
                input()
        
        # Step 5: Reset
        if not OPERATION:
            print('Now resetting the board...')
            # TODO: Change this since in the esp32 executing a reset will not "return", cusing a neverending loop
            time.sleep(2)
            output = os_shell('{} deps/ampy.py -p {} run deps/reset.py'.format(PYTHON, serial_port), interactive=INTERACTIVE, silent=SILENT, capture=True)
            if output.exit_code != 0:
                print('Automatic reset seems to have failed, you might need a manual reset.')
            else:
                print('Done.')
            print('')
    
        if INTERACTIVE:
            print('')
            print('Press any key to continue')
            try:
                raw_input()
            except:
                input()
    
    if console:
    
        print('Now opening a serial connection...')
        print('The output below is coming from PythingsOS running on your board!')
        print('  - Hit ctrl-C to exit.')
        print('  - Try pressing the reset button on your board if you don\'t see anything.')
        print('')
        # Step 6: Open serial console
        try:
            with serial.Serial(serial_port_raw, 115200, timeout=1) as ser:
                while True:
                    # Read a '\n' terminated line
                    line_raw = ser.readline()
                    if isinstance(line_raw, bytes):
                        try:
                            line = line_raw.decode('ascii')
                        except:
                            line=''
                    else:
                        line = line_raw
                    # Clean line
                    line_clean = line.rstrip()
    
                    # Print line if not empty
                    if line_clean:
                        print(line_clean)
    
        except serial.serialutil.SerialException:
            raise
            # print('Cannot open serial port')
    
    if not OPERATION:
        print('')
        print('Press any key to exit2')
        try:
            raw_input()
        except:
            input()

except Exception as e:
    abort(e)
    
