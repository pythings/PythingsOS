import globals
from utils import mv
from http import download

def update_app(version):
    mv('/app.py','/app_bk.py')
    if not download('{}/api/v1/apps/get/?version={}&token={}'.format(globals.pythings_host, version, globals.token), '/app.py'):
        raise Exception('App download failed')
