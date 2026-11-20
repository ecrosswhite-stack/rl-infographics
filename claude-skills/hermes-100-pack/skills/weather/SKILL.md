---
name: weather
description: Weather observations, forecasts, alerts, METARs, severe-weather outlooks and global conditions from public NWS, aviationweather.gov, SPC and Open-Meteo endpoints, plus the recipe for the Rust-backed model imagery, radar, sounding and ECAPE tools, ported from the Hermes weather plugin. Use it when the user asks "what's the weather in Denver", "7-day or hourly forecast for lat/lon", "any active warnings for Oklahoma", "METAR for KORD", "today's SPC outlook", "weather in Tokyo", "dewpoint or wind chill calculation", or wants radar, HRRR/GFS maps, a model sounding or ECAPE values.
---
# Weather

**Hermes original:** https://github.com/FahrenheitResearch/hermes-weather-plugin @ d474493 · tier: community · category: tools · license: no LICENSE file found (pyproject.toml declares MIT, no LICENSE file in the checkout)
**Port class:** C · the seven data tools are plain HTTPS calls Claude can make with curl; the six image and calculation tools need Rust binaries bootstrapped from GitHub plus the `metrust`, `rusbie`, `wrf-rust`, `rustweather` and `cfrust` packages, which Claude can install but which were not verified to build here.

## What the Hermes plugin does
Registers 13 tools in toolset `weather`. Data: `wx_conditions`, `wx_forecast`, `wx_alerts`, `wx_metar`, `wx_brief`, `wx_global`, `wx_severe`. Images: `wx_model_image` (model field PNGs via `rusbie` and `wrf-rust`, models `aigfs, gdas, gefs, gfs, graphcast, hiresw, hrrr, hrrrak, nam, nbm, rap`), `wx_radar_image` and `wx_storm_image` (NEXRAD Level 2 through the `rustdar` or bundled `nexrad-render-cli` backend). Calculations: `wx_calc` (205 `metrust` functions verified against MetPy per the skill), `wx_sounding` (model profile with CAPE/CIN, LCL/LFC/EL, shear, SRH) and `wx_ecape` (`ecape-rs` runner). Missing binaries are built on first use into `~/.hermes/weather/bin` with a Rust toolchain. A bundled `skill.md` tells the agent to start with lightweight data tools, batch model variables in one call and zoom to the region asked about.

## Equivalent in Claude
Data tools, exactly as `nws.py` does them. Send `User-Agent` and `Accept: application/geo+json,application/json` on every api.weather.gov call (NWS requires a User-Agent). Resolve place names to lat/lon from your own knowledge or ask; the plugin takes lat/lon as input.

| Hermes tool | How Claude does it |
|---|---|
| `wx_conditions` | `GET https://api.weather.gov/points/{lat},{lon}`, follow `properties.observationStations`, take the first station id, `GET https://api.weather.gov/stations/{id}/observations/latest`; report temperature, dewpoint, wind, pressure, visibility, `textDescription`, `rawMessage` |
| `wx_forecast` | from the same points response follow `properties.forecast` (14 periods) or `properties.forecastHourly` (24 periods) |
| `wx_alerts` | `GET https://api.weather.gov/alerts/active?status=actual&message_type=alert&point={lat},{lon}` or `&area={STATE}`; summarize event, severity, urgency, headline, onset, expires, areaDesc |
| `wx_metar` | `GET https://aviationweather.gov/api/data/metar?ids={STATION}&format=json`; fields `rawOb, temp, dewp, wdir, wspd, wgst, visib, altim, fltcat, clouds, reportTime` |
| `wx_brief` | conditions plus the first 3 forecast periods plus alert count and headlines |
| `wx_global` | `GET https://api.open-meteo.com/v1/forecast?latitude=..&longitude=..&current=temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,weather_code,wind_speed_10m,wind_direction_10m,wind_gusts_10m,surface_pressure&temperature_unit=fahrenheit&wind_speed_unit=mph` |
| `wx_severe` | `GET https://www.spc.noaa.gov/products/outlook/day1otlk_cat.nolyr.geojson` (features' `LABEL`, `LABEL2`) and `GET https://www.spc.noaa.gov/products/watch/activeWW.json` |
| `wx_calc` | `pip install metrust`, then call the named function, e.g. `dewpoint_from_relative_humidity`, `wind_chill`, `heat_index`, `lcl` with unit strings like `"30 degC"`, `"65 percent"`; function names per `skill.md` |
| `wx_model_image`, `wx_radar_image`, `wx_storm_image`, `wx_sounding`, `wx_ecape` | install the plugin package in a scratch venv (`pip install git+https://github.com/FahrenheitResearch/hermes-weather-plugin.git`) with a Rust toolchain present and call the handlers in `tools/images.py` and `tools/calc.py` from Python; treat as best effort |

Follow the upstream usage rules: start with data tools, produce images only when the user wants to see something, use Open-Meteo for non-US locations, batch model variables (for example `cape,helicity,uh,srh`) in a single call, and pass lat/lon plus `radius_km` to zoom to the area asked about.

## Setup
1. None for the data tools; they are public endpoints without keys.
2. For calculations: `pip install metrust` (verified with `pip index versions metrust`: latest 0.5.0).
3. For imagery, soundings and ECAPE: install Rust (`cargo`, `rustc`), then the plugin package as above. Optional overrides the plugin reads: `RADAR_BACKEND` (`rustdar` default or `nexrad`), `RADAR_RENDER_PATH`, `NEXRAD_RENDER_PATH`, `ECAPE_RS_RUNNER`, `CARGO`.

## Limits
- Radar, model imagery, soundings and ECAPE depend on git-sourced Rust packages (`cfrust`, `rusbie`, `rustweather`, `wrf-rust`) and on binaries downloaded from GitHub and compiled on first use; not verified to build in this environment.
- Place-name geocoding is not part of the plugin; Claude must supply coordinates.
- NWS endpoints cover the United States only; Open-Meteo is the global fallback and returns current conditions only in this recipe.
- `skill.md` in the checkout lists 12 tools while `plugin.yaml` registers 13 (`wx_ecape` is the extra); both are reflected above.
- No LICENSE file in the checkout, so `skill.md` is summarized rather than copied.
- Endpoints are stated per `nws.py` and were not called here.

## Source
- Catalog entry (reviewed commit): https://github.com/FahrenheitResearch/hermes-weather-plugin/tree/d474493ef4ffeefabad9dbf0188f72bce3b47b67
- Catalog YAML: https://github.com/NousResearch/hermes-agent/blob/bb0c2303664edc01960fdbbb148b47acdbe553ce/plugin-catalog/weather.yaml
