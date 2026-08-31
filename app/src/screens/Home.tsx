import { Icon } from "../components/Icon";
import type { RepairState } from "../types";

type Spec = { icon: string; label: string; value: string };

type Props = {
  overall: RepairState;
  subtitle: string;
  specs: Spec[];
  installedCount: number;
  selectedCount: number;
  canStart: boolean;
  startHint: string;
  onStart: () => void;
  onDoctor: () => void;
  onModels: () => void;
};

export function HomeScreen({
  overall,
  subtitle,
  specs,
  installedCount,
  selectedCount,
  canStart,
  startHint,
  onStart,
  onDoctor,
  onModels,
}: Props) {
  const ready = overall === "ready";
  const checking = overall === "checking" || overall === "repairing";
  return (
    <div className="page">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-end", gap: 24, marginBottom: 30 }}>
        <div style={{ maxWidth: 640 }}>
          <div className="kicker" style={{ marginBottom: 12 }}>
            Welcome back
          </div>
          <h1 className="display" style={{ margin: "0 0 12px" }}>
            Know what your PC can really run.
          </h1>
          <p className="body" style={{ margin: 0, maxWidth: 560 }}>
            A guided, evidence-based way to find which local AI models fit this hardware — for whom, for which work, and why.
          </p>
        </div>
        <div style={{ display: "flex", flexDirection: "column", alignItems: "flex-end", gap: 12 }}>
          <button className="btn primary" onClick={onStart} disabled={!canStart} title={canStart ? "Start Benchmark" : startHint}>
            <Icon name="play" size={18} />
            Start Benchmark
          </button>
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1.4fr 1fr", gap: 22, marginBottom: 22 }}>
        <div className="card">
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 18 }}>
            <div>
              <div className="kicker-muted" style={{ marginBottom: 8 }}>
                System readiness
              </div>
              <div style={{ display: "flex", alignItems: "center", gap: 9 }}>
                <span
                  style={{
                    width: 9,
                    height: 9,
                    borderRadius: 999,
                    background: ready ? "var(--ok)" : checking ? "var(--accent)" : "var(--warn)",
                  }}
                />
                <span className="page-title" style={{ fontSize: 22, lineHeight: "28px" }}>
                  {ready ? "Ready" : checking ? "Checking…" : "Needs attention"}
                </span>
              </div>
              <p className="body" style={{ fontSize: 13, margin: "8px 0 0", maxWidth: 420 }}>
                {subtitle}
              </p>
            </div>
            <button className="btn tertiary" onClick={onDoctor}>
              Open Doctor <Icon name="arrow-right" size={14} />
            </button>
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "14px 26px" }}>
            {specs.map((s) => (
              <div key={s.label} style={{ display: "flex", alignItems: "center", gap: 11 }}>
                <div
                  style={{
                    width: 34,
                    height: 34,
                    borderRadius: 9,
                    background: "var(--canvas)",
                    border: "1px solid var(--border)",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    color: "var(--ink-soft)",
                    flex: "none",
                  }}
                >
                  <Icon name={s.icon} size={17} />
                </div>
                <div style={{ minWidth: 0 }}>
                  <div style={{ fontSize: 11, color: "var(--ink-faint)", fontWeight: 600, textTransform: "uppercase", letterSpacing: 0.5 }}>
                    {s.label}
                  </div>
                  <div style={{ fontSize: 14, fontWeight: 600, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
                    {s.value}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="card" style={{ display: "flex", flexDirection: "column" }}>
          <div className="kicker-muted" style={{ marginBottom: 18 }}>
            Model library
          </div>
          <div style={{ display: "flex", gap: 28, marginBottom: "auto" }}>
            <div>
              <div style={{ fontFamily: "var(--font-serif)", fontSize: 34, fontWeight: 600, lineHeight: 1 }}>{installedCount}</div>
              <div style={{ fontSize: 12.5, color: "var(--ink-soft)", marginTop: 5 }}>Installed</div>
            </div>
            <div>
              <div style={{ fontFamily: "var(--font-serif)", fontSize: 34, fontWeight: 600, lineHeight: 1, color: "var(--accent-text)" }}>
                {selectedCount}
              </div>
              <div style={{ fontSize: 12.5, color: "var(--ink-soft)", marginTop: 5 }}>Selected for this run</div>
            </div>
          </div>
          <button className="btn secondary" style={{ marginTop: 18 }} onClick={onModels}>
            <Icon name="boxes" size={16} />
            Manage models
          </button>
        </div>
      </div>
    </div>
  );
}
