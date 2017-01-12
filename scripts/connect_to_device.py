#!/usr/bin/env python
"""
This script sets up a simple serial spy and tries to connect to a device.

It interacts briefly with the controller, querying and increasing its
address by 2.
"""
import serial
from pl_gpib import GPIBController, GPIBInstrument

INSTRUMENT_PORT = 10


def main():
    """Main Script Function."""
    port = '/dev/ttyUSB0'
    spy_file = 'development.spy'
    with serial.serial_for_url(
        'spy://{port}?file={spy_file}'.format(
            port=port, spy_file=spy_file),
            timeout=1) as s:
        c = GPIBController(port, connection=s)
        print("Device Connected: {}".format(c.version))
        print("Device Address: {}".format(c.address))

        inst = GPIBInstrument(address=INSTRUMENT_PORT)

        c.add_instrument(inst)

        print("Instrument ID: {}".format(inst.name))
if __name__ == '__main__':
    main()
