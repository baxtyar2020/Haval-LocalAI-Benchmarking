# Rising Game Developer — Customer Chat Pack (text-in / text-out)

Pack name: **Customer Chat Pack**  
Rule: **text-in / text-out** — they type a question; the model answers with text in the reply. No tools, no folders on disk, no execution, no image or video generate waits.

## Role description

This customer is a junior or jam developer who asks a normal chat AI for a Unity C# (or Godot) script they will paste themselves. They expect a MonoBehaviour and a short Inspector note in the reply. Chat must not open Unity, create a project, or press Play.

---

## Agents in the room

- **Maya** — just shipped a jam and is asking chat for a script
- **Rafi** — reviews junior PRs; wants one feature in one reply
- **Lin** — fails any item that needs the Editor, a video, or “create a new 2D project”

**Maya:** Light is “write me a move / jump / coin script.”
**Rafi:** Balanced is “write me a patrol-and-chase enemy.”
**Lin:** Heavy is “here is my dash — why does it double and go through walls, and what should I paste instead?”

---

## Local LLM clock (this role only)

Hardware: 10–20B Q4_K_M in VRAM, ~20–40 tok/s. Chat text only.

| Tier | Output cap | First token max | Full answer max |
| --- | --- | --- | --- |
| Light | 400 tokens | 10 s | 50 s |
| Balanced | 800 tokens | 12 s | 100 s |
| Heavy | 1200 tokens | 18 s | 3 min |

Split Heavy into two chat turns if the first reply gets long. Score the text. Do not press Play.

---

## 1. Light

**Ask / scenario:** A jam developer already has a 2D player in the scene and is asking the AI for one Unity script they can paste on it: move, jump only on ground, and pick up coins.

### What they type

```text
Can you write a Unity C# script for a simple 2D player?

I want left/right movement, a jump only when they are on the ground, and collecting coins. When they touch a coin, add 1 to a score and print it in the console, then remove the coin.

I already have a player with a Rigidbody2D. Coins are triggers tagged "Coin". I can add a small ground check object at the feet.

Please put the full script in your answer and a short list of what I should hook up in the Inspector. Don't create a Unity project and don't walk me through installing Unity.
```

### What a good text answer looks like

One `CoinCollector` (or similar) in a code block: move, ground check, jump, trigger pickup. A few bullets: drag GroundCheck, set layer, tag coins. No “File → New 2D project.”

---

## 2. Balanced

**Ask / scenario:** A junior game developer needs one enemy that patrols two points, chases when the player is close, then returns and patrols again. They are asking the AI to write that single Unity script in the chat.

### What they type

```text
I need a Unity C# enemy script.

It should walk back and forth between two points. If the player comes within a detect range, it chases. If the player gets far enough away, it walks back to where it started and then patrols again.

Please use a simple state machine with Patrol, Chase, and Return so I can add Attack later without rewriting it. Put the speeds and ranges as fields I can change in the Inspector. If you can, add gizmos for the two ranges.

One script in the chat is enough. Tell me what to drag onto the component. Don't build a scene for me and don't use NavMesh unless I ask.
```

### What a good text answer looks like

One `PatrolChaser` in a code block: enum states, Inspector fields, flip facing, editor gizmos. A short “drag point A, point B, and the player here.” No three-script architecture, no NavMesh lecture.

---

## 3. Heavy

**Ask / scenario:** A player dash flies through thin walls and fires twice if they mash the button. They paste the broken coroutine and ask the AI what is wrong, then to write the replacement script in the chat.

Use two chat turns if needed: first “what is wrong,” then “show the fixed script.”

### What they type — turn 1

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

Can you tell me why both bugs happen? Don't write the new script yet. Just explain in plain language.
```

### What they type — turn 2

```text
Okay, write the fixed dash script I can paste over this one.

I want a cooldown so I cannot start another dash while one is running, and I want the move to use the Rigidbody so it stops at walls instead of sliding through them. A short raycast in front each step is fine.

One script in the chat plus a few lines mapping each bug to the fix. Don't ask me to hit Play and report back. Don't add extra systems.
```

### What a good text answer looks like

Turn 1: mash starts a second coroutine; `Translate` ignores colliders so the body tunnels. Turn 2: one script with cooldown + `MovePosition` (or equivalent physics move) that stops on a hit. No “send me a Play-mode video.”

---

## Quick score (text only)

| | Pass | Fail |
| --- | --- | --- |
| Light | One move/jump/coin script + short Inspector notes | New-project tutorial, 3D controller |
| Balanced | One state-machine enemy + what to drag | NavMesh essay, three files |
| Heavy | Names both bugs, then a physics dash with cooldown | “Hit Play and tell me what you see” |

---

Skill version: **role-task-playbooks 1.3** · Customer Chat Pack · text-in / text-out · Ask / scenario required on every tier.
