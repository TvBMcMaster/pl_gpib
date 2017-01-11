"""
GPIB Instrument Module.

All interfaced instruments should be a subclassed instance of this general
Instrument class.
"""

from pl_gpib import DEFAULT_IDENT_COMMAND


class GPIBInstrument(object):
    """
    Base GPIB Instrument Object.

    Intended to be extended on a per instrument basis.
    This object maintains the code to interface effectively with the GPIBController object.

    Attributes:
        address: The GPIB Address for this instrument
        name: The ID name of the instrument
        connection: The connection object to read / write data to the
            instrument.
    """

    def __init__(self, address=None, name=None, connection=None, ident_command=None):
        """Constructor method.

        Args:
            address: The GPIB address the instrument is currently configured
            name: An optional name to set for the instrument.  Defaults to
                the value from the ident command.
            connection: Assign the connection object at instantiation.
            ident_command: Instrument specific ident command.  Defaults to
                project wide default

        """
        self.address = address
        self.name = name
        self.connection = connection
        self.ident_command = ident_command or DEFAULT_IDENT_COMMAND

    def write(self, command):
        """
        Write a string to the device.

        Args:
            command: The command string to write.

        """
        if self.connection is not None:
            if self.address != self.connection.address:
                self.connection.set_address(self.address)
            self.connection.write(command)

    def set_address(self, address):
        """
        Set the address property of the instrument.

        Args:
            address: The GPIB address to assign to the instrument.  Must be
                able to be represented as an integer.

        """
        address = int(address)  # Force to int
        self.address = address

    def query_ident(self):
        """
        Query the Identity Command.

        Returns:
            The declared identity of this instrument.
        """
        self.write(self.ident_command)
        resp = self.readline()
        if resp is not None:
            self.name = resp
        return resp

    def read(self, n):
        """
        Read bytes from connected device.

        If stop bit is encountered before number of bytes is reached, read is
        ended early.

        Args:
            n: The integer number of bytes to read from the device.

        Returns:
            The decoded bytestring read from the device.
        """
        if self.connection is not None:
            return self.connection.read(n)

    def readline(self):
        """
        Read a line from the connected device.

        Returns:
            The decoded bytestring read from the device
        """
        if self.connection is not None:
            return self.connection.readline()
