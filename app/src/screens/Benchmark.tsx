import { Icon } from "../components/Icon";
import type { BenchSnapshot } from "../types";

type Props = {
  snapshot: BenchSnapshot | null;
  showLog: boolean;
  canStart: boolean;
  startHint: string;
  onStart: () => void;
  onPause: () => void;
  onStop: () => void;
  onToggleLog: () => void;
};

function fmtElapsed(s?: number) {
  const n = Math.max(0, s || 0);
  const m = Math.floor(n / 60);
  const r = n % 60;
  return `${m}:${String(r).padStart(2, "0")}`;
}

function PhaseTitle({ text }: { text: string }) {
  const parts = text.split(/(\bPhase\s+[12]\b)/i);
  return (
    <div className="bench-phase-title">
      {parts.map((part, i) =>
        /^Phase\s+[12]$/i.test(part) ? (
          <span key={i} className="bench-phase-num">
            {part}
          </span>
        ) : (
          <span key={i}>{part}</span>
        ),
      )}
    </div>
  );
}
function UsageMeter({ icon, label, pct }: { icon: string; label: string; pct?: number | null }) {
  const n = pct == null || Number.isNaN(pct) ? null : Math.max(0, Math.min(100, Math.round(pct)));
  const hot = n != null && n >= 90;
  return (
    <div className={`usage-meter${hot ? " hot" : ""}`}>
      <div className="usage-icon">
        <Icon name={icon} size={22} />
      </div>
      <div>
        <div className="usage-label">{label}</div>
        <div className="usage-value">{n == null ? "—" : `${n}%`}</div>
      </div>
    </div>
  );
}

export function BenchmarkScreen({ snapshot, showLog, canStart, startHint, onStart, onPause, onStop, onToggleLog }: Props) {
  const state = snapshot?.state || "idle";
  const running = state === "running";
  const paused = state === "paused";
  const idle = !running && !paused;
  const pct = idle ? 0 : Math.round(snapshot?.pct || 0);
  const heading = idle ? "Ready to benchmark" : running ? "Benchmarking in progress" : "Paused";
  const current = snapshot?.message || (idle ? "Press Start to begin the sequence" : "");
  const selectedName = snapshot?.selected?.[0];
  const sub =
    snapshot?.detail ||
    (idle
      ? selectedName
        ? `${selectedName} · ${snapshot?.thinking ? "thinking on" : "thinking off"}`
        : "Press Start to choose a model"
      : "");
  const logs = snapshot?.log || [];
  const question = (snapshot?.prompt || "").trim();

  const stats = [
    { label: "Generation speed", value: snapshot?.tok_s != null ? String(snapshot.tok_s) : "—", unit: "tok/s" },
    { label: "Time to first token", value: snapshot?.ttft_s != null ? String(snapshot.ttft_s) : "—", unit: "s" },
    { label: "VRAM headroom", value: snapshot?.headroom_gb != null ? String(snapshot.headroom_gb) : "—", unit: "GB" },
    { label: "Completion", value: snapshot?.completion_pct != null ? String(Math.round(snapshot.completion_pct)) : idle ? "0" : "—", unit: "%" },
  ];

  return (
    <div className="page">
      <div className="kicker" style={{ marginBottom: 10 }}>
        Benchmark progress
      </div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 26 }}>
        <div>
          <h1 className="page-title">{heading}</h1>
          {!canStart && idle ? (
            <p className="body" style={{ fontSize: 13, margin: "8px 0 0", maxWidth: 520 }}>
              {startHint}
            </p>
          ) : null}
        </div>
        <div style={{ display: "flex", flexDirection: "column", alignItems: "flex-end", gap: 10 }}>
          <div style={{ display: "flex", gap: 10 }}>
            {!idle ? (
              <>
                <button className="btn secondary" onClick={onPause}>
                  <Icon name={paused ? "play" : "pause"} size={16} />
                  {paused ? "Resume" : "Pause"}
                </button>
                <button className="btn destructive" onClick={onStop}>
                  <Icon name="square" size={14} />
                  Stop
                </button>
              </>
            ) : (
              <button className="btn primary" style={{ height: 40 }} onClick={onStart} disabled={!canStart} title={canStart ? undefined : startHint}>
                <Icon name="play" size={17} />
                Start Benchmark
              </button>
            )}
          </div>
        </div>
      </div>

      <div className="card elevated" style={{ padding: 30, marginBottom: 22 }}>
        <div className="usage-strip">
          <UsageMeter icon="memory-stick" label="RAM usage" pct={snapshot?.ram_pct} />
          <UsageMeter icon="circuit-board" label="VRAM usage" pct={snapshot?.vram_pct} />
          <UsageMeter icon="cpu" label="CPU usage" pct={snapshot?.cpu_pct} />
        </div>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
          <div className="kicker-muted">Overall progress</div>
          <div style={{ fontSize: 13, color: "var(--ink-soft)" }}>
            {selectedName || snapshot?.message || "One model"}
            {" · "}Elapsed {fmtElapsed(snapshot?.elapsed_s)}
          </div>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 18, marginBottom: 22 }}>
          <div className="progress" style={{ flex: 1, height: 12 }}>
            <span style={{ width: `${pct}%` }} />
          </div>
          <div className="bench-pct">
            {pct}%
          </div>
        </div>
        <div className="bench-phase-card">
          <div className="bench-phase-glyph">
            <Icon name={running ? "loader" : paused ? "pause" : "flag"} size={18} className={running ? "spin" : undefined} />
          </div>
          <div style={{ flex: 1, minWidth: 0 }}>
            <PhaseTitle text={current} />
            {idle && sub ? <div className="bench-phase-idle-sub">{sub}</div> : null}
          </div>
        </div>
        {!idle && question ? (
          <div className="scenario-stage">
            <div className="scenario-stage-rail" aria-hidden="true" />
            <div className="scenario-stage-body">
              <p className="scenario-stage-copy">{question}</p>
            </div>
            {snapshot?.answer ? <div className="scenario-stage-note">{snapshot.answer}</div> : null}
          </div>
        ) : null}
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 16, marginBottom: 22 }}>
        {stats.map((b) => (
          <div key={b.label} className="stat-tile">
            <div className="kicker-muted" style={{ fontSize: 11.5, letterSpacing: 0.5, marginBottom: 9 }}>
              {b.label}
            </div>
            <div className="metric">
              {b.value}
              <span style={{ fontSize: 14, fontWeight: 500, color: "var(--ink-faint)" }}> {b.unit}</span>
            </div>
          </div>
        ))}
      </div>

      <div className="card" style={{ padding: 0, overflow: "hidden" }}>
        <button
          className="btn tertiary"
          onClick={onToggleLog}
          style={{ display: "flex", width: "100%", justifyContent: "flex-start", padding: "16px 22px", color: "var(--ink-soft)" }}
        >
          <Icon name={showLog ? "chevron-down" : "chevron-right"} size={16} />
          Live technical log
        </button>
        {showLog ? (
          <div style={{ padding: "0 22px 20px" }}>
            <pre className="tech-log">{logs.length ? logs.join("\n") : "No run activity yet."}</pre>
          </div>
        ) : null}
      </div>
    </div>
  );
}
