# CODEX.md

Guidance for Codex and other coding agents working on PyXooHub.

## Project Overview

PyXooHub is a Python dashboard engine for the Divoom Pixoo 64. It renders small widget-based dashboards into a 64x64 RGB buffer and sends frames to the Pixoo over the device HTTP API.

The project is intentionally modular:

- `src/app.py` handles app startup, dashboard discovery, and CLI dashboard selection.
- `src/engine/engine.py` runs the update/draw/push lifecycle.
- `src/engine/pixoo_driver.py` owns the Pixoo HTTP connection and frame delivery.
- `src/engine/dashboard.py` aggregates widgets and dirty state.
- `src/engine/widget.py` defines the base widget lifecycle and visual dirty tracking.
- `src/widgets/` contains concrete UI widgets and layout containers.
- `src/providers/` contains data providers such as weather and mouse battery.
- `src/default_dashboards.py` contains built-in dashboards.
- `src/dashboards.py` is user-local custom dashboard code and is gitignored.

## Runtime Environment

Use Python 3.12 or newer. The project currently uses `uv`.

Common commands:

```powershell
uv sync
uv run python src/app.py
uv run ruff check .
uv run python -m compileall -f src
```

The `.env` file is required for real device runs and is gitignored. At minimum:

```env
PIXOO_IP=192.168.x.x
```

Useful optional settings:

```env
PIXOO_PORT=80
FRAME_INTERVAL=0.5
PIXOO_ASYNC_PUSH=true
PIXOO_SKIP_UNCHANGED_FRAMES=true
PIXOO_RESET_POLICY=always
PIXOO_RESET_EVERY_FRAMES=120
PIXOO_LOG_FRAME_STATUS_INTERVAL=60
```

## Pixoo Behavior Notes

The Pixoo HTTP GIF endpoint is used as the frame transport.

Current reliable behavior:

- Reset the HTTP GIF slot before sending each changed frame.
- Send one 64x64 frame with `Draw/SendHttpGif`.
- Keep the reset default as `PIXOO_RESET_POLICY=always` unless testing on the real device proves another policy works.

Avoid assuming `periodic`, `first`, or `never` reset policies will behave correctly on-device. They are experimental.

The async sender keeps the render loop responsive. If frames arrive faster than the Pixoo can accept them, stale queued frames may be replaced with the newest frame.

## Engine Lifecycle

`PyXooEngine.tick()` performs one lifecycle step:

1. Update dashboard/widgets.
2. Skip rendering if nothing is dirty.
3. Clear driver buffer.
4. Draw dashboard.
5. Queue/push frame through the driver.

Dirty-state tracking is deliberate. Widgets start dirty, mark themselves dirty when visual state changes, and are marked clean after a successful dashboard draw.

When adding new widgets:

- Return `True` from `update(dt)` when visible output changes.
- Return `False` when nothing visible changed.
- Call `mark_dirty()` when changing visual properties outside `update()`.
- Avoid expensive work inside `draw()`.

The base `Widget` already marks dirty when these properties change:

- `x`
- `y`
- `width`
- `height`
- `current_color`

Containers aggregate child dirty state.

## Provider Guidance

Providers should expose cached values through cheap properties and do I/O only in `update(dt)` or explicit refresh methods.

Provider `update(dt)` should return:

- `True` if cached visible data changed.
- `False` otherwise.

Do not block the render loop with unnecessary provider I/O. Weather and mouse polling already use intervals; keep that pattern.

## Dashboard Guidance

Built-in dashboards live in `src/default_dashboards.py`.

Personal/custom dashboards live in `src/dashboards.py`, which is gitignored. Do not assume it should be committed.

Dashboard update methods should call `super().update(dt)` unless there is a very good reason not to. If a dashboard manually changes widget visual state, prefer setting widget properties that mark dirty automatically, or call `mark_dirty()`.

## Logging

Terminal logging should be useful but not chatty.

Good terminal logs:

- startup/shutdown summary
- selected dashboard
- Pixoo connection success/failure
- first frame sent
- periodic interval sender stats
- recoverable warnings

Debug-only logs:

- skipped duplicate frames
- replaced queued frames
- detailed timing/profiler output
- exception tracebacks

The Pixoo sender interval log reports deltas since the previous interval, not lifetime totals.

## Testing And Validation

Before committing code changes, run:

```powershell
uv run ruff check .
uv run python -m compileall -f src
```

Use small fake-driver smoke checks when possible instead of touching the real Pixoo. Avoid accidentally constructing `PixooDriver()` in tests unless a real device connection is intended.

There is no formal test suite yet. Prefer adding focused tests or smoke checks when touching shared engine, driver, widget, or provider behavior.

## Git Workflow

Current feature branch convention used in this repo:

```text
feature-stabilize-pixoo-push
```

When asked to work with commits:

- Check `git status --short --branch` first.
- Keep commits focused and reasonably small.
- Commit intermediate checkpoints after validated changes.
- Do not revert user changes.
- Be careful with `src/dashboards.py`; it is user-local and gitignored.

Useful commit style examples:

```text
Add async Pixoo frame sender
Introduce PyXoo engine loop
Track dirty state in widgets
Report Pixoo sender interval stats
```

## Coding Style

- Prefer existing project patterns over new abstractions.
- Use `rg` for searching.
- Keep comments sparse and useful.
- Use ASCII unless the file already needs non-ASCII.
- Keep terminal output readable.
- Use `apply_patch` for manual edits.
