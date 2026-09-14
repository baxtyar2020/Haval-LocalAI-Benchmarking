from __future__ import annotations

from haval_engine.compare.models import CAP_ORDER, MeasuredRun, PersonaRow


def merge_runs(runs: list[MeasuredRun]) -> list[MeasuredRun]:
    """Same model + same machine → one column. Newest evidence; persona union."""
    groups: dict[tuple[str, str], list[MeasuredRun]] = {}
    order: list[tuple[str, str]] = []
    for run in runs:
        key = (run.model_key or run.model_name.lower(), (run.machine or "").strip().upper())
        if key not in groups:
            groups[key] = []
            order.append(key)
        groups[key].append(run)
    columns: list[MeasuredRun] = []
    for key in order:
        columns.append(_merge_group(groups[key]))
    return columns


def _newer(a: MeasuredRun, b: MeasuredRun) -> MeasuredRun:
    return a if a.run_id >= b.run_id else b


def _merge_group(runs: list[MeasuredRun]) -> MeasuredRun:
    full = [r for r in runs if r.persona_count >= 20]
    if not full:
        most = max(r.persona_count for r in runs)
        full = [r for r in runs if r.persona_count == most]
    evidence = full[0]
    for r in full[1:]:
        evidence = _newer(evidence, r)
    newest_any = runs[0]
    for r in runs[1:]:
        newest_any = _newer(newest_any, r)
    personas: dict[str, tuple[str, PersonaRow]] = {}
    for r in sorted(runs, key=lambda x: x.run_id):
        for p in r.personas:
            personas[p.name] = (r.run_id, p)
    merged = MeasuredRun(
        run_id=evidence.run_id,
        source_label=evidence.source_label,
        machine=evidence.machine or newest_any.machine,
        os_label=evidence.os_label or newest_any.os_label,
        gpu=evidence.gpu or newest_any.gpu,
        vram=evidence.vram or newest_any.vram,
        cpu=evidence.cpu or newest_any.cpu,
        ram=evidence.ram or newest_any.ram,
        thinking=evidence.thinking if evidence.thinking is not None else newest_any.thinking,
        model_name=evidence.model_name,
        model_key=evidence.model_key,
        arch=evidence.arch,
        total_b=evidence.total_b,
        active_b=evidence.active_b,
        quant=evidence.quant,
        tok_s=evidence.tok_s,
        ttft_s=evidence.ttft_s,
        mean_s=evidence.mean_s,
        phase1=evidence.phase1,
        phase2=evidence.phase2,
        final=evidence.final,
        finish=evidence.finish,
        capabilities=dict(evidence.capabilities),
        personas=[p for _, p in personas.values()],
    )
    if not merged.capabilities:
        merged.capabilities = dict(newest_any.capabilities)
    for cap in CAP_ORDER:
        merged.capabilities.setdefault(cap, None)
    return merged
