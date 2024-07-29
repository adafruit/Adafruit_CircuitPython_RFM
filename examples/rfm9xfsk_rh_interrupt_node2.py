# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

# Example using Interrupts to send a message and then wait indefinitely for messages
# to be received. Interrupts are used only for receive. sending is done with polling.
# This example is for systems that support interrupts like the Raspberry Pi with "blinka"
# CircuitPython does not support interrupts so it will not work on  Circutpython boards
# Author: Tony DiCola, Jerry Needell
import board
import busio
import digitalio
import RPi.GPIO as io

from adafruit_rfm import rfm9xfsk


# setup interrupt callback function
def rfm9x_callback(rfm9x_irq):
    global packet_received  # noqa: PLW0603
    print("OP MODE: ", hex(rfm9x.read_u8(0x01)))
    print("IRQ FLAGS 2: ", hex(rfm9x.read_u8(0x3F)))
    print("IRQ detected ", rfm9x_irq, rfm9x.packet_sent(), rfm9x.payload_ready())
    # check to see if this was a rx interrupt - ignore tx
    if rfm9x.payload_ready():
        packet = rfm9x.receive_with_ack(with_header=True, timeout=None)
        if packet is not None:
            packet_received = True
            # Received a packet!
            # Print out the raw bytes of the packet:
            print(f"Received (raw bytes): {packet}")
            print([hex(x) for x in packet])
            print(f"RSSI: {rfm9x.last_rssi}")


# Define radio parameters.
RADIO_FREQ_MHZ = 915.0  # Frequency of the radio in Mhz. Must match your
# module! Can be a value like 915.0, 433.0, etc.

# Define pins connected to the chip, use these if wiring up the breakout according to the guide:
CS = digitalio.DigitalInOut(board.CE1)
RESET = digitalio.DigitalInOut(board.D25)

# Initialize SPI bus.
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)

# Initialze RFM radio
rfm9x = rfm9xfsk.RFM9xFSK(spi, CS, RESET, RADIO_FREQ_MHZ)

# Note that the radio is configured in LoRa mode so you can't control sync
# word, encryption, frequency deviation, or other settings!

# You can however adjust the transmit power (in dB).  The default is 13 dB but
# high power radios like the RFM95 can go up to 23 dB:
rfm9x.tx_power = 23

# configure the interrupt pin and event handling.
RFM9X_G0 = 22
io.setmode(io.BCM)
io.setup(RFM9X_G0, io.IN, pull_up_down=io.PUD_DOWN)  # activate input
io.add_event_detect(RFM9X_G0, io.RISING)
io.add_event_callback(RFM9X_G0, rfm9x_callback)

packet_received = False

# set delay before sending ACK
rfm9x.ack_delay = None
# set node addresses
rfm9x.node = 2
rfm9x.destination = 1
# initialize counter
counter = 0
ack_failed_counter = 0
rfm9x.listen()
# send startup message from my_node
rfm9x.send_with_ack(bytes(f"startup message from node {rfm9x.node}", "UTF-8"))
# Wait to receive packets.
print("Waiting for packets...")
# initialize flag and timer
while True:
    # If no packet was received during the timeout then None is returned.
    if packet_received:
        packet_received = False
        counter += 1
        # send a  mesage to destination_node from my_node
        if not rfm9x.send_with_ack(
            bytes(f"message from node node {rfm9x.node} {counter}", "UTF-8")
        ):
            ack_failed_counter += 1
            print(" No Ack: ", counter, ack_failed_counter)
