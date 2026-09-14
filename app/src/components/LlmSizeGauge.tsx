export function LlmSizeGauge() {
  return (
    <div className="llm-gauge" aria-hidden>
      <div className="llm-gauge-wrap">
        <svg width="360" height="230" viewBox="0 0 360 230">
          <defs>
            <linearGradient id="gaugegrad" gradientUnits="userSpaceOnUse" x1="40" y1="0" x2="320" y2="0">
              <stop offset="0" stopColor="#2f6b1f" />
              <stop offset="0.22" stopColor="#5a9636" />
              <stop offset="0.42" stopColor="#8bb43f" />
              <stop offset="0.58" stopColor="#c2bd38" />
              <stop offset="0.72" stopColor="#e2a92f" />
              <stop offset="0.86" stopColor="#dd7623" />
              <stop offset="1" stopColor="#d0381b" />
            </linearGradient>
          </defs>
          <path d="M40 200 A 140 140 0 0 1 320 200" fill="none" stroke="var(--divider)" strokeWidth="20" strokeLinecap="round" />
          <path
            className="llm-gauge-arc"
            d="M40 200 A 140 140 0 0 1 320 200"
            fill="none"
            stroke="url(#gaugegrad)"
            strokeWidth="20"
            strokeLinecap="round"
            strokeDasharray="440"
          />
          <g stroke="var(--muted)" strokeWidth="2.5" strokeLinecap="round">
            <path d="M40 200 l14 -3" />
            <path d="M80 116 l13 6" />
            <path d="M180 60 v14" />
            <path d="M280 116 l-13 6" />
            <path d="M320 200 l-14 -3" />
          </g>
          <g className="llm-gauge-needle">
            <path d="M180 200 L180 74" stroke="var(--accent)" strokeWidth="6" strokeLinecap="round" />
          </g>
          <circle cx="180" cy="200" r="12" fill="var(--accent)" />
          <circle cx="180" cy="200" r="5" fill="var(--bg)" />
        </svg>
        <div className="llm-gauge-tick llm-gauge-tick-10">10B</div>
        <div className="llm-gauge-tick llm-gauge-tick-50">50B</div>
        <div className="llm-gauge-tick llm-gauge-tick-70">70B</div>
        <div className="llm-gauge-tick llm-gauge-tick-200">200B</div>
      </div>
      <div className="llm-gauge-label">LLM Size</div>
    </div>
  );
}
