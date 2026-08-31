# Engineer & Software Developer — Customer Chat Pack (text-in / text-out)

Pack name: **Customer Chat Pack**  
Rule: **text-in / text-out** — they type a question; the model answers with text in the reply. No tools, no folders on disk, no execution, no image or video generate waits.

## Role description

This customer is a software engineer who opens a normal chat AI the way they open ChatGPT — not Cursor, not a terminal agent. They paste a Saturday question, a feature they want written out, or a broken function. They expect explanation and/or code in the reply. They copy it themselves. Chat must not run anything, create a repo, or touch their disk.

---

## Agents in the room

- **Maya** — mid-level engineer who pastes a Saturday question into chat
- **Rafi** — staff engineer who pastes a feature spec and wants one reply he can read
- **Lin** — fails any item that requires execute, browse, or “create a repo”

**Maya:** Light is “write me this small script in the chat.”
**Rafi:** Balanced is “show me one service in one reply.”
**Lin:** Heavy is “here is the broken bit — what is wrong and what should it say instead?”

---

## Local LLM clock (this role only)

Hardware: 10–20B Q4_K_M in VRAM, ~20–40 tok/s. Chat text only.

| Tier | Output cap | First token max | Full answer max |
| --- | --- | --- | --- |
| Light | 500 tokens | 12 s | 60 s |
| Balanced | 900 tokens | 15 s | 2 min |
| Heavy | 1300 tokens | 20 s | 3.5 min |

Split Heavy into two chat turns if the first reply gets long. Score the text. Do not run it.

---

## 1. Light

**Ask / scenario:** An engineer needs a weekend helper that finds true duplicate files by content, not name. They are asking the AI to write that small Python CLI in the chat so they can copy it and run it later themselves.

### What they type

```text
Can you write a small Python script that scans a folder and finds duplicate files by comparing the actual file contents, not the names?

I want it as a command-line tool I can run later myself. Use only the Python standard library. Hash the files in chunks so big files are okay. If the path I give is not a folder, just print an error.

Please put the full script in your answer and one example of how I would run it. Don't set anything up for me and don't run it.
```

### What a good text answer looks like

One complete script in a code block (argparse, SHA-256 in chunks, groups of 2+ paths printed) plus one example command. Short. No tutorial. No “I created the file on your machine.”

---

## 2. Balanced

**Ask / scenario:** An engineer is building a tiny publish-job API and wants one FastAPI file in the reply: accept a job, store status in SQLite, and let them look that status up later. They will run it themselves; chat should only write the code.

### What they type

```text
I need a small FastAPI service for publish jobs.

Someone posts a job with a platform name and a JSON payload. The API gives back a job id and a status. There should be a GET endpoint to check that job later. Store jobs in a local SQLite file. When a job is created, kick off a background task that just waits a moment and then marks the job as ok — I will replace that wait with a real upload later.

Please show me this as one Python file in the chat: models, database table, POST, GET, and the background task. If the id does not exist, return 404.

Don't start the server. Don't install packages. Don't create files. Just write the code and a few lines on how I would run it myself later.
```

### What a good text answer looks like

One file in a code block (Pydantic models, sqlite table, POST 202, GET with 404, asyncio task). A short note like “you would run uvicorn yourself.” No Docker, no second service, no “I started it on port 8000.”

---

## 3. Heavy

**Ask / scenario:** Two workers are claiming the same queued job and customers get double posts. The engineer pastes the broken claim and asks the AI to explain the race, then show a fixed atomic claim and worker loop in the chat.

Use two chat turns if needed: first “what is wrong,” then “show the fixed functions.”

### What they type — turn 1

```text
We have a bug. Two workers both pick the same queued job and the customer gets two posts.

Here is the claim function:

async def claim_job_broken(jobs):
    for j in jobs:
        if j.status == "queued":
            j.status = "leased"
            return j
    return None

Can you explain what is going wrong? Why can two workers both pass that if? What would a correct claim have to do in one step so only one worker wins?

Please don't write the new code yet. Just explain it in plain language.
```

### What they type — turn 2

```text
Okay, now show me the fixed claim and the worker loop in the chat.

I want one atomic claim, like a single SQL update that leases one row only if it is still queued (or the lease expired), sets a short lease time, and bumps attempts.

Then a worker that: claims a job, tries to publish with exponential backoff, marks ok on success, puts it back in queue on a retryable error, and marks failed on a fatal error.

You can assume a store with methods like fetch_one, mark_ok, mark_failed, release_to_queued. Don't build the whole app. Don't run anything. Just the functions and a short why.
```

### What a good text answer looks like

Turn 1: names the race (two workers read “queued” before either writes). Turn 2: the lease update + worker error split + a few lines on why that stops the double claim. No “spin up two processes and watch logs.”

---

## Quick score (text only)

| | Pass | Fail |
| --- | --- | --- |
| Light | Full script in the reply, stdlib, content hash | Asks to scan your real disk or runs a command |
| Balanced | One service in the reply, POST + GET + 404 | Starts a server, adds Redis/Docker |
| Heavy | Names the race, then a one-winner claim | “I need to reproduce this by running workers” |

---

Skill version: **role-task-playbooks 1.3** · Customer Chat Pack · text-in / text-out · Ask / scenario required on every tier.
