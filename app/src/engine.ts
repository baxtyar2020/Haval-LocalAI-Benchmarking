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
  } catch (err) {
    const msg = typeof err === "string" ? err : (err as Error)?.message || "";
    if (path.includes("/reports/") && msg) {
      throw new Error(msg);
    }
    return null;
  }
}

type FetchResult =
  | { kind: "ok"; text: string }
  | { kind: "fail"; retrySidecar: boolean; error?: Error };

async function viaFetch(info: EngineInfo, method: string, path: string, body?: unknown, timeoutMs = 4000): Promise<FetchResult> {
  if (!info.url || !info.token) return { kind: "fail", retrySidecar: true };
  const ctrl = new AbortController();
  const timer = window.setTimeout(() => ctrl.abort(), timeoutMs);
  try {
    const res = await fetch(`${info.url}${path}`, {
      method,
      signal: ctrl.signal,
      headers: {
        Authorization: `Bearer ${info.token}`,
        ...(method === "POST" ? { "Content-Type": "application/json" } : {}),
      },
      body: method === "POST" ? JSON.stringify(body ?? {}) : undefined,
    });
    const text = await res.text();
    if (!res.ok) {
      if (path.includes("/reports/")) {
        try {
          const parsed = JSON.parse(text) as { detail?: unknown };
          if (typeof parsed.detail === "string" && parsed.detail) {
            return { kind: "fail", retrySidecar: false, error: new Error(parsed.detail) };
          }
        } catch (err) {
          if (err instanceof Error && err.message && err.message !== text) {
            return { kind: "fail", retrySidecar: false, error: err };
          }
        }
        return { kind: "fail", retrySidecar: false, error: new Error(text || res.statusText) };
      }
      return { kind: "fail", retrySidecar: false };
    }
    return { kind: "ok", text };
  } catch (err) {
    if (err instanceof Error && path.includes("/reports/")) {
      const aborted = err.name === "AbortError";
      return { kind: "fail", retrySidecar: !aborted, error: aborted ? undefined : err };
    }
    const aborted = err instanceof Error && err.name === "AbortError";
    return { kind: "fail", retrySidecar: !aborted };
  } finally {
    window.clearTimeout(timer);
  }
}

async function engineText(info: EngineInfo, method: string, path: string, body?: unknown): Promise<string | null> {
  const timeoutMs = method === "POST" ? 45000 : 4000;
  const fetched = await viaFetch(info, method, path, body, timeoutMs);
  if (fetched.kind === "ok") return fetched.text;
  if (fetched.error) throw fetched.error;
  if (!fetched.retrySidecar) return null;
  return viaSidecar(method, path, body);
}

function isPing(data: unknown): boolean {
  return !!data && typeof data === "object" && "ping" in data && Object.keys(data as object).length === 1;
}

export async function engineSse(
  info: EngineInfo,
  path: string,
  onData: (data: unknown) => void,
  signal: AbortSignal,
): Promise<void> {
  if (!info.url || !info.token) throw new Error("Engine is not ready.");
  const res = await fetch(`${info.url}${path}`, {
    method: "GET",
    headers: { Authorization: `Bearer ${info.token}`, Accept: "text/event-stream" },
    signal,
  });
  if (!res.ok || !res.body) throw new Error(`SSE ${res.status}`);
  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buf = "";
  while (!signal.aborted) {
    const { done, value } = await reader.read();
    if (done) break;
    buf += decoder.decode(value, { stream: true });
    const chunks = buf.split("\n\n");
    buf = chunks.pop() || "";
    for (const chunk of chunks) {
      const line = chunk.split("\n").find((row) => row.startsWith("data:"));
      if (!line) continue;
      const raw = line.slice(5).trim();
      if (!raw) continue;
      try {
        const parsed: unknown = JSON.parse(raw);
        if (!isPing(parsed)) onData(parsed);
      } catch {
        /* ignore malformed SSE */
      }
    }
  }
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
