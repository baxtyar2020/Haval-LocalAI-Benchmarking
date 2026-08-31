# Code signing (Authenticode)

Haval LocalAI Bench ships as an NSIS installer from Tauri. Windows SmartScreen reputation requires a **real** Authenticode certificate, preferably EV. This repository does not contain a certificate, a PFX, or a signed binary.

## What to sign

1. The NSIS setup EXE (`*_x64-setup.exe`).
2. The installed / bundled app EXE (`Haval LocalAI Bench.exe`).
3. Any other EXE you ship next to it (for example embeddable `python.exe` is usually left unsigned by CPython; do not replace it with a fake signature).

## How to sign

1. Import the organization’s code-signing certificate into the Windows certificate store (or use a hardware token / USB EV key with the vendor middleware).
2. Install the Windows SDK so `signtool.exe` is on disk.
3. Run:

```powershell
$env:HAVAL_SIGN_FILE = "C:\path\to\Haval LocalAI Bench_0.1.0_x64-setup.exe"
$env:HAVAL_SIGN_THUMBPRINT = "<SHA1 of the cert>"
powershell -ExecutionPolicy Bypass -File scripts\sign-release.ps1
```

Timestamping uses DigiCert’s server by default (`http://timestamp.digicert.com`). Change `-TimestampUrl` if your CA requires another RFC 3161 service.

## What not to do

- Do not generate a self-signed cert and call the build “signed for release.”
- Do not commit private keys.
- Do not skip timestamping; signatures without a timestamp fail after the cert expires.

## After signing

Verify: `signtool verify /pa /v <file>`. First-run SmartScreen warnings can still appear until the EV cert accumulates reputation.
