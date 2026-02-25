import pytest
import time
import math
import threading
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from conftest import write_dac, sinus_dac_code, DAC_A0_ADDR, DAC_A1_ADDR

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

    Handles the Teleplot format:  >LABEL:VALUE
    and the XY-position format:  >position:VRx:VRy|xy
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
                # XY position line: "position:VRx:VRy|xy"
                if rest.startswith("position:") and "|xy" in rest:
                    samples.append({"label": "position", "value": line, "ts": ts})
                else:
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
    if len(x) < 2 or len(y) < 2:
        return 0.0
    xm = x - x.mean()
    ym = y - y.mean()
    denom = np.sqrt((xm**2).sum() * (ym**2).sum())
    return float(np.dot(xm, ym) / denom) if denom > 0 else 0.0


def save_comparison_chart(times, received, expected_fn, filename, label, phase=0.0):
    """Save a two-panel comparison chart (received vs expected)."""
    os.makedirs(ARTIFACTS_DIR, exist_ok=True)

    # Reconstruct expected curve from sample timestamps
    exp = [expected_fn(t, phase=phase) for t in times]

    fig, axes = plt.subplots(2, 1, figsize=(12, 8))

    # Top: overlay
    axes[0].plot(times, exp, "b-", linewidth=1.5, label="Expected (generated sinus)")
    axes[0].scatter(times, received, c="orange", s=8, zorder=5, label="Received (ADC)")
    axes[0].set_xlabel("Time (s)")
    axes[0].set_ylabel("ADC counts (0–1023)")
    axes[0].set_title(f"{label}: Generated vs Received")
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    # Bottom: residual
    residual = [r - e for r, e in zip(received, exp)]
    axes[1].plot(times, residual, "g-", linewidth=1.0)
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

def test_vrx_output_present(setup_hardware):
    """VRx values must appear in the serial output."""
    _, ser = setup_hardware
    samples = collect_serial_timed(ser, 3.0)
    vrx = [s for s in samples if s["label"] == "VRx"]
    assert len(vrx) >= 1, "No VRx values received over serial in 3 seconds"
    print(f"✓ Received {len(vrx)} VRx samples")


def test_vry_output_present(setup_hardware):
    """VRy values must appear in the serial output."""
    _, ser = setup_hardware
    samples = collect_serial_timed(ser, 3.0)
    vry = [s for s in samples if s["label"] == "VRy"]
    assert len(vry) >= 1, "No VRy values received over serial in 3 seconds"
    print(f"✓ Received {len(vry)} VRy samples")


def test_position_format_present(setup_hardware):
    """Serial output must contain a correctly formatted position line."""
    _, ser = setup_hardware
    samples = collect_serial_timed(ser, 3.0)
    pos = [s for s in samples if s["label"] == "position"]
    assert len(pos) >= 1, "No position lines (>position:VRx:VRy|xy) found in 3 seconds"
    # Verify format
    example = pos[0]["value"]
    assert "|xy" in example, f"Position line missing '|xy' suffix: {example!r}"
    print(f"✓ Position line format OK: {example!r}")


def test_vrx_tracks_sinus_signal(setup_hardware):
    """VRx must track a 1 Hz sinus generated on DAC A0 (0x4E)."""
    bus, ser = setup_hardware

    stop_flag = threading.Event()
    t0 = time.time()

    def dac_loop():
        while not stop_flag.is_set():
            code = sinus_dac_code(time.time() - t0)
            write_dac(bus, DAC_A0_ADDR, code)

    thread = threading.Thread(target=dac_loop, daemon=True)
    thread.start()

    samples = collect_serial_timed(ser, 2.0)
    stop_flag.set()
    thread.join(timeout=1.0)

    vrx = [s for s in samples if s["label"] == "VRx"]
    assert len(vrx) >= 20, f"Too few VRx samples ({len(vrx)}) for correlation analysis"

    ts = [s["ts"] for s in vrx]
    received = [s["value"] for s in vrx]
    expected = [dac_to_adc_expected(t) for t in ts]

    r = pearson_r(received, expected)
    print(f"VRx Pearson R = {r:.3f} ({len(vrx)} samples)")

    save_comparison_chart(
        ts, received, dac_to_adc_expected, "analog_serial_vrx_comparison.png",
        label="VRx"
    )

    assert r > 0.90, f"VRx does not track sinus signal (Pearson R = {r:.3f}, need > 0.90)"
    print("✓ VRx correctly tracks sinus signal")


def test_vry_tracks_sinus_signal(setup_hardware):
    """VRy must track a 1 Hz sinus generated on DAC A1 (0x4C)."""
    bus, ser = setup_hardware

    stop_flag = threading.Event()
    t0 = time.time()

    def dac_loop():
        while not stop_flag.is_set():
            code = sinus_dac_code(time.time() - t0)
            write_dac(bus, DAC_A1_ADDR, code)

    thread = threading.Thread(target=dac_loop, daemon=True)
    thread.start()

    samples = collect_serial_timed(ser, 2.0)
    stop_flag.set()
    thread.join(timeout=1.0)

    vry = [s for s in samples if s["label"] == "VRy"]
    assert len(vry) >= 20, f"Too few VRy samples ({len(vry)}) for correlation analysis"

    ts = [s["ts"] for s in vry]
    received = [s["value"] for s in vry]
    expected = [dac_to_adc_expected(t) for t in ts]

    r = pearson_r(received, expected)
    print(f"VRy Pearson R = {r:.3f} ({len(vry)} samples)")

    save_comparison_chart(
        ts, received, dac_to_adc_expected, "analog_serial_vry_comparison.png",
        label="VRy"
    )

    assert r > 0.90, f"VRy does not track sinus signal (Pearson R = {r:.3f}, need > 0.90)"
    print("✓ VRy correctly tracks sinus signal")


def test_antiphase_signals_and_xy_position(setup_hardware):
    """VRx and VRy must each correlate with anti-phase sinus signals,
    and position lines must be present and correctly formatted.

    DAC 0x4E → VRx (phase 0)
    DAC 0x4C → VRy (phase π)
    """
    bus, ser = setup_hardware

    stop_flag = threading.Event()
    t0 = time.time()

    def dac_a0_loop():
        while not stop_flag.is_set():
            write_dac(bus, DAC_A0_ADDR, sinus_dac_code(time.time() - t0, phase=0.0))

    def dac_a1_loop():
        while not stop_flag.is_set():
            write_dac(bus, DAC_A1_ADDR, sinus_dac_code(time.time() - t0, phase=math.pi))

    t_a0 = threading.Thread(target=dac_a0_loop, daemon=True)
    t_a1 = threading.Thread(target=dac_a1_loop, daemon=True)
    t_a0.start()
    t_a1.start()

    samples = collect_serial_timed(ser, 3.0)

    stop_flag.set()
    t_a0.join(timeout=1.0)
    t_a1.join(timeout=1.0)

    vrx = [s for s in samples if s["label"] == "VRx"]
    vry = [s for s in samples if s["label"] == "VRy"]
    pos = [s for s in samples if s["label"] == "position"]

    assert len(vrx) >= 20, f"Too few VRx samples ({len(vrx)})"
    assert len(vry) >= 20, f"Too few VRy samples ({len(vry)})"
    assert len(pos) >= 1, "No position lines found"

    # --- VRx correlation with phase=0 sinus ---
    ts_x = [s["ts"] for s in vrx]
    rec_x = [s["value"] for s in vrx]
    exp_x = [dac_to_adc_expected(t, phase=0.0) for t in ts_x]
    r_x = pearson_r(rec_x, exp_x)
    print(f"VRx Pearson R (phase=0) = {r_x:.3f}")

    # --- VRy correlation with phase=π sinus ---
    ts_y = [s["ts"] for s in vry]
    rec_y = [s["value"] for s in vry]
    exp_y = [dac_to_adc_expected(t, phase=math.pi) for t in ts_y]
    r_y = pearson_r(rec_y, exp_y)
    print(f"VRy Pearson R (phase=π) = {r_y:.3f}")

    # --- Position format check ---
    example_pos = pos[0]["value"]
    assert "|xy" in example_pos, f"Position line missing '|xy': {example_pos!r}"

    # --- Save waveform comparison chart ---
    os.makedirs(ARTIFACTS_DIR, exist_ok=True)

    # Continuous expected curves for plotting
    t_plot = np.linspace(0, 3.0, 500)
    exp_x_curve = [dac_to_adc_expected(t, phase=0.0) for t in t_plot]
    exp_y_curve = [dac_to_adc_expected(t, phase=math.pi) for t in t_plot]

    fig, axes = plt.subplots(2, 1, figsize=(12, 8))

    # Top: time-domain overlay
    axes[0].plot(t_plot, exp_x_curve, "b-", linewidth=1.5, alpha=0.6,
                 label="Expected VRx (phase=0)")
    axes[0].plot(t_plot, exp_y_curve, "r-", linewidth=1.5, alpha=0.6,
                 label="Expected VRy (phase=π)")
    axes[0].scatter(ts_x, rec_x, c="blue", s=6, zorder=5, label="Received VRx")
    axes[0].scatter(ts_y, rec_y, c="orange", s=6, zorder=5, label="Received VRy")
    axes[0].set_xlabel("Time (s)")
    axes[0].set_ylabel("ADC counts (0–1023)")
    axes[0].set_title("Anti-phase Signals: VRx (phase=0) and VRy (phase=π)")
    axes[0].legend(fontsize=8)
    axes[0].grid(True, alpha=0.3)

    # Bottom: residuals
    res_x = [r - e for r, e in zip(rec_x, exp_x)]
    res_y = [r - e for r, e in zip(rec_y, exp_y)]
    axes[1].plot(ts_x, res_x, "b-", linewidth=0.8, label="VRx residual")
    axes[1].plot(ts_y, res_y, "orange", linewidth=0.8, label="VRy residual")
    axes[1].axhspan(-50, 50, color="grey", alpha=0.2, label="±50 ADC count band")
    axes[1].set_xlabel("Time (s)")
    axes[1].set_ylabel("Residual (ADC counts)")
    axes[1].set_title("Residuals")
    axes[1].legend(fontsize=8)
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    wf_path = os.path.join(ARTIFACTS_DIR, "analog_serial_antiphase_waveforms.png")
    plt.savefig(wf_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved waveform chart: {wf_path}")

    # --- Save X-Y position chart ---
    # Parse position values: ">position:VRx_val:VRy_val|xy"
    pos_x_vals = []
    pos_y_vals = []
    for s in pos:
        try:
            line = s["value"]  # raw line stored as value for position entries
            body = line[1:]    # strip leading '>'
            # "position:VRx:VRy|xy"
            body = body.replace("|xy", "")
            _, vrx_str, vry_str = body.split(":")
            pos_x_vals.append(int(vrx_str))
            pos_y_vals.append(int(vry_str))
        except Exception:
            pass

    if pos_x_vals and pos_y_vals:
        fig2, ax2 = plt.subplots(figsize=(8, 8))
        ax2.plot(pos_x_vals, pos_y_vals, "b-", linewidth=1.0, alpha=0.5)
        ax2.scatter(pos_x_vals, pos_y_vals, c="orange", s=8, zorder=5)
        ax2.set_xlabel("VRx (ADC counts)")
        ax2.set_ylabel("VRy (ADC counts)")
        ax2.set_title("X-Y Position Plot (anti-phase: should be a diagonal line)")
        ax2.grid(True, alpha=0.3)
        plt.tight_layout()
        xy_path = os.path.join(ARTIFACTS_DIR, "analog_serial_xy_position.png")
        plt.savefig(xy_path, dpi=150, bbox_inches="tight")
        plt.close()
        print(f"Saved X-Y chart: {xy_path}")

    assert r_x > 0.90, (
        f"VRx does not correlate with generated sinus (phase=0): R={r_x:.3f}, need > 0.90"
    )
    assert r_y > 0.90, (
        f"VRy does not correlate with generated sinus (phase=π): R={r_y:.3f}, need > 0.90"
    )
    print("✓ VRx and VRy correctly track their respective anti-phase sinus signals")
    print(f"✓ Position format correct: {example_pos!r}")
