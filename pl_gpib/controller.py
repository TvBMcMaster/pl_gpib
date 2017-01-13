"""
GPIB Controller Module.

Contains the main `GPIBController` class.

Attributes:
    DEFAULT_ENCODING: The default encoding to use for communication
    DEFAULT_EOI: The default End or Identity (EOI) character to use
"""
import serial
from .exc import ERROR_MESSAGES, GPIBAddressInUseError
from .instrument import GPIBInstrument

DEFAULT_ENCODING = 'ascii'
DEFAULT_EOI = '\n'


class GPIBController(object):
    r"""
    GPIB Controller Object.

    This class is the main interface to the Prologix device.  A serial
    connection is opened and queried for sanity.

    The class allows for many instruments to be added.  Each instrument must
    be a subclass of the GPIBInstrument object.

    Args:
        port (str): The serial device port connected to the physical
            controller. `i.e.` '/dev/ttyUSB0' or 'COM1'

    Keyword Arguments:
        encoding (str): The default encoding to use for a command.  Defaults to
            'ascii'.
        eoi_char (str): The line ending character to use after each write
        connection (GPIBController): A connection to immediately attach to
            instrument
        mode (int): The mode to set on the controller.  Set 0 for *DEVICE*
            mode and 1 for *CONTROLLER* mode

    Raises:
        serial.SerialException:  When a problem opening the serial port has
            occurred.

    """

    def __init__(self, port, mode=None, connection=None, encoding=None, eoi_char=None):
        """Constructor method."""
        self.encoding = encoding or DEFAULT_ENCODING
        self.eoi_char = eoi_char or DEFAULT_EOI

        if connection is not None:
            self.serial = connection
        else:
            self.serial = serial.Serial(port=port, baudrate=115200, timeout=1)

            # May throw a `serial.SerialException` if there's a problem
            # self.serial.open()

        self.address = None  # Keep track of the instrument address
        self.mode = None  # Track the current mode setting of the device
        self.version = None
        self.instruments = {}  # Dict of connected instruments indexed by address

        self.query_version()

        if mode is not None:
            mode = int(mode)
        else:
            mode = 1

        self.set_mode(mode)

        self.query_address()

    def add_instrument(self, instrument, address=None):
        """
        Connect an instrument via its GPIB address.

        Calling this method sets the device address to the instrument and
        attempts to call the instrument for its ident ID.

        Args:
            instrument (GPIBInstrument): The instrument instance to initialize
            address (int): The GPIB address the instrument is set.  This is
                optional and will look at the instrument object itself if this
                attribute is not set upon calling.

        Raises:
            TypeError: When the instrument begin added is not a child of
                :py:class:`~pl_gpib.instrument.GPIBInstrument`.
            :py:class:`~pl_gpib.exc.GPIBAddressInUseError`: When an address is already configured
        """
        address = address or instrument.address
        assert address is not None
        if not isinstance(instrument, GPIBInstrument):
            raise TypeError("Instrument must be a child of GPIBInstrument")
        address = int(address)
        if address in self.instruments:
            err_instrument = self.instruments[address]
            err_text = "The GPIB address {} is already in use by {}".format(
                address,
                err_instrument
            )
            raise GPIBAddressInUseError(err_text)

        if address != instrument.address:
            instrument.set_address(address)

        if instrument.add_connection(self):
            self.instruments[address] = instrument

    def write(self, command, encoding=None):
        """
        Write general command to device.

        Args:
            command (str): The command to write
            encoding (str): Optional encoding to use for the command.
                Defaults to the attribute `encoding` on this class.

        """
        encoding = encoding or self.encoding
        self.serial.write(bytes(command + self.eoi_char, encoding))

    def read(self, n):
        """
        Read bytes from the serial connection.

        Args:
            n (int): Number of bytes to read.

        Raises:
            :py:class:`~pl_gpib.exc.GPIBCommandError`: When any of the
                expected error strings are read back from the device.
        Returns:
            str: The value read from the device

        """
        self.write("++read eoi")
        resp = self.serial.read(n).strip()

        if resp in ERROR_MESSAGES:
            err = ERROR_MESSAGES[resp]
            raise err()

        return resp

    def readline(self):
        """
        Read until line end indicated from device.

        This is nice that it does not require the user to think about the
        approximate size of the result.  The drawback is that the result is
        read one byte at a time, which can pollute debug logs.

        For now, I think I prefer to readout more bytes than I need, knowing
        the read will terminate at the same line ending characters that
        `readline` will look for.

        Raises:
            :py:class:`~pl_gpib.exc.GPIBCommandError`: When any of the
                expected error strings are read back from the device.

        Returns:
            str: The line read from the device

        """
        self.write("++read eoi")

        resp = self.serial.readline()

        if resp in ERROR_MESSAGES:
            err = ERROR_MESSAGES[resp]
            raise err()

        return resp.strip()

    def query_address(self):
        """
        Query the current GPIB address set on the controller.

        Returns:
            int: The address currently set on the controller or None
        """
        self.write('++addr')
        address = self.read(10)
        if address is not None:
            address = int(address)
            self.address = address
        return address

    def set_address(self, address):
        """
        Set the current GPIB address of the controller.

        Args:
            address (int):  The address to set, must be convertable to an
                integer
        """
        address = int(address)  # This forces only primary addresses
        self.write('++addr {}'.format(address))
        self.address = address

    def query_mode(self):
        """
        Query the controller mode.

        The controller mode is gives as:

        +------------+--------+
        |  Mode      |  Value |
        +============+========+
        | DEVICE     | 0      |
        +------------+--------+
        | CONTROLLER | 1      |
        +------------+--------+

        Returns:
            (int) The current mode of the controller

        """
        self.write('++mode')
        mode = self.read(1)
        if mode is not None:
            mode = int(mode)
            self.mode = mode
        return mode

    def set_mode(self, mode):
        """
        Set the controller mode.

        +------------+--------+
        |  Mode      |  Value |
        +============+========+
        | DEVICE     | 0      |
        +------------+--------+
        | CONTROLLER | 1      |
        +------------+--------+

        Args:
            mode (int): The mode to set the device.

        """
        mode = int(mode)  # Force to int
        self.write("++mode {}".format(mode))
        self.mode = mode

    def query_version(self):
        """
        Query the device version.

        Returns:
            (str): The version string returned from the controller
        """
        self.write("++ver")
        resp = self.read(100)
        if resp is not None:
            self.version = resp.decode(self.encoding)
        return resp
