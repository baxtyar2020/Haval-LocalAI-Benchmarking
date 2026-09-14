use std::fs::{self, File};
use std::io::{Read, Write};
use std::path::{Path, PathBuf};
use std::sync::Mutex;
use std::time::Duration;

use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};
use tauri::{AppHandle, Emitter, Manager};

use crate::stop_engine;

pub const PUBLIC_HOST: &str = "https://pub-3ecafaa87e184cb58f5f8ab76a9f4648.r2.dev";
pub const LATEST_JSON_URL: &str =
    "https://pub-3ecafaa87e184cb58f5f8ab76a9f4648.r2.dev/havalbencmarkingapp/update/latest.json";
const UPDATE_PATH_PREFIX: &str = "/havalbencmarkingapp/update/";
const DATA_FOLDER: &str = "Haval LocalAI Bench";

#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct LatestManifest {
    pub version: String,
    pub url: String,
    pub sha256: String,
    pub size: u64,
    #[serde(default)]
    pub notes: String,
}

#[derive(Clone, Debug, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct UpdateStatus {
    pub installed: String,
    pub latest: Option<String>,
    pub notes: String,
    pub online: bool,
    pub update_available: bool,
    pub state: String,
    pub message: String,
    pub received: u64,
    pub total: u64,
    pub just_updated: bool,
}

#[derive(Clone, Debug, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct ProgressPayload {
    pub received: u64,
    pub total: u64,
}

struct Inner {
    latest: Option<LatestManifest>,
    state: String,
    message: String,
    online: bool,
    received: u64,
    total: u64,
    just_updated: Option<String>,
}

pub struct UpdateHub {
    inner: Mutex<Inner>,
}

impl UpdateHub {
    pub fn new() -> Self {
        Self {
            inner: Mutex::new(Inner {
                latest: None,
                state: "idle".into(),
                message: String::new(),
                online: true,
                received: 0,
                total: 0,
                just_updated: None,
            }),
        }
    }
}

fn installed_version() -> String {
    env!("CARGO_PKG_VERSION").trim_start_matches('v').to_string()
}

fn data_dir() -> PathBuf {
    let root = std::env::var("LOCALAPPDATA").unwrap_or_else(|_| {
        PathBuf::from(r"C:\Users\Public\AppData\Local")
            .to_string_lossy()
            .into()
    });
    PathBuf::from(root).join(DATA_FOLDER)
}

fn updates_dir() -> PathBuf {
    let path = data_dir().join("updates");
    let _ = fs::create_dir_all(&path);
    path
}

fn parse_semver(raw: &str) -> Option<(u64, u64, u64)> {
    let t = raw.trim().trim_start_matches('v');
    let mut parts = t.split('.');
    let major = parts.next()?.parse().ok()?;
    let minor = parts.next().unwrap_or("0").parse().unwrap_or(0);
    let patch = parts
        .next()
        .unwrap_or("0")
        .split(|c: char| !c.is_ascii_digit())
        .next()
        .unwrap_or("0")
        .parse()
        .unwrap_or(0);
    Some((major, minor, patch))
}

fn remote_newer(remote: &str, local: &str) -> bool {
    match (parse_semver(remote), parse_semver(local)) {
        (Some(r), Some(l)) => r > l,
        _ => false,
    }
}

fn url_allowed(url: &str) -> bool {
    match url.strip_prefix(PUBLIC_HOST) {
        Some(rest) => rest.starts_with(UPDATE_PATH_PREFIX),
        None => false,
    }
}

fn read_install_dir() -> Option<PathBuf> {
    let json_path = data_dir().join("install.json");
    if let Ok(text) = fs::read_to_string(&json_path) {
        if let Ok(v) = serde_json::from_str::<serde_json::Value>(&text) {
            if let Some(dir) = v.get("install_dir").and_then(|x| x.as_str()) {
                if !dir.is_empty() {
                    return Some(PathBuf::from(dir));
                }
            }
        }
    }
    #[cfg(windows)]
    {
        if let Some(dir) = read_reg_install_dir() {
            return Some(dir);
        }
    }
    None
}

#[cfg(windows)]
fn read_reg_install_dir() -> Option<PathBuf> {
    use std::os::windows::process::CommandExt;
    let mut cmd = std::process::Command::new("reg");
    cmd.args([
        "query",
        r"HKCU\Software\Haval\LocalAIBench",
        "/v",
        "InstallDir",
    ])
    .creation_flags(0x0800_0000);
    let out = cmd.output().ok()?;
    let text = String::from_utf8_lossy(&out.stdout);
    for line in text.lines() {
        if let Some(idx) = line.find("REG_SZ") {
            let val = line[idx + 6..].trim();
            if !val.is_empty() {
                return Some(PathBuf::from(val));
            }
        }
    }
    None
}

fn consume_just_updated(hub: &UpdateHub) {
    let path = data_dir().join("just-updated.json");
    if let Ok(text) = fs::read_to_string(&path) {
        if let Ok(v) = serde_json::from_str::<serde_json::Value>(&text) {
            if let Some(ver) = v.get("version").and_then(|x| x.as_str()) {
                if let Ok(mut g) = hub.inner.lock() {
                    g.just_updated = Some(ver.to_string());
                    g.state = "updated".into();
                    g.message = format!("Updated to {ver}.");
                }
            }
        }
        let _ = fs::remove_file(&path);
    }
}

fn snapshot(hub: &UpdateHub) -> UpdateStatus {
    let g = hub.inner.lock().unwrap();
    let installed = installed_version();
    let latest = g.latest.as_ref().map(|m| m.version.clone());
    let notes = g.latest.as_ref().map(|m| m.notes.clone()).unwrap_or_default();
    let update_available = g
        .latest
        .as_ref()
        .map(|m| remote_newer(&m.version, &installed))
        .unwrap_or(false);
    UpdateStatus {
        installed,
        latest,
        notes,
        online: g.online,
        update_available,
        state: g.state.clone(),
        message: g.message.clone(),
        received: g.received,
        total: g.total,
        just_updated: g.just_updated.is_some(),
    }
}

pub fn run_check(app: &AppHandle) {
    let Some(hub) = app.try_state::<UpdateHub>() else {
        return;
    };
    consume_just_updated(&hub);
    {
        let mut g = hub.inner.lock().unwrap();
        if g.state == "downloading" || g.state == "applying" {
            return;
        }
        g.state = "checking".into();
    }
    let agent = ureq::AgentBuilder::new()
        .timeout(Duration::from_secs(8))
        .build();
    match agent.get(LATEST_JSON_URL).call() {
        Ok(resp) => {
            let text = resp.into_string().unwrap_or_default();
            match serde_json::from_str::<LatestManifest>(&text) {
                Ok(manifest) => {
                    if !url_allowed(&manifest.url) {
                        let mut g = hub.inner.lock().unwrap();
                        g.online = true;
                        g.state = "failed".into();
                        g.message = "Could not check for updates.".into();
                        return;
                    }
                    let newer = remote_newer(&manifest.version, &installed_version());
                    let mut g = hub.inner.lock().unwrap();
                    g.latest = Some(manifest.clone());
                    g.online = true;
                    if g.just_updated.is_some() {
                        g.state = "updated".into();
                    } else if newer {
                        g.state = "available".into();
                        g.message = format!(
                            "Version {} is available. Open Settings → Update.",
                            manifest.version
                        );
                    } else {
                        g.state = "idle".into();
                        g.message.clear();
                    }
                }
                Err(_) => {
                    let mut g = hub.inner.lock().unwrap();
                    g.online = true;
                    g.state = "failed".into();
                    g.message = "Could not check for updates.".into();
                }
            }
        }
        Err(ureq::Error::Status(404, _)) => {
            let mut g = hub.inner.lock().unwrap();
            g.online = true;
            g.latest = None;
            if g.just_updated.is_none() {
                g.state = "idle".into();
                g.message.clear();
            }
        }
        Err(err) => {
            let offline = matches!(
                err,
                ureq::Error::Transport(_)
            );
            let mut g = hub.inner.lock().unwrap();
            g.online = !offline;
            if g.just_updated.is_none() {
                g.state = if offline { "offline" } else { "failed" }.into();
                g.message = if offline {
                    "No internet — could not check for updates.".into()
                } else {
                    "Could not check for updates.".into()
                };
            }
        }
    }
}

fn hex_sha256(path: &Path) -> Result<String, String> {
    let mut file = File::open(path).map_err(|e| e.to_string())?;
    let mut hasher = Sha256::new();
    let mut buf = [0u8; 64 * 1024];
    loop {
        let n = file.read(&mut buf).map_err(|e| e.to_string())?;
        if n == 0 {
            break;
        }
        hasher.update(&buf[..n]);
    }
    Ok(format!("{:x}", hasher.finalize()))
}

#[tauri::command]
pub fn update_status(app: AppHandle) -> UpdateStatus {
    let Some(hub) = app.try_state::<UpdateHub>() else {
        return UpdateStatus {
            installed: installed_version(),
            latest: None,
            notes: String::new(),
            online: true,
            update_available: false,
            state: "idle".into(),
            message: String::new(),
            received: 0,
            total: 0,
            just_updated: false,
        };
    };
    consume_just_updated(&hub);
    snapshot(&hub)
}

#[tauri::command]
pub fn update_check(app: AppHandle) -> UpdateStatus {
    run_check(&app);
    update_status(app)
}

#[tauri::command]
pub fn update_download(app: AppHandle) -> Result<UpdateStatus, String> {
    let hub = app
        .try_state::<UpdateHub>()
        .ok_or_else(|| "Update service is not ready.".to_string())?;
    let manifest = {
        let g = hub.inner.lock().unwrap();
        g.latest.clone()
    }
    .ok_or_else(|| "Could not check for updates.".to_string())?;
    if !url_allowed(&manifest.url) {
        return Err("Could not check for updates.".into());
    }
    if !remote_newer(&manifest.version, &installed_version()) {
        return Err("This PC already has the latest version.".into());
    }
    {
        let mut g = hub.inner.lock().unwrap();
        g.state = "downloading".into();
        g.message = "Downloading 0%".into();
        g.received = 0;
        g.total = manifest.size;
    }
    let dest = updates_dir().join(format!(
        "HavalLocalAIBench-{}-setup.exe",
        manifest.version
    ));
    let agent = ureq::AgentBuilder::new()
        .timeout_read(Duration::from_secs(600))
        .timeout_connect(Duration::from_secs(20))
        .build();
    let resp = agent
        .get(&manifest.url)
        .call()
        .map_err(|_| "Download failed. Try again.".to_string())?;
    let total = resp
        .header("Content-Length")
        .and_then(|s| s.parse().ok())
        .unwrap_or(manifest.size);
    {
        let mut g = hub.inner.lock().unwrap();
        g.total = total;
    }
    let mut reader = resp.into_reader();
    let mut file = File::create(&dest).map_err(|e| e.to_string())?;
    let mut buf = [0u8; 64 * 1024];
    let mut received = 0u64;
    let mut hasher = Sha256::new();
    loop {
        let n = reader.read(&mut buf).map_err(|_| "Download failed. Try again.".to_string())?;
        if n == 0 {
            break;
        }
        file.write_all(&buf[..n])
            .map_err(|_| "Download failed. Try again.".to_string())?;
        hasher.update(&buf[..n]);
        received += n as u64;
        {
            let mut g = hub.inner.lock().unwrap();
            g.received = received;
            g.total = total;
            let pct = if total > 0 {
                (100 * received / total).min(100)
            } else {
                0
            };
            g.message = format!("Downloading {pct}%");
        }
        let _ = app.emit(
            "update://progress",
            ProgressPayload {
                received,
                total,
            },
        );
    }
    drop(file);
    let digest = format!("{:x}", hasher.finalize());
    let expect = manifest.sha256.trim().to_ascii_lowercase();
    if digest != expect {
        let _ = fs::remove_file(&dest);
        let mut g = hub.inner.lock().unwrap();
        g.state = "failed".into();
        g.message = "Download failed. Try again.".into();
        return Err("Download failed. Try again.".into());
    }
    {
        let mut g = hub.inner.lock().unwrap();
        g.state = "ready".into();
        g.message = "Download complete.".into();
        g.received = received;
    }
    Ok(snapshot(&hub))
}

#[tauri::command]
pub fn update_apply(app: AppHandle) -> Result<(), String> {
    let hub = app
        .try_state::<UpdateHub>()
        .ok_or_else(|| "Update service is not ready.".to_string())?;
    let manifest = {
        let g = hub.inner.lock().unwrap();
        g.latest.clone()
    }
    .ok_or_else(|| "Could not check for updates.".to_string())?;
    let setup = updates_dir().join(format!(
        "HavalLocalAIBench-{}-setup.exe",
        manifest.version
    ));
    if !setup.is_file() {
        return Err("Download failed. Try again.".into());
    }
    let got = hex_sha256(&setup)?;
    if got != manifest.sha256.trim().to_ascii_lowercase() {
        let _ = fs::remove_file(&setup);
        let mut g = hub.inner.lock().unwrap();
        g.state = "failed".into();
        g.message = "Download failed. Try again.".into();
        return Err("Download failed. Try again.".into());
    }
    let install_dir = read_install_dir()
        .or_else(|| {
            std::env::current_exe()
                .ok()
                .and_then(|p| p.parent().map(|d| d.to_path_buf()))
        })
        .ok_or_else(|| "Could not find the install folder.".to_string())?;
    {
        let mut g = hub.inner.lock().unwrap();
        g.state = "applying".into();
        g.message = "Installer starting. This window will close.".into();
    }
    stop_engine(&app);
    spawn_updater(&setup, &install_dir)?;
    let handle = app.clone();
    std::thread::spawn(move || {
        std::thread::sleep(Duration::from_millis(800));
        handle.exit(0);
    });
    Ok(())
}

fn spawn_updater(setup: &Path, install_dir: &Path) -> Result<(), String> {
    let dir = install_dir.to_string_lossy().trim_end_matches(['\\', '/']).to_string();
    let mut cmd = std::process::Command::new(setup);
    #[cfg(windows)]
    {
        use std::os::windows::process::CommandExt;
        cmd.raw_arg("/UPDATE");
        cmd.raw_arg(format!("/D={dir}"));
        let _ = cmd.creation_flags(0);
    }
    #[cfg(not(windows))]
    {
        cmd.args(["/UPDATE", &format!("/D={dir}")]);
    }
    cmd.spawn()
        .map(|_| ())
        .map_err(|e| format!("Could not start the installer: {e}"))
}
