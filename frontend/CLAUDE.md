## Test builder UI (disabled — kept for reference)

**Both test builder UI services below were stopped and disabled on
`192.168.100.100` in July 2026.** They are being kept only as a reference
for building similar web-UI services for a different framework — do not
re-enable them, and do not assume either is reachable. The application code
(`testrail_builder.py`, `local_builder.py`, `builder_core.py`, the static
UI, and the `start_*.py` launchers) is untouched and still reflects a
working implementation to copy from.

- Their systemd units (`easybdd-testrail-builder.service`,
  `easybdd-local-builder.service`) still exist on disk in
  `/etc/systemd/system/` for reference, but are `disabled`/`inactive` and no
  longer start at boot.
- The root `Jenkinsfile`'s "Restart services" stage no longer restarts
  either of them (it only restarts `easy-bdd-mcp`) — a push to `main` will
  not bring them back up. Re-enabling requires deliberately re-adding those
  `systemctl restart` lines and running `systemctl enable --now` again.

`frontend/testrail_builder.py` (started via `frontend/start_testrail_builder.py`,
port 8091) was the current, non-deprecated web UI test builder — it pushed
cases directly into TestRail via `TestRailService`. Do not confuse it with
`frontend/test_builder_app.py` / `start_builder.py`, which is an older,
deprecated app with only copy-paste YAML export and no real TestRail push.

- Formerly ran persistently on `192.168.100.100` as systemd unit
  `easybdd-testrail-builder.service`, from `/home/jenkins/EasyBDD/frontend`.
  Was reachable at `http://192.168.100.100:8091` before being disabled.
- Deploy = push to main: the `EasyBDD` Jenkins job pulls into
  `/home/jenkins/EasyBDD`. The old `/var/lib/jenkins/workspace/EASYBDD`
  checkout was decommissioned in July 2026 (archived as
  `EASYBDD.decommissioned-*`) — do not reference or recreate it.
- See `ONBOARDING.md` "Production instance" section for more detail.

## Local (TestRail-free) test builder UI

`frontend/local_builder.py` (started via `frontend/start_local_builder.py`,
port 9093) was a filesystem-backed sibling of the TestRail builder — same
case/step model and UI (`frontend/static/testrail_builder.html` serves both;
it detects which backend it's talking to via `/api/local/status` vs
`/api/testrail/status`), but cases/shared-steps/vars are stored as plain YAML
under `tests/cases/` instead of pushed to TestRail. No TestRail credentials
required. Shared logic between the two builders lives in
`frontend/builder_core.py` — don't duplicate case-model/serialization/
validation code into either app; extend `builder_core.py` and import from
both. Persisted run history lives in `frontend/local_runner.py` and
`reports/local_runs/*.json`; the TestRail-import feature
(`/api/local/import/testrail*`) uses `TestRailService` only as a one-shot
data source, never at test-run time.

- Formerly ran persistently on `192.168.100.100` as systemd unit
  `easybdd-local-builder.service`, from `/home/jenkins/EasyBDD/frontend`,
  same shape as `easybdd-testrail-builder.service`. Was reachable at
  `http://192.168.100.100:9093` before being disabled.
- Port map on `192.168.100.100`: 8080 Jenkins, 8091 TestRail builder (now
  disabled), **9093 local builder (now disabled)**, 8092 easy-bdd-mcp, 4566
  Floci, 9001/9002 Jira/Confluence MCP, 8765 crawler, 11434 Ollama.
