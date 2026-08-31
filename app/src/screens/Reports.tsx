import { Icon } from "../components/Icon";
import type { EngineRun } from "../types";

type Props = {
  detailId: string | null;
  runs: EngineRun[];
  onOpen: (id: string) => void;
  onBack: () => void;
  onOpenHtml: (id: string) => void;
  onPdf: (id: string) => void;
  onFolder: (id: string) => void;
  onDelete: (id: string) => void;
};

function modelsOf(run: EngineRun): string[] {
  try {
    return JSON.parse(run.models_json || "[]");
  } catch {
    return [];
  }
}

function reportTitle(run: EngineRun): string {
  const fromReport = (run.headline || "").trim();
  if (fromReport) return fromReport;
  const model = modelsOf(run)[0];
  return model ? `How this PC performed on ${model}` : "How this PC performed";
}

export function ReportsScreen({ detailId, runs, onOpen, onBack, onOpenHtml, onPdf, onFolder, onDelete }: Props) {
  const latest = runs.find((r) => r.id === detailId) || null;
  if (latest) {
    return (
      <div className="page">
        <button className="btn tertiary" onClick={onBack} style={{ marginBottom: 18, color: "var(--ink-soft)" }}>
          <Icon name="arrow-left" size={16} />
          All reports
        </button>
        <div className="card elevated" style={{ padding: 34, marginBottom: 22 }}>
          <div className="kicker" style={{ marginBottom: 12 }}>
            Hardware-first report · {latest.status}
          </div>
          <h1 className="display" style={{ fontSize: 38, lineHeight: "42px", margin: "0 0 10px", maxWidth: 720 }}>
            {reportTitle(latest)}
          </h1>
          <p className="body" style={{ fontSize: 15, lineHeight: "23px", margin: "0 0 26px", maxWidth: 680 }}>
            Run {latest.id}. Open the self-contained HTML report. Empty cells in the report are em dashes, never invented scores.
          </p>
          <div style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>
            <button className="btn primary" onClick={() => onOpenHtml(latest.id)}>
              <Icon name="book-open" size={17} />
              Open Report
            </button>
            <button className="btn secondary" style={{ height: 44 }} onClick={() => onPdf(latest.id)}>
              <Icon name="download" size={17} />
              Export PDF
            </button>
            <button className="btn secondary" style={{ height: 44 }} onClick={() => onFolder(latest.id)}>
              <Icon name="folder-open" size={17} />
              Show in folder
            </button>
            <button className="btn destructive" style={{ height: 44 }} onClick={() => onDelete(latest.id)}>
              <Icon name="trash" size={16} />
              Delete report
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="page">
      <div className="kicker" style={{ marginBottom: 10 }}>
        Reports
      </div>
      <h1 className="display" style={{ margin: "0 0 26px" }}>
        Your benchmark library
      </h1>
      {runs.length === 0 ? (
        <div className="card">No runs stored yet. Start a benchmark to collect evidence for this PC.</div>
      ) : (
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 22 }}>
          {runs.map((r) => {
            const models = modelsOf(r);
            const when = r.started_at ? new Date(r.started_at).toLocaleString() : r.id;
            return (
              <div key={r.id} className="card elevated" style={{ padding: 20 }}>
                <div style={{ fontSize: 12, color: "var(--ink-faint)", fontWeight: 600, marginBottom: 6 }}>
                  {when} · {r.status}
                </div>
                <div style={{ fontFamily: "var(--font-serif)", fontSize: 19, fontWeight: 500, marginBottom: 4, lineHeight: 1.25 }}>
                  {reportTitle(r)}
                </div>
                <div style={{ fontSize: 13, color: "var(--ink-soft)", marginBottom: 16 }}>
                  {models[0] || "No model recorded"} · 20 personas
                </div>
                <div style={{ display: "flex", gap: 10 }}>
                  <button className="btn primary" style={{ flex: 1, height: 40 }} onClick={() => onOpen(r.id)}>
                    <Icon name="book-open" size={16} />
                    Open Report
                  </button>
                  <button className="icon-btn" style={{ width: 40, height: 40 }} aria-label="Show in folder" onClick={() => onFolder(r.id)}>
                    <Icon name="folder" size={16} />
                  </button>
                  <button className="icon-btn" style={{ width: 40, height: 40, color: "var(--err)" }} aria-label="Delete report" onClick={() => onDelete(r.id)}>
                    <Icon name="trash" size={16} />
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
