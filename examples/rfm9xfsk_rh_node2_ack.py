# SPDX-FileCopyrightText: 2020 Jerry Needell for Adafruit Industries
# SPDX-License-Identifier: MIT

# Example to receive addressed packed with ACK and send a response

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


# set delay before transmitting ACK (seconds)
rfm9xfsk.ack_delay = 0.1
rfm9xfsk.ack_wait = 0.2
# set node addresses
rfm9xfsk.node = 2
rfm9xfsk.destination = 1
# initialize counter
counter = 0
ack_failed_counter = 0

# Wait to receive packets.
print("Waiting for packets...")
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
        # send response 2 sec after any packet received
        time.sleep(2)
        counter += 1
        # send a  mesage to destination_node from my_node
        if not rfm9xfsk.send_with_ack(
            bytes(f"response from node {rfm9xfsk.node} {counter}", "UTF-8")
        ):
            ack_failed_counter += 1
            print(" No Ack: ", counter, ack_failed_counter)
