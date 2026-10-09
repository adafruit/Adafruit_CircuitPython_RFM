# SPDX-FileCopyrightText: 2024 Ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

# Simple demo of sending and receiving data with the RFM9x or RFM69 radios.
# Author: Jerry Needell

import time

import board
import busio
import digitalio


def checksum(message) -> bool:
    if message is not None and len(message) > 2:
        message_sum = sum(message[0 : len(message) - 1])
        return message_sum & 0xFF == message[len(message) - 1]
    return False


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
# rfm.send(bytes("Hello world!\r\n", "utf-8"))
# print("Sent Hello World message!")

rfm.packet_format = 0
rfm.preamble_length = 5
rfm.modulation_shaping = 0
rfm.frequency_deviation = 35000
rfm.bitrate = 17241
rfm.payload_length = 14
rfm.dio_mapping = 0b01
rfm.dc_free = 0
rfm.rx_bw_dcc_freq = 0b010
rfm.rx_bw_mantissa = 0b0
rfm.rx_bw_exponent = 0b0
rfm.crc = False
rfm.crc_auto_clear_off = True
rfm.radiohead = False
# Wait to receive packets.
print("Waiting for packets...")

while True:
    packet = rfm.receive(timeout=2.0)
    # Optionally change the receive timeout from its default of 0.5 seconds:
    # packet = rfm9x.receive(timeout=5.0)
    # If no packet was received during the timeout then None is returned.
    if packet is None:
        # Packet has not been received
        # print("Received nothing! Listening again...")
        pass
    # Received a packet!
    elif checksum(packet):
        print(time.monotonic())
        # Print out the raw bytes of the packet:
        print(f"Received (raw bytes): {packet}")
        # And decode to ASCII text and print it too.  Note that you always
        # receive raw bytes and need to convert to a text format like ASCII
        # if you intend to do string processing on your data.  Make sure the
        # sending side is sending ASCII data before you try to decode!
        try:
            packet_text = str(packet, "ascii")
            print(f"Received (ASCII): {packet_text}")
        except UnicodeError:
            print("Hex data: ", [hex(x) for x in packet])
        # Also read the RSSI (signal strength) of the last received message and
        # print it.
        rssi = rfm.last_rssi
        print(f"Received signal strength: {rssi} dB")
