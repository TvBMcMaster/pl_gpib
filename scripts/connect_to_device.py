#!/usr/bin/env python
"""
This script sets up a simple serial spy and tries to connect to a device.

It interacts briefly with the controller, querying and increasing its
address by 2.
"""
import serial
import pl_gpib


def main():
    """Main Script Function."""
    port = '/dev/ttyUSB0'
    spy_file = 'development.spy'
    with serial.serial_for_url(
        'spy://{port}?file={spy_file}'.format(
            port=port, spy_file=spy_file),
            timeout=1) as s:
        c = pl_gpib.controller.GPIBController(port, connection=s)
        print("Device Connected: {}".format(c.version))
        print("Device Address: {}".format(c.address))

        new_address = c.address + 2

        c.set_address(new_address)

        print("New Device Address: {}".format(c.address))


if __name__ == '__main__':
    main()
