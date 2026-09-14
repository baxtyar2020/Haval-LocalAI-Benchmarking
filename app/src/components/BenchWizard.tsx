import { useMemo, useState } from "react";
import { invoke } from "@tauri-apps/api/core";
import { Icon } from "./Icon";
import { WizardArtModel, WizardArtPeople, WizardArtReport, WizardArtThink, WIZARD_STEPS } from "./WizardArt";
import { BUSINESSES, PERSONA_CHOICES, PERSONA_ICONS, type BusinessId } from "../personaCatalog";
import type { LibraryItem } from "../types";
import screen1 from "../assets/wizard/screen1.png";
import screen2 from "../assets/wizard/screen2.png";
import screen3 from "../assets/wizard/screen3.png";
import screen4 from "../assets/wizard/screen4.png";
import screen5 from "../assets/wizard/screen5.png";

export type WizardLaunch = {
  model: string;
  personas: string[];
  thinking: boolean;
  report_dir: string | null;
};

type Props = {
  models: LibraryItem[];
  defaultModel?: string;
  defaultThinking: boolean;
  defaultReportDir?: string | null;
  onCancel: () => void;
  onLaunch: (opts: WizardLaunch) => void;
  onGoToModels: () => void;
  onSearchModels: () => void;
  /** Skip illustrated intro and show a setup step (used for in-app screenshots). */
  previewWork?: boolean;
  previewStep?: number;
};

const TITLES = [
  "Which model should we test?",
  "Who is this test for?",
  "Should the model think first?",
  "Where should we save the report?",
];

const BLURBS = [
  "One model per report. Choose an installed model on this PC — the drawing is a PC with a model cube on the screen.",
  "Pick whole groups or single roles. The three cards are home, play, and work. We only run what you select.",
  "This stays for the whole run. The left path answers right away. The right path thinks first, then answers.",
  "We always keep a copy in the app. Optionally save another copy in a folder you choose.",
];

const STEP_ART = [screen1, screen2, screen3, screen4];

type BriefLine = { icon: string; text: string; tone?: "ink" | "accent" | "ok" | "warn" };

type BriefCopy = {
  kicker: string;
  title: string;
  mark: string;
  lines: BriefLine[];
};

const BRIEF_COPY: BriefCopy[] = [
  {
    kicker: "Step 1 · Your model",
    title: "Choose the model to test",
    mark: "sparkles",
    lines: [
      { icon: "download", tone: "accent", text: "Pick any LLM you already downloaded." },
      { icon: "box", text: "You can select any model on your list. Use the one you want to run the benchmark." },
    ],
  },
  {
    kicker: "Step 2 · Who it is for",
    title: "Choose your personas",
    mark: "users",
    lines: [
      { icon: "user-round", text: "A persona is a real customer role and use case. It is how that person uses AI in daily work or life." },
      { icon: "sparkles", tone: "accent", text: "All 20 personas start selected. That is the default." },
      { icon: "list-checks", text: "You can clear a whole segment, then keep only the ones you want." },
      { icon: "users", text: "You can also mix personas from different segments. That is up to you." },
      { icon: "check", text: "Tap a role to select or unselect it." },
      { icon: "arrow-right", tone: "ok", text: "On the next screen, scroll down to see every role." },
    ],
  },
  {
    kicker: "Step 3 · Speed vs thinking",
    title: "Thinking on or off?",
    mark: "brain",
    lines: [
      { icon: "gauge", text: "Most industry benchmarks leave thinking off." },
      { icon: "zap", tone: "accent", text: "Here, thinking is off by default as well." },
      { icon: "timer", tone: "warn", text: "When thinking is on, the model can take 3 times longer — sometimes more." },
      { icon: "shield-alert", text: "Do not turn it on unless you have a very specific reason." },
    ],
  },
  {
    kicker: "Step 4 · Your report",
    title: "Save the final report (optional)",
    mark: "folder-open",
    lines: [
      { icon: "scroll-text", text: "The app already saves the report in the default place." },
      { icon: "folder", text: "If you want a second copy, pick another folder on the next screen." },
      { icon: "play", tone: "ok", text: "If you do not need that, leave it blank and tap Start. Then just click Start benchmark." },
    ],
  },
];

const EMPTY_COPY: BriefCopy = {
  kicker: "Need a model first",
  title: "No model to test yet",
  mark: "boxes",
  lines: [
    { icon: "alert-triangle", tone: "warn", text: "The benchmark needs at least one installed model." },
    { icon: "boxes", text: "Go back to Models and download one from the preferred list." },
    { icon: "search", text: "You can also search for a model yourself, then download it." },
    { icon: "sparkles", tone: "ok", text: "When a model is on your list, come back here and start the guide again." },
  ],
};

export function BenchWizard({
  models,
  defaultModel,
  defaultThinking: _defaultThinking,
  defaultReportDir,
  onCancel,
  onLaunch,
  onGoToModels,
  onSearchModels,
  previewWork = false,
  previewStep = 0,
}: Props) {
  const installed = models.filter((m) => m.installed);
  const empty = installed.length === 0;
  const [brief, setBrief] = useState(!previewWork);
  const [step, setStep] = useState(previewStep);
  const [model, setModel] = useState(defaultModel || installed[0]?.name || "");
  const [picked, setPicked] = useState<Set<string>>(() => new Set(PERSONA_CHOICES.map((p) => p.name)));
  const [thinking, setThinking] = useState(false);
  const [folder, setFolder] = useState<string | null>(defaultReportDir || null);

  const byBiz = useMemo(() => {
    const map: Record<BusinessId, typeof PERSONA_CHOICES> = { Consumer: [], Gaming: [], Commercial: [] };
    for (const p of PERSONA_CHOICES) map[p.business].push(p);
    return map;
  }, []);

  const selectedModel = installed.some((m) => m.name === model) ? model : installed[0]?.name || "";
  const canNext = step === 0 ? Boolean(selectedModel) : step === 1 ? picked.size > 0 : true;
  const allCount = PERSONA_CHOICES.length;
  const allPicked = picked.size === allCount;
  const nonePicked = picked.size === 0;

  function selectAllPersonas() {
    setPicked(new Set(PERSONA_CHOICES.map((p) => p.name)));
  }

  function deselectAllPersonas() {
    setPicked(new Set());
  }

  function togglePersona(name: string) {
    setPicked((prev) => {
      const next = new Set(prev);
      if (next.has(name)) next.delete(name);
      else next.add(name);
      return next;
    });
  }

  function setBiz(id: BusinessId, on: boolean) {
    const names = byBiz[id].map((p) => p.name);
    setPicked((prev) => {
      const next = new Set(prev);
      for (const n of names) {
        if (on) next.add(n);
        else next.delete(n);
      }
      return next;
    });
  }

  async function chooseFolder() {
    try {
      const path = await invoke<string | null>("pick_report_folder");
      if (path) setFolder(path);
    } catch {
      const typed = window.prompt("Folder path for the report", folder || "");
      if (typed) setFolder(typed);
    }
  }

  function backFromWork() {
    setBrief(true);
  }

  function nextFromWork() {
    if (step < 3) {
      setStep((s) => s + 1);
      setBrief(true);
      return;
    }
    if (!selectedModel || picked.size < 1) return;
    onLaunch({
      model: selectedModel,
      personas: PERSONA_CHOICES.map((p) => p.name).filter((n) => picked.has(n)),
      thinking,
      report_dir: folder,
    });
  }

  function backFromBrief() {
    if (step === 0) {
      onCancel();
      return;
    }
    setStep((s) => s - 1);
    setBrief(false);
  }

  const Art = [WizardArtModel, WizardArtPeople, WizardArtThink, WizardArtReport][step];

  if (empty || brief) {
    const copy = empty ? EMPTY_COPY : BRIEF_COPY[step];
    const art = empty ? screen5 : STEP_ART[step];
    return (
      <div
        className={`wizard-brief${empty ? " wizard-brief-empty" : ` wizard-brief-s${step}`}`}
        role="dialog"
        aria-labelledby="wizard-brief-title"
      >
        <img className="wizard-brief-art" src={art} alt="" />
        <div className="wizard-brief-dock">
          <div className="wizard-brief-kicker">{copy.kicker}</div>
          <h1 className="wizard-brief-title" id="wizard-brief-title">
            {copy.title}
          </h1>
          <p className="wizard-brief-copy">
            {copy.lines.map((line, i) => (
              <span key={line.text} className={`tone-${line.tone || "ink"}`} style={{ animationDelay: `${120 + i * 160}ms` }}>
                {line.text}{" "}
              </span>
            ))}
          </p>
          <div className="wizard-brief-actions">
            <button type="button" className="btn tertiary" onClick={empty ? onCancel : backFromBrief}>
              Back
            </button>
            {empty ? (
              <>
                <button type="button" className="btn secondary" onClick={onSearchModels}>
                  <Icon name="search" size={16} />
                  Search for a model
                </button>
                <button type="button" className="btn primary" onClick={onGoToModels}>
                  <Icon name="boxes" size={16} />
                  Go to Models
                </button>
              </>
            ) : (
              <button type="button" className="btn primary" onClick={() => setBrief(false)}>
                OK, let’s go
                <Icon name="arrow-right" size={16} />
              </button>
            )}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="page wizard-page">
      <div className="kicker" style={{ marginBottom: 10 }}>
        Set up this run
      </div>
      <h1 className="page-title" id="wizard-title">
        {TITLES[step]}
      </h1>
      <p className="body wizard-lead">{BLURBS[step]}</p>

      <ol className="wizard-rail" aria-label="Setup steps">
        {WIZARD_STEPS.map((s, i) => (
          <li key={s.key}>
            <button
              type="button"
              className={`wizard-rail-btn${i === step ? " on" : i < step ? " done" : ""}`}
              onClick={() => {
                setStep(i);
                setBrief(false);
              }}
              disabled={i > step + 1 || (i === step + 1 && !canNext)}
            >
              <span className="wizard-rail-icon">
                <Icon name={s.icon} size={22} />
              </span>
              <span className="wizard-rail-copy">
                <strong>
                  {i + 1}. {s.label}
                </strong>
                <em>{s.hint}</em>
              </span>
            </button>
          </li>
        ))}
      </ol>

      <div className="wizard-stage">
        <div className="wizard-art-wrap">
          <Art className="wizard-art" />
          <div className="wizard-art-caption">
            {step === 0 && (
              <>
                <Icon name="cpu" size={16} />
                One model, this PC
              </>
            )}
            {step === 1 && (
              <>
                <Icon name="users" size={16} />
                Home · Play · Work
              </>
            )}
            {step === 2 && (
              <>
                <Icon name="brain" size={16} />
                Fast path or think path
              </>
            )}
            {step === 3 && (
              <>
                <Icon name="folder-open" size={16} />
                Report lands in a folder
              </>
            )}
          </div>
          {step === 1 ? (
            <div className="wizard-persona-bulk">
              <div className="wizard-persona-bulk-count">
                {picked.size} of {allCount} personas
              </div>
              <button type="button" className="btn secondary wizard-persona-bulk-btn" disabled={allPicked} onClick={selectAllPersonas}>
                <Icon name="list-checks" size={15} />
                Select all {allCount}
              </button>
              <button type="button" className="btn secondary wizard-persona-bulk-btn" disabled={nonePicked} onClick={deselectAllPersonas}>
                <Icon name="x" size={15} />
                Deselect all {allCount}
              </button>
            </div>
          ) : null}
          <div className="wizard-nav wizard-nav-art">
            <button type="button" className="btn tertiary" onClick={backFromWork}>
              <Icon name="arrow-left" size={16} />
              Back
            </button>
            {step < 3 ? (
              <button type="button" className="btn primary" disabled={!canNext} onClick={nextFromWork}>
                Next
                <Icon name="arrow-right" size={16} />
              </button>
            ) : (
              <button type="button" className="btn primary" disabled={!selectedModel || picked.size < 1} onClick={nextFromWork}>
                <Icon name="play" size={16} />
                Start benchmark
              </button>
            )}
          </div>
        </div>

        <div className="wizard-panel">
          {step === 0 ? (
            <div className="wizard-list">
              {installed.map((m) => {
                const on = selectedModel === m.name;
                return (
                  <button key={m.name} type="button" className={`wizard-choice${on ? " on" : ""}`} onClick={() => setModel(m.name)}>
                    <span className="wizard-choice-glyph">
                      <Icon name="box" size={22} />
                    </span>
                    <span>
                      <strong>{m.display_name || m.name}</strong>
                      <em>
                        {m.params_total && m.params_total !== "—" ? (
                          <>
                            <strong>{m.params_total}</strong> total · <strong>{m.params_active || m.params_total}</strong> active
                          </>
                        ) : (
                          m.params || m.tag || "Installed"
                        )}
                        {m.quant ? ` · ${m.quant}` : ""}
                        {m.size_label ? ` · ${m.size_label}` : ""}
                      </em>
                    </span>
                    <span className={`checkbox${on ? " on" : ""}`}>{on ? <Icon name="check" size={14} /> : null}</span>
                  </button>
                );
              })}
            </div>
          ) : null}

          {step === 1
            ? BUSINESSES.map((biz) => {
                const rows = byBiz[biz.id];
                const allOn = rows.every((p) => picked.has(p.name));
                return (
                  <div key={biz.id} className="wizard-biz">
                    <div className="wizard-biz-head">
                      <div className="wizard-biz-title">
                        <span className="wizard-biz-glyph">
                          <Icon name={biz.icon} size={22} />
                        </span>
                        <div>
                          <strong>{biz.label}</strong>
                          <em>
                            {biz.note} · {rows.filter((p) => picked.has(p.name)).length}/{rows.length}
                          </em>
                        </div>
                      </div>
                      <button type="button" className="btn tertiary" onClick={() => setBiz(biz.id, !allOn)}>
                        {allOn ? "Clear" : "Select all"}
                      </button>
                    </div>
                    <div className="wizard-personas">
                      {rows.map((p) => {
                        const on = picked.has(p.name);
                        return (
                          <button key={p.name} type="button" className={`wizard-choice compact${on ? " on" : ""}`} onClick={() => togglePersona(p.name)}>
                            <span className="wizard-choice-glyph sm">
                              <Icon name={PERSONA_ICONS[p.name] || "user-round"} size={18} />
                            </span>
                            <span>
                              <strong>{p.name}</strong>
                              <em>{p.blurb}</em>
                            </span>
                          </button>
                        );
                      })}
                    </div>
                  </div>
                );
              })
            : null}

          {step === 2 ? (
            <div className="wizard-think">
              <button type="button" className={`wizard-choice${thinking === false ? " on" : ""}`} onClick={() => setThinking(false)}>
                <span className="wizard-choice-glyph">
                  <Icon name="zap" size={22} />
                </span>
                <span>
                  <strong>Thinking Off</strong>
                  <em>Straight to the answer. Faster. A good default for this bench.</em>
                </span>
                <span className={`checkbox${thinking === false ? " on" : ""}`}>{thinking === false ? <Icon name="check" size={14} /> : null}</span>
              </button>
              <button type="button" className={`wizard-choice${thinking ? " on" : ""}`} onClick={() => setThinking(true)}>
                <span className="wizard-choice-glyph">
                  <Icon name="lightbulb" size={22} />
                </span>
                <span>
                  <strong>Thinking On</strong>
                  <em>It may work the problem out first. Often slower. We still wait until it finishes.</em>
                </span>
                <span className={`checkbox${thinking ? " on" : ""}`}>{thinking ? <Icon name="check" size={14} /> : null}</span>
              </button>
            </div>
          ) : null}

          {step === 3 ? (
            <div className="wizard-folder">
              <div className="wizard-folder-path">
                <span className="wizard-choice-glyph">
                  <Icon name="scroll-text" size={22} />
                </span>
                <div>
                  <div className="kicker-muted" style={{ marginBottom: 4 }}>
                    Always saved in the app
                  </div>
                  <div>Open it later from Reports. No extra folder required.</div>
                </div>
              </div>
              <div className="wizard-folder-path">
                <span className="wizard-choice-glyph">
                  <Icon name="folder-open" size={22} />
                </span>
                <div>
                  <div className="kicker-muted" style={{ marginBottom: 4 }}>
                    Optional extra copy
                  </div>
                  <div>{folder || "Not chosen — we will still keep the in-app copy."}</div>
                </div>
              </div>
              <button type="button" className="btn secondary" onClick={() => void chooseFolder()}>
                <Icon name="folder" size={16} />
                Choose folder
              </button>
            </div>
          ) : null}
        </div>
      </div>

      <div className="wizard-nav">
        <button type="button" className="btn tertiary" onClick={backFromWork}>
          <Icon name="arrow-left" size={16} />
          Back
        </button>
        <div style={{ display: "flex", gap: 10 }}>
          {step > 0 ? (
            <button
              type="button"
              className="btn secondary"
              onClick={() => {
                setStep((s) => s - 1);
                setBrief(false);
              }}
            >
              Previous
            </button>
          ) : null}
          {step < 3 ? (
            <button type="button" className="btn primary" disabled={!canNext} onClick={nextFromWork}>
              Next
              <Icon name="arrow-right" size={16} />
            </button>
          ) : (
            <button type="button" className="btn primary" disabled={!selectedModel || picked.size < 1} onClick={nextFromWork}>
              <Icon name="play" size={16} />
              Start benchmark
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
