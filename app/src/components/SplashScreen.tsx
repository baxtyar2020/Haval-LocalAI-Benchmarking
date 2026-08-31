import splashPhoto from "../assets/splashscreen.png";
import type { DoctorSnapshot } from "../types";

type Props = {
  snapshot: DoctorSnapshot | null;
  waitingForEngine: boolean;
};

function progressFrom(snapshot: DoctorSnapshot | null, waitingForEngine: boolean): { pct: number; label: string } {
  if (waitingForEngine && !snapshot?.checks?.length) {
    return { pct: 8, label: "Starting the bench engine…" };
  }
  const checks = snapshot?.checks || [];
  if (!checks.length) {
    return { pct: 12, label: "Doctor is inspecting this PC…" };
  }
  const settled = checks.filter((c) => c.status !== "checking" && c.status !== "repairing").length;
  const pct = Math.max(8, Math.round((settled / checks.length) * 100));
  const current = checks.find((c) => c.status === "checking" || c.status === "repairing");
  if (snapshot?.state === "repairing") {
    return { pct, label: current?.title ? `Repairing: ${current.title}` : "Repairing automatically…" };
  }
  if (current) {
    return { pct, label: `Checking: ${current.title}` };
  }
  return { pct: Math.max(pct, 92), label: snapshot?.subtitle || "Finishing Doctor…" };
}

export function SplashScreen({ snapshot, waitingForEngine }: Props) {
  const { pct, label } = progressFrom(snapshot, waitingForEngine);
  return (
    <div className="splash" role="status" aria-live="polite" aria-busy="true" aria-label="Opening Haval LocalAI Benchmarking">
      <div className="splash-photo-wrap">
        <img className="splash-photo" src={splashPhoto} alt="" />
        <div className="splash-photo-veil" />
      </div>
      <div className="splash-card">
        <div className="splash-card-shine" aria-hidden="true" />
        <div className="splash-kicker">Haval LocalAI Benchmarking</div>
        <h1 className="splash-title">Preparing your PC</h1>
        <p className="splash-copy">Doctor is confirming Windows, Ollama, storage, and acceleration before you start.</p>
      </div>
      <div className="splash-footer">
        <div className="splash-progress-label">{label}</div>
        <div className="splash-progress" role="progressbar" aria-valuemin={0} aria-valuemax={100} aria-valuenow={pct} aria-label={label}>
          <div className="splash-progress-fill" style={{ width: `${pct}%` }} />
        </div>
      </div>
    </div>
  );
}
