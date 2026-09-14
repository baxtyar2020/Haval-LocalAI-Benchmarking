import { invoke } from "@tauri-apps/api/core";
import { listen, type UnlistenFn } from "@tauri-apps/api/event";

export type UpdateStatus = {
  installed: string;
  latest: string | null;
  notes: string;
  online: boolean;
  updateAvailable: boolean;
  state: string;
  message: string;
  received: number;
  total: number;
  justUpdated: boolean;
};

export type UpdateProgress = {
  received: number;
  total: number;
};

export async function getUpdateStatus(): Promise<UpdateStatus | null> {
  try {
    return await invoke<UpdateStatus>("update_status");
  } catch {
    return null;
  }
}

export async function checkForUpdate(): Promise<UpdateStatus | null> {
  try {
    return await invoke<UpdateStatus>("update_check");
  } catch {
    return null;
  }
}

export async function downloadUpdate(): Promise<UpdateStatus> {
  return invoke<UpdateStatus>("update_download");
}

export async function applyUpdate(): Promise<void> {
  await invoke("update_apply");
}

export function onUpdateProgress(handler: (p: UpdateProgress) => void): Promise<UnlistenFn> {
  return listen<UpdateProgress>("update://progress", (ev) => handler(ev.payload));
}
