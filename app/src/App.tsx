import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { AppHeader } from "./components/AppHeader";
import { BenchWizard, type WizardLaunch } from "./components/BenchWizard";
import { SplashScreen } from "./components/SplashScreen";
import { TABS } from "./demoData";
import { HomeScreen } from "./screens/Home";
import { DoctorScreen } from "./screens/Doctor";
import { ModelsScreen } from "./screens/Models";
import { BenchmarkScreen } from "./screens/Benchmark";
import { ReportsScreen } from "./screens/Reports";
import { SettingsScreen } from "./screens/Settings";
import { engineGet, enginePost, waitForEngine, restartEngine, loadEngineInfo, openOnOs, type HealthResponse, type PreferredResponse } from "./engine";
import type { BenchSnapshot, DoctorSnapshot, EngineInfo, EngineRun, LibraryItem, LibraryResponse, ModelFilter, RepairState, TabId } from "./types";

function overallFrom(snap: DoctorSnapshot | null): RepairState {
  if (!snap) return "checking";
  if (snap.state === "repairing") return "repairing";
  const working = (snap.checks || []).some((c) => c.status === "checking" || c.status === "repairing");
  if (snap.state === "running" && (working || !(snap.checks || []).length)) return "checking";
  return snap.overall === "ready" ? "ready" : "attention";
}

function doctorStillWorking(snap: DoctorSnapshot | null): boolean {
  if (!snap) return true;
  if (snap.state === "running" || snap.state === "repairing") return true;
  return (snap.checks || []).some((c) => c.status === "checking" || c.status === "repairing");
}

function blockingFails(snap: DoctorSnapshot | null): boolean {
  return (snap?.checks || []).some((c) => c.blocking && (c.status === "failed" || c.status === "blocked"));
}

export default function App() {
  const [tab, setTab] = useState<TabId>("home");
  const [showTech, setShowTech] = useState(false);
  const [filter, setFilter] = useState<ModelFilter>("Installed");
  const [query, setQuery] = useState("");
  const [library, setLibrary] = useState<LibraryResponse | null>(null);
  const [benchSnap, setBenchSnap] = useState<BenchSnapshot | null>(null);
  const [runs, setRuns] = useState<EngineRun[]>([]);
  const [showLog, setShowLog] = useState(false);
  const [reportId, setReportId] = useState<string | null>(null);
  const [help, setHelp] = useState(false);
  const [settings, setSettings] = useState({
    updates: true,
    telemetry: false,
    hideCmd: true,
    autoSelect: true,
    keepModels: true,
  });
  const [engine, setEngine] = useState<EngineInfo>({ url: "", token: "", ready: false });
  const [engineHealthy, setEngineHealthy] = useState(false);
  const [catalogCount, setCatalogCount] = useState(5);
  const [thinking, setThinking] = useState(false);
  const [wizard, setWizard] = useState(false);
  const [wizardModels, setWizardModels] = useState<LibraryItem[]>([]);
  const [doctor, setDoctor] = useState<DoctorSnapshot | null>(null);
  const [splash, setSplash] = useState(true);
  const [bootDoctorDone, setBootDoctorDone] = useState(false);
  const [splashRepairHint, setSplashRepairHint] = useState(false);
  const [minSplashElapsed, setMinSplashElapsed] = useState(false);
  const autoOpenedReport = useRef<string | null>(null);
  const benchWasActive = useRef(false);
  const splashRef = useRef(true);
  const bootSawWork = useRef(false);
  splashRef.current = splash;

  useEffect(() => {
    const t = window.setTimeout(() => setMinSplashElapsed(true), 5000);
    return () => window.clearTimeout(t);
  }, []);

  useEffect(() => {
    let cancelled = false;
    let fallback: number | undefined;
    (async () => {
      const info = await waitForEngine();
      if (cancelled) return;
      setEngine(info);
      const stillStarting =
        !info.ready &&
        /starting|not answering/i.test(info.error || "") &&
        !info.url;
      if (info.error && !info.ready && !stillStarting && !info.url) {
        bootSawWork.current = true;
        setDoctor({
          state: "idle",
          overall: "attention",
          subtitle: info.error,
          checks: [{ id: "engine", title: "Bench Engine", detail: info.error, status: "failed", blocking: true }],
          hardware: {},
          tech_log: "",
          models: [],
          probe: {},
          gate: { ready: false, environment_ready: false, reasons: [info.error] },
        } as DoctorSnapshot);
        setBootDoctorDone(true);
        return;
      }
      if (!info.url) {
        setBootDoctorDone(true);
        return;
      }
      void enginePost<DoctorSnapshot>(info, "/doctor/run").then((snap) => {
        if (!cancelled && snap) setDoctor(snap);
      });
      void engineGet<DoctorSnapshot>(info, "/doctor/status").then((snap) => {
        if (!cancelled && snap) setDoctor(snap);
      });
      const health = await engineGet<HealthResponse>(info, "/health");
      if (!cancelled) setEngineHealthy(!!health?.ok || info.ready);
      const catalog = await engineGet<PreferredResponse>(info, "/models/preferred");
      if (!cancelled && catalog?.models?.length) setCatalogCount(catalog.models.length);
      const prefs = await engineGet<{ thinking?: boolean }>(info, "/bench/prefs");
      if (!cancelled && prefs && typeof prefs.thinking === "boolean") setThinking(prefs.thinking);
      const lib = await engineGet<LibraryResponse>(info, "/models/library?filter=Installed");
      if (!cancelled && lib) setLibrary(lib);
    })();
    fallback = window.setTimeout(() => {
      if (!cancelled) setBootDoctorDone(true);
    }, 180000);
    return () => {
      cancelled = true;
      if (fallback) window.clearTimeout(fallback);
    };
  }, []);

  const openHtml = useCallback(async (id: string) => {
    const rendered = await enginePost<{ html_path?: string }>(engine, `/reports/${id}/render`);
    const path =
      rendered?.html_path ||
      (await engineGet<{ html_path?: string }>(engine, `/reports/${id}/paths`))?.html_path;
    if (!path) {
      window.alert("The report file could not be created.");
      return;
    }
    try {
      await openOnOs(path);
      return;
    } catch {
      const launched = await enginePost<{ ok?: boolean }>(engine, `/reports/${id}/open`);
      if (launched?.ok) return;
      window.alert(`Could not open the report in your browser. It is saved at:\n${path}`);
    }
  }, [engine]);

  useEffect(() => {
    if (engine.url) return;
    let cancelled = false;
    const tick = window.setInterval(async () => {
      const info = await loadEngineInfo();
      if (cancelled) return;
      if (info.url) {
        setEngine(info);
        void enginePost<DoctorSnapshot>(info, "/doctor/run").then((snap) => {
          if (!cancelled && snap) setDoctor(snap);
        });
      }
    }, 800);
    return () => {
      cancelled = true;
      window.clearInterval(tick);
    };
  }, [engine.url]);

  useEffect(() => {
    if (!engine.url) return;
    let cancelled = false;
    if (filter === "Search Ollama") {
      setLibrary((prev) => (prev ? { ...prev, items: [] } : prev));
    }
    const libPath =
      `/models/library?filter=${encodeURIComponent(filter)}` +
      (query ? `&q=${encodeURIComponent(query)}` : "");
    const pullLibrary = async () => {
      const lib = await engineGet<LibraryResponse>(engine, libPath);
      if (!cancelled && lib) setLibrary(lib);
    };
    void pullLibrary();
    const tick = window.setInterval(async () => {
      const snap = await engineGet<DoctorSnapshot>(engine, "/doctor/status");
      if (cancelled) return;
      if (snap) setDoctor(snap);
      const b = await engineGet<BenchSnapshot>(engine, "/bench/status");
      if (cancelled) return;
      if (b) {
        setBenchSnap(b);
        if (b.state === "idle" && typeof b.thinking === "boolean") setThinking(b.thinking);
        if (b.state === "running" || b.state === "paused") {
          benchWasActive.current = true;
        } else if (benchWasActive.current && b.open_report && b.open_report !== autoOpenedReport.current) {
          benchWasActive.current = false;
          autoOpenedReport.current = b.open_report;
          void openHtml(b.open_report);
        } else if (b.state === "idle") {
          benchWasActive.current = false;
        }
      }
      const listed = await engineGet<{ runs: EngineRun[] }>(engine, "/bench/runs");
      if (cancelled) return;
      if (listed?.runs) setRuns(listed.runs);
      await pullLibrary();
    }, 1000);
    return () => {
      cancelled = true;
      window.clearInterval(tick);
    };
  }, [engine, filter, query, openHtml]);

  const overall = overallFrom(doctor);

  useEffect(() => {
    if (doctor?.state === "running" || doctor?.state === "repairing") bootSawWork.current = true;
    if ((doctor?.checks || []).some((c) => c.status === "checking" || c.status === "repairing")) {
      bootSawWork.current = true;
    }
    if (bootSawWork.current && doctor && !doctorStillWorking(doctor)) {
      setBootDoctorDone(true);
    }
  }, [doctor]);

  useEffect(() => {
    if (!engine.url || bootDoctorDone) return;
    const t = window.setTimeout(() => setBootDoctorDone(true), 20000);
    return () => window.clearTimeout(t);
  }, [engine.url, bootDoctorDone]);

  useEffect(() => {
    if (!splash) return;
    if (!minSplashElapsed) return;
    if (!bootDoctorDone) return;
    if (doctor && doctorStillWorking(doctor)) return;
    if (!doctor) {
      setSplash(false);
      setSplashRepairHint(true);
      setTab("doctor");
      setHelp(false);
      setWizard(false);
      return;
    }
    const failed = blockingFails(doctor) || overallFrom(doctor) === "attention";
    setSplash(false);
    if (failed) {
      setSplashRepairHint(true);
      setTab("doctor");
      setHelp(false);
      setWizard(false);
    }
  }, [splash, minSplashElapsed, bootDoctorDone, doctor]);

  const selectedCount = library?.selected?.length ?? 0;
  const downloading = (library?.items ?? []).some((m) =>
    ["queued", "downloading", "verifying"].includes(m.download?.state || ""),
  );
  const installedCount = library?.installed_count ?? doctor?.models?.length ?? 0;
  const envReady = !!doctor?.gate?.environment_ready;
  const canStart = envReady && installedCount >= 1 && !downloading && benchSnap?.state !== "running" && benchSnap?.state !== "paused";
  const startHint = useMemo(() => {
    if (!envReady) return doctor?.gate?.reasons?.[0] || "Finish Doctor before starting a benchmark.";
    if (downloading) return "Wait for downloads to finish.";
    if (benchSnap?.state === "running" || benchSnap?.state === "paused") return "A benchmark is already in progress.";
    if (installedCount < 1) return "Install at least one model first.";
    return "";
  }, [envReady, doctor, downloading, installedCount, benchSnap]);

  const ramLabel = doctor?.hardware?.unified_memory
    ? "Unified memory"
    : doctor?.hardware?.vram_gb != null
      ? "Dedicated VRAM"
      : "System memory";
  const ramValue =
    doctor?.hardware?.unified_memory || doctor?.hardware?.vram_gb == null
      ? doctor?.hardware?.ram_gb != null
        ? `${doctor.hardware.ram_gb} GB`
        : "Detecting…"
      : `${doctor.hardware.vram_gb} GB`;
  const specs = [
    { icon: "cpu", label: "Processor", value: String(doctor?.hardware?.cpu || "Detecting…") },
    { icon: "square-chevron-up", label: "Graphics", value: String(doctor?.hardware?.gpu || "Detecting…") },
    {
      icon: "memory-stick",
      label: ramLabel,
      value: ramValue,
    },
    {
      icon: "zap",
      label: "Acceleration",
      value: String(doctor?.probe?.classification || (overall === "ready" ? "Verified" : "Not proven yet")),
    },
    {
      icon: "hard-drive",
      label: "Storage free",
      value: doctor?.hardware?.disk_free_gb != null ? `${doctor.hardware.disk_free_gb} GB` : "Detecting…",
    },
    {
      icon: "network",
      label: "Ollama",
      value: doctor?.checks?.find((c) => c.id === "ollama_api")?.status === "passed" ? "API ready" : "Not ready",
    },
  ];

  const go = (id: TabId) => {
    if (splashRef.current) return;
    setTab(id);
    if (id === "models") {
      setFilter("Installed");
      setQuery("");
    }
    if (id !== "reports") setReportId(null);
    setHelp(false);
    setWizard(false);
  };

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        setHelp(false);
        setWizard(false);
      }
      if (!e.altKey || e.ctrlKey || e.metaKey) return;
      const idx = Number(e.code.replace("Digit", "").replace("Numpad", ""));
      if (idx < 1 || idx > TABS.length) return;
      const target = (e.target as HTMLElement | null)?.tagName;
      if (target === "INPUT" || target === "TEXTAREA" || target === "SELECT") return;
      e.preventDefault();
      go(TABS[idx - 1].id);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  const tryStart = () => {
    if (!canStart) {
      go(!envReady ? "doctor" : "models");
      return;
    }
    go("benchmark");
    setWizard(true);
    engineGet<LibraryResponse>(engine, "/models/library?filter=Installed").then((lib) => {
      setWizardModels((lib?.items || []).filter((m) => m.installed));
    });
  };

  const launchWizard = (opts: WizardLaunch) => {
    setWizard(false);
    setThinking(opts.thinking);
    go("benchmark");
    enginePost(engine, "/bench/start", {
      model: opts.model,
      thinking: opts.thinking,
      personas: opts.personas,
      report_dir: opts.report_dir,
    }).then(() => engineGet<BenchSnapshot>(engine, "/bench/status").then((b) => b && setBenchSnap(b)));
  };

  async function exportPdf(id: string) {
    const rendered = await enginePost<{ pdf_path?: string | null; html_path?: string }>(engine, `/reports/${id}/render`);
    const path = rendered?.pdf_path || rendered?.html_path;
    if (!path) return;
    try {
      await openOnOs(path);
    } catch {
      window.alert(rendered?.pdf_path ? `PDF saved at ${path}` : `HTML saved at ${path}. Print it to PDF from the browser.`);
    }
  }

  async function showFolder(id: string) {
    await enginePost(engine, `/reports/${id}/render`);
    const paths = await engineGet<{ folder?: string; html_path?: string }>(engine, `/reports/${id}/paths`);
    const target = paths?.folder || paths?.html_path;
    if (!target) return;
    try {
      await openOnOs(target);
    } catch {
      window.alert(`Run folder: ${paths?.folder || target}`);
    }
  }

  async function deleteReport(id: string) {
    if (!window.confirm("Delete this report and every file stored for it? This cannot be undone.")) return;
    const result = await enginePost<{ ok?: boolean; runs?: EngineRun[] }>(engine, `/reports/${id}/delete`);
    if (!result?.ok) {
      window.alert("Could not delete that report. If a benchmark is still running, stop it first.");
      return;
    }
    setReportId(null);
    if (result.runs) {
      setRuns(result.runs);
      return;
    }
    const listed = await engineGet<{ runs: EngineRun[] }>(engine, "/bench/runs");
    if (listed?.runs) setRuns(listed.runs);
  }

  return (
    <div className="shell">
      {splash ? <SplashScreen snapshot={doctor} waitingForEngine={!engine.url && !bootDoctorDone} /> : null}
      <a className="skip-link" href="#main">
        Skip to main content
      </a>
      <div className="sr-only" aria-live="polite" aria-atomic="true">
        {splash
          ? "Doctor is checking this PC."
          : benchSnap?.state === "running"
          ? `Benchmark running. ${benchSnap.message || ""} ${Math.round(benchSnap.pct || 0)} percent.`
          : benchSnap?.state === "paused"
            ? `Benchmark paused. ${benchSnap.message || ""}`
            : ""}
      </div>
      {!splash ? <AppHeader tab={tab} repair={overall} onTab={go} onHelp={() => setHelp((h) => !h)} /> : null}
      <main id="main" className="content" tabIndex={-1}>
        {wizard ? (
          <BenchWizard
            models={wizardModels.length ? wizardModels : (library?.items || []).filter((m) => m.installed)}
            defaultModel={library?.selected?.[0]}
            defaultThinking={thinking}
            onCancel={() => setWizard(false)}
            onLaunch={launchWizard}
          />
        ) : (
          <>
        {tab === "home" && (
          <HomeScreen
            overall={overall}
            subtitle={doctor?.subtitle || "Doctor is inspecting this PC."}
            specs={specs}
            installedCount={installedCount}
            selectedCount={selectedCount}
            canStart={canStart}
            startHint={startHint}
            onStart={tryStart}
            onDoctor={() => go("doctor")}
            onModels={() => go("models")}
          />
        )}
        {tab === "doctor" && (
          <DoctorScreen
            snapshot={doctor}
            showTech={showTech}
            onRun={() => {
              void (async () => {
                let info = engine;
                if (!info.url) {
                  try {
                    info = await restartEngine();
                    setEngine(info);
                  } catch {
                    info = await waitForEngine();
                    setEngine(info);
                  }
                }
                const s = await enginePost<DoctorSnapshot>(info, "/doctor/run");
                if (s) setDoctor(s);
              })();
            }}
            onRepair={() => {
              void (async () => {
                let info = engine;
                if (!info.url || !info.ready) {
                  try {
                    info = await restartEngine();
                    setEngine(info);
                  } catch {
                    info = await waitForEngine();
                    setEngine(info);
                  }
                }
                const s = await enginePost<DoctorSnapshot>(info, "/doctor/repair");
                if (s) setDoctor(s);
              })();
            }}
            sequenceHelp={splashRepairHint || overall === "attention"}
            onToggleTech={() => setShowTech((s) => !s)}
          />
        )}
        {tab === "models" && (
          <ModelsScreen
            filter={filter}
            query={query}
            library={library}
            onFilter={setFilter}
            onQuery={setQuery}
            onToggle={(name, selected) =>
              enginePost(engine, "/models/select", { name, selected }).then(() =>
                engineGet<LibraryResponse>(engine, `/models/library?filter=${encodeURIComponent(filter)}&q=${encodeURIComponent(query)}`).then(
                  (lib) => lib && setLibrary(lib),
                ),
              )
            }
            onDownload={(name) => enginePost(engine, "/models/downloads", { name })}
            onCancel={(jobId) => enginePost(engine, `/models/downloads/${jobId}/cancel`)}
            onRetry={(jobId) => enginePost(engine, `/models/downloads/${jobId}/retry`)}
            onRemove={(name) =>
              enginePost(engine, "/models/remove", { name }).then(() =>
                engineGet<LibraryResponse>(engine, `/models/library?filter=${encodeURIComponent(filter)}`).then((lib) => lib && setLibrary(lib)),
              )
            }
          />
        )}
        {tab === "benchmark" && (
          <BenchmarkScreen
            snapshot={benchSnap}
            showLog={showLog}
            canStart={canStart}
            startHint={startHint}
            onStart={tryStart}
            onPause={() => enginePost(engine, "/bench/pause").then((b) => b && setBenchSnap(b as BenchSnapshot))}
            onStop={() => enginePost(engine, "/bench/stop").then((b) => b && setBenchSnap(b as BenchSnapshot))}
            onToggleLog={() => setShowLog((s) => !s)}
          />
        )}
        {tab === "reports" && (
          <ReportsScreen
            detailId={reportId}
            runs={runs}
            onOpen={(id) => {
              setReportId(id);
              void openHtml(id);
            }}
            onBack={() => setReportId(null)}
            onOpenHtml={(id) => void openHtml(id)}
            onPdf={(id) => void exportPdf(id)}
            onFolder={(id) => void showFolder(id)}
            onDelete={(id) => void deleteReport(id)}
          />
        )}
        {tab === "settings" && (
          <SettingsScreen
            settings={settings}
            engine={engine}
            engineHealthy={engineHealthy}
            catalogCount={catalogCount}
            onToggle={(key) => setSettings((s) => ({ ...s, [key]: !s[key] }))}
          />
        )}
          </>
        )}
      </main>
      {help ? (
        <div className="card help-panel" role="dialog" aria-modal="true" aria-labelledby="help-title">
          <div id="help-title" className="kicker" style={{ marginBottom: 8 }}>
            Help
          </div>
          <p className="body" style={{ fontSize: 13, margin: 0 }}>
            Doctor prepares this PC and proves acceleration is real. Start Benchmark opens a setup screen in this window: model, roles, thinking, and where to save the report. Alt+1 through Alt+6 switch tabs. Escape closes this panel.
          </p>
          <button className="btn secondary" style={{ marginTop: 14 }} onClick={() => setHelp(false)}>
            Close
          </button>
        </div>
      ) : null}
    </div>
  );
}
