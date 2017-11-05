#!/usr/bin/env python
# -*- coding: utf-8 -*-
 
from distutils.core import setup

import FGPIO
 
setup(
    name='FGPIO',
    version=FGPIO.__version__,
    packages=['FGPIO'],
    author="FredThx",
    author_email="FredThx@gmail.com",
    description="A package for managing E/S of Raspberry pi or PCduino. Gestion des E/S d'un Raspberry PI ou d'un pcduino",
    long_description=open('README.md').read(),
    #install_requires=["smbus-cffi >= 0.4.1"],
    include_package_data=True,
    url='https://github.com/FredThx/FGPIO/archive/0.6.6.tar.gz',
    classifiers=[
        "Programming Language :: Python",
        "Development Status :: 4 - Beta",
        "License :: OSI Approved",
        "Natural Language :: French",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.7"
    ],
    # entry_points = {
        # 'console_scripts': [
            # 'proclame-sm = sm_lib.core:proclamer',
        # ],
    # },
    license="WTFPL",

)