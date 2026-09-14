import { useEffect } from "react";
import { Icon } from "./Icon";

type Props = {
  count: number;
  busy?: boolean;
  onCancel: () => void;
  onConfirm: () => void;
};

export function ConfirmDelete({ count, busy, onCancel, onConfirm }: Props) {
  const many = count !== 1;
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape" && !busy) onCancel();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [busy, onCancel]);
  return (
    <div
      className="confirm-scrim"
      role="presentation"
      onClick={() => {
        if (!busy) onCancel();
      }}
    >
      <div
        className="confirm-card"
        role="dialog"
        aria-modal="true"
        aria-labelledby="confirm-delete-title"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="confirm-icon" aria-hidden>
          <Icon name="trash" size={22} />
        </div>
        <div className="kicker">Delete {many ? "reports" : "report"}</div>
        <h2 id="confirm-delete-title">This will completely remove and delete {many ? "these reports" : "this report"} on your machine.</h2>
        <p>Are you sure? HTML, folders, and every saved file for {many ? "the selected reports" : "this report"} leave this PC. This cannot be undone.</p>
        <div className="confirm-actions">
          <button className="btn secondary" type="button" onClick={onCancel} disabled={busy}>
            Cancel
          </button>
          <button className="btn danger" type="button" onClick={onConfirm} disabled={busy}>
            <Icon name="trash" size={15} />
            {busy ? "Deleting…" : "Delete"}
          </button>
        </div>
      </div>
    </div>
  );
}
