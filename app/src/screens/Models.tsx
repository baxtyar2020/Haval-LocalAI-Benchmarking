import { Icon } from "../components/Icon";
import type { LibraryItem, LibraryResponse, ModelFilter } from "../types";

const FILTERS: ModelFilter[] = ["Installed", "Preferred", "Search Ollama"];

type Props = {
  filter: ModelFilter;
  query: string;
  library: LibraryResponse | null;
  onFilter: (f: ModelFilter) => void;
  onQuery: (q: string) => void;
  onToggle: (name: string, selected: boolean) => void;
  onDownload: (name: string) => void;
  onCancel: (jobId: string) => void;
  onRetry: (jobId: string) => void;
  onRemove: (name: string) => void;
};

export function ModelsScreen({
  filter,
  query,
  library,
  onFilter,
  onQuery,
  onToggle,
  onDownload,
  onCancel,
  onRetry,
  onRemove,
}: Props) {
  const rows = library?.items ?? [];
  const free = library?.storage?.free_gb;
  const total = library?.storage?.total_gb;
  const usedPct = free != null && total ? Math.min(100, Math.round(((total - free) / total) * 100)) : 0;

  return (
    <div className="page">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-end", marginBottom: 22 }}>
        <div>
          <div className="kicker" style={{ marginBottom: 8 }}>
            Model library
          </div>
          <h1 className="page-title">Choose the model for this run</h1>
          <p className="body" style={{ fontSize: 13, margin: "8px 0 0", maxWidth: 480 }}>
            One model per report. Run again to test another model.
          </p>
        </div>
        <div style={{ textAlign: "right" }}>
          <div className="kicker-muted" style={{ marginBottom: 6, letterSpacing: 0.5 }}>
            Storage
          </div>
          <div style={{ fontSize: 13.5, color: "var(--ink-soft)" }}>
            {free != null ? (
              <>
                <strong style={{ color: "var(--ink)" }}>{free} GB</strong> free
                {total != null ? ` of ${total} GB` : ""}
              </>
            ) : (
              "Measuring…"
            )}
          </div>
          <div className="progress" style={{ width: 190, height: 6, marginTop: 6 }}>
            <span style={{ width: `${usedPct}%` }} />
          </div>
        </div>
      </div>

      <div style={{ display: "flex", alignItems: "center", gap: 14, marginBottom: 18 }}>
        <label className="search">
          <Icon name="search" size={18} style={{ color: "var(--ink-faint)" }} />
          <span className="visually-hidden" style={{ position: "absolute", width: 1, height: 1, overflow: "hidden" }}>
            Search models
          </span>
          <input
            value={query}
            onChange={(e) => {
              onQuery(e.target.value);
              if (e.target.value) onFilter("Search Ollama");
            }}
            placeholder="Filter the list or search the Ollama library…"
          />
        </label>
        <div className="segmented" role="tablist" aria-label="Model source">
          {FILTERS.map((f) => (
            <button key={f} className={filter === f ? "active" : ""} onClick={() => onFilter(f)} role="tab" aria-selected={filter === f}>
              {f}
            </button>
          ))}
        </div>
      </div>

      {library && !library.ollama_ok ? (
        <div className="card" style={{ marginBottom: 16 }}>
          Ollama’s API is not ready. Open Doctor to start or repair it before downloading models.
        </div>
      ) : null}

      <div className="card" style={{ padding: 0, overflow: "hidden" }}>
        {!library ? (
          <div className="check-row" style={{ color: "var(--ink-soft)" }}>
            Loading models from this PC…
          </div>
        ) : rows.length === 0 ? (
          <div className="check-row" style={{ color: "var(--ink-soft)" }}>
            {filter === "Search Ollama"
              ? query.trim()
                ? "Searching the Ollama library…"
                : "Type a model name to search the Ollama library. Results list names, tags, parameters, and precision/quant. Download uses that exact ollama pull command."
              : filter === "Preferred"
                ? "The five-model Standard Roster will appear here."
                : "No models are installed on this PC yet."}
          </div>
        ) : null}
        {rows.map((m) => (
          <ModelRow
            key={m.id}
            item={m}
            onToggle={onToggle}
            onDownload={onDownload}
            onCancel={onCancel}
            onRetry={onRetry}
            onRemove={onRemove}
          />
        ))}
      </div>
    </div>
  );
}

function ModelRow({
  item,
  onToggle,
  onDownload,
  onCancel,
  onRetry,
  onRemove,
}: {
  item: LibraryItem;
  onToggle: (name: string, selected: boolean) => void;
  onDownload: (name: string) => void;
  onCancel: (jobId: string) => void;
  onRetry: (jobId: string) => void;
  onRemove: (name: string) => void;
}) {
  const sel = !!item.selected;
  const dl = item.download;
  const state = dl?.state;
  const downloading = state === "queued" || state === "downloading" || state === "verifying";
  const failed = state === "failed";
  const installed = !!item.installed && !downloading;
  const available = !installed && !downloading;
  const totalB = item.params_total && item.params_total !== "—" ? item.params_total : null;
  const activeB = item.params_active && item.params_active !== "—" ? item.params_active : totalB;
  const quant = (item.quant || "").trim();
  const restMeta = [item.size_label].filter(Boolean).join(" · ");

  return (
    <div className={`model-row${sel ? " selected" : ""}`}>
      <button
        className={`checkbox${sel ? " on" : ""}`}
        onClick={() => item.selectable && onToggle(item.name, !sel)}
        disabled={!item.selectable}
        aria-pressed={sel}
        aria-label={`Select ${item.display_name || item.name} for this benchmark run`}
        title={item.selectable ? "Select for this run (one model only)" : "Install and verify this model before selecting it"}
      >
        {sel ? <Icon name="check" size={14} /> : null}
      </button>
      <div
        style={{
          width: 40,
          height: 40,
          borderRadius: 10,
          background: "var(--canvas)",
          border: "1px solid var(--border)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          color: "var(--ink-soft)",
          flex: "none",
        }}
      >
        <Icon name="box" size={19} />
      </div>
      <div style={{ flex: 1, minWidth: 180 }}>
        <div style={{ fontSize: 15, fontWeight: 600, display: "flex", alignItems: "center", gap: 8, flexWrap: "wrap" }}>
          {item.display_name || item.name}
          {item.tag ? (
            <span style={{ fontSize: 10.5, fontWeight: 600, color: "var(--ink-faint)", border: "1px solid var(--border)", borderRadius: 5, padding: "1px 6px", background: "var(--canvas)" }}>
              {item.tag}
            </span>
          ) : null}
          {item.preferred ? (
            <span style={{ fontSize: 10.5, fontWeight: 600, color: "var(--accent-text)" }}>Preferred</span>
          ) : null}
        </div>
        <div className="param-line">
          {item.params_moe ? <span className="param-moe">MoE</span> : null}
          {restMeta ? <span className="param-rest">{restMeta}</span> : null}
          {item.pull_command && !item.installed ? <span className="pull-cmd">{item.pull_command}</span> : null}
          {item.validation?.detail ? ` · ${item.validation.detail}` : ""}
          {dl?.error ? ` · ${dl.error}` : ""}
        </div>
      </div>
      <div className="param-col total-col">
        <span className="param-col-kicker">Total</span>
        <strong>{totalB || "—"}</strong>
      </div>
      <div className="param-col active-col">
        <span className="param-col-kicker">Active</span>
        <strong>{activeB || "—"}</strong>
      </div>
      <div className="param-col quant-col">
        <span className="param-col-kicker">Precision / Quant</span>
        <strong>{quant || "—"}</strong>
      </div>
      <div style={{ width: 220, flex: "none", marginLeft: "auto", display: "flex", justifyContent: "flex-end", alignItems: "center", gap: 8 }}>
        {downloading ? (
          <div style={{ width: "100%" }}>
            <div style={{ display: "flex", justifyContent: "space-between", fontSize: 12, color: "var(--ink-soft)", marginBottom: 5 }}>
              <span>{dl?.stage || "Downloading"}</span>
              <span style={{ fontWeight: 600, color: "var(--ink)" }}>{dl?.pct ?? 0}%</span>
            </div>
            <div style={{ display: "flex", alignItems: "center", gap: 9 }}>
              <div className={`progress${state === "downloading" ? " striped" : ""}`} style={{ flex: 1 }}>
                <span style={{ width: `${dl?.pct ?? 0}%` }} />
              </div>
              {dl?.id ? (
                <button className="icon-btn" style={{ width: 32, height: 32 }} aria-label="Cancel download" onClick={() => onCancel(dl.id)}>
                  <Icon name="x" size={15} />
                </button>
              ) : null}
            </div>
          </div>
        ) : null}
        {installed ? (
          <>
            <div className="status-pill" style={{ background: "var(--ok-bg)", color: "var(--ok)", padding: "6px 14px" }}>
              <Icon name="check-circle-2" size={15} />
              Installed
            </div>
            <button
              className="btn tertiary"
              style={{ color: "var(--err)" }}
              onClick={() => {
                if (window.confirm(`Remove ${item.name} from this PC? This deletes the model files. Excluding it from a benchmark does not require this.`)) {
                  onRemove(item.name);
                }
              }}
            >
              Remove
            </button>
          </>
        ) : null}
        {available ? (
          <button className="btn secondary" style={{ height: 38 }} onClick={() => onDownload(item.name)}>
            <Icon name="download" size={15} />
            Download
          </button>
        ) : null}
        {failed && !downloading ? (
          <button className="btn secondary" style={{ height: 38 }} onClick={() => dl?.id && onRetry(dl.id)}>
            Retry
          </button>
        ) : null}
      </div>
    </div>
  );
}
