"""pl_gpib.

Easy OO Interface to working with Prologix GPIB-USB Controller.

Attributes:
    DEFAULT_PORT: The default port to connect
    DEFAULT_ENCODING: The default module wide encoding to use
    DEFAULT_EOI: The default module wide EOI character to use
    DEFAULT_IDENT_COMMAND: The default module wide Ident command to use
"""
__version__ = 0.1
__author__ = "Tim van Boxtel"

DEFAULT_PORT = '/dev/ttyUSB0'
DEFAULT_ENCODING = 'ascii'
DEFAULT_EOI = "\n"
DEFAULT_IDENT_COMMAND = "*IDN?"

from .controller import GPIBController
from .instrument import GPIBInstrument
