import os

def uninstall(path=''):   
    print (path+'/files.txt')
    files_list = open(path+'/files.txt')
    
    for item in files_list.read().split('\n'):
        if 'file:' in item:
            filename=item.split(':')[2]
            if filename=='app.py': continue
            fullfilename=path+'/'+filename
            print('Removing', fullfilename)
            try: os.remove(fullfilename)
            except: pass
    files_list.close()
    try: os.remove(path+'/app.py')
    except: pass
    try: os.remove(path+'/app_bk.py')
    except: pass
    try: os.remove(path+'/app_bk.py')
    except: pass
    try: os.remove(path+'/settings.json')
    except: pass
    try: os.remove(path+'/settings_bk.json')
    except: pass
    if path != '/':
        try: os.remove(path)
        except: pass

if __name__ == "__main__":
    uninstall()
