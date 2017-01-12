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
    """

    base_queries = {
        'ident': QueryString('identification', '*IDN', 100),
        'event_status_enable': QueryString('event_status_enable', '*ESE'),
        'event_status_register': QueryString('event_status_register', '*ESR'),
        'operation_complete': QueryString('operation_complete', '*OPC'),
        'options': QueryString('options', '*OPT'),
        'service_request_enable': QueryString('service_request_enable', '*SRE'),
        'read_status_byte': QueryString('read_status_byte', '*STB'),
        'self_test': QueryString('self_test', '*TST')
    }

    base_commands = {
        'clear': CommandString('clear', '*CLS'),
        'event_status_enable': CommandString('event_status_enable', '*ESE'),
        'operation_complete': CommandString('operation_complete', '*OPC'),
        'recall_instrument_setting': CommandString('recall_instrument_setting', '*RCL'),
        'reset': CommandString('reset', '*RST'),
        'save': CommandString('save', '*SAV'),
        'service_request_enable': CommandString('service_request_enable', '*SRE'),
        'wait': CommandString('wait', '*WAI')
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

        self._init_query()
        self._init_command()

    def _init_query(self):
        """Initialize base and class queries."""
        for query in self.base_queries.values():
            self.query.add_command(query)

        for query in self.queries.values():
            self.query.add_command(query)

    def _init_command(self):
        """Initialize base and class commands."""
        for command in self.base_commands.values():
            self.command.add_command(command)

        for command in self.commands.values():
            self.command.add_command(command)

    def add_query(self, query):
        """
        Attach a query method to the query attribute object.

        Args:
            query: The QueryString instance holding the relevant state values

        """
        def _query(self, query, n=100):
            self.write(query.command)
            return self.read(n)

        setattr(self.query, query.name, _query)

    def add_command(self, command):
        """
        Attach a command method to the command attribute object.

        Args:
            command: The CommandString instnce holding the relevant state
                values

        """
        def _command(self, command, *args):
            self.write(command.command + " ".join([str(r) for r in args]))

        setattr(self.command, command.name, _command)

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
            self.name = ident
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
