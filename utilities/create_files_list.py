from os import listdir, stat
from os.path import isfile, join

ignored=['websetup.html', 'jquery.js']

for file in listdir('./'):
    if file!='version.py' and file[0] != '.' and file not in ignored: 
        if not isfile(file):
            continue
        else:
            print 'file:{}:{}'.format(stat(file).st_size,file)

# Do version as last
for file in listdir('./'):
    if file=='version.py':
        if not isfile(file):
            continue
        else:
            print 'file:{}:{}'.format(stat(file).st_size,file)
