import pytest
import time
import math
import subprocess
import RPi.GPIO as GPIO
import smbus2
import serial


DAC_A0_ADDR = 0x4E  # DAC connected to Nucleo A0
SERIAL_PORT = "/dev/ttyACM0"
BAUD_RATE = 115200


def write_dac(bus, addr, code):
    """Write a 16-bit code to an AD5693R DAC at the given I2C address.

    Protocol (3 bytes):
      cmd  = 0x30  → command nibble 0x3 (write+update DAC and input registers),
                      lower nibble 0x0 (don't care)
      msb  = (code >> 8) & 0xFF  → bits [15:8]
      lsb  = code & 0xFF         → bits [7:0]
    """
    bus.write_i2c_block_data(addr, 0x30, [(code >> 8) & 0xFF, code & 0xFF])


def sinus_dac_code(t, freq=1.0, amplitude=0.4, offset=0.5, phase=0.0):
    """Compute a 16-bit DAC code from wall-clock time t.

    Signal is kept within [offset-amplitude, offset+amplitude] × 65535.
    """
    v = offset + amplitude * math.sin(2 * math.pi * freq * t + phase)
    return int(max(0, min(65535, v * 65535)))


@pytest.fixture(scope="function")
def setup_hardware():
    """Setup and teardown for analog-serial hardware testing."""
    GPIO.setwarnings(False)
    try:
        GPIO.setmode(GPIO.BCM)
    except Exception:
        pass

    bus = smbus2.SMBus(1)  # I2C bus 1 (GPIO 2 = SDA, GPIO 3 = SCL)

    # Set DAC to mid-scale before starting
    write_dac(bus, DAC_A0_ADDR, 32768)

    # Reset the MCU so the program starts from scratch
    subprocess.run(
        [
            "pio",
            "pkg",
            "exec",
            "-p",
            "tool-openocd",
            "-c",
            "openocd -f interface/stlink.cfg -f target/stm32f4x.cfg"
            " -c 'init; reset run; shutdown'",
        ],
        check=True,
    )
    time.sleep(1.0)  # Wait for MCU to initialize and serial to come up

    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    ser.reset_input_buffer()

    yield bus, ser

    # Teardown: leave DAC at mid-scale
    write_dac(bus, DAC_A0_ADDR, 32768)
    ser.close()
    bus.close()
    GPIO.cleanup()
