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

VERSION          = 'v1.0.0-rc1'
CHOOSE_OPERATION = False
INTERACTIVE      = False
DEBUG            = False
SILENT           = True
HOST = 'https://pythings.io'

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
        elif 'Version:' in line or 'System' in line or '|-------' in line or 'Starting' in line:
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
    string += sanitize_encoding(stdout)
    string += '"\n\nStandard error: "'
    string += sanitize_encoding(stderr) +'"\n\n'
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

print('')
print('-----------------------------------------------')
print('  Welcome to PythingsOS {} installer    '.format(VERSION))
print('-----------------------------------------------')

print('')
print('Notes:')
print(' - An Internet connection is required for downloading the required files.')
print(' - You need a working serial connection to your board.')
print(' - Most common USB-to-serial drivers here: /downloads.'.format(HOST))
print(' - Some chips require high quality USB cables, switch cable in case of problems.')
print(' - On Linux, run this program as root (i.e. "sudo installer.sh")')
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


if CHOOSE_OPERATION:
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
    print('Do you want a frozen or standard install?')
    print('Frozen = PythingsOS not updatable remotely,')
    print('         but more free memory for your App.')
    print('')
    print(' 1) Frozen')
    print(' 2) Standard')
    print('')
    #print(' 3) Raspberry PI')
    
    sys.stdout.write('Your choice (number): ')
    
    try:
        forzen_choice  = int(input())
    except:
        abort('Error, please type a valid numerical choice')

    if forzen_choice == 1:
        frozen = True
    elif forzen_choice == 2:
        frozen = False
    else:
        abort('Error, please type a valid choice')





# Ask for serial ports
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
print('Using "{}'.format(serial_port))
print('')


if flash:
    
    # Step 0: download firmware
    print('Downloading firmware...')
    if chip_type== 'esp8266':
        if frozen:
            download('{}/static/builds/PythingsOS_v1.0.0-rc1_esp8266.frozen.bin'.format(HOST), 'tmp/')
        else:
            download('{}/static/builds/PythingsOS_v1.0.0-rc1_esp8266.bin'.format(HOST), 'tmp/')
            
    elif chip_type == 'esp32':
        download('{}/static/firmware/esp32-20181105-v1.9.4-683-gd94aa577a.bin'.format(HOST), 'tmp/')
    else:
        abort('Consistency Exception')
    print('Done.')
    print('')
    
    # Step 1: Erease flash
    if chip_type== 'esp8266':
        command = 'python deps/esptool.py --port {} erase_flash'.format(serial_port)
    elif chip_type == 'esp32':
        command =  'python deps/esptool.py --port {} erase_flash'.format(serial_port)  
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
            command = 'python deps/esptool.py --port {} --baud 115200 write_flash --flash_size=detect -fm dio 0 tmp/PythingsOS_v1.0.0-rc1_esp8266.frozen.bin'.format(serial_port)
        else:
            command = 'python deps/esptool.py --port {} --baud 115200 write_flash --flash_size=detect -fm dio 0 tmp/PythingsOS_v1.0.0-rc1_esp8266.bin'.format(serial_port)

    elif chip_type == 'esp32':
        command = 'python deps/esptool.py --chip esp32 --port {} write_flash -z 0x1000 tmp/esp32-20181105-v1.9.4-683-gd94aa577a.bin'.format(serial_port)  
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
        if not os_shell('python deps/ampy.py -p {} ls'.format(serial_port), interactive=INTERACTIVE, silent=SILENT):
            abort('Error (see output above)')
        time.sleep(2)
        print('Done.')
        print('')

if (copy and chip_type!='esp8266') or operation == 2:
    
    # Step 3: Download and extract PythingsOS
    print('Downloading PythingsOS...')
    url = '{}/static/dist/PythingsOS/{}/zips/PythingsOS_{}_{}.zip'.format(HOST,VERSION,VERSION,chip_type)
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
                if not os_shell('python deps/ampy.py -p {} put {}/{}'.format(serial_port,files_path,file), interactive=INTERACTIVE, silent=SILENT):
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
    if not os_shell('python deps/ampy.py -p {} reset'.format(serial_port,files_path,file), interactive=INTERACTIVE, silent=SILENT):
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
                line = ser.readline()
                # Check if it is valid
                if valid(line):
                    print(line[:-1])
    except serial.serialutil.SerialException:
        raise
        # print('Cannot open serial port')

print('')
print('Press any key to exit')
input()

