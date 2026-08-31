"""Short Phase 1 blurbs for the Benchmark window. Generate prompts stay in scenario.prompt."""

from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from functools import lru_cache
from pathlib import Path
from zipfile import ZipFile

from haval_engine.paths import config_dir, repo_root

_NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}


def blurbs_xlsx_path() -> Path:
    """Prefer the ask-matrix workbook; also accept capability-requirements if it has Light/Balanced/Heavy copy."""
    for path in blurbs_xlsx_candidates():
        if path.is_file():
            return path
    return repo_root() / "Doc" / "roles" / "Role_Ask_Matrix-discription.xlsx"


def blurbs_xlsx_candidates() -> list[Path]:
    root = repo_root() / "Doc" / "roles"
    return [
        root / "Role_Ask_Matrix-discription.xlsx",
        root / "role-ai-capability-requirements.xlsx",
    ]


def blurbs_json_path() -> Path:
    return config_dir() / "role_ask_blurbs.json"


def _col_row(cell_ref: str) -> tuple[int, int]:
    letters = "".join(c for c in cell_ref if c.isalpha())
    digits = "".join(c for c in cell_ref if c.isdigit())
    col = 0
    for ch in letters.upper():
        col = col * 26 + (ord(ch) - 64)
    return col, int(digits or 0)


def _cell_text(cell: ET.Element, strings: list[str]) -> str:
    kind = cell.attrib.get("t")
    if kind == "inlineStr":
        return "".join((t.text or "") for t in cell.findall(".//m:t", _NS)).strip()
    value = cell.find("m:v", _NS)
    if value is None or value.text is None:
        return ""
    if kind == "s":
        idx = int(value.text)
        return (strings[idx] if 0 <= idx < len(strings) else "").strip()
    return (value.text or "").strip()


def _zip_sheet_path(target: str) -> str:
    t = (target or "worksheets/sheet1.xml").replace("\\", "/")
    if t.startswith("/"):
        return t.lstrip("/")
    if t.startswith("xl/"):
        return t
    return "xl/" + t.lstrip("./")


def _shared_strings(zf: ZipFile) -> list[str]:
    try:
        root = ET.fromstring(zf.read("xl/sharedStrings.xml"))
    except KeyError:
        return []
    out: list[str] = []
    for si in root.findall("m:si", _NS):
        parts = [t.text or "" for t in si.findall(".//m:t", _NS)]
        out.append("".join(parts))
    return out


_REL_NS = {"r": "http://schemas.openxmlformats.org/package/2006/relationships"}
_INTENSITY_HEADERS = {
    "light": "Light",
    "light ask": "Light",
    "balanced": "Balanced",
    "balanced ask": "Balanced",
    "balance": "Balanced",
    "balance ask": "Balanced",
    "heavy": "Heavy",
    "heavy ask": "Heavy",
}


def _sheet_targets(zf: ZipFile) -> list[tuple[str, str]]:
    wb = ET.fromstring(zf.read("xl/workbook.xml"))
    rels = ET.fromstring(zf.read("xl/_rels/workbook.xml.rels"))
    rid_to_target: dict[str, str] = {}
    for rel in rels.findall("r:Relationship", _REL_NS):
        rid_to_target[rel.attrib.get("Id") or ""] = rel.attrib.get("Target") or ""
    out: list[tuple[str, str]] = []
    for sheet in wb.findall("m:sheets/m:sheet", _NS):
        name = sheet.attrib.get("name") or ""
        rid = sheet.attrib.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id") or ""
        target = rid_to_target.get(rid) or ""
        if target:
            out.append((name, target))
    return out


def _grid(root: ET.Element, strings: list[str]) -> dict[int, dict[int, str]]:
    rows: dict[int, dict[int, str]] = {}
    for cell in root.findall(".//m:c", _NS):
        ref = cell.attrib.get("r") or ""
        col, row = _col_row(ref)
        if not row:
            continue
        text = _cell_text(cell, strings)
        if not text:
            continue
        rows.setdefault(row, {})[col] = text
    return rows


def _header_map(cells: dict[int, str]) -> dict[str, int] | None:
    found: dict[str, int] = {}
    role_col: int | None = None
    for col, raw in cells.items():
        key = " ".join((raw or "").lower().replace("·", " ").split())
        if key in {"role", "role name", "persona"}:
            role_col = col
        intensity = _INTENSITY_HEADERS.get(key)
        if intensity:
            found[intensity] = col
    if role_col is None or not {"Light", "Balanced", "Heavy"} <= found.keys():
        return None
    found["Role"] = role_col
    return found


def _parse_workbook(src: Path) -> dict[str, dict[str, str]]:
    if not src.is_file():
        return {}
    with ZipFile(src) as zf:
        strings = _shared_strings(zf)
        sheets = _sheet_targets(zf)
        best: dict[str, dict[str, str]] = {}
        for _name, target in sheets:
            root = ET.fromstring(zf.read(_zip_sheet_path(target)))
            rows = _grid(root, strings)
            header: dict[str, int] | None = None
            by_role: dict[str, dict[str, str]] = {}
            for r in sorted(rows):
                cells = rows[r]
                if header is None:
                    header = _header_map(cells)
                    continue
                role = cells.get(header["Role"]) or ""
                if not role or role.lower() in {"role", "role name"}:
                    continue
                light = cells.get(header["Light"], "")
                bal = cells.get(header["Balanced"], "")
                heavy = cells.get(header["Heavy"], "")
                if not (light and bal and heavy):
                    continue
                by_role[role] = {"Light": light, "Balanced": bal, "Heavy": heavy}
            if len(by_role) > len(best):
                best = by_role
    return best


def parse_role_blurbs(path: Path | None = None) -> dict[str, dict[str, str]]:
    if path is not None:
        return _parse_workbook(path)
    best: dict[str, dict[str, str]] = {}
    for cand in blurbs_xlsx_candidates():
        books = _parse_workbook(cand)
        if len(books) > len(best):
            best = books
        if len(best) >= 20:
            return best
    return best


def blurbs_source_name() -> str:
    for cand in blurbs_xlsx_candidates():
        if len(_parse_workbook(cand)) >= 20:
            return cand.name
    return blurbs_xlsx_path().name


def blurbs_by_scenario_id() -> dict[str, str]:
    from haval_engine.pack.matrix import scenarios as build_scenarios

    books = parse_role_blurbs()
    out: dict[str, str] = {}
    for row in build_scenarios():
        text = (books.get(row["persona"]) or {}).get(row["intensity"]) or ""
        if text:
            out[row["id"]] = text
    return out


def write_blurbs_json() -> Path:
    payload = {"version": "1.0.0", "source": blurbs_source_name(), "phase1": blurbs_by_scenario_id()}
    path = blurbs_json_path()
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    load_phase1_blurbs.cache_clear()
    return path


@lru_cache(maxsize=1)
def load_phase1_blurbs() -> dict[str, str]:
    live = blurbs_by_scenario_id()
    if live:
        return live
    path = blurbs_json_path()
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
        return dict(data.get("phase1") or {})
    return {}
