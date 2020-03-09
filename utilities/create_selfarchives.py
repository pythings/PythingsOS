from os import listdir, stat
from os.path import isfile, join, exists
from os import makedirs

# Now prepare installer

def sanitize(text):
    return text.replace('\\','\\\\')
            
platforms = ['esp8266', 'esp8266_sim800']

for platform in platforms:
    print(' Generating self extracting archive for platform "{}"...'.format(platform))
    dir = 'artifacts/selfarchives/' + platform
    if not exists(dir):
        makedirs(dir)
 
    with open( dir + '/selfarchive.py','w') as installer:
        
        # Init installer code
        installer.write('''
import os

def install(path='/'):
    try:
        os.stat(path+'initialized')
        return
    except:
        pass
''')
          
        for source_file in listdir(platform):
            if source_file == 'selfarchive.py':
                continue
            try:
                if source_file.split('.')[1] == 'pyc':
                    continue
            except:
                pass
            
            
            
            with open(platform+'/'+source_file,'r') as source:

                content = source.read()
                #print('Processing ', source_file)
                #print(len(content))
                if len(content) > 3000:
                    content1=content[0:3000]
                    content2=content[3000:]
                else:
                    content1=content
                    content2=''

                # Add this file contents to the installer
                installer.write('''
    print('[INFO] Initializing',path+'/{0}')
    with open(path+'/{0}','w') as f:
        f.write(\'\'\'{1}\'\'\')
        f.write(\'\'\'{2}\'\'\')
'''.format(source_file,sanitize(content1),sanitize(content2)))

        # Add initialized file and initializer
        installer.write('''
    with open(path+'/initialized','w') as f:
        f.write('')

install()
            
    ''')























