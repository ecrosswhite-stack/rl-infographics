---
name: jackal-verified
description: Reference and partial port of the Hermes jackal-verified plugin, a typed adapter over the JACKAL v1.7.3 verified-computation release (41 tools: exact arithmetic, canonical forms, polynomial and number-theory certificates, interval bounds, Lean-checked formal bounds for sqrt/exp/ln/sin/cos/atan/tanh and integrals, claim compilation and replay, structural test-citation checks, decision ranking, Anubis program-evidence verification). Use when the user mentions JACKAL, "jackal_exact", "formal-bounded", "replay this receipt", "verify this claim bundle", or wants exact or certified math with named refusals instead of estimates, and is on an Apple Silicon Mac where the JACKAL release can run.
---
# JACKAL Verified Computation

**Hermes original:** https://github.com/AnubisQuantumCipher/hermes-jackal-verified @ dab507a · tier: community · category: tools · license: MIT
**Port class:** C — the plugin shells out to a public, content-pinned macOS arm64 release that Claude could invoke from bash on the same platform, but the 41 typed schemas, package admission checks and refusal mapping are plugin code, and nothing here was executed or verified.

## What the Hermes plugin does
Registers 41 `jackal_*` tools (full list in plugin.yaml: `jackal_exact`, `jackal_evaluate`, `jackal_diff`, `jackal_integrate*`, `jackal_solve`, `jackal_canon`, `jackal_poly_*`, `jackal_ratfunc_canon`, `jackal_roots_isolate`, `jackal_alg_sign`, `jackal_alg_cmp`, `jackal_xgcd`, `jackal_mod_pow`, `jackal_mod_inv`, `jackal_crt`, `jackal_divides`, `jackal_prime_cert`, `jackal_range_bound`, `jackal_gaussian_integral`, `jackal_*_rat_bound`, `jackal_verify_receipt`, `jackal_claim`, `jackal_verify_bundle`, `jackal_test_exists`, `jackal_claim_cites_test`, `jackal_decision_rank`, `jackal_decision_rank_v2`, `jackal_anubis_*`) and one skill, `jackal-verified-computation`. Per tools.py it reassembles the vendored `pkg/jackal-v1.7.3-macos-arm64.tar.gz.part00/.part01` (SHA-256 `68b0e785...505ae`, 158,363,786 bytes), verifies every file against the package `SHA256SUMS`, extracts to a private 0700 directory, then runs `plugin/hermes/jackal_hermes call <tool> '<json args>'` with `shell=False`, a restricted PATH and a 180 s default timeout, and returns the single JSON object (with a `status` field) the frontend prints. Requires Apple Silicon macOS, Python 3.11+, and Z3 4.15.4 for the Anubis program lanes.

## Equivalent in Claude
Only on an Apple Silicon Mac, and only if the user accepts running the third-party native release:
1. Download `jackal-v1.7.3-macos-arm64.tar.gz` from https://github.com/AnubisQuantumCipher/jackal/releases/tag/v1.7.3 into an empty directory; check `shasum -a 256` equals `68b0e7850fcb60358633908f70ffcf405cbbef103b04d3d93dd1298789e505ae` (value from the plugin README and tools.py). Stop on mismatch.
2. Extract, `cd` into `jackal-v1.7.3-macos-arm64`, verify `shasum -a 256 -c SHA256SUMS`.
3. Invoke the same frontend the plugin invokes: `./plugin/hermes/jackal_hermes call <tool_name> '<json args>'` from the package root, with stdin closed. Tool names are the `jackal_*` names above; argument schemas live in the package's `capability_inventory_v1.json` and `plugin/hermes/tools.json` (read them first; the plugin's schemas.py is generated from them).
4. Parse stdout as one JSON object. Read `status` before any value. Preserve `refused` and `indeterminate` as terminal; never substitute a weaker numeric lane unless the user asks for one explicitly and separately.
5. Follow `references/upstream-jackal-verified-computation.md` for lane selection (claim vs bundle vs receipt vs direct tool), the formal-bounded fragments, and the rule that `expected_*` pins come from the caller, never from the artifact being verified.

| Hermes tool | How Claude does it |
|---|---|
| any `jackal_<name>(args)` | `./plugin/hermes/jackal_hermes call jackal_<name> '<args json>'` inside the verified package |

## Setup
1. Apple Silicon macOS, Python 3.11 or newer; for `jackal_anubis_*` also Z3 4.15.4 (plugin pins binary SHA-256 `ae6c8df3...594f48`).
2. Download and verify the release as in step 1 above. No env vars are used by the plugin.

## Limits
- Not verified: the frontend's CLI contract (`call <tool> <json>`) was read from the plugin source, not run. Treat the first invocation as an experiment and report what happens.
- Not replicated: the 41 typed tool schemas with argument-length limits (`max_expression_chars` 8192), the TOCTOU re-hashing around each call, named local refusals (`plugin-admission-failed`, `plugin-timeout`, ...) and EPOCH/MANIFEST drift checks.
- macOS arm64 only; Linux and Windows hosts, including Claude's cloud sandbox, cannot run it.
- The release is native code from a third party and is not a sandbox; the user decides whether to run it.
- SHA-256 identifies bytes only; it is not a correctness or authenticity proof (the plugin README says the same).

## Source
- Catalog entry (reviewed commit): https://github.com/AnubisQuantumCipher/hermes-jackal-verified/tree/dab507a521406a69d308025bed380401eff967b9
- Catalog YAML: https://github.com/NousResearch/hermes-agent/blob/bb0c2303664edc01960fdbbb148b47acdbe553ce/plugin-catalog/jackal-verified.yaml
