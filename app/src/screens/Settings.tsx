import { invoke } from "@tauri-apps/api/core";
import { Icon } from "../components/Icon";
import { COLOR_THEME_CHOICES, type ColorTheme } from "../theme";
import type { UpdateStatus } from "../update";

type Props = {
  reportDir: string;
  onReportDir: (path: string) => void;
  colorTheme: ColorTheme;
  onColorTheme: (theme: ColorTheme) => void;
  update: UpdateStatus | null;
  downloadPct: number;
  onUpdateNow: () => void;
};

function statusLine(update: UpdateStatus | null, downloadPct: number): string {
  if (!update) return "Checking…";
  if (update.state === "downloading") return `Downloading  ${downloadPct}%`;
  if (update.state === "applying" || update.message.includes("Installer starting")) {
    return update.message || "Installer starting. This window will close.";
  }
  if (update.justUpdated || update.state === "updated") return update.message || `Updated to ${update.installed}.`;
  if (update.state === "offline") return "No internet — could not check for updates.";
  if (update.state === "failed") return update.message || "Could not check for updates.";
  if (update.updateAvailable) return update.notes || "A newer version is ready to install.";
  return "This PC has the latest version.";
}

async function pickFolder(current: string): Promise<string | null> {
  try {
    const path = await invoke<string | null>("pick_report_folder");
    return path || null;
  } catch {
    const typed = window.prompt("Folder for reports and results", current || "");
    return typed ? typed.trim() : null;
  }
}

export function SettingsScreen({
  reportDir,
  onReportDir,
  colorTheme,
  onColorTheme,
  update,
  downloadPct,
  onUpdateNow,
}: Props) {
  const busy = update?.state === "downloading" || update?.state === "applying";
  const canUpdate = !!update?.updateAvailable && !busy;

  return (
    <div className="page" style={{ maxWidth: 820 }}>
      <div className="kicker" style={{ marginBottom: 10 }}>
        Settings
      </div>
      <h1 className="page-title" style={{ margin: "0 0 26px" }}>
        Preferences
      </h1>

      <div className="kicker-muted" style={{ margin: "0 0 12px 2px" }}>
        Reports
      </div>
      <div className="card" style={{ padding: 18, marginBottom: 24 }}>
        <div style={{ fontSize: 15, fontWeight: 500, marginBottom: 4 }}>Save reports and results</div>
        <p className="body" style={{ fontSize: 13, margin: "0 0 14px" }}>
          The app always keeps a copy. Choose a folder if you also want HTML and spreadsheet files saved there by default.
        </p>
        <div className="wizard-folder-path" style={{ marginBottom: 12 }}>
          <span className="wizard-choice-glyph">
            <Icon name="folder-open" size={20} />
          </span>
          <div style={{ minWidth: 0 }}>
            <div className="kicker-muted" style={{ marginBottom: 4 }}>
              Default folder
            </div>
            <div style={{ fontSize: 13.5, wordBreak: "break-all" }}>
              {reportDir || "App library only — no extra folder"}
            </div>
          </div>
        </div>
        <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
          <button
            className="btn secondary"
            type="button"
            onClick={() => {
              void pickFolder(reportDir).then((path) => {
                if (path) onReportDir(path);
              });
            }}
          >
            <Icon name="folder" size={15} />
            Choose folder
          </button>
          {reportDir ? (
            <button className="btn tertiary" type="button" onClick={() => onReportDir("")}>
              Clear
            </button>
          ) : null}
        </div>
      </div>

      <div className="kicker-muted" style={{ margin: "0 0 12px 2px" }}>
        Appearance
      </div>
      <div className="card" style={{ padding: 16, marginBottom: 24 }}>
        <div style={{ fontSize: 14.5, fontWeight: 500, marginBottom: 4 }}>Color theme</div>
        <div style={{ fontSize: 12.5, color: "var(--ink-soft)", marginBottom: 12 }}>
          Layout stays the same. Only the palette changes. Haval is the default.
        </div>
        <div className="theme-picks" role="radiogroup" aria-label="Color theme">
          {COLOR_THEME_CHOICES.map((choice) => (
            <button
              key={choice.id}
              type="button"
              role="radio"
              className={`theme-pick${colorTheme === choice.id ? " on" : ""}`}
              aria-checked={colorTheme === choice.id}
              onClick={() => onColorTheme(choice.id)}
            >
              <span className="theme-swatches" aria-hidden>
                <span style={{ background: choice.swatches[0] }} />
                <span style={{ background: choice.swatches[1] }} />
              </span>
              <span className="theme-pick-copy">
                <strong>{choice.name}</strong>
                <em>{choice.note}</em>
              </span>
            </button>
          ))}
        </div>
      </div>

      <div className="kicker-muted" style={{ margin: "0 0 12px 2px" }}>
        Update
      </div>
      <div className="card update-card" style={{ marginBottom: 24 }}>
        <div className="update-meta">
          <div>
            <div className="update-label">Installed</div>
            <div className="update-value">{update?.installed || "—"}</div>
          </div>
          <div>
            <div className="update-label">Latest</div>
            <div className="update-value">{update?.latest || "—"}</div>
          </div>
        </div>
        <p className="update-notes">{update?.notes || statusLine(update, downloadPct)}</p>
        <p className="update-status" role="status">
          {statusLine(update, downloadPct)}
        </p>
        {update?.state === "downloading" ? (
          <div className="update-bar" aria-valuemin={0} aria-valuemax={100} aria-valuenow={downloadPct}>
            <span style={{ width: `${downloadPct}%` }} />
          </div>
        ) : null}
        <button className="btn" disabled={!canUpdate} onClick={onUpdateNow}>
          Update
        </button>
      </div>
    </div>
  );
}
