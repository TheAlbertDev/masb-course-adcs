import pytest
import time
import math
import subprocess
import RPi.GPIO as GPIO
import smbus2
import serial

DAC_A0_ADDR = 0x4E  # DAC connected to Nucleo A0
BUTTON_GPIO = 27    # RPi GPIO output wired to Nucleo button (pin 23)
SERIAL_PORT = "/dev/ttyACM0"
BAUD_RATE = 9600


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
    """Compute a 16-bit DAC code from elapsed wall-clock time t."""
    v = offset + amplitude * math.sin(2 * math.pi * freq * t + phase)
    return int(max(0, min(65535, v * 65535)))


def press_button():
    """Simulate a button press on BUTTON_GPIO (active-low, falling edge)."""
    GPIO.output(BUTTON_GPIO, GPIO.LOW)
    time.sleep(0.15)
    GPIO.output(BUTTON_GPIO, GPIO.HIGH)
    time.sleep(0.2)


@pytest.fixture(scope="function")
def setup_hardware():
    """Setup and teardown for ADC challenge hardware testing."""
    GPIO.setwarnings(False)
    try:
        GPIO.setmode(GPIO.BCM)
    except Exception:
        pass

    GPIO.setup(BUTTON_GPIO, GPIO.OUT, initial=GPIO.HIGH)  # button not pressed

    bus = smbus2.SMBus(1)  # I2C bus 1 (GPIO 2 = SDA, GPIO 3 = SCL)
    write_dac(bus, DAC_A0_ADDR, 0)  # start at 0 V

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
    time.sleep(0.5)  # Wait for MCU to initialize

    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    ser.reset_input_buffer()

    yield bus, ser

    # Teardown
    write_dac(bus, DAC_A0_ADDR, 0)
    GPIO.output(BUTTON_GPIO, GPIO.HIGH)
    ser.close()
    bus.close()
    GPIO.cleanup()
