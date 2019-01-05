import sys
import glob
import serial
import subprocess
import time
from collections import namedtuple

def serial_ports():
    """ Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
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



#========================
#  Main
#========================

# Ask for serial ports
print('Please select serial port:')
#print(serial_ports())
serial_port='/dev/cu.SLAB_USBtoUART'
print('Using "{}'.format(serial_port))
 
# Step 1: Erease flash
print('Erasing flash... (about 10 secs)')
os_shell('source venv/bin/activate && esptool.py --port {} erase_flash'.format(serial_port), interactive=True)
time.sleep(3)

# Step 2: Flash MicroPython firmware
print('Flashing firmware... (about a minute)')
os_shell('source venv/bin/activate && esptool.py --chip esp32 -p /dev/tty.SLAB_USBtoUART write_flash -z 0x1000 esp32-20181105-v1.9.4-683-gd94aa577a.bin'.format(serial_port), interactive=True)
time.sleep(5)
 
# Step 3: Check ampy and successful MicroPython install
print('Checking...')
os_shell('source venv/bin/activate && ampy -p {} ls'.format(serial_port), interactive=True)
time.sleep(2)

# Step 4: Copy over all files
files_path = '../../esp32'
from os import listdir
from os.path import isfile, join
files = [f for f in listdir(files_path) if isfile(join(files_path, f))]

for file in files:
    if file.endswith('.py'):
        print('Now copying {}/{} ...'.format(files_path,file))
        os_shell('source venv/bin/activate && ampy -p {} put {}/{}'.format(serial_port,files_path,file), interactive=True)
        time.sleep(2)


# Step 5: Reset and show outout
os_shell('source venv/bin/activate && ampy -p {} reset'.format(serial_port,files_path,file), interactive=True)

try:
    with serial.Serial(serial_port, 115200, timeout=1) as ser:
        while True:
            # Read a '\n' terminated line
            line = ser.readline()
            # Check if it is valid
            if valid(line):
                print(line[:-1])
except serial.serialutil.SerialException:
    raise
    # print('Cannot open serial port')



