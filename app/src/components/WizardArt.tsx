/** Simple in-app drawings for the guided setup. Warm paper, terracotta, ink. */

type ArtProps = { className?: string };

const ink = "#1a1a1a";
const soft = "#8a857d";
const paper = "#fffdf8";
const cream = "#fbf0de";
const accent = "#db4f1b";
const blush = "#ffe9e0";
const ok = "#7a8a5e";
const info = "#456a87";

export function WizardArtModel({ className }: ArtProps) {
  return (
    <svg className={className} viewBox="0 0 320 240" fill="none" aria-hidden>
      <rect x="18" y="28" width="284" height="184" rx="28" fill={blush} />
      <g className="wa-bob">
        <rect x="78" y="52" width="164" height="108" rx="12" fill={ink} />
        <rect x="86" y="60" width="148" height="86" rx="6" fill={cream} />
        <circle className="wa-glow" cx="160" cy="103" r="28" fill={accent} opacity="0.22" />
        <circle className="wa-spin-slow" cx="160" cy="103" r="22" fill={accent} />
        <rect x="148" y="91" width="24" height="24" rx="5" fill={paper} />
        <rect className="wa-pulse" x="154" y="97" width="12" height="12" rx="2" fill={accent} />
      </g>
      <rect x="118" y="164" width="84" height="10" rx="3" fill={ink} />
      <rect x="132" y="174" width="56" height="8" rx="3" fill={soft} opacity="0.45" />
      <g className="wa-pulse">
        <circle cx="58" cy="188" r="16" fill={paper} stroke={ink} strokeWidth="2.5" />
        <path d="M52 188h12M58 182v12" stroke={accent} strokeWidth="2.2" strokeLinecap="round" />
      </g>
      <g className="wa-bars">
        <rect x="248" y="48" width="36" height="50" rx="8" fill={paper} stroke={ink} strokeWidth="2" />
        <rect className="wa-bar1" x="256" y="58" width="20" height="6" rx="2" fill={ok} />
        <rect className="wa-bar2" x="256" y="70" width="20" height="6" rx="2" fill={info} />
        <rect className="wa-bar3" x="256" y="82" width="14" height="6" rx="2" fill={accent} />
      </g>
    </svg>
  );
}

export function WizardArtPeople({ className }: ArtProps) {
  return (
    <svg className={className} viewBox="0 0 320 240" fill="none" aria-hidden>
      <rect x="18" y="28" width="284" height="184" rx="28" fill={cream} />
      <g className="wa-card wa-d1">
        <rect x="36" y="58" width="78" height="118" rx="18" fill={paper} stroke={blush} strokeWidth="3" />
        <path d="M62 88h26" stroke={accent} strokeWidth="4" strokeLinecap="round" />
        <circle className="wa-pulse" cx="75" cy="118" r="14" fill={blush} />
        <rect x="58" y="136" width="34" height="22" rx="8" fill={ink} />
      </g>
      <g className="wa-card wa-d2">
        <rect x="121" y="58" width="78" height="118" rx="18" fill={paper} stroke={blush} strokeWidth="3" />
        <rect className="wa-blink" x="138" y="84" width="44" height="28" rx="6" fill={info} />
        <circle cx="149" cy="93" r="4" fill={paper} />
        <circle cx="171" cy="93" r="4" fill={paper} />
        <path d="M148 104h22" stroke={paper} strokeWidth="2" strokeLinecap="round" />
        <rect x="146" y="128" width="28" height="32" rx="6" fill={accent} />
      </g>
      <g className="wa-card wa-d3">
        <rect x="206" y="58" width="78" height="118" rx="18" fill={paper} stroke={blush} strokeWidth="3" />
        <rect x="222" y="86" width="46" height="34" rx="4" fill={ink} />
        <rect className="wa-scan" x="228" y="92" width="34" height="16" rx="2" fill={cream} />
        <rect className="wa-bar1" x="236" y="132" width="30" height="8" rx="2" fill={ok} />
        <rect x="228" y="146" width="46" height="8" rx="2" fill={soft} opacity="0.4" />
      </g>
    </svg>
  );
}

export function WizardArtThink({ className }: ArtProps) {
  return (
    <svg className={className} viewBox="0 0 320 240" fill="none" aria-hidden>
      <rect x="18" y="28" width="284" height="184" rx="28" fill={blush} />
      <path className="wa-dash" d="M52 128h86" stroke={ok} strokeWidth="6" strokeLinecap="round" />
      <path className="wa-nudge" d="M120 116l18 12-18 12" stroke={ok} strokeWidth="6" strokeLinecap="round" strokeLinejoin="round" />
      <g className="wa-pulse">
        <circle cx="78" cy="88" r="22" fill={paper} />
        <path d="M78 78v16M70 88h16" stroke={ok} strokeWidth="3" strokeLinecap="round" />
      </g>
      <g className="wa-think">
        <path
          d="M176 86c18-22 52-18 62 8 18 4 28 28 8 42-8 22-48 26-64 8-22 2-40-18-22-38 4-8 10-14 16-20z"
          fill={paper}
          stroke={ink}
          strokeWidth="2.5"
        />
        <circle className="wa-dot1" cx="214" cy="118" r="5" fill={accent} />
        <circle className="wa-dot2" cx="232" cy="112" r="3.5" fill={accent} opacity="0.7" />
        <circle className="wa-dot3" cx="198" cy="128" r="3" fill={ink} />
      </g>
      <text x="52" y="178" fill={ink} fontSize="11" fontWeight="500" fontFamily="Segoe UI, sans-serif">
        Off — answer now
      </text>
      <text x="176" y="178" fill={ink} fontSize="11" fontWeight="500" fontFamily="Segoe UI, sans-serif">
        On — think first
      </text>
    </svg>
  );
}

export function WizardArtReport({ className }: ArtProps) {
  return (
    <svg className={className} viewBox="0 0 320 240" fill="none" aria-hidden>
      <rect x="18" y="28" width="284" height="184" rx="28" fill={cream} />
      <path d="M58 168h88l18-22h78v22" stroke={blush} strokeWidth="10" strokeLinejoin="round" fill="none" />
      <rect x="70" y="118" width="180" height="52" rx="10" fill={info} />
      <g className="wa-paper">
        <rect x="86" y="72" width="92" height="118" rx="8" fill={paper} stroke={ink} strokeWidth="2.4" transform="rotate(-8 132 131)" />
        <path d="M92 96h48M92 110h40M92 124h36" stroke={soft} strokeWidth="3" strokeLinecap="round" transform="rotate(-8 132 131)" />
      </g>
      <g className="wa-check">
        <circle cx="236" cy="86" r="28" fill={ok} />
        <path d="M224 86l8 8 16-16" stroke={paper} strokeWidth="4" strokeLinecap="round" strokeLinejoin="round" />
      </g>
    </svg>
  );
}

export const WIZARD_STEPS = [
  { key: "model", label: "Model", hint: "Pick one installed model", icon: "cpu" },
  { key: "roles", label: "Roles", hint: "Who this test is for", icon: "users" },
  { key: "think", label: "Thinking", hint: "Off or on for the whole run", icon: "brain" },
  { key: "save", label: "Report", hint: "Where a copy is saved", icon: "folder-open" },
] as const;
