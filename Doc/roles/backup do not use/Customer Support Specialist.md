# Customer Support Specialist — Light / Balanced / Heavy playbook

**Job of this role (who hits send):** Reply using only the policy they pasted. Ticket fields stay clean.

Hardware is shared. Patience is not.

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

**Job:** Reply using only this policy sentence.

### Prompt (copy / paste)

```text
POLICY: Refunds within 30 days of delivery, original payment method, no cash.
Customer: “Can I get store credit on day 41?”
Write the reply, 6 lines max. If policy does not allow it, say so. No extra goodwill promise.

HARD LIMIT: 90 words.
```

### Expected result & local LLM time — Light

**Expected result:** 6-line reply. Cap ≤250 tokens.

| Clock | Target | Max this role still accepts | Feels broken |
| --- | --- | --- | --- |
| First token | 1–4 s | **6 s** | ~10 s blank |
| Full answer | — | **25 s** | ~1.5× that, still going |

---

## 2. Balanced

**Job:** Ticket reply + fields.

### Prompt (copy / paste)

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

### Expected result & local LLM time — Balanced

**Expected result:** reply + 3 fields. Cap ≤500 tokens.

| Clock | Target | Max this role still accepts | Feels broken |
| --- | --- | --- | --- |
| First token | 2–6 s | **8 s** | ~14 s blank |
| Full answer | — | **50 s** | ~1.5× that |

---

## 3. Heavy

**Job:** Four macros from one policy.

### Prompt (copy / paste)

```text
POLICY
[PASTE]

Write 4 macros: allow / deny / need-more-info / escalate
Each: when to use (1 line) + text (max 70 words)
Do not invent a policy branch.

HARD LIMIT: 320 words.
```

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

