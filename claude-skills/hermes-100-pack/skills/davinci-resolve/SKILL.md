---
name: davinci-resolve
description: Drive DaVinci Resolve from Claude Code on macOS the way the Hermes davinci-resolve plugin did: probe whether Resolve Studio scripting is reachable, summarize the open project and timeline, scan folders for footage and music, import media, create or append to timelines, add markers, build a scripted rough cut from a clip plan, queue and poll renders, and for the free edition generate an importable FCPXML timeline or a marker CSV. Use it when a user mentions DaVinci Resolve, Resolve Studio, "rough cut", "import this footage into Resolve", "make a timeline from these clips", "add markers", "render the timeline", "FCPXML", "marker CSV", or editing video with Blackmagic Resolve.
---
# DaVinci Resolve control

**Hermes original:** https://github.com/wassermanproductions/hermes-davinci-resolve-plugin @ bbd5b20 · tier: community · category: tools · license: MIT
**Port class:** B — the plugin wraps the local DaVinci Resolve Python scripting API plus plain file generation; Claude Code can run the same Python on the user's Mac.

## What the Hermes plugin does
Per the README, it is dual-mode: with DaVinci Resolve Studio it connects to the Resolve Python scripting API (`DaVinciResolveScript.scriptapp("Resolve")`) to inspect the project, import media, create timelines, add markers, build scripted rough cuts and queue renders; with free Resolve, which does not expose live scripting, it writes importable FCPXML timelines and marker CSV files. Tools registered (plugin.yaml): `resolve_capabilities`, `resolve_launch`, `resolve_probe`, `resolve_project_summary`, `resolve_import_media`, `resolve_create_timeline`, `resolve_append_to_current_timeline`, `resolve_add_timeline_marker`, `resolve_scan_media_folder`, `resolve_create_scripted_timeline`, `resolve_render_timeline`, `resolve_render_status`, `resolve_generate_fcpxml_timeline`, `resolve_generate_marker_csv`. All mutating tools default to `dry_run=true` and require `confirm=true`. Platform: macOS only.

## Equivalent in Claude
Work in Claude Code with Bash and Python on the user's Mac. Follow the plugin's order: probe, dry-run (describe the plan), get explicit approval, then mutate.

1. Probe. Import the scripting module the way `resolve_bridge/operations.py` does: try `import DaVinciResolveScript`; if that fails, load `DaVinciResolveScript.py` from `$RESOLVE_SCRIPT_API/Modules` (if `RESOLVE_SCRIPT_API` is set) or from `/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting/Modules` or `/Applications/DaVinci Resolve/DaVinci Resolve.app/Contents/Libraries/Fusion`. Then call `module.scriptapp("Resolve")`. A live object means Studio live control; module import but no object means free edition, use interchange mode.
2. Launch if needed: `open -a "DaVinci Resolve Studio"` (or the exact `.app` path; the plugin lists bundles under `/Applications/DaVinci Resolve*/`). The user must have set Preferences > System > General > External scripting using: Local.
3. Project summary: `resolve.GetProjectManager().GetCurrentProject()`, then the project's current timeline, track counts and markers.
4. Scan media: walk the folder with Python, grouping by extension into video, audio, image.
5. Mutate only after approval: `media_pool.ImportMedia(paths)`, `media_pool.CreateEmptyTimeline(name)`, `media_pool.AppendToTimeline(items)`, `timeline.AddMarker(frame, color, name, note, duration, "")`.
6. Render: `project.LoadRenderPreset(name)` or `project.SetCurrentRenderFormatAndCodec(fmt, codec)`, `project.SetRenderSettings(settings)`, `job_id = project.AddRenderJob()`, `project.StartRendering(job_id)`; poll `project.GetRenderJobStatus(job_id)`, `project.GetRenderJobList()`, `project.IsRenderingInProgress()`.
7. Free edition: write an FCPXML 1.10 document (`<fcpxml version="1.10">` with `<resources>` and `<library>`, as the plugin does with `xml.etree`) or a CSV of frame, time, name, color, note, duration. Default output folder in the plugin: `~/Documents/Hermes Resolve Exports`. Tell the user to use File > Import > Timeline > Import AAF, EDL, XML and relink media.

| Hermes tool | How Claude does it |
|---|---|
| resolve_capabilities | Summarize this skill |
| resolve_launch | `open -a <app>` then re-probe |
| resolve_probe | Python import + `scriptapp("Resolve")` |
| resolve_project_summary | ProjectManager / CurrentProject / CurrentTimeline getters |
| resolve_scan_media_folder | Python `os.walk` by extension |
| resolve_import_media, resolve_create_timeline, resolve_append_to_current_timeline, resolve_add_timeline_marker, resolve_create_scripted_timeline | MediaPool / Timeline API calls listed above, after approval |
| resolve_render_timeline, resolve_render_status | Project render API calls listed above |
| resolve_generate_fcpxml_timeline, resolve_generate_marker_csv | Write files with Python |

## Setup
1. macOS with DaVinci Resolve or Resolve Studio installed; Studio is required for live control.
2. In Resolve: Preferences > System > General > External scripting using: Local.
3. Optional: `export RESOLVE_SCRIPT_API="/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting"` if the module is not at a standard path (the plugin also reads `RESOLVE_SCRIPT_LIB` for diagnostics only).
4. Run Claude Code on that Mac (not in a cloud sandbox).

## Limits
- Not verified in this port: no Mac with Resolve was available; API calls are quoted from the plugin source, not executed.
- Free Resolve cannot be controlled live; only file generation applies.
- No transitions, color, Fusion, Fairlight mixing, multicam or semantic video analysis; clip selection is Claude's job from the user's script.
- The plugin's dry-run/confirm gate is a convention here: always show the plan and wait for approval before changing a project or starting a render.
- Cowork cannot reach the Resolve API; use Claude Code locally.

## Source
- Catalog entry (reviewed commit): https://github.com/wassermanproductions/hermes-davinci-resolve-plugin/tree/bbd5b207f823f16a20e756bfa80f44ad34790a3f
- Catalog YAML: https://github.com/NousResearch/hermes-agent/blob/bb0c2303664edc01960fdbbb148b47acdbe553ce/plugin-catalog/davinci-resolve.yaml
