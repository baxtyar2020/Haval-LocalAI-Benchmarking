export type TabId = "home" | "doctor" | "models" | "benchmark" | "reports" | "settings";

export type RepairState = "attention" | "repairing" | "ready" | "checking";
export type BenchState = "idle" | "running" | "paused";

export type BenchSnapshot = {
  state: BenchState | string;
  run_id?: string | null;
  pct: number;
  message: string;
  detail?: string;
  model_index?: number;
  model_count?: number;
  elapsed_s?: number;
  tok_s?: number | null;
  ttft_s?: number | null;
  headroom_gb?: number | null;
  cpu_pct?: number | null;
  ram_pct?: number | null;
  vram_pct?: number | null;
  completion_pct?: number | null;
  prompt?: string;
  answer?: string;
  task_title?: string;
  log?: string[];
  selected?: string[];
  thinking?: boolean;
  open_report?: string | null;
};

export type EngineRun = {
  id: string;
  started_at?: string;
  ended_at?: string;
  status?: string;
  models_json?: string;
  summary_json?: string;
  headline?: string;
};
export type ModelFilter = "Installed" | "Preferred" | "Search Ollama";
export type FitLevel = "exc" | "str" | "mar" | "no";

export type CatalogModel = {
  id: string;
  display_name: string;
  tag: string;
  family: string;
  pull: string;
  params: string;
  quant: string;
  size_hint: string;
  roster_order: number;
};

export type LibraryItem = {
  id: string;
  name: string;
  display_name?: string;
  tag?: string;
  family?: string;
  params?: string;
  params_total?: string;
  params_active?: string;
  params_moe?: boolean;
  params_label?: string;
  pull_command?: string;
  quant?: string;
  size_label?: string;
  preferred?: boolean;
  installed?: boolean;
  selectable?: boolean;
  selected?: boolean;
  description?: string;
  fit?: { level: FitLevel | string; label: string };
  validation?: { class?: string; detail?: string };
  download?: {
    id: string;
    name: string;
    state: string;
    pct: number;
    stage: string;
    error?: string | null;
  };
};

export type LibraryResponse = {
  ollama_ok: boolean;
  storage: { free_gb?: number; total_gb?: number };
  accel_gb?: number;
  items: LibraryItem[];
  selected: string[];
  installed_count?: number;
};

export type EngineInfo = {
  url: string;
  token: string;
  ready: boolean;
  error?: string | null;
};

export type DoctorCheck = {
  id: string;
  title: string;
  detail: string;
  status: "checking" | "passed" | "warning" | "failed" | "repairing" | "blocked";
  blocking?: boolean;
  action?: string | null;
};

export type DoctorSnapshot = {
  state: string;
  overall: RepairState;
  subtitle: string;
  checks: DoctorCheck[];
  hardware: Record<string, unknown>;
  tech_log: string;
  models: { name?: string; size?: number }[];
  probe: Record<string, unknown>;
  gate: {
    ready: boolean;
    environment_ready?: boolean;
    reasons: string[];
  };
};
