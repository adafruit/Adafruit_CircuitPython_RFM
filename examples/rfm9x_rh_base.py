# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

import board
import busio
import digitalio

from adafruit_rfm import rfm9x

# Define radio parameters.
RADIO_FREQ_MHZ = 915.0  # Frequency of the radio in Mhz. Must match your
# module! Can be a value like 915.0, 433.0, etc.

# Define pins connected to the chip, use these if wiring up the breakout according to the guide:
CS = digitalio.DigitalInOut(board.CE1)
RESET = digitalio.DigitalInOut(board.D25)

# Initialize SPI bus.
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)

# Initialze RFM radio
rfm9x = rfm9x.RFM9x(spi, CS, RESET, RADIO_FREQ_MHZ)

# set node addresses
rfm9x.node = 100
rfm9x.destination = 0xFF
# send startup message from my_node
rfm9x.send(
    bytes(f"startup message from base {rfm9x.node}", "UTF-8"),
    keep_listening=True,
)
# Wait to receive packets.
print("Waiting for packets...")
# initialize flag and timer


while True:
    if rfm9x.payload_ready():
        packet = rfm9x.receive_with_ack(with_header=True, timeout=None)
        if packet is not None:
            # Received a packet!
            # Print out the raw bytes of the packet:
            print(f"Received (raw bytes): {packet}")
            print([hex(x) for x in packet])
            print(f"RSSI: {rfm9x.last_rssi}")
