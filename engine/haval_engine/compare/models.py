from __future__ import annotations

from dataclasses import dataclass, field


CAP_ORDER = (
    "Reasoning",
    "Coding",
    "Instruction following",
    "Structured output",
    "Math",
)

MODEL_COLORS = ("#7a5c2e", "#247f79", "#3f6797", "#ae3812", "#745486")


@dataclass
class PersonaRow:
    business: str
    name: str
    light_s: float | None = None
    balanced_s: float | None = None
    heavy_s: float | None = None
    phase1: int | None = None
    phase2: int | None = None
    final: int | None = None
    match: str | None = None


@dataclass
class MeasuredRun:
    run_id: str
    source_label: str
    machine: str = ""
    os_label: str = ""
    gpu: str = ""
    vram: str = ""
    cpu: str = ""
    ram: str = ""
    thinking: bool | None = None
    model_name: str = ""
    model_key: str = ""
    arch: str = ""
    total_b: float | None = None
    active_b: float | None = None
    quant: str = ""
    tok_s: float | None = None
    ttft_s: float | None = None
    mean_s: float | None = None
    phase1: int | None = None
    phase2: int | None = None
    final: int | None = None
    finish: int | None = None
    capabilities: dict[str, int | None] = field(default_factory=dict)
    personas: list[PersonaRow] = field(default_factory=list)

    @property
    def persona_count(self) -> int:
        return len(self.personas)
