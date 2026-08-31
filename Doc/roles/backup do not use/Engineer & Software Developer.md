# Engineer & Software Developer — Light / Balanced / Heavy playbook

**Job of this role (who hits send):** A developer talking to a normal chat AI. They want a text answer (explanation and/or code in the reply). They copy anything useful themselves.

The model must not run code, open files, call tools, start servers, or create projects.

Hardware is shared. Patience is not.

---

## Agents in the room

- **Maya** — mid-level engineer who pastes a Saturday question into chat
- **Rafi** — staff engineer who pastes a feature spec and wants one reply he can read
- **Lin** — will fail any item that requires the model to execute, browse, or “create a repo”

**Maya:** Light is “write me this small script in the chat.”

**Rafi:** Balanced is “show me one service in one reply.”

**Lin:** Heavy is “here is the broken bit — what is wrong and what should it say instead?”

They locked Light / Balanced / Heavy below.

### Local LLM clock — this role only

Same box for every pack: **10–20B Q4_K_M fully in VRAM**, 12–16 GB class GPU, plan **20–40 tok/s**. Chat text only.

| Tier | Output cap | First token max | Full answer max |
| --- | --- | --- | --- |
| Light | **500 tokens** | 12 s | **60 s** |
| Balanced | **900 tokens** / turn | 15 s | **2 min** |
| Heavy | **1300 tokens** / turn | 20 s | **3.5 min** |

Pass if the reply answers the question, stays on one artifact, and does not ask you to execute anything. Fail if it says it needs your disk, a terminal, Docker, or “let me run this.”

---

## 1. Light

**Job:** Write me a small Python script that finds duplicate files in a folder by comparing file contents, and show me the code in the chat.

### Prompt (copy / paste)

```text
Can you write a small Python script that scans a folder and finds duplicate files by comparing the actual file contents, not the names?

I want it as a command-line tool I can run later myself. Use only the Python standard library. Hash the files in chunks so big files are okay. If the path I give is not a folder, just print an error.

Please put the full script in your answer and one example of how I would run it. Don't set anything up for me and don't run it.
```

### Expected result & local LLM time — Light

**Expected result:** One complete script in a code block (argparse, SHA-256 in chunks, groups of 2+ paths printed) plus one example command. Short. No tutorial. No “I created the file on your machine.” Cap ≤500 tokens.

| Clock | Target | Max this role still accepts | Feels broken |
| --- | --- | --- | --- |
| First token | 1–4 s | **12 s** | ~20 s blank |
| Full answer | — | **60 s** | ~1.5× that, still going |

---

## 2. Balanced

**Job:** Show me one small web API that accepts a publish job, remembers its status, and lets me check that status. Just the code in the chat.

### Prompt (copy / paste)

```text
I need a small FastAPI service for publish jobs.

Someone posts a job with a platform name and a payload of fields. The API gives back a job id and a status. There should be a GET endpoint to check that job later. Store jobs in a local SQLite file. When a job is created, kick off a background task that just waits a moment and then marks the job as ok — I will replace that wait with a real upload later.

Please show me this as one Python file in the chat: models, database table, POST, GET, and the background task. If the id does not exist, return 404.

Don't start the server. Don't install packages. Don't create files. Just write the code and a few lines on how I would run it myself later.
```

### Expected result & local LLM time — Balanced

**Expected result:** One file in a code block (Pydantic models, sqlite table, POST 202, GET with 404, asyncio task). A short note like “you would run uvicorn yourself.” No Docker, no second service, no “I started it on port 8000.” Cap ≤900 tokens.

| Clock | Target | Max this role still accepts | Feels broken |
| --- | --- | --- | --- |
| First token | 1–4 s | **15 s** | ~25 s blank |
| Full answer | — | **2 min** | ~1.5× that, still going |

---

## 3. Heavy

**Job:** Two workers are grabbing the same queued job and customers get double posts. Here is the claim function — what is the bug, and what should the claim look like instead?

### Prompt (copy / paste)

```text
We have a bug. Two workers both pick the same queued job and the customer gets two posts.

Here is the claim function:

async def claim_job_broken(jobs):
    for j in jobs:
        if j.status == "queued":
            j.status = "leased"
            return j
    return None

First explain what is going wrong: why can two workers both pass that if? What would a correct claim have to do in one step so only one worker wins?

Then show the fixed claim and the worker loop in the chat.

I want one atomic claim, like a single SQL update that leases one row only if it is still queued (or the lease expired), sets a short lease time, and bumps attempts.

Then a worker that: claims a job, tries to publish with exponential backoff, marks ok on success, puts it back in queue on a retryable error, and marks failed on a fatal error.

You can assume a store with methods like fetch_one, mark_ok, mark_failed, release_to_queued. Don't build the whole app. Don't run anything. Just the explanation, the functions, and a short why.
```

### Expected result & local LLM time — Heavy

**Expected result:** Names the race (two workers read “queued” before either writes). Then the lease update + worker error split + a few lines on why that stops the double claim. No “spin up two processes and watch logs.” Cap ≤1300 tokens.

| Clock | Target | Max this role still accepts | Feels broken |
| --- | --- | --- | --- |
| First token | 1–4 s | **20 s** | ~35 s blank |
| Full answer | — | **3.5 min** | ~1.5× that, still going |

---

## Quick score (text only)

| | Pass | Fail |
| --- | --- | --- |
| Light | Full script in the reply, stdlib, content hash | Asks to scan your real disk or runs a command |
| Balanced | One service in the reply, POST + GET + 404 | Starts a server, adds Redis/Docker |
| Heavy | Names the race, then a one-winner claim | “I need to reproduce this by running workers” |

Light proves they can finish a small tool on the page. Balanced proves they can describe one feature. Heavy proves they can talk through a race and show the patch — still only as chat text.
