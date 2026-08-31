# Progressive Creator — 3 AI Assistance Examples

Not code. The job is **direction**: briefs, prompts, iteration, and QC with AI chat + image / video / audio tools.

Light use → balanced feature workflow → heavy production system.

---

## Agents in the room

- **Maya** — creator who posts 5× a week with ChatGPT + one image model
- **Rafi** — creative producer who runs multi-tool pipelines (script → still → motion → cut)
- **Lin** — hiring / brand lead who can smell “AI slop” in three seconds

**Maya:** Light is a *single useful turn*. Caption, hook list, or a still that is close enough to post after one edit. If you needed a meeting to write the prompt, it isn’t light.

**Rafi:** Balanced is a *owned piece*: one asset that survives platform crop, brand voice, and a second pass. Script + shot list + image prompt + “what to reject.”

**Lin:** Heavy is how a real series ships. Character lock, tool chain, versioned prompts, fact check, rights, and a human who still says no. Progressive Creator means you *progress the work*, not that you accept the first render.

They locked these three.

### Local LLM clock — this role wants the list now

Same hardware as the other files: **10–20B Q4 in VRAM**, ~**20–40 tok/s**. Chat only — no image/video generate waits.

A Progressive Creator is in a posting / drafting loop. Five hooks in 15 seconds get used. Five hooks in two minutes get skipped. They do **not** share the engineer’s “think then emit a file” clock. Keep answers short so the model can hit *this* clock.

| Tier | Output cap | Why they will not wait like a developer |
| --- | --- | --- |
| Light | **200–300 tokens** | Hooks + caption + one image-prompt. |
| Balanced | **400–600 tokens** / turn | Brief *or* prompts *or* copy. |
| Heavy | **700–1000 tokens** / turn | Board *or* four prompts *or* one rewrite. |

---

## How this role actually uses AI chat

| Chat job | What they ask the local LLM for |
| --- | --- |
| Hooks / captions | Short lists with a hard line cap |
| Scene / beat writing | What we SEE + HEAR, not a novel |
| Shot list | 4–8 shots, one line each |
| Image-prompt text | Camera + light + subject + rejects — the prompt itself, not the picture |
| Motion-prompt text | One camera move + one gesture, from a locked still description |
| Continuity / critique | Diff vs last episode; rewrite only the broken lines |
| Platform copy | After the cut exists; no new story |

The skill is a brief the 14B/20B cannot dodge — and an output cap it can finish.

---

## 1. Light — one turn that ships something small

**Job:** You have a 12-second clip of a desk setup. You need 5 hooks + 1 caption + 1 *thumbnail prompt* (text only). Chat only. Cap the model at ~300 tokens.

### Chat prompt (copy / paste)

```text
You are my short-form editor, not a hype bot.

CLIP CONTEXT
- 12s vertical clip: clean desk, monitor glow, hands drop a headset onto a stand
- Audience: PC gamers and creators, 18–34
- Tone: calm, specific, zero “unlock your potential”
- Must not invent specs I didn’t give

TASK
1) Write 5 hooks (max 8 words each). Each hook must be a different angle:
   curiosity / sensory / mistake / status / utility
2) Write 1 caption (max 120 characters) + 3 hashtags that are actually used, not junk
3) Write 1 image-model prompt for a thumbnail that matches the clip
   - 9:16
   - same mood as “warm lamp + cold monitor”
   - no readable fake logos, no extra fingers, no watermark

FORMAT
Hooks:
1. ...
Caption:
...
Thumbnail prompt:
...

After the three blocks, add 2 lines only:
- Weakest hook and why
- One detail the thumbnail must keep consistent with the clip

HARD LIMIT: 280 words total. No preamble.
```

### Thumbnail prompt the chat should produce (example of a good output)

```text
9:16 close three-quarter view of a dark oak desk at night, single warm desk lamp
left, cold blue-white monitor glow right, black headset resting on a metal stand
in sharp focus, shallow depth of field, cinematic still, no text, no logos,
no watermark, photoreal, clean cable, two hands not visible
```

### How you use it (light ritual)

1. Paste the chat prompt.  
2. Kill the weakest hook yourself.  
3. Keep the thumbnail *prompt* — you are not generating the image in this role example.  
4. Do **not** ask the chat to “make it more viral.” That is how light work becomes slop.

**What this shows:** you can brief constraints, formats, and a reject list in one shot. Light Progressive Creator work.

### Expected result & local LLM time — Light

**Expected result:** 5 hooks + 1 caption + 1 thumbnail *prompt* (text). Cap: **≤300 tokens**.

| Clock | Target | **Max this role still accepts** | Feels broken |
| --- | --- | --- | --- |
| First token | 1–3 seconds | **6 seconds** | 12 s blank |
| Full pack | 8–15 seconds | **25 seconds** | **40 seconds** |

---

## 2. Balanced — own one asset end-to-end

**Job:** A 30-second product-lifestyle piece for a headset. Chat only: locked brief, beat sheet, one still-prompt, one motion-prompt, then platform copy. You never ask this local model to render pixels.

### Step A — Chat: make the creative brief (you will reuse this)

```text
You are a creative producer sitting next to me. Do not write ads. Write a shoot brief.

PRODUCT
- Over-ear gaming headset, matte black, subtle green accent ring on the cup
- We sell “late-session comfort,” not RGB fireworks

AUDIENCE
- People who stream or edit after midnight, not arena-finals fantasy

CONSTRAINTS
- No celebrity lookalikes
- No readable UI on screens
- No invented awards, dB numbers, or “used by pros”
- Talent is one adult, mid-20s, any gender, hoodie, tired-but-focused face
- Room: small apartment studio, practical lamps, not a warehouse set

DELIVER
1) Logline (1 sentence)
2) 30-second beat sheet (6 beats, each beat = what we SEE + what we HEAR)
3) 3 must-keep visual rules (identity of the product)
4) 3 automatic rejects (common AI mistakes for this scene)
5) Then wait. Do not write social copy yet.

HARD LIMIT: 400 words. No preamble.
```

### Step B — Chat: turn beat 3 into an image prompt + a video prompt

```text
Using ONLY beat 3 from the brief above.

Write two prompts. Do not add story that was not in beat 3.

IMAGE PROMPT (locked still)
- Start with camera + lens + lighting
- Describe the headset as a product hero, accent ring visible
- Face optional, if present keep it 3/4, no beauty-glaze skin
- End with negatives: extra ears on cups, warped headband, fake logos

VIDEO / I2V PROMPT (2.5–4s)
- Start from that still
- One camera move only (slow push OR slight orbit)
- Talent motion: inhale, tiny head turn, no talking yet
- Keep product geometry stable — do not morph the cups

Then list 3 things I should check on the first render before I generate take 2.
```

### Step C — Chat: platform pack after the cut exists

```text
The 30s cut is locked. Do not change the story.

Write:
- YouTube title (≤58 chars) + description first 2 lines
- 3 Shorts / Reels captions (different hooks, same facts)
- 1 alt-text sentence for the cover frame (accessibility, no keywords stuffing)

Brand voice: dry, specific, no emoji walls.
If you don’t know a fact, write [MISSING] instead of guessing.
```

### How you use it (balanced ritual)

1. Brief first. Freeze product rules.  
2. Lock one still-*prompt* (geometry rules).  
3. Write one motion-*prompt* that starts from that still description only.  
4. After the human cut exists, ask chat for copy.  
5. Save the brief + both prompts in a note titled `headset-late-session-v3`.

**What this shows:** sequence, lock, and platform adaptation. You own the asset. Balanced Progressive Creator work.

### Expected result & local LLM time — Balanced

**Expected result per chat turn:** brief *or* still+motion prompts *or* copy. Cap: **≤600 tokens**.

| Turn | Target | **Max this role still accepts** | Feels broken |
| --- | --- | --- | --- |
| First token | 2–5 seconds | **8 seconds** | 15 s blank |
| Step A brief | 15–30 seconds | **50 seconds** | 75 seconds |
| Step B prompts | 12–25 seconds | **45 seconds** | 70 seconds |
| Step C copy | 10–20 seconds | **35 seconds** | 50 seconds |

---

## 3. Heavy — series system: chat as desk, AI as crew, you as director

**Job:** A 6-episode short series with one recurring character. Local chat holds the bible, writes frame boards, writes image-prompt text and motion-prompt text, and critiques drift. You hold veto. No image/video model in this loop.

This is where juniors dump a paragraph into one model. Progressive Creators build a **desk** of short chat turns.

### 3.1 Series bible — paste this into a Project / Custom GPT / Claude Project once

```text
SYSTEM / PROJECT INSTRUCTIONS — “NORTH LAMP” SERIES BIBLE
You are the continuity editor and prompt engineer for a fiction short series.
You never invent canon. You never flatter. You flag drift.

CANON (do not change unless I say “canon update”)
- Title: North Lamp
- Format: 6 episodes, each 20–35 seconds, vertical, almost no dialogue
- Protagonist: “Nara,” mid-20s, short black hair with one silver streak behind the left ear,
  small scar through left eyebrow, thin gold chain, dark olive canvas jacket
- Setting: rainy port city, sodium streetlights, one apartment with a north-facing window
- Tone: quiet competence, not tragedy-porn, not cyberpunk costume party
- Language on screen: English only unless I supply a line

HARD RULES
1) If a detail is not in canon or in my latest note, answer “NOT IN CANON” and ask.
2) When you write image or video prompts, always restate:
   silver streak behind LEFT ear, scar through LEFT eyebrow, gold chain, olive jacket
3) No celebrity likeness. No real brand logos. No readable phone UI.
4) Do not write music lyrics that copy a famous song.
5) After every prompt you generate, add a QC checklist of 5 visual fails to look for.

YOUR JOB EACH SESSION
- Help me break an episode into 4 locked frames
- Write image prompts for those frames
- Write I2V / V2V prompts that start from the approved frame
- Diff against previous episode so hair / jacket / scar don’t drift
- Draft captions only after I type FRAME LOCKED
```

### 3.2 Episode briefing (you type this every week)

```text
EPISODE 04 brief
Goal: Nara waits for a ferry that never shows; she leaves before the rain gets worse.
New canon (approve?): she carries a dented steel thermos. Yes / no?

Give me:
1) 4-frame board (Frame A setup / B wait / C decision / D leave)
2) Continuity diff vs Episode 03 (what must match, what may change)
3) Image prompts for A–D
4) I2V prompt only for Frame C (the decision) — 3 seconds, one gesture
5) QC list: hair streak side, scar side, chain, jacket color, thermos dent

HARD LIMIT: 700 words. One line per shot. No novel.
```

### 3.3 Critique pass — this is the heavy skill

After the first Frame C render, you do **not** say “make it better.” You say this:

```text
CRITIQUE — Frame C, take 1 (I’m describing what I see, not what I hoped)

SEEN
- Streak is on the RIGHT ear (wrong)
- Scar is gone
- Jacket reads black, not olive
- Thermos looks brand-new, no dent
- Rain is going upward near the shoulder

KEEP
- Composition: she is small in frame, ferry lights in background — good
- Hand on thermos — good

REWRITE the Frame C image prompt only.
- Force LEFT streak, LEFT scar
- Olive canvas, wet sheen not plastic
- Thermos dent on the lower third
- Rain direction downward, 1/60s still, no fog wall
- Do not change camera angle

Then give me a 4-line “don’t drift” block I can paste into the video model.
```

### 3.4 Chat chain (heavy usage map)

```text
1. Bible project (once) — short canon only
      ↓
2. Episode brief → 4-frame board + continuity diff
      ↓
3. Image-prompt text for A–D (one turn; cap tokens)
      ↓
4. Motion-prompt text for Frame C only
      ↓
5. Critique turn: rewrite the one broken prompt
      ↓
6. Copy turn after FRAME LOCKED
```

Split turns so each stays under ~1100 tokens. Do not paste the whole bible every time.

### 3.5 What you refuse to outsource (Lin’s list)

- Final face  
- Facts and claims  
- Music that sounds like a hit you don’t own  
- “Make her hotter / younger”  
- Dialogue in a language you cannot check  
- Anything that looks like a real private person who didn’t consent  

**What this shows:** a Progressive Creator runs continuity and critique in **short local-chat turns** — scene text, image-prompt text, motion-prompt text — without asking a 14B/20B to render media.

### Expected result & local LLM time — Heavy

**Expected result per turn:** board *or* four image prompts *or* one critique rewrite. Cap: **≤1000 tokens**.

| Turn | Target | **Max this role still accepts** | Feels broken |
| --- | --- | --- | --- |
| First token (short brief) | 2–6 seconds | **10 seconds** | 18 s blank |
| First token (bible already in context) | 4–12 seconds | **18 seconds** | 25 s blank |
| Episode board + prompts | 30–70 seconds | **2 minutes** | **3 minutes** |
| Critique rewrite only | 12–25 seconds | **45 seconds** | 70 seconds |

Do not ask “write episode 4 + all prompts + captions” in one shot.

### Local LLM time summary — Progressive Creator (not the other roles)

| Tier | Output cap | First token max | Full answer max |
| --- | --- | --- | --- |
| Light | 300 tokens | 6 s | **25 s** |
| Balanced (per turn) | 600 tokens | 8 s | **50 s** |
| Heavy (per turn) | 1000 tokens | 10–18 s | **2 min** |

---

## Prompt patterns this role should keep in a swipe file

| Pattern | When | One-line shape |
| --- | --- | --- |
| Constraint first | Light copy | “Tone X. Max N words. Don’t invent.” |
| Brief then wait | Balanced | “Deliver the brief. Do not write copy yet.” |
| Locked still → motion | Video | “Start from this frame. One move. Don’t remake the face.” |
| Critique from SEEN | Heavy | “I describe the error. Rewrite only the broken part.” |
| Canon + NOT IN CANON | Series | “If missing, say so. Don’t fill gaps.” |
| QC tail | Every gen | “5 fails to inspect before take 2.” |
| Platform last | Always | “Cut exists. Now write native copy. No story changes.” |

---

## Portfolio proof (no GitHub required)

| Level | What to show | What a lead looks for |
| --- | --- | --- |
| Light | Before prompt → after post, 1 page | You can brief and ship the same day |
| Balanced | Brief + still + motion + 3 platform captions | You can own one asset across tools |
| Heavy | Bible excerpt + critique thread + episode that matches last week’s face | You can run a series without drift or slop |

Three folders on a drive beat a folder named `ai stuff final FINAL v7`.

---

## Lin’s close

Light proves you can talk to a model without drowning.  
Balanced proves you can direct one piece through chat → image → motion → copy.  
Heavy proves you can keep a character, a brand, and the truth stable while the tools try to wander.

Progressive Creator is not “person who uses AI.”  
It is **person who progresses the work until a human would sign it.**
