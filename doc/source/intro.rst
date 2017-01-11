Intro
======

The library `pl_gpib` is intended to act as a set of helpers for interfacing with Laboratory instruments with the GPIB
protocol via a Prologix USB-GPIB Interface controller.  The controller acts as a native RS232 serial device and has several native commands that can be leveraged to create custom scripted experiment runs.

The idea is that there is one GPIBController instance that manages the connection to each Prologix Controller.  These are
defined by the device port.  Once connected, specific instrument subclass instances can be added to the controller indexed
by the instrument GPIB address.  Each Instrument subclass will allow for raw commands and queries to be sent as well as more common and complex interactions are to be coded into subclass methods.
