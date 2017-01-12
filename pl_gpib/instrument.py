"""
GPIB Instrument Module.

All interfaced instruments should be a subclassed instance of this general
Instrument class.
"""
from pl_gpib.commands import QueryString, CommandString, CommandContainer


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
        query: An object holding supported query commands
        command: An object holding supported commands
        queries: Any class level query definitions are to be read from here
        base_queries: The common queries available to all instruments
        base_commands: The common commands available to all instruments.

    Notes:
        The commands and queries dict structure should be of the following form:

        commands = {
            'command_a': '*CMDA',
            'command_b': '*CMDB'
        }

        queries = {
            'query_a': '*CMDA',
            'query_b': {'cmd': '*CMDB', read_bytes: 1024}
        }

        where the dict key is the name to use and the value is either a string
        of the command text to use, or a dict with the following keys:

            *cmd*
            *read_bytes*

        Read_bytes is used by the query read function to read back an
        expected number of bytes from the query operation.
    """

    base_queries = {
        'ident': '*IDN',
        'event_status_enable': '*ESE',
        'event_status_register': '*ESR',
        'operation_complete': '*OPC',
        'options': '*OPT',
        'service_request_enable': '*SRE',
        'read_status_byte': '*STB',
        'self_test': '*TST'
    }

    base_commands = {
        'clear': '*CLS',
        'event_status_enable': '*ESE',
        'operation_complete': '*OPC',
        'recall_instrument_setting': '*RCL',
        'reset': '*RST',
        'save': '*SAV',
        'service_request_enable': '*SRE',
        'wait': '*WAI'
    }

    queries = {}
    commands = {}

    def __init__(self, address=None, name=None, connection=None):
        """Constructor method.

        Keyword Args:
            address: The GPIB address the instrument is currently configured
            name: An optional name to set for the instrument.  Defaults to
                the value from the initial ident command.
            connection: Assign the connection object at instantiation.
        """
        self.address = address
        self.name = name
        self.connection = connection
        self.query = CommandContainer(self)
        self.command = CommandContainer(self)

        self.init_commands()

    def init_commands(self):
        """Initialize base and class queries and commands."""
        self.query.add_commands(self.base_queries, query=True)
        self.query.add_commands(self.queries, query=True)

        self.command.add_commands(self.base_commands)
        self.command.add_commands(self.commands)

    def add_connection(self, connection):
        """
        Add a new controller connection to this instrument instance.

        Args:
            connection: The connection object to attach

        Returns:
            Boolean indicating connection was successful and identity was
                successfully queried.
        """
        self.connection = connection

        ident = self.query.ident()

        if ident is not None:
            self.name = ident.decode(self.connection.encoding)
            return True

        return False

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
