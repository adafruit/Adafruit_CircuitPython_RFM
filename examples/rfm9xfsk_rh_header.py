# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

# Example to display raw packets including header
# Author: Jerry Needell
#
import board
import busio
import digitalio

from adafruit_rfm import rfm9xfsk

# Define radio parameters.
RADIO_FREQ_MHZ = 915.0  # Frequency of the radio in Mhz. Must match your
# module! Can be a value like 915.0, 433.0, etc.

# Define pins connected to the chip, use these if wiring up the breakout according to the guide:
CS = digitalio.DigitalInOut(board.CE1)
RESET = digitalio.DigitalInOut(board.D25)

# Initialize SPI bus.
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)

# Initialze RFM radio
rfm9xfsk = rfm9xfsk.RFM9xFSK(spi, CS, RESET, RADIO_FREQ_MHZ)

# Wait to receive packets.
print("Waiting for packets...")
# initialize flag and timer
while True:
    # Look for a new packet: only accept if addresses to my_node
    packet = rfm9xfsk.receive(with_header=True)
    # If no packet was received during the timeout then None is returned.
    if packet is not None:
        # Received a packet!
        # Print out the raw bytes of the packet:
        print("Received (raw header):", [hex(x) for x in packet[0:]])
        print(f"Received (raw payload): {packet[4:]}")
        print(f"RSSI: {rfm9xfsk.last_rssi}")
        # send reading after any packet received
