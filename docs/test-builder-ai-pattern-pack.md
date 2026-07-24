# Test Builder AI Pattern Pack (v1)

This pack translates current TestRail data into practical AI-generation strategy for the EasyBDD Test Builder.

## Source data used

- Automated pattern source: Suite `106658` (Project `77`) — `EASYBDD: Wattbox`
- Description/manual sources:
  - Suite `88128` (Project `68`) — `WattBox-NS`
  - Suite `76210` (Project `43`) — `x20 IPC Full Regression Test - UPDATED`
  - Suite `3524` (Project `50`) — `Araknis WAPs`
- Golden cases provided:
  - Upgrade resiliency: `C18690496`
  - Protocol/shared examples: `C18690466`, `C18690467`
  - Working websocket OvrC GET/POST examples: `C18690483`, `C18690468`
  - Web UI + websocket bridge: `C18690473`
  - Multi-device orchestration style: `C18690502`

## Key findings

### 1) What is already strong in automation patterns

From suite `106658`:

- Rich `Feature:`/`Shared:` composition with looping and conditions.
- Strong websocket + assertion motif (`websocket.send` + `test.assert`).
- Practical resiliency control flow (fault insertion + timed recovery).
- Reusable device-level shared steps (telnet/network/power/server setup).

### 2) What is underrepresented

- True multi-protocol chaining within a single test case (UI + telnet + ssh + websocket/jsonrpc) is still sparse.
- SSH coverage is low in this suite.
- A subset of resiliency flows rely on `sleep/state` with weak terminal pass/fail checks.

### 3) Description-only suite conversion potential

- `88128`: metadata-only for now (no step fields populated in sampled records).
- `76210`: summary-rich cases, sparse structured steps; good for intent extraction.
- `3524`: high conversion value. Many `custom_steps_separated` records with explicit expected outcomes.

## Golden template motifs (to encode into Builder AI)

### A. Fault-insertion firmware resiliency loop
Reference: `C18690496`

Pattern:
1. Capture pre-upgrade baseline (`Get_Firmware_Version`).
2. Execute upgrade path (with guard condition).
3. Inject a fault at parametric time offsets (`for_each` loop over fault timings).
4. Recover/wait for system stabilization.
5. Re-validate firmware state and service health.

Required assertions:
- Firmware version validity check (semantic format and expected branch).
- Recovery success signal (device reachable, command responses valid).
- No persistent error in telemetry response.

### B. Device/protocol control via telnet with assertion
References: `C18690466`, `C18690467`

Pattern:
1. Send control command over telnet.
2. Capture response into variable.
3. Assert command acceptance (`not_contains(..., 'command unknown')`, no error token).
4. Optionally send inverse command and re-assert.

Required assertions:
- Command accepted.
- Expected state transition observed (or absence of known failure token).

### C. UI-to-cloud bridge validation
Reference: `C18690473`

Pattern:
1. Login/open local UI.
2. Configure server endpoint/port settings.
3. Save/apply and allow settle window.
4. Validate via websocket request to remote endpoint.
5. Assert no error and expected content.

Required assertions:
- Save/apply success indicator.
- Websocket response contains valid payload and no error object.

### D. Multi-cycle network/power orchestration
Reference: `C18690502`

Pattern:
1. Run repeated cycle (`for_each`) of network + outlet actions.
2. Re-establish connectivity.
3. Validate through multiple channels (`dxGetAbout`, telnet validation, ssh validation).

Required assertions:
- Service availability restored after each cycle.
- Channel consistency checks pass after each iteration.

## Builder AI generation rules (must enforce)

1. Every generated test must end with explicit pass/fail assertions.
2. If `test.sleep` is present, include a reasoned post-condition check after the wait.
3. If a fault is injected, include both immediate and post-recovery validation.
4. For protocol actions (`telnet.send`, `ssh.send`, `websocket.send`, `jsonrpc.*`, `api.*`):
- capture output (`store_as`) and assert against output.
5. For upgrade/reboot flows:
- include baseline -> action -> post-action comparison.
6. Prefer reusable shared-step composition when equivalent shared blocks exist.

## Prompt presets for engineers (Builder UI)

### Preset 1: Firmware Resiliency

"Create a `Feature:` test for firmware resiliency on {{product_type}}.
Use a loop over fault timings {{fault_timing_list}}.
Sequence: baseline firmware -> upgrade -> fault insertion -> recovery -> final validation.
Include telnet and websocket validation, and explicit assertions for version validity and error-free responses.
Use shared steps where possible."

### Preset 2: Protocol Consistency

"Create a `Feature:` test that validates the same firmware/state across {{protocol_list}}.
Collect values via each protocol, normalize, and assert equality.
Fail if any channel mismatches or returns error tokens."

### Preset 3: UI + Device + Cloud Chain

"Create a `Feature:` test that changes setting(s) in local Web UI, validates effect via telnet/ssh command, and confirms cloud/websocket telemetry reflects the change.
Include rollback or cleanup and final assertions."

### Preset 4: Multi-device Orchestration

"Create a `Feature:` test where Device A action affects Device B.
Validate on Device B with {{device_protocol}}, and verify Device A telemetry via websocket/jsonrpc.
Run {{iterations}} cycles and assert deterministic recovery each cycle."

## Product profile model for cross-product generation

Builder should accept/select a profile object and gate generation accordingly:

```yaml
product_profile:
  name: "WattBox"
  supports_ui: true
  supports_telnet: true
  supports_ssh: true
  supports_websocket: true
  supports_jsonrpc: false
  supports_local_api: true
  firmware_channel: "ovrc"
```

Generation should fail fast (or auto-adjust) when a requested protocol is unsupported.

## Description-to-automation conversion pipeline

For suites like `3524` and `76210`:

1. Parse source fields by priority:
- `custom_steps_separated[].content`
- `custom_steps_separated[].expected`
- `custom_summary`
- `custom_expected`

2. Convert to intermediate intent graph:
- action intent
- target surface (UI/API/telnet/ssh/websocket)
- expected outcome

3. Compile to EasyBDD steps:
- Choose action templates from catalog
- Insert `store_as` on all protocol calls
- Emit assertion templates from expected text

4. Validate:
- run parser/validator
- fail generation if no terminal assertion exists

5. Human-in-the-loop:
- show draft + uncertainty tags for ambiguous steps

## Suggested additional smoke tests (based on current pattern)

1. Cross-channel firmware identity parity
- websocket vs local API vs telnet/ssh exact match

2. Upgrade interruption matrix
- power-only, network-only, and combined interruptions

3. Session and credential persistence
- credential change, reboot, and multi-channel re-auth behavior

4. OvrC command effect propagation
- command accepted + local device state converges + telemetry converges

5. Repeated recovery stability
- N-cycle fault/recover sequence with bounded timing and no drift

6. UI security control smoke
- web access disable/enable and alternate-management channel verification

## Immediate implementation backlog (Builder-focused)

1. Add scenario picker (preset intents above) in Assistant tab.
2. Add required assertion gate in backend generation response checker.
3. Add protocol support gating from selected product profile.
4. Add conversion mode for description-only TestRail suites.
5. Add confidence markers where conversion from natural-language steps is ambiguous.

## What is still needed from engineering to move from v1 to v2

1. Product capability matrix for each family under test.
2. Canonical "valid firmware version" assertion policy:
- regex format
- semantic compare behavior
- branch/channel expectations
3. 10-20 high-quality manual cases (preferably from `3524`) to seed the first conversion benchmark.
