import pytest
import time
import math
import threading
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from conftest import write_dac, sinus_dac_code, press_button, DAC_A0_ADDR

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
        {'label': str, 'value': int, 'ts': float}

    Handles the Teleplot format: >LABEL:VALUE
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
                        samples.append(
                            {"label": label, "value": int(val_str), "ts": ts}
                        )
                    except ValueError:
                        pass
        except Exception:
            pass
    return samples


def dac_to_adc_expected(t, phase=0.0, freq=1.0, amplitude=0.4, offset=0.5):
    """Expected ADC count (0–1023) for a given elapsed time t.

    DAC outputs 0–2.5 V (internal VREF); Nucleo ADC reference is 3.3 V.
    ADC = (Vdac / ADC_VREF) * 1023  =  (v * DAC_VREF / ADC_VREF) * 1023
    """
    v = offset + amplitude * math.sin(2 * math.pi * freq * t + phase)
    v = max(0.0, min(1.0, v))
    return int(v * (DAC_VREF / ADC_VREF) * 1023)


def pearson_r(x, y):
    """Compute Pearson correlation coefficient between two arrays."""
    x = np.array(x, dtype=float)
    y = np.array(y, dtype=float)
    if len(x) < 2:
        return 0.0
    xm = x - x.mean()
    ym = y - y.mean()
    denom = np.sqrt((xm**2).sum() * (ym**2).sum())
    return float(np.dot(xm, ym) / denom) if denom > 0 else 0.0


def save_comparison_chart(ts, received, t0_offset, filename):
    """Save a two-panel comparison chart (received valAdc vs expected sinus)."""
    os.makedirs(ARTIFACTS_DIR, exist_ok=True)

    expected = [dac_to_adc_expected(t + t0_offset) for t in ts]

    # Continuous expected curve for plotting
    if ts:
        t_plot = np.linspace(0, max(ts), 500)
        exp_curve = [dac_to_adc_expected(t + t0_offset) for t in t_plot]
    else:
        t_plot, exp_curve = [], []

    fig, axes = plt.subplots(2, 1, figsize=(12, 8))

    axes[0].plot(t_plot, exp_curve, "b-", linewidth=1.5, alpha=0.7,
                 label="Expected (generated sinus)")
    axes[0].scatter(ts, received, c="orange", s=10, zorder=5,
                    label="Received valAdc (serial)")
    axes[0].set_xlabel("Time (s)")
    axes[0].set_ylabel("ADC counts (0–1023)")
    axes[0].set_title("ADC Challenge: Generated Sinus vs Received valAdc")
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    residual = [r - e for r, e in zip(received, expected)]
    axes[1].plot(ts, residual, "g-", linewidth=0.8)
    axes[1].axhspan(-50, 50, color="grey", alpha=0.2, label="±50 ADC count band")
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

def test_no_output_initially(setup_hardware):
    """No >valAdc: lines must appear when ADC conversion is disabled."""
    _, ser = setup_hardware
    samples = collect_serial_timed(ser, 2.0)
    adc_samples = [s for s in samples if s["label"] == "valAdc"]
    assert len(adc_samples) == 0, (
        f"Expected no valAdc output initially, but received {len(adc_samples)} samples"
    )
    print("✓ No ADC output received when disabled")


def test_adc_starts_on_button_press(setup_hardware):
    """Pressing the button must start ADC conversion output."""
    _, ser = setup_hardware

    print("Pressing button to enable ADC...")
    press_button()

    samples = collect_serial_timed(ser, 2.0)
    adc_samples = [s for s in samples if s["label"] == "valAdc"]

    assert len(adc_samples) >= 15, (
        f"Expected ≥15 valAdc samples after enabling, got {len(adc_samples)}"
    )
    print(f"✓ Received {len(adc_samples)} valAdc samples after button press")


def test_sampling_rate_100ms(setup_hardware):
    """ADC sampling rate must be approximately 100 ms (± 20 ms)."""
    _, ser = setup_hardware

    press_button()  # enable ADC

    samples = collect_serial_timed(ser, 3.0)
    adc_ts = [s["ts"] for s in samples if s["label"] == "valAdc"]

    assert len(adc_ts) >= 10, (
        f"Too few samples ({len(adc_ts)}) to compute sampling interval"
    )

    intervals = [adc_ts[i] - adc_ts[i - 1] for i in range(1, len(adc_ts))]
    median_interval = float(np.median(intervals))
    print(f"Sampling interval: median={median_interval*1000:.1f} ms "
          f"(from {len(intervals)} intervals)")

    assert 0.080 <= median_interval <= 0.120, (
        f"Sampling interval {median_interval*1000:.1f} ms is outside 80–120 ms range"
    )
    print("✓ Sampling rate is approximately 100 ms")


def test_adc_tracks_sinus_signal(setup_hardware):
    """valAdc must track a 1 Hz sinus generated on DAC A0 when ADC is enabled."""
    bus, ser = setup_hardware

    stop_flag = threading.Event()
    t0 = time.time()

    def dac_loop():
        while not stop_flag.is_set():
            code = sinus_dac_code(time.time() - t0)
            write_dac(bus, DAC_A0_ADDR, code)

    # Start the DAC thread BEFORE enabling the ADC so that A0 already carries
    # the sinus signal when the first timer ISR fires after the button press.
    # Without this, the first conversion would read 0 V (DAC idle value).
    thread = threading.Thread(target=dac_loop, daemon=True)
    thread.start()
    time.sleep(0.05)  # let at least one I2C write complete before enabling ADC

    press_button()  # enable ADC — first conversion will see sinus value, not 0

    # The ADC samples at 100 ms intervals; collect 2 cycles (2 s)
    collection_start = time.time()
    samples = collect_serial_timed(ser, 2.0)

    stop_flag.set()
    thread.join(timeout=1.0)

    adc_samples = [s for s in samples if s["label"] == "valAdc"]
    assert len(adc_samples) >= 10, (
        f"Too few valAdc samples ({len(adc_samples)}) for correlation analysis"
    )

    # Timestamps are relative to collection_start; sinus time = ts + (collection_start - t0)
    offset = collection_start - t0
    ts = [s["ts"] for s in adc_samples]
    received = [s["value"] for s in adc_samples]
    expected = [dac_to_adc_expected(t + offset) for t in ts]

    r = pearson_r(received, expected)
    print(f"valAdc Pearson R = {r:.3f} ({len(adc_samples)} samples)")

    save_comparison_chart(ts, received, offset, "adcs_challenge_comparison.png")

    assert r > 0.90, (
        f"valAdc does not track sinus signal (Pearson R = {r:.3f}, need > 0.90)"
    )
    print("✓ valAdc correctly tracks generated sinus signal")


def test_adc_stops_on_second_button_press(setup_hardware):
    """Pressing the button a second time must stop ADC output."""
    _, ser = setup_hardware

    # First press: enable
    print("First press: enabling ADC...")
    press_button()

    # Verify the first press actually enabled the ADC before proceeding
    samples_enabled = collect_serial_timed(ser, 1.0)
    adc_enabled = [s for s in samples_enabled if s["label"] == "valAdc"]
    assert len(adc_enabled) >= 5, (
        f"First button press did not enable ADC: expected ≥5 valAdc samples in 1 s, "
        f"got {len(adc_enabled)}"
    )
    print(f"✓ First press confirmed: {len(adc_enabled)} valAdc samples received")

    # Second press: disable
    print("Second press: disabling ADC...")
    press_button()
    time.sleep(0.5)

    # Flush any buffered data
    ser.reset_input_buffer()

    # Collect for 2 s — should see no valAdc lines
    samples = collect_serial_timed(ser, 2.0)
    adc_samples = [s for s in samples if s["label"] == "valAdc"]

    assert len(adc_samples) == 0, (
        f"Expected no valAdc output after disabling, but received {len(adc_samples)} samples"
    )
    print("✓ ADC output stopped after second button press")
