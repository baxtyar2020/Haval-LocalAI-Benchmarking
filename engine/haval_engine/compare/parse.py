from __future__ import annotations

import html as html_lib
import json
import re
from html.parser import HTMLParser
from pathlib import Path

from haval_engine.compare.models import CAP_ORDER, MeasuredRun, PersonaRow


def parse_mmss(text: str | None) -> float | None:
    raw = (text or "").strip().replace("—", "").replace("–", "")
    if not raw or raw == "-":
        return None
    if re.fullmatch(r"\d+:\d{2}", raw):
        m, s = raw.split(":")
        return int(m) * 60 + int(s)
    return None


def parse_number(text: str | None) -> float | None:
    raw = (text or "").strip().replace("—", "").replace(",", "")
    if not raw:
        return None
    m = re.search(r"-?\d+(?:\.\d+)?", raw)
    if not m:
        return None
    try:
        return float(m.group(0))
    except ValueError:
        return None


def parse_int(text: str | None) -> int | None:
    n = parse_number(text)
    return int(round(n)) if n is not None else None


def parse_params_b(text: str | None) -> float | None:
    raw = (text or "").upper().replace("B", " ").strip()
    n = parse_number(raw)
    return n


def format_mmss(seconds: float | None) -> str:
    if seconds is None:
        return "—"
    total = max(0, int(round(seconds)))
    return f"{total // 60}:{total % 60:02d}"


def estimate_task_seconds(row: PersonaRow) -> float | None:
    if row.light_s is None or row.balanced_s is None or row.heavy_s is None:
        return None
    return (row.light_s + row.balanced_s + row.heavy_s) * 10


def avg_task_seconds(personas: list[PersonaRow]) -> float | None:
    times = [estimate_task_seconds(p) for p in personas]
    ok = [t for t in times if t is not None]
    if not ok:
        return None
    return sum(ok) / len(ok)


def model_key(name: str, total_b: float | None, active_b: float | None) -> str:
    family = re.sub(r":[\w.\-]+$", "", name or "")
    family = family.lower()
    family = re.sub(r"[^a-z0-9]+", "-", family).strip("-")
    family = re.sub(r"-(latest|instruct|it)$", "", family)
    tot = _b_token(total_b)
    act = _b_token(active_b) or tot
    if tot and act:
        return f"{family}-{tot}-{act}"
    return family or "model"


def _b_token(n: float | None) -> str:
    if n is None:
        return ""
    if abs(n - round(n)) < 0.05:
        return f"{int(round(n))}b"
    return f"{n:g}b".lower()


def _cell_text(raw: str) -> str:
    return html_lib.unescape(re.sub(r"\s+", " ", raw)).strip()


class _ReportParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.title = ""
        self._in_title = False
        self._capture = False
        self._buf: list[str] = []
        self.tables: list[list[list[str]]] = []
        self._table: list[list[str]] | None = None
        self._row: list[str] | None = None
        self.tile_names: list[str] = []
        self.tile_accents: list[str] = []
        self._cls = ""
        self.footer = ""
        self.body_text_parts: list[str] = []
        self._in_body = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        ad = {k: v or "" for k, v in attrs}
        self._cls = ad.get("class", "")
        if tag == "title":
            self._in_title = True
            self._buf = []
        if tag == "body":
            self._in_body = True
        if tag == "table":
            self._table = []
        if tag == "tr" and self._table is not None:
            self._row = []
        if tag in {"td", "th"} and self._row is not None:
            self._capture = True
            self._buf = []
        if tag in {"b", "span", "div"} and "tile-name" in self._cls.split():
            self._capture = True
            self._buf = []
            self._cls = "tile-name"
        if tag in {"span", "div"} and "tile-accent" in self._cls.split():
            self._capture = True
            self._buf = []
            self._cls = "tile-accent"

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._in_title = False
            self.title = _cell_text("".join(self._buf))
        if tag in {"td", "th"} and self._row is not None and self._capture:
            self._row.append(_cell_text("".join(self._buf)))
            self._capture = False
        if tag == "tr" and self._table is not None and self._row is not None:
            if any(self._row):
                self._table.append(self._row)
            self._row = None
        if tag == "table" and self._table is not None:
            if self._table:
                self.tables.append(self._table)
            self._table = None
        if tag in {"b", "span", "div"} and self._capture and self._cls == "tile-name":
            self.tile_names.append(_cell_text("".join(self._buf)))
            self._capture = False
        if tag in {"span", "div"} and self._capture and self._cls == "tile-accent":
            self.tile_accents.append(_cell_text("".join(self._buf)))
            self._capture = False
        if tag == "footer":
            self.footer = _cell_text("".join(self.body_text_parts[-8:]))

    def handle_data(self, data: str) -> None:
        if self._in_title or self._capture:
            self._buf.append(data)
        if self._in_body:
            self.body_text_parts.append(data)


def validate_source_html(html: str) -> str | None:
    low = html.lower()
    if "haval localai bench" not in low and "haval localai benchmarking" not in low:
        return "Not a Haval bench report"
    if "cross-model comparison" in low:
        return "Not a Haval bench report"
    return None


def parse_report_html(html: str, source_label: str = "") -> MeasuredRun:
    err = validate_source_html(html)
    if err:
        raise ValueError(err)
    p = _ReportParser()
    p.feed(html)
    p.close()
    blob = " ".join(p.body_text_parts)
    run = MeasuredRun(run_id="", source_label=source_label or "upload", model_name="")
    m = re.search(r"Run\s+([A-Za-z0-9._-]+)", blob + " " + p.footer + " " + p.title)
    if m:
        run.run_id = m.group(1)
    if p.tile_names:
        run.machine = p.tile_names[0]
    if p.tile_accents:
        run.os_label = p.tile_accents[0]
    if len(p.tile_names) > 1:
        run.gpu = p.tile_names[1]
    if len(p.tile_accents) > 1 and "GB" in p.tile_accents[1]:
        run.vram = p.tile_accents[1]
    if len(p.tile_names) > 2:
        run.cpu = p.tile_names[2]
    for acc in p.tile_accents:
        if re.search(r"\d+\s*GB", acc) and "VRAM" not in acc.upper():
            run.ram = acc
    if "thinking was enabled" in blob.lower():
        run.thinking = True
    elif "thinking was disabled" in blob.lower():
        run.thinking = False

    evidence = _find_table(p.tables, ("Tok/s", "TTFT", "Final"))
    if evidence and len(evidence) > 1:
        headers = [h.lower() for h in evidence[0]]
        row = evidence[1]
        def col(*names: str) -> str:
            for n in names:
                for i, h in enumerate(headers):
                    if n in h:
                        return row[i] if i < len(row) else ""
            return ""

        run.model_name = col("model") or run.model_name
        run.arch = col("architecture", "arch")
        params = col("total", "active")
        tot_m = re.search(r"([\d.]+)\s*B?\s*total", params, re.I)
        act_m = re.search(r"([\d.]+)\s*B?\s*active", params, re.I)
        if tot_m:
            run.total_b = float(tot_m.group(1))
        if act_m:
            run.active_b = float(act_m.group(1))
        run.quant = col("quant")
        run.tok_s = parse_number(col("tok"))
        run.ttft_s = parse_number(col("ttft"))
        run.mean_s = parse_mmss(col("mean", "completion")) or parse_number(col("mean", "completion"))
        run.phase1 = parse_int(col("phase 1"))
        run.phase2 = parse_int(col("phase 2"))
        run.final = parse_int(col("final"))
        run.finish = parse_int(col("finish"))

    personas = _find_table(p.tables, ("Persona", "Light", "Balanced", "Heavy"))
    if personas and len(personas) > 1:
        headers = [h.lower() for h in personas[0]]
        for row in personas[1:]:
            def at(key: str) -> str:
                for i, h in enumerate(headers):
                    if key in h:
                        return row[i] if i < len(row) else ""
                return ""

            name = at("persona")
            if not name:
                continue
            run.personas.append(
                PersonaRow(
                    business=at("business"),
                    name=name,
                    light_s=parse_mmss(at("light")),
                    balanced_s=parse_mmss(at("balanced")),
                    heavy_s=parse_mmss(at("heavy")),
                    phase1=parse_int(at("phase 1")),
                    phase2=parse_int(at("phase 2")),
                    final=parse_int(at("final")),
                    match=at("match") or None,
                )
            )

    caps = _find_table(p.tables, ("Category", "Score"))
    if caps and len(caps) > 1:
        headers = [h.lower() for h in caps[0]]
        name_i = next((i for i, h in enumerate(headers) if "categor" in h), 1)
        score_i = next((i for i, h in enumerate(headers) if "score" in h or h == "pct"), len(headers) - 1)
        for row in caps[1:]:
            if max(name_i, score_i) >= len(row):
                continue
            label = row[name_i].strip()
            if label in CAP_ORDER:
                run.capabilities[label] = parse_int(row[score_i])

    if not run.model_name:
        t = p.title
        t = re.sub(r"Haval LocalAI Bench[^-–]*[-–]\s*", "", t, flags=re.I).strip()
        run.model_name = t
    if not run.model_name:
        raise ValueError("Not a Haval bench report")
    if run.final is None and not run.personas:
        raise ValueError("Not a Haval bench report")
    run.model_key = model_key(run.model_name, run.total_b, run.active_b)
    if not run.run_id:
        run.run_id = re.sub(r"[^A-Za-z0-9._-]+", "-", source_label)[:40] or "upload"
    return run


def _find_table(tables: list[list[list[str]]], must: tuple[str, ...]) -> list[list[str]] | None:
    need = [m.lower() for m in must]
    for table in tables:
        if not table:
            continue
        head = " ".join(table[0]).lower()
        if all(n in head for n in need):
            return table
    return None


def parse_measured_json(text: str, source_label: str = "") -> MeasuredRun | None:
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return None
    if data.get("kind") != "measured-run":
        return None
    model = data.get("model") or {}
    ev = data.get("evidence") or {}
    hw = data.get("hardware") or {}
    caps = {row.get("name"): parse_int(str(row.get("score"))) for row in (data.get("capabilities") or []) if row.get("name")}
    personas = []
    for p in data.get("personas") or []:
        personas.append(
            PersonaRow(
                business=str(p.get("business") or ""),
                name=str(p.get("name") or ""),
                light_s=parse_mmss(str(p.get("light") or "")) or parse_number(p.get("light_s")),
                balanced_s=parse_mmss(str(p.get("balanced") or "")) or parse_number(p.get("balanced_s")),
                heavy_s=parse_mmss(str(p.get("heavy") or "")) or parse_number(p.get("heavy_s")),
                phase1=parse_int(str(p.get("phase1") or "")),
                phase2=parse_int(str(p.get("phase2") or "")),
                final=parse_int(str(p.get("final") or "")),
                match=p.get("match"),
            )
        )
    name = str(model.get("name") or "")
    total = parse_params_b(str(model.get("total") or ""))
    active = parse_params_b(str(model.get("active") or ""))
    return MeasuredRun(
        run_id=str(data.get("run_id") or ""),
        source_label=source_label,
        machine=str(hw.get("machine") or ""),
        os_label=str(hw.get("os") or ""),
        gpu=str(hw.get("gpu") or ""),
        vram=str(hw.get("vram") or ""),
        cpu=str(hw.get("cpu") or ""),
        ram=str(hw.get("ram") or ""),
        thinking=data.get("thinking"),
        model_name=name,
        model_key=model_key(name, total, active),
        arch=str(model.get("arch") or ""),
        total_b=total,
        active_b=active,
        quant=str(model.get("quant") or ""),
        tok_s=parse_number(str(ev.get("tok_s") or "")),
        ttft_s=parse_number(str(ev.get("ttft_s") or "")),
        mean_s=parse_mmss(str(ev.get("mean") or "")) or parse_number(str(ev.get("mean_s") or "")),
        phase1=parse_int(str(ev.get("phase1") or "")),
        phase2=parse_int(str(ev.get("phase2") or "")),
        final=parse_int(str(ev.get("final") or "")),
        finish=parse_int(str(ev.get("finish") or "")),
        capabilities=caps,
        personas=personas,
    )


def load_run_file(path: Path) -> MeasuredRun:
    html_path = path if path.suffix.lower() in {".html", ".htm"} else path / "report.html"
    json_path = html_path.with_name("measured.json")
    if json_path.is_file():
        parsed = parse_measured_json(json_path.read_text(encoding="utf-8"), str(path))
        if parsed and parsed.model_name:
            return parsed
    return parse_report_html(html_path.read_text(encoding="utf-8", errors="replace"), html_path.name)
