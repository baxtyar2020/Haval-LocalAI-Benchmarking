from fastapi import APIRouter

from haval_engine.pack import load_scenarios
from haval_engine.pack.paths import fixtures_dir

router = APIRouter(prefix="/pack", tags=["pack"])


@router.get("/scenarios")
def list_scenarios() -> dict:
    items = load_scenarios()
    return {"version": "1.0.0", "count": len(items), "attempts_per_scenario": 1, "scenarios": items}


@router.get("/fixtures")
def list_fixtures() -> dict:
    names = sorted(p.stem for p in fixtures_dir().glob("*.json") if p.name != "manifest.json")
    return {"count": len(names), "fixtures": names}
