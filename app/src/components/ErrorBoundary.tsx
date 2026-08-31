import { Component, type ErrorInfo, type ReactNode } from "react";

type Props = { children: ReactNode };
type State = { message: string | null };

export class ErrorBoundary extends Component<Props, State> {
  state: State = { message: null };

  static getDerivedStateFromError(error: Error): State {
    return { message: error.message || "Something went wrong." };
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error(error, info.componentStack);
  }

  render() {
    if (this.state.message) {
      return (
        <div className="page" style={{ maxWidth: 640, padding: 40 }}>
          <div className="kicker" style={{ marginBottom: 10 }}>
            Application error
          </div>
          <h1 className="page-title" style={{ margin: "0 0 12px" }}>
            The window hit a display error
          </h1>
          <p className="body" style={{ marginBottom: 16 }}>
            Your benchmark data on disk was not changed. Close and reopen the app. If it keeps happening, send{" "}
            <code>%LOCALAPPDATA%\Haval LocalAI Bench\support.log</code> to support.
          </p>
          <p className="body" style={{ color: "var(--ink-soft)", fontSize: 13 }}>
            {this.state.message}
          </p>
          <button className="btn secondary" style={{ marginTop: 20 }} onClick={() => window.location.reload()}>
            Reload
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}
