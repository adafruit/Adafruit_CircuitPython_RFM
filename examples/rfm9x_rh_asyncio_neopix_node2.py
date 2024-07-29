# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

# Example using Interrupts to send a message and then wait indefinitely for messages
# to be received. Interrupts are used only for receive. sending is done with polling.
# This example is for systems that support interrupts like the Raspberry Pi with "blinka"
# CircuitPython does not support interrupts so it will not work on  Circutpython boards
# Author: Tony DiCola, Jerry Needell
import asyncio
import time

import board
import busio
import digitalio
import neopixel

from adafruit_rfm import rfm9x

# On CircuitPlayground Express, and boards with built in status NeoPixel -> board.NEOPIXEL
# Otherwise choose an open pin connected to the Data In of the NeoPixel strip, i.e. board.D1
pixel_pin = board.D5

# On a Raspberry pi, use this instead, not all pins are supported
# pixel_pin = board.D18

# The number of NeoPixels
num_pixels = 32

# The order of the pixel colors - RGB or GRB. Some NeoPixels have red and green reversed!
# For RGBW NeoPixels, simply change the ORDER to RGBW or GRBW.
ORDER = neopixel.GRB

pixels = neopixel.NeoPixel(
    pixel_pin, num_pixels, brightness=0.2, auto_write=False, pixel_order=ORDER
)


# Define radio parameters.
RADIO_FREQ_MHZ = 915.0  # Frequency of the radio in Mhz. Must match your
# module! Can be a value like 915.0, 433.0, etc.

# Define pins connected to the chip, use these if wiring up the breakout according to the guide:
CS = digitalio.DigitalInOut(board.D10)
RESET = digitalio.DigitalInOut(board.D11)

# Initialize SPI bus.
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)

# Initialze RFM radio
rfm9x = rfm9x.RFM9x(spi, CS, RESET, RADIO_FREQ_MHZ)

# set node addresses
rfm9x.node = 2
rfm9x.destination = 100
# send startup message from my_node
# rfm9x.send_with_ack(bytes("startup message from node {}".format(rfm9x.node), "UTF-8"))
rfm9x.listen()
# rfm9x.xmit_timeout = 5.
# Wait to receive packets.
print("Waiting for packets...")
# initialize flag and timer


# pylint: disable=too-few-public-methods
class Packet:
    """Simple class to hold an  value. Use .value to to read or write."""

    def __init__(self):
        self.received = False


def wheel(pos):
    # Input a value 0 to 255 to get a color value.
    # The colours are a transition r - g - b - back to r.
    if pos < 0 or pos > 255:
        r = g = b = 0
    elif pos < 85:
        r = int(pos * 3)
        g = int(255 - pos * 3)
        b = 0
    elif pos < 170:
        pos -= 85
        r = int(255 - pos * 3)
        g = 0
        b = int(pos * 3)
    else:
        pos -= 170
        r = 0
        g = int(pos * 3)
        b = int(255 - pos * 3)
    return (r, g, b) if ORDER in (neopixel.RGB, neopixel.GRB) else (r, g, b, 0)


async def rainbow_cycle(wait, lock):
    while True:
        if not lock.locked():
            for j in range(255):
                for i in range(num_pixels):
                    pixel_index = (i * 256 // num_pixels) + j
                    pixels[i] = wheel(pixel_index & 255)
                pixels.show()
        await asyncio.sleep(wait)


async def wait_for_packets(packet_status, lock):
    while True:
        if rfm9x.payload_ready():
            if lock.locked():
                print("locked waiting for receive")
            async with lock:
                packet = await rfm9x.asyncio_receive_with_ack(with_header=True, timeout=None)
            if packet is not None:
                packet_status.received = True
                # Received a packet!
                # Print out the raw bytes of the packet:
                print(f"Received (raw bytes): {packet}")
                print([hex(x) for x in packet])
                print(f"RSSI: {rfm9x.last_rssi}")
        await asyncio.sleep(0.001)


async def send_packets(packet_status, lock):
    # initialize counter
    counter = 0
    ack_failed_counter = 0
    counter = 0
    transmit_interval = 5
    time_now = time.monotonic()
    while True:
        # If no packet was received during the timeout then None is returned.
        if packet_status.received:
            packet_status.received = False
        if time.monotonic() - time_now > transmit_interval:
            # reset timeer
            time_now = time.monotonic()
            counter += 1
            # send a  mesage to destination_node from my_node
            if lock.locked():
                print("locked waiting for send")
            async with lock:
                if not await rfm9x.asyncio_send_with_ack(
                    bytes(
                        f"message from node {rfm9x.node} {counter} {ack_failed_counter}",
                        "UTF-8",
                    )
                ):
                    ack_failed_counter += 1
                    print(" No Ack: ", counter, ack_failed_counter)
        await asyncio.sleep(0.1)


async def main():
    packet_status = Packet()
    lock = asyncio.Lock()
    task1 = asyncio.create_task(wait_for_packets(packet_status, lock))
    task2 = asyncio.create_task(send_packets(packet_status, lock))
    task3 = asyncio.create_task(rainbow_cycle(0.001, lock))  # rainbow cycle with 1ms delay per step

    await asyncio.gather(task1, task2, task3)  # Don't forget "await"!


asyncio.run(main())
