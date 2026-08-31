import { Icon } from "./Icon";
import { TABS } from "../demoData";
import type { RepairState, TabId } from "../types";

type Props = {
  tab: TabId;
  repair: RepairState;
  onTab: (id: TabId) => void;
  onHelp: () => void;
};

export function AppHeader({ tab, repair, onTab, onHelp }: Props) {
  const health =
    repair === "ready"
      ? { label: "Ready", bg: "var(--ok-bg)", fg: "var(--ok)", dot: "var(--ok)", halo: "rgba(40,118,83,.18)" }
      : repair === "repairing"
        ? {
            label: "Repairing",
            bg: "var(--accent-soft)",
            fg: "var(--accent-text)",
            dot: "var(--accent)",
            halo: "rgba(219,79,27,.18)",
          }
        : repair === "checking"
          ? {
              label: "Checking",
              bg: "var(--info-bg)",
              fg: "var(--info)",
              dot: "var(--info)",
              halo: "rgba(69,106,135,.18)",
            }
          : {
              label: "Needs attention",
              bg: "var(--warn-bg)",
              fg: "var(--warn)",
              dot: "var(--warn)",
              halo: "rgba(167,96,0,.18)",
            };

  return (
    <header className="header">
      <div className="brand">
        <div className="brand-mark" aria-hidden>
          H
        </div>
        <div>
          <div className="brand-title">Haval LocalAI Benchmarking</div>
          <div className="brand-kicker">Local model evaluation</div>
        </div>
      </div>
      <nav className="nav" aria-label="Primary">
        {TABS.map((t) => (
          <button
            key={t.id}
            className={`nav-pill${tab === t.id ? " active" : ""}`}
            onClick={() => onTab(t.id)}
            aria-current={tab === t.id ? "page" : undefined}
          >
            <Icon name={t.icon} size={16} />
            {t.label}
          </button>
        ))}
      </nav>
      <div className="header-right">
        <div
          className="health-pill"
          role="status"
          aria-live="polite"
          style={{ background: health.bg, color: health.fg }}
          title="Machine readiness"
        >
          <span
            className="health-dot"
            style={{ background: health.dot, boxShadow: `0 0 0 3px ${health.halo}` }}
          />
          {health.label}
        </div>
        <button className="icon-btn" aria-label="Help" onClick={onHelp}>
          <Icon name="life-buoy" size={17} />
        </button>
      </div>
    </header>
  );
}
