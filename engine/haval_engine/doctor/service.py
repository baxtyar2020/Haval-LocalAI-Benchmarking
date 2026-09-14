from __future__ import annotations

import json
import threading
import time
from datetime import datetime, timezone
from typing import Any, Callable

from haval_engine import hardware
from haval_engine.ollama import client as ollama
from haval_engine.ollama import install as ollama_install
from haval_engine.ollama.process import start_ollama, stop_stale_ollama
from haval_engine.ollama.runtime import locate
from haval_engine.doctor.probe_model import DEFAULT_PROBE_MODEL, is_hidden_probe_model, pick_probe_model
from haval_engine.paths import config_dir, locate_node, locate_python, snapshot_path, support_log_path
from haval_engine.winproc import run_hidden

Check = dict[str, Any]
Listener = Callable[[dict], None]


def _load_doctor_config() -> dict:
    path = config_dir() / "doctor.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {"cpu_only_eval_tok_s": {"conservative_max": 12}, "storage_reserve_gb": 10, "probe": {}}


def _log(line: str) -> None:
    stamp = datetime.now().strftime("%H:%M:%S")
    path = support_log_path()
    with path.open("a", encoding="utf-8") as fh:
        fh.write(f"[{stamp}] {line}\n")


def _check(
    check_id: str,
    title: str,
    detail: str,
    status: str,
    *,
    blocking: bool = False,
    action: str | None = None,
) -> Check:
    return {
        "id": check_id,
        "title": title,
        "detail": detail,
        "status": status,
        "blocking": blocking,
        "action": action,
    }


class DoctorService:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self.state = "idle"
        self.overall = "attention"
        self.subtitle = "Run Doctor to inspect this PC."
        self.checks: list[Check] = []
        self.hardware: dict = {}
        self.tech_log = ""
        self.models: list[dict] = []
        self.probe: dict = {}
        self.gate = {
            "ready": False,
            "environment_ready": False,
            "reasons": ["Doctor has not finished yet."],
        }
        self._listeners: list[Listener] = []
        self._in_flight = False
        self._restore()

    def snapshot(self) -> dict:
        with self._lock:
            return {
                "state": self.state,
                "overall": self.overall,
                "subtitle": self.subtitle,
                "checks": list(self.checks),
                "hardware": dict(self.hardware),
                "tech_log": self.tech_log,
                "models": list(self.models),
                "probe": dict(self.probe),
                "gate": dict(self.gate),
            }

    def _restore(self) -> None:
        path = snapshot_path()
        if not path.exists():
            return
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return
        self.checks = list(data.get("checks") or [])
        self.hardware = dict(data.get("hardware") or {})
        self.models = list(data.get("models") or [])
        self.probe = dict(data.get("probe") or {})
        self.gate = dict(data.get("gate") or self.gate)
        self.state = "idle"
        if self.checks:
            self._refresh_overall()

    def subscribe(self, listener: Listener) -> None:
        with self._lock:
            self._listeners.append(listener)

    def unsubscribe(self, listener: Listener) -> None:
        with self._lock:
            self._listeners = [item for item in self._listeners if item is not listener]

    def _emit(self) -> None:
        snap = self.snapshot()
        with self._lock:
            listeners = list(self._listeners)
        for listener in listeners:
            try:
                listener(snap)
            except Exception:
                pass

    def _set_checks(self, checks: list[Check], *, state: str | None = None) -> None:
        with self._lock:
            self.checks = checks
            if state:
                self.state = state
            self._refresh_overall()
        self._persist()
        self._emit()

    def _refresh_overall(self) -> None:
        if not self.checks:
            self.overall = "checking"
            self.subtitle = "Run Doctor to inspect this PC."
            self.gate = {
                "environment_ready": False,
                "ready": False,
                "reasons": ["Doctor has not finished yet."],
            }
            return
        statuses = [c["status"] for c in self.checks]
        blocking_fail = any(
            c.get("blocking") and c["status"] in {"failed", "blocked"} for c in self.checks
        )
        if self.state in {"running", "repairing"}:
            self.overall = "repairing" if self.state == "repairing" else "checking"
            self.subtitle = (
                "Checking this PC. Nothing here is hidden in a terminal window."
                if self.state == "running"
                else "Repairing automatically. This is safe and stays in the background."
            )
        elif blocking_fail:
            self.overall = "attention"
            self.subtitle = "Some items need a fix before benchmarking. We can repair most of them automatically."
        elif "warning" in statuses:
            self.overall = "ready"
            self.subtitle = "Ready, with notes. Acceleration is working; read the list for anything to watch."
        else:
            self.overall = "ready"
            self.subtitle = "All blocking prerequisites are healthy. This PC is ready to benchmark local models."
        reasons: list[str] = []
        if blocking_fail:
            reasons.extend(
                c["detail"]
                for c in self.checks
                if c.get("blocking") and c["status"] in {"failed", "blocked"}
            )
        if not self.models:
            reasons.append("Install and select at least one model.")
        self.gate = {
            "environment_ready": not blocking_fail and self.state == "idle",
            "ready": (not blocking_fail) and self.state == "idle" and bool(self.models),
            "reasons": reasons,
        }

    def _persist(self) -> None:
        snap = {
            "saved_at": datetime.now(timezone.utc).isoformat(),
            "overall": self.overall,
            "hardware": self.hardware,
            "checks": self.checks,
            "models": self.models,
            "probe": self.probe,
            "gate": self.gate,
        }
        snapshot_path().write_text(json.dumps(snap, indent=2), encoding="utf-8")
        self.tech_log = support_log_path().read_text(encoding="utf-8")[-8000:] if support_log_path().exists() else ""

    def run_async(self, *, repair: bool = False) -> None:
        with self._lock:
            if self.state in {"running", "repairing"} or self._in_flight:
                return
            self._in_flight = True
        threading.Thread(target=self._run, kwargs={"repair": repair}, daemon=True).start()

    def _run(self, *, repair: bool) -> None:
        _log("doctor pass started")
        try:
            cfg = _load_doctor_config()
            if repair:
                self._repair_chain(cfg)
            done = threading.Event()
            crash: list[BaseException] = []

            def diagnose() -> None:
                try:
                    self._diagnose(cfg)
                except BaseException as exc:  # noqa: BLE001
                    crash.append(exc)
                finally:
                    done.set()

            threading.Thread(target=diagnose, daemon=True, name="doctor-diagnose").start()
            if not done.wait(55):
                _log("doctor diagnose exceeded 55s; releasing the UI")
                with self._lock:
                    self.state = "idle"
                    for item in self.checks:
                        if item.get("status") in {"checking", "repairing"}:
                            item["status"] = "warning"
                            item["blocking"] = False
                            item["detail"] = (
                                str(item.get("detail") or "")
                                + " Released so this screen never stays stuck."
                            ).strip()
                    if not self.checks:
                        self.checks = [
                            _check(
                                "doctor",
                                "Doctor",
                                "The check took too long and was released so the app never stays stuck.",
                                "warning",
                            )
                        ]
                    self._refresh_overall()
                self._persist()
                self._emit()
                return
            if crash:
                raise crash[0]
        except Exception as exc:  # noqa: BLE001
            _log(f"doctor crashed: {exc}")
            self._set_checks(
                [_check("doctor", "Doctor", str(exc), "failed", blocking=True)],
                state="idle",
            )
        else:
            with self._lock:
                self.state = "idle"
                self._refresh_overall()
            self._persist()
            self._emit()
        finally:
            with self._lock:
                self._in_flight = False
                if self.state in {"running", "repairing"}:
                    self.state = "idle"
                    self._refresh_overall()

    def _mark(self, checks: list[Check], check_id: str, **fields: Any) -> None:
        for item in checks:
            if item["id"] == check_id:
                item.update(fields)
        self._set_checks(checks)

    def _diagnose(self, cfg: dict) -> None:
        checks: list[Check] = [
            _check("windows", "Windows 11", "Checking Windows version…", "checking", blocking=True),
            _check("runtime", "Application runtime", "Checking Visual C++ components…", "checking"),
            _check("scoring", "Hidden-test runtimes", "Checking bundled Node and Python…", "checking", blocking=True),
            _check("hardware", "Hardware", "Detecting CPU, GPU, and memory…", "checking"),
            _check("ollama_exe", "Ollama installed", "Searching standard and custom locations…", "checking", blocking=True),
            _check("ollama_api", "Ollama service", "Checking the local API…", "checking", blocking=True),
            _check("storage", "Storage", "Measuring free disk space…", "checking", blocking=True),
            _check("models", "Installed models", "Asking Ollama for the local inventory…", "checking"),
            _check("probe", "Hardware acceleration", "Waiting for the live probe…", "checking", blocking=True),
        ]
        self._set_checks(checks, state="running")

        ok, detail = hardware.is_windows_11()
        _log(f"windows: {detail}")
        self._mark(checks, "windows", detail=detail, status="passed" if ok else "failed")

        vok, vdetail = hardware.vcpp_present()
        _log(f"vcpp: {vdetail}")
        self._mark(checks, "runtime", detail=vdetail, status="passed" if vok else "warning")

        py = locate_python()
        node = locate_node()
        scoring_parts: list[str] = []
        scoring_ok = True
        if py:
            scoring_parts.append(f"Python at {py}")
        else:
            scoring_ok = False
            scoring_parts.append("bundled Python is missing")
        if node:
            node_label = "Node"
            try:
                ver = run_hidden([str(node), "-v"], timeout=8)
                node_label = (ver.stdout or ver.stderr or "").strip() or "Node"
            except Exception:
                pass
            scoring_parts.append(f"{node_label} at {node}")
        else:
            scoring_ok = False
            scoring_parts.append("Node.js is missing — Phase 2 coding hidden tests would score 0")
        scoring_detail = "; ".join(scoring_parts)
        _log(f"scoring runtimes: {scoring_detail}")
        self._mark(
            checks,
            "scoring",
            detail=scoring_detail if scoring_ok else (
                "Reinstall from the Haval setup package so Node and Python ship with the app. " + scoring_detail
            ),
            status="passed" if scoring_ok else "failed",
        )

        hw = hardware.hardware_snapshot()
        self.hardware = hw
        gpu = hw.get("gpu", "Unknown graphics")
        cpu = hw.get("cpu", "Unknown processor")
        ram = hw.get("ram_gb", "?")
        mem = hw.get("memory_label") or f"{ram} GB"
        kind = hw.get("memory_kind") or "memory"
        host = hw.get("computer_name") or "This PC"
        hdetail = f"{host} · {cpu} · {gpu} · {mem} {kind}"
        _log(f"hardware: {hdetail}")
        if hw.get("nvidia_smi"):
            _log(f"nvidia-smi: {hw['nvidia_smi']}")
        self._mark(checks, "hardware", detail=hdetail, status="passed")

        exe, version = locate()
        if exe:
            _log(f"ollama exe: {exe} ({version})")
            self._mark(
                checks,
                "ollama_exe",
                detail=f"{version} at {exe}",
                status="passed",
                action=None,
            )
        else:
            _log("ollama exe: not found")
            self._mark(
                checks,
                "ollama_exe",
                detail="Ollama is not installed in a known location.",
                status="failed",
                action="Install",
            )

        api_ok, payload = ollama.tags(timeout=3)
        if not api_ok and exe:
            _log("api down; attempting start")
            started, msg = start_ollama()
            _log(msg)
            api_ok, payload = ollama.tags(timeout=3)
        if api_ok:
            _log("GET /api/tags HTTP 200")
            self._mark(checks, "ollama_api", detail="Local API responding at 127.0.0.1:11434.", status="passed", action=None)
        else:
            err = payload.get("error") if isinstance(payload, dict) else payload
            _log(f"GET /api/tags failed: {err}")
            self._mark(
                checks,
                "ollama_api",
                detail="The local Ollama API is not responding.",
                status="failed",
                action="Start",
            )

        reserve = float(cfg.get("storage_reserve_gb") or 10)
        free = float(hw.get("disk_free_gb") or 0)
        total = hw.get("disk_total_gb")
        if free >= reserve:
            self._mark(
                checks,
                "storage",
                detail=f"{free} GB free" + (f" of {total} GB." if total else "."),
                status="passed",
            )
        elif free >= 2:
            self._mark(
                checks,
                "storage",
                detail=f"{free} GB free — below the {reserve:.0f} GB operating reserve.",
                status="warning",
                action="Free space",
            )
        else:
            self._mark(
                checks,
                "storage",
                detail=f"Only {free} GB free. Downloads need more space.",
                status="failed",
                action="Free space",
            )

        models: list[dict] = []
        if api_ok:
            models = list(payload.get("models") or [])
        visible = [m for m in models if not is_hidden_probe_model(m.get("name"))]
        self.models = visible
        if visible:
            names = ", ".join(m.get("name", "?") for m in visible[:6])
            extra = f" (+{len(visible) - 6} more)" if len(visible) > 6 else ""
            self._mark(checks, "models", detail=f"{len(visible)} installed · {names}{extra}", status="passed")
        else:
            probe_ready = bool(
                pick_probe_model(models, list((cfg.get("probe") or {}).get("fallback_models") or []))
            )
            detail = "No benchmark models are installed yet."
            if probe_ready:
                detail += " A hidden acceleration probe is on this PC and is not shown in Models."
            else:
                detail += " Repair can add a tiny hidden probe for Doctor."
            self._mark(
                checks,
                "models",
                detail=detail,
                status="warning",
                action="Need model",
            )

        probe = self._probe(cfg, api_ok=api_ok, models=models, hw=hw)
        self.probe = probe
        self._mark(
            checks,
            "probe",
            detail=probe["detail"],
            status=probe["status"],
            blocking=probe["status"] in {"failed", "blocked"},
            action=probe.get("action"),
        )

        with self._lock:
            self.checks = checks
            self._refresh_overall()
        self._persist()
        self._emit()

    def _probe(self, cfg: dict, *, api_ok: bool, models: list[dict], hw: dict) -> dict:
        if not api_ok:
            return {
                "status": "failed",
                "detail": "Acceleration cannot be proven until the Ollama API is running.",
                "action": "Start",
            }
        probe_cfg = cfg.get("probe") or {}
        model = pick_probe_model(models, list(probe_cfg.get("fallback_models") or []))
        if not model:
            visible_names = [str(m.get("name") or "?") for m in models if not is_hidden_probe_model(m.get("name"))]
            names = ", ".join(visible_names[:8]) or "none"
            return {
                "status": "warning",
                "detail": (
                    "The tiny hidden probe model is not installed yet, so live GPU proof was skipped. "
                    "Installed roster models were not loaded just to check Doctor. "
                    f"You can still benchmark ({names}). Repair can add {DEFAULT_PROBE_MODEL}."
                ),
                "action": "Probe model",
                "classification": "no_small_model",
            }
        _log(f"probe model: {model}")
        result = ollama.generate_stream(
            model,
            probe_cfg.get("prompt") or "Reply with a single word: ready.",
            int(probe_cfg.get("num_predict") or 32),
            timeout=float(probe_cfg.get("timeout_s") or 12),
            stall_s=float(probe_cfg.get("stall_s") or 8),
            wall_s=float(probe_cfg.get("wall_s") or 20),
        )
        if not result.get("ok"):
            _log(f"probe generate failed: {result.get('error')}")
            return {
                "status": "warning",
                "detail": (
                    f"Live probe on {model} did not finish ({result.get('error') or 'unknown error'}). "
                    "Doctor will not keep waiting. You can still use installed models."
                ),
                "action": "Re-probe",
                "classification": "probe_timeout",
            }
        loaded = ollama.ps()
        split = _processor_split(loaded, model)
        tok_s = float(result.get("tok_s") or 0)
        ttft = result.get("ttft_ms")
        cpu_max = float((cfg.get("cpu_only_eval_tok_s") or {}).get("conservative_max") or 12)
        gpu_name = str(hw.get("gpu") or "")
        has_named_gpu = gpu_name and "no discrete" not in gpu_name.lower()
        vram_share = split["size_vram"] / split["size"] if split["size"] else 0
        _log(
            f"probe ttft_ms={ttft} tok/s={tok_s:.2f} size={split['size']} size_vram={split['size_vram']}"
        )
        classification = "pass"
        detail = (
            f"{model} answered on this PC ({tok_s:.1f} tok/s"
            + (f", first token {ttft:.0f} ms" if ttft else "")
            + ")."
        )
        status = "passed"
        action = None
        if split["size_vram"] > 0 and vram_share >= 0.85:
            classification = "full_gpu"
            detail = f"Fully accelerated on {gpu_name or 'the GPU'}. {detail}"
        elif split["size_vram"] > 0:
            classification = "partial_offload"
            status = "warning"
            detail = f"Meaningful GPU acceleration with some CPU offload ({vram_share:.0%} on GPU). {detail}"
        elif has_named_gpu and tok_s <= cpu_max:
            classification = "cpu_only_false"
            status = "failed"
            action = "Re-probe"
            detail = (
                f"Looks like CPU-only even though {gpu_name} is present "
                f"({tok_s:.1f} tok/s, no VRAM residency). Repair will restart Ollama and probe again."
            )
        elif not has_named_gpu:
            classification = "igpu_or_unified"
            detail = f"Acceleration looks like iGPU/APU/shared memory. {detail}"
        return {
            "status": status,
            "detail": detail,
            "action": action,
            "classification": classification,
            "model": model,
            "tok_s": tok_s,
            "ttft_ms": ttft,
            "size": split["size"],
            "size_vram": split["size_vram"],
        }

    def _repair_chain(self, cfg: dict) -> None:
        self._set_checks(
            [_check("repair", "Repair", "Starting automatic repair…", "repairing")],
            state="repairing",
        )
        exe, _ = locate()
        if not exe:
            _log("repair: downloading official Ollama installer")
            try:
                setup = ollama_install.download_ollama_installer()
                _log(f"repair: downloaded {setup}")
                msg = ollama_install.run_ollama_installer(setup)
                _log(msg)
                time.sleep(2)
            except Exception as exc:  # noqa: BLE001
                _log(f"repair install failed: {exc}")
                raise RuntimeError(
                    "Could not install Ollama automatically. Organizational policy may be blocking the installer."
                ) from exc
        api_ok, _ = ollama.tags(timeout=2)
        if not api_ok:
            _log("repair: stop stale then start")
            _log(stop_stale_ollama())
            ok, msg = start_ollama()
            _log(msg)
            if not ok:
                raise RuntimeError(msg)
        models_ok, payload = ollama.tags(timeout=4)
        models = list((payload or {}).get("models") or []) if models_ok else []
        probe_cfg = cfg.get("probe") or {}
        if not pick_probe_model(models, list(probe_cfg.get("fallback_models") or [])):
            fallback = (cfg.get("probe") or {}).get("fallback_models") or [DEFAULT_PROBE_MODEL]
            name = fallback[0]
            _log(f"repair: pulling probe model {name}")
            self._pull(name)
        _log("repair: re-probe after chain")

    def _pull(self, name: str) -> None:
        import json
        import urllib.request

        body = json.dumps({"name": name, "stream": False}).encode("utf-8")
        req = urllib.request.Request(
            "http://127.0.0.1:11434/api/pull",
            data=body,
            method="POST",
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=600) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
        _log(f"pull {name}: {raw[:200]}")


def _processor_split(ps_payload: dict, model: str) -> dict[str, int]:
    for item in ps_payload.get("models") or []:
        name = str(item.get("name") or item.get("model") or "")
        if model in name or name in model:
            return {
                "size": int(item.get("size") or 0),
                "size_vram": int(item.get("size_vram") or 0),
            }
    if ps_payload.get("models"):
        item = ps_payload["models"][0]
        return {
            "size": int(item.get("size") or 0),
            "size_vram": int(item.get("size_vram") or 0),
        }
    return {"size": 0, "size_vram": 0}


SERVICE = DoctorService()
