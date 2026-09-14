import { useMemo, useRef, useState } from "react";
import { ConfirmDelete } from "../components/ConfirmDelete";
import { Icon } from "../components/Icon";
import type { EngineRun } from "../types";
import screen6 from "../assets/wizard/screen6.png";

export type CompareSource = {
  id: string;
  started_at?: string;
  status?: string;
  model_name: string;
  size_line: string;
  final?: number | null;
  machine?: string;
  headline?: string;
};

type UploadChip = {
  key: string;
  name: string;
  html: string;
  modelHint: string;
  error?: string;
};

type Props = {
  sources: CompareSource[];
  thisMachine: string;
  runs: EngineRun[];
  busy?: boolean;
  error?: string | null;
  lastId?: string | null;
  onCompare: (runIds: string[], uploads: { name: string; html: string }[]) => void;
  onOpenHtml: (id: string) => void;
  onFolder: (id: string) => void;
  onDelete: (ids: string[]) => Promise<boolean>;
  deleting?: boolean;
  onIntroBack?: () => void;
  skipIntro?: boolean;
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

function inspectHtml(html: string, fileName: string): { modelHint: string; error?: string } {
  const low = html.toLowerCase();
  if (!low.includes("haval localai bench") && !low.includes("haval localai benchmarking")) {
    return { modelHint: fileName, error: "Not a Haval bench report" };
  }
  if (low.includes("cross-model comparison")) {
    return { modelHint: fileName, error: "Not a Haval bench report" };
  }
  const title = html.match(/<title[^>]*>([\s\S]*?)<\/title>/i);
  const hint = title ? title[1].replace(/<[^>]+>/g, "").trim() : fileName;
  return { modelHint: hint || fileName };
}

export function CompareScreen({
  sources,
  thisMachine,
  runs,
  busy,
  error,
  lastId,
  onCompare,
  onOpenHtml,
  onFolder,
  onDelete,
  deleting,
  onIntroBack,
  skipIntro = false,
}: Props) {
  const [brief, setBrief] = useState(!skipIntro);
  const [selected, setSelected] = useState<string[]>([]);
  const [uploads, setUploads] = useState<UploadChip[]>([]);
  const [query, setQuery] = useState("");
  const [thisPcOnly, setThisPcOnly] = useState(true);
  const [dragOver, setDragOver] = useState(false);
  const [confirmId, setConfirmId] = useState<string | null>(null);
  const fileRef = useRef<HTMLInputElement>(null);

  const hasThisMachine = sources.some((s) => thisMachine && s.machine && s.machine.toUpperCase() === thisMachine.toUpperCase());
  const filteredSources = useMemo(() => {
    const q = query.trim().toLowerCase();
    return sources.filter((s) => {
      if (thisPcOnly && hasThisMachine && thisMachine && (s.machine || "").toUpperCase() !== thisMachine.toUpperCase()) {
        return false;
      }
      if (!q) return true;
      return `${s.model_name} ${s.size_line} ${s.id} ${s.machine}`.toLowerCase().includes(q);
    });
  }, [sources, query, thisPcOnly, hasThisMachine, thisMachine]);

  const acceptedUploads = uploads.filter((u) => !u.error);
  const modelKeys = new Set<string>();
  for (const id of selected) {
    const row = sources.find((s) => s.id === id);
    if (row?.model_name) modelKeys.add(row.model_name.toLowerCase());
  }
  for (const u of acceptedUploads) {
    modelKeys.add((u.modelHint || u.name).toLowerCase());
  }
  const reportCount = selected.length + acceptedUploads.length;
  const canRun = reportCount >= 2 && modelKeys.size >= 2 && !busy;
  const comparisons = useMemo(
    () =>
      runs
        .filter(isComparison)
        .slice()
        .sort((a, b) => String(b.started_at || b.id).localeCompare(String(a.started_at || a.id))),
    [runs],
  );
  const recentComparison = (lastId ? comparisons.find((r) => r.id === lastId) : null) || comparisons[0] || null;

  function runComparison() {
    onCompare(
      selected,
      acceptedUploads.map((u) => ({ name: u.name, html: u.html })),
    );
  }

  function toggle(id: string) {
    setSelected((cur) => (cur.includes(id) ? cur.filter((x) => x !== id) : [...cur, id]));
  }

  async function takeFiles(files: FileList | File[]) {
    const list = Array.from(files);
    const next: UploadChip[] = [];
    for (const file of list) {
      if (!/\.html?$/i.test(file.name)) {
        next.push({ key: `${file.name}-${file.size}`, name: file.name, html: "", modelHint: file.name, error: "Not a Haval bench report" });
        continue;
      }
      const html = await file.text();
      const inspected = inspectHtml(html, file.name);
      next.push({
        key: `${file.name}-${file.size}-${file.lastModified}`,
        name: file.name,
        html,
        modelHint: inspected.modelHint,
        error: inspected.error,
      });
    }
    setUploads((cur) => {
      const seen = new Set(cur.map((u) => u.key));
      const merged = [...cur];
      for (const item of next) {
        if (!seen.has(item.key)) merged.push(item);
      }
      return merged;
    });
  }

  function clearChooser() {
    setSelected([]);
    setUploads([]);
  }

  if (brief) {
    return (
      <div className="wizard-brief wizard-brief-compare" role="dialog" aria-labelledby="compare-brief-title">
        <img className="wizard-brief-art" src={screen6} alt="" />
        <div className="wizard-brief-dock">
          <div className="wizard-brief-kicker">Compare reports</div>
          <h1 className="wizard-brief-title" id="compare-brief-title">
            Compare Different <span className="wizard-brief-accent">LLM model</span> sizes
          </h1>
          <p className="wizard-brief-copy">
            <span>Put two or more benchmarking reports you already ran in this app on one page. </span>
            <span className="tone-accent">Same PC. Different LLM sizes. </span>
            <span>Quality, time side by side and overall evaluation.</span>
          </p>
          <div className="wizard-brief-actions">
            <button type="button" className="btn tertiary" onClick={onIntroBack}>
              Back
            </button>
            <button type="button" className="btn primary" onClick={() => setBrief(false)}>
              OK, let’s do it
              <Icon name="arrow-right" size={16} />
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="page compare-page">
      <div className="compare-hero">
        <div>
          <div className="kicker">Compare reports</div>
          <h1 className="display home-headline">
            Size is not the winner. <span>Fit is.</span>
          </h1>
          <p className="home-lead compare-lead">
            This is <strong>not a new benchmark</strong>. It reads reports you already have — from this library or files you upload — and builds one comparison page for this PC.
          </p>
        </div>
        <aside className="compare-explain" aria-label="How compare works">
          <article>
            <Icon name="ban" size={18} />
            <div>
              <strong>No extra run</strong>
              <span>The models are not called again. Scores and times come from the reports you pick.</span>
            </div>
          </article>
          <article>
            <Icon name="columns-2" size={18} />
            <div>
              <strong>Two models, minimum</strong>
              <span>Pick at least two different models. Same-model repeats on this PC merge into one column.</span>
            </div>
          </article>
          <article>
            <Icon name="scroll-text" size={18} />
            <div>
              <strong>One page to keep</strong>
              <span>You get a scoreboard, capability bars, and task times. It is saved in Reports like any other run.</span>
            </div>
          </article>
        </aside>
      </div>

      <div className="compare-actions">
        <button
          className="btn primary"
          type="button"
          disabled={!recentComparison}
          onClick={() => recentComparison && onOpenHtml(recentComparison.id)}
        >
          <Icon name="book-open" size={16} />
          Open recent comparison report
        </button>
        <button className="btn primary" type="button" disabled={!canRun} onClick={runComparison}>
          {busy ? "Building…" : "Run comparison"}
        </button>
      </div>

      <div className="compare-grid">
        <section className="compare-pane">
          <h2>Saved reports</h2>
          <p className="compare-pane-lead">Completed single-model runs on this install.</p>
          <div className="compare-tools">
            <label className="compare-search">
              <Icon name="search" size={14} />
              <input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search models" />
            </label>
            {hasThisMachine ? (
              <button className={`chip-btn${thisPcOnly ? " on" : ""}`} type="button" onClick={() => setThisPcOnly((v) => !v)}>
                This machine
              </button>
            ) : null}
          </div>
          {filteredSources.length === 0 ? (
            <p className="body compare-empty">No completed single-model reports to compare. Finish a benchmark first, or upload HTML on the right.</p>
          ) : (
            <ul className="compare-list">
              {filteredSources.map((s) => {
                const on = selected.includes(s.id);
                return (
                  <li key={s.id}>
                    <button type="button" className={`compare-pick${on ? " on" : ""}`} onClick={() => toggle(s.id)}>
                      <span className={`check${on ? " on" : ""}`} aria-hidden>
                        {on ? <Icon name="check" size={14} /> : null}
                      </span>
                      <span className="compare-pick-copy">
                        <strong>{s.model_name}</strong>
                        <span>
                          {s.size_line || "Size unknown"}
                          {s.final != null ? ` · Final ${s.final}` : ""}
                        </span>
                        <span>
                          {s.id} · {s.machine || "Unknown PC"}
                        </span>
                      </span>
                    </button>
                  </li>
                );
              })}
            </ul>
          )}
        </section>
        <section className="compare-pane">
          <h2>Upload reports</h2>
          <p className="compare-pane-lead">Haval measured-run HTML from this or another copy of the app.</p>
          <input
            ref={fileRef}
            type="file"
            accept=".html,.htm,text/html"
            multiple
            hidden
            onChange={(e) => {
              if (e.target.files) void takeFiles(e.target.files);
              e.target.value = "";
            }}
          />
          <button
            type="button"
            className={`compare-drop${dragOver ? " over" : ""}`}
            onClick={() => fileRef.current?.click()}
            onDragOver={(e) => {
              e.preventDefault();
              setDragOver(true);
            }}
            onDragLeave={() => setDragOver(false)}
            onDrop={(e) => {
              e.preventDefault();
              setDragOver(false);
              if (e.dataTransfer.files.length) void takeFiles(e.dataTransfer.files);
            }}
          >
            Drop .html files here or browse
          </button>
          {uploads.length > 0 ? (
            <ul className="compare-chips">
              {uploads.map((u) => (
                <li key={u.key} className={u.error ? "bad" : ""}>
                  <span>
                    {u.name}
                    {u.modelHint && u.modelHint !== u.name ? ` · ${u.modelHint}` : ""}
                    {u.error ? ` · ${u.error}` : ""}
                  </span>
                  <button type="button" aria-label={`Remove ${u.name}`} onClick={() => setUploads((cur) => cur.filter((x) => x.key !== u.key))}>
                    <Icon name="x" size={12} />
                  </button>
                </li>
              ))}
            </ul>
          ) : null}
        </section>
      </div>

      <div className="compare-bar">
        <span>Selected: {reportCount}</span>
        <button className="btn tertiary" type="button" onClick={clearChooser} disabled={reportCount === 0}>
          Clear
        </button>
        <button className="btn primary" type="button" disabled={!canRun} onClick={runComparison}>
          {busy ? "Building…" : "Run comparison"}
        </button>
      </div>
      {error ? <p className="compare-err">{error}</p> : null}

      {comparisons.length > 0 ? (
        <section className="compare-history">
          <div className="kicker">Saved comparisons</div>
          <ul className="reports-list">
            {comparisons.map((r) => (
              <li key={r.id} className="reports-row">
                <div className="reports-row-copy">
                  <div className="reports-row-title">{r.headline || `Comparison · ${modelsOf(r).length} models`}</div>
                  <div className="reports-row-meta">
                    <span>{formatWhen(r.started_at, r.id)}</span>
                    <span>{modelsOf(r).join(" · ") || "Comparison"}</span>
                  </div>
                </div>
                <div className="reports-row-actions">
                  <button className="reports-open" type="button" onClick={() => onOpenHtml(r.id)}>
                    Open
                  </button>
                  <button className="icon-btn reports-icon" type="button" aria-label="Show in folder" onClick={() => onFolder(r.id)}>
                    <Icon name="folder" size={15} />
                  </button>
                  <button className="icon-btn reports-icon reports-icon-del" type="button" aria-label="Delete comparison" onClick={() => setConfirmId(r.id)}>
                    <Icon name="trash" size={14} />
                  </button>
                </div>
              </li>
            ))}
          </ul>
        </section>
      ) : null}
      {confirmId ? (
        <ConfirmDelete
          count={1}
          busy={deleting}
          onCancel={() => setConfirmId(null)}
          onConfirm={() => {
            void onDelete([confirmId]).then((ok) => {
              if (ok) setConfirmId(null);
            });
          }}
        />
      ) : null}
    </div>
  );
}
