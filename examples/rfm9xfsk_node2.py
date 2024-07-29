# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

# Example to send a packet periodically
# Author: Jerry Needell
#
import random
import time

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
node = 2
destination = 1

rfm9xfsk.radiohead = False
rfm9xfsk.enable_address_filter = True
rfm9xfsk.fsk_node_address = node
rfm9xfsk.fsk_broadcast_address = 0xFF
# set the time interval (seconds) for sending packets
transmit_interval = 2

# Note that the radio is configured in LoRa mode so you can't control sync
# word, encryption, frequency deviation, or other settings!

# You can however adjust the transmit power (in dB).  The default is 13 dB but
# high power radios like the RFM95 can go up to 23 dB:
# rfm9xfsk.tx_power = 23


# initialize counter
counter = 0
# send a startup  mesage
rfm9xfsk.send(bytes(f"message number {counter}", "UTF-8"), destination=destination)

# Wait to receive packets.
print("Waiting for packets...")
# initialize flag and timer
time_now = time.monotonic()
while True:
    # Look for a new packet - wait up to 2 seconds:
    packet = rfm9xfsk.receive(timeout=0.5)
    # If no packet was received during the timeout then None is returned.
    if packet is not None:
        # Received a packet!
        # Print out the raw bytes of the packet:
        print(f"Received (raw bytes): {packet}", rfm9xfsk.last_rssi)
    if time.monotonic() - time_now > transmit_interval + random.random():
        counter = counter + 1
        rfm9xfsk.send(bytes(f"message number {counter}", "UTF-8"), destination=destination)
        time_now = time.monotonic()
