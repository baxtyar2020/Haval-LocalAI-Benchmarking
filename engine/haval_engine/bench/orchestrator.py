from __future__ import annotations

import json
import os
import threading
import time
from collections import defaultdict

from haval_engine.bench.display_text import phase1_question, phase2_question
from haval_engine.data.store import RunStore
from haval_engine.doctor.service import SERVICE as DOCTOR
from haval_engine.grading.engine import grade_output
from haval_engine.hardware import live_usage
from haval_engine.models.fit import accel_memory_bytes
from haval_engine.ollama import client as ollama
from haval_engine.ollama.runtime import load_settings
from haval_engine.pack import load_fixture, load_scenarios
from haval_engine.report.render import generate_report
from haval_engine.paths import support_log_path
from haval_engine.scoring.pipeline import (
    match_label,
    mean,
    persona_quality,
    phase1_score,
    quality,
    reliability,
    role_speed_band,
    speed_band,
)


def _log(line: str) -> None:
    with support_log_path().open("a", encoding="utf-8") as fh:
        fh.write(f"[bench] {line}\n")


from haval_engine.scoring.fail_reason import (
    fail_payload,
    phase1_all_hardware,
    phase1_all_roles_too_slow,
    phase1_any_role_continues,
    summarize_failures,
)
from haval_engine.scoring.rules import load_ruleset


def attempt_wall_s(scenario: dict, think: bool = False) -> float:
    """Hard cap: 2× the role budget. 1.5× or more is Not Recommended.

    Thinking on is allowed ~3× that wait so the hidden pass can finish before the answer.
    """
    base = max(20.0, float(scenario.get("total_s") or 90))
    wall = base * float(load_ruleset().get("speed_wall_multiple") or 2.0)
    return wall * 3.0 if think else wall


_CAP_ERRORS = {"cancelled", "wall_timeout", "repeat_loop", "output_cap"}

# Unscored practice ask: similar length to a Light prompt so the first scored
# question is not paying a cold first-token hitch.
WARMUP_PREDICT = 160
WARMUP_PROMPT = (
    "This is a warm-up. The answer is not scored.\n\n"
    "FACTS\n"
    "- Leave the house at 7:40am\n"
    "- Two kids need packed lunches\n"
    "- Trash goes out on Tuesday\n"
    "- Keys hang on the hook by the door\n\n"
    "Write a 6-line weekday morning checklist. Time first when a time is known.\n"
    "Do not add errands. No preamble. No tips.\n\n"
    "HARD LIMIT: 120 words."
)


def _grade_or_timeout(scenario: dict, text: str, seconds: float = 20) -> dict:
    box: dict = {}

    def work() -> None:
        try:
            box["g"] = grade_output(scenario, text)
        except Exception as exc:  # noqa: BLE001
            box["g"] = {
                "Q": 0.0,
                "hard_fail": True,
                "passed": False,
                "scores": {},
                "reasons": [f"grader:{exc}"],
            }

    t = threading.Thread(target=work, daemon=True, name="grade-cap")
    t.start()
    t.join(seconds)
    if t.is_alive() or "g" not in box:
        return {
            "Q": 0.0,
            "hard_fail": True,
            "passed": False,
            "scores": {},
            "reasons": ["grader_timeout"],
        }
    return box["g"]


def _prompt(scenario: dict) -> str:
    text = scenario["prompt"]
    fixture = load_fixture(scenario.get("fixture"))
    if fixture:
        import json

        text += "\n\n--- Fixture " + str(scenario.get("fixture")) + " ---\n"
        text += json.dumps(fixture, indent=2)[:12000]
    return text


class BenchRunner:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self.store = RunStore()
        self._stop = threading.Event()
        self._pause = threading.Event()
        self._pause.set()
        self._thread: threading.Thread | None = None
        self._run_t0: float | None = None
        self._listeners: list = []
        self.snapshot: dict = {
            "state": "idle",
            "run_id": None,
            "pct": 0,
            "message": "Press Start to begin the sequence",
            "detail": "",
            "model_index": 0,
            "model_count": 0,
            "elapsed_s": 0,
            "tok_s": None,
            "ttft_s": None,
            "headroom_gb": None,
            "cpu_pct": None,
            "ram_pct": None,
            "vram_pct": None,
            "completion_pct": None,
            "log": [],
            "selected": [],
            "thinking": False,
            "prompt": "",
            "answer": "",
            "task_title": "",
            "open_report": None,
        }

    def status(self) -> dict:
        with self._lock:
            snap = dict(self.snapshot)
            t0 = self._run_t0
            state = snap.get("state")
        snap.update(live_usage())
        if state in {"running", "paused"} and t0 is not None:
            snap["elapsed_s"] = round(time.perf_counter() - t0)
        if snap.get("state") == "idle":
            snap["thinking"] = bool(load_settings().get("thinking", False))
        return snap

    def subscribe(self, listener) -> None:
        with self._lock:
            self._listeners.append(listener)

    def unsubscribe(self, listener) -> None:
        with self._lock:
            self._listeners = [item for item in self._listeners if item is not listener]

    def _notify(self) -> None:
        snap = self.status()
        with self._lock:
            listeners = list(self._listeners)
        for listener in listeners:
            try:
                listener(snap)
            except Exception:
                pass

    def _emit(self, **fields: object) -> None:
        with self._lock:
            self.snapshot.update(fields)
            if fields.get("log_line"):
                lines = list(self.snapshot.get("log") or [])
                lines.append(str(fields["log_line"]))
                self.snapshot["log"] = lines[-80:]
        self._notify()

    def start(self, personas: list[str] | None = None, report_dir: str | None = None) -> dict:
        gate = DOCTOR.snapshot().get("gate") or {}
        if not gate.get("environment_ready"):
            return {"ok": False, "error": (gate.get("reasons") or ["Doctor is not ready."])[0]}
        selected = list(load_settings().get("selected_models") or [])
        if not selected:
            return {"ok": False, "error": "Select one model in the Model Library."}
        selected = selected[:1]
        think = bool(load_settings().get("thinking", False))
        think_label = "thinking on" if think else "thinking off"
        known = {str(s.get("persona")) for s in load_scenarios()}
        picked = [p for p in (personas or []) if p in known]
        if personas and not picked:
            return {"ok": False, "error": "Select at least one persona."}
        dest = (report_dir or "").strip() or (load_settings().get("default_report_dir") or "").strip() or None
        with self._lock:
            if self.snapshot.get("state") in {"running", "paused"}:
                return {"ok": False, "error": "A benchmark is already running."}
        self._stop.clear()
        self._pause.set()
        run_id = self.store.create_run(selected)
        self.store.set_status(
            run_id,
            "running",
            {"thinking": think, "personas": picked or None, "report_dir": dest},
        )
        n_p = len(picked) if picked else 20
        self._emit(
            state="running",
            run_id=run_id,
            pct=0,
            message="Starting benchmark",
            detail=f"{selected[0]} · {n_p} persona{'s' if n_p != 1 else ''} · Phase 2 capability pack · {think_label}",
            model_index=1,
            model_count=len(selected),
            elapsed_s=0,
            selected=selected,
            thinking=think,
            prompt="",
            answer="",
            task_title="",
            log=[],
            open_report=None,
        )
        self._thread = threading.Thread(
            target=self._loop,
            args=(run_id, selected, think, picked, dest),
            daemon=True,
        )
        self._thread.start()
        return {"ok": True, "run_id": run_id}

    def pause(self) -> dict:
        if self.snapshot.get("state") == "running":
            self._pause.clear()
            self._emit(state="paused", message="Paused — progress is saved")
        elif self.snapshot.get("state") == "paused":
            self._pause.set()
            self._emit(state="running", message="Resuming")
        return self.status()

    def stop(self) -> dict:
        self._stop.set()
        self._pause.set()
        if self.snapshot.get("state") in {"running", "paused"}:
            self._emit(message="Stopping — writing a report of what finished.", log_line="stop requested")
        return self.status()

    def _wait_pause(self) -> None:
        while not self._pause.is_set() and not self._stop.is_set():
            time.sleep(0.2)

    def _warmup(self, model: str, t0: float) -> None:
        prompt = WARMUP_PROMPT
        self._emit(
            message="Warming up the model",
            detail="Running one unpaid practice question so the first timed ask is not a cold start.",
            prompt=prompt,
            answer="",
            task_title="Warm-up",
            elapsed_s=round(time.perf_counter() - t0),
            log_line=f"warmup {model}",
        )
        for attempt in range(1, 4):
            self._wait_pause()
            if self._stop.is_set():
                return
            gen = ollama.generate_stream(
                model,
                prompt,
                num_predict=WARMUP_PREDICT,
                timeout=180,
                stall_s=15,
                wall_s=180,
                cancel=self._stop,
                think=False,
            )
            ttft = gen.get("ttft_ms")
            ttft_s = (float(ttft) / 1000.0) if ttft else None
            text = (gen.get("text") or "").strip()
            self._emit(
                elapsed_s=round(time.perf_counter() - t0),
                tok_s=round(float(gen.get("tok_s") or 0), 1) or None,
                ttft_s=round(ttft_s, 2) if ttft_s is not None else None,
                log_line=f"warmup attempt {attempt} ok={gen.get('ok')} ttft={ttft_s}",
            )
            if text:
                self._emit(
                    message="Model is ready",
                    detail="Starting scored scenarios.",
                    elapsed_s=round(time.perf_counter() - t0),
                    log_line="warmup complete",
                )
                return
            self._emit(log_line=f"warmup retry {attempt}: {gen.get('error') or 'empty'}")
        self._emit(log_line="warmup did not complete; scoring will start")

    def _loop(self, run_id: str, models: list[str], think: bool, personas: list[str] | None = None, report_dir: str | None = None) -> None:
        t0 = time.perf_counter()
        self._run_t0 = t0
        scenarios = load_scenarios()
        if personas:
            wanted = set(personas)
            scenarios = [s for s in scenarios if s.get("persona") in wanted]
        limit = os.environ.get("HAVAL_BENCH_MAX_SCENARIOS")
        if limit:
            scenarios = scenarios[: max(1, int(limit))]
        attempts_n = 1
        skip_phase2 = bool(os.environ.get("HAVAL_BENCH_SKIP_PHASE2"))
        phase1_units = max(1, len(models) * len(scenarios) * attempts_n)
        phase2_units = 0
        if not skip_phase2:
            from haval_engine.phase2.runner import pack_item_count

            phase2_units = pack_item_count() * max(1, len(models))
        total_units = max(1, phase1_units + phase2_units)
        done = 0
        model_summaries: list[dict] = []
        try:
            for mi, model in enumerate(models, start=1):
                if self._stop.is_set():
                    break
                _log(f"model {model}")
                self._emit(model_index=mi, model_count=len(models), message=f"{model}", log_line=f"load {model}")
                self._warmup(model, t0)
                if self._stop.is_set():
                    break
                h_samples: list[dict] = []
                by_scenario: dict[str, dict] = {}
                skip_p2 = skip_phase2
                for scenario in scenarios:
                    self._wait_pause()
                    if self._stop.is_set():
                        break
                    qs: list[float | None] = []
                    totals: list[float] = []
                    heads: list[float | None] = []
                    toks: list[float | None] = []
                    success = 0
                    for attempt in range(1, attempts_n + 1):
                        self._wait_pause()
                        if self._stop.is_set():
                            break
                        asked = _prompt(scenario)
                        shown = phase1_question(scenario)
                        self._emit(
                            message=f"Phase 1 · {scenario['persona']} · {scenario['intensity']}",
                            detail="",
                            prompt=shown,
                            answer="",
                            task_title="",
                            log_line=f"run {scenario['id']}",
                        )
                        wall = attempt_wall_s(scenario, think)
                        self._emit(
                            log_line=f"cap {scenario['id']} {wall:.0f}s",
                        )
                        gen = ollama.generate_stream(
                            model,
                            asked,
                            num_predict=8192 if think else 4096,
                            timeout=wall,
                            stall_s=min(12.0, wall),
                            wall_s=wall,
                            cancel=self._stop,
                            think=think,
                        )
                        ttft_s = (gen.get("ttft_ms") / 1000) if gen.get("ttft_ms") else None
                        total_s = (gen.get("total_ms") / 1000) if gen.get("total_ms") else None
                        err = str(gen.get("error") or "")
                        timed_out = err in _CAP_ERRORS or "timeout" in err.lower()
                        technical_ok = bool(gen.get("ok")) and bool((gen.get("text") or "").strip()) and not timed_out
                        if timed_out:
                            technical_ok = False
                            try:
                                ollama.unload(model)
                            except Exception:
                                pass
                        if err:
                            self._emit(log_line=f"skip {scenario['id']} {err}")
                        grade = {"Q": None, "hard_fail": True, "passed": False, "scores": {}}
                        if technical_ok:
                            grade = _grade_or_timeout(scenario, gen.get("text") or "")
                            if "grader_timeout" in (grade.get("reasons") or []):
                                technical_ok = False
                            else:
                                success += 1
                        fail_note = (
                            "This attempt hit the time cap and failed. Moving to the next test."
                            if timed_out
                            else ""
                        )
                        q = grade.get("Q") if technical_ok else None
                        qs.append(q)
                        if technical_ok and total_s is not None:
                            totals.append(total_s)
                        load_s = None
                        if gen.get("load_duration_ns"):
                            load_s = float(gen["load_duration_ns"]) / 1e9
                        ps = ollama.ps()
                        vram = 0
                        size = 0
                        for item in ps.get("models") or []:
                            if item.get("name") == model or str(item.get("name", "")).startswith(model):
                                vram += int(item.get("size_vram") or 0)
                                size += int(item.get("size") or 0)
                        try:
                            accel = accel_memory_bytes()
                        except Exception:
                            accel = 0
                        headroom = ((accel - vram) / accel) if accel else None
                        offload = (vram / size) if size else None
                        h_samples.append({"offload": offload, "headroom": headroom})
                        heads.append(headroom)
                        toks.append(gen.get("tok_s"))
                        self.store.add_attempt(
                            {
                                "run_id": run_id,
                                "model": model,
                                "scenario_id": scenario["id"],
                                "attempt": attempt,
                                "ok": technical_ok,
                                "ttft_s": ttft_s,
                                "total_s": total_s,
                                "tok_s": gen.get("tok_s"),
                                "load_s": load_s,
                                "prompt_tokens": gen.get("prompt_eval_count"),
                                "output_tokens": gen.get("eval_count"),
                                "q": q,
                                "e": headroom,
                                "hard_fail": grade.get("hard_fail"),
                                "error": None if technical_ok else (gen.get("error") or "incomplete"),
                                "output": (gen.get("text") or "")[:8000],
                                "grade": grade,
                            }
                        )
                        done += 1
                        self._emit(
                            pct=round(100 * done / total_units, 1),
                            elapsed_s=round(time.perf_counter() - t0),
                            tok_s=round(float(gen.get("tok_s") or 0), 1) or None,
                            ttft_s=round(ttft_s, 2) if ttft_s is not None else None,
                            headroom_gb=round((accel - vram) / 1024**3, 1) if accel and vram else None,
                            completion_pct=round(100 * done / total_units, 1),
                            prompt=shown,
                            answer=fail_note,
                            task_title=str(scenario.get("name") or ""),
                            log_line=f"ttft {ttft_s}s tok/s {gen.get('tok_s')} ok={technical_ok}",
                        )
                    finish = reliability(success, attempts_n)
                    answer = mean(qs)
                    speed = speed_band(mean(totals), float(scenario["total_s"]))
                    failed = success == 0
                    p1 = None if failed else phase1_score(
                        content=answer,
                        speed=speed,
                        answers=qs,
                        successful=success,
                        attempted=attempts_n,
                        headrooms=heads,
                        tok_s=toks,
                    )
                    rec = {
                        "run_id": run_id,
                        "model": model,
                        "scenario_id": scenario["id"],
                        "q": answer,
                        "e": mean(heads),
                        "r": finish,
                        "w": p1,
                        "internal": speed,
                        "customer": match_label(finish=finish, answer=p1, speed=speed),
                        "cap_reason": None,
                        "attempted": attempts_n,
                        "successful": success,
                        "persona": scenario["persona"],
                        "business": scenario["business"],
                        "intensity": scenario["intensity"],
                    }
                    self.store.upsert_scenario(rec)
                    by_scenario[scenario["id"]] = rec
                fail = None
                atts_m = [a for a in self.store.attempts_for(run_id) if a.get("model") == model]
                recs = list(by_scenario.values())
                recs = self._apply_role_speeds(model, recs, atts_m, scenarios)
                by_scenario = {r["scenario_id"]: r for r in recs}
                if not skip_p2 and not phase1_any_role_continues(recs, personas):
                    skip_p2 = True
                    if phase1_all_hardware(atts_m, thinking=think):
                        fail = fail_payload("hardware")
                    elif phase1_all_roles_too_slow(recs, personas):
                        fail = fail_payload("too_slow")
                    else:
                        fail = summarize_failures(atts_m, thinking=think)
                    self._emit(
                        message="Phase 1 complete — skipping Phase 2",
                        detail=(fail or {}).get("message") or "Every selected role failed.",
                        log_line=f"phase1 skip phase2 {(fail or {}).get('kind')}",
                    )
                phase2 = None
                if not skip_p2 and not self._stop.is_set():
                    from haval_engine.phase2.runner import run_quality_pack

                    self._emit(message=f"{model} — Phase 2 capability pack", detail="", log_line="phase2 start")

                    def p2_progress(message: str, prompt: str = "", answer: str = "", tick: bool = False) -> None:
                        nonlocal done
                        if tick:
                            done += 1
                        self._emit(
                            pct=round(100 * min(done, total_units) / total_units, 1),
                            completion_pct=round(100 * min(done, total_units) / total_units, 1),
                            elapsed_s=round(time.perf_counter() - t0),
                            message=message,
                            detail="",
                            prompt=prompt,
                            answer="",
                            task_title="",
                            log_line=message,
                        )

                    phase2 = run_quality_pack(
                        model,
                        think=think,
                        cancel=self._stop,
                        progress=p2_progress,
                    )
                try:
                    ollama.unload(model)
                    time.sleep(1.5)
                except Exception:
                    pass
                if by_scenario or h_samples:
                    roll = self._model_rollups(model, list(by_scenario.values()), h_samples)
                    roll["phase2"] = phase2
                    if not fail and not roll.get("finish"):
                        fail = summarize_failures(atts_m, thinking=think)
                    if fail:
                        roll["fail"] = fail
                        _log(f"fail {model} {fail['kind']}: {fail['headline']}")
                    model_summaries.append(roll)
            prior = {}
            try:
                prior = json.loads((self.store.get(run_id) or {}).get("summary_json") or "{}")
            except json.JSONDecodeError:
                prior = {}
            summary = {
                **prior,
                "models": model_summaries,
                "scenario_count": len(scenarios),
                "attempts": attempts_n,
                "thinking": think,
                "personas": personas or None,
                "report_dir": report_dir,
            }
            status = "stopped" if self._stop.is_set() else "completed"
            if status == "stopped":
                summary["partial"] = True
            self.store.set_status(run_id, status, summary)
            self.store.export_csv(run_id)
            wrote = None
            try:
                wrote = generate_report(run_id, self.store)
            except Exception as exc:  # noqa: BLE001
                _log(f"report {exc}")
            self._emit(
                state="idle",
                message="Benchmark complete" if status == "completed" else "Stopped. A report of what finished was saved.",
                pct=100 if status == "completed" else self.snapshot.get("pct"),
                detail=run_id,
                open_report=run_id if wrote is not None else None,
                log_line=f"finished {run_id} {status}",
            )
            _log(f"finished {run_id} {status}")
        except Exception as exc:  # noqa: BLE001
            _log(f"failed {exc}")
            self.store.set_status(run_id, "failed", {"error": str(exc), "thinking": think})
            self._emit(state="idle", message="Benchmark failed", detail=str(exc), log_line=str(exc), open_report=None)
        finally:
            self._run_t0 = None

    def _apply_role_speeds(
        self,
        model: str,
        recs: list[dict],
        attempts: list[dict],
        scenarios: list[dict],
    ) -> list[dict]:
        pack = {s["id"]: s for s in scenarios}
        by_persona: dict[str, list[dict]] = defaultdict(list)
        for rec in recs:
            by_persona[str(rec.get("persona") or "")].append(rec)
        out: list[dict] = []
        for group in by_persona.values():
            actuals: list[float | None] = []
            expecteds: list[float | None] = []
            heavy_actual = None
            for rec in group:
                sc = pack.get(rec.get("scenario_id") or "") or {}
                exp = float(sc.get("total_s") or 0) or None
                times = [
                    float(a["total_s"])
                    for a in attempts
                    if a.get("model") == model
                    and a.get("scenario_id") == rec.get("scenario_id")
                    and a.get("ok")
                    and a.get("total_s") is not None
                ]
                act = mean(times)
                rec["actual_s"] = act
                rec["expected_s"] = exp
                if act is not None and exp:
                    actuals.append(act)
                    expecteds.append(exp)
                if rec.get("intensity") == "Heavy":
                    heavy_actual = act
            band = role_speed_band(actuals, expecteds, heavy_actual)
            for rec in group:
                rec["role_speed"] = band
                if rec.get("successful"):
                    rec["w"] = phase1_score(
                        content=rec.get("q"),
                        speed=band,
                        answers=[rec.get("q")],
                        successful=int(rec.get("successful") or 0),
                        attempted=int(rec.get("attempted") or 1),
                        headrooms=[rec.get("e")],
                        tok_s=[],
                    )
                    rec["customer"] = match_label(
                        finish=rec.get("r"),
                        answer=rec.get("w"),
                        speed=band,
                    )
                self.store.upsert_scenario(rec)
                out.append(rec)
        return out

    def _model_rollups(self, model: str, rows: list[dict], h_samples: list[dict]) -> dict:
        by_persona: dict[str, dict[str, float | str | None]] = defaultdict(dict)
        personas_meta: dict[str, str] = {}
        for row in rows:
            by_persona[row["persona"]][row["intensity"]] = row.get("q")
            by_persona[row["persona"]][row["intensity"] + "_speed"] = row.get("role_speed") or row.get("internal")
            personas_meta[row["persona"]] = row["business"]
        persona_rows = []
        for persona, intensities in by_persona.items():
            p = persona_quality(
                intensities.get("Light"),
                intensities.get("Balanced"),
                intensities.get("Heavy"),
                intensities.get("Light_speed"),
                intensities.get("Balanced_speed"),
                intensities.get("Heavy_speed"),
            )
            persona_rows.append({"persona": persona, "business": personas_meta[persona], "overall": p, **intensities})
        businesses: dict[str, list[float]] = defaultdict(list)
        for prow in persona_rows:
            if prow.get("overall") is not None:
                businesses[prow["business"]].append(float(prow["overall"]))
        business_scores = {b: (sum(vs) / len(vs) if vs else None) for b, vs in businesses.items()}
        q_all = [quality(r.get("q"), r.get("internal")) for r in rows]
        offloads = [s["offload"] for s in h_samples if s.get("offload") is not None]
        heads = [s["headroom"] for s in h_samples if s.get("headroom") is not None]
        gpu = None
        if offloads:
            gpu = "Mostly on GPU" if (sum(offloads) / len(offloads)) >= 0.5 else "Heavy CPU offload"
        head = None
        if heads:
            head = "Headroom OK" if (sum(heads) / len(heads)) >= 0.1 else "Tight memory"
        note = " · ".join(x for x in (gpu, head) if x) or "Hardware note not measured"
        return {
            "model": model,
            "personas": persona_rows,
            "businesses": business_scores,
            "Q": mean(q_all),
            "finish": mean([r.get("r") for r in rows]),
            "hardware_note": note,
        }


RUNNER = BenchRunner()
