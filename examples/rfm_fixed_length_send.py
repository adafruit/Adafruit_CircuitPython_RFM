# SPDX-FileCopyrightText: 2024 Ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

# Simple demo of sending and recieving data with the RFM9x or RFM69 radios.
# Author: Jerry Needell

import time

import board
import busio
import digitalio

# Define radio parameters.
RADIO_FREQ_MHZ = 915.00  # Frequency of the radio in Mhz. Must match your
# module! Can be a value like 915.0, 433.0, etc.

# Define pins connected to the chip, use these if wiring up the breakout according to the guide:
# CS = digitalio.DigitalInOut(board.CE1)
# RESET = digitalio.DigitalInOut(board.D25)
CS = digitalio.DigitalInOut(board.D20)
RESET = digitalio.DigitalInOut(board.D21)
# CS = digitalio.DigitalInOut(board.RFM_CS)
# RESET = digitalio.DigitalInOut(board.RFM_RST)

# Initialize SPI bus.
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)

# Initialze RFM radio
# uncommnet the desired import and rfm initialization depending on the radio boards being used

# Use rfm9x for two RFM9x radios using LoRa

# from adafruit_rfm import rfm9x

# rfm = rfm9x.RFM9x(spi, CS, RESET, RADIO_FREQ_MHZ)

# Use rfm9xfsk for two RFM9x radios or RFM9x to RFM69 using FSK

# from adafruit_rfm import rfm9xfsk

# rfm = rfm9xfsk.RFM9xFSK(spi, CS, RESET, RADIO_FREQ_MHZ)

# Use rfm69 for two RFM69 radios using FSK

from adafruit_rfm import rfm69

rfm = rfm69.RFM69(spi, CS, RESET, RADIO_FREQ_MHZ)

# For RFM69 only: Optionally set an encryption key (16 byte AES key). MUST match both
# on the transmitter and receiver (or be set to None to disable/the default).
rfm.encryption_key = None
# rfm.encryption_key = (
#    b"\x01\x02\x03\x04\x05\x06\x07\x08\x01\x02\x03\x04\x05\x06\x07\x08"
# )

# for OOK on RFM69 or RFM9xFSK
# rfm.modulation_type = 1
# rfm.modulation_type = 1

# Send a packet.  Note you can only send a packet containing up to 60 bytes for an RFM69
# and 252 bytes for an RFM9x.
# This is a limitation of the radio packet size, so if you need to send larger
# amounts of data you will need to break it into smaller send calls.  Each send
# call will wait for the previous one to finish before continuing.

rfm.packet_format = 0
rfm.payload_length = 20
rfm.crc = False
rfm.crc_auto_clear_off = True
rfm.radiohead = False
# Wait to receive packets.
print("Waiting for packets...")

while True:
    rfm.send(bytes("0123456789012345678\r", "utf-8"))
    print("Sent message!")
    time.sleep(5)
