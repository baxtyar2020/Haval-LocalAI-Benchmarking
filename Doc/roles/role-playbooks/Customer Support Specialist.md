# Customer Support Specialist — Customer Chat Pack (text-in / text-out)

Pack name: **Customer Chat Pack**  
Rule: **text-in / text-out** — they type a question; the model answers with text in the reply. No tools, no folders on disk, no execution, no image or video generate waits.

## Role description

This customer answers tickets from a pasted policy. They want a reply (and ticket fields) that keep every constraint and invent no goodwill. They type into a normal chat AI and paste the answer into the ticket. Policy holes stay marked [MISSING].

---

## Agents in the room

- **Maya** — uses the local model between other tasks
- **Rafi** — owns one artifact end-to-end
- **Lin** — will reject slop, invented facts, and essays

**Maya:** Light is one policy sentence in a reply.

**Rafi:** Balanced is a full ticket reply + fields.

**Lin:** Heavy is a macros pack from the policy doc.

They locked Light / Balanced / Heavy below.

### Local LLM clock — this role needs the reply now

Same box for every pack: **10–20B Q4_K_M fully in VRAM**, 12–16 GB class GPU, plan **20–40 tok/s**. Prefill 1–4 s short / 5–15 s long paste. RAM offload voids the clock. Chat only — no image or video generate waits.

IF is the gate. Math unused. A warm paragraph that breaks policy fails.

| Tier | Output cap | First token max | Full answer max |
| --- | --- | --- | --- |
| Light | **250 tokens** | 6 s | **25 s** |
| Balanced | **500 tokens** / turn | 8 s | **50 s** |
| Heavy | **900 tokens** / turn | 12 s | **2 min** |

---

## 1. Light

**Ask / scenario:** A customer asked for store credit after the refund window. They are asking the AI to write a short reply that uses only the pasted policy and does not invent goodwill.

### What they type

```text
POLICY: Refunds within 30 days of delivery, original payment method, no cash.
Customer: “Can I get store credit on day 41?”
Write the reply, 6 lines max. If policy does not allow it, say so. No extra goodwill promise.

HARD LIMIT: 90 words.
```

### What a good text answer looks like

The reply stays on one artifact, uses only pasted facts, and never asks to run, install, render, or open a tool. See expected result below.

### Expected result & local LLM time — Light

**Expected result:** 6-line reply. Cap ≤250 tokens.

| Clock | Target | Max this role still accepts | Feels broken |
| --- | --- | --- | --- |
| First token | 1–4 s | **6 s** | ~10 s blank |
| Full answer | — | **25 s** | ~1.5× that, still going |

---

## 2. Balanced

**Ask / scenario:** They have a policy paste and a ticket paste. They are asking the AI for the customer reply plus status, reason code, and next action, marking [MISSING] where the ticket is thin.

### What they type

```text
POLICY
[PASTE]
TICKET
[PASTE]

Output:
- Reply (max 120 words)
- Status
- Reason code
- Next action
Use [MISSING] if the ticket lacks a fact.

HARD LIMIT: 180 words.
```

### What a good text answer looks like

The reply stays on one artifact, uses only pasted facts, and never asks to run, install, render, or open a tool. See expected result below.

### Expected result & local LLM time — Balanced

**Expected result:** reply + 3 fields. Cap ≤500 tokens.

| Clock | Target | Max this role still accepts | Feels broken |
| --- | --- | --- | --- |
| First token | 2–6 s | **8 s** | ~14 s blank |
| Full answer | — | **50 s** | ~1.5× that |

---

## 3. Heavy

**Ask / scenario:** They need reusable macros from one policy doc. They are asking the AI for allow, deny, need-more-info, and escalate text without inventing extra policy branches.

### What they type

```text
POLICY
[PASTE]

Write 4 macros: allow / deny / need-more-info / escalate
Each: when to use (1 line) + text (max 70 words)
Do not invent a policy branch.

HARD LIMIT: 320 words.
```

### What a good text answer looks like

The reply stays on one artifact, uses only pasted facts, and never asks to run, install, render, or open a tool. See expected result below.

### Expected result & local LLM time — Heavy

**Expected result:** 4 macros. Cap ≤900 tokens.

| Clock | Target | Max this role still accepts | Feels broken |
| --- | --- | --- | --- |
| First token | 3–10 s | **12 s** | ~21 s blank |
| Full answer | — | **2 min** | frozen spinner past that |

### Local LLM time summary — Customer Support Specialist

| Tier | Output cap | First token max | Full answer max |
| --- | --- | --- | --- |
| Light | 250 | 6 s | 25 s |
| Balanced | 500 / turn | 8 s | 50 s |
| Heavy | 900 / turn | 12 s | 2 min |

Split Heavy into two turns if the first answer hits the cap.

## Quick score (text only)

| | Pass | Fail |
| --- | --- | --- |
| Light | Reply uses only the pasted policy sentence | Extra goodwill or a new refund path |
| Balanced | Reply + status + reason + next action | Fills ticket holes with invented facts |
| Heavy | 4 macros, no new policy branch | Invented escalate rules |

Every item is scored as **text-in / text-out**. A later human run is a second scorecard, not this pack.

---

Skill version: **role-task-playbooks 1.3** · Customer Chat Pack · text-in / text-out · Ask / scenario required on every tier.
