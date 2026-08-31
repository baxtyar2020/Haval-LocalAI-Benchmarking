# Haval LocalAI Bench

## Prerequisites, Doctor, Automated Fix Process, and Model Download Requirements

**Document purpose:** Define the customer environment requirements, automated prerequisite installation, Doctor diagnostics, repair workflow, hardware-acceleration validation, and Model Library experience for Haval LocalAI Bench.

This document covers only application readiness and model acquisition. It does not define benchmark methodology, scoring, calculations, or reporting logic.

---

## 1. Customer Experience Objective

The customer experience must be simple:

> Install the signed Windows application, launch it, allow Doctor to prepare and verify the system, select or download models, and start the benchmark.

The customer must not normally need to:

- Open PowerShell or Command Prompt.
- Copy or paste Ollama commands.
- Install Python manually.
- Find or repair environment paths.
- Start or restart Ollama manually.
- Change PowerShell execution policies.
- Diagnose ports, permissions, services, or GPU settings.

The installer and Doctor must handle environment discovery, dependency installation, Ollama configuration, service recovery, model acquisition, and hardware-acceleration verification through a graphical interface.

Manual commands may exist for advanced troubleshooting and support, but they are not part of the normal customer setup.

---

## 2. Supported Operating Environment

### 2.1 Operating system

The customer operating-system requirement is **Windows 11**.

A separate “64-bit Windows” requirement does not need to be presented to the customer because Windows 11 is already a 64-bit operating system.

### 2.2 Supported compute and memory architectures

NVIDIA and CUDA are not mandatory prerequisites. The application must support any Windows 11 system on which Ollama can provide supported hardware-accelerated inference, including:

- A discrete NVIDIA GPU.
- A discrete AMD GPU.
- A supported Intel GPU.
- An integrated GPU or APU.
- A unified-memory architecture.
- A GPU that uses shared system memory.
- Any other Windows hardware-acceleration backend supported by the installed Ollama runtime.

The application must identify the available architecture and apply the correct diagnostic method. NVIDIA-specific checks are supplemental and must be used only when NVIDIA hardware exists.

---

## 3. Required Application Prerequisites

Before a benchmark can begin, Doctor must verify the following requirements.

| Requirement | Required behavior |
|---|---|
| Windows 11 | Detect the operating system. Block with a clear explanation if unsupported. |
| Ollama runtime | Detect an existing installation or install Ollama automatically. |
| Ollama executable | Find Ollama in its standard or custom installation location. Do not depend only on the system `PATH`. |
| Ollama service/API | Confirm that the local Ollama API is available, normally at `http://127.0.0.1:11434`. |
| Hardware acceleration | Prove through a live model probe that inference is not operating purely on the CPU when supported acceleration is available. |
| Storage | Require enough free space for selected model downloads plus a minimum 10 GB operating reserve. |
| Application runtime | Bundle Python and required application dependencies inside the customer installer. |
| Windows runtime components | Detect and install required Microsoft Visual C++ runtime components when permitted. |
| Permissions and security compatibility | Detect blocked execution, access-denied conditions, quarantined components, port conflicts, and local security restrictions. |

Git, LM Studio, vLLM, llama.cpp, cloud APIs, a separately installed Python environment, and a separately installed CUDA Toolkit are not normal customer prerequisites.

---

## 4. Doctor Mode and Readiness Gate

The application must start in **Doctor mode** on first launch. Doctor is the readiness gate for the application.

The **Start Benchmark** control must remain disabled until:

- All blocking prerequisites pass.
- The Ollama API is available.
- The machine-level hardware-acceleration probe passes.
- At least one model is installed and selected for benchmarking.
- No selected model is actively downloading.

Doctor must present each check with a clear status:

- Checking
- Passed
- Warning
- Repairing
- Failed
- Blocked by policy

Doctor must keep a technical log for support while presenting plain-language status and repair guidance to the customer.

Doctor must never silently continue with an invalid CPU-only configuration.

---

## 5. Doctor Diagnostic Sequence

Doctor must perform the following workflow:

1. Confirm that the customer is running Windows 11.
2. Detect the CPU, GPU, integrated graphics, APU, unified-memory configuration, and available system memory.
3. Detect whether Ollama is installed.
4. Locate the Ollama executable, including non-default installation locations.
5. Install Ollama automatically when it is missing and the customer permits installation.
6. Start or restart Ollama when necessary.
7. Poll the local Ollama API until it becomes ready or the configured timeout expires.
8. Detect available disk space.
9. Inventory all models already installed through Ollama.
10. Select the smallest installed chat model for a machine-level probe.
11. If no suitable model exists, offer or automatically download a small probe model.
12. Run a short deterministic generation.
13. Inspect `ollama ps` while the model remains loaded.
14. Confirm full or partial hardware acceleration using Ollama and available platform telemetry.
15. Apply a basic performance sanity check to detect a false hardware-acceleration report.
16. Open Model Library after the environment passes.
17. Enable Start Benchmark only after at least one model is installed, ready, and selected.

---

## 6. Vendor-Neutral Hardware-Acceleration Probe

### 6.1 Purpose

The probe does not require every model to report `100% GPU`. Its purpose is to prove that Ollama is actively using available graphics or AI acceleration and has not silently fallen back to CPU-only inference.

### 6.2 Acceptable operation

The following configurations are acceptable:

- Full GPU acceleration.
- A GPU-and-CPU split caused by partial model offloading.
- GPU acceleration using unified memory.
- GPU acceleration using shared system memory.
- An integrated GPU or APU actively accelerating inference.
- Normal CPU participation in model loading, tokenization, scheduling, or operations that the active backend does not accelerate.

System RAM or unified memory may hold model data while the GPU performs accelerated computation. This must not be misclassified as CPU-only operation.

### 6.3 Probe execution

Doctor must:

1. Detect the available compute and memory architecture.
2. Confirm the Ollama API is responding.
3. Load the smallest suitable installed chat model.
4. If necessary, download a small probe model such as `smollm:135m-instruct-v0.2-q2_K`.
5. Send a short fixed prompt using temperature `0` and a small output-token limit.
6. Measure time to first token and generation speed.
7. Inspect `ollama ps` while the model remains loaded.
8. Confirm that Ollama reports full or partial GPU acceleration.
9. When platform telemetry is available, confirm that the relevant accelerator is active.
10. Compare observed performance with a conservative CPU-only sanity range for the probe model and hardware class.

### 6.4 Platform-specific verification

The primary requirement is vendor-neutral. Supplemental evidence may include:

- **NVIDIA:** `nvidia-smi`, Ollama processor split, Ollama-runner GPU memory, and generation speed.
- **AMD, Intel, integrated GPU, or APU:** supported Windows GPU telemetry, Ollama processor information, runtime/backend information, and generation speed.
- **Unified-memory system:** confirmed accelerator activity, Ollama processor information, shared-memory use, and generation speed. Dedicated VRAM must not be required.

The absence of NVIDIA tooling is not a failure on a non-NVIDIA system.

### 6.5 Probe result classification

| Observed result | Doctor decision |
|---|---|
| Model is fully GPU-accelerated | **Pass** |
| Model uses meaningful GPU acceleration with some CPU offload | **Pass with information notice** |
| Model uses an integrated GPU, APU, shared memory, or unified memory for acceleration | **Pass** |
| Vendor telemetry is limited, but Ollama reports acceleration and the performance check supports it | **Pass with verification details** |
| Model is too large and falls predominantly or entirely onto the CPU | **Fail that model** and recommend a smaller model or quantization |
| Ollama uses the CPU only even though supported acceleration should be available | **Fail** and open the automated repair flow |
| No compatible acceleration is detected | **Block the normal benchmark** and explain the hardware limitation |
| Telemetry sources contradict each other | **Fail verification**, collect evidence, and open the repair flow |

The normal benchmark is hardware-accelerated. A future CPU-only benchmark, if added, must be a separate and clearly labeled mode.

---

## 7. Automated Installation and Repair Requirements

### 7.1 General requirement

The signed Windows installer and Doctor must complete setup and repair through the graphical application. They must not depend on the customer manually running scripts.

The installer and Doctor must:

- Install the application and bundled runtime.
- Detect whether Ollama is installed.
- Download and install Ollama when missing.
- Locate Ollama in default or custom paths.
- Store the resolved Ollama path internally.
- Start and restart Ollama when required.
- Verify the Ollama version and local API.
- Detect permissions, security restrictions, port conflicts, and service failures.
- Check and install required Windows runtime components when permitted.
- Run the hardware-acceleration probe.
- Open Model Library for model selection and acquisition.
- Keep Start Benchmark disabled until the environment is ready.

### 7.2 Missing Ollama

**Installation wizard (before Doctor):** detect whether Ollama is already on this PC.

- If Ollama **is** installed, skip any Ollama download step. Do not tell the customer they need the internet for Ollama.
- If Ollama **is not** installed, show a short, plain message **before** downloading:

  **Internet needed for Ollama.** This PC does not have Ollama yet. Haval LocalAI Bench uses the official Ollama service to run models here. This step downloads the latest Ollama service. It is a small, fast download. Stay connected until it finishes.

  Do not start the download if there is no internet. The Haval application can still be installed; Doctor can finish Ollama later when a connection is available. This is not a model download and not a Python install.

If Ollama is missing at runtime, Doctor must:

1. Download the official Windows installer through a trusted connection.
2. Verify the installer before execution when supported.
3. Request administrator approval only if required.
4. Run the installer.
5. Rediscover the installed executable.
6. Start Ollama.
7. Verify the version and local API.
8. Continue automatically to the hardware probe.

### 7.3 Ollama path failure

Doctor must not assume that Ollama is available through `PATH` or installed in one fixed location.

If the configured path fails, Doctor must:

1. Search known Ollama installation locations.
2. Inspect registered application information where appropriate.
3. Validate candidate executables.
4. Save the valid path in the application's internal configuration.
5. Start Ollama directly using its resolved full path.
6. Recheck the API.

Doctor should repair the application's own configuration first. It should modify the Windows system or user `PATH` only when necessary, permitted, and safe.

### 7.4 Ollama service or API failure

If Ollama cannot be contacted, Doctor must check:

- Whether the executable still exists.
- Whether an Ollama process is already running.
- Whether the configured API address is correct.
- Whether port `11434` is available.
- Whether another process is using the port.
- Whether multiple Ollama instances are conflicting.
- Whether the process has permission to start.
- Whether local loopback communication is permitted.
- Whether security software blocked or quarantined a component.
- Whether the Ollama installation is damaged or incomplete.

Doctor must attempt the following repair sequence:

1. Rediscover the Ollama executable.
2. Repair the application's internal path.
3. Stop a failed or stale Ollama process when safe.
4. Start Ollama from its resolved location.
5. Poll the local API until ready.
6. Restart Ollama if the first attempt fails.
7. Offer an automated Ollama repair or reinstall.
8. Request elevation only when required.
9. Re-run the hardware-acceleration probe.
10. Export a Doctor diagnostic report if repair remains blocked.

### 7.5 Hardware-acceleration failure

If the probe indicates CPU-only inference or contradictory telemetry, Doctor must:

- Restart Ollama and repeat the probe.
- Detect whether another application is consuming accelerator resources.
- Recommend closing games, recording/streaming applications, and other local model servers.
- Check whether the active Ollama runtime supports the detected hardware backend.
- Check applicable environment variables and backend configuration.
- Check laptop high-performance or discrete-graphics settings when applicable.
- Check integrated-GPU, shared-memory, or unified-memory availability.
- On NVIDIA systems, check the installed driver and use `nvidia-smi` as supplemental proof.
- Guide the customer through a driver update or reinstall only when needed.
- Require a reboot when a driver or system component change requires it.
- Recommend a smaller model or quantization when the selected model is too large.
- Re-run the probe after repair.

The application must not automatically rewrite GPU drivers or weaken system security protections.

### 7.6 Insufficient storage

Doctor must calculate:

```text
Required free space = total selected download size + 10 GB reserve
```

If storage is insufficient, the application must let the customer:

- Deselect one or more models.
- Choose smaller models or quantizations.
- Choose another supported model-storage location.
- Free storage and retry the check.

### 7.7 PowerShell and security restrictions

The application must not depend exclusively on customer-run PowerShell scripts. PowerShell execution policies, enterprise restrictions, antivirus software, or other security controls may block scripts.

The implementation must:

- Use signed executables and trusted Windows installer mechanisms.
- Prefer native application code for downloads, API checks, path discovery, and process management.
- Run required PowerShell commands through a controlled hidden background process when PowerShell is used.
- Avoid permanently weakening PowerShell execution policy.
- Never silently disable Windows Defender, firewall rules, antivirus software, or enterprise security controls.
- Request administrator approval only for actions that genuinely require it.
- Detect and explain security-policy blocks in plain language.
- Produce a Doctor report suitable for IT support when organizational policy prevents repair.

---

## 8. Model Library Tab

The application must include a dedicated **Model Library** tab. It allows customers to see installed models, download preferred models, search for additional Ollama models, and choose which models participate in a benchmark.

The tab must contain three clear areas:

1. **Models Already Installed on This PC**
2. **Haval Preferred Models**
3. **Search Ollama Models**

---

## 9. Installed Models Inventory

When Model Library opens, the application must query Ollama and display all locally available models.

Internally, this may use:

```powershell
ollama list
```

For each model, display when available:

- Exact Ollama model name and tag.
- Friendly display name.
- Parameter size.
- Quantization.
- Storage size.
- Digest.
- Model family.
- Installation status.
- Estimated hardware fit.
- Acceleration readiness.
- **Include in Benchmark** checkbox.

The customer must be able to:

- Include a model in the benchmark.
- Exclude a model from the benchmark.
- Select all eligible installed models.
- Select only recommended models.
- Re-download or repair a model when appropriate.
- Remove a downloaded model through a clearly confirmed action.

Excluding or skipping a model must never delete it from the computer.

---

## 10. Haval Preferred Models

The following models must appear in the default preferred list.

The following **five** models appear in the default preferred list (Decision D-2). GPT-OSS 20B is not a preferred catalog entry; it remains searchable and selectable.

| Preferred model | Exact Ollama download command |
|---|---|
| Gemma 4 26B | `ollama pull gemma4:26b` |
| Qwen 3 Coder 30B | `ollama pull qwen3-coder:30b` |
| Kimi Linear 48B | `ollama pull hf.co/mradermacher/Kimi-Linear-48B-A3B-Instruct-GGUF:Q4_K_S` |
| Qwen 3 Next 80B | `ollama pull qwen3-next:80b` |
| GPT-OSS 120B | `ollama pull gpt-oss:120b` |

Exact commands:

```powershell
ollama pull gemma4:26b
ollama pull qwen3-coder:30b
ollama pull hf.co/mradermacher/Kimi-Linear-48B-A3B-Instruct-GGUF:Q4_K_S
ollama pull qwen3-next:80b
ollama pull gpt-oss:120b
```

Each preferred-model row must provide:

- Model name.
- Model size when known.
- Download status.
- Estimated hardware fit.
- Estimated storage requirement.
- **Download** button.
- Individual progress bar.
- **Include in Benchmark** checkbox.
- Cancel, retry, and remove controls where applicable.
- A clear error explanation if the pull fails.

The preferred-model catalog must be configuration-driven so its model names, tags, metadata, and download commands can be updated without redesigning the application.

---

## 11. One-Click Download Experience

### 11.1 Customer-facing behavior

When the customer selects **Download**, the application must execute the exact pull command automatically. The customer must not copy or paste it.

The experience must remain graphical:

- No flashing Command Prompt windows.
- No visible PowerShell windows.
- No separate terminal for each model.
- No manual command entry.

### 11.2 Background execution

The application may start a hidden PowerShell process for each active download or execute the Ollama operation through a supported application interface. When PowerShell is used, it must run hidden in the background.

The application must:

- Execute one model's command independently.
- Capture standard output and error output.
- Parse Ollama progress information.
- Translate the output into a stable graphical progress bar.
- Store the technical output in a support log.
- Avoid showing raw terminal noise as the primary customer experience.

### 11.3 Progress information

For an active download, show when available:

- Model name.
- Current stage.
- Percentage complete.
- Downloaded size.
- Total size.
- Current transfer speed.
- Estimated remaining time.
- Pause or cancel control when technically supported.

When the pull completes, show **Completed**, refresh the installed-model inventory, and enable the model's benchmark-selection checkbox.

---

## 12. Download Queue

Downloads must run sequentially by default. This avoids competing large downloads, excessive storage activity, overlapping terminal output, and unnecessary registry failures.

Each queued model must show one of these states:

- Not installed
- Queued
- Downloading
- Paused
- Verifying
- Completed
- Failed
- Cancelled

A failure downloading one model must not cancel the remaining queue. The customer must be able to retry, edit the model tag, search for an alternative, or skip the failed model.

The application may later provide controlled parallel downloads as an advanced setting, but sequential download is the default requirement.

---

## 13. Post-Download Validation

After every successful pull, the application must:

1. Confirm that the download command completed successfully.
2. Refresh the installed-model inventory.
3. Verify that the exact model appears in Ollama.
4. Record available name, tag, size, digest, family, parameter size, and quantization metadata.
5. Run a short model load test.
6. Check whether the model can use available GPU, integrated-GPU, APU, shared-memory, or unified-memory acceleration.
7. Classify the model as one of the following:
   - Ready
   - Ready with partial offload
   - Installed but not verified
   - Not suitable for this hardware
   - Failed to load
8. Make an eligible completed model available for benchmark selection.

A completed download does not automatically mean that the model is suitable for the customer's hardware.

If a model is too large, the application must recommend a smaller model or quantization rather than allowing an unexplained CPU-only run.

---

## 14. Benchmark Model Selection

Every installed model must have an independent **Include in Benchmark** checkbox.

The customer may:

- Select one model.
- Select multiple models.
- Select all eligible installed models.
- Select the preferred models that fit the hardware.
- Exclude a model without uninstalling it.
- Change the selection before starting a run.

Start Benchmark must remain disabled when:

- No model is selected.
- A selected model is still downloading or verifying.
- Ollama is unavailable.
- The machine-level acceleration probe has failed.
- A required repair is still active.

Models that do not meet the acceleration policy must remain visible with a clear status and explanation. They must not silently participate in the normal benchmark.

---

## 15. Search Ollama Models

Model Library must include a **Search Ollama Models** function.

The customer must be able to:

- Search by model name.
- Paste an exact Ollama model tag.
- Paste a supported Hugging Face Ollama reference.
- Filter results by model family, parameter size, quantization, download size, or estimated hardware fit when metadata is available.
- Review estimated storage and hardware fit before downloading.
- Add a result to the sequential download queue.
- Download it through the same hidden background process and graphical progress interface.
- Select the completed model for benchmarking.

Examples of accepted model entries include:

```text
mistral
phi4
qwen3-coder:30b
hf.co/organization/repository:quantization
```

Search and download errors must distinguish among conditions such as:

- Model or tag not found.
- Network unavailable.
- Registry unavailable.
- Authentication required.
- Insufficient storage.
- Unsupported or invalid model format.
- Unsupported sharded model package.
- Checksum or download verification failure.
- Model load failure.
- Model too large for the selected acceleration policy.

The customer must be offered appropriate actions:

- Retry.
- Edit model tag.
- Search for another quantization.
- Choose a smaller model.
- Skip the model.
- View technical details.

---

## 16. Internal Support Commands

The application may use the following commands internally. They are documented for implementation and support, not as required customer actions.

```powershell
ollama --version
ollama list
ollama ps
ollama serve
ollama stop MODEL_NAME
```

On NVIDIA systems only, Doctor may also use:

```powershell
nvidia-smi
```

To test the local Ollama API through PowerShell when permitted:

```powershell
Invoke-RestMethod http://127.0.0.1:11434/api/tags
```

If PowerShell is restricted, the application must perform the equivalent API request and process control through its signed native or bundled application components.

---

## 17. Acceptance Requirements

The prerequisite and model-download experience is complete only when all of the following are true:

- A Windows 11 customer can install and launch the application without manually installing Python.
- Doctor detects, installs, locates, starts, and verifies Ollama through the graphical experience.
- A non-NVIDIA Windows system is not rejected merely because CUDA or `nvidia-smi` is unavailable.
- NVIDIA-specific validation is applied when NVIDIA hardware exists.
- Integrated-GPU, APU, shared-memory, and unified-memory acceleration can pass the probe.
- CPU-only inference is not silently accepted for the normal benchmark.
- Doctor distinguishes full GPU acceleration, partial offload, unified/shared-memory acceleration, and CPU-only fallback.
- Path, port, permissions, service, API, and security-policy failures have clear automated repair routes.
- The application does not permanently weaken PowerShell or Windows security policies.
- Model Library lists all models already installed on the PC.
- All five Haval Preferred Models appear with the exact specified pull commands.
- Each model can be downloaded independently with one click.
- Downloads run without flashing terminal windows.
- Each download has a clean status and progress presentation.
- A failed pull does not terminate the entire queue.
- Completed models are refreshed and validated automatically.
- Every installed model can be independently included in or excluded from a benchmark.
- Excluding a model never deletes it.
- Customers can search for and download other supported Ollama models.
- Start Benchmark remains disabled until the environment and at least one selected model are ready.

---

## 18. Final Product Requirement

The prerequisite, repair, and model-acquisition workflow must feel like one guided application experience—not a collection of scripts.

The customer should be able to:

> Install Haval LocalAI Bench, allow Doctor to prepare and verify the PC, open Model Library, see what is installed, download preferred or searched models with one click, select the models to evaluate, and start the benchmark.

All command execution, service management, prerequisite repair, progress interpretation, and acceleration verification must remain managed by the application.
