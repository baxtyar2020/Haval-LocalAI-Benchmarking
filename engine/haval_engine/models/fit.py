from __future__ import annotations

import re

from haval_engine.hardware import hardware_snapshot, nvidia_smi


def accel_memory_bytes() -> int:
    smi = nvidia_smi() or ""
    total = 0
    for line in smi.splitlines():
        match = re.search(r"(\d+)\s*MiB", line)
        if match:
            total += int(match.group(1)) * 1024 * 1024
    if total:
        return total
    hw = hardware_snapshot()
    ram_gb = float(hw.get("ram_gb") or 0)
    # Unified / shared-memory fallback: treat half of system RAM as accelerator budget.
    return int(ram_gb * 0.5 * 1024**3)


def estimate_fit(model_bytes: int | None, size_hint_gb: float | None = None) -> dict:
    accel = accel_memory_bytes()
    size = int(model_bytes or 0)
    if size <= 0 and size_hint_gb:
        size = int(size_hint_gb * 1024**3)
    if accel <= 0 or size <= 0:
        return {
            "level": "mar",
            "label": "Fit unknown",
            "needed_gb": round(size / 1024**3, 1) if size else None,
            "accel_gb": round(accel / 1024**3, 1) if accel else None,
        }
    needed = size * 1.25  # weights + rough KV-cache headroom
    ratio = needed / accel
    if ratio <= 0.5:
        level, label = "exc", "Excellent fit"
    elif ratio <= 0.75:
        level, label = "str", "Strong fit"
    elif ratio <= 1.0:
        level, label = "mar", "Partial fit"
    else:
        level, label = "no", "Not suitable"
    return {
        "level": level,
        "label": label,
        "needed_gb": round(needed / 1024**3, 1),
        "accel_gb": round(accel / 1024**3, 1),
        "ratio": round(ratio, 2),
    }
