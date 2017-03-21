# -*- coding: utf-8 -*-
"""
FnetPy
======

FnetPy is a F-net client, written in Python, for seismologists, to request 
seismic waveform data from F-net website.
"""

__title__ = "FnetPy"
__version__ = '0.1.0'
__author__ = 'Dongdong Tian'
__license__ = 'MIT'

from .client import Client

__all__ = ['Client']
