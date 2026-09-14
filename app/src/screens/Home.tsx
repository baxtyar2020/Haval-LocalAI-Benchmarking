import { Icon } from "../components/Icon";
import { LlmSizeGauge } from "../components/LlmSizeGauge";
import type { RepairState } from "../types";

type Spec = { icon: string; label: string; value: string };

type Props = {
  overall: RepairState;
  subtitle: string;
  specs: Spec[];
  installedCount: number;
  selectedCount: number;
  canStart: boolean;
  startHint: string;
  onStart: () => void;
  onDoctor: () => void;
  onModels: () => void;
};

type StageKind = "done" | "current" | "pending";

function journeyStages(overall: RepairState, installedCount: number): StageKind[] {
  const hardware: StageKind = overall === "ready" ? "done" : "current";
  const models: StageKind =
    overall !== "ready" ? "pending" : installedCount > 0 ? "done" : "current";
  const later = (prev: StageKind): StageKind => {
    if (prev === "pending" || prev === "current") return "pending";
    return "current";
  };
  const roles = later(models);
  const run = later(roles);
  const report = later(run);
  return [hardware, models, roles, run, report];
}

const STAGES = [
  { label: "Hardware", icon: "cpu", doneIcon: "check" },
  { label: "Pick models", icon: "boxes", doneIcon: "check" },
  { label: "Choose roles", icon: "users", doneIcon: "check" },
  { label: "Run benchmark", icon: "activity", doneIcon: "check" },
  { label: "Get report", icon: "scroll-text", doneIcon: "check" },
] as const;

export function HomeScreen({
  overall,
  subtitle,
  specs,
  installedCount,
  selectedCount,
  canStart,
  startHint,
  onStart,
  onDoctor,
  onModels: _onModels,
}: Props) {
  const kinds = journeyStages(overall, installedCount);
  void selectedCount;
  void subtitle;

  return (
    <div className="page home-page">
      <div className="home-hero-row">
        <div className="home-hero">
          <div className="kicker">Welcome back</div>
          <h1 className="display home-headline">
            Know what your PC <span>can really run.</span>
          </h1>
          <p className="home-lead">
            See how this hardware holds up across different LLM sizes — in{" "}
            <em>real customer roles</em>, use cases, and day-to-day work.{" "}
            <strong>Not which model is best.</strong> How your machine feels at each size.
          </p>
          <p className="home-guide">
            Click <span>Guide me through</span> to start.
          </p>
          <button
            className="btn primary home-guide-btn"
            onClick={onStart}
            disabled={!canStart}
            title={canStart ? "Guide me through" : startHint}
          >
            <Icon name="sparkles" size={20} />
            Guide me through
            <Icon name="arrow-right" size={20} />
          </button>
        </div>
        <LlmSizeGauge />
      </div>

      <section className="home-journey" aria-label="Your run, step by step">
        <div className="kicker home-journey-kicker">Your run, step by step</div>
        <svg
          className="home-journey-line"
          viewBox="0 0 1080 60"
          preserveAspectRatio="none"
          aria-hidden
        >
          <path
            d="M20 42 C 60 34, 80 30, 108 30 C 216 6, 216 6, 324 30 C 432 54, 432 54, 540 30 C 648 6, 648 6, 756 30 C 864 54, 864 54, 972 30 C 1000 30, 1020 34, 1060 42"
            fill="none"
            stroke="var(--accent-400)"
            strokeWidth="3.5"
            strokeLinecap="round"
            strokeDasharray="9 9"
          />
        </svg>
        <div className="home-journey-steps">
          {STAGES.map((stage, i) => {
            const kind = kinds[i];
            return (
              <div key={stage.label} className={`home-journey-step ${kind}`}>
                <div className="home-journey-tile">
                  <Icon name={kind === "done" ? stage.doneIcon : stage.icon} size={28} />
                  {kind === "current" ? <span className="home-journey-now">now</span> : null}
                </div>
                <div className="home-journey-label">{stage.label}</div>
              </div>
            );
          })}
        </div>
      </section>

      <div className="home-spec-strip">
        {specs.map((s) => (
          <span key={s.label} className="home-spec-tag">
            <Icon name={s.icon} size={15} />
            {s.label === "Ollama" ? `Ollama · ${s.value}` : s.value}
          </span>
        ))}
        <button className="btn tertiary home-spec-doctor" type="button" onClick={onDoctor}>
          Open Doctor <Icon name="arrow-right" size={15} />
        </button>
      </div>
    </div>
  );
}
