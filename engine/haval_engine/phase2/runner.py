"""Run the HavalLLMphase2 quality pack (no multilingual, no sensitivity) against one Ollama model."""

from __future__ import annotations

import os
from typing import Callable

from haval_engine.ollama import client as ollama
from haval_engine.phase2 import load_json
from haval_engine.phase2.coding import CODING_PROMPT, grade_coding_js, weighted_coding_pct
from haval_engine.phase2.parse import math_matches, reasoning_matches, strip_think
from haval_engine.phase2.validate import validate_instruction_following, validate_structured_output
from haval_engine.bench.display_text import phase2_question
from haval_engine.scoring.pipeline import havalllmphase2_quality_total
from haval_engine.scoring.rules import load_ruleset

REASONING_PROMPT = (
    "Answer the following multiple choice question. Reply with ONLY the letter (A, B, C, or D).\n\n"
    "Question: {question}\n{choices}\n\nAnswer:"
)
MATH_PROMPT = (
    "Solve the following math problem. Give ONLY the numerical answer, nothing else.\n\n"
    "Problem: {question}\n\nAnswer:"
)
_STALL_QUALITY_S = 30.0
_STALL_DEFAULT_S = 12.0
_QUALITY_CLOCK = {"math", "reasoning", "structuredOutput"}


def _limit(name: str) -> list:
    cap = os.environ.get("HAVAL_LLM_PHASE2_MAX")
    items = load_json(name)
    if cap:
        return items[: max(1, int(cap))]
    return items


def _generate(
    model: str,
    prompt: str,
    think: bool,
    cancel,
    wall_s: float,
    num_predict: int = 1024,
    stall_s: float | None = None,
) -> dict:
    stall = _STALL_DEFAULT_S if stall_s is None else stall_s
    return ollama.generate_stream(
        model,
        prompt,
        num_predict=num_predict,
        timeout=wall_s,
        stall_s=min(float(stall), wall_s),
        wall_s=wall_s,
        cancel=cancel,
        think=think,
    )


def _timed_ok(correct: bool, time_ms: float, limit_ms: float) -> bool:
    return bool(correct) and time_ms <= limit_ms


def pack_item_count() -> int:
    return sum(
        len(_limit(name))
        for name in (
            "reasoning.json",
            "math.json",
            "instruction-following.json",
            "structured-output.json",
            "coding.json",
        )
    )


def run_quality_pack(
    model: str,
    *,
    think: bool = False,
    cancel=None,
    progress: Callable[..., None] | None = None,
) -> dict:
    limits = load_ruleset().get("havalllmphase2_time_limits_ms") or {}
    categories: dict[str, dict] = {}

    def emit(msg: str, prompt: str = "", answer: str = "", tick: bool = False) -> None:
        if progress:
            progress(msg, prompt, answer, tick)

    def run_cat(key: str, items: list, ask, *, predict: int = 1024) -> None:
        limit_ms = float(limits.get(key) or 30000)
        details = []
        credited = 0
        for i, item in enumerate(items, start=1):
            if cancel is not None and cancel.is_set():
                break
            prompt, checker = ask(item)
            shown = phase2_question(key, item)
            label = {"reasoning": "Reasoning", "math": "Math", "instructionFollowing": "Instruction following", "structuredOutput": "Structured output", "coding": "Coding"}.get(key, key)
            emit(f"Phase 2 · {label} {i}/{len(items)}", shown, "", False)
            quality_clock = key in _QUALITY_CLOCK
            wall_s = max(1.0, limit_ms / 1000.0) if quality_clock else max(15.0, limit_ms / 1000.0 + 8.0)
            if key == "structuredOutput":
                stall_s = wall_s
            elif quality_clock:
                stall_s = _STALL_QUALITY_S
            else:
                stall_s = _STALL_DEFAULT_S
            gen = _generate(
                model,
                prompt,
                think,
                cancel,
                wall_s=wall_s,
                num_predict=predict,
                stall_s=stall_s,
            )
            text = strip_think(gen.get("text") or "")
            cap_fail = {"wall_timeout", "cancelled"}
            if key != "structuredOutput":
                cap_fail.update({"repeat_loop", "output_cap"})
            if gen.get("error") in cap_fail or ("timeout" in str(gen.get("error") or "").lower()):
                emit(
                    f"Phase 2 · {label} {i}/{len(items)}",
                    shown,
                    "Time cap — failed, next item.",
                    True,
                )
                details.append(
                    {
                        "id": item.get("id"),
                        "correct": False,
                        "raw_correct": False,
                        "time_ms": float(gen.get("total_ms") or limit_ms),
                        "slow": True,
                    }
                )
                continue
            emit(f"Phase 2 · {label} {i}/{len(items)}", shown, "", True)
            time_ms = float(gen.get("total_ms") or 0)
            if key in {"math", "reasoning", "coding", "structuredOutput"}:
                ok_raw = checker(text, item)
            else:
                ok_raw = bool(gen.get("ok")) and checker(text, item)
            if quality_clock:
                ok = bool(ok_raw)
            else:
                ok = _timed_ok(ok_raw, time_ms, limit_ms)
            if ok:
                credited += 1
            details.append(
                {
                    "id": item.get("id"),
                    "correct": ok,
                    "raw_correct": ok_raw,
                    "time_ms": time_ms,
                    "slow": ok_raw and time_ms > limit_ms,
                }
            )
        total = len(items)
        pct = (100.0 * credited / total) if total else 0.0
        if key == "coding":
            pct = weighted_coding_pct(items, details)
        categories[key] = {"correct": credited, "total": total, "pct": pct, "details": details}

    run_cat(
        "reasoning",
        _limit("reasoning.json"),
        lambda q: (
            REASONING_PROMPT.format(question=q["question"], choices="\n".join(q.get("choices") or [])),
            lambda text, item: reasoning_matches(text, str(item.get("answer") or "")),
        ),
    )
    run_cat(
        "math",
        _limit("math.json"),
        lambda q: (
            MATH_PROMPT.format(question=q["question"]),
            lambda text, item: math_matches(
                text, float(item["answer"]), float(item.get("tolerance") or 0)
            ),
        ),
    )
    run_cat(
        "instructionFollowing",
        _limit("instruction-following.json"),
        lambda q: (q["prompt"], lambda text, item: validate_instruction_following(text, item)),
    )
    run_cat(
        "structuredOutput",
        _limit("structured-output.json"),
        lambda q: (q["prompt"], lambda text, item: validate_structured_output(text, item)),
    )
    run_cat(
        "coding",
        _limit("coding.json"),
        lambda q: (
            CODING_PROMPT.format(signature=q["signature"], description=q["description"]),
            lambda text, item: grade_coding_js(text, item),
        ),
        predict=2048,
    )

    pcts = {k: v["pct"] for k, v in categories.items()}
    total = havalllmphase2_quality_total(pcts)
    excluded = ["multilingual", "sensitivity"]
    return {
        "pack": "phase2-quality",
        "excluded": excluded,
        "categories": categories,
        "pct": pcts,
        "total": total,
        "source": "Phase 2 capability pack; multilingual and sensitivity omitted",
    }
