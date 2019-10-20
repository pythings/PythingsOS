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

# Defaults
VERSION          = 'v1.0.0-rc3'
CHOOSE_OPERATION = False
INTERACTIVE      = False
DEBUG            = False
SILENT           = True
PYTHON           = os.environ.get('PYTHON', 'python')
HOST             = 'https://pythings.io'

# Booleanize utility
def booleanize(var):
    if isinstance(var, bool):
        return var
    elif isinstance(var, str):
        if var.lower=='false':
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

# Overrides
VERSION          = os.environ.get('VERSION', VERSION)
CHOOSE_OPERATION = os.environ.get('CHOOSE_OPERATION', booleanize(CHOOSE_OPERATION))
INTERACTIVE      = os.environ.get('INTERACTIVE', booleanize(INTERACTIVE))
DEBUG            = os.environ.get('DEBUG', booleanize(DEBUG))
SILENT           = os.environ.get('SILENT', booleanize(SILENT))
HOST             = os.environ.get('HOST', HOST)


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
        serial_port = arg  

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

    return "\\'".join("'" + p + "'" for p in string.split("'"))


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
    sys.exit(1)


def download(url, dest=''):
    
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

if not only_console:
    print('')
    print('-----------------------------------------------')
    print('  Welcome to PythingsOS {} installer    '.format(VERSION))
    print('-----------------------------------------------')
    
    print('')
    print('Notes:')
    print(' * You will need an active Internet connection to download the required files.')
    print(' * You will need a working serial connection to your board.')
    print('    - Most common USB-to-serial drivers here: {}/downloads.'.format(HOST))
    print('    - Some chips require quality USB cables, switch cable in case of problems.')
    print(' * On Linux, run this program as root (i.e. "sudo installer.sh")')
    print('')
    
    # Create tmp dir if not already present
    if not os.path.isdir('tmp'):
        os.mkdir('tmp')
    
    print('What type of chip do you want to operate on?')
    print('')
    print(' 1) Esp8266')
    print(' 2) Esp32')
    #print(' 3) Raspberry PI')
    print('')
    
    sys.stdout.write('Your choice (number): ')

    try:
        chip_type_id  = input()
    except:
        abort('Error, please type a valid numerical choice')
    
    chips={}
    chips[1] = 'esp8266'
    chips[2] = 'esp32'
    #chips[3] = 'raspberrypi'
    
    try:
        chip_type_id = int(chip_type_id)
        chip_type    = chips[chip_type_id]
    except:
        abort('Error, please type a valid numerical choice')
else:
    chip_type_id = None
    chip_type    = None

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
forzen = False
if flash and chip_type=='esp8266':
    print('')
    print('Do you want a standard or a frozen PythingsOS version?')
    print('With a frozen version you will not be able to update')
    print('the OS as it will be burn into the firmware, but you')
    print('will have more free memory for your App.')
    print('')
    print(' 1) Standard')
    print(' 2) Frozen')
    print('')
    #print(' 3) Raspberry PI')
    
    sys.stdout.write('Your choice (number): ')
    
    try:
        forzen_choice  = int(input())
    except:
        abort('Error, please type a valid numerical choice')

    if forzen_choice == 1:
        frozen = False
    elif forzen_choice == 2:
        frozen = True
    else:
        abort('Error, please type a valid choice')





# Ask for serial port if not already set
if not serial_port:
    print('')
    print('Scanning serial ports...')
    serial_ports = serial_ports()
    print('Done.')
    print('')
    print('On which serial port is the device connected?')
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

print('Using "{}'.format(serial_port))
print('')


if flash:
    
    # Step 0: download firmware
    use_local = False
    print('Downloading firmware...')
    if chip_type== 'esp8266':
        if frozen:
            if os.path.isfile('../../artifacts/firmware/PythingsOS_{}_esp8266.frozen.bin'.format(VERSION)):
                print('WARNING: found and using local firmware file  in "artifacts/firmware/PythingsOS_{}_esp8266.frozen.bin"'.format(VERSION))
                use_local=True
            else:
                download('{}/static/PythingsOS/firmware/PythingsOS_{}_esp8266.frozen.bin'.format(HOST,VERSION), 'tmp/')
        else:
            if os.path.isfile('../../artifacts/firmware/PythingsOS_{}_esp8266.bin'.format(VERSION)):
                print('WARNING: found and using local firmware file  in "artifacts/firmware/PythingsOS_{}_esp8266.bin"'.format(VERSION))
                use_local=True
            else:
                download('{}/static/PythingsOS/firmware/PythingsOS_{}_esp8266.bin'.format(HOST,VERSION), 'tmp/')
            
    elif chip_type == 'esp32':
        download('{}/static/MicroPython/esp32-20190529-v1.11.bin'.format(HOST), 'tmp/')
    else:
        abort('Consistency Exception')
    print('Done.')
    print('')
    
    # Step 1: Erease flash
    if chip_type== 'esp8266':
        command = '{} deps/esptool.py --port {} erase_flash'.format(PYTHON, serial_port)
    elif chip_type == 'esp32':
        command =  '{} deps/esptool.py --port {} erase_flash'.format(PYTHON, serial_port)  
    else:
        abort('Consistency Exception')

    print('Erasing flash... (about 10 secs)')
    if not(os_shell(command, interactive=INTERACTIVE, silent=SILENT)):
        abort('Error (see output above)')
    time.sleep(3)
    print('Done.')
    print('')
     
    # Step 2: Flash MicroPython firmware
    if chip_type== 'esp8266':
        if frozen:
            if use_local:
                command = '{} deps/esptool.py --port {} --baud 115200 write_flash --flash_size=detect -fm dio 0 ../../artifacts/firmware/PythingsOS_{}_esp8266.frozen.bin'.format(PYTHON, serial_port, VERSION)
            else:
                command = '{} deps/esptool.py --port {} --baud 115200 write_flash --flash_size=detect -fm dio 0 tmp/PythingsOS_{}_esp8266.frozen.bin'.format(PYTHON, serial_port, VERSION)
        else:
            if use_local:
                command = '{} deps/esptool.py --port {} --baud 115200 write_flash --flash_size=detect -fm dio 0 ../../artifacts/firmware/PythingsOS_{}_esp8266.bin'.format(PYTHON, serial_port, VERSION)
            else:
                command = '{} deps/esptool.py --port {} --baud 115200 write_flash --flash_size=detect -fm dio 0 tmp/PythingsOS_{}_esp8266.bin'.format(PYTHON, serial_port, VERSION)

    elif chip_type == 'esp32':
        command = '{} deps/esptool.py --chip esp32 --port {} write_flash -z 0x1000 tmp/esp32-20181105-v1.9.4-683-gd94aa577a.bin'.format(PYTHON, serial_port)  
    else:
        abort('Consistency Exception')
        
    print('Flashing firmware... (about a minute)')
    if not(os_shell(command, interactive=INTERACTIVE, silent=SILENT)):
        abort('Error (see output above)')
    time.sleep(5)
    print('Done.')
    print('')
         
    # Step 3: Check ampy and successful MicroPython install
    if chip_type != 'esp8266':
        print('Checking...')
        if not os_shell('{} deps/ampy.py -p {} ls'.format(PYTHON, serial_port), interactive=INTERACTIVE, silent=SILENT):
            abort('Error (see output above)')
        time.sleep(2)
        print('Done.')
        print('')

if (copy and chip_type!='esp8266') or operation == 2:
    
    # Step 3: Download and extract PythingsOS
    print('Downloading PythingsOS...')
    url = '{}/static/PythingsOS/zips/PythingsOS_{}_{}.zip'.format(HOST,VERSION,VERSION,chip_type)
    #print ('Downloading {}'.format(url))
    download(url, 'tmp/')
    print('Done.')
    print('')    
    
    # (now extract)
    zip_ref = zipfile.ZipFile('tmp/PythingsOS_{}_{}.zip'.format(VERSION,chip_type), 'r')
    zip_ref.extractall('tmp/extracted')
    zip_ref.close()
    
    # Step 4: Copy over all files
    files_path = 'tmp/extracted/{}'.format(chip_type)
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
    print('Now resetting the device...')
 
    # Step 5: Reset
    time.sleep(2)
    if not os_shell('{} deps/ampy.py -p {} reset'.format(PYTHON, serial_port,files_path,file), interactive=INTERACTIVE, silent=SILENT):
        abort('Error (see output above)')
    time.sleep(2)
    print('Done.')
    print('')
   

    

if console:

    print('Now opening a serial connection...')
    print('The output you will see below is from PythingsOS running on your device!')
    print('  - Hit ctrl-C to exit.')
    print('  - Try press the reset button on your device if you don\'t see anything.')
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

print('')
print('Press any key to exit')
input()

