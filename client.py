# -*- coding: utf-8 -*-

"""Request continuous waveform data from NIED F-net.
"""

import io
import os
import re
import sys
import zipfile
import requests


class Client(object):
    FNET = 'http://www.fnet.bosai.go.jp/auth/dataget/'
    DATAGET = FNET + 'cgi-bin/dataget.cgi'
    DATADOWN = FNET + 'dlDialogue.php'

    def __init__(self, user=None, password=None, timeout=120):
        self.timeout = timeout
        if user and password:
            self.login(user, password)

    def login(self, user, password):
        self.session = requests.Session()
        self.session.auth = (user, password)

    def get_waveform(self, starttime, duration,
                     format='SEED', archive='ZIP',
                     station='ALL',
                     component='BH?',
                     time='UT'):

        if int(starttime.strftime("%Y")) < 1995:
            raise ValueError("No data avaiable before year 1995.")

        data = {
            's_year': starttime.strftime("%Y"),
            's_month': starttime.strftime("%m"),
            's_day': starttime.strftime("%d"),
            's_hour': starttime.strftime("%H"),
            's_min': starttime.strftime("%M"),
            's_sec': starttime.strftime("%S"),
            'end': 'duration',
            'sec': duration,
            'format': format,
            'archive': 'ZIP',  # alawys use ZIP format
            'station': station,
            'component': component,
            'time': time,
        }
        print(data)

        r = self.session.post(self.DATAGET, auth=("seisman", "seismanustc"), data=data)
        if r.status_code == 401:  # username is right, password is wrong
            sys.exit("Unauthorized! Please check your username and password!")
        elif r.status_code == 500:  # internal server error, or username is wrong
            sys.exit("Internal server error! Or you're using the wrong username!")
        elif r.status_code != 200:
            sys.exit("Something wrong happened! Status code = %d" % (r.status_code))

        print(r.text)
        # extract data id
        m = re.search(r'dataget\.cgi\?data=(NIED_\d+\.zip)&', r.text)
        if m:
            id = m.group(1)
        else:
            sys.exit("Error in parsing HTML!")

        # check if data preparation is done
        r = self.session.get(self.DATAGET + "?data=" + id, auth=self.auth)

        # download data
        r = self.session.get(self.DATADOWN + '?_f=' + id, auth=self.auth, stream=True)
        if r.text == 'Could not open your requested file.':
            sys.stderr.write(r.text + '\n')
            sys.stderr.write("Possible reasons:\n"
                             "1. Something wrong happened to the Fnet server.\n"
                             "2. No data avaiable in your requested time range.\n"
                             "3. Multiple requests at the same time.\n")
            sys.exit()

        z = zipfile.ZipFile(io.BytesIO(r.content))
        for f in z.filelist:
            root, ext = os.path.splitext(f.filename)
            if ext == '.log':
                continue
            if data['format'] == 'SEED':
                f.filename = "%s.%s".format(starttime.strftime("%Y%m%d%H%M%S"), ext)
                z.extract(f)
            elif data['format'] in ['MSEED', 'SAC', 'TEXT']:
                z.extract(f)
