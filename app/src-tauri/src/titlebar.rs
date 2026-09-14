//! Windows 11 caption / border colors follow the in-app theme (Haval cream by default).

use tauri::WebviewWindow;

const DWMWA_USE_IMMERSIVE_DARK_MODE: u32 = 20;
const DWMWA_BORDER_COLOR: u32 = 34;
const DWMWA_CAPTION_COLOR: u32 = 35;
const DWMWA_TEXT_COLOR: u32 = 36;

const DEFAULT_BG: &str = "#fbf0de";
const DEFAULT_FG: &str = "#201e1d";

#[cfg(windows)]
#[link(name = "dwmapi")]
extern "system" {
    fn DwmSetWindowAttribute(
        hwnd: isize,
        attr: u32,
        value: *const std::ffi::c_void,
        size: u32,
    ) -> i32;
}

fn colorref(hex: &str) -> Option<u32> {
    let h = hex.trim().trim_start_matches('#');
    if h.len() != 6 {
        return None;
    }
    let r = u8::from_str_radix(&h[0..2], 16).ok()?;
    let g = u8::from_str_radix(&h[2..4], 16).ok()?;
    let b = u8::from_str_radix(&h[4..6], 16).ok()?;
    Some(u32::from(r) | (u32::from(g) << 8) | (u32::from(b) << 16))
}

#[cfg(windows)]
fn hwnd_of(window: &WebviewWindow) -> Option<isize> {
    window.hwnd().ok().map(|h| h.0 as isize)
}

#[cfg(windows)]
fn set_attr(hwnd: isize, attr: u32, value: u32) {
    unsafe {
        let _ = DwmSetWindowAttribute(hwnd, attr, &value as *const u32 as *const _, 4);
    }
}

#[cfg(windows)]
pub fn apply_to_window(window: &WebviewWindow, background: &str, foreground: &str) {
    let Some(hwnd) = hwnd_of(window) else {
        return;
    };
    let caption = colorref(background).or_else(|| colorref(DEFAULT_BG)).unwrap_or(0x00d8eaf5);
    let text = colorref(foreground).or_else(|| colorref(DEFAULT_FG)).unwrap_or(0x001d1e20);
    set_attr(hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE, 0);
    set_attr(hwnd, DWMWA_CAPTION_COLOR, caption);
    set_attr(hwnd, DWMWA_BORDER_COLOR, caption);
    set_attr(hwnd, DWMWA_TEXT_COLOR, text);
}

#[cfg(not(windows))]
pub fn apply_to_window(_window: &WebviewWindow, _background: &str, _foreground: &str) {}

pub fn apply_default(window: &WebviewWindow) {
    apply_to_window(window, DEFAULT_BG, DEFAULT_FG);
}

#[tauri::command]
pub fn set_titlebar_theme(window: WebviewWindow, background: String, foreground: String) {
    apply_to_window(&window, &background, &foreground);
}
