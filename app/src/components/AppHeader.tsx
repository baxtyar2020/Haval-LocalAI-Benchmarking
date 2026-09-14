import { Icon } from "./Icon";
import { TABS } from "../demoData";
import type { RepairState, TabId } from "../types";

type Props = {
  tab: TabId;
  repair: RepairState;
  onTab: (id: TabId) => void;
  onHelp: () => void;
  lockedTabs?: TabId[];
};

export function AppHeader({ tab, repair, onTab, onHelp, lockedTabs = [] }: Props) {
  const healthClass =
    repair === "ready"
      ? "ready"
      : repair === "repairing"
        ? "repairing"
        : repair === "checking"
          ? "checking"
          : "attention";
  const healthLabel =
    repair === "ready"
      ? "Ready"
      : repair === "repairing"
        ? "Repairing"
        : repair === "checking"
          ? "Checking"
          : "Needs attention";

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
        {TABS.map((t) => {
          const locked = lockedTabs.includes(t.id);
          return (
            <button
              key={t.id}
              className={`nav-pill${tab === t.id ? " active" : ""}${locked ? " locked" : ""}`}
              onClick={() => onTab(t.id)}
              disabled={locked}
              aria-disabled={locked}
              aria-current={tab === t.id ? "page" : undefined}
              title={locked ? "Update this app in Settings before using this page." : undefined}
            >
              <Icon name={t.icon} size={16} />
              {t.label}
            </button>
          );
        })}
      </nav>
      <div className="header-right">
        <div className={`health-pill ${healthClass}`} role="status" aria-live="polite" title="Machine readiness">
          <span className="health-dot" />
          {healthLabel}
        </div>
        <button className="icon-btn" aria-label="Help" onClick={onHelp}>
          <Icon name="life-buoy" size={17} />
        </button>
      </div>
    </header>
  );
}
