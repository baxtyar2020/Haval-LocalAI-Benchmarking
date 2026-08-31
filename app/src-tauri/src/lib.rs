use serde::Serialize;
use std::net::{SocketAddr, TcpStream};
use std::path::{Path, PathBuf};
use std::process::{Child, Command, Stdio};
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::Mutex;
use std::thread;
use std::time::{Duration, Instant, SystemTime, UNIX_EPOCH};

use tauri::{AppHandle, Manager, RunEvent, State};

#[cfg(windows)]
const CREATE_NO_WINDOW: u32 = 0x0800_0000;

static SHUTTING_DOWN: AtomicBool = AtomicBool::new(false);

#[derive(Clone, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct EngineInfo {
    pub url: String,
    pub token: String,
    pub ready: bool,
    pub error: Option<String>,
}

#[derive(Clone)]
struct SpawnSpec {
    python: PathBuf,
    engine_dir: PathBuf,
    repo_root: PathBuf,
    port: u16,
    token: String,
}

pub struct EngineProcess {
    info: Mutex<EngineInfo>,
    spec: Mutex<Option<SpawnSpec>>,
    child: Mutex<Option<Child>>,
}

fn random_token() -> String {
    let nanos = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap_or_default()
        .as_nanos();
    format!("{:032x}{:016x}", nanos, u128::from(std::process::id()) * 0x9E37)
}

fn pick_port() -> u16 {
    std::net::TcpListener::bind("127.0.0.1:0")
        .ok()
        .and_then(|l| l.local_addr().ok())
        .map(|a| a.port())
        .unwrap_or(8765)
}

fn cargo_repo_root() -> PathBuf {
    Path::new(env!("CARGO_MANIFEST_DIR"))
        .join("../..")
        .canonicalize()
        .unwrap_or_else(|_| PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("../.."))
}

fn hide_window(cmd: &mut Command) {
    #[cfg(windows)]
    {
        use std::os::windows::process::CommandExt;
        cmd.creation_flags(CREATE_NO_WINDOW);
    }
    let _ = cmd;
}

fn python_available(cmd: &str) -> bool {
    let mut c = Command::new(cmd);
    c.arg("--version");
    hide_window(&mut c);
    c.stdout(Stdio::null())
        .stderr(Stdio::null())
        .status()
        .map(|s| s.success())
        .unwrap_or(false)
}

fn find_python(search_roots: &[PathBuf]) -> Option<PathBuf> {
    for root in search_roots {
        for rel in ["python/python.exe", "python-embed/python.exe"] {
            let candidate = root.join(rel);
            if candidate.is_file() {
                return Some(candidate);
            }
        }
    }
    if let Ok(exe) = std::env::current_exe() {
        if let Some(dir) = exe.parent() {
            let beside = dir.join("python").join("python.exe");
            if beside.is_file() {
                return Some(beside);
            }
        }
    }
    ["python", "py"]
        .into_iter()
        .find(|cmd| python_available(cmd))
        .map(PathBuf::from)
}

fn collect_roots(resource: &Path) -> Vec<PathBuf> {
    let mut roots: Vec<PathBuf> = Vec::new();
    let mut push = |p: PathBuf| {
        if p.exists() && !roots.iter().any(|e| e == &p) {
            roots.push(p);
        }
    };
    push(resource.to_path_buf());
    if let Ok(exe) = std::env::current_exe() {
        if let Some(dir) = exe.parent() {
            push(dir.to_path_buf());
        }
    }
    let mut cur = resource.to_path_buf();
    for _ in 0..5 {
        let up = cur.join("_up_");
        if up.is_dir() {
            push(up.clone());
            cur = up;
        } else {
            break;
        }
    }
    push(cargo_repo_root());
    roots
}

fn engine_layout(base: &Path) -> Option<(PathBuf, PathBuf)> {
    for root in collect_roots(base) {
        if root.join("engine").join("haval_engine").is_dir() && root.join("config").is_dir() {
            return Some((root.join("engine"), root));
        }
        if root.join("haval_engine").is_dir() && root.join("config").is_dir() {
            return Some((root.clone(), root));
        }
    }
    None
}

fn wait_for_port(port: u16) -> bool {
    wait_for_port_for(port, Duration::from_secs(20))
}

fn wait_for_port_for(port: u16, timeout: Duration) -> bool {
    let addr = SocketAddr::from(([127, 0, 0, 1], port));
    let deadline = Instant::now() + timeout;
    while Instant::now() < deadline {
        if TcpStream::connect_timeout(&addr, Duration::from_millis(80)).is_ok() {
            return true;
        }
        thread::sleep(Duration::from_millis(40));
    }
    false
}

fn engine_stderr() -> Stdio {
    let path = std::env::var("LOCALAPPDATA").ok().map(|p| {
        PathBuf::from(p)
            .join("Haval LocalAI Bench")
            .join("engine-stderr.log")
    });
    if let Some(path) = path {
        if let Some(parent) = path.parent() {
            let _ = std::fs::create_dir_all(parent);
        }
        if let Ok(file) = std::fs::OpenOptions::new()
            .create(true)
            .append(true)
            .open(&path)
        {
            return Stdio::from(file);
        }
    }
    Stdio::null()
}

fn spawn_child(spec: &SpawnSpec) -> Option<Child> {
    // Embeddable CPython ships a ._pth file, which ignores PYTHONPATH.
    // Inject the engine directory on sys.path so `haval_engine` always imports.
    let engine_dir = spec.engine_dir.to_string_lossy().replace('\\', "/");
    let boot = format!(
        "import sys; p=r'''{engine_dir}''';\n\
sys.path.insert(0, p) if p not in sys.path else None;\n\
from haval_engine.__main__ import main;\n\
main()"
    );
    let mut cmd = Command::new(&spec.python);
    cmd.current_dir(&spec.engine_dir)
        .env("HAVAL_ENGINE_HOST", "127.0.0.1")
        .env("HAVAL_ENGINE_PORT", spec.port.to_string())
        .env("HAVAL_ENGINE_TOKEN", &spec.token)
        .env("PYTHONPATH", &spec.engine_dir)
        .env("HAVAL_REPO_ROOT", &spec.repo_root)
        .env("HAVAL_CONFIG_DIR", spec.repo_root.join("config"))
        .args(["-c", &boot])
        .stdin(Stdio::null())
        .stdout(Stdio::null())
        .stderr(engine_stderr());
    hide_window(&mut cmd);
    cmd.spawn().ok()
}

fn spawn_engine(base: &Path) -> (Option<Child>, EngineInfo, Option<SpawnSpec>) {
    let roots = collect_roots(base);
    let python = match find_python(&roots) {
        Some(p) => p,
        None => {
            return (
                None,
                EngineInfo {
                    url: String::new(),
                    token: String::new(),
                    ready: false,
                    error: Some("Python was not found on this PC. Place python-embed next to the app or install Python 3.".into()),
                },
                None,
            )
        }
    };

    let Some((engine_dir, repo)) = engine_layout(base) else {
        return (
            None,
            EngineInfo {
                url: String::new(),
                token: String::new(),
                ready: false,
                error: Some(format!(
                    "Engine package missing under {}",
                    base.display()
                )),
            },
            None,
        );
    };

    let port = pick_port();
    let token = random_token();
    let url = format!("http://127.0.0.1:{port}");
    let spec = SpawnSpec {
        python,
        engine_dir,
        repo_root: repo,
        port,
        token: token.clone(),
    };

    match spawn_child(&spec) {
        Some(child) => {
            let ready = wait_for_port(port);
            (
                Some(child),
                EngineInfo {
                    url,
                    token,
                    ready,
                    error: if ready {
                        None
                    } else {
                        Some("Bench Engine started but is not answering yet.".into())
                    },
                },
                Some(spec),
            )
        }
        None => (
            None,
            EngineInfo {
                url: String::new(),
                token: String::new(),
                ready: false,
                error: Some("Failed to start Bench Engine.".into()),
            },
            Some(spec),
        ),
    }
}

fn start_watchdog(app: AppHandle) {
    thread::spawn(move || loop {
        thread::sleep(Duration::from_secs(3));
        if SHUTTING_DOWN.load(Ordering::SeqCst) {
            break;
        }
        let Some(state) = app.try_state::<EngineProcess>() else {
            continue;
        };
        let Some(spec) = state.spec.lock().ok().and_then(|g| g.clone()) else {
            continue;
        };
        let dead = {
            let mut child = match state.child.lock() {
                Ok(g) => g,
                Err(_) => continue,
            };
            match child.as_mut() {
                Some(c) => match c.try_wait() {
                    Ok(Some(_)) => {
                        let _ = child.take();
                        true
                    }
                    _ => false,
                },
                None => false,
            }
        };
        if !dead || SHUTTING_DOWN.load(Ordering::SeqCst) {
            continue;
        }
        if let Some(new_child) = spawn_child(&spec) {
            let _ = wait_for_port(spec.port);
            if let Ok(mut slot) = state.child.lock() {
                *slot = Some(new_child);
            }
        } else {
            thread::sleep(Duration::from_secs(10));
        }
    });
}

#[tauri::command]
fn engine_info(state: State<EngineProcess>) -> EngineInfo {
    state
        .info
        .lock()
        .map(|g| g.clone())
        .unwrap_or_else(|e| e.into_inner().clone())
}

/// Proxy UI → bench engine so WebView CORS cannot block Doctor.
#[tauri::command]
fn engine_request(
    state: State<EngineProcess>,
    method: String,
    path: String,
    body: Option<String>,
) -> Result<String, String> {
    let info = state
        .info
        .lock()
        .map(|g| g.clone())
        .unwrap_or_else(|e| e.into_inner().clone());
    if info.url.is_empty() || info.token.is_empty() {
        return Err(info
            .error
            .unwrap_or_else(|| "The Bench Engine is still starting.".into()));
    }
    let url = format!("{}{}", info.url, path);
    let auth = format!("Bearer {}", info.token);
    let result = if method.eq_ignore_ascii_case("POST") {
        ureq::post(&url)
            .set("Authorization", &auth)
            .set("Content-Type", "application/json")
            .timeout(Duration::from_secs(30))
            .send_string(body.as_deref().unwrap_or("{}"))
    } else {
        ureq::get(&url)
            .set("Authorization", &auth)
            .timeout(Duration::from_secs(30))
            .call()
    };
    match result {
        Ok(resp) => resp.into_string().map_err(|e| e.to_string()),
        Err(ureq::Error::Status(_, resp)) => {
            let status = resp.status();
            let text = resp.into_string().unwrap_or_default();
            Err(format!("Engine HTTP {status}: {text}"))
        }
        Err(e) => Err(e.to_string()),
    }
}

#[tauri::command]
fn pick_report_folder() -> Option<String> {
    rfd::FileDialog::new()
        .set_title("Choose where to save the benchmark report")
        .pick_folder()
        .map(|p| p.to_string_lossy().into_owned())
}

/// Open a file or folder with the OS default app (HTML → default browser).
/// Bypasses the webview popup blocker and the opener-plugin path allowlist.
#[tauri::command]
fn open_with_os(path: String) -> Result<(), String> {
    let p = PathBuf::from(&path);
    if !p.exists() {
        return Err(format!("Nothing to open at {path}"));
    }
    #[cfg(windows)]
    {
        let mut cmd = if p.is_dir() {
            let mut c = Command::new("explorer");
            c.arg(&path);
            c
        } else {
            // `start` treats the first quoted argument as a window title.
            // Do not hide this process — CREATE_NO_WINDOW can prevent the browser from launching.
            let mut c = Command::new("cmd");
            c.args(["/C", "start", "", &path]);
            c
        };
        let status = cmd.status().map_err(|e| e.to_string())?;
        if !status.success() {
            return Err("Windows could not open that path.".into());
        }
        Ok(())
    }
    #[cfg(not(windows))]
    {
        Command::new("xdg-open")
            .arg(&path)
            .status()
            .map_err(|e| e.to_string())
            .and_then(|s| {
                if s.success() {
                    Ok(())
                } else {
                    Err("Could not open that path.".into())
                }
            })
    }
}

fn engine_base(app: &AppHandle) -> PathBuf {
    let repo = cargo_repo_root();
    if repo.join("engine").join("haval_engine").is_dir() && repo.join("config").is_dir() {
        return repo;
    }
    app.path()
        .resource_dir()
        .unwrap_or(repo)
}

fn restart_engine_inner(app: &AppHandle) -> EngineInfo {
    let Some(state) = app.try_state::<EngineProcess>() else {
        return EngineInfo {
            url: String::new(),
            token: String::new(),
            ready: false,
            error: Some("The app could not reach the engine supervisor.".into()),
        };
    };
    if let Ok(mut child) = state.child.lock() {
        if let Some(mut c) = child.take() {
            let _ = c.kill();
            let _ = c.wait();
        }
    }
    let base = engine_base(app);
    let (child, info, spec) = spawn_engine(&base);
    if let Ok(mut g) = state.info.lock() {
        *g = info.clone();
    }
    if let Ok(mut g) = state.spec.lock() {
        *g = spec;
    }
    if let Ok(mut g) = state.child.lock() {
        *g = child;
    }
    info
}

#[tauri::command]
fn restart_engine(app: AppHandle) -> EngineInfo {
    restart_engine_inner(&app)
}

fn stop_engine(app: &AppHandle) {
    SHUTTING_DOWN.store(true, Ordering::SeqCst);
    if let Some(state) = app.try_state::<EngineProcess>() {
        if let Ok(mut child) = state.child.lock() {
            if let Some(mut c) = child.take() {
                let _ = c.kill();
                let _ = c.wait();
            }
        }
    }
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .setup(move |app| {
            app.manage(EngineProcess {
                info: Mutex::new(EngineInfo {
                    url: String::new(),
                    token: String::new(),
                    ready: false,
                    error: Some("Starting the bench engine…".into()),
                }),
                spec: Mutex::new(None),
                child: Mutex::new(None),
            });
            let handle = app.handle().clone();
            let base = engine_base(app.handle());
            thread::spawn(move || {
                let info = {
                    let (child, info, spec) = spawn_engine(&base);
                    let Some(state) = handle.try_state::<EngineProcess>() else {
                        return;
                    };
                    if let Ok(mut g) = state.info.lock() {
                        *g = info.clone();
                    };
                    if let Ok(mut g) = state.spec.lock() {
                        *g = spec;
                    };
                    if let Ok(mut g) = state.child.lock() {
                        *g = child;
                    };
                    info
                };
                let _ = info;
            });
            start_watchdog(app.handle().clone());
            if let Some(window) = app.get_webview_window("main") {
                let _ = window.center();
                let _ = window.show();
                let _ = window.set_focus();
            }
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![
            engine_info,
            engine_request,
            restart_engine,
            pick_report_folder,
            open_with_os
        ])
        .build(tauri::generate_context!())
        .expect("error while building tauri application")
        .run(|app, event| {
            if matches!(event, RunEvent::Exit | RunEvent::ExitRequested { .. }) {
                stop_engine(app);
            }
        });
}
