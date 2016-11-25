import os
def rmdir(dir):
    for file in os.listdir(dir):
        os.remove(dir+'/'+file)
    os.rmdir(dir)
#rmdir('yourdir')