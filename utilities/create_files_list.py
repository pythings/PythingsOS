from os import listdir, stat
from os.path import isfile, join

for file in listdir('./'):
    if file!='version' and file != '.gitignore': # Skip gitignore and do version as last (see next block)
        if not isfile(file):
            continue
        else:
            print 'file:{}:{}'.format(stat(file).st_size,file)

for file in listdir('./'):
    if file=='version':
        if not isfile(file):
            continue
        else:
            print 'file:{}:{}'.format(stat(file).st_size,file)
