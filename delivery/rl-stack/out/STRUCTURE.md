# Stack structure (constitution v1.1.0)

Every AI in the fleet reads a projection of one file. Order below is authoritative.

## Pipeline
```
0  ingress         rl-mode-sentinel         ALWAYS
1  ingress         rl-state-sync            if mode in [BUILD, FINAL_DIRECT, CONCEPTUAL] or turn references live state  [skip if mode == TALK_VISION]
2  work            thalweg-focus-engine     if turn is where-to-look OR is-this-rewrite-better about a frame/objective/plan
3  work            reticulative-data-gate   if a checkable prediction/decision is made, OR an outcome arrives, OR gate status asked
4  egress          rl-provenance-gate       if the output is about to emit ANY number, date, hash, or quantity
5  egress          rl-axis-firewall         if mode == FINAL_DIRECT or output reaches a decision-maker
6  egress          rl-verdict-cast          if turn is a decision, forecast, checkable claim, or go/no-go  [skip if mode == TALK_VISION]
7  egress_parallel rl-resonance-in-gate     if piece is outward-facing AND persuasive/selling/audience-directed
```

## Roster (who reads it, and how)
| client | kind | reads via | projection |
|---|---|---|---|
| claude | Anthropic Claude (Code + API) | `mcp_resource:rl://constitution` | claude_skill_shims |
| chatgpt | OpenAI GPT | `system_preamble` | system_preamble |
| kimi | Moonshot Kimi | `system_preamble` | system_preamble |
| gemini | Google Gemini | `system_preamble` | system_preamble |
| grok | xAI Grok | `system_preamble` | system_preamble |
| hermes | Hermes-built swarm workers | `mcp_resource:rl://constitution` | system_preamble |
| router_cascade | SLM+LLM cascade router (local + hosted tiers) | `inject` | router_inject |

## Independent axes (never conflate)
- **patent** — establishes *filed / pending (administrative fact)*; NOT *efficacy validated*
- **trademark** — establishes *registered (Reticulative Logic™, USPTO serial 99916565)*; NOT *patent, or system proven*
- **tests** — establishes *mechanism green on synthetic/injected data (ISO / DRIFT)*; NOT *field efficacy*
- **genealogy** — establishes *provenance integrity / SHA-clean corpus*; NOT *deployed / adopted*
- **expert_panel** — establishes *AI panel = PROCESS-TESTING*; NOT *human expert review (report the delta explicitly)*
- **data_gate** — establishes *cases logged*; NOT *gate MET (opens only at >=30 real labeled cases)*
- **contacts** — establishes *prospective / contacted*; NOT *committed*
