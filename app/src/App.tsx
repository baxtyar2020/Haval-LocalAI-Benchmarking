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
import { CompareScreen, type CompareSource } from "./screens/Compare";
import { SettingsScreen } from "./screens/Settings";
import { engineGet, enginePost, engineSse, waitForEngine, restartEngine, loadEngineInfo, openOnOs } from "./engine";
import { applyUpdate, checkForUpdate, downloadUpdate, getUpdateStatus, onUpdateProgress, type UpdateStatus } from "./update";
import { loadColorTheme, saveColorTheme, type ColorTheme } from "./theme";
import type { BenchSnapshot, DoctorSnapshot, EngineInfo, EngineRun, LibraryItem, LibraryJob, LibraryResponse, ModelFilter, RepairState, TabId } from "./types";

function overallFrom(snap: DoctorSnapshot | null): RepairState {
  if (!snap) return "checking";
  if (snap.state === "repairing") return "repairing";
  const working = (snap.checks || []).some((c) => c.status === "checking" || c.status === "repairing");
  if (snap.state === "running" && (working || !(snap.checks || []).length)) return "checking";
  return snap.overall === "ready" ? "ready" : "attention";
}

function doctorStillWorking(snap: DoctorSnapshot | null): boolean {
  if (!snap) return false;
  if (snap.state === "running" || snap.state === "repairing") return true;
  return (snap.checks || []).some((c) => c.status === "checking" || c.status === "repairing");
}

function blockingFails(snap: DoctorSnapshot | null): boolean {
  return (snap?.checks || []).some((c) => c.blocking && (c.status === "failed" || c.status === "blocked"));
}

function jobToDownload(job: { id: string; name: string; state: string; pct: number; stage?: string; error?: string | null }) {
  return {
    id: job.id,
    name: job.name,
    state: job.state,
    pct: job.pct,
    stage: job.stage || "",
    error: job.error,
  };
}

function mergeLibraryJobs(prev: LibraryResponse | null, jobs: LibraryJob[]): LibraryResponse | null {
  if (!prev) return prev;
  const byName = new Map(jobs.map((j) => [j.name, j]));
  return {
    ...prev,
    jobs,
    items: prev.items.map((item) => {
      const job = byName.get(item.name);
      if (!job) return item;
      return { ...item, download: jobToDownload(job) };
    }),
  };
}

function patchSelected(prev: LibraryResponse | null, sel: string[]): LibraryResponse | null {
  if (!prev) return prev;
  return {
    ...prev,
    selected: sel,
    items: prev.items.map((it) => ({
      ...it,
      selected: sel.includes(it.name) || sel.includes(it.id),
    })),
  };
}

function viewFromCaches(
  filter: ModelFilter,
  installed: LibraryResponse | null,
  preferred: LibraryResponse | null,
  search: LibraryResponse | null,
  query: string,
): LibraryResponse | null {
  const jobs = installed?.jobs || [];
  if (filter === "Preferred") return mergeLibraryJobs(preferred, jobs);
  if (filter === "Search Ollama") {
    const searchView = mergeLibraryJobs(search, jobs);
    if (!query.trim()) {
      return searchView ? { ...searchView, items: [] } : searchView;
    }
    return searchView;
  }
  const installedView = mergeLibraryJobs(installed, jobs) || installed;
  if (filter === "Downloading" && installedView) {
    const open = ["queued", "downloading", "verifying", "paused", "failed"];
    return {
      ...installedView,
      items: installedView.items.filter((item) => open.includes(item.download?.state || "")),
    };
  }
  return installedView;
}

export default function App() {
  const [tab, setTab] = useState<TabId>("home");
  const [showTech, setShowTech] = useState(false);
  const [filter, setFilter] = useState<ModelFilter>("Installed");
  const [query, setQuery] = useState("");
  const [installedLib, setInstalledLib] = useState<LibraryResponse | null>(null);
  const [preferredLib, setPreferredLib] = useState<LibraryResponse | null>(null);
  const [searchLib, setSearchLib] = useState<LibraryResponse | null>(null);
  const [benchSnap, setBenchSnap] = useState<BenchSnapshot | null>(null);
  const [runs, setRuns] = useState<EngineRun[]>([]);
  const [compareSources, setCompareSources] = useState<CompareSource[]>([]);
  const [thisMachine, setThisMachine] = useState("");
  const [compareBusy, setCompareBusy] = useState(false);
  const [compareError, setCompareError] = useState<string | null>(null);
  const [lastCompareId, setLastCompareId] = useState<string | null>(null);
  const [deleteError, setDeleteError] = useState<string | null>(null);
  const [deletingReports, setDeletingReports] = useState(false);
  const [showLog, setShowLog] = useState(false);
  const [reportId, setReportId] = useState<string | null>(null);
  const [help, setHelp] = useState(false);
  const [colorTheme, setColorTheme] = useState<ColorTheme>(loadColorTheme);
  const helpFrameRef = useRef<HTMLIFrameElement>(null);
  const [reportDir, setReportDir] = useState("");
  const [engine, setEngine] = useState<EngineInfo>({ url: "", token: "", ready: false });
  const [wizard, setWizard] = useState(false);
  const [wizardModels, setWizardModels] = useState<LibraryItem[]>([]);
  const [modelsFocusSearch, setModelsFocusSearch] = useState(false);
  const [doctor, setDoctor] = useState<DoctorSnapshot | null>(null);
  const [splash, setSplash] = useState(true);
  const [bootDoctorDone, setBootDoctorDone] = useState(false);
  const [splashRepairHint, setSplashRepairHint] = useState(false);
  const [minSplashElapsed, setMinSplashElapsed] = useState(false);
  const [update, setUpdate] = useState<UpdateStatus | null>(null);
  const [downloadPct, setDownloadPct] = useState(0);
  const autoOpenedReport = useRef<string | null>(null);
  const benchWasActive = useRef(false);
  const splashRef = useRef(true);
  const bootSawWork = useRef(false);
  const compareLoaded = useRef(false);
  splashRef.current = splash;

  useEffect(() => {
    const t = window.setTimeout(() => setMinSplashElapsed(true), 5000);
    return () => window.clearTimeout(t);
  }, []);

  useEffect(() => {
    let cancelled = false;
    let unlisten: (() => void) | undefined;
    (async () => {
      const first = await getUpdateStatus();
      if (!cancelled && first) {
        setUpdate(first);
        if (first.justUpdated) setTab("settings");
      }
      void checkForUpdate().then((s) => {
        if (!cancelled && s) {
          setUpdate(s);
          if (s.justUpdated) setTab("settings");
        }
      });
      unlisten = await onUpdateProgress((p) => {
        if (p.total > 0) setDownloadPct(Math.min(100, Math.round((100 * p.received) / p.total)));
      });
    })();
    return () => {
      cancelled = true;
      unlisten?.();
    };
  }, []);

  useEffect(() => {
    if (update?.state !== "downloading" && update?.state !== "applying") return;
    let cancelled = false;
    const poll = window.setInterval(() => {
      void getUpdateStatus().then((s) => {
        if (!cancelled && s) setUpdate(s);
      });
    }, 800);
    return () => {
      cancelled = true;
      window.clearInterval(poll);
    };
  }, [update?.state]);

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
      void engineGet<DoctorSnapshot>(info, "/doctor/status").then((snap) => {
        if (!cancelled && snap) setDoctor(snap);
      });
      const [reportPrefs, lib, b, listed] = await Promise.all([
        engineGet<{ default_report_dir?: string }>(info, "/settings"),
        engineGet<LibraryResponse>(info, "/models/library?filter=Installed"),
        engineGet<BenchSnapshot>(info, "/bench/status"),
        engineGet<{ runs: EngineRun[] }>(info, "/bench/runs"),
      ]);
      if (!cancelled && typeof reportPrefs?.default_report_dir === "string") setReportDir(reportPrefs.default_report_dir);
      if (!cancelled && lib) setInstalledLib(lib);
      if (!cancelled && b) setBenchSnap(b);
      if (!cancelled && listed?.runs) setRuns(listed.runs);
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
    try {
      const existing = await engineGet<{ html_path?: string | null }>(engine, `/reports/${id}/paths`);
      const ready = existing?.html_path;
      const path =
        ready ||
        (await enginePost<{ html_path?: string }>(engine, `/reports/${id}/render`))?.html_path;
      if (!path) {
        return;
      }
      try {
        await openOnOs(path);
        return;
      } catch {
        const launched = await enginePost<{ ok?: boolean }>(engine, `/reports/${id}/open`);
        if (launched?.ok) return;
      }
    } catch {
      /* report may still have opened in the browser */
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
        void engineGet<DoctorSnapshot>(info, "/doctor/status").then((snap) => {
          if (!cancelled && snap) setDoctor(snap);
        });
      }
    }, 800);
    return () => {
      cancelled = true;
      window.clearInterval(tick);
    };
  }, [engine.url]);

  const doctorLive = doctorStillWorking(doctor);
  const benchLive = benchSnap?.state === "running" || benchSnap?.state === "paused";
  const doctorStream = splash || doctorLive;

  const refreshReports = useCallback(async () => {
    if (!engine.url) return;
    compareLoaded.current = true;
    const listed = await engineGet<{ runs: EngineRun[] }>(engine, "/bench/runs");
    if (listed?.runs) setRuns(listed.runs);
    const res = await engineGet<{ runs?: CompareSource[]; this_machine?: string }>(engine, "/reports/compare/sources");
    if (res?.runs) setCompareSources(res.runs);
    if (res?.this_machine) setThisMachine(res.this_machine);
  }, [engine]);

  useEffect(() => {
    if (!engine.url || !doctorStream) return;
    const ac = new AbortController();
    let cancelled = false;
    const apply = (data: unknown) => {
      const snap = data as DoctorSnapshot;
      if (snap && (snap.state || snap.checks)) setDoctor(snap);
    };
    void engineSse(engine, "/doctor/events", apply, ac.signal).catch(async () => {
      while (!cancelled && !ac.signal.aborted) {
        const snap = await engineGet<DoctorSnapshot>(engine, "/doctor/status");
        if (cancelled) return;
        if (snap) setDoctor(snap);
        await new Promise((r) => window.setTimeout(r, 1000));
      }
    });
    return () => {
      cancelled = true;
      ac.abort();
    };
  }, [engine.url, engine.token, doctorStream]);

  useEffect(() => {
    if (!engine.url || !benchLive) return;
    const ac = new AbortController();
    let cancelled = false;
    const apply = (data: unknown) => {
      const b = data as BenchSnapshot;
      if (!b?.state) return;
      setBenchSnap(b);
      if (b.state === "running" || b.state === "paused") {
        benchWasActive.current = true;
      } else if (benchWasActive.current) {
        benchWasActive.current = false;
        void refreshReports();
        if (b.open_report && b.open_report !== autoOpenedReport.current) {
          autoOpenedReport.current = b.open_report;
          void openHtml(b.open_report);
        }
      }
    };
    void engineSse(engine, "/bench/events", apply, ac.signal).catch(async () => {
      while (!cancelled && !ac.signal.aborted) {
        const b = await engineGet<BenchSnapshot>(engine, "/bench/status");
        if (cancelled) return;
        if (b) apply(b);
        await new Promise((r) => window.setTimeout(r, 1000));
      }
    });
    return () => {
      cancelled = true;
      ac.abort();
    };
  }, [engine.url, engine.token, benchLive, openHtml, refreshReports]);

  const downloadBusy = (installedLib?.jobs || []).some((j) =>
    ["queued", "downloading", "verifying", "paused"].includes(String(j.state || "")),
  );

  const library = useMemo(
    () => viewFromCaches(filter, installedLib, preferredLib, searchLib, query),
    [filter, installedLib, preferredLib, searchLib, query],
  );

  const libraryPath = (which: ModelFilter = filter, q = query) =>
    `/models/library?filter=${encodeURIComponent(which)}` +
    (q ? `&q=${encodeURIComponent(q)}` : "");

  const applyJobs = (jobs: LibraryJob[]) => {
    setInstalledLib((prev) => mergeLibraryJobs(prev, jobs));
    setPreferredLib((prev) => mergeLibraryJobs(prev, jobs));
    setSearchLib((prev) => mergeLibraryJobs(prev, jobs));
  };

  const refreshLibrary = () => {
    if (!engine.url) return;
    void engineGet<LibraryResponse>(engine, libraryPath("Installed", "")).then((lib) => lib && setInstalledLib(lib));
    if (filter === "Preferred") {
      void engineGet<LibraryResponse>(engine, libraryPath("Preferred", "")).then((lib) => lib && setPreferredLib(lib));
    } else if (filter === "Search Ollama" && query.trim()) {
      void engineGet<LibraryResponse>(engine, libraryPath()).then((lib) => lib && setSearchLib(lib));
    }
  };

  useEffect(() => {
    if (!engine.url || filter !== "Preferred" || preferredLib) return;
    void engineGet<LibraryResponse>(engine, libraryPath("Preferred", "")).then((lib) => lib && setPreferredLib(lib));
  }, [engine.url, engine.token, filter, preferredLib]);

  useEffect(() => {
    if (!engine.url || filter !== "Search Ollama") return;
    const q = query.trim();
    if (!q) return;
    const start = window.setTimeout(() => {
      void engineGet<LibraryResponse>(engine, libraryPath("Search Ollama", q)).then((lib) => lib && setSearchLib(lib));
    }, 350);
    return () => window.clearTimeout(start);
  }, [engine.url, engine.token, filter, query]);

  useEffect(() => {
    if (!engine.url || !downloadBusy) return;
    let cancelled = false;
    const pullJobs = async () => {
      const res = await engineGet<{ jobs?: LibraryJob[] }>(engine, "/models/jobs");
      if (!cancelled && res?.jobs) applyJobs(res.jobs);
    };
    void pullJobs();
    const id = window.setInterval(() => void pullJobs(), 2000);
    return () => {
      cancelled = true;
      window.clearInterval(id);
    };
  }, [engine.url, engine.token, downloadBusy]);

  useEffect(() => {
    if (!engine.url || tab !== "compare" || compareLoaded.current) return;
    compareLoaded.current = true;
    void engineGet<{ runs?: CompareSource[]; this_machine?: string }>(engine, "/reports/compare/sources").then((res) => {
      if (res?.runs) setCompareSources(res.runs);
      if (res?.this_machine) setThisMachine(res.this_machine);
    });
  }, [engine.url, engine.token, tab]);

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

  const selectedCount = installedLib?.selected?.length ?? 0;
  const openDownloadStates = ["queued", "downloading", "verifying", "paused", "failed"];
  const downloading = (installedLib?.jobs ?? []).some((j) => openDownloadStates.includes(j.state))
    || (installedLib?.items ?? []).some((m) => openDownloadStates.includes(m.download?.state || ""));
  const installedCount = installedLib?.installed_count ?? installedLib?.items?.filter((m) => m.installed).length ?? doctor?.models?.length ?? 0;
  const envReady = !!doctor?.gate?.environment_ready;
  const canOpenGuide = envReady && !downloading && benchSnap?.state !== "running" && benchSnap?.state !== "paused";
  const startHint = useMemo(() => {
    if (!envReady) return doctor?.gate?.reasons?.[0] || "Finish Doctor before starting a benchmark.";
    if (downloading) return "Wait for downloads to finish.";
    if (benchSnap?.state === "running" || benchSnap?.state === "paused") return "A benchmark is already in progress.";
    if (installedCount < 1) return "No model yet — the guide will show you where to get one.";
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

  const lockTabs = !!update?.updateAvailable && update.online;
  const lockedTabs: TabId[] = lockTabs ? ["doctor", "models", "benchmark", "reports", "compare"] : [];

  const go = (id: TabId) => {
    if (splashRef.current) return;
    if (lockedTabs.includes(id)) {
      setTab("settings");
      setHelp(false);
      setWizard(false);
      return;
    }
    setTab(id);
    if (id !== "reports") setReportId(null);
    setHelp(false);
    setWizard(false);
  };

  useEffect(() => {
    const frame = helpFrameRef.current;
    if (!help || !frame) return;
    const send = () => {
      frame.contentWindow?.postMessage({ type: "haval-color-theme", theme: colorTheme }, "*");
    };
    send();
    frame.addEventListener("load", send);
    return () => frame.removeEventListener("load", send);
  }, [help, colorTheme]);

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
      const id = TABS[idx - 1].id;
      if (lockTabs && ["doctor", "models", "benchmark", "reports", "compare"].includes(id)) {
        setTab("settings");
        setHelp(false);
        setWizard(false);
        return;
      }
      go(id);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [lockTabs]);

  const tryStart = () => {
    if (lockTabs) {
      go("settings");
      return;
    }
    if (!envReady) {
      go("doctor");
      return;
    }
    if (!canOpenGuide) {
      go("benchmark");
      return;
    }
    go("benchmark");
    setWizard(true);
    setWizardModels((installedLib?.items || []).filter((m) => m.installed));
  };

  useEffect(() => {
    if (!wizard || !installedLib) return;
    setWizardModels((installedLib.items || []).filter((m) => m.installed));
  }, [wizard, installedLib]);

  const leaveWizardToModels = (search: boolean) => {
    setWizard(false);
    setFilter(search ? "Search Ollama" : "Preferred");
    setQuery("");
    setModelsFocusSearch(search);
    go("models");
  };

  const launchWizard = (opts: WizardLaunch) => {
    setWizard(false);
    go("benchmark");
    enginePost(engine, "/bench/start", {
      model: opts.model,
      thinking: opts.thinking,
      personas: opts.personas,
      report_dir: opts.report_dir || reportDir || null,
    }).then(() => engineGet<BenchSnapshot>(engine, "/bench/status").then((b) => b && setBenchSnap(b)));
  };

  async function exportPdf(id: string) {
    const rendered = await enginePost<{ pdf_path?: string | null; html_path?: string }>(engine, `/reports/${id}/render`);
    const path = rendered?.pdf_path || rendered?.html_path;
    if (!path) return;
    try {
      await openOnOs(path);
    } catch {
      /* opened or not — never show a path dialog */
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
      /* Explorer may still have opened the folder */
    }
  }

  async function deleteReports(ids: string[]): Promise<boolean> {
    if (!ids.length) return false;
    setDeletingReports(true);
    setDeleteError(null);
    try {
      let lastRuns: EngineRun[] | undefined;
      for (const id of ids) {
        const result = await enginePost<{ ok?: boolean; runs?: EngineRun[] }>(engine, `/reports/${id}/delete`);
        if (!result?.ok) {
          setDeleteError("Could not delete that report. If a benchmark is still running, stop it first.");
          if (result?.runs) setRuns(result.runs);
          return false;
        }
        lastRuns = result.runs;
        if (lastCompareId === id) setLastCompareId(null);
      }
      setReportId(null);
      if (lastRuns) {
        setRuns(lastRuns);
        return true;
      }
      const listed = await engineGet<{ runs: EngineRun[] }>(engine, "/bench/runs");
      if (listed?.runs) setRuns(listed.runs);
      return true;
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Could not delete that report.";
      setDeleteError(msg);
      return false;
    } finally {
      setDeletingReports(false);
    }
  }

  async function runCompare(runIds: string[], uploads: { name: string; html: string }[]) {
    setCompareBusy(true);
    setCompareError(null);
    try {
      const result = await enginePost<{ ok?: boolean; run_id?: string }>(engine, "/reports/compare", {
        run_ids: runIds,
        uploads,
      });
      if (!result?.run_id) {
        setCompareError("Select reports from at least two different models.");
        return;
      }
      await refreshReports();
      setLastCompareId(result.run_id);
      void openHtml(result.run_id);
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Comparison could not be built.";
      setCompareError(msg);
    } finally {
      setCompareBusy(false);
    }
  }

  return (
    <div className={`shell${help ? " help-open" : ""}`}>
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
      {!splash ? (
        <AppHeader
          tab={tab}
          repair={overall}
          onTab={go}
          onHelp={() => setHelp((h) => !h)}
          lockedTabs={lockedTabs}
        />
      ) : null}
      <main id="main" className="content" tabIndex={-1}>
        {!splash && update?.updateAvailable && update.online ? (
          <div className="update-banner" role="status">
            <span>Version {update.latest} is available. Open Settings → Update.</span>
            <button className="btn tertiary" type="button" onClick={() => go("settings")}>
              Open Settings
            </button>
          </div>
        ) : null}
        {!splash && (update?.state === "offline" || (update?.state === "failed" && !update.updateAvailable)) ? (
          <div className="update-banner" style={{ background: "var(--canvas)", color: "var(--ink-soft)", fontWeight: 500 }} role="status">
            {update.message || (update.state === "offline"
              ? "No internet — could not check for updates."
              : "Could not check for updates.")}
          </div>
        ) : null}
        {wizard ? (
          <BenchWizard
            models={wizardModels}
            defaultModel={installedLib?.selected?.[0]}
            defaultThinking={false}
            defaultReportDir={reportDir || null}
            onCancel={() => setWizard(false)}
            onLaunch={launchWizard}
            onGoToModels={() => leaveWizardToModels(false)}
            onSearchModels={() => leaveWizardToModels(true)}
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
            canStart={canOpenGuide}
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
            focusSearch={modelsFocusSearch}
            onFilter={setFilter}
            onQuery={setQuery}
            onRefresh={refreshLibrary}
            onToggle={(name, selected) =>
              enginePost<{ selected?: string[] }>(engine, "/models/select", { name, selected }).then((res) => {
                const sel = res?.selected ?? (selected ? [name] : []);
                setInstalledLib((prev) => patchSelected(prev, sel));
                setPreferredLib((prev) => patchSelected(prev, sel));
                setSearchLib((prev) => patchSelected(prev, sel));
              })
            }
            onDownload={(name) =>
              enginePost<{ jobs?: LibraryJob[] }>(engine, "/models/downloads", { name }).then((res) => {
                if (res?.jobs) applyJobs(res.jobs);
              })
            }
            onCancel={(jobId) =>
              enginePost<{ jobs?: LibraryJob[] }>(engine, `/models/downloads/${jobId}/cancel`).then((res) => {
                if (res?.jobs) applyJobs(res.jobs);
              })
            }
            onRetry={(jobId) =>
              enginePost<{ jobs?: LibraryJob[] }>(engine, `/models/downloads/${jobId}/retry`).then((res) => {
                if (res?.jobs) applyJobs(res.jobs);
              })
            }
            onRemove={(name) =>
              enginePost<LibraryResponse>(engine, "/models/remove?filter=Installed", { name }).then((lib) => {
                if (lib) setInstalledLib(lib);
              })
            }
          />
        )}
        {tab === "benchmark" && (
          <BenchmarkScreen
            snapshot={benchSnap}
            showLog={showLog}
            canStart={canOpenGuide}
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
            deleting={deletingReports}
            deleteError={deleteError}
            onDelete={(ids) => deleteReports(ids)}
            onRefresh={refreshReports}
            onGoCompare={() => go("compare")}
          />
        )}
        {tab === "compare" && (
          <CompareScreen
            sources={compareSources}
            thisMachine={thisMachine}
            runs={runs}
            busy={compareBusy}
            error={compareError}
            lastId={lastCompareId}
            onCompare={(ids, uploads) => void runCompare(ids, uploads)}
            onOpenHtml={(id) => void openHtml(id)}
            onFolder={(id) => void showFolder(id)}
            deleting={deletingReports}
            onDelete={(ids) => deleteReports(ids)}
            onIntroBack={() => go("reports")}
          />
        )}
        {tab === "settings" && (
          <SettingsScreen
            reportDir={reportDir}
            onReportDir={(path) => {
              setReportDir(path);
              void enginePost(engine, "/settings", { default_report_dir: path });
            }}
            colorTheme={colorTheme}
            onColorTheme={(theme) => {
              saveColorTheme(theme);
              setColorTheme(theme);
            }}
            update={update}
            downloadPct={downloadPct}
            onUpdateNow={() => {
              void (async () => {
                try {
                  const next = await downloadUpdate();
                  setUpdate(next);
                  await applyUpdate();
                } catch (err) {
                  const msg = err instanceof Error ? err.message : String(err);
                  setUpdate((cur) =>
                    cur
                      ? { ...cur, state: "failed", message: msg || "Download failed. Try again." }
                      : cur,
                  );
                }
              })();
            }}
          />
        )}
          </>
        )}
      </main>
      {help ? (
        <div className="help-guide-overlay" role="dialog" aria-modal="true" aria-labelledby="help-guide-title">
          <div className="help-guide-toolbar">
            <div>
              <div className="kicker" id="help-guide-title">
                Help guide
              </div>
              <div className="help-guide-sub">How to use Haval — fits this window</div>
            </div>
            <button className="btn secondary" type="button" onClick={() => setHelp(false)}>
              Close
            </button>
          </div>
          <iframe
            ref={helpFrameRef}
            className="help-guide-frame"
            title="How to use Haval LocalAI Benchmarking"
            src={`/app-help-guide/index.html?theme=${encodeURIComponent(colorTheme)}`}
          />
        </div>
      ) : null}
    </div>
  );
}
