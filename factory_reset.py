
import os
def factory_reset():
    try:
        os.stat('/last')
    except OSError:
        print('Software is already to the factory version')
    else:
        for file in os.listdir('/last'):
            filepath = '/last/'+file
            print('Removing', filepath)
            os.remove(filepath)
        print('Removing "/last" directory')
        os.rmdir('/last')