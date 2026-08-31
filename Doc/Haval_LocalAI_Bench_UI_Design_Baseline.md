# Haval LocalAI Bench

## Windows Application UI Design Baseline

**Purpose:** Define a simple, intuitive, and implementation-ready visual baseline for the Haval LocalAI Bench Windows 11 desktop application.

**Visual source:** [HavalOthman.com](https://havalothman.com/)

**Design direction:** Preserve the warmth, editorial character, and burnt-orange identity of the website while giving the application the quiet elegance, precision, clarity, and refined interaction associated with premium Apple-style product design.

This is a Windows application, not a website replica and not a macOS imitation. It should feel native to Windows 11 while sharing the same visual family as HavalOthman.com.

---

## 1. Design Vision

The application should feel:

- Elegant but not decorative.
- Warm rather than clinical.
- Premium but approachable.
- Powerful without appearing complicated.
- Calm during long-running operations.
- Consistent across setup, model downloads, benchmarking, and reports.

The interface should make local AI benchmarking feel understandable and safe, even when the underlying work involves services, drivers, GPU acceleration, large downloads, and technical diagnostics.

The customer should always know:

1. Where they are.
2. What the application is doing.
3. Whether everything is healthy.
4. What action is available next.
5. What happened if something failed.

---

## 2. Core Design Principles

### 2.1 Simplicity first

Show the most important information first. Hide advanced technical details behind **View details**, **Advanced**, or expandable sections.

Do not place logs, environment variables, terminal output, and support data in the primary customer view.

### 2.2 One clear primary action

Each screen should have one visually dominant next action, such as:

- Repair
- Download
- Continue
- Start Benchmark
- Open Report

Secondary actions must be quieter.

### 2.3 Calm visual hierarchy

Use whitespace, typography, alignment, and contrast before adding borders, colors, dividers, or containers.

### 2.4 Progressive disclosure

Start with a short status or recommendation. Let customers reveal technical explanations only when needed.

### 2.5 Immediate feedback

Every click must produce an immediate visible response. Downloads, probes, repairs, and benchmarks must show stable progress rather than appearing frozen.

### 2.6 Human language

Prefer:

> Ollama is ready

Instead of:

> API endpoint 127.0.0.1:11434 returned HTTP 200

Technical details may appear in an expandable support panel.

### 2.7 Restraint

Avoid visual noise, excessive gradients, glowing effects, heavy shadows, oversized icons, dense dashboards, and too many simultaneous accent colors.

---

## 3. Visual Identity from HavalOthman.com

The website establishes the following visual language:

- Warm ivory background rather than pure white.
- Paper-like cream surfaces for cards.
- Deep charcoal text rather than pure black.
- Burnt orange as the signature accent.
- Fraunces-style editorial serif for expressive headings.
- Inter-style sans-serif for navigation, body copy, controls, and metadata.
- Fine warm-gray borders.
- Rounded cards with subtle shadows.
- Generous horizontal and vertical spacing.
- Small uppercase category labels with wide letter spacing.
- Pill-shaped primary buttons.
- Black-and-white or restrained imagery framed by the orange identity color.

The Windows application must reuse these qualities consistently.

---

## 4. Color System

### 4.1 Core brand colors

| Token | Hex | Use |
|---|---:|---|
| `Canvas` | `#F6F1E9` | Main application background |
| `Surface` | `#FBF7EF` | Cards, panels, dialogs, menus |
| `Border` | `#E6DFD3` | Dividers, card outlines, input borders |
| `Ink` | `#1A1A1A` | Primary text and high-emphasis icons |
| `Ink Soft` | `#4A4540` | Secondary text and descriptions |
| `Accent` | `#DB4F1B` | Primary actions, active states, progress, brand moments |
| `Accent Soft` | `#F4DCD0` | Selected rows, subtle highlights, informational accent backgrounds |
| `On Accent` | `#F6F1E9` | Text and icons on accent-filled controls |

### 4.2 Accessible accent use

The signature orange should not be used for long paragraphs or small low-weight text on the ivory background.

Use it for:

- Primary buttons.
- Selected tabs.
- Progress bars.
- Active icons.
- Large headings or short emphasis.
- Focus indicators.

For small orange text that requires stronger contrast, use a darker accessible accent such as:

| Token | Hex | Use |
|---|---:|---|
| `Accent Text` | `#A83B15` | Small links, labels, and text on light backgrounds |
| `Accent Hover` | `#C54518` | Primary-button hover and pressed emphasis |

### 4.3 Semantic colors

Semantic status colors must be used sparingly and never replace a written status label.

| Status | Color | Soft background |
|---|---:|---:|
| Success | `#287653` | `#DDEDE5` |
| Warning | `#A76000` | `#F7E8C8` |
| Error | `#B42318` | `#F8DFDC` |
| Information | `#456A87` | `#E1EAF0` |
| Neutral | `#625D57` | `#ECE6DD` |

Every status must combine color with an icon and text, for example: **Ready**, **Needs attention**, or **Download failed**.

### 4.4 Color rules

- Do not use pure white as the main canvas.
- Do not use pure black for large UI regions.
- Do not create rainbow-colored dashboards.
- Reserve orange for brand and action emphasis.
- Use semantic colors only for actual state.
- Maintain accessible contrast for text, controls, focus, and disabled states.

---

## 5. Typography

### 5.1 Font families

Use two complementary type families:

| Role | Preferred font | Windows fallback |
|---|---|---|
| Expressive title | Fraunces | Georgia |
| Interface and body | Inter | Segoe UI Variable, Segoe UI |
| Technical values | Cascadia Mono | Consolas |

Inter and Fraunces may be bundled with the application when their font licenses and distribution terms are included correctly.

### 5.2 Typography usage

Fraunces should be used only for:

- Application welcome title.
- Major page titles.
- Report-preview headings.
- Empty-state or completion statements.

Inter or Segoe UI Variable should be used for:

- Navigation.
- Buttons.
- Model names.
- Tables and lists.
- Status messages.
- Body copy.
- Settings and forms.

Do not use the serif font for dense operational data.

### 5.3 Type scale

| Style | Size | Weight | Line height | Typical use |
|---|---:|---:|---:|---|
| Display | 40 px | 500 | 44 px | Welcome and completion hero |
| Page title | 30 px | 500 | 36 px | Main tab title |
| Section title | 22 px | 500–600 | 28 px | Major card or section |
| Card title | 17 px | 600 | 22 px | Card and model-row title |
| Body | 15 px | 400 | 22 px | Primary descriptions |
| Secondary | 13 px | 400 | 19 px | Supporting information |
| Label | 12 px | 600 | 16 px | Category and control labels |
| Metric | 24–32 px | 600 | 1.1 | Key progress or result values |
| Monospace | 12–13 px | 400 | 18 px | Commands, logs, IDs, paths |

### 5.4 Editorial labels

Small category labels may use uppercase text with 1.5–2 px letter spacing, following the website style.

Examples:

- SYSTEM READINESS
- MODEL LIBRARY
- BENCHMARK PROGRESS

Use these labels sparingly. They should guide the eye, not create visual clutter.

---

## 6. Application Window and Navigation

### 6.1 Window behavior

- Target Windows 11.
- Default window size: approximately 1360 × 860 px.
- Minimum supported size: 1100 × 720 px.
- Support maximize, restore, minimize, and resize correctly.
- Preserve the last valid window size and position.
- Use per-monitor DPI awareness and remain crisp from 100% through 200% scaling.
- Support keyboard navigation and screen readers.

### 6.2 Window appearance

- Use the warm `Canvas` color for the client area.
- Use Windows 11 rounded-window treatment when available.
- Use native shadows and system window behavior.
- A custom title bar may be used only if dragging, resizing, snapping, system menus, accessibility, and high-DPI behavior remain correct.
- Use Mica or translucency, if used at all, only in restrained window chrome. Do not allow it to disturb the warm brand canvas.

### 6.3 Primary navigation

Use a clean top navigation system that reflects the website's horizontal navigation.

Recommended tabs:

1. **Home**
2. **Doctor**
3. **Models**
4. **Benchmark**
5. **Reports**
6. **Settings**

The header should contain:

- Haval LocalAI Bench mark and product name on the left.
- Primary tabs in the center or immediately after the product name.
- Current machine-health indicator and Help on the right.

### 6.4 Active-tab treatment

The active tab should use:

- Darker text.
- A subtle `Accent Soft` background or a thin orange indicator.
- A smooth 160–200 ms transition.

Avoid thick underlines, large colored blocks, or multiple simultaneous active indicators.

---

## 7. Layout and Spacing

### 7.1 Content layout

- Center the main content within a maximum width of approximately 1180 px.
- Use 28–36 px outer margins at standard desktop sizes.
- Use 32–48 px between major sections.
- Use 20–24 px between related cards.
- Use 12–16 px between a title and its supporting text.
- Use an 8 px base spacing grid.

### 7.2 Information density

The application may contain advanced information, but it should never feel like a raw engineering console.

- Prefer one strong summary followed by supporting cards.
- Keep important values visible without scrolling where practical.
- Keep long logs collapsed.
- Use tables only for true repeated data.
- Use cards for status, decisions, and guided actions.

### 7.3 Alignment

- Left-align most text and data.
- Right-align numeric columns when comparison matters.
- Vertically center controls within rows.
- Keep actions in predictable locations.
- Avoid arbitrary center alignment for operational content.

---

## 8. Surface and Card System

### 8.1 Standard card

Use the website's paper-like card language:

- Background: `#FBF7EF`
- Border: 1 px `#E6DFD3`
- Corner radius: 14 px
- Internal padding: 20–24 px
- Shadow: very soft and warm

Suggested desktop shadow:

```text
0 1px 2px rgba(26,26,26,0.04),
0 6px 18px -8px rgba(26,26,26,0.08)
```

### 8.2 Elevated card or dialog

- Corner radius: 16 px
- Padding: 24–32 px
- Use a slightly stronger shadow only when the surface must clearly float above other content.

### 8.3 Card behavior

- Hoverable cards may rise by no more than 1–2 px.
- Border and shadow may strengthen slightly on hover.
- Cards must not bounce, tilt, glow, or dramatically scale.
- Noninteractive cards must not look clickable.

---

## 9. Buttons and Controls

### 9.1 Primary button

- Burnt-orange fill.
- Warm-ivory text.
- Height: 38–42 px.
- Horizontal padding: 18–22 px.
- Fully rounded or 20–22 px corner radius.
- Medium font weight.
- One clear action label.

Examples:

- Start Benchmark
- Download Model
- Repair Automatically

### 9.2 Secondary button

- `Surface` background.
- 1 px `Border` outline.
- `Ink` text.
- Same height and radius as the primary button.

### 9.3 Tertiary action

- No container by default.
- Use `Accent Text` or `Ink Soft`.
- Provide a subtle hover background.

### 9.4 Destructive action

Destructive actions such as removing a model must use the semantic error color and require clear confirmation when data will be deleted.

### 9.5 Inputs and search

- Height: 40–44 px.
- Background: `Surface`.
- Border: 1 px `Border`.
- Corner radius: 10–12 px.
- Use an orange focus ring with sufficient contrast.
- Include a visible label; placeholder text must not be the only label.
- Search should include a leading search icon and a clear button when populated.

### 9.6 Checkboxes and switches

- Use native-feeling Windows controls styled with the brand accent.
- Maintain a minimum 32 × 32 px interaction area.
- The selected state must remain understandable without color alone.

### 9.7 Disabled states

Disabled controls must remain readable and should explain why they are unavailable through nearby text or a tooltip.

---

## 10. Icons and Illustration

- Use a consistent rounded-line icon family.
- Standard icon size: 18–20 px.
- Standard stroke: approximately 1.5–1.75 px.
- Use filled icons only for strong state or selected navigation.
- Do not mix unrelated icon styles.
- Do not use emoji as primary application icons.
- Use the orange accent for active or primary icons and charcoal for normal icons.

Custom illustrations may appear in onboarding, empty states, and completion screens. They should use the website palette, simple geometry, restrained detail, and generous whitespace.

---

## 11. Motion and Feedback

Motion should communicate state, not decorate the interface.

### 11.1 Timing

- Hover and press: 120–160 ms.
- Tab and selection transitions: 160–200 ms.
- Card expansion and dialogs: 180–240 ms.
- Progress changes: smoothly interpolated without delaying truthful progress.

### 11.2 Motion rules

- Use ease-out for appearing elements.
- Use ease-in-out for state changes.
- Avoid continuous animation unless a task is actively running.
- Avoid flashing, pulsing, or rapid color changes.
- Respect Windows reduced-motion settings.

### 11.3 Long-running work

For downloads, repair, probes, and benchmarks:

- Show a stable progress indicator.
- Show the current step in plain language.
- Show elapsed time when useful.
- Show estimated remaining time only when reliable.
- Keep Cancel or Pause visible when supported.
- Never flash terminal windows.

---

## 12. Status and Messaging

### 12.1 Status hierarchy

Every major workflow should provide:

1. A short headline.
2. A one-sentence explanation.
3. A status icon and label.
4. One recommended action.
5. Optional technical details.

### 12.2 Message examples

Prefer:

> **Ollama is ready**  
> The local service is running and responding normally.

Prefer:

> **This model needs more memory**  
> Choose a smaller quantization for reliable acceleration on this PC.

Avoid unexplained error codes in the main message.

### 12.3 Notifications

- Use compact in-app toast notifications for completed background actions.
- Keep critical failures visible until resolved or dismissed.
- Do not overuse modal dialogs.
- Never use a modal for routine success.

---

## 13. Key Screen Baselines

### 13.1 Home

The Home screen should provide a calm overview:

- Editorial welcome title.
- One-line product purpose.
- Machine readiness card.
- Installed and selected model count.
- Last benchmark summary.
- One primary next action.

Use no more than three or four summary cards in the first viewport.

### 13.2 Doctor

The Doctor screen should feel reassuring, not alarming.

Recommended structure:

- Overall state: **Ready**, **Needs attention**, or **Repairing**.
- Vertical checklist of prerequisites.
- Each item shows icon, title, one-line status, and optional action.
- One **Repair Automatically** primary action when repair is possible.
- Collapsed **Technical details** section.

Green should indicate confirmed readiness. Orange should indicate an action or active repair—not every warning. Red should be reserved for true blockers.

### 13.3 Models

The Models tab should include:

- Search field at the top.
- Segmented filter: **Installed**, **Preferred**, and **Search Ollama**.
- Storage summary.
- Model rows or cards with consistent columns.

Each model row should show:

- Selection checkbox.
- Model name and tag.
- Size and quantization.
- Hardware-fit badge.
- Installation or download status.
- Primary row action.

During download, replace the Download action with:

- Clean progress bar.
- Percentage.
- Current stage.
- Cancel control.

The progress track should use `Border`; the active fill should use `Accent`. Completed models should use the success state without losing the brand styling.

### 13.4 Benchmark

The Benchmark screen should emphasize progress and confidence:

- Current model and sequence position.
- Large but restrained overall progress.
- Current test description in plain language.
- Elapsed time.
- Pause and Cancel actions.
- Collapsed live technical log.

Do not create multiple competing gauges or animated charts.

### 13.5 Reports

The Reports screen should feel editorial and premium:

- Large Fraunces page title.
- Report cards with date, machine, model count, and verdict.
- Clean preview thumbnail or summary.
- Primary **Open Report** action.
- Secondary export and folder actions.

### 13.6 Settings

Group settings by purpose:

- Application
- Ollama
- Models and storage
- Benchmark behavior
- Privacy and support

Use simple labeled controls. Keep risky or advanced settings collapsed.

---

## 14. Tables and Dense Data

Use tables only when the customer benefits from comparing repeated values.

- Header background should remain subtle.
- Row height: approximately 48–56 px.
- Use fine horizontal dividers instead of full cell grids.
- Keep model names left-aligned.
- Align comparable numbers consistently.
- Use monospaced numerals only when it materially improves scanning.
- Keep the selected row visible with an `Accent Soft` background.
- Support keyboard row navigation.
- Do not place more than two primary actions in a row.

For narrow windows, hide secondary columns before shrinking text below readable sizes.

---

## 15. Accessibility and Windows Quality

The application must:

- Meet WCAG 2.2 AA contrast targets where applicable.
- Provide visible keyboard focus.
- Support keyboard-only navigation.
- Use logical tab order.
- Expose control names, roles, values, and states to Windows accessibility APIs.
- Support Narrator and common screen readers.
- Respect Windows text scaling.
- Respect reduced-motion and high-contrast modes.
- Never communicate status through color alone.
- Keep primary interaction targets at least 32 × 32 px, preferably 40 px high.
- Render sharply at common Windows scaling levels.

When Windows High Contrast is enabled, system accessibility colors and outlines take precedence over brand styling.

---

## 16. Windows Desktop Implementation Guidance

This design baseline is framework-independent and may be implemented with a native Windows desktop stack.

Implementation must preserve:

- Windows 11 window management and snap behavior.
- Per-monitor DPI awareness.
- Smooth text rendering.
- Accessible controls and automation properties.
- Background processing without UI freezing.
- Hidden command execution without flashing PowerShell or CMD windows.
- Responsive progress updates through the main UI thread.
- Correct disabled, hover, pressed, focus, and selected states.

If custom-drawn controls are used, they must match or exceed the keyboard, accessibility, scaling, and input behavior of native Windows controls.

The visual design should not compromise reliability.

---

## 17. Light and Dark Themes

The first release should prioritize a polished light theme matching HavalOthman.com.

Dark mode may be added later, but it must be deliberately designed rather than generated through simple color inversion.

The initial application should therefore ship with:

- One complete light theme.
- Windows High Contrast support.
- Centralized design tokens so a future dark theme can be added safely.

---

## 18. Do and Do Not

### Do

- Use warm ivory and cream surfaces.
- Use burnt orange as a controlled signature.
- Use generous whitespace.
- Use editorial serif headings selectively.
- Keep body and operational UI in a clean sans-serif.
- Use 14 px cards and subtle shadows.
- Use plain language and progressive disclosure.
- Make progress calm, stable, and easy to understand.
- Make the next action obvious.

### Do not

- Copy macOS controls literally.
- Turn the application into a webpage inside a window.
- Use dark gaming gradients as the default visual style.
- Use neon glow, glass everywhere, or heavy drop shadows.
- Put every metric in a separate colored tile.
- Expose raw PowerShell as the normal experience.
- Use orange for every heading and icon.
- Animate constantly.
- reduce font sizes to fit excessive information.
- Hide failures behind generic messages.

---

## 19. Minimum Design Acceptance Criteria

The design is ready for implementation when:

- The application uses the defined core palette consistently.
- Main screens visually belong to the same family as HavalOthman.com.
- The product still feels like a native Windows 11 application.
- The top navigation clearly identifies the current tab.
- Every screen has one obvious primary action.
- Cards use consistent surface, border, radius, padding, and shadow rules.
- Typography follows the serif-for-expression and sans-serif-for-operation rule.
- All controls have normal, hover, pressed, focused, selected, disabled, and error states.
- Doctor remains understandable without opening technical details.
- Model downloads show stable progress without terminal-window flashing.
- Long-running benchmarks never make the application appear frozen.
- The interface remains usable at the minimum supported window size.
- The interface remains sharp and readable at common Windows scaling levels.
- Keyboard navigation, visible focus, Narrator support, and high-contrast behavior are verified.
- Status is never communicated through color alone.
- The final UI feels calm, elegant, human, and deliberately crafted.

---

## 20. Final Design Statement

Haval LocalAI Bench should combine the warm editorial identity of HavalOthman.com with the precision and restraint of a premium modern product.

Its beauty should come from proportion, typography, whitespace, subtle depth, thoughtful motion, and clear behavior—not decoration.

The intended experience is:

> Sophisticated at first glance, simple at first use, and trustworthy during every technical operation.
