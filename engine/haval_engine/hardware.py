from __future__ import annotations

import math
import os
import re
import shutil
import socket
import threading
import time
from collections import Counter
from pathlib import Path

from haval_engine.winproc import run_hidden

_IGPU_HINTS = (
    "uhd graphics",
    "iris",
    "radeon graphics",
    "vega graphics",
    "adreno",
    "microsoft basic",
    "orise",
)
_DGPU_HINTS = (
    "geforce",
    "rtx ",
    "gtx ",
    "quadro",
    "tesla",
    "radeon rx",
    "radeon pro",
    "arc a",
    "intel arc",
)

_HW_TTL_S = 12.0
_smi_cache: tuple[float, str | None] | None = None
_hw_cache: tuple[float, dict] | None = None


def windows_build() -> int | None:
    try:
        import winreg

        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion")
        build, _ = winreg.QueryValueEx(key, "CurrentBuildNumber")
        return int(str(build))
    except OSError:
        return None


def is_windows_11() -> tuple[bool, str]:
    if os.name != "nt":
        return False, f"{os.name} is not Windows 11."
    build = windows_build()
    if build is None:
        return False, "Could not read the Windows build number."
    if build >= 22000:
        return True, f"Windows 11 (build {build})."
    return False, f"Windows build {build} is below 22000. This app requires Windows 11."


def computer_name() -> str:
    for value in (
        os.environ.get("COMPUTERNAME"),
        os.environ.get("HOSTNAME"),
    ):
        if value and str(value).strip():
            return str(value).strip()
    try:
        host = socket.gethostname()
        if host and host.strip():
            return host.strip()
    except OSError:
        pass
    return "This PC"


def _wmi_query_inner() -> dict:
    info: dict = {}
    try:
        import wmi  # type: ignore

        c = wmi.WMI()
        cpus = c.Win32_Processor()
        if cpus:
            info["cpu"] = cpus[0].Name.strip()
            info["cores"] = int(cpus[0].NumberOfCores or 0)
            info["threads"] = int(cpus[0].NumberOfLogicalProcessors or 0)
        gpus = c.Win32_VideoController()
        names = [g.Name.strip() for g in gpus if g.Name]
        if names:
            info["gpu"] = names[0]
            info["gpus"] = names
        ram = 0
        for stick in c.Win32_PhysicalMemory():
            ram += int(stick.Capacity or 0)
        if ram:
            info["ram_gb"] = round(ram / (1024**3), 1)
    except Exception:
        pass
    return info


def _wmi_query() -> dict:
    box: dict = {}

    def work() -> None:
        box.update(_wmi_query_inner())

    t = threading.Thread(target=work, daemon=True, name="wmi-hw")
    t.start()
    t.join(3.0)
    return dict(box)


def os_label() -> str:
    if os.name != "nt":
        return os.name
    ok, detail = is_windows_11()
    if ok:
        return detail.rstrip(".")
    build = windows_build()
    if build:
        return f"Windows (build {build})"
    return "Windows"


def round_up_half(value: float | int | None) -> float | None:
    """Round VRAM up to the next 0.5 GB (98.2 → 98.5, 98.9 → 99)."""
    if value is None:
        return None
    n = float(value)
    if n <= 0:
        return 0.0
    stepped = math.ceil(n * 2 - 1e-9) / 2.0
    return stepped


def format_gb(value: float | int | None) -> str:
    n = round_up_half(value)
    if n is None:
        return "—"
    if abs(n - round(n)) < 0.05:
        return f"{int(round(n))} GB"
    return f"{n:.1f} GB"


def parse_nvidia_gpus(text: str | None) -> list[tuple[str, float]]:
    rows: list[tuple[str, float]] = []
    for line in (text or "").splitlines():
        line = line.strip()
        if not line:
            continue
        name = line.split(",")[0].strip()
        gb = _smi_vram_gb(line) or 0.0
        if name:
            rows.append((name, gb))
    return rows


def gpu_card_copy(smi_text: str | None, fallback_name: str = "") -> dict:
    rows = parse_nvidia_gpus(smi_text)
    if not rows and fallback_name:
        return {"title": fallback_name, "count": 1, "vram_gb": None, "vram_label": ""}
    if not rows:
        return {"title": fallback_name or "No discrete GPU name reported", "count": 0, "vram_gb": None, "vram_label": ""}
    names = [n for n, _ in rows]
    counts = Counter(names)
    if len(counts) == 1:
        name, n = next(iter(counts.items()))
        title = f"{n}× {name}" if n > 1 else name
    else:
        title = " + ".join(f"{c}× {name}" if c > 1 else name for name, c in counts.items())
    total = sum(gb for _, gb in rows)
    rounded = round_up_half(total)
    return {"title": title, "count": len(rows), "vram_gb": rounded, "vram_label": format_gb(total)}


def _smi_vram_gb(text: str) -> float | None:
    # "NVIDIA GeForce RTX 4070, 12282 MiB"
    parts = [p.strip() for p in text.split(",")]
    if len(parts) < 2:
        return None
    m = re.search(r"([\d.]+)\s*(MiB|GiB|MB|GB)", parts[1], re.I)
    if not m:
        return None
    n = float(m.group(1))
    unit = m.group(2).lower()
    if unit in {"mib", "mb"}:
        return round(n / 1024, 1)
    return round(n, 1)


def _looks_discrete_gpu(name: str) -> bool:
    n = (name or "").lower()
    if any(h in n for h in _DGPU_HINTS):
        return True
    if any(h in n for h in _IGPU_HINTS):
        return False
    if "nvidia" in n:
        return True
    return False


def nvidia_smi() -> str | None:
    global _smi_cache
    now = time.monotonic()
    if _smi_cache and now - _smi_cache[0] < _HW_TTL_S:
        return _smi_cache[1]
    smi = shutil.which("nvidia-smi")
    if not smi:
        _smi_cache = (now, None)
        return None
    try:
        result = run_hidden(
            [smi, "--query-gpu=name,memory.total", "--format=csv,noheader"],
            timeout=6,
        )
    except Exception:
        _smi_cache = (now, None)
        return None
    text = (result.stdout or "").strip() or None
    _smi_cache = (now, text)
    return text


def vcpp_present() -> tuple[bool, str]:
    try:
        import winreg

        key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\x64",
        )
        installed, _ = winreg.QueryValueEx(key, "Installed")
        if int(installed) == 1:
            ver, _ = winreg.QueryValueEx(key, "Version")
            return True, f"Visual C++ x64 runtime {ver}."
    except OSError:
        pass
    # Presence of common VC++ DLLs is enough to continue.
    system32 = Path(os.environ.get("SystemRoot", r"C:\Windows")) / "System32"
    if (system32 / "vcruntime140.dll").exists():
        return True, "Visual C++ runtime DLLs are present."
    return False, "Visual C++ runtime was not detected. The installer can add it when permitted."


def hardware_snapshot() -> dict:
    global _hw_cache
    now = time.monotonic()
    if _hw_cache and now - _hw_cache[0] < _HW_TTL_S:
        return dict(_hw_cache[1])
    info = _wmi_query()
    try:
        import psutil

        if "ram_gb" not in info:
            info["ram_gb"] = round(psutil.virtual_memory().total / (1024**3), 1)
        disk = psutil.disk_usage(os.environ.get("SystemDrive", "C:") + "\\")
        info["disk_free_gb"] = round(disk.free / (1024**3), 1)
        info["disk_total_gb"] = round(disk.total / (1024**3), 1)
        try:
            info["cpu_percent"] = psutil.cpu_percent(interval=0.15)
        except Exception:
            pass
    except Exception:
        pass
    nv = nvidia_smi()
    vram_gb = None
    gpu_card = {"title": None, "count": 0, "vram_gb": None, "vram_label": ""}
    if nv:
        info["nvidia_smi"] = nv
        gpu_card = gpu_card_copy(nv, "")
        if "gpu" not in info:
            info["gpu"] = gpu_card["title"]
        vram_gb = gpu_card.get("vram_gb")
    info.setdefault("cpu", "Unknown processor")
    info.setdefault("gpu", gpu_card.get("title") or "No discrete GPU name reported")
    info["computer_name"] = computer_name()
    info["os_label"] = os_label()
    if gpu_card.get("title"):
        info["gpu"] = gpu_card["title"]
        info["gpu_title"] = gpu_card["title"]
        info["gpu_count"] = gpu_card["count"]
        info["gpu_vram_label"] = gpu_card["vram_label"]
    gpu_name = str(info.get("gpu") or "")
    has_dgpu = bool(vram_gb) or _looks_discrete_gpu(gpu_name)
    info["vram_gb"] = vram_gb
    info["unified_memory"] = not has_dgpu
    ram = info.get("ram_gb")
    info["memory_kind"] = "Unified memory" if not has_dgpu else "System memory"
    info["memory_gb"] = ram
    if ram is None:
        info["memory_label"] = "—"
    elif abs(float(ram) - round(float(ram))) < 0.05:
        info["memory_label"] = f"{int(round(float(ram)))} GB"
    else:
        info["memory_label"] = f"{float(ram):.1f} GB"
    _hw_cache = (now, dict(info))
    return info


_usage_cache: tuple[float, dict] | None = None
_cpu_primed = False


def _parse_smi_usage(text: str) -> tuple[float | None, float | None]:
    used = 0.0
    total = 0.0
    utils: list[float] = []
    for line in (text or "").splitlines():
        parts = [p.strip().rstrip("%") for p in line.split(",")]
        if len(parts) < 2:
            continue
        try:
            used += float(parts[0])
            total += float(parts[1])
            if len(parts) >= 3 and parts[2] != "":
                utils.append(float(parts[2]))
        except ValueError:
            continue
    vram_pct = round(100.0 * used / total) if total > 0 else None
    gpu_util = round(sum(utils) / len(utils)) if utils else None
    return vram_pct, gpu_util


def live_usage() -> dict:
    """CPU / RAM / VRAM percents for the live benchmark meters. Cached ~1s."""
    global _usage_cache, _cpu_primed
    now = time.monotonic()
    if _usage_cache and now - _usage_cache[0] < 1.0:
        return dict(_usage_cache[1])
    out: dict = {"cpu_pct": None, "ram_pct": None, "vram_pct": None}
    try:
        import psutil

        if not _cpu_primed:
            out["cpu_pct"] = int(round(psutil.cpu_percent(interval=0.05)))
            _cpu_primed = True
        else:
            out["cpu_pct"] = int(round(psutil.cpu_percent(interval=None)))
        out["ram_pct"] = int(round(psutil.virtual_memory().percent))
    except Exception:
        pass
    smi = shutil.which("nvidia-smi")
    if smi:
        try:
            result = run_hidden(
                [smi, "--query-gpu=memory.used,memory.total,utilization.gpu", "--format=csv,noheader,nounits"],
                timeout=4,
            )
            vram_pct, _gpu = _parse_smi_usage(result.stdout or "")
            if vram_pct is not None:
                out["vram_pct"] = int(vram_pct)
        except Exception:
            pass
    _usage_cache = (now, dict(out))
    return out
