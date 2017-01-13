Getting Started
================

This guide is intended to walk a user through initial connection and interaction with their Prologix GPIB Controller.  For this, a controller is required and must be connected to the computer.

Configuring a Controller
------------------------

Begin by importing and creating your instance of :py:class:`~pl_gpib.controller.Controller` object.  You
must just enter the port being used to communicate with the Prologix controller.  In the connection routine, some basic
information is queried from the device, such as its current address, current mode, and version string.

.. code-block:: python

    >>> from pl_gpib import GPIBController
    >>> controller = GPIBController('/dev/ttyUSB0')
    >>> controller.mode
    1
    >>> controller.address
    12
    >>> controller.version
    'Prologix GPIB USB version 3.4.5'

Configure An Instrument
------------------------

Next, the controller needs some instruments to manage.  These instruments can be a simple instance of
:py:class:`~pl_gpib.instrument.GPIBInstrument` or can be a more refined Instrument object from a library, such as
`pl_gpib_inst`.  In any case, you need to know the GPIB address that the instrument is currently configured to
communicate.  Each physical instrument will be represented by a corresponding
:py:class:`~pl_gpib.instrument.GPIBInstrument` instance.

.. code-block:: python

    >>> from pl_gpib import GPIBInstrument
    >>> my_instrument = GPIBInstrument(address=12)
    >>> controller.add_instrument(my_instrument)

Interact with an Instrument
----------------------------

Commands can be written and responses read back using the low level `read` and `write` methods.

.. code-block:: python

    >>> my_instrument.write('*IDN?')
    >>> my_instrument.read(100)
    b'Lab Corp. XJ324'

Alternatively, instruments might have more refined logic and commands available.  The Instrument instance has attributes,
`query` and `command`, which contain configured commands available to that instrument.  There are some common queries and
commands which are required for all instruments.  These come built in.

.. code-block:: python

    >>> my_instrument.query.ident()
    b'Lab Corp. XJ324'

The available commands and queries on an Instrument can be found using the respective `list_all()` method call.

.. code-block:: python

    >>> my_instrument.query.list_all()
    ['event_status_enable',
     'event_status_register',
     'ident',
     'operation_complete',
     'options',
     'read_status_byte',
     'self_test',
     'service_request_enable']
    >>> my_instrument.command.list_all()
    ['clear',
     'event_status_enable',
     'operation_complete',
     'recall_instrument_setting',
     'reset',
     'save',
     'service_request_enable',
     'wait']


Script An Experiment
---------------------

Next steps are to connect up your instruments, and script up an experiment.
