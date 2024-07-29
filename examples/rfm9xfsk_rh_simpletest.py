# SPDX-FileCopyrightText: 2024 Ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

# Simple demo of sending and recieving data with the rfm9x FSK radio.
# Author: Jerry Needell
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

# Print out some chip state:
print(f"Temperature: {rfm9xfsk.temperature}C")
print(f"Frequency: {rfm9xfsk.frequency_mhz}mhz")
print(f"Bit rate: {rfm9xfsk.bitrate / 1000}kbit/s")
print(f"Frequency deviation: {rfm9xfsk.frequency_deviation}hz")

# Send a packet.  Note you can only send a packet up to 252 bytes in length.
# This is a limitation of the radio packet size, so if you need to send larger
# amounts of data you will need to break it into smaller send calls.  Each send
# call will wait for the previous one to finish before continuing.
rfm9xfsk.send(bytes("Hello world!\r\n", "utf-8"))
print("Sent hello world message!")

# Wait to receive packets.  Note that this library can't receive data at a fast
# rate, in fact it can only receive and process one 252 byte packet at a time.
# This means you should only use this for low bandwidth scenarios, like sending
# and receiving a single message at a time.
print("Waiting for packets...")
while True:
    packet = rfm9xfsk.receive()
    # Optionally change the receive timeout from its default of 0.5 seconds:
    # packet = rfm9xfsk.receive(timeout=5.0)
    # If no packet was received during the timeout then None is returned.
    if packet is None:
        # Packet has not been received
        print("Received nothing! Listening again...")
    else:
        # Received a packet!
        # Print out the raw bytes of the packet:
        print(f"Received (raw bytes): {packet}")
        # And decode to ASCII text or HEX if the ASCII decode fails
        try:
            packet_text = str(packet, "ascii")
            print(f"Received (ASCII): {packet_text}")
        except UnicodeDecodeError:
            print("Hex data: ", [hex(x) for x in packet])
        rssi = rfm9xfsk.last_rssi
        print(f"Received signal strength: {rssi} dB")
