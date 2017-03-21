#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
from os import path
from codecs import open
from setuptools import setup, find_packages

here = path.abspath(path.dirname(__file__))

# get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

# get version number from __init__.py
# https://github.com/kennethreitz/requests/blob/master/setup.py#L52
with open('FnetPy/__init__.py', 'r') as fd:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                        fd.read(), re.MULTILINE).group(1)

setup(
    name='FnetPy',
    version=version,
    description='A NIED F-net web service client',
    long_description=long_description,
    url='https://github.com/seisman/FnetPy',
    author='Dongdong Tian',
    author_email='seisman.info@gmail.com',
    keywords='Seismology, NIED, F-net, Waveform',
    license='MIT',

    packages=find_packages(exclude=[]),
    install_requires=['requests'],
    extras_require={
        'dev': [
        ]
    },

    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Scientific/Engineering :: Physics',
        'Topic :: Utilities',
    ],
)
