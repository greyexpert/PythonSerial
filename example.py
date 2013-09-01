__author__ = 'greyexpert'

import struct
from time import sleep
from serial import Serial
from protocol import Protocol

ser = Serial()
ser.port = "/dev/tty.usbmodemfd1331"
ser.baudrate = 155200

arduino = Protocol(ser)
arduino.start()

channel, data = arduino.waitForPackage() # Wait for initial package

# Blinking
for x in range(10):
    sleep(1)
    arduino.send(1, struct.pack("B", x % 2))

sleep(1) # Sleep 1 second before exit