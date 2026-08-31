from __future__ import annotations

import json
import threading
import time
import uuid

from haval_engine.doctor.probe_model import is_hidden_probe_model
from haval_engine.ollama import client as ollama
from haval_engine.ollama.pull import delete_model, pull_stream, registry_search
from haval_engine.models.fit import accel_memory_bytes, estimate_fit
from haval_engine.models.params import parse_params, total_b_value
from haval_engine.ollama.runtime import load_settings, save_settings
from haval_engine.paths import config_dir, support_log_path
from haval_engine.hardware import hardware_snapshot

STATES = (
    "not_installed",
    "queued",
    "downloading",
    "paused",
    "verifying",
    "completed",
    "failed",
    "cancelled",
)


def _log(line: str) -> None:
    with support_log_path().open("a", encoding="utf-8") as fh:
        fh.write(f"[models] {line}\n")


def _catalog() -> list[dict]:
    path = config_dir() / "preferred-models.json"
    if not path.exists():
        return []
    return list(json.loads(path.read_text(encoding="utf-8")).get("models") or [])


def _parse_hint_gb(text: str | None) -> float | None:
    if not text:
        return None
    digits = "".join(ch for ch in text if ch.isdigit() or ch == ".")
    try:
        return float(digits) if digits else None
    except ValueError:
        return None


def _fmt_size(n: int | None) -> str:
    if not n:
        return "Size unknown"
    gb = n / 1024**3
    if gb >= 1:
        return f"{gb:.1f} GB"
        return f"{n / 1024**2:.0f} MB"


def _params_size_sort_key(row: dict) -> tuple:
    total = total_b_value(row.get("params_total"))
    name = str(row.get("display_name") or row.get("name") or "").lower()
    if total is None:
        return (1, 10**9, name)
    return (0, total, name)


class ModelLibrary:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self.jobs: dict[str, dict] = {}
        self.order: list[str] = []
        self._cancel: set[str] = set()
        self._worker = threading.Thread(target=self._loop, daemon=True)
        self._worker.start()

    def enqueue(self, name: str) -> dict:
        name = name.strip()
        if not name:
            raise ValueError("Model name is required.")
        with self._lock:
            for job in self.jobs.values():
                if job["name"] == name and job["state"] in {"queued", "downloading", "verifying"}:
                    return job
            job_id = str(uuid.uuid4())[:8]
            job = {
                "id": job_id,
                "name": name,
                "state": "queued",
                "pct": 0,
                "stage": "Queued",
                "completed": 0,
                "total": 0,
                "error": None,
            }
            self.jobs[job_id] = job
            self.order.append(job_id)
            _log(f"queued {name}")
            return dict(job)

    def cancel(self, job_id: str) -> dict | None:
        with self._lock:
            job = self.jobs.get(job_id)
            if not job:
                return None
            self._cancel.add(job_id)
            if job["state"] == "queued":
                job["state"] = "cancelled"
                job["stage"] = "Cancelled"
            return dict(job)

    def retry(self, job_id: str) -> dict | None:
        with self._lock:
            job = self.jobs.get(job_id)
            if not job:
                return None
            job.update({"state": "queued", "pct": 0, "stage": "Queued", "error": None})
            if job_id not in self.order:
                self.order.append(job_id)
            self._cancel.discard(job_id)
            return dict(job)

    def _loop(self) -> None:
        while True:
            job_id = None
            with self._lock:
                for jid in list(self.order):
                    job = self.jobs.get(jid)
                    if job and job["state"] == "queued":
                        job_id = jid
                        job["state"] = "downloading"
                        job["stage"] = "Downloading"
                        break
            if not job_id:
                time.sleep(0.4)
                continue
            self._run_job(job_id)

    def _run_job(self, job_id: str) -> None:
        with self._lock:
            name = self.jobs[job_id]["name"]

        def on_event(event: dict) -> None:
            completed = int(event.get("completed") or 0)
            total = int(event.get("total") or 0)
            status = str(event.get("status") or "Downloading")
            pct = int(completed * 100 / total) if total else (5 if status else 0)
            with self._lock:
                job = self.jobs[job_id]
                job["completed"] = completed
                job["total"] = total
                job["pct"] = min(99, pct)
                job["stage"] = status[:48] or "Downloading"
                if event.get("error"):
                    job["error"] = str(event["error"])

        result = pull_stream(name, on_event, lambda: job_id in self._cancel)
        with self._lock:
            job = self.jobs[job_id]
            if result == "cancelled" or job_id in self._cancel:
                job["state"] = "cancelled"
                job["stage"] = "Cancelled"
                self._cancel.discard(job_id)
                _log(f"cancelled {name}")
                return
            if result == "failed":
                job["state"] = "failed"
                job["stage"] = "Failed"
                job["error"] = job.get("error") or "Download failed."
                _log(f"failed {name}: {job['error']}")
                return
            job["state"] = "verifying"
            job["stage"] = "Verifying"
            job["pct"] = 99
        validation = self._validate(name)
        with self._lock:
            job = self.jobs[job_id]
            job["validation"] = validation
            if validation["class"] == "failed_to_load":
                job["state"] = "failed"
                job["stage"] = "Failed to load"
                job["error"] = validation["detail"]
            else:
                job["state"] = "completed"
                job["stage"] = "Completed"
                job["pct"] = 100
            _log(f"validated {name}: {validation['class']}")

    def _validate(self, name: str) -> dict:
        ok, payload = ollama.tags(timeout=8)
        names = {m.get("name") for m in (payload.get("models") or [])} if ok else set()
        if name not in names and not any(str(n).startswith(name) for n in names):
            return {"class": "failed_to_load", "detail": "Pull finished but the model is not in Ollama’s inventory."}
        info = next((m for m in (payload.get("models") or []) if m.get("name") == name or str(m.get("name")).startswith(name)), {})
        size = int(info.get("size") or 0)
        fit = estimate_fit(size)
        if size and size <= 8 * 1024**3:
            probe = ollama.generate_stream(name, "Reply with one word: ready.", 24)
            loaded = ollama.ps()
            vram = 0
            total = 0
            for item in loaded.get("models") or []:
                vram += int(item.get("size_vram") or 0)
                total += int(item.get("size") or 0)
            if not probe.get("ok"):
                return {"class": "failed_to_load", "detail": probe.get("error") or "Load test failed."}
            if vram and total and vram / total < 0.4:
                return {"class": "partial_offload", "detail": "Ready with partial offload."}
            if fit["level"] == "no":
                return {"class": "not_suitable", "detail": "Installed, but this hardware is unlikely to accelerate it well."}
            return {"class": "ready", "detail": "Ready."}
        if fit["level"] == "no":
            return {"class": "not_suitable", "detail": "Installed, but too large for reliable acceleration on this PC."}
        return {"class": "not_verified", "detail": "Installed but not load-tested (model is large)."}

    def snapshot(self, *, filter_name: str = "Installed", query: str = "") -> dict:
        ok, payload = ollama.tags(timeout=6)
        installed = [
            m
            for m in (payload.get("models") or [])
            if ok and not is_hidden_probe_model(m.get("name"))
        ]
        catalog = _catalog()
        selected = [n for n in list(load_settings().get("selected_models") or []) if not is_hidden_probe_model(n)]
        if len(selected) > 1:
            selected = selected[:1]
            save_settings({"selected_models": selected})
        jobs = [j for j in self.jobs.values() if not is_hidden_probe_model(j.get("name"))]
        hw = hardware_snapshot()
        items = self._rows(installed, catalog, jobs, selected, filter_name, query)
        disk_free = hw.get("disk_free_gb")
        disk_total = hw.get("disk_total_gb")
        return {
            "ollama_ok": ok,
            "storage": {"free_gb": disk_free, "total_gb": disk_total},
            "accel_gb": round(accel_memory_bytes() / 1024**3, 1),
            "jobs": jobs,
            "items": items,
            "selected": list(selected),
            "installed_count": len(installed),
        }

    def _rows(
        self,
        installed: list[dict],
        catalog: list[dict],
        jobs: list[dict],
        selected: list[str] | set[str],
        filter_name: str,
        query: str,
    ) -> list[dict]:
        from haval_engine.ollama.registry import precision_of

        by_name: dict[str, dict] = {}

        def upsert(key: str, **fields: object) -> dict:
            row = by_name.setdefault(key, {"id": key, "name": key})
            for k, v in fields.items():
                if v is None:
                    continue
                if k == "display_name" and row.get("preferred") and row.get("display_name"):
                    continue
                row[k] = v
            return row

        for cat in catalog:
            pull = cat["pull"]
            upsert(
                pull,
                display_name=cat.get("display_name"),
                tag=cat.get("tag"),
                family=cat.get("family"),
                params=cat.get("params"),
                quant=cat.get("quant"),
                size_hint=cat.get("size_hint"),
                preferred=True,
                roster_order=cat.get("roster_order"),
                installed=False,
            )

        for model in installed:
            name = str(model.get("name") or "")
            details = model.get("details") or {}
            extra_details = details
            existing = by_name.get(name) or {}
            catalog_params = str(existing.get("params") or "")
            ollama_params = extra_details.get("parameter_size")
            params = catalog_params if "-A" in catalog_params.upper() else (ollama_params or catalog_params)
            upsert(
                name,
                display_name=existing.get("display_name") or name.split(":")[0].replace("hf.co/", "").split("/")[-1],
                tag=existing.get("tag") or (name.split(":")[-1] if ":" in name else "latest"),
                family=extra_details.get("family") or existing.get("family"),
                params=params,
                quant=extra_details.get("quantization_level") or existing.get("quant"),
                size_bytes=int(model.get("size") or 0),
                digest=model.get("digest"),
                installed=True,
                preferred=existing.get("preferred", False)
                or any(name == c["pull"] or str(c["pull"]) in name for c in catalog),
            )

        for job in jobs:
            row = upsert(job["name"], download=job)
            if job["state"] == "completed":
                row["installed"] = True

        rows = list(by_name.values())
        for row in rows:
            size = int(row.get("size_bytes") or 0)
            hint = _parse_hint_gb(str(row.get("size_hint") or ""))
            row["size_label"] = _fmt_size(size) if size else (row.get("size_hint") or "Size unknown")
            row["fit"] = estimate_fit(size or None, hint)
            validation = (row.get("download") or {}).get("validation") or {}
            if row.get("installed") and not validation:
                if row["fit"]["level"] == "no":
                    validation = {"class": "not_suitable", "detail": "Likely too large for this hardware."}
                else:
                    validation = {"class": "ready" if size and size <= 8 * 1024**3 else "not_verified", "detail": ""}
            row["validation"] = validation
            failed_load = validation.get("class") == "failed_to_load"
            downloading = (row.get("download") or {}).get("state") in {"queued", "downloading", "verifying"}
            row["selected"] = row["id"] in selected or row.get("name") in selected
            row["selectable"] = bool(row.get("installed")) and not failed_load and not downloading
            row.setdefault("preferred", False)
            row.setdefault("installed", False)
            parsed = parse_params(row.get("params"), row.get("name"), row.get("display_name"), row.get("tag"))
            row["params_total"] = parsed["total"]
            row["params_active"] = parsed["active"]
            row["params_moe"] = parsed["moe"]
            row["params_label"] = parsed["label"]
            row["quant"] = precision_of(
                name=str(row.get("name") or ""),
                tag=str(row.get("tag") or ""),
                quant=str(row.get("quant") or ""),
            )

        q = query.strip().lower()
        if filter_name == "Preferred":
            rows = [r for r in rows if r.get("preferred")]
            rows.sort(key=_params_size_sort_key)
        elif filter_name == "Search Ollama":
            hits = registry_search(query) if q else []
            extra = []
            for hit in hits:
                name = str(hit.get("name") or "")
                existing = by_name.get(name)
                if existing:
                    existing["pull_command"] = f"ollama pull {existing.get('name')}"
                    extra.append(existing)
                    continue
                parsed = parse_params(
                    hit.get("params_label"),
                    name,
                    hit.get("display_name"),
                    hit.get("tag"),
                )
                extra.append(
                    {
                        "id": name,
                        "name": name,
                        "display_name": hit.get("display_name") or name.split(":")[0],
                        "tag": hit.get("tag") or (name.split(":")[-1] if ":" in name else ""),
                        "description": hit.get("description"),
                        "quant": hit.get("quant") or precision_of(name=name, tag=str(hit.get("tag") or "")),
                        "preferred": False,
                        "installed": False,
                        "selectable": False,
                        "selected": False,
                        "size_label": "Unknown until download",
                        "params_total": hit.get("params_total") or parsed["total"],
                        "params_active": hit.get("params_active") or parsed["active"],
                        "params_moe": hit.get("params_moe") if "params_moe" in hit else parsed["moe"],
                        "params_label": hit.get("params_label") or parsed["label"],
                        "pull_command": hit.get("pull_command") or f"ollama pull {name}",
                        "fit": estimate_fit(None),
                        "validation": {},
                    }
                )
            rows = extra
        else:
            rows = [r for r in rows if r.get("installed")]
            rows.sort(key=_params_size_sort_key)
        return [r for r in rows if not is_hidden_probe_model(r.get("name"))]

    def set_selected(self, name: str, selected: bool) -> list[str]:
        if is_hidden_probe_model(name):
            return list(load_settings().get("selected_models") or [])
        if selected:
            current = [name]
        else:
            current = [n for n in (load_settings().get("selected_models") or []) if n != name]
        save_settings({"selected_models": current})
        return current

    def remove(self, name: str) -> tuple[bool, str]:
        ok, msg = delete_model(name)
        if ok:
            current = set(load_settings().get("selected_models") or [])
            current.discard(name)
            save_settings({"selected_models": sorted(current)})
        return ok, msg


LIBRARY = ModelLibrary()
