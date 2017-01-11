"""
GPIB Controller Module.

Contains the main `GPIBController` class.
"""
import serial
from pl_gpib import DEFAULT_ENCODING, DEFAULT_EOI
import pl_gpib.exc as exc
from pl_gpib.instrument import GPIBInstrument


class GPIBController(object):
    r"""
    GPIB Controller Object.

    This class is the main interface to the Prologix device.  A serial
    connection is opened and queried for sanity.

    The class allows for many instruments to be added.  Each instrument must
    be a subclass of the GPIBInstrument object.

    Attributes:
        encoding: The default encoding to use for a command.  Defaults to
            'ascii'.
        eoi_char: The line ending character to use after each write command.
            Defaults to '\\n'.
        serial: The serial.Serial connection used for reading and writing to
            the device.
        address: The current address set on the controller
        mode: The current mode set on the controller
        instruments: A dict of connected instruments indexed by address number.
            The values are instances of GPIBInstrument subclasses.
        version:  The device version string.  Gets queried on each connection.

    """

    def __init__(self, port, mode=None, connection=None, encoding=None, eoi_char=None):
        """
        Constructor method.

        Args:
            port: The port to communicate with the serial device (ie
                '/dev/ttyUSB0' on Linux or 'COM1' on Windows).
            mode: Set the initial mode bit.  Accepts either 0 (DEVICE) or
                1 (CONTROLLER).  Defaults to 1.
            connection:  Optionally pass a serial object to communicate with.
                This is useful for implementing a serial spy to debug.
            encoding: Optional encoding to use for this device, defaults to module
                wide default.
            eoi_char: The character to use for indicating EOI.  Defaults to
                project wide defaults.

        Raises:
            serial.SerialException:  When a problem opening the serial port has
                occurred.
        """
        self.encoding = encoding or DEFAULT_ENCODING
        self.eoi_char = eoi_char or DEFAULT_EOI

        if connection is not None:
            self.serial = connection
        else:
            self.serial = serial.Serial(port=port, baudrate=115200, timeout=1)

            # May throw a `serial.SerialException` if there's a problem
            self.serial.open()

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

    def add_instrument(self, instrument, address):
        """
        Connect an instrument via its GPIB address.

        Calling this method sets the device address to the instrument and
        attempts to call the instrument for its ident ID.

        Args:
            instrument: The instrument instance to initialize
            address: The GPIB address the instrument is set

        Raises:
            TypeError: When the instrument begin added is not a child of
                `GPIBInstrument`.
            GPIBAddressInUseError: When an address is already configured
        """
        if not isinstance(instrument, GPIBInstrument):
            raise TypeError("Instrument must be a child of GPIBInstrument")
        address = int(address)
        if address in self.instruments:
            err_instrument = self.instruments[address]
            err_text = "The GPIB address {} is already in use by {}".format(
                address,
                err_instrument
            )
            raise exc.GPIBAddressInUseError(err_text)

        self.set_address(address)
        instrument.connection = self
        instrument.set_address(address)

        self.instruments[address] = instrument

        # Attempt an Ident Ping to the instrument, be sure to fail gracefully
        return instrument.query_ident()

    def write(self, command, encoding=None):
        """
        Write general command to device.

        Args:
            command: The command to write
            encoding: Optional encoding to use for the command.  Defaults to
                the attribute `encoding` on this class.

        """
        encoding = encoding or self.encoding
        self.serial.write(bytes(command + self.eoi_char, encoding))

    def read(self, n):
        """
        Read bytes from the serial connection.

        Args:
            n: An integer number of bytes to read.

        Raises:
            GPIBCommandError: When any of the expected error strings are read
                back from the device.
        Returns:
            The string read from the device
        """
        self.write("++read eoi")
        resp = self.serial.read(n).strip()

        if resp in exc.ERROR_MESSAGES:
            err = exc.ERROR_MESSAGES[resp]
            raise err()

        return resp

    def readline(self):
        """
        Read until line ending from device.

        This is nice that it does not require the user to think about the
        approximate size of the result.  The drawback is that the result is
        read one byte at a time, which can pollute debug logs.

        For now, I think I prefer to readout more bytes than I need, knowing
        the read will terminate at the same line ending characters that
        `readline` will look for.

        Raises:
            GPIBCommandError: When any of the expected error strings are read
                back from the device.

        Returns:
            The lines read from the device
        """
        self.write("++read eoi")

        resp = self.serial.readline()

        if resp in exc.ERROR_MESSAGES:
            err = exc.ERROR_MESSAGES[resp]
            raise err()

        return resp.strip()

    def query_address(self):
        """
        Query the current GPIB address set on the controller.

        Returns:
            The integer address currently set on the controller or None
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
            address:  The address to set, must be convertable to an integer
        """
        address = int(address)  # This forces only primary addresses
        self.write('++addr {}'.format(address))
        self.address = address

    def query_mode(self):
        """
        Query the controller mode.

        DEVICE: 0
        CONTROLLER: 1

        Returns:
            The mode integer the device is currently set as.  0 or 1
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

        DEVICE: 0
        CONTROLLER: 1

        Args:
            mode: The integer mode to set the device.

        """
        mode = int(mode)  # Force to int
        self.write("++mode {}".format(mode))
        self.mode = mode

    def query_version(self):
        """
        Query the device version.

        Returns:
            The version string
        """
        self.write("++ver")
        resp = self.read(100)
        if resp is not None:
            self.version = resp.decode(self.encoding)
        return resp
