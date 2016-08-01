#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Author: Dongdong Tian @ USTC
#

"""Request continuous waveform data from NIED F-net.
"""

import os
import re
import sys
import time
import requests

from docopt import docopt

BASE = 'http://www.fnet.bosai.go.jp/auth/dataget/'
DATAGET = BASE + 'cgi-bin/dataget.cgi'
DATADOWN = BASE + 'dlDialogue.php'
auth = ('username', 'password')

if len(sys.argv) != 8:
    sys.exit("Usage: python %s year month day hour min sec duration" % sys.argv[0])

year, month, day, hour, min, sec, duration = sys.argv[1:]

data = {
    'format': 'SEED',
    'archive': 'zip',
    'station': 'ALL',
    'component': 'BHZ',
    'time': 'UT',
    's_year': year,
    's_month': month,
    's_day': day,
    's_hour': hour,
    's_min': min,
    's_sec': sec,
    'end': 'duration',
    'sec': duration,
}

# post data request
r = requests.post(DATAGET, auth=auth, data=data)
if r.status_code == 401:
    sys.exit("Error in username or password!")

# extract data id
m = re.search(r'dataget\.cgi\?data=(NIED_\d+\.zip)&', r.text)
if m:
    id = m.group(1)
else:
    sys.exit("Error in parsing HTML!")

# check if data preparation is done
r = requests.get(DATAGET + "?data=" + id, auth=auth)

# download data
r = requests.get(DATADOWN + '?_f=' + id, auth=auth, stream=True)
total_length = int(r.headers.get('Content-Length'))
fname = "test.zip"
with open(fname, "wb") as fd:
    for chunk in r.iter_content(1024):
        fd.write(chunk)

if os.path.getsize(fname) != total_length:
    sys.exit("error")
