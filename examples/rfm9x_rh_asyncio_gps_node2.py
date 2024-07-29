# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

# Example using Interrupts to send a message and then wait indefinitely for messages
# to be received. Interrupts are used only for receive. sending is done with polling.
# This example is for systems that support interrupts like the Raspberry Pi with "blinka"
# CircuitPython does not support interrupts so it will not work on  Circutpython boards
# Author: Tony DiCola, Jerry Needell
import asyncio
import time

import adafruit_gps
import board
import busio
import digitalio

from adafruit_rfm import rfm9x

uart = busio.UART(board.TX, board.RX, baudrate=9600, timeout=10)

# Create a GPS module instance.
gps = adafruit_gps.GPS(uart, debug=False)  # Use UART/pyserial

# Turn on the basic GGA and RMC info (what you typically want)
gps.send_command(b"PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0")

# Set update rate to once a second (1hz) which is what you typically want.
gps.send_command(b"PMTK220,1000")


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
        self.gps_time = "Unknown"
        self.gps_latitude = 0.0
        self.gps_longitude = 0.0


async def read_gps(packet_status, wait):
    # Main loop runs forever printing the location, etc. every second.
    last_print = time.monotonic()
    while True:
        # Make sure to call gps.update() every loop iteration and at least twice
        # as fast as data comes from the GPS unit (usually every second).
        # This returns a bool that's true if it parsed new data (you can ignore it
        # though if you don't care and instead look at the has_fix property).
        gps.update()
        # Every second print out current location details if there's a fix.
        current = time.monotonic()
        if current - last_print >= 1.0:
            last_print = current
            if not gps.has_fix:
                # Try again if we don't have a fix yet.
                print("Waiting for fix...")
                packet_status.gps_time = "Unknown"
                packet_status.gps_latitude = 0.0
                packet_status.gps_longitude = 0.0
                continue
            # We have a fix! (gps.has_fix is true)
            # Print out details about the fix like location, date, etc.
            print("=" * 40)  # Print a separator line.
            packet_status.gps_time = f"Fix timestamp: {gps.timestamp_utc.tm_mon}/{gps.timestamp_utc.tm_mday}/{gps.timestamp_utc.tm_year} {gps.timestamp_utc.tm_hour:02}:{gps.timestamp_utc.tm_min:02}:{gps.timestamp_utc.tm_sec:02}"  # noqa: E501
            print(packet_status.gps_time)
            print(f"Latitude: {gps.latitude:.6f} degrees")
            print(f"Longitude: {gps.longitude:.6f} degrees")
            packet_status.gps_latitude = gps.latitude
            packet_status.gps_longitude = gps.longitude
            if gps.satellites is not None:
                print(f"# satellites: {gps.satellites}")
            if gps.altitude_m is not None:
                print(f"Altitude: {gps.altitude_m} meters")
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
                        f"message from node {rfm9x.node} {counter} {ack_failed_counter} {packet_status.gps_time} {packet_status.gps_latitude:.6f} {packet_status.gps_longitude:.6f}",  # noqa: E501
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
    task3 = asyncio.create_task(read_gps(packet_status, 0.25))

    await asyncio.gather(task1, task2, task3)  # Don't forget "await"!


asyncio.run(main())
