import { Icon } from "../components/Icon";
import type { EngineInfo } from "../types";

type SettingsState = {
  updates: boolean;
  telemetry: boolean;
  hideCmd: boolean;
  autoSelect: boolean;
  keepModels: boolean;
};

type Props = {
  settings: SettingsState;
  engine: EngineInfo;
  engineHealthy: boolean;
  catalogCount: number;
  onToggle: (key: keyof SettingsState) => void;
};

export function SettingsScreen({ settings, engine, engineHealthy, catalogCount, onToggle }: Props) {
  const groups: {
    title: string;
    rows: { title: string; sub: string; kind: "toggle" | "value"; key?: keyof SettingsState; value?: string }[];
  }[] = [
    {
      title: "Application",
      rows: [
        { title: "Check for updates automatically", sub: "Notify when a new version is available.", kind: "toggle", key: "updates" },
        { title: "Theme", sub: "Light theme matched to the Haval identity.", kind: "value", value: "Warm Light" },
        {
          title: "Bench Engine",
          sub: engineHealthy
            ? `Connected · ${engine.url || "localhost"}`
            : engine.error || "Not connected — start the desktop app or run the engine locally.",
          kind: "value",
          value: engineHealthy ? "Healthy" : "Offline",
        },
        {
          title: "Keyboard",
          sub: "Alt+1 through Alt+6 switch Home, Doctor, Models, Benchmark, Reports, Settings. Tab moves between controls.",
          kind: "value",
          value: "Alt+1–6",
        },
        { title: "High Contrast", sub: "Windows High Contrast uses system colors. Reduced motion is respected automatically.", kind: "value", value: "System" },
      ],
    },
    {
      title: "Ollama",
      rows: [
        { title: "Run technical steps hidden", sub: "Never flash PowerShell or command windows.", kind: "toggle", key: "hideCmd" },
        { title: "API endpoint", sub: "Local service address for the model runtime.", kind: "value", value: "127.0.0.1:11434" },
      ],
    },
    {
      title: "Models & storage",
      rows: [
        { title: "Auto-select preferred models", sub: "Pre-tick Haval Preferred models that fit this PC.", kind: "toggle", key: "autoSelect" },
        { title: "Keep models after benchmarking", sub: "Do not remove downloaded models automatically.", kind: "toggle", key: "keepModels" },
        {
          title: "Preferred catalog",
          sub: `${catalogCount} Standard Roster models (GPT-OSS 20B is not in the catalog).`,
          kind: "value",
          value: `${catalogCount} models`,
        },
        { title: "Download location", sub: "Where Ollama stores model weights.", kind: "value", value: "D:\\ollama\\models" },
      ],
    },
    {
      title: "Privacy & support",
      rows: [{ title: "Share anonymous diagnostics", sub: "Help improve reliability. No prompts are ever sent.", kind: "toggle", key: "telemetry" }],
    },
  ];

  return (
    <div className="page" style={{ maxWidth: 820 }}>
      <div className="kicker" style={{ marginBottom: 10 }}>
        Settings
      </div>
      <h1 className="page-title" style={{ margin: "0 0 26px" }}>
        Preferences
      </h1>
      {groups.map((g) => (
        <div key={g.title} style={{ marginBottom: 24 }}>
          <div className="kicker-muted" style={{ margin: "0 0 12px 2px" }}>
            {g.title}
          </div>
          <div className="card" style={{ padding: 0, overflow: "hidden" }}>
            {g.rows.map((r) => (
              <div key={r.title} className="setting-row">
                <div style={{ flex: 1 }}>
                  <div style={{ fontSize: 14.5, fontWeight: 600 }}>{r.title}</div>
                  <div style={{ fontSize: 12.5, color: "var(--ink-soft)", marginTop: 2 }}>{r.sub}</div>
                </div>
                {r.kind === "toggle" && r.key ? (
                  <button
                    className={`toggle${settings[r.key] ? " on" : ""}`}
                    onClick={() => onToggle(r.key!)}
                    aria-pressed={settings[r.key]}
                    aria-label={r.title}
                  >
                    <span />
                  </button>
                ) : (
                  <div style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 13.5, fontWeight: 600, padding: "7px 14px", borderRadius: 10, background: "var(--canvas)", border: "1px solid var(--border)" }}>
                    {r.value}
                    <Icon name="chevron-down" size={15} style={{ color: "var(--ink-faint)" }} />
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
