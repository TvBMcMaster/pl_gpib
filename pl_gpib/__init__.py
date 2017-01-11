"""pl_gpib.py -- Easy OO Interface to working with Prologix GPIB-USB Controller."""
import sys
import serial
__version__ = 0.1
__author__ = "Tim van Boxtel"


#
#  Module Exceptions
#

class BaseGPIBError(Exception):
    """The core Error class for this module."""

    pass


class GPIBAddressInUseError(BaseGPIBError):
    """
    GPIB Address is already in use.

    Thrown when Address is already configured for a controller.
    """

    pass


class UnconnectedInstrumentError(BaseGPIBError):
    """
    Unconnected Instrument.

    Thrown by instrument instances that have not been attached to a
    connection yet a write command is attempted.
    """

    pass

#
# Module Core Objects
#


class GPIBController(object):
    """
    GPIB Controller Object.

    This class is the main interface to the Prologix device.  A serial
    connection is opened and queried for sanity.

    The class allows for many instruments to be added.  Each instrument must
    be a subclass of the GPIBInstrument object.
    """

    lineending = '\n'

    def __init__(self, port, mode=None):
        """Constructor.  Creates the serial connection."""
        self.serial = serial.Serial(port=port, baudrate=115200, timeout=1)
        self.current_address = None  # Keep track of the instrument address
        self.instruments = {}  # Dict of connected instruments indexed by address

        mode = mode or 1  # Default CONTROLLER mode

        # Try to open the port, fail gracefully if not available
        try:
            self.serial.open()
        except serial.SerialException as e:
            print("Serial Connection Error: {}".format(str(e)))
            sys.exit(1)
        else:
            self.set_mode(mode)  # Default in controller mode
            self.query_address()

    def add_instrument(self, instrument, address):
        """Connect an instrument via its GPIB address."""
        address = int(address)
        if address in self.instruments:
            err_instrument = self.instruments[address]
            raise GPIBAddressInUseError("The GPIB address {} is already in use by {}".format(address, err_instrument))

        self.set_address(address)
        instrument.connection = self
        instrument.set_address(address)

        self.instruments[address] = instrument

        # Attempt an Ident Ping to the instrument, be sure to fail gracefully

    def write(self, command):
        """Write general command to device."""
        resp = self.serial.write(bytes(command + self.lineending))

        # TODO: Do we check right away for the read?
        return resp

    def read(self, n):
        """Read bytes from the serial connection."""
        self.write("++read eoi")
        read = self.serial.read(n).strip()
        return read

    def query_address(self):
        """Query the current GPIB address set on the controller."""
        self.write('++addr')
        address = int(self.read(10))
        self.current_address = address
        return address

    def set_address(self, address):
        """Set the current GPIB address of the controller."""
        address = int(address)
        self.write('++addr {}'.format(address))
        self.current_address = address

    def set_mode(self, mode):
        """Set the controller mode."""
        mode = int(mode)  # Force to int
        self.write("++mode {}".format(mode))


class GPIBInstrument(object):
    """
    Base GPIB Instrument Object.

    Intended to be extended on a per instrument basis.
    This object maintains the code to interface effectively with the GPIBController object.
    """

    ident_command = "*IDN?"

    def __init__(self, address=None, name=None, connection=None):
        """Constructor.  Able to set state data such as GPIB address."""
        self.address = address
        self.name = name
        self.connection = connection

    def write(self, command):
        """Write a string to the device."""
        if self.connection is not None:
            if self.address != self.connection.current_address:
                self.connection.set_address(self.address)
            self.connection.write(command)

    def set_address(self, address):
        """Set the address property of the instrument."""
        address = int(address)  # Force to int
        self.address = address

    def query_ident(self):
        """Query the Identity Command.  Typically *IDN?."""
        self.write(self.ident_command)
        resp = self.read(80)
        if resp is not None:
            self.name = resp

    def read(self, n):
        """Read from connected device."""
        if self.connection is not None:
            return self.connection.read(n)
