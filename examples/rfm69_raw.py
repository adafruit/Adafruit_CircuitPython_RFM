# SPDX-FileCopyrightText: 2020 Jerry Needell for Adafruit Industries
# SPDX-License-Identifier: MIT

# Example to send a packet periodically

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
rfm69.radiohead = False
# Optionally set an encryption key (16 byte AES key). MUST match both
# on the transmitter and receiver (or be set to None to disable/the default).
rfm69.encryption_key = None
# rfm69.encryption_key = (
#    b"\x01\x02\x03\x04\x05\x06\x07\x08\x01\x02\x03\x04\x05\x06\x07\x08"
# )


# Wait to receive packets.
print("Waiting for packets...")
# initialize flag and timer
while True:
    # Look for a new packet - wait up to 5 seconds:
    packet = rfm69.receive(timeout=2.0)
    # If no packet was received during the timeout then None is returned.
    if packet is not None:
        # Received a packet!
        # Print out the raw bytes of the packet:
        print("Received (raw header):", [hex(x) for x in packet[0:]])
        print(f"RSSI: {rfm69.last_rssi}")
