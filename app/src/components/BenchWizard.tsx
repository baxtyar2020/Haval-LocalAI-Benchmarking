import { useMemo, useState } from "react";
import { invoke } from "@tauri-apps/api/core";
import { Icon } from "./Icon";
import { WizardArtModel, WizardArtPeople, WizardArtReport, WizardArtThink, WIZARD_STEPS } from "./WizardArt";
import { BUSINESSES, PERSONA_CHOICES, PERSONA_ICONS, type BusinessId } from "../personaCatalog";
import type { LibraryItem } from "../types";

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
  onCancel: () => void;
  onLaunch: (opts: WizardLaunch) => void;
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

export function BenchWizard({ models, defaultModel, defaultThinking, onCancel, onLaunch }: Props) {
  const installed = models.filter((m) => m.installed);
  const [step, setStep] = useState(0);
  const [model, setModel] = useState(defaultModel || installed[0]?.name || "");
  const [picked, setPicked] = useState<Set<string>>(() => new Set(PERSONA_CHOICES.map((p) => p.name)));
  const [thinking, setThinking] = useState(defaultThinking);
  const [folder, setFolder] = useState<string | null>(null);

  const byBiz = useMemo(() => {
    const map: Record<BusinessId, typeof PERSONA_CHOICES> = { Consumer: [], Gaming: [], Commercial: [] };
    for (const p of PERSONA_CHOICES) map[p.business].push(p);
    return map;
  }, []);

  const canNext = step === 0 ? Boolean(model) : step === 1 ? picked.size > 0 : true;

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

  const Art = [WizardArtModel, WizardArtPeople, WizardArtThink, WizardArtReport][step];

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
              onClick={() => setStep(i)}
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
        </div>

        <div className="wizard-panel">
          {step === 0 ? (
            installed.length ? (
              <div className="wizard-list">
                {installed.map((m) => {
                  const on = model === m.name;
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
            ) : (
              <p className="body">Install a model in the Model Library first, then come back here.</p>
            )
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
                  <strong>Thinking off</strong>
                  <em>Straight to the answer. Faster. A good default for this bench.</em>
                </span>
                <span className={`checkbox${thinking === false ? " on" : ""}`}>{thinking === false ? <Icon name="check" size={14} /> : null}</span>
              </button>
              <button type="button" className={`wizard-choice${thinking ? " on" : ""}`} onClick={() => setThinking(true)}>
                <span className="wizard-choice-glyph">
                  <Icon name="lightbulb" size={22} />
                </span>
                <span>
                  <strong>Thinking on</strong>
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
        <button type="button" className="btn tertiary" onClick={onCancel}>
          <Icon name="arrow-left" size={16} />
          Back to Benchmark
        </button>
        <div style={{ display: "flex", gap: 10 }}>
          {step > 0 ? (
            <button type="button" className="btn secondary" onClick={() => setStep((s) => s - 1)}>
              Previous
            </button>
          ) : null}
          {step < 3 ? (
            <button type="button" className="btn primary" disabled={!canNext} onClick={() => setStep((s) => s + 1)}>
              Next
              <Icon name="arrow-right" size={16} />
            </button>
          ) : (
            <button
              type="button"
              className="btn primary"
              disabled={!model || picked.size < 1}
              onClick={() =>
                onLaunch({
                  model,
                  personas: PERSONA_CHOICES.map((p) => p.name).filter((n) => picked.has(n)),
                  thinking,
                  report_dir: folder,
                })
              }
            >
              <Icon name="play" size={16} />
              Start benchmark
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
