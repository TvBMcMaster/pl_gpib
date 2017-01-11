#!/usr/bin/env python

import serial
import pl_gpib

port = '/dev/ttyUSB0'
spy_file = 'development.spy'
with serial.serial_for_url(
    'spy://{port}?file={spy_file}'.format(
        port=port, spy_file=spy_file),
        timeout=1) as s:
    c = pl_gpib.GPIBController(port, connection=s)
    print("Device Connected: {}".format(c.version))
    print("Device Address: {}".format(c.address))

    new_address = c.address + 2

    c.set_address(new_address)

    print("New Device Address: {}".format(c.address))
