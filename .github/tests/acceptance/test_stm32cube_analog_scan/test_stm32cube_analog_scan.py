import pytest
import time
import math
import threading
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from conftest import write_dac, sinus_dac_code, DAC_A0_ADDR

ARTIFACTS_DIR = "../../../../artifacts"

# Voltage references — DAC outputs 0–2.5 V, Nucleo ADC reference is 3.3 V
DAC_VREF = 2.5
ADC_VREF = 3.3


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def collect_serial_timed(ser, duration):
    """Read serial lines for *duration* seconds and return parsed samples.

    Returns a list of dicts:
        {'label': str, 'value': int|float, 'ts': float}

    Handles the Teleplot format:  >LABEL:VALUE
    Integer values (e.g. potADC) and float values (e.g. temp) are both parsed.
    """
    ser.reset_input_buffer()  # discard any stale data before the collection window
    samples = []
    start = time.time()
    while time.time() - start < duration:
        try:
            raw = ser.readline()
            ts = time.time() - start
            if not raw:
                continue
            line = raw.decode("utf-8", errors="ignore").strip()
            if line.startswith(">") and ":" in line:
                rest = line[1:]  # strip leading '>'
                parts = rest.split(":", 1)
                if len(parts) == 2:
                    label, val_str = parts
                    try:
                        value = int(val_str)
                    except ValueError:
                        try:
                            value = float(val_str)
                        except ValueError:
                            continue
                    samples.append({"label": label, "value": value, "ts": ts})
        except Exception:
            pass
    return samples


def dac_to_adc_expected(t, phase=0.0, freq=1.0, amplitude=0.4, offset=0.5):
    """Expected ADC count (0–4095) for a given elapsed time t.

    DAC outputs 0–2.5 V (internal VREF); Nucleo ADC reference is 3.3 V.
    ADC = (Vdac / ADC_VREF) * 4095  =  (v * DAC_VREF / ADC_VREF) * 4095
    """
    v = offset + amplitude * math.sin(2 * math.pi * freq * t + phase)
    v = max(0.0, min(1.0, v))
    return int(v * (DAC_VREF / ADC_VREF) * 4095)


def pearson_r(x, y):
    """Compute Pearson correlation coefficient between two arrays."""
    x = np.array(x, dtype=float)
    y = np.array(y, dtype=float)
    if len(x) < 2 or len(y) < 2:
        return 0.0
    xm = x - x.mean()
    ym = y - y.mean()
    denom = np.sqrt((xm**2).sum() * (ym**2).sum())
    return float(np.dot(xm, ym) / denom) if denom > 0 else 0.0


def save_comparison_chart(times, received, expected_fn, filename, label, phase=0.0):
    """Save a two-panel comparison chart (received vs expected)."""
    os.makedirs(ARTIFACTS_DIR, exist_ok=True)

    exp = [expected_fn(t, phase=phase) for t in times]

    fig, axes = plt.subplots(2, 1, figsize=(12, 8))

    axes[0].plot(times, exp, "b-", linewidth=1.5, label="Expected (generated sinus)")
    axes[0].scatter(times, received, c="orange", s=8, zorder=5, label="Received (ADC)")
    axes[0].set_xlabel("Time (s)")
    axes[0].set_ylabel("ADC counts (0–4095)")
    axes[0].set_title(f"{label}: Generated vs Received")
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    residual = [r - e for r, e in zip(received, exp)]
    axes[1].plot(times, residual, "g-", linewidth=1.0)
    axes[1].axhspan(-200, 200, color="grey", alpha=0.2, label="±200 ADC count band")
    axes[1].set_xlabel("Time (s)")
    axes[1].set_ylabel("Residual (ADC counts)")
    axes[1].set_title("Residual (Received − Expected)")
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    path = os.path.join(ARTIFACTS_DIR, filename)
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved chart: {path}")


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_potadc_output_present(setup_hardware):
    """potADC values must appear in the serial output."""
    _, ser = setup_hardware
    samples = collect_serial_timed(ser, 3.0)
    potadc = [s for s in samples if s["label"] == "potADC"]
    assert len(potadc) >= 1, "No potADC values received over serial in 3 seconds"
    print(f"✓ Received {len(potadc)} potADC samples")


def test_temp_output_present(setup_hardware):
    """temp values must appear in the serial output."""
    _, ser = setup_hardware
    samples = collect_serial_timed(ser, 3.0)
    temp = [s for s in samples if s["label"] == "temp"]
    assert len(temp) >= 1, "No temp values received over serial in 3 seconds"
    print(f"✓ Received {len(temp)} temp samples")


def test_potadc_tracks_sinus_signal(setup_hardware):
    """potADC must track a 1 Hz sinus generated on DAC A0 (0x4E)."""
    bus, ser = setup_hardware

    stop_flag = threading.Event()
    t0 = time.time()

    def dac_loop():
        while not stop_flag.is_set():
            code = sinus_dac_code(time.time() - t0)
            write_dac(bus, DAC_A0_ADDR, code)

    thread = threading.Thread(target=dac_loop, daemon=True)
    thread.start()

    samples = collect_serial_timed(ser, 3.0)
    stop_flag.set()
    thread.join(timeout=1.0)

    potadc = [s for s in samples if s["label"] == "potADC"]
    assert len(potadc) >= 20, f"Too few potADC samples ({len(potadc)}) for correlation analysis"

    ts = [s["ts"] for s in potadc]
    received = [s["value"] for s in potadc]
    expected = [dac_to_adc_expected(t) for t in ts]

    r = pearson_r(received, expected)
    print(f"potADC Pearson R = {r:.3f} ({len(potadc)} samples)")

    save_comparison_chart(
        ts, received, dac_to_adc_expected,
        "stm32cube_analog_scan_potadc_comparison.png",
        label="potADC"
    )

    assert r > 0.90, f"potADC does not track sinus signal (Pearson R = {r:.3f}, need > 0.90)"
    print("✓ potADC correctly tracks sinus signal")


def test_temp_in_valid_range(setup_hardware):
    """temp values must be within a plausible internal MCU temperature range (15–50 °C)."""
    _, ser = setup_hardware
    samples = collect_serial_timed(ser, 3.0)
    temp_samples = [s for s in samples if s["label"] == "temp"]
    assert len(temp_samples) >= 1, "No temp values received over serial in 3 seconds"

    values = [s["value"] for s in temp_samples]
    out_of_range = [v for v in values if not (15.0 <= v <= 50.0)]
    assert len(out_of_range) == 0, (
        f"Some temp values are outside 15–50 °C range: {out_of_range[:5]}"
    )
    avg = sum(values) / len(values)
    print(f"✓ All {len(values)} temp samples within 15–50 °C (avg = {avg:.2f} °C)")
