"""
GPIB Instrument Module.

All interfaced instruments should be a subclassed instance of this general
Instrument class.
"""
from pl_gpib.commands import CommandContainer


class GPIBInstrument(object):
    """
    Base GPIB Instrument Object.

    Intended to be extended on a per instrument basis.
    This object maintains the code to interface effectively with the
    :py:class:`pl_gpib.controller.GPIBController` object.

    Attributes:
        queries (dict): Any class level query definitions are to be read from
            here
        commands (dict):  Any class level command definitions are to be defined here.
        base_queries (dict): The common queries available to all instruments
        base_commands (dict): The common commands available to all instruments.

    Notes:
        The commands and queries dict structure should be of the following form:

        .. code-block: python
            commands = {
                'command_a': '\*CMDA',
                'command_b': '\*CMDB'
            }

            queries = {
                'query_a': '\*CMDA',
                'query_b': ['\*CMDB',  1024]
            }

        where the dict key is the name to use and the value is either a string
        of the command text to use, or a list of arguments to pass to the
        :py:class:`pl_gpib.commands.QueryString` object.:

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
            address (int): The GPIB address the instrument is currently
                configured
            name (str): An optional name to set for the instrument.
                Defaults to the value from the initial ident command.
            connection (GPIBController): Assign the connection object at
                instantiation.
        """
        self.address = address
        self.name = name
        self.connection = connection
        self.query = CommandContainer(self)
        self.command = CommandContainer(self)

        self._init_commands()

    def _init_commands(self):
        """Initialize base and class queries and commands."""
        self.query.add_commands(self.base_queries, query=True)
        self.query.add_commands(self.queries, query=True)

        self.command.add_commands(self.base_commands)
        self.command.add_commands(self.commands)

    def add_connection(self, connection):
        """
        Add a new controller connection to this instrument instance.

        Args:
            connection (GPIBConnection): The connection object to attach

        Returns:
            bool: On successful ident return
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
            command (str): The command string to write.

        """
        if self.connection is not None:
            if self.address != self.connection.address:
                self.connection.set_address(self.address)
            self.connection.write(command)

    def set_address(self, address):
        """
        Set the address property of the instrument.

        Args:
            address (int): The GPIB address to assign to the instrument.

        """
        address = int(address)  # Force to int
        self.address = address

    def read(self, n):
        """
        Read bytes from connected device.

        If stop bit is encountered before number of bytes is reached, read is
        ended early.

        Args:
            n (int): The integer number of bytes to read from the device.

        Returns:
            bytes: The response read from the device.
        """
        if self.connection is not None:
            return self.connection.read(n)

    def readline(self):
        """
        Read a line from the connected device.

        Returns:
            bytes: The response read from the device
        """
        if self.connection is not None:
            return self.connection.readline()
