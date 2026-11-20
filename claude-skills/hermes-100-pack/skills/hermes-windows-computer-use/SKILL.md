---
name: hermes-windows-computer-use
description: Drive a desktop GUI the way the Hermes THEIA ("hermes-windows-computer-use") plugin does, in basic mode, by running small PyAutoGUI and Pillow scripts from Claude Code: take screenshots, read the active window, move/click/type/scroll/drag, check pixels, and verify results, following the see, target, act, verify loop. Use when the user says "click the button in <app>", "automate this desktop app", "there is no API, use the GUI", "take a screenshot and find the field", "pyautogui", "computer use on Windows/macOS/Linux", or "THEIA". Prefer Claude's native computer-use capability when it is available in the current surface.
---
# THEIA desktop computer use

**Hermes original:** https://github.com/TREE-Ind/THEIA-UI-Computer-Use @ 6c73f53 · tier: community · category: tools · license: MIT
**Port class:** C — the basic toolset wraps PyAutoGUI, Pillow and PyGetWindow, which Claude Code can call from Python; the 37 registered `computer_use_*` tools, the LocateAnything visual-grounding worker (Python or C++/CUDA), the guarded grounding cache and the preflighted batch/workflow executors are Hermes runtime pieces that were not ported.

## What the Hermes plugin does
THEIA (kind `standalone`, toolset id `windows_computer_use`) registers 37 tools, among them `computer_use_capture_screen`, `computer_use_get_active_window`, `computer_use_focus_window`, `computer_use_open_app`, `computer_use_move`, `computer_use_click`, `computer_use_double_click`, `computer_use_type`, `computer_use_press`, `computer_use_hotkey`, `computer_use_scroll`, `computer_use_drag`, `computer_use_drag_path`, `computer_use_mouse_down/up`, `computer_use_release_all`, `computer_use_pixel`, `computer_use_pixel_matches`, `computer_use_set_dry_run`, plus grounding tools (`computer_use_locate`, `computer_use_locate_batch`, `computer_use_find_click`, `computer_use_find_drag`, `computer_use_observe_stage`, `computer_use_remember_groundings`) and bounded executors (`computer_use_batch`, `computer_use_execute_code`, `computer_use_dynamic_workflow`). Basic mode needs `pyautogui`, `pillow`, `pygetwindow` (plus `python3-xlib` on Linux, `pywin32` on Windows). Grounding uses LocateAnything-3B in an isolated worker venv or a `locate-anything.cpp` Q5 GGUF build. It bundles the operator skill `theia-ui-computer-use`.

## Equivalent in Claude
If the current Claude surface offers native computer use (Claude desktop app, Cowork, or the `computer-use` skill), use it; it already does screenshot, click, type and verify. Otherwise, from Claude Code on the machine that owns the display:

1. Install basic dependencies in a user venv: `python -m pip install "pyautogui>=0.9.54" "pillow>=10.0.0" "pygetwindow>=0.0.9"` (all three verified on PyPI: pyautogui 0.9.54, pillow 13.0.0, pygetwindow 0.0.9). Linux also needs `python3-xlib`; Windows `pywin32`.
2. Honor a dry-run flag: when `COMPUTER_USE_DRY_RUN=true` (the plugin's env var), print intended actions instead of performing them.
3. See: `pyautogui.screenshot("stage.png", region=(left, top, w, h))`; active window bounds via `pygetwindow.getActiveWindow()`. Read the PNG with the Read tool. Coordinates belong only to that exact screenshot.
4. Target: identify the control in the screenshot visually (no LocateAnything model is available); use `pyautogui.pixel(x, y)` / `pixelMatchesColor` to confirm state.
5. Act with one primitive at a time: `moveTo`, `click`, `doubleClick`, `write`, `press`, `hotkey`, `scroll`, `drag`/`dragTo`, `mouseDown`/`mouseUp`; after any failed hold, release all buttons and keys.
6. Verify with a fresh screenshot, window title or output file before claiming success. Recapture after any action that can change layout.
7. Never automate submit/send/pay/delete, authentication, credential entry, or permission changes without stopping for the user's explicit confirmation, and never type secrets through the GUI.

| Hermes tool | How Claude does it |
|---|---|
| `computer_use_capture_screen` | `pyautogui.screenshot(..., region=...)` then Read the file |
| `computer_use_get_active_window`, `computer_use_focus_window` | `pygetwindow.getActiveWindow()`, `.activate()` |
| `computer_use_click/type/press/hotkey/scroll/drag` | matching `pyautogui` calls |
| `computer_use_pixel`, `computer_use_pixel_matches` | `pyautogui.pixel`, `pyautogui.pixelMatchesColor` |
| `computer_use_release_all` | `pyautogui.mouseUp()` for each button, `keyUp` for held keys |
| `computer_use_set_dry_run` | `COMPUTER_USE_DRY_RUN=true` guard in your script |
| `computer_use_locate*`, `computer_use_find_click`, `computer_use_batch`, `computer_use_execute_code`, `computer_use_dynamic_workflow` | not reproduced; locate visually, act step by step |

The upstream operator skill is copied at `references/upstream-theia-ui-computer-use.md`; read its invariants and safety sections, but ignore the `backend="cpp"` and tool-schema details that need the Hermes plugin.

## Setup
1. Run Claude Code on the computer with the GUI session (a headless cloud sandbox cannot drive a desktop).
2. `python -m pip install pyautogui pillow pygetwindow` (plus platform extras above). On macOS grant Accessibility and Screen Recording permission to the terminal.
3. Optional: `export COMPUTER_USE_DRY_RUN=true` while rehearsing.

## Limits
- No visual grounding model: the LocateAnything worker (`scripts/setup_locate_worker.py`, `COMPUTER_USE_LOCATE_BACKEND`, `COMPUTER_USE_LOCATE_MODEL`, CUDA DLL path) is not ported; Claude must find targets by looking at the screenshot.
- No preflighted batches, restricted action code, guarded grounding cache or multi-stage dynamic workflows; every action is an explicit script step.
- PyAutoGUI is live by default and moves the real mouse and keyboard; mistakes act on the user's machine.
- Screenshots may contain sensitive data and are sent to the model when read; the plugin README carries the same privacy warning.
- Plugin env vars `THEIA_AUTO_INSTALL_BASIC_DEPS`, `THEIA_AUTO_INSTALL_LOCATE_WORKER`, `THEIA_LOCATE_TORCH`, `COMPUTER_USE_LOCATE_PYTHON`, `COMPUTER_USE_LOCATE_CPP_CLI`, `COMPUTER_USE_LOCATE_CPP_DLL`, `COMPUTER_USE_LOCATE_CUDA_BIN` have no effect here.

## Source
- Catalog entry (reviewed commit): https://github.com/TREE-Ind/THEIA-UI-Computer-Use/tree/6c73f53617c68e74618a6d6783e966795afe0e7a
- Catalog YAML: https://github.com/NousResearch/hermes-agent/blob/bb0c2303664edc01960fdbbb148b47acdbe553ce/plugin-catalog/hermes-windows-computer-use.yaml
