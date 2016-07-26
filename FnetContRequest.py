#!/usr/bin/env python

import os
import re
import time
import requests

BASE = 'http://www.fnet.bosai.go.jp/auth/dataget/'
DATAGET = BASE + 'cgi-bin/dataget.cgi'
DATADOWN = BASE + 'dlDialogue.php'
auth = ('username', 'password')

data = {
    'format': 'SEED',
    'archive': 'zip',
    'station': 'ALL',
    'component': 'BHZ',
    'time': 'UT',
    's_year': '2016',
    's_month': '01',
    's_day': '01',
    's_hour': '00',
    's_min': '00',
    's_sec': '00',
    'end': 'duration',
    'sec': '300',
}

# post data request
r = requests.post(DATAGET, auth=auth, data=data)

# extract data id
id = re.search(r'dataget\.cgi\?data=(NIED_\d+\.zip)&', r.text).group(1)

# check if data preparation is done
requests.get(DATAGET + "?data=" + id, auth=auth)

# download data
r = requests.get(DATADOWN + '?_f=' + id, auth=auth, stream=True)
total_length = int(r.headers.get('Content-Length'))
fname = "test.zip"
with open(fname, "wb") as fd:
    for chunk in r.iter_content(1024):
        fd.write(chunk)

if os.path.getsize(fname) != total_length:
    sys.exit("error")
