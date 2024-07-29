# SPDX-FileCopyrightText: 2020 Jerry Needell for Adafruit Industries
# SPDX-License-Identifier: MIT

# Example to send a packet periodically between addressed nodes with ACK

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


# set the time interval (seconds) for sending packets
transmit_interval = 10

# set delay before sending ACK
rfm9xfsk.ack_delay = 0.1
# set node addresses
rfm9xfsk.node = 1
rfm9xfsk.destination = 2
# initialize counter
counter = 0
ack_failed_counter = 0
# send startup message from my_node
rfm9xfsk.send_with_ack(bytes(f"startup message from node {rfm9xfsk.node}", "UTF-8"))

# Wait to receive packets.
print("Waiting for packets...")
# initialize flag and timer
time_now = time.monotonic()
while True:
    # Look for a new packet: only accept if addresses to my_node
    packet = rfm9xfsk.receive_with_ack(with_header=True)
    # If no packet was received during the timeout then None is returned.
    if packet is not None:
        # Received a packet!
        # Print out the raw bytes of the packet:
        print("Received (raw header):", [hex(x) for x in packet[0:4]])
        print(f"Received (raw payload): {packet[4:]}")
        print(f"RSSI: {rfm9xfsk.last_rssi}")
        # send reading after any packet received
    if time.monotonic() - time_now > transmit_interval:
        # reset timeer
        time_now = time.monotonic()
        counter += 1
        # send a  mesage to destination_node from my_node
        if not rfm9xfsk.send_with_ack(
            bytes(f"message from node node {rfm9xfsk.node} {counter}", "UTF-8")
        ):
            ack_failed_counter += 1
            print(" No Ack: ", counter, ack_failed_counter)
