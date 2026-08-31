type Props = {
  thinking: boolean;
  disabled?: boolean;
  onChange: (value: boolean) => void;
};

export function ThinkingToggle({ thinking, disabled, onChange }: Props) {
  return (
    <div>
      <div className="kicker-muted" style={{ marginBottom: 6 }}>
        Model thinking
      </div>
      <div className="segmented" role="radiogroup" aria-label="Model thinking for this benchmark">
        <button
          type="button"
          className={!thinking ? "active" : ""}
          disabled={disabled}
          aria-checked={!thinking}
          role="radio"
          onClick={() => onChange(false)}
        >
          Off
        </button>
        <button
          type="button"
          className={thinking ? "active" : ""}
          disabled={disabled}
          aria-checked={thinking}
          role="radio"
          onClick={() => onChange(true)}
        >
          On
        </button>
      </div>
      <p className="body" style={{ fontSize: 12, margin: "8px 0 0", maxWidth: 260 }}>
        {thinking
          ? "On for the whole run. The model may reason before answering. Slower, still waits until done."
          : "Off for the whole run. The model answers without a thinking pass."}
      </p>
    </div>
  );
}
