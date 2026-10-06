# Spectra-Review v2.0 — 7-Field Finding Template

> **Loaded by:** SKILL.md §Finding Schema. Round 1 always writes `default` values; subsequent rounds preserve `default` and only mutate `value` via PM Skill `/pm-bug-review` override.

## BLOCKER / CONCERN / NIT Template

```yaml
finding:
  # 1. Identification
  tier: 🔴 BLOCKER | 🟡 CONCERN | 🟢 NIT
  id: <B|C|N><N>
  name: "..."
  evidence:
    - "<target>:<line>"
  
  # 2. Severity 三件套 (Default + Override + auto-derived band)
  severity:
    score:
      value: <X>              # Round 1 = default;后续 round 可被 override
      default: <X>            # LOCKED 跨 round
      override:               # Round 1 一律 null
        by: null
        at: null
        reason: null
    band: low | med | high    # auto from value
    semantic: how_bad
  
  # 3. Fix Economics 三件套
  fix_economics:
    difficulty:
      value: <X>
      default: <X>
      override: null
    roi:
      value: <X>              # auto: severity.score.value / difficulty.value
      default: <X>
    resource_estimate:
      value: "1h|2h|4h|1d|2d|1w"
      default: "..."
      override: null
  
  # 4. Cross-Impact (LOCKED — PO cannot override)
  cross_impact:
    affected_modules: []
    cascade_depth: 1-5
    dependency_chain: "..."
  
  # 5. Phase-aware
  phase_aware:
    current_phase: 0-7
    if_not_fixed_now_breaks_at: 0-7
    estimated_rework_cost: low | medium | high
  
  # 6. Decision Tree (LOCKED — content fixed at Round 1)
  decision_tree:
    options:
      - { id: A, action: "不修", cost: <X>, notes: "..." }
      - { id: B, action: "現在修", cost: <X>, notes: "..." }
      - { id: C, action: "延後修", cost: <X>, notes: "..." }
    recommended_option: B
    counterfactual: "If do nothing, expected outcome: ..."
  
  # 7. Dependencies + Severity Decay
  dependencies:
    blocks: []                # SKILL 估
    blocked_by: []
    manual_blocks: []         # PO 加 via /pm-bug-review
  
  severity_decay:
    phase_when_found: 0-7
    by_phase:
      2: { value: <X>, default: <X>, override: null }
      3: { value: <X>, default: <X>, override: null }
      5: { value: <X>, default: <X>, override: null }
  
  # PO Decision Status (Round 1 always no_decision)
  po_decision:
    status: no_decision
    decided_at: null
    decided_by: null
    reason: null
```

## STRENGTH Template

```yaml
finding:
  tier: ✅ STRENGTH
  id: S<N>
  name: "..."
  evidence:
    - "<target>:<line>"
  
  # STRENGTH 用 preservation_value 不是 how_bad
  severity:
    score:
      value: <X>
      default: <X>
      override: null
    band: low | med | high
    semantic: how_valuable      # 對 STRENGTH 唯一改的欄位
  
  # STRENGTH 不需要 fix_economics / decision_tree / etc.
  # 簡化 schema
  
  po_decision:
    status: valued              # 預設 STRENGTH = valued accept
    decided_at: null
    decided_by: null
    reason: null
```

## Default Value Heuristics

When SKILL writes default values:

| Tier | severity.score.default | difficulty.default | resource.default |
|:---:|:---:|:---:|:---:|
| 🔴 BLOCKER | 7-10(estimate impact × probability)| 2-5(LLM estimate)| 1d-1w |
| 🟡 CONCERN | 3-5 | 1-3 | 2h-1d |
| 🟢 NIT | 0.2-1.5 | 0.5-1.5 | 1h-4h |
| ✅ STRENGTH | 5-10(preservation value)| — | — |

## Audit Rules

- `default` values written at Round 1 are LOCKED across all subsequent rounds
- `value` mutation requires explicit `override` 三件套(by/at/reason)
- Override audit entry MUST be appended to `docs/pm/<project>/decision-log.md`
- Empty `reason` is rejected (override fails)
