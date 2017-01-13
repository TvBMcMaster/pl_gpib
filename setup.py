#!/usr/bin/env python
"""Setup file for ph_gpib."""
import os
from distutils.core import setup

with open(os.path.join(os.path.dirname(__file__), 'VERSION')) as version_file:
    version = version_file.read().strip()

setup(name="Prologix GPIB USB Library",
      version=version,
      description='Interface with GPIB Instruments via Prologix USB Controller',
      author='Tim van Boxtel',
      author_email='vanboxtj@mcmaster.ca',
      packages=['pl_gpib'],
      install_requires=['PySerial']
      )
