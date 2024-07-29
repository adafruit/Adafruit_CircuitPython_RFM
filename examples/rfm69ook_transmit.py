# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

# Example to send a packet periodically
# Author: Jerry Needell
#
import time

import board
import busio
import digitalio

from adafruit_rfm import rfm69

# Define radio parameters.
RADIO_FREQ_MHZ = 915.0  # Frequency of the radio in Mhz. Must match your
# module! Can be a value like 915.0, 433.0, etc.

# Define pins connected to the chip, use these if wiring up the breakout according to the guide:
CS = digitalio.DigitalInOut(board.CE1)
RESET = digitalio.DigitalInOut(board.D25)

# Initialize SPI bus.
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)


# Initialze RFM radio
rfm69 = rfm69.RFM69(spi, CS, RESET, RADIO_FREQ_MHZ)
# set the time interval (seconds) for sending packets
node = 1
destination = 2
rfm69.radiohead = False
print(rfm69.modulation_type)
rfm69.modulation_type = 1
print(rfm69.modulation_type)
# Optionally set an encryption key (16 byte AES key). MUST match both
# on the transmitter and receiver (or be set to None to disable/the default).
rfm69.encryption_key = None
# rfm69.encryption_key = (
#    b"\x01\x02\x03\x04\x05\x06\x07\x08\x01\x02\x03\x04\x05\x06\x07\x08"
# )

# set the time interval (seconds) for sending packets
transmit_interval = 5

# Note that the radio is configured in LoRa mode so you can't control sync
# word, encryption, frequency deviation, or other settings!

# You can however adjust the transmit power (in dB).  The default is 13 dB but
# high power radios like the RFM69 can go up to 20 dB:
# rfm69.tx_power = 20


# initialize counter
counter = 0
# send a broadcast mesage
rfm69.send(bytes(f"message number {counter}", "UTF-8"))

# Wait to receive packets.
print("Waiting for packets...")
# initialize flag and timer
send_reading = False
time_now = time.monotonic()
while True:
    # Look for a new packet - wait up to 2 seconds:
    packet = rfm69.receive(timeout=2.0)
    # If no packet was received during the timeout then None is returned.
    if packet is not None:
        # Received a packet!
        # Print out the raw bytes of the packet:
        print(f"Received (raw bytes): {packet}")
        # send reading after any packet received
    if time.monotonic() - time_now > transmit_interval:
        # reset timeer
        time_now = time.monotonic()
        # clear flag to send data
        send_reading = False
        counter = counter + 1
        rfm69.send(bytes(f"message number {counter}", "UTF-8"))
