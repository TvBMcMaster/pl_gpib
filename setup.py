#!/usr/bin/env python
"""Setup file for ph_gpib."""
from distutils.core import setup


setup(name="Prologix GPIB USB Library",
      version='0.1',
      description='Interface with GPIB Instruments via Prologix USB Controller',
      author='Tim van Boxtel',
      author_email='vanboxtj@mcmaster.ca',
      packages=['pl_gpib'],
      )
