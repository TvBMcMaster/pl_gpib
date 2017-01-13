"""Easy Python interface for working with a Prologix GPIB-USB Controller."""
import os
from .controller import GPIBController
from .instrument import GPIBInstrument


with open(os.path.join(os.path.dirname(__file__), os.pardir, 'VERSION')) as version_file:
    version = version_file.read().strip()

__version__ = version
__author__ = "Tim van Boxtel"
