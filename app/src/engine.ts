import { invoke } from "@tauri-apps/api/core";
import type { CatalogModel, EngineInfo } from "./types";

const fallback: EngineInfo = {
  url: "http://127.0.0.1:8765",
  token: "dev-local-token",
  ready: false,
  error: null,
};

function isViteDev(): boolean {
  return typeof location !== "undefined" && location.port === "1420";
}

export async function loadEngineInfo(): Promise<EngineInfo> {
  try {
    return await invoke<EngineInfo>("engine_info");
  } catch {
    if (isViteDev()) return fallback;
    return { url: "", token: "", ready: false, error: "Starting the bench engine…" };
  }
}

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => window.setTimeout(resolve, ms));
}

function engineStillStarting(info: EngineInfo): boolean {
  if (info.ready && info.url) return false;
  const err = (info.error || "").toLowerCase();
  if (!err) return !info.url;
  return err.includes("starting") || err.includes("not answering");
}

export async function waitForEngine(timeoutMs = 45000): Promise<EngineInfo> {
  const deadline = Date.now() + timeoutMs;
  let last = await loadEngineInfo();
  while (Date.now() < deadline && engineStillStarting(last)) {
    await sleep(400);
    last = await loadEngineInfo();
  }
  return last;
}

export async function restartEngine(): Promise<EngineInfo> {
  return invoke<EngineInfo>("restart_engine");
}

export async function openOnOs(path: string): Promise<void> {
  await invoke("open_with_os", { path });
}

async function viaSidecar(method: string, path: string, body?: unknown): Promise<string | null> {
  try {
    return await invoke<string>("engine_request", {
      method,
      path,
      body: body === undefined ? null : JSON.stringify(body ?? {}),
    });
  } catch {
    return null;
  }
}

async function viaFetch(info: EngineInfo, method: string, path: string, body?: unknown): Promise<string | null> {
  if (!info.url || !info.token) return null;
  try {
    const res = await fetch(`${info.url}${path}`, {
      method,
      headers: {
        Authorization: `Bearer ${info.token}`,
        ...(method === "POST" ? { "Content-Type": "application/json" } : {}),
      },
      body: method === "POST" ? JSON.stringify(body ?? {}) : undefined,
    });
    if (!res.ok) return null;
    return await res.text();
  } catch {
    return null;
  }
}

async function engineText(info: EngineInfo, method: string, path: string, body?: unknown): Promise<string | null> {
  const proxied = await viaSidecar(method, path, body);
  if (proxied != null) return proxied;
  return viaFetch(info, method, path, body);
}

export async function engineGetText(info: EngineInfo, path: string): Promise<string | null> {
  return engineText(info, "GET", path);
}

export async function engineGet<T>(info: EngineInfo, path: string): Promise<T | null> {
  const text = await engineText(info, "GET", path);
  if (!text) return null;
  try {
    return JSON.parse(text) as T;
  } catch {
    return null;
  }
}

export async function enginePost<T>(info: EngineInfo, path: string, body: unknown = {}): Promise<T | null> {
  const text = await engineText(info, "POST", path, body);
  if (!text) return null;
  try {
    return JSON.parse(text) as T;
  } catch {
    return null;
  }
}

export type HealthResponse = {
  ok: boolean;
  service: string;
  version: string;
  started_at: string;
};

export type PreferredResponse = {
  version: string;
  models: CatalogModel[];
};
