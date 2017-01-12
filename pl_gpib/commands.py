"""
GPIB Commands Module.

Base objects of commands and queries.  Mainly used as state objects for now,
but functionality such as custom __call__ overrides might be useful.
"""
from types import MethodType


class CommandString(object):
    """
    Command String State Holder.

    Args:
        name: The name of the command
        command: The command text
    """

    def __init__(self, name, command):
        """Constructor."""
        self.name = name
        self.command_text = command

    def __call__(self, *args):
        """
        Construct the command text from called arguments.

        Simply converts all args to str and separates the command text plus
        args with spaces.

        Args:
            *args: Variable positional arguments to be formatted into the
                command text.

        """
        command_args = [self.command_text]
        command_args.extend([str(a) for a in args])
        return " ".join(command_args)


class QueryString(CommandString):
    """
    Class container of Query commands.

    A special case of CommandString where no commmand arguments are accepted
     and values are read back after the write.

    Args:
        name: The name of the command
        command: The command text
        read_bytes: Read this many bytes after issues the query.  Defaults to 100.
    """

    def __init__(self, *args, **kwargs):
        """Constructor."""
        args = list(args)
        if len(args) > 2:
            self.read_bytes = args.pop(2)
        else:
            self.read_bytes = 100

        super(QueryString, self).__init__(*args)

    def __call__(self):
        """
        Query Command String call method.

        Query command does not take any arguments and appends a '?' to the command text.
        """
        return self.command_text + '?'


class CommandContainer(object):
    """
    A Command Container object.  Useful for storing all command methods.

    Args:
        instrument: The parent instrument of the commands.
    """

    def __init__(self, instrument):
        """Constructor."""
        self.commands = {}
        self.instrument = instrument

    def add_commands(self, commands_dict, query=None):
        """
        Add command and query methods based on a dict of query data.

        Args:
            commands_dict:  A dict of command and query data.  Keys are the
            query name, and values are either a simple string of command text,
            or a list/tuple of extra data.

        Examples:

            q_data = {
                'query_a': ':QRYA',
                'query_b': (':QRYB', 200)
            }
            c.add_queries(q_data)

        """
        if query is True:
            Command = QueryString
        else:
            Command = CommandString

        for name, query_data in commands_dict.items():

            if isinstance(query_data, str):
                qry = Command(name, query_data)
            else:
                qry = Command(name, *query_data)

            self.add_command(qry)

    def add_command(self, command):
        """
        Add a new command to the container.

        Args:
            command: The CommandString instance of the command to add.
        """
        if command.name not in self.commands:
            self.commands[command.name] = command

            def wrapped(instrument, command):
                def wrapper(self, *args):
                    self.instrument.write(command(*args))
                    if isinstance(command, QueryString):
                        if command.read_bytes < 0:
                            resp = self.instrument.readline()
                        else:
                            resp = self.instrument.read(command.read_bytes)
                        return resp
                return wrapper

            setattr(self, command.name, MethodType(wrapped(self.instrument, command), self))

    def remove_command(self, command):
        """
        Remove a command from this container.

        Args:
            command: The command name string to remove
        """
        if command in self.commands:
            del self.commands[command]
            delattr(self, command)

    def list_all(self):
        """
        List the callable methods on this object.

        Returns: A sorted list of method names.
        """
        return sorted(list(self.commands.keys()))
