from __future__ import annotations

from haval_engine.pack.weights import forty_sixty

# First-token Fast max from Doc/roles/role-playbooks (seconds).
# Fallback intensity defaults if a persona row is missing a key.
TTFT = {"Light": 6, "Balanced": 8, "Heavy": 12}

PERSONA_TTFT = {
    "Everyday Organizer": {"Light": 6, "Balanced": 8, "Heavy": 12},
    "Student & Learner": {"Light": 6, "Balanced": 8, "Heavy": 12},
    "Family Coordinator": {"Light": 6, "Balanced": 8, "Heavy": 12},
    "Researcher & Shopper": {"Light": 6, "Balanced": 8, "Heavy": 12},
    "Writer & Communicator": {"Light": 6, "Balanced": 8, "Heavy": 12},
    "Creative Prosumer": {"Light": 6, "Balanced": 8, "Heavy": 12},
    "Personal Adviser": {"Light": 7, "Balanced": 10, "Heavy": 15},
    "Technical Hobbyist": {"Light": 8, "Balanced": 12, "Heavy": 18},
    "Casual Gamer": {"Light": 5, "Balanced": 8, "Heavy": 10},
    "Power Player": {"Light": 6, "Balanced": 8, "Heavy": 12},
    "Progressive Creator": {"Light": 6, "Balanced": 8, "Heavy": 18},
    "Rising Game Developer": {"Light": 10, "Balanced": 12, "Heavy": 18},
    "Executive & Decision Maker": {"Light": 8, "Balanced": 10, "Heavy": 15},
    "Project & Operations Manager": {"Light": 7, "Balanced": 10, "Heavy": 15},
    "Engineer & Software Developer": {"Light": 12, "Balanced": 15, "Heavy": 20},
    "Analyst & Finance Professional": {"Light": 7, "Balanced": 10, "Heavy": 15},
    "Research & Product Professional": {"Light": 8, "Balanced": 10, "Heavy": 15},
    "Sales & Marketing Professional": {"Light": 6, "Balanced": 8, "Heavy": 12},
    "Customer Support Specialist": {"Light": 6, "Balanced": 8, "Heavy": 12},
    "People, Legal & Compliance Professional": {"Light": 8, "Balanced": 12, "Heavy": 18},
}

# Full-answer Fast max from each role playbook (seconds). 2 min=120, 2.5 min=150, 3 min=180, 3.5 min=210.
PERSONA_TOTAL_S = {
    "Everyday Organizer": {"Light": 25, "Balanced": 45, "Heavy": 90},
    "Student & Learner": {"Light": 25, "Balanced": 50, "Heavy": 120},
    "Family Coordinator": {"Light": 25, "Balanced": 50, "Heavy": 120},
    "Researcher & Shopper": {"Light": 25, "Balanced": 50, "Heavy": 120},
    "Writer & Communicator": {"Light": 25, "Balanced": 45, "Heavy": 90},
    "Creative Prosumer": {"Light": 25, "Balanced": 50, "Heavy": 120},
    "Personal Adviser": {"Light": 30, "Balanced": 60, "Heavy": 120},
    "Technical Hobbyist": {"Light": 40, "Balanced": 90, "Heavy": 150},
    "Casual Gamer": {"Light": 20, "Balanced": 40, "Heavy": 75},
    "Power Player": {"Light": 25, "Balanced": 50, "Heavy": 120},
    "Progressive Creator": {"Light": 25, "Balanced": 50, "Heavy": 120},
    "Rising Game Developer": {"Light": 50, "Balanced": 100, "Heavy": 180},
    "Executive & Decision Maker": {"Light": 30, "Balanced": 70, "Heavy": 150},
    "Project & Operations Manager": {"Light": 30, "Balanced": 70, "Heavy": 150},
    "Engineer & Software Developer": {"Light": 60, "Balanced": 120, "Heavy": 210},
    "Analyst & Finance Professional": {"Light": 30, "Balanced": 70, "Heavy": 150},
    "Research & Product Professional": {"Light": 30, "Balanced": 70, "Heavy": 150},
    "Sales & Marketing Professional": {"Light": 25, "Balanced": 50, "Heavy": 120},
    "Customer Support Specialist": {"Light": 25, "Balanced": 50, "Heavy": 120},
    "People, Legal & Compliance Professional": {"Light": 35, "Balanced": 75, "Heavy": 150},
}

# Explicit override for GAM-RGD-H-001 / G-RD-H (report-requirements example).
G_RD_H_WEIGHTS = {"P": 0.40, "R": 0.25, "I": 0.20, "S": 0.15}


def _ts(persona: str, intensity: str) -> float:
    return PERSONA_TOTAL_S[persona][intensity]


def _row(
    sid: str,
    business: str,
    persona: str,
    intensity: str,
    name: str,
    total_s: float,
    primary: str,
    dims: str,
    fixture: str | None,
    prompt: str,
    must: list[str],
    good: str,
    bad: str,
    *,
    grader: str = "rules",
    json_required: bool = False,
    numbers: dict | None = None,
    code_kind: str | None = None,
    hard: list[str] | None = None,
    weights: dict | None = None,
    alias: str | None = None,
    forbidden: list[str] | None = None,
    code_tests: str | None = None,
    sandbox_prelude: str | None = None,
) -> dict:
    applicable = [d.strip() for d in dims.split(",") if d.strip()]
    w = weights or forty_sixty(primary, applicable)
    return {
        "id": sid,
        "alias": alias,
        "version": "1.0.0",
        "business": business,
        "persona": persona,
        "intensity": intensity,
        "name": name,
        "ttft_s": PERSONA_TTFT[persona][intensity],
        "total_s": total_s,
        "attempts": 1,
        "fixture": fixture,
        "prompt": prompt,
        "primary": primary,
        "dimensions": applicable,
        "weights": w,
        "grader": grader,
        "json_required": json_required,
        "numbers": numbers or {},
        "code_kind": code_kind,
        "code_tests": code_tests or "",
        "sandbox_prelude": sandbox_prelude or "",
        "hard_gates": hard or (["json_valid"] if json_required else []),
        "must_contain": must,
        "must_not_contain": forbidden or [],
        "seeds": {"good": good, "bad": bad},
        "research_basis": "Persona-AI-Workload-Response-Time-Source-Table.md",
    }


def scenarios() -> list[dict]:
    from haval_engine.pack.scenario_rows import build_rows

    rows = build_rows(_row, _ts)
    assert len(rows) == 60, len(rows)
    for row in rows:
        times = PERSONA_TOTAL_S[row["persona"]]
        row["total_s"] = times[row["intensity"]]
        row["ttft_s"] = PERSONA_TTFT[row["persona"]][row["intensity"]]
        row["research_basis"] = "role-playbooks"
    return rows
