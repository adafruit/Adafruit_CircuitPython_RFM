# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

import time

import board
import busio
import digitalio

# Define radio parameters.
RADIO_FREQ_MHZ = 915.0  # Frequency of the radio in Mhz. Must match your
# module! Can be a value like 915.0, 433.0, etc.

# Define pins connected to the chip, use these if wiring up the breakout according to the guide:
CS = digitalio.DigitalInOut(board.CE1)
RESET = digitalio.DigitalInOut(board.D25)

# Initialize SPI bus.
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)

# Initialze RFM radio
# uncommnet the desired import and rfm initialization depending on the radio boards being used

# Use rfm9x for two RFM9x radios using LoRa

from adafruit_rfm import rfm9x

rfm = rfm9x.RFM9x(spi, CS, RESET, RADIO_FREQ_MHZ)

rfm.radiohead = False  # don't appent RadioHead heade
# set spreading factor
rfm.spreading_factor = 7
print("spreading factor set to :", rfm.spreading_factor)
print("low_datarate_optimize set to: ", rfm.low_datarate_optimize)
# rfm.signal_bandwidth = 500000
print("signal_bandwidth set to :", rfm.signal_bandwidth)
print("low_datarate_optimize set to: ", rfm.low_datarate_optimize)
if rfm.spreading_factor == 12:
    rfm.xmit_timeout = 5
print("xmit_timeout set to: ", rfm.xmit_timeout)
if rfm.spreading_factor == 12:
    rfm.receive_timeout = 5
elif rfm.spreading_factor > 7:
    rfm.receive_timeout = 2
print("receive_timeout set to: ", rfm.receive_timeout)
rfm.enable_crc = True
# send startup message
message = bytes(f"startup message from base", "UTF-8")
if rfm.spreading_factor == 6:
    payload = bytearray(40)
    rfm.payload_length = len(payload)
    payload[0 : len(message)] = message
    rfm.send(
        payload,
        keep_listening=True,
    )
else:
    rfm.send(
        message,
        keep_listening=True,
    )
# Wait to receive packets.
print("Waiting for packets...")
# initialize flag and timer
# set a delay before sending the echo packet
# avoide multibples of .5 second to minimize chances of node missing
# the packet between receive attempts
transmit_delay = 0.75
last_transmit_time = 0
packet_received = False
while True:
    if rfm.payload_ready():
        packet_received = False
        packet = rfm.receive(timeout=None)
        if packet is not None:
            # Received a packet!
            # Print out the raw bytes of the packet:
            print(f"Received (raw payload): {packet}")
            print([hex(x) for x in packet])
            print(f"RSSI: {rfm.last_rssi}")
            packet_received = True
            last_transmit_time = time.monotonic()
    if packet_received and ((time.monotonic() - last_transmit_time) > transmit_delay):
        # send back the received packet
        if rfm.spreading_factor == 6:
            payload = bytearray(40)
            rfm.payload_length = len(payload)
            payload[0 : len(packet)] = packet
            rfm.send(
                payload,
                keep_listening=True,
            )
        else:
            rfm.send(
                packet,
                keep_listening=True,
            )
        packet_received = False
