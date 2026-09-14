export const COLOR_THEMES = ["current", "classic", "dawn", "flexoki"] as const;
export type ColorTheme = (typeof COLOR_THEMES)[number];

export const DEFAULT_COLOR_THEME: ColorTheme = "current";
const STORAGE_KEY = "haval-color-theme";

export const COLOR_THEME_CHOICES: {
  id: ColorTheme;
  name: string;
  note: string;
  swatches: [string, string];
}[] = [
  { id: "current", name: "Haval", note: "Default · cream and sage", swatches: ["#db4f1b", "#7a8a5e"] },
  { id: "classic", name: "Classic", note: "Original paper and forest green", swatches: ["#db4f1b", "#287653"] },
  { id: "dawn", name: "Dawn", note: "Rosé Pine · rose and pine", swatches: ["#d7827e", "#286983"] },
  { id: "flexoki", name: "Flexoki", note: "Ink on paper · orange and moss", swatches: ["#bc5215", "#66800b"] },
];

export function isColorTheme(value: string | null | undefined): value is ColorTheme {
  return COLOR_THEMES.includes(value as ColorTheme);
}

export function loadColorTheme(): ColorTheme {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (isColorTheme(stored)) return stored;
  } catch {
    /* ignore */
  }
  return DEFAULT_COLOR_THEME;
}

export function applyColorTheme(theme: ColorTheme): void {
  const root = document.documentElement;
  root.removeAttribute("data-color-theme");
  void root.offsetWidth;
  root.setAttribute("data-color-theme", theme);
  requestAnimationFrame(() => syncWindowChrome());
}

function cssHex(value: string, fallback: string): string {
  const raw = value.trim();
  if (raw.startsWith("#") && (raw.length === 7 || raw.length === 4)) {
    if (raw.length === 4) {
      return `#${raw[1]}${raw[1]}${raw[2]}${raw[2]}${raw[3]}${raw[3]}`;
    }
    return raw.slice(0, 7);
  }
  const m = raw.match(/rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)/i);
  if (!m) return fallback;
  const hex = (n: string) => Number(n).toString(16).padStart(2, "0");
  return `#${hex(m[1])}${hex(m[2])}${hex(m[3])}`;
}

/** Match the Windows title bar to the active in-app theme (cream by default). */
export function syncWindowChrome(): void {
  try {
    const cs = getComputedStyle(document.documentElement);
    const background = cssHex(cs.getPropertyValue("--bg"), "#fbf0de");
    const foreground = cssHex(cs.getPropertyValue("--text"), "#201e1d");
    void import("@tauri-apps/api/core")
      .then(({ invoke }) => invoke("set_titlebar_theme", { background, foreground }))
      .catch(() => {
        /* browser preview / older OS */
      });
  } catch {
    /* ignore */
  }
}

export function saveColorTheme(theme: ColorTheme): void {
  applyColorTheme(theme);
  try {
    localStorage.setItem(STORAGE_KEY, theme);
  } catch {
    /* ignore */
  }
}

applyColorTheme(loadColorTheme());
