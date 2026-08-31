# Rising Game Developer — Light / Balanced / Heavy playbook

**Job of this role (who hits send):** A junior / jam developer talking to a normal chat AI. They will copy a script into Unity themselves.

Stack people usually name: Unity + C#. Same kind of question works for Godot if they say so.

They type a question. They expect a **text answer** (explanation and/or a script in the reply). The model must not open Unity, create a project, press Play, call tools, or generate scenes.

Hardware is shared. Patience is not.

---

## Agents in the room

- **Maya** — just shipped a jam and is asking chat for a script
- **Rafi** — reviews junior PRs; wants one feature in one reply
- **Lin** — fails any item that needs the Editor, a video, or “create a new 2D project”

**Maya:** Light is “write me a move / jump / coin script.”

**Rafi:** Balanced is “write me a patrol-and-chase enemy.”

**Lin:** Heavy is “here is my dash — why does it double and go through walls, and what should I paste instead?”

They locked Light / Balanced / Heavy below.

### Local LLM clock — this role only

Same box for every pack: **10–20B Q4_K_M fully in VRAM**, 12–16 GB class GPU, plan **20–40 tok/s**. Chat text only.

| Tier | Output cap | First token max | Full answer max |
| --- | --- | --- | --- |
| Light | **400 tokens** | 10 s | **50 s** |
| Balanced | **800 tokens** / turn | 12 s | **100 s** |
| Heavy | **1200 tokens** / turn | 18 s | **3 min** |

Pass if the reply is a paste-ready script (and a short wiring note if they asked). Fail if it says it needs Unity Hub, Play mode, or a screenshot.

---

## 1. Light

**Job:** Write me a Unity script so my 2D player can move, jump, and pick up coins. Just show the code in the chat.

### Prompt (copy / paste)

```text
Can you write a Unity C# script for a simple 2D player?

I want left/right movement, a jump only when they are on the ground, and collecting coins. When they touch a coin, add 1 to a score and print it in the console, then remove the coin.

I already have a player with a Rigidbody2D. Coins are triggers tagged "Coin". I can add a small ground check object at the feet.

Please put the full script in your answer and a short list of what I should hook up in the Inspector. Don't create a Unity project and don't walk me through installing Unity.
```

### Expected result & local LLM time — Light

**Expected result:** One `CoinCollector` (or similar) in a code block: move, ground check, jump, trigger pickup. A few bullets: drag GroundCheck, set layer, tag coins. No “File → New 2D project.” Cap ≤400 tokens.

| Clock | Target | Max this role still accepts | Feels broken |
| --- | --- | --- | --- |
| First token | 1–4 s | **10 s** | ~18 s blank |
| Full answer | — | **50 s** | ~1.5× that, still going |

---

## 2. Balanced

**Job:** Write me an enemy that walks between two points, chases the player if they get close, then goes back to walking if the player leaves.

### Prompt (copy / paste)

```text
I need a Unity C# enemy script.

It should walk back and forth between two points. If the player comes within a detect range, it chases. If the player gets far enough away, it walks back to where it started and then patrols again.

Please use a simple state machine with Patrol, Chase, and Return so I can add Attack later without rewriting it. Put the speeds and ranges as fields I can change in the Inspector. If you can, add gizmos for the two ranges.

One script in the chat is enough. Tell me what to drag onto the component. Don't build a scene for me and don't use NavMesh unless I ask.
```

### Expected result & local LLM time — Balanced

**Expected result:** One `PatrolChaser` in a code block: enum states, Inspector fields, flip facing, editor gizmos. A short “drag point A, point B, and the player here.” No three-script architecture, no NavMesh lecture. Cap ≤800 tokens.

| Clock | Target | Max this role still accepts | Feels broken |
| --- | --- | --- | --- |
| First token | 1–4 s | **12 s** | ~20 s blank |
| Full answer | — | **100 s** | ~1.5× that, still going |

---

## 3. Heavy

**Job:** My dash goes through walls and if I mash the button I dash twice. Here is the script — what is wrong, and what should I replace it with?

### Prompt (copy / paste)

```text
My player dash is buggy. If I mash the button I dash twice and go flying. If I dash into a thin wall I end up on the other side.

Here is the script:

void Update() {
    if (Input.GetButtonDown("Jump"))
        StartCoroutine(DashBroken());
}

IEnumerator DashBroken() {
    float facing = Mathf.Sign(transform.localScale.x);
    float t = 0f;
    while (t < dashTime) {
        transform.Translate(Vector3.right * facing * dashSpeed * Time.deltaTime);
        t += Time.deltaTime;
        yield return null;
    }
}

First tell me why both bugs happen. Then write the fixed dash script I can paste over this one.

I want a cooldown so I cannot start another dash while one is running, and I want the move to use the Rigidbody so it stops at walls instead of sliding through them. A short raycast in front each step is fine.

One script in the chat plus a few lines mapping each bug to the fix. Don't ask me to hit Play and report back. Don't add extra systems.
```

### Expected result & local LLM time — Heavy

**Expected result:** Mash starts a second coroutine; `Translate` ignores colliders so the body tunnels. Then one script with cooldown + `MovePosition` (or equivalent physics move) that stops on a hit. No “send me a Play-mode video.” Cap ≤1200 tokens.

| Clock | Target | Max this role still accepts | Feels broken |
| --- | --- | --- | --- |
| First token | 1–4 s | **18 s** | ~30 s blank |
| Full answer | — | **3 min** | ~1.5× that, still going |

---

## Quick score (text only)

| | Pass | Fail |
| --- | --- | --- |
| Light | One move/jump/coin script + short Inspector notes | New-project tutorial, 3D controller |
| Balanced | One state-machine enemy + what to drag | NavMesh essay, three files |
| Heavy | Names both bugs, then a physics dash with cooldown | “Hit Play and tell me what you see” |

Light proves they can ask for a tiny playable loop. Balanced proves they can ask for one tunable mechanic. Heavy proves they can paste a broken dash and get a diagnosis plus a replacement — still only as chat text.
