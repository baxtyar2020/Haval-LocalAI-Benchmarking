import { useEffect, useState } from "react";
import { ConfirmDelete } from "../components/ConfirmDelete";
import { Icon } from "../components/Icon";
import type { EngineRun } from "../types";

type Props = {
  detailId: string | null;
  runs: EngineRun[];
  deleting?: boolean;
  deleteError?: string | null;
  onOpen: (id: string) => void;
  onBack: () => void;
  onOpenHtml: (id: string) => void;
  onPdf: (id: string) => void;
  onFolder: (id: string) => void;
  onDelete: (ids: string[]) => Promise<boolean>;
  onRefresh: () => void;
  onGoCompare: () => void;
};

function modelsOf(run: EngineRun): string[] {
  try {
    return JSON.parse(run.models_json || "[]");
  } catch {
    return [];
  }
}

function isComparison(run: EngineRun): boolean {
  try {
    return (JSON.parse(run.summary_json || "{}") as { kind?: string }).kind === "comparison";
  } catch {
    return false;
  }
}

function reportTitle(run: EngineRun): string {
  const fromReport = (run.headline || "").trim();
  if (fromReport) return fromReport;
  if (isComparison(run)) {
    const n = modelsOf(run).length;
    return `Comparison · ${n} models`;
  }
  const model = modelsOf(run)[0];
  return model ? `How this PC performed on ${model}` : "How this PC performed";
}

function formatWhen(iso?: string, fallback?: string): string {
  if (!iso) return fallback || "";
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return fallback || "";
  return d.toLocaleString(undefined, {
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });
}

export function ReportsScreen({
  detailId,
  runs,
  deleting,
  deleteError,
  onOpen,
  onBack,
  onOpenHtml,
  onPdf,
  onFolder,
  onDelete,
  onRefresh,
  onGoCompare,
}: Props) {
  const [picking, setPicking] = useState(false);
  const [selected, setSelected] = useState<string[]>([]);
  const [confirmIds, setConfirmIds] = useState<string[] | null>(null);

  const latest = runs.find((r) => r.id === detailId) || null;
  const allIds = runs.map((r) => r.id);
  const allOn = allIds.length > 0 && allIds.every((id) => selected.includes(id));

  useEffect(() => {
    setSelected((cur) => cur.filter((id) => runs.some((r) => r.id === id)));
  }, [runs]);

  function toggle(id: string) {
    setSelected((cur) => (cur.includes(id) ? cur.filter((x) => x !== id) : [...cur, id]));
  }

  function closePick() {
    setPicking(false);
    setSelected([]);
    setConfirmIds(null);
  }

  async function confirmDelete() {
    if (!confirmIds?.length) return;
    const ok = await onDelete(confirmIds);
    if (ok) closePick();
    else setConfirmIds(null);
  }

  if (latest && !picking) {
    const models = modelsOf(latest);
    const compare = isComparison(latest);
    return (
      <div className="page reports-page">
        <button className="btn tertiary reports-back" type="button" onClick={onBack}>
          <Icon name="arrow-left" size={15} />
          All reports
        </button>
        <div className="kicker">Report · {latest.status || "saved"}</div>
        <h1 className="page-title reports-detail-title">{reportTitle(latest)}</h1>
        <p className="body reports-detail-lead">
          {compare ? models.join(" · ") || "Comparison" : models[0] || "No model recorded"}
          {latest.started_at ? ` · ${formatWhen(latest.started_at, latest.id)}` : ""}
        </p>
        <div className="reports-detail-actions">
          <button className="btn primary" type="button" onClick={() => onOpenHtml(latest.id)}>
            <Icon name="book-open" size={16} />
            Open report
          </button>
          <button className="btn secondary" type="button" onClick={() => onPdf(latest.id)}>
            <Icon name="download" size={15} />
            PDF
          </button>
          <button className="btn secondary" type="button" onClick={() => onFolder(latest.id)}>
            <Icon name="folder-open" size={15} />
            Folder
          </button>
          <button className="btn tertiary reports-delete" type="button" onClick={() => setConfirmIds([latest.id])}>
            <Icon name="trash" size={14} />
            Delete
          </button>
        </div>
        {deleteError ? <p className="compare-err">{deleteError}</p> : null}
        {confirmIds ? (
          <ConfirmDelete count={confirmIds.length} busy={deleting} onCancel={() => setConfirmIds(null)} onConfirm={() => void confirmDelete()} />
        ) : null}
      </div>
    );
  }

  if (picking) {
    return (
      <div className="page reports-page">
        <button className="btn tertiary reports-back" type="button" onClick={closePick}>
          <Icon name="arrow-left" size={15} />
          Reports
        </button>
        <div className="kicker">Delete reports</div>
        <h1 className="page-title">Choose what to remove from this PC.</h1>
        <p className="body reports-detail-lead">Select all, or tick the reports you want gone. Nothing is deleted until you confirm.</p>
        {runs.length === 0 ? (
          <p className="body reports-empty">There are no reports left to delete.</p>
        ) : (
          <>
            <div className="compare-bar">
              <span>Selected: {selected.length}</span>
              <button className="btn tertiary" type="button" onClick={closePick}>
                Cancel
              </button>
              <button className="btn danger" type="button" disabled={selected.length === 0 || deleting} onClick={() => setConfirmIds(selected)}>
                <Icon name="trash" size={15} />
                Delete
              </button>
            </div>
            <button className={`reports-pick${allOn ? " on" : ""}`} type="button" onClick={() => setSelected(allOn ? [] : allIds)}>
              <span className={`checkbox${allOn ? " on" : ""}`} aria-hidden>
                {allOn ? <Icon name="check" size={14} /> : null}
              </span>
              <span className="reports-pick-copy">
                <strong>Select all</strong>
                <span>
                  {selected.length} of {runs.length} selected
                </span>
              </span>
            </button>
            <ul className="reports-pick-list">
              {runs.map((r) => {
                const models = modelsOf(r);
                const compare = isComparison(r);
                const on = selected.includes(r.id);
                return (
                  <li key={r.id}>
                    <button type="button" className={`reports-pick${on ? " on" : ""}`} onClick={() => toggle(r.id)}>
                      <span className={`checkbox${on ? " on" : ""}`} aria-hidden>
                        {on ? <Icon name="check" size={14} /> : null}
                      </span>
                      <span className="reports-pick-copy">
                        <strong>{reportTitle(r)}</strong>
                        <span>
                          {formatWhen(r.started_at, r.id)}
                          {compare ? " · comparison" : r.status ? ` · ${r.status}` : ""}
                          {` · ${compare ? models.join(" · ") || "Comparison" : models[0] || "No model recorded"}`}
                        </span>
                      </span>
                    </button>
                  </li>
                );
              })}
            </ul>
          </>
        )}
        <div className="compare-bar">
          <span>Selected: {selected.length}</span>
          <button className="btn tertiary" type="button" onClick={closePick}>
            Cancel
          </button>
          <button className="btn danger" type="button" disabled={selected.length === 0 || deleting} onClick={() => setConfirmIds(selected)}>
            <Icon name="trash" size={15} />
            Delete
          </button>
        </div>
        {deleteError ? <p className="compare-err">{deleteError}</p> : null}
        {confirmIds ? (
          <ConfirmDelete count={confirmIds.length} busy={deleting} onCancel={() => setConfirmIds(null)} onConfirm={() => void confirmDelete()} />
        ) : null}
      </div>
    );
  }

  return (
    <div className="page reports-page">
      <div className="reports-head">
        <div>
          <div className="kicker">Reports</div>
          <h1 className="page-title">Your benchmark library</h1>
        </div>
        <div className="reports-head-actions">
          {runs.length > 0 ? <span className="reports-count">{runs.length} saved</span> : null}
          <button className="btn secondary" type="button" onClick={onRefresh}>
            <Icon name="refresh-cw" size={15} />
            Refresh
          </button>
          <button
            className="btn secondary"
            type="button"
            disabled={runs.length === 0}
            onClick={() => setPicking(true)}
          >
            <Icon name="trash" size={15} />
            Delete reports
          </button>
          <button className="btn secondary" type="button" onClick={onGoCompare}>
            <Icon name="columns-2" size={15} />
            Compare
          </button>
        </div>
      </div>

      {runs.length === 0 ? (
        <p className="body reports-empty">No runs stored yet. Start a benchmark to collect evidence for this PC.</p>
      ) : (
        <ul className="reports-list">
          {runs.map((r) => {
            const models = modelsOf(r);
            const compare = isComparison(r);
            return (
              <li key={r.id} className="reports-row">
                <div className="reports-row-copy">
                  <div className="reports-row-title">{reportTitle(r)}</div>
                  <div className="reports-row-meta">
                    <span>{formatWhen(r.started_at, r.id)}</span>
                    <span>{compare ? "comparison" : r.status || "saved"}</span>
                    <span>{compare ? models.join(" · ") || "Comparison" : models[0] || "No model recorded"}</span>
                  </div>
                </div>
                <div className="reports-row-actions">
                  <button className="reports-open" type="button" onClick={() => onOpen(r.id)}>
                    Open
                  </button>
                  <button className="icon-btn reports-icon" type="button" aria-label="Show in folder" onClick={() => onFolder(r.id)}>
                    <Icon name="folder" size={15} />
                  </button>
                </div>
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}
