"""
Module Exceptions.

All project level exceptions.
"""


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


class GPIBCommandError(BaseGPIBError):
    """
    Base GPIB Command Error.

    To be subclassed by each individual error string supported.
    """

    pass


class UnrecognizedCommandError(GPIBCommandError):
    """
    Unrecognized Command.

    Thrown when Controller returns the appropriate error string.
    """

    pass


ERROR_MESSAGES = {
    b'Unrecognized Command': UnrecognizedCommandError
}
