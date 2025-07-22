# SPDX-FileCopyrightText: 2024 Jerry Needell for Adafruit Industries
# SPDX-License-Identifier: MIT

# Example to test maximum power output for RFM98PW (30 dBm)
# This demonstrates the enhanced power capability for satellite communications

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

# Initialize RFM radio for LoRa mode
from adafruit_rfm import rfm9x

rfm = rfm9x.RFM9x(spi, CS, RESET, RADIO_FREQ_MHZ)

# Test different power levels including the new maximum
power_levels = [13, 20, 23, 27, 30]

print("Testing RFM98PW maximum power capability...")
print("=" * 50)

for power in power_levels:
    try:
        rfm.tx_power = power
        # Read back the register to verify OCP setting
        if power > 23:
            ocp_reg = rfm.read_u8(0x0B)  # Read OCP register
            print(f"Power: {power} dBm - SUCCESS (OCP register: 0x{ocp_reg:02X})")
        else:
            print(f"Power: {power} dBm - SUCCESS")

        # Send a test message at this power level
        message = f"Test message at {power} dBm"
        rfm.send(bytes(message, "UTF-8"))
        print(f"  -> Sent: '{message}'")
        time.sleep(1)

    except Exception as e:
        print(f"Power: {power} dBm - FAILED: {e}")

print("=" * 50)
print("Test complete! For satellite communications, use:")
print("rfm.tx_power = 30  # Maximum power for RFM98PW")
print(
    "This enables the command: c.radio1.write_u8(0x0B,0x3F);c.radio1.output_power=0x0F"
)
