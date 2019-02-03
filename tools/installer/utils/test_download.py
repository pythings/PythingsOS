


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

# MAIN
url = "https://pythings.io/static/dist/PythingsOS/v0.2/builds/PythingsOS_v0.2_Python.zip"
download(url)