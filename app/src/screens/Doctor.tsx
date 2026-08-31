import { Icon } from "../components/Icon";
import type { DoctorCheck, DoctorSnapshot, RepairState } from "../types";

type Props = {
  snapshot: DoctorSnapshot | null;
  showTech: boolean;
  sequenceHelp?: boolean;
  onRun: () => void;
  onRepair: () => void;
  onToggleTech: () => void;
};

const STYLE: Record<string, { bg: string; fg: string; status: string; icon: string }> = {
  passed: { bg: "var(--ok-bg)", fg: "var(--ok)", status: "Ready", icon: "check" },
  warning: { bg: "var(--warn-bg)", fg: "var(--warn)", status: "Notice", icon: "alert-triangle" },
  failed: { bg: "var(--err-bg)", fg: "var(--err)", status: "Failed", icon: "x" },
  blocked: { bg: "var(--err-bg)", fg: "var(--err)", status: "Blocked", icon: "x" },
  checking: { bg: "var(--accent-soft)", fg: "var(--accent-text)", status: "Checking", icon: "loader" },
  repairing: { bg: "var(--accent-soft)", fg: "var(--accent-text)", status: "Fixing", icon: "loader" },
};

function overallOf(snapshot: DoctorSnapshot | null): RepairState {
  if (!snapshot) return "checking";
  if (snapshot.state === "repairing") return "repairing";
  const working = (snapshot.checks || []).some((c) => c.status === "checking" || c.status === "repairing");
  if (snapshot.state === "running" && (working || !(snapshot.checks || []).length)) return "checking";
  return snapshot.overall === "ready" ? "ready" : "attention";
}

export function DoctorScreen({ snapshot, showTech, sequenceHelp, onRun, onRepair, onToggleTech }: Props) {
  const repair = overallOf(snapshot);
  const checks: DoctorCheck[] = snapshot?.checks?.length
    ? snapshot.checks
    : [
        { id: "wait", title: "Doctor", detail: "Connecting to the Bench Engine…", status: "checking" },
      ];
  const busy = repair === "repairing" || repair === "checking";
  const sequence = checks.filter((c) => c.blocking && (c.status === "failed" || c.status === "blocked"));
  const nextFixId = sequence[0]?.id;
  const doctor =
    repair === "ready"
      ? {
          title: "Everything is ready",
          subtitle: snapshot?.subtitle || "All prerequisites are healthy.",
          icon: "shield-check",
          iconBg: "var(--ok-bg)",
          iconFg: "var(--ok)",
          btnLabel: "Re-run checks",
          btnIcon: "refresh-cw",
          primary: false,
          onClick: onRun,
        }
      : repair === "repairing"
        ? {
            title: "Repairing…",
            subtitle: snapshot?.subtitle || "Fixing this PC in the background. No terminal windows will flash.",
            icon: "loader",
            iconBg: "var(--accent-soft)",
            iconFg: "var(--accent-text)",
            btnLabel: "Repairing",
            btnIcon: "loader",
            primary: true,
            onClick: onRepair,
          }
        : repair === "checking"
          ? {
              title: "Checking this PC…",
              subtitle: snapshot?.subtitle || "Confirming Windows, Ollama, storage, and acceleration.",
              icon: "loader",
              iconBg: "var(--info-bg)",
              iconFg: "var(--info)",
              btnLabel: "Checking",
              btnIcon: "loader",
              primary: false,
              onClick: onRun,
            }
          : {
              title: "Needs attention",
              subtitle: snapshot?.subtitle || "Some items need a quick fix before benchmarking.",
              icon: "shield-alert",
              iconBg: "var(--warn-bg)",
              iconFg: "var(--warn)",
              btnLabel: sequence.length > 1 ? "Repair all in sequence" : "Repair Automatically",
              btnIcon: "wrench",
              primary: true,
              onClick: onRepair,
            };

  return (
    <div className="page">
      <div className="kicker" style={{ marginBottom: 10 }}>
        System Doctor
      </div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 20, marginBottom: 26 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
          <div
            style={{
              width: 56,
              height: 56,
              borderRadius: 14,
              background: doctor.iconBg,
              color: doctor.iconFg,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              flex: "none",
            }}
          >
            <Icon name={doctor.icon} size={28} className={busy ? "spin" : undefined} />
          </div>
          <div>
            <h1 className="page-title">{doctor.title}</h1>
            <p className="body" style={{ fontSize: 14, margin: "4px 0 0" }}>
              {doctor.subtitle}
            </p>
          </div>
        </div>
        <button className={`btn ${doctor.primary ? "primary" : "secondary"}`} onClick={doctor.onClick} disabled={busy}>
          <Icon name={doctor.btnIcon} size={18} className={busy ? "spin" : undefined} />
          {doctor.btnLabel}
        </button>
      </div>

      {sequenceHelp && sequence.length ? (
        <div className="card doctor-sequence">
          <h2>Fix issues in order</h2>
          <p>
            Doctor found problems that block benchmarking. Start with step 1 (highlighted below). Use Repair on that row, or Repair all in sequence. Come back to the next failed row until every blocking item is Ready.
          </p>
          <ol>
            {sequence.map((c, i) => (
              <li key={c.id}>
                <strong>Step {i + 1}.</strong> {c.title} — {c.detail}
              </li>
            ))}
          </ol>
        </div>
      ) : null}

      <div className="card" style={{ padding: 0, overflow: "hidden" }}>
        {checks.map((c) => {
          const st = STYLE[c.status] || STYLE.checking;
          const spinning = c.status === "checking" || c.status === "repairing";
          const step = sequence.findIndex((s) => s.id === c.id);
          const isNext = c.id === nextFixId;
          return (
            <div key={c.id} className={`check-row${isNext ? " next-fix" : ""}`}>
              <div
                style={{
                  width: 34,
                  height: 34,
                  borderRadius: 999,
                  background: st.bg,
                  color: st.fg,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  flex: "none",
                }}
              >
                <Icon name={st.icon} size={18} className={spinning ? "spin" : undefined} />
              </div>
              {step >= 0 ? <div className="step-badge">{step + 1}</div> : null}
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ fontSize: 15, fontWeight: 600 }}>{c.title}</div>
                <div style={{ fontSize: 13, color: "var(--ink-soft)", marginTop: 2 }}>{c.detail}</div>
              </div>
              <div className="status-pill" style={{ background: st.bg, color: st.fg }}>
                <span style={{ width: 6, height: 6, borderRadius: 999, background: st.fg }} />
                {st.status}
              </div>
              {(c.action || (step >= 0 && sequenceHelp)) && !busy ? (
                <button className="btn tertiary" onClick={onRepair}>
                  {isNext ? "Repair this first" : c.action || "Repair"}
                </button>
              ) : null}
            </div>
          );
        })}
        <button
          className="btn tertiary"
          onClick={onToggleTech}
          style={{ display: "flex", width: "100%", justifyContent: "flex-start", padding: "16px 22px", color: "var(--ink-soft)" }}
        >
          <Icon name={showTech ? "chevron-down" : "chevron-right"} size={16} />
          Technical details
        </button>
        {showTech ? (
          <div style={{ padding: "0 22px 20px" }}>
            <pre className="tech-log">{snapshot?.tech_log || "No support log yet."}</pre>
          </div>
        ) : null}
      </div>
    </div>
  );
}
