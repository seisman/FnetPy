# -*- coding: utf-8 -*-

"""Request continuous waveform data from NIED F-net.
"""

import io
import os
import re
import sys
import zipfile
import certifi
import requests
from requests.adapters import HTTPAdapter
from urllib3 import PoolManager
from urllib3.util import create_urllib3_context


# Hacking solution for "ssl.SSLError: [SSL: DH_KEY_TOO_SMALL] dh key too small" error.
# Reference: https://stackoverflow.com/a/76217135
class AddedCipherAdapter(HTTPAdapter):
    def init_poolmanager(self, connections, maxsize, block=False):
        ctx = create_urllib3_context(ciphers=":HIGH:!DH:!aNULL")
        self.poolmanager = PoolManager(
            num_pools=connections, maxsize=maxsize, block=block, ssl_context=ctx
        )

class Client():
    """Client for F-net server."""
    FNET = "https://www.fnet.bosai.go.jp/auth/dataget/"
    DATAGET = FNET + "cgi-bin/dataget.cgi"
    DATADOWN = FNET + "dlDialogue.php"

    def __init__(self, user, password, timeout=120):
        self.session = requests.Session()
        self.session.mount(self.DATAGET, AddedCipherAdapter())
        self.session.mount(self.DATADOWN, AddedCipherAdapter())
        self.session.auth = (user, password)
        self.timeout = timeout

    def get_waveform(
            self,
            starttime,
            duration_in_seconds,
            format="SEED",
            station="ALL",
            component="BHX",
            time="UT",
            filename=None,
    ):
        """Get waveform data from NIED F-net."""

        if starttime.year < 1995:
            raise ValueError("No data avaiable before year 1995.")

        # check data format
        if format not in ["SEED"]:
            raise ValueError("Data format error, currently only support SEED.")

        # BH? => BHX
        component = component.replace("?", "X")

        data = {
            "s_year": starttime.strftime("%Y"),
            "s_month": starttime.strftime("%m"),
            "s_day": starttime.strftime("%d"),
            "s_hour": starttime.strftime("%H"),
            "s_min": starttime.strftime("%M"),
            "s_sec": starttime.strftime("%S"),
            "end": "duration",
            "sec": duration_in_seconds,
            "format": format,
            "archive": "zip",  # alawys use ZIP format
            "station": station,
            "component": component,
            "time": time,
        }

        r = self.session.post(self.DATAGET, auth=self.session.auth, data=data, verify=certifi.where())
        if r.status_code == 401:  # username is right, password is wrong
            sys.exit("Unauthorized! Please check your username and password!")
        elif r.status_code == 500:  # internal server error, or username is wrong
            sys.exit("Internal server error! Or you're using the wrong username!")
        elif r.status_code != 200:
            sys.exit("Something wrong happened! Status code = %d" % (r.status_code))

        # extract data id
        m = re.search(r"dataget\.cgi\?data=(NIED_\d+\.zip)&", r.text)
        if m:
            data_id = m.group(1)
        else:
            sys.stderr.write(r.text)
            sys.exit("Error in parsing HTML!")

        # check if data preparation is done
        r = self.session.get(self.DATAGET + "?data=" + data_id,
                             auth=self.session.auth)
        if "Our data server is very busy now." in r.text:
            sys.stderr.write("Something wrong with the F-net server.\n")
            return None

        # download data
        r = self.session.get(
            self.DATADOWN + "?_f=" + data_id, auth=self.session.auth, stream=True
        )
        if r.text == "Could not open your requested file.":
            sys.stderr.write(r.text + "\n")
            sys.stderr.write(
                "Possible reasons:\n"
                "1. Something wrong happened to the Fnet server.\n"
                "2. No data avaiable in your requested time range.\n"
                "3. Multiple requests at the same time.\n"
            )
            return None

        if not filename:
            filename = starttime.strftime("%Y%m%d%H%M%S") + ".SEED"
        dirname = os.path.dirname(filename)

        z = zipfile.ZipFile(io.BytesIO(r.content))
        for f in z.filelist:
            ext = os.path.splitext(f.filename)[1]
            if ext.lower() == '.seed' and f.file_size != 0:
                if dirname and not os.path.exists(dirname):
                    os.makedirs(dirname, exist_ok=True)
                f.filename = filename
                z.extract(f)
                return f.filename
            else:
                return None
