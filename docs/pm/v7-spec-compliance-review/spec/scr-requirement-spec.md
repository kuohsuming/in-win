---
title: V7 Specification Compliance Reviewer — Requirement Spec
version: 0.3.0
status: proposal-draft
created: 2026-06-29
last_updated: 2026-06-30
author: PO + Claude(co-authored)
review_iteration: 9  # rev 0.2.6 ship-as-is(Round 2 c81690b);rev 0.3.0 = rev 0.3 cycle bundle close — 4 NIT(N1 § 8 heading rename / N7 chitchat scope narrowed / N10 collapse markdown 1-line bullet decision / N11 § 8.13 Invocation Lifecycle numbered flow chart NEW)+ per `[[incremental-rev-cascade]]` 4-NIT bundle 1 cohesive rev(non-mega-rev)
schema_version: req-spec-v1.1
related:
  - docs/pm/dev-workflow-orchestrator/spec/orchestrator-requirement-spec.md  # Phase 4.5 host
  - ~/.claude/skills/spectra-review/SKILL.md  # 5-section schema reuse
  - docs/archives/htmljscss2claude_v2ui_20260512.tar.gz:htmljscss2claude_20260512/skills/namecard-v2-ddd-guardian/SKILL.md  # V0-V6 host
  - docs/reviews/2026-06-29-scr-poc-sanity-tc-impl-L1-L2.md  # Stage 5 PoC dogfood evidence (commit 2432c7b)
fidelity_markings:
  - 🎤 verbatim PO quote
  - 📝 Claude paraphrase
  - ❓ Claude inference(needs PO confirmation)
tier_scope:
  rev_0_1: Tier 1 only(6 items)
  rev_0_1_1: Tier 1 + 9/11 R1-patch + R2 ship-as-is (commit 40f42c5)
  rev_0_2: Tier 2(5 items)+ N4-N5 R1-patch defer + N7-N10 R2 defer + ⭐ spec scope declaration mechanism (PoC blocker insight) + § 6.2.1 校正 (PoC finding) + V-005/V-006 (PoC defer NITs)
  future:  Tier 3(4 items — deferred indefinitely until Stage 5 PoC evidence on additional projects)
---

# V7 Specification Compliance Reviewer — Requirement Spec rev 0.1

> 👔 **For PM:** SCR 是一個確保 code 真的對齊 spec(req/func/design)的 review skill,目的是把「code 過 lint = ship-ready」這個假議題,升級成「code 過 SG Gate = 真實 spec-compliant ship-ready」。
>
> 🔬 **For QA:** SCR 給你雙向 traceability — REQ → code 抓 missing implementation,code → REQ 抓 unspec'd 程式碼。SG Gate threshold maturity-aware(MVP/GA/mature)避免 100% 強制過嚴。
>
> 💻 **For Developer:** SCR 不 auto-apply fix(對齊 `[[backend-change-rule]]`),只 report violations。落地後你的每個 PR 在 Phase 4.5 會經過 4.5b SCR(與 4.5a spectra-review / 4.5c lint / 4.5d pytest / 4.5e smoke 並列),fail BLOCKER 擋住 Phase 5 release note。emergency 可用 `--bypass=urgent-fix` token escape,但須 retroactive 補回 SG pass。

---

## § 1. Context

### § 1.1 Proposal genesis(2026-06-29 single-session multi-turn 收斂)

本 proposal 在 2026-06-29 single session 累積 5 turn 收斂 — 對齊 D-012 fidelity invariant(orchestrator decision log)pattern,本 § 區分 🎤 verbatim quote / 📝 paraphrase / ❓ inference 三層次。

> ⚠ **rev 0.1.1 N1 fidelity correction:** 以下各 Turn timestamp(~17:55 / ~17:58 / ~18:00 / ~18:02 / ~18:05)皆為 ❓ Claude inference based on session pacing — 非 verbatim wall-clock。實際 timestamp 待 transcript JSONL 取(`~/.claude/projects/-home-hsuming-AzureLineBOT-main/<session-id>.jsonl`)校準;校準前以「Turn 順序」為 canonical。

#### Turn 1(❓ ~17:55+08:00 inference)— PO propose SCR baseline

**🎤 PO 觸發 verbatim:**
> 「我想與你討論建立 Specification Compliance skill or let it be v7. here is clear idear regarding compliance ..」
>
> 「Review 的對象不是 Code。Review 的對象是:Requirement → Functional → Design → Code」
>
> 「我會拆成五個 Reviewer。Review 1 Requirement Coverage / Review 2 Functional Compliance / Review 3 Design Compliance / Review 4 Design Pattern Compliance / Review 5 Coding Standard」
>
> 「我還會增加一個 Missing Traceability Review」
>
> 「Specification Gate(SG)... 整個 AI Software Factory 的流程會變成:RG → FG → DG → IG → ⭐SG → TG → ReG」

**📝 Claude paraphrase of intent:**
- PO 的核心 inversion:Code 是 Evidence,Review target 是 spec layers 對 code 的合規性
- 5+1 reviewer decomposition(5 directional + 1 traceability)是 orthogonal dimension
- SG 是 Specification Gate,在 IG(impl gate)之後 / TG(test gate)之前必過
- Pipeline 概念跨 7 gate(RG → FG → DG → IG → SG → TG → ReG)— 對齊 AI software factory 全流程

**❓ Claude inference(待 PO 驗證):**
- SG threshold 是否如 PO 例「Requirement Coverage 100% / Functional 100% / Design ≥95%」hard pin,還是 maturity-aware?(後續 Turn 4 確認 maturity-aware)
- 7-gate pipeline 是否要 Stage 1 全 codify,或先 codify SG 一個?(本 proposal 先 SG,RG/FG/DG/IG/TG/ReG defer future round)

#### Turn 2(❓ ~17:58+08:00 inference)— Claude 4-gap critique + 3-option recommendation

**📝 Claude action:**
- 給 4 critical gap:detection algorithm reliability / spec format prerequisite / architecture spec explicit-ness / unspec'd impl FP risk
- 給 3 implementation option:Option A new V7 skill / Option B extend spectra / Option C hybrid(V7 SCR + orchestrator chain)
- 推薦 Option C — 解耦 spec quality vs spec compliance,orchestrator 統一 chain
- 推薦 next step:meta-circular 8-phase Stage 1 propose-first(對齊 orchestrator pattern)

#### Turn 3(❓ ~18:00+08:00 inference)— PO 問 refinements

**🎤 PO verbatim:**
> 「any comments make it better?」

**📝 Claude paraphrase of intent:**
- V1 Discussion mode 持續 — PO 要 critical refinement 而非立即 impl
- 開放性詢問,Claude 應提全面 refinements 而非單點 patch

#### Turn 4(❓ ~18:02+08:00 inference)— Claude 提 15 refinement(Tier 1/2/3)

**📝 Claude action:**
- 提 15 個 refinements 分 Tier 1 / Tier 2 / Tier 3
- Tier 1(6 個 must-add):reorder + R0 self-consistency / version pin / coverage methodology / threshold maturity-aware / bypass token / memory invariants
- Tier 2(5 個 should-add):detection tier / cost-staged / bi-dir anchor scope / actionable report / per-stack adapter
- Tier 3(4 個 nice-to-have):confidence score / test gen loop / multi-repo / self-test corpus
- 提 5 個 implementation path 選項
- 推薦「Tier 1 only rev 0.1 → spectra-review → Tier 2 rev 0.2」 incremental rev pattern

#### Turn 5(❓ ~18:05+08:00 inference)— PO decision

**🎤 PO verbatim:**
> 「Y go Option C + Stage 1 propose-first, 先 Tier 1 only 寫 rev 0.1 → Round 1 spectra-review → Tier 2 進 rev 0.2」

**📝 PO 回應與見解 — Claude reading:**
- ✅ 接受 Option C(hybrid V7 + orchestrator chain)
- ✅ 接受 Stage 1 propose-first(對齊 orchestrator meta-circular pattern)
- ✅ 接受 Tier-split incremental(rev 0.1 Tier 1 / rev 0.2 Tier 2)
- ✅ 接受 Round 1 spectra-review mandate(對齊 D-008 「review 也是得照程序走」principle)
- ❓ Tier 3 不在 PO 訊息明示 — Claude 推斷「未來 PoC 後再 decision」(本 spec § 14.2 紀錄)

**❓ Claude 推測 5 個 inference points 標明:**

| # | Inference point | 待 PO 驗證 |
|:---:|:---|:---|
| 1 | SCR skill 命名 `/spec-compliance-review` vs `/scr` 短形 vs `/v7-scr` | Stage 5 impl 階段拍板 |
| 2 | SG 之外的 RG/FG/DG/IG/TG/ReG 6 gate 是否同 proposal codify | 本 rev 預設 only SG,其餘 defer |
| 3 | Maturity threshold 邊界值(MVP=70% / GA=95% / mature=100%)是否 final | Phase 1 PoC 後 calibrate |
| 4 | R0 7th reviewer 是否所有 project 強制,或 1-layer spec 可 skip | § 4.1 預設強制,OQ 列彈性 |
| 5 | SG-Bypass token 觸發是否需 PO 親自簽核 vs Claude 自主判斷 | § 7.2 預設 PO 簽核 + audit log |

### § 1.2 Why a 7th AI mode(V7)— dual-name design + mode-skill pair contract

> **rev 0.2.3 OQ-T1-1 closure(per PO 2026-06-30 directive 「spec-compliance-review,並在 v0~v6 裡擴充 v7 內部執行呼叫 spec-compliance-review」):**
>
> SCR 採 **dual-name pattern** — 1 abstract mode + 1 concrete skill:
>
> | Layer | Name | Purpose | Precedent |
> |:---:|:---|:---|:---|
> | **Mode** | **V7**(對齊 V0-V6 framework)| AI agent operating mode — 對應 user mental model「我想做 spec compliance review」 | V3 Review mode / V5 DDD Convergence mode |
> | **Skill** | **`/spec-compliance-review`**(slash command)| Concrete review engine — R0-R6 7-reviewer architecture executable | `/spectra-review`(對齊 V3)/ `namecard-v2-ddd-guardian`(對齊 V5)|
>
> **Invocation contract(V7 mode internally invokes skill):**
>
> ```
> User: "v7 <target>"  OR  "/spec-compliance-review <target>"
>   ├─ V7 mode dispatcher(ai-principles.md §3 Mode Map)
>   │     └─ V7 internally invokes `/spec-compliance-review` skill
>   │
>   OR
>   └─ User 直接 `/spec-compliance-review <target>` bypass V7 mode wrapper
>          └─ Same skill execution path
> ```
>
> **Both paths converge** to SCR R0-R6 execution → SG 4-state verdict。User 可二選一(對齊 V3 + `/spectra-review` user choice pattern)。
>
> **Implementation:** Stage 7 並列 land:(a) `~/.claude/skills/spec-compliance-review/SKILL.md` 寫作(主 entry)+ (b) `ai-principles.md` §3 Mode Map 加 V7 entry(propose-first per `[[backend-change-rule]]` L1 protection — separate cascade)。

---

#### Why V7 needed — 與既有 V0-V6 / spectra / orchestrator 邊界

| 既有 | Niche | 與 SCR 區別 |
|:---|:---|:---|
| **V0 Bootstrap** | Repo-aware onboarding | Not review-tool |
| **V1 Discussion** | Open-ended chat | Not enforce-tool |
| **V2 Direct Dev** | Coding execution | Not review-tool |
| **V3 Code Review** | Code quality(naming / dead code / security)| 不 review spec compliance |
| **V4 Doc Proposal** | Spec drafting | Not review code |
| **V5 DDD Convergence** | Cross-context coherence | 不 measure coverage % |
| **V6 Long-form Analysis** | Multi-doc analysis | Not real-time gate |
| **spectra-review enhanced-v1** | Spec internal drift(naming / completeness / cross-section)| Target = spec text;not code-vs-spec |
| **`[[backend-lint-workflow]]` ruff/mypy** | Lint / type error | Not semantic spec match |
| **V7 SCR(本 proposal)** | **Code ↔ 3-layer spec bi-dir compliance** | **niche niche niche** |

V7 與 V3 在功能上互補非競爭:
- **V3:** Code 寫得「好」嗎?(naming / DRY / pattern)
- **V7:** Code 寫得「對」嗎?(對齊 spec 嗎?)

### § 1.3 Scope / Out of Scope

**In scope(rev 0.2 — Tier 2 + R1/R2 defer carryovers + Stage 5 PoC findings):**
- (rev 0.1 Tier 1 inherit:) 7 reviewer architecture / Coverage % methodology / SG Gate threshold / SG-Bypass token / Spec Version Pin / Memory-bound invariants
- **NEW Tier 2.1:** Detection algorithm tier per reviewer(L1-L5 hybrid)
- **NEW Tier 2.2:** Cost-staged invocation tier(light / medium / heavy)
- **NEW Tier 2.3:** Bi-directional traceability anchor scope
- **NEW Tier 2.4:** Actionable Compliance Report enhancements(top-10 + quick-wins + trendline)
- **NEW Tier 2.5:** Per-stack adapter layer(Python / JS / HTML / SQL / YAML)
- **NEW PoC critical(⭐ BLOCKER must-add per Stage 5 PoC):** Spec scope declaration mechanism(`scr_scope` PR/commit metadata + scope-aware R2 coverage calc)
- **NEW PoC finding:** § 6.2.1 state.md backfill list 5 處不對齊 校正
- **R1-patch defer carryover:** N4(§ 4.8 dependency graph prose)+ N5(§ 14.3 OQ-T1-1 deadline)
- **R2 defer carryover:** N7(§ 4.1 Detection focus per-mode)+ N8(§ 2 sync invariant ownership)+ N9(§ 6.2.1 conditional ambiguity)+ N10(§ 7.4 decision-log dual path)
- **PoC defer NIT:** V-005(§ 4.1 heading levels H2/H3 check)+ V-006(REQ-025 B vs REQ-024 A cross-ref drift — sanity-check spec-side concern,本 SCR spec 不直接 patch but acknowledge)

**Out of scope(future / Tier 3 / never):**
- Auto-apply fix(violates `[[backend-change-rule]]`)
- 6-gate(RG/FG/DG/IG/TG/ReG) full codify(只 SG codify;其餘 acknowledge but defer)
- Multi-repo / cross-service SCR(deferred until microservice 出現)
- Tier 3:AI confidence score + self-test corpus + test gen integration loop + multi-repo SCR(全 deferred indefinitely until additional Stage 5 PoC evidence)

---

## § 2. Memory-bound Invariants(Tier 1.6)

SCR 必須嵌入既有 memory rules — 不可違反。本 § 列 enforce-able rules(排除 project-state-only / resolved 類 memory);rev 0.1.1 Round 1-patch C1 補列 4 條(human-first-docs / backend-lint-workflow / v3-backend-contract-source-rule / v1-ui-retired)後共 17 條:

| # | Memory rule | SCR enforcement point |
|:---:|:---|:---|
| 1 | `[[backend-change-rule]]` | SCR 不可 auto-apply fix;只 report violations。SCR 找到 *.py violation → propose-first,等 PO 授權後改 |
| 2 | `[[backend-schema-change-workflow]]` SSOTs plural | R0 必 cross-check laundry SSOT + sanity SSOT。R5 Architecture 抓 hub-issue cascade 漏 inline footnote |
| 3 | `[[audit-patch-cascade-verify]]` 5-dim | SCR fix violation 後必 cascade 5-dim verify:(a) cross-file grep / (b) intra-file grep / (c) commit-time evidence / (d) Round N+1 verify / (e) external state verify |
| 4 | `[[public-vs-private-friend-data]]` | R5 special check — friend data public/private boundary 不可混淆;新 friend text field 必 trigger PII boundary review |
| 5 | `[[friend-fetch-cost]]` | R5 抓 bulk fetch(`last_days` API)anti-pattern;Browse=latest_newadd:10 + search=keyword 為合規 |
| 6 | `[[delete-dialog-no-undo-hint]]` | R6 UX pattern rule — 刪除 confirm dialog 文案禁含「隱藏 / 可還原 / 軟刪 / 資料保留」 |
| 7 | `[[dep-management]]` | R5 抓 requirements.txt unauthorized add;OS-related 必 Azure Linux 3.0 兼容 |
| 8 | `[[v3-default-ui-mainline]]` | R5 抓 V2 UI dev attempt(frozen) — 非 PROD V2 過渡期改動 = violation |
| 9 | `[[profile-bizcard-invariant]]` | R5 抓 「profile 無 main_bizcard」 invariant violation |
| 10 | `[[sender-discard-silent]]` | R5 抓 discard 行為 leak label/banner/hint 到 receiver |
| 11 | `[[receiver-edit-invariant]]` | R5 抓 RBT update path 加 sender side guard |
| 12 | `[[sanity-check-bug-fix-direct-main-rule]]` | § 7 SG-Bypass token 對齊此 rule — bug fix 同 session 可 skip Phase 1-6 |
| 13 | `[[profile-json-ssot]]` | R0 抓 V3 identity invariant 讀錯 source(BCT cards array vs profile JSON sub-key) |
| **14** | **`[[human-first-docs]]`(NEW rev 0.1.1)** | R6 抓 spec / proposal 文件 missing 3-role perspective(👔 PM / 🔬 QA / 💻 Developer);YAML metadata 退到 frontmatter |
| **15** | **`[[backend-lint-workflow]]`(NEW rev 0.1.1)** | R6 reuse `bash lint.sh`(ruff F821/F)不增 baseline 才 commit;catch attr typo 等 mypy 已知限制 |
| **16** | **`[[v3-backend-contract-source-rule]]`(NEW rev 0.1.1)** | R4 Design Compliance 抓 V3 cmd/response 形狀 — 嚴格依 V2 UI 已實作;V2 無解才退 V1 UI;不可依 mock 假設 |
| **17** | **`[[v1-ui-retired]]`(NEW rev 0.1.1)** | R5 抓 V1 LIFF page 新功能 dev(生產 retired);V1 code 僅可作設計參考,不可新增 path |

> **Invariant Statement(rev 0.1.1 strengthened):**
>
> 1. 上述 17 條 memory rules 皆為 SCR 之 inviolable invariant。SCR 自身 spec / code / report 若被發現違反任一條 → 該 SCR run 結果 invalid,須 restart。
> 2. **Sync invariant:** 本 list 隨 `~/.claude/projects/-home-hsuming-AzureLineBOT-main/memory/MEMORY.md` 增刪 sync;每 rev 升必 cascade audit(grep MEMORY.md 全 entry 標 enforce-able vs project-state-only,confirm 對齊本 § list count)。
> 3. **Future memory rule add path:** 新 memory rule add 後 trigger SCR rev minor bump(rev 0.1.1 → 0.1.2)補列;漏列發現後 retroactive 補入 + Round N+1 spectra cascade verify。
> 4. **Sync ownership(rev 0.2 N8 closure):** Sync 責任分配:
>    - **MEMORY.md update event 觸發者:** PO 或 Claude(per `[[backend-change-rule]]` propose-first round)
>    - **Sync 執行者:** Claude 自動 propose SCR § 2 + § 6.3 always-zero cascade audit;output 為 propose-first artifact 給 PO sign-off
>    - **Sign-off + rev bump:** PO 簽核後,Claude 執行 SCR rev minor bump(eg. 0.2.0 → 0.2.1)+ 更新 decision-log + cascade Round N+1 spectra verify
>    - **Audit cadence:** 每 SCR rev bump 時 mandatory full sync audit(`grep MEMORY.md 全 entry vs § 2 list`)— 不是 ad-hoc 而是 invariant per audit-patch-cascade 5-dim invariant `(e)external state verify` dim

---

## Requirements

> **canonical anchor section(2026-07-02 OD-5 option A):** 下列 13 個 discrete REQ-XXX 是本 spec 的 **canonical requirement anchors**,對齊 `docs/pm/spec-authoring/requirement-spec-authoring-rules.md §3`(REQ ⇄ golden_scenario ⇄ anti_examples 三元組不變式)+ §2.5 admission gate + PM skill `§6.4.10 §B.4` 11-field schema。
> **與既有 § 之關係:** 每個 REQ block 是 canonical anchor;既有 § 4.x reviewer / § 5-9 tier methodology / § 13 acceptance criteria 為其 **detailed elaboration**(仍為 SSOT of behavioral detail)。每個被 anchor 的 § 均附 `> Requirement anchor: REQ-0XX` cross-link。REQ 皆 grounded 於既有 spec 內容(見各 `source_evidence`),無 invented scope。
> **Triad:** 每 REQ 恰 1 `golden_scenario`(Given/When/Then)+ ≥ 1 `anti_examples`(1:N 邊界)per §3 INV-1/INV-2。

### REQ-001: R0 Spec Cross-Layer Consistency Pre-Gate

```yaml
id: REQ-001
title: R0 Spec Cross-Layer Consistency Pre-Gate
description: |
  SCR 執行任何 code review 之前,R0 reviewer 必先驗證 spec 自身正確(cross-layer
  ID mapping / semantic conflict / freshness / heading levels / ID 唯一性)。R0 mode
  依 project spec layer 數自動 detect(R0-full 3-layer / R0-medium 2-layer / R0-lite
  1-layer)。R0 verdict 為 binary(pass/fail);fail → SCR 全 abort,return「fix spec
  layers first」,R1-R6 不跑。
priority: P0
rationale: |
  spec 自身矛盾則無 review code 的 ruler(§ 3.2 4 critical gap 之 spec format
  prerequisite + architecture explicit-ness);R0 fail 屬 § 6.3 always-zero gate。
acceptance:
  - R0 依 docs/pm/<project>/spec/ 內 *-requirement-*/*-functional-*/*-design-* file 數 auto-pick full/medium/lite mode
  - R0-full 對 REQ-XXX↔FUNC-YYY↔DESIGN-ZZZ 3 層 ID mapping + semantic conflict 全檢
  - Heading levels 僅允 H1(title)/ H2(## § N.)/ H3(### § N.M.);H4+ 或 skip-level → fail
  - R0 fail → SCR abort + 標 spec drift bug + R1-R6 不執行(§ 6.3 always-zero)
golden_scenario: |
  Given 一個 3-layer spec project,requirement 寫「export PDF」但 design 寫「only CSV」
  When SCR 開跑,auto-detect 為 R0-full mode 並跑 cross-layer semantic check
  Then R0 verdict = fail,SCR abort,return「fix spec layers first」,R1-R6 不執行,SG always-zero
anti_examples:
  - ❌ R0 semantic conflict 存在但 SCR 照跑 R1-R6 並回報 coverage %(spec ruler 自身錯,結果 meaningless)
  - ❌ 1-layer(only req)project 因無 func/design 就 skip R0(應降級 R0-lite 仍跑 ID 唯一性 + 內部 self-consistency)
  - ❌ spec 用 H4 heading 或 `#`→`###` skip-level 但 R0 判 pass
dependencies:
  blocked_by: []
  blocks: [REQ-002, REQ-003, REQ-004, REQ-005, REQ-006, REQ-008]
proposed_module: r0-spec-cross-layer
source_evidence: "§ 4.1 R0 Spec Cross-Layer Consistency Reviewer;§ 3.2 gap 表;§ 6.3 always-zero gates;§ 4.8 dependency graph"
```

### REQ-002: R1 Bi-directional Traceability Map

```yaml
id: REQ-002
title: R1 Bi-directional Traceability Map
description: |
  R1 reviewer 建立 spec ↔ code 雙向 mapping(spec_to_code + code_to_spec）供 R2-R5
  consume。對 spec 每 REQ-XXX/FUNC-XXX/DESIGN-XXX grep codebase reference;對每 code
  entry-point 反查 REQ link。REQ-tag mandatory scope 依 § 5.4 anchor matrix(public
  entry-point / service / invariant guard = MUST;internal helper / test fixture /
  generated = free pass)。R1 自身不報 violation,只 produce data。
priority: P0
rationale: |
  bi-dir traceability 是 SCR core niche(§ 3.1 「Code ↔ 3-layer spec bi-dir
  compliance」);free-pass scope 避免 unspec'd impl false-flag(§ 3.2 FP risk gap)。
acceptance:
  - 輸出 traceability map(spec_to_code list + code_to_spec list)per § 4.2 schema
  - REQ-tag mandatory 僅套 § 5.4 anchor matrix 之 ✅ MUST scope;free-pass scope 自動 skip 不計 unspec'd
  - 多 anchor type 疊加(§ 5.4 N3):任一 anchor MUST → function 適用 MUST,1 個 REQ-tag 覆蓋全 anchor
  - stack adapter unavailable → 降級 L1 regex string match + emit warning,不 fail(§ 4.10 fallback chain)
golden_scenario: |
  Given src/api/export.py:42 是 Flask route(public entry-point,§ 5.4 ✅ MUST)且 tag 了 :requirement: REQ-005
  When R1 建立 traceability map
  Then spec_to_code[REQ-005] 含 export.py:42,code_to_spec[export.py:42] 含 REQ-005,且該 entry-point 不列為 unspec'd
anti_examples:
  - ❌ 對 internal helper `_format_date()`(free pass)強制要求 REQ-tag 並 flag 為 unspec'd entry-point
  - ❌ R1 自身直接報 violation / 打 verdict(R1 只 produce map,violation 由 R2-R5 算)
  - ❌ Python stack adapter 缺失時直接 fail,而非降級 L1 regex + warning
dependencies:
  blocked_by: [REQ-001]
  blocks: [REQ-003, REQ-004, REQ-005, REQ-006]
proposed_module: r1-traceability
source_evidence: "§ 4.2 R1 Traceability Reviewer;§ 5.4 anchor scope matrix;§ 4.10 per-stack adapter fallback chain"
```

### REQ-003: R2 Acceptance-Criteria Coverage Quantification

```yaml
id: REQ-003
title: R2 Acceptance-Criteria Coverage Quantification
description: |
  R2 reviewer 以 acceptance criteria(非 REQ 數本身)為 base unit 計算 req spec → code
  coverage %,採 3-tier partial scoring(0 / 0.5 / 1)。coverage % 依 § 8.4 declared
  scope 計算(scoped coverage 進 SG gate;full-spec coverage 並列 report 不進 gate)。
priority: P0
rationale: |
  REQ 大小不一(1 vs 8 AC),用 REQ 數計算會 distort(§ 5.1 rationale);scoped
  coverage 解 § 8.4 PoC BLOCKER(scoped impl 被 false-flag 為 SG fail)。
acceptance:
  - coverage_% = (fully_impl_AC + 0.5 × partial_impl_AC) / total_AC × 100(§ 5.1 formula)
  - partial scoring 0/0.5/1 依 R1 map spec_to_code list + sub-step grep binary heuristic(§ 5.2,rev 0.1 不依賴 LLM)
  - declared scope 存在時 R2 base = scoped coverage;full-spec coverage 並列 report(§ 8.4)
  - coverage < 100% 時 mandatory 輸出 per-REQ coverage gap enumeration(complete/partial/missing + missing sub-AC,§ 5.6)
golden_scenario: |
  Given REQ-024 有 3 個 sub-AC,其中 A/E/F 已 impl、B/C 未 impl,且 scope 宣告含 REQ-024
  When R2 計算 scoped coverage
  Then REQ-024 status=partial score≈0.7,coverage gap enumeration 明列 missing_sub_ac=[B, C]
anti_examples:
  - ❌ 用「已 impl REQ 數 / 總 REQ 數」當 coverage %(base unit 錯,§ 5.1 禁)
  - ❌ coverage 顯示 78% 但不列出哪個 REQ partial / missing(§ 5.6 PO directive 明示必列)
  - ❌ 對 scoped impl(僅宣告 3 REQ)計算 full-spec coverage 並判 SG fail(§ 8.4 BLOCKER)
dependencies:
  blocked_by: [REQ-001, REQ-002]
  blocks: [REQ-008, REQ-011, REQ-012]
proposed_module: r2-req-coverage
source_evidence: "§ 4.3 R2 Requirement Coverage;§ 5.1-5.3 coverage methodology;§ 5.6 coverage gap enumeration;§ 8.4 scoped coverage"
```

### REQ-004: R3 Functional Flow Compliance

```yaml
id: REQ-004
title: R3 Functional Flow Compliance
description: |
  R3 reviewer 驗證 code 實現的 functional flow 對齊 func spec 流程 —— 對每 FUNC-XXX
  flow(eg. Login → OTP → JWT → Dashboard)AST-parse code 追 call chain,抓 missing
  step / extra step / out-of-order step,輸出 compliance %。
priority: P1
rationale: |
  coverage % 只量 REQ 對齊,不保證 functional flow step 順序正確;R3 補此 dimension
  (§ 4.4);flow step 需 semantic understanding,default detection tier = L4(§ 5.5)。
acceptance:
  - 對每 FUNC-XXX flow AST-parse code call chain,verify 每 step 真實存在(§ 4.4)
  - 抓 missing_step / extra_step / out_of_order 並計 compliance_percent(§ 4.4 schema)
  - v3-backend-contract-source-rule:V3 cmd/response 形狀嚴格依 V2 UI 已實作,不依 mock 假設(§ 2 rule 16)
golden_scenario: |
  Given FUNC-008 flow 宣告 Login → OTP → JWT → Dashboard 4 step,但 code 直接 Login → JWT
  When R3 AST-parse code call chain 對齊 flow
  Then R3 output 對 FUNC-008 記 missing_step=[OTP],該 flow status ≠ fully_compliant,且 aggregate compliance_percent < 100(未達全 flow 對齊)
anti_examples:
  - ❌ code call chain 缺 OTP step 但 R3 仍判 FUNC-008 fully_compliant
  - ❌ R3 依 mock/假設 判 flow 對齊,而非依 V2 UI 已實作 contract(§ 2 rule 16 violation)
  - ❌ code 多插一個 spec 未宣告的 step 但 R3 不標 extra_step
dependencies:
  blocked_by: [REQ-001, REQ-002]
  blocks: [REQ-008]
proposed_module: r3-functional
source_evidence: "§ 4.4 R3 Functional Compliance Reviewer;§ 5.5 per-reviewer detection tier(R3=L4);§ 2 memory rule 16"
```

### REQ-005: R4 Design Component & Interface Compliance

```yaml
id: REQ-005
title: R4 Design Component & Interface Compliance
description: |
  R4 reviewer 驗證 code 結構對齊 design spec 之 component / interface 規範 —— 對每
  DESIGN-XXX component verify code 真實存在對應 class/module,並比對 interface
  signature(method name / param / return type),抓 signature drift / missing
  component / interface incompatibility。
priority: P1
rationale: |
  R2/R3 不檢 code 結構層 signature 對齊;R4 補 component-level compliance(§ 4.5);
  signature drift L3 deterministic detection 足夠(§ 5.5)。
acceptance:
  - 對每 DESIGN-XXX verify 對應 class/module 存在 + signature 對齊 design 規約(§ 4.5)
  - 抓 signature drift / missing component / interface incompatibility(§ 4.5)
  - per-stack adapter signature_compare() 回 typed Drift list(§ 4.10 adapter API)
golden_scenario: |
  Given DESIGN-007 宣告 FriendBizcardService.update(id: int) -> bool,但 code 實作 update(id: str) -> None
  When R4 對比 code signature vs design 規約
  Then R4 回報 Drift(kind=type_mismatch + return_type_drift),標 interface incompatibility
anti_examples:
  - ❌ code signature 與 DESIGN-007 param type 不符但 R4 判 pass
  - ❌ design 宣告的 component 在 code 完全缺失但 R4 不標 missing_component
  - ❌ R4 對無 design layer 宣告的 flat project 硬套 component check(應 skip design dimension)
dependencies:
  blocked_by: [REQ-001, REQ-002]
  blocks: [REQ-008]
proposed_module: r4-design
source_evidence: "§ 4.5 R4 Design Compliance Reviewer;§ 4.10 adapter signature_compare/Drift;§ 5.5 per-reviewer tier(R4=L3)"
```

### REQ-006: R5 Architecture Pattern & Memory-Rule Invariant Enforcement

```yaml
id: REQ-006
title: R5 Architecture Pattern & Memory-Rule Invariant Enforcement
description: |
  R5 reviewer 驗證 code 對齊 design 之 architecture pattern(layer skip / 反向
  dependency)並落地 § 2 之 17 條 inviolable memory-rule invariant(profile-bizcard /
  sender-discard-silent / friend-fetch-cost / dep-management / v3-default-ui-frozen
  等)。memory rule violation 屬 § 6.3 always-zero gate(0 容忍,不分 maturity)。
priority: P0
rationale: |
  memory rules 是 repo law(§ 2 invariant statement:違反任一條 → SCR run invalid);
  architecture layer skip / 反向依賴會腐蝕結構(§ 4.6);兩者皆須專責 reviewer。
acceptance:
  - design 宣告 layer 時 grep import graph 驗 Controller→Service→Repository,抓 layer skip / 反向 dependency(§ 4.6)
  - 無 explicit layer 宣告(flat Flask)→ layer dimension skip,但 memory rule check 仍跑(§ 4.6 skip condition)
  - § 2 之 17 條 memory rule 全數在 R5 落地;任一違反 → SG always-zero fail(§ 6.3 gate 2)
  - § 2 list 隨 MEMORY.md sync,每 rev bump mandatory full sync audit(§ 2 sync invariant)
golden_scenario: |
  Given commit 新增 friend text field 導致 sender discard 身份 leak 一個 banner hint 到 receiver
  When R5 跑 memory-rule cross-cutting check(§ 2 rule 10 sender-discard-silent)
  Then R5 標 memory-rule violation → SG always-zero,該 SCR run 結果 invalid 直至 fix
anti_examples:
  - ❌ Controller 直接呼叫 SQL 跳過 Service/Repository(layer skip)但 R5 不標 architecture violation
  - ❌ commit bulk-fetch friends via last_days API(§ 2 rule 5)但 R5 放行(memory rule 0 容忍被違反)
  - ❌ memory rule violation 存在但 SG 因 maturity=MVP 而寬容放行(§ 6.3 memory rule always-block)
dependencies:
  blocked_by: [REQ-001, REQ-002]
  blocks: [REQ-008]
proposed_module: r5-architecture
source_evidence: "§ 4.6 R5 Architecture Compliance Reviewer;§ 2 Memory-bound Invariants(17 rules);§ 6.3 always-zero gates"
```

### REQ-007: R6 Coding Standard via Existing Lint Reuse

```yaml
id: REQ-007
title: R6 Coding Standard via Existing Lint Reuse
description: |
  R6 reviewer 檢 PEP8 / naming / lint / dead code / security baseline —— 直接 reuse
  既有 `bash lint.sh`(ruff F821/F + baseline)per [[backend-lint-workflow]],不增
  baseline 才 commit,並加 UX pattern rule([[delete-dialog-no-undo-hint]] 文案
  check)。R6 無 SCR-specific LLM call,cost 最低,可與 R1-R5 完全並行。
priority: P1
rationale: |
  lint 與 spec 無關故可獨立並行(§ 4.8 R6 island);reuse 既有 tooling 避免重造;
  lint baseline 增加屬 § 6.3 always-zero gate。
acceptance:
  - reuse 既有 bash lint.sh(ruff F821/F + baseline),不自建 detection logic(§ 4.7,detection tier=L1)
  - lint baseline 增加 → SG always-zero fail(§ 6.3 gate 4 + [[backend-lint-workflow]])
  - 加 [[delete-dialog-no-undo-hint]] 刪除 confirm dialog 文案 check(禁「隱藏/可還原/軟刪/資料保留」)
  - R6 可與 R1-R5 並行,不依賴 R1 map(§ 4.8 island)
golden_scenario: |
  Given commit 新增刪除 confirm dialog 文案含「資料仍會保留」且 ruff 多 1 個 F821 baseline
  When R6 跑 lint reuse + UX pattern check
  Then R6 標 lint baseline +1(always-zero fail)+ delete-dialog 文案違規
anti_examples:
  - ❌ R6 自建一套 lint 引擎而非 reuse bash lint.sh(§ 4.7 reuse 原則)
  - ❌ lint baseline 增加但 R6 因 maturity 寬容放行(§ 6.3 lint baseline 不可增)
  - ❌ R6 被排成必等 R1 map 才能跑(應為 island 並行)
dependencies:
  blocked_by: []
  blocks: [REQ-008]
proposed_module: r6-coding-standard
source_evidence: "§ 4.7 R6 Coding Standard Reviewer;§ 4.8 R6 island 並行;§ 6.3 gate 4;§ 2 rules 6/15"
```

### REQ-008: SG 4-State Maturity-Aware Verdict Gate

```yaml
id: REQ-008
title: SG 4-State Maturity-Aware Verdict Gate
description: |
  SG(Specification Gate)彙整 R0-R6 結果,依 state.md project_maturity(MVP/GA/mature)
  auto-pick threshold column,輸出 4-state verdict:✅ PASS / ⚠ SOFT FAIL / 🔴 HARD FAIL
  / ⏸ PENDING。SOFT FAIL 可經 PO override 過 Phase 5;HARD FAIL blocked;PENDING
  awaiting scope declaration。always-zero gates(R0 conflict / memory rule / missing
  required code / lint baseline 增)不分 maturity。
priority: P0
rationale: |
  反對 PO 原 hard 100%(§ 6.1)—— maturity-aware 避免 MVP 過嚴;4-state verdict 對齊
  Phase 4.5 → Phase 5 gate transition(§ 9.2);always-zero gates 保護 inviolable 底線。
acceptance:
  - threshold 從 state.md project_maturity field 讀取 auto-pick column;無 field → 預設 MVP + warning(§ 6.2)
  - verdict ∈ {PASS, SOFT FAIL, HARD FAIL, PENDING};phase transition 依 § 9.2 table
  - § 6.3 4 always-zero gate(R0 conflict / memory rule / missing required code / lint baseline)不分 maturity 恆 0 容忍
  - SG Gate Decision matrix(9 dimension required vs actual)輸出於 report(§ 9.2)
golden_scenario: |
  Given project_maturity=MVP,R2 scoped coverage 96.6%(≥70%)、memory rule violation 0、其餘 dimension 皆達 MVP threshold
  When SG 彙整 R0-R6 並 auto-pick MVP threshold column
  Then SG verdict = ✅ PASS,allow Phase 4.5 → Phase 5 release note
anti_examples:
  - ❌ 不讀 project_maturity 而一律套 mature=100% threshold(§ 6.1 反對 hard 100%)
  - ❌ memory rule violation=1 但因 maturity=MVP 判 PASS(§ 6.3 always-zero 被違反)
  - ❌ 缺 scr_scope declaration 卻直接判 PASS/FAIL 而非 ⏸ PENDING(§ 8.4 fallback 4 / § 9.2 verdict)
dependencies:
  blocked_by: [REQ-001, REQ-002, REQ-003, REQ-004, REQ-005, REQ-006, REQ-007]
  blocks: []
proposed_module: sg-gate
source_evidence: "§ 6 SG Gate Threshold Matrix;§ 6.1-6.3 maturity-aware + always-zero;§ 9.2 SG Gate Decision 4-state verdict"
```

### REQ-009: Propose-First No-Auto-Apply Discipline

```yaml
id: REQ-009
title: Propose-First No-Auto-Apply Discipline
description: |
  SCR 是 read-only review tool —— 只 report violations,絕不 auto-apply fix。找到
  *.py / SQL violation → propose-first,等 PO 授權後才改(對齊 [[backend-change-rule]]);
  fix violation 後必跑 [[audit-patch-cascade-verify]] 5-dim verify。任何 stage 違反
  no-auto-apply → 該行為 invalid。
priority: P0
rationale: |
  對齊 [[backend-change-rule]](§ 2 rule 1)+ § 13 inviolable criteria「任何 stage 不可
  auto-apply fix / 任何 *.py source change 必 propose-first」;SCR 0 source change(§ 11.4)。
acceptance:
  - SCR 對 code 0 source change —— 只輸出 report,不 auto-apply(§ 11.4 + § 13)
  - 找到 *.py / SQL violation → propose-first,等 PO 授權(§ 2 rule 1)
  - fix 後跑 5-dim cascade verify(cross-file / intra-file / commit-time / Round N+1 / external state,§ 2 rule 3)
golden_scenario: |
  Given SCR 在 src/api/payment.py 找到一個 unspec'd entry-point violation
  When SCR 產出 report
  Then report 列出 violation + 建議 fix,但不修改 payment.py;修 code 需另走 PO propose-first 授權
anti_examples:
  - ❌ SCR 直接 edit payment.py 補上 REQ docstring tag(違反 no-auto-apply)
  - ❌ SCR fix 一個 *.py violation 未經 PO 授權(違反 [[backend-change-rule]] propose-first)
  - ❌ fix 後不跑 5-dim cascade verify 就 commit(§ 2 rule 3 違反)
dependencies:
  blocked_by: []
  blocks: []
proposed_module: scr-governance
source_evidence: "§ 2 rules 1/3;§ 11.4 對既有 source(0 source change);§ 13 inviolable criteria"
```

### REQ-010: SG-Bypass Token + Audit Log + Retroactive Backfill

```yaml
id: REQ-010
title: SG-Bypass Token + Audit Log + Retroactive Backfill
description: |
  SCR 提供 emergency escape valve —— `/scr --bypass=urgent-fix` 對齊
  [[sanity-check-bug-fix-direct-main-rule]]。bypass 依 severity 走授權 chain(同
  session bug fix = PO inline;cross-session = async sign-off;architectural change /
  memory rule fix = NO bypass)。bypass commit 必 auto-append decision-log + release
  note audit,且必在 due date 前 retroactive 補回 SCR pass,逾期 → 阻擋 Phase 5。
priority: P1
rationale: |
  emergency direct-to-main 需 escape valve 但不可 silent(§ 7);retroactive backfill
  enforcement 防技術債 silent grow(§ 7.4);architectural / memory rule fix 不可 bypass
  對齊 always-zero 底線。
acceptance:
  - bypass token forms + 授權 chain per severity(§ 7.1-7.2);architectural / memory rule fix = NO bypass
  - bypass commit auto-append decision-log(D-scr-bypass-*)+ release note sg_bypass field(§ 7.3)
  - 每輪 SCR run 開頭 scan 雙路徑 decision-log(per-project + org)找未 close bypass entry(§ 7.4 dual path)
  - 逾 due_by 未 backfill → P-bypass-overdue + state.md outstanding_blockers +1 + 阻擋 Phase 5(§ 7.4)
golden_scenario: |
  Given PROD iOS crash,PO 以 /scr --bypass=urgent-fix --reason "..." --po-confirm 同 session 修
  When SCR 處理 bypass
  Then auto-append D-scr-bypass-<id>(retroactive_required=yes)+ release note sg_bypass=yes,下輪 SCR run 掃到並要求 due_by 前補回 pass
anti_examples:
  - ❌ architectural change 用 --bypass 規避 full SG path(§ 7.2 NO bypass)
  - ❌ bypass commit 不寫 decision-log / release note audit(§ 7.3 必 append)
  - ❌ bypass 逾 due_by 未 backfill 卻仍放行 Phase 5(§ 7.4 overdue 必阻擋)
dependencies:
  blocked_by: [REQ-008]
  blocks: []
proposed_module: sg-bypass
source_evidence: "§ 7 SG-Bypass Token + Audit Log;§ 7.1-7.4 授權 chain + retroactive enforcement;§ 2 rule 12"
```

### REQ-011: Spec Scope Declaration Mechanism + PENDING Fallback

```yaml
id: REQ-011
title: Spec Scope Declaration Mechanism + PENDING Fallback
description: |
  PR/commit 以 scr_scope metadata 宣告本次 impl 覆蓋的 REQ-XXX;SCR 對 declared scope
  計算 coverage %(scoped 進 SG gate,undeclared 視為 future round 不 flag)。讀取順序:
  PR YAML → commit footer → auto-detect fallback(3a adapter extract → 3b regex →
  union)→ 全無宣告時 SG verdict = ⏸ PENDING(3rd state,neither PASS nor FAIL),
  Phase 5 blocked until declare-or-decline。scope declaration 不可 exempt § 2 memory rules。
priority: P0
rationale: |
  Stage 5 PoC BLOCKER(§ 8.4):scoped impl 無 scope mechanism → R2 算 full-spec 56.3%
  < 70% MVP → false-flag SG fail;PENDING 為 mitigation-of-mitigation 防 silent default;
  scope 為 trust commitment 不可 silent miss。
acceptance:
  - scr_scope 讀取順序 PR YAML(1)→ commit footer(2)→ auto-detect fallback(3a→3b→3c union,§ 8.4)
  - 全無宣告 → SG verdict ⏸ PENDING + P-scr-scope-pending entry 雙路徑 + Phase 5 blocked(§ 8.4 fallback 4)
  - explicit decline → force_full + maturity-aware threshold apply(explicit choice not silent)
  - LOC > 300 OR architectural_change=true 必 declare scope(§ 8.4 undeclared policy);memory rule 0 容忍不受 scope 豁免
golden_scenario: |
  Given commit 改 <50 LOC 但完全無 scr_scope 宣告且 auto-detect union 為空
  When SCR 計算 R2 coverage 並打 SG verdict
  Then SG verdict = ⏸ PENDING,emit「no scope declaration」warning,P-scr-scope-pending entry 記入雙路徑 decision-log,Phase 5 blocked 直至 declare-or-decline
anti_examples:
  - ❌ 大型 architectural change 不 declare scope「規避 SG fail」(§ 8.4 illegal / undeclared policy)
  - ❌ 全無宣告時 silent default 成 full-spec 並直接判 PASS/FAIL 而非 ⏸ PENDING(§ 8.4 OPT-A)
  - ❌ declared scope 內宣稱只改 3 REQ 但實際夾帶 scope-out feature(§ 8.4 trust commitment 違反)
dependencies:
  blocked_by: [REQ-003]
  blocks: [REQ-008]
proposed_module: scr-scope-declaration
source_evidence: "§ 8.4 Spec scope declaration mechanism(PoC BLOCKER);§ 8.4 fallback 4-step + PENDING verdict;§ 9.2 verdict table"
```

### REQ-012: 3-Role Human-First Compliance Report

```yaml
id: REQ-012
title: 3-Role Human-First Compliance Report
description: |
  SCR output 必對齊 [[human-first-docs]] 3-role(👔 PM / 🔬 QA / 💻 Developer)perspective —
  TL;DR ship verdict 最先,PM Lens(規格↔實作對照 / 趨勢 / time-to-ship / open-vs-closed
  / effort-value)plain prose,QA Lens(測試對齊 + gap + 推薦重點),Developer Lens
  (file:line + 命令),technical R0-R6 / SG matrix / Mental Lens 退到 Appendix。coverage
  < 100% 時必 per-REQ explicit enumerate complete/partial/missing。verbosity(簡要/
  medium/全部)modulate detail level。
priority: P1
rationale: |
  Real-try evidence(§ 9.5):first PROD V7 output jargon-heavy → PM 看不到「能不能
  ship」核心;PO directive「PM 不是技術人員」;§ 5.6 PO directive 覆蓋率非 100% 要明列缺項。
acceptance:
  - output 依 § 9.5 結構:TL;DR → PM Lens → QA Lens → Dev Lens → Appendix(mode-aware skip)
  - coverage < 100% 必列 complete / partial(含 missing sub-AC)/ missing / out-of-scope 4 群(§ 5.6 / § 9.6.1)
  - plain language standard:jargon 轉 PM 語言(§ 9.5 anti-pattern 表);technical detail 退 Appendix
  - verbosity 簡要(default)/ medium / 全部 modulate per-section detail(§ 8.6 matrix);metrics.json sidecar 不受 verbosity 影響
golden_scenario: |
  Given SCR 跑完 sanity-check,coverage 78%,REQ-024 partial 缺 sub-AC B/C
  When 以 default 簡要 verbosity 產出 report
  Then TL;DR 先給 ship verdict,PM Lens 規格↔實作對照表明列 REQ-024 partial + missing sub-AC B/C,technical R0-R6 detail 收在 Appendix(--full 才展開)
anti_examples:
  - ❌ report 以 heavy YAML frontmatter + § 1 Mental Lens / R0-R6 jargon 開頭,PM 找不到 ship verdict(§ 9.5 real-try 反例)
  - ❌ coverage 78% 只給 aggregate 數字,不列哪些 REQ partial / missing(§ 5.6 違反)
  - ❌ 簡要 mode 仍 dump 全 R0-R6 appendix(§ 8.6 verbosity matrix 違反)
dependencies:
  blocked_by: [REQ-003, REQ-008]
  blocks: []
proposed_module: scr-reporting
source_evidence: "§ 9.5 3-Role Output Format;§ 5.6 Coverage Gap Enumeration;§ 9.6-9.8 PM/QA/Dev Lens;§ 8.6 Verbosity"
```

### REQ-013: Natural-Language Invocation with Popup Disambiguation & Escape

```yaml
id: REQ-013
title: Natural-Language Invocation with Popup Disambiguation & Escape
description: |
  SCR 支援全自然語言 invocation(4-slot intent:action / target / verbosity /
  focus_lens),PM/QA 不需記 flag。低 confidence slot → popup 詢問(用 PM 看得懂的話 +
  附成本 + 預設選 + ⓧ escape);out-of-scope intent(code gen / bug fix / deploy /
  chitchat)→ explicit reject + redirect;實跑前 echo + cost preview;3-level escape
  route;每次 resolution 寫 metrics.json audit(4-state status)。REQ-ID / --feature
  targeting 自動 fill scr_scope。
priority: P1
rationale: |
  PO insight「no one be able to remember the detail commands / PM/QA may not really
  know the feature」(§ 8.7);NL + popup 降 cognitive load 對齊 [[user-working-style]];
  negative reject 防 silent 誤觸發 hallucinated review garbage(§ 8.9)。
acceptance:
  - 4-slot NL parse + confidence-tier popup contract(全≥0.9 skip / 1 slot 0.7-0.9 single / <0.7 multi popup,§ 8.7)
  - popup 5 mandatory 條件(PM 語言 / 附成本 / 預設選 / ⓧ escape / echo,§ 8.7.1);ⓧ escape silent 0 file 0 audit(§ 8.11 L1)
  - out-of-scope intent explicit reject + redirect(§ 8.9);跑前 cost + time preview(§ 8.10)+ heavy-tier 2-stage confirm
  - --req / --feature targeting 自動 fill scr_scope 成 explicit declaration(§ 8.5,不 fallback);resolution 寫 metrics.json 4-state audit(§ 8.12);對齊 § 8.13 8-step lifecycle
golden_scenario: |
  Given PM 打「v7 review sanity check 看還剩什麼」,target 與 focus_lens slot confidence < 0.9
  When SCR parse 4-slot 並觸 popup
  Then 以 PM 看得懂的話 popup(附「~3 分鐘」成本 + ⭐ 預設 + ⓧ 我打錯了),user 選定後 echo + cost preview 才開跑,resolution 寫 metrics.json status=completed
anti_examples:
  - ❌ 「v7 幫我寫一個 react component」被當 review input 硬跑產 hallucinated garbage(§ 8.9 negative reject 違反)
  - ❌ popup 選項用「REQ-scoped fallback 3a」這種術語(§ 8.7.1 用 PM 看得懂的話違反)
  - ❌ 選 ⓧ「我打錯了」後仍留 partial metrics.json / audit entry(§ 8.11 L1 silent escape 違反)
dependencies:
  blocked_by: [REQ-011]
  blocks: []
proposed_module: scr-nl-invocation
source_evidence: "§ 8.5 REQ-ID + NL Targeting;§ 8.6 Verbosity;§ 8.7-8.13 NL invocation / popup / reject / cost preview / escape / audit / lifecycle"
```

---

## § 3. Current State Analysis

### § 3.1 為何 spectra-review + ruff + mypy + pytest 加總仍不夠

| Tool | 抓得到 | 漏掉的 SCR niche |
|:---|:---|:---|
| spectra-review enhanced-v1 | Spec 內部 drift(naming / completeness)| Spec ↔ code semantic 對齊 |
| ruff(F821 / F)| Undefined var / unused import | REQ-XXX 是否 impl |
| mypy | Type mismatch | Functional flow 對齊 design |
| pytest | Runtime behavior | Architecture layer violation |
| smoke test(dogfood)| UI render / runtime crash | Bi-dir traceability gap |

**Niche niche niche:** Code ↔ 3-layer spec bi-dir compliance — 既有 5 工具皆 miss。

### § 3.2 The 4 critical gap(已 Turn 2 enumerate,本 spec 處置)

| Gap | rev 0.1 處置 |
|:---|:---|
| Detection algorithm reliability | Tier 2 — rev 0.2 spec L1-L5 hybrid tier per reviewer |
| Spec format prerequisite | § 4.x 各 reviewer 明示 spec ID 規約(REQ-XXX / FUNC-XXX / DESIGN-XXX);1-layer spec 可降級為 lite SCR(Tier 2 詳) |
| Architecture spec explicit-ness | § 4.6 R5 明示「無 layer 宣告 = skip Architecture dimension,不 default 假設」 |
| Unspec'd impl FP risk | Tier 2 — rev 0.2 spec bi-dir anchor scope(entry-point / service / helper free pass)|

---

## § 4. Proposed Changes — 7-Reviewer Architecture(Tier 1.1)

### § 4.1 R0 Spec Cross-Layer Consistency Reviewer(NEW — 對齊 PO 5+1 → 6+1)

> Requirement anchor: REQ-001

**Purpose:** SCR 自身先 verify spec 自身正確,才有 review code 的基準。

**Detection focus(rev 0.2 N7 closure — per-mode 拆分,避免 aspirational 文字與 operational 表格不對齊):**

| Mode | Layer-mapping check | Semantic conflict check | Spec freshness check | Heading levels check(V-005 closure)|
|:---|:---|:---|:---|:---|
| **R0-full**(3-layer)| req↔func↔design 全 3 層 ID mapping(REQ-XXX↔FUNC-YYY↔DESIGN-ZZZ)| 3 層 cross-check(eg. req「export PDF」 vs design「only CSV」)| rev 落後對齊 issue date(3 layer 同步)| ✅ check H1/H2/H3 only |
| **R0-medium**(2-layer 含 req)| req↔func OR req↔design 2 層 mapping | 2 層 cross-check | rev 落後對齊 issue date(2 layer 同步)| ✅ check H1/H2/H3 only |
| **R0-lite**(1-layer only req)| ID 唯一性(REQ-XXX 不重複)| spec 內 AC sub-step 內部 self-consistency(無 sub-step 矛盾)| rev metadata freshness only | ✅ check H1/H2/H3 only |

**Common to all modes:**
- ID 唯一性(各 layer 自身內 ID 不重複)
- Heading levels:H1(title only)+ H2(`## § N. ...`)+ H3(`### § N.M ...`)— no H4+,no skip-level(`#` → `###` 直跳禁)
- Acceptance criteria sub-step syntax compliance(eg. bullet point + sub-step numbering)

**Fail behavior:** R0 fail → SCR 全 abort,return「fix spec layers first」 + 標 spec drift bug。後續 R1-R6 不跑。

**R0 mode auto-detection(rev 0.1.1 Round 1-patch B1 — 取代原 skippable condition,解 § 6.3 always-zero invariant 衝突):**

| project_layers | R0 mode | 檢測 scope | always-zero invariant 適用? |
|:---|:---|:---|:---:|
| **3-layer(req + func + design)** | **R0-full** | req↔func↔design 三層 cross-check + ID 唯一性 + 語意對齊 | ✅ R0-full verdict pass/fail binary;fail = SG always-zero |
| **2-layer(req + func OR req + design)** | **R0-medium** | 已存在兩層 cross-check + ID 唯一性 + 語意對齊 | ✅ R0-medium verdict pass/fail binary;fail = SG always-zero |
| **1-layer(only req)** | **R0-lite** | spec 內 acceptance criteria syntax + REQ-ID 唯一性 + 內部 self-consistency(eg. AC-X-1 vs AC-X-2 無矛盾)| ✅ R0-lite verdict pass/fail binary;fail = SG always-zero |

**Invariant:** 所有 R0 mode verdict 皆 binary(pass/fail),fail → SG always-zero(對齊 § 6.3)。Mode 區別僅 scope,不變更 verdict 機制。

**Mode 自動 detect:** SCR 開跑時 check `docs/pm/<project>/spec/` directory 內 spec file 數 / type(`*-requirement-*.md` / `*-functional-*.md` / `*-design-*.md`),據此 pick R0 mode。

### § 4.2 R1 Traceability Reviewer

> Requirement anchor: REQ-002

**Purpose:** 建立 spec ↔ code 雙向 map,後續 R2-R5 依此計算 coverage %。

**Detection focus:**
- 對 spec 每 REQ-XXX / FUNC-XXX / DESIGN-XXX,grep 全 codebase 找 reference(docstring tag / comment / function name)
- 對每 code entry-point(Flask route / LIFF handler / CLI subcommand)反查 REQ link
- 輸出 traceability map JSON(spec → code list + code → spec list)

**Output schema:**
```yaml
traceability:
  spec_to_code:
    REQ-005: [src/api/export.py:42, templates/export-pdf.html:18]
    REQ-099: []   # missing impl
  code_to_spec:
    src/api/export.py:42: [REQ-005, FUNC-012, DESIGN-007]
    src/api/payment.py:88: []   # unspec'd
```

**Detection methodology(Tier 1 baseline):**
- L1 string match + L4 LLM confirm hybrid(Tier 2 詳細 L1-L5 tier)

### § 4.3 R2 Requirement Coverage Reviewer

> Requirement anchor: REQ-003

**Purpose:** 量化 req spec → code 對齊度。

**Detection focus:**
- 計算 `已 impl acceptance criteria 數 / 總 acceptance criteria 數`(coverage methodology § 5 詳)
- 對每未 impl REQ,列 missing file path 建議(based on naming convention)
- 對 partial impl REQ(0.5 計分),列具體缺哪個 sub-criterion

**Output schema:**
```yaml
requirement_coverage:
  total_acceptance_criteria: 87
  implemented: 82
  partial: 3   # 0.5 weight
  missing: 2
  coverage_percent: 96.6   # = (82 + 0.5*3) / 87
  missing_list:
    - { req: REQ-099, criteria: AC-99-2, suggested_path: src/api/export.py }
```

### § 4.4 R3 Functional Compliance Reviewer

> Requirement anchor: REQ-004

**Purpose:** Verify code 實現的 functional flow 對齊 func spec 流程。

**Detection focus:**
- 對每 FUNC-XXX flow(eg. Login → OTP → JWT → Dashboard)
- AST-parse code,追 call chain,verify 每 step 是否真實存在
- 抓 missing step / extra step / out-of-order step

**Output schema:**
```yaml
functional_compliance:
  total_flows: 23
  fully_compliant: 21
  missing_step: 1   # eg. FUNC-008 缺 OTP step
  extra_step: 0
  out_of_order: 1
  compliance_percent: 91.3
```

### § 4.5 R4 Design Compliance Reviewer

> Requirement anchor: REQ-005

**Purpose:** Verify code 結構對齊 design spec component / layer / interface 規範。

**Detection focus:**
- 對每 DESIGN-XXX component,verify code 真實存在對應 class/module
- Verify interface signature(method name / param / return type)對齊 design 規約
- 抓 signature drift / missing component / interface incompatibility

### § 4.6 R5 Architecture Compliance Reviewer

> Requirement anchor: REQ-006

**Purpose:** Verify code 對齊 design spec 之 architecture pattern(若 design 有宣告)。

**Detection focus:**
- 若 design spec 宣告「Controller → Service → Repository」 layer,grep code import graph 驗證
- 抓 layer skip(Controller → SQL 跳過 Service / Repository)
- 抓 dependency 反向(Service → Controller)
- **Memory rule cross-cutting checks:** § 2 enumerate 之 13 條 memory rules 在此 reviewer 落地

**Skip condition:** 若 design spec 無 explicit layer 宣告(eg. AzureLineBOT 後端 flat Flask)→ R5 layer dimension skip,但 memory rule check 仍跑。

### § 4.7 R6 Coding Standard Reviewer

> Requirement anchor: REQ-007

**Purpose:** PEP8 / naming / lint / dead code / security baseline。

**Detection focus:**
- Reuse existing `[[backend-lint-workflow]]` bash lint.sh(ruff F821/F + baseline)
- + UX pattern rule(`[[delete-dialog-no-undo-hint]]` 文案 check)
- + frontend lint(Tier 2 per-stack adapter)

**Cost:** 最低 — 直接 invoke existing tooling,無 LLM call。

### § 4.8 Execution Order & Dependency Graph

```
R0 Spec Cross-Layer Consistency
   │ (fail → abort)
   ▼
R1 Traceability(map 建立)
   │
   ├──► R2 Requirement Coverage
   │       │
   │       ▼
   │     R3 Functional Compliance
   │       │
   │       ▼
   │     R4 Design Compliance
   │       │
   │       ▼
   │     R5 Architecture Compliance
   │
   └──► R6 Coding Standard(可獨立並行)
```

**並行 vs 序列:**
- R0 must run first(序列)
- R1 fan-out 後,R2 → R3 → R4 → R5 是 sequential(每階段依賴上階段 map)
- R6 可與 R1-R5 並行(獨立)

**Dependency graph prose explanation(rev 0.2 N4 closure):**

R0 是 **mandatory pre-gate** — spec 自身正確才有 review code 的 ruler。R0 fail → SCR abort,return「fix spec layers first」,後續 R1-R6 不跑(避免 wasteful compute on broken spec)。

R1 Traceability 是 **fan-out host** — 建立 spec ↔ code 雙向 mapping JSON,R2-R5 直接 consume 此 map 計算各自指標。R1 自身不報 violation,只 produce data。

R2-R5 是 **sequential cascade** — 後階段依賴前階段的 finer-grained map:
- R2 對 R1 map 計算 acceptance criteria coverage %(spec → code 方向)
- R3 對 R2 結果 + R1 map 對 functional flow step 順序 verify
- R4 對 R3 結果 + R1 map 對 design spec component signature verify
- R5 對 R4 結果 + R1 map + memory rules 對 architecture pattern + 17 條 invariant verify

R6 是 **完全並行 island** — 不依賴 R1 map,直接 reuse 既有 lint/baseline 工具(`bash lint.sh` per `[[backend-lint-workflow]]`);可與 R1 同時開跑,結果合併到 final report 即可。

**Quote rationale:** 此 dependency 結構源於 avoid wasted compute — 若 R0 fail,R1-R5 結果 無 meaning(spec ruler 自身錯);若 R1 fail(no spec → code path map),R2-R5 全無 base data;R6 是 lint 與 spec 無關,故可獨立並行。

### § 4.9 Cost-staged invocation tier(rev 0.2 Tier 2.2 NEW)

**Purpose:** SCR 跑全 7 reviewer 之 LLM/compute cost 對小 commit 不 economic;cost-staged tier 對 invocation context 自動 pick light/medium/heavy。

**Tier matrix:**

| Tier | Trigger condition | Reviewer 跑哪些 | Estimated cost(relative)|
|:---|:---|:---|:---:|
| **Light** | 改動 < 50 LOC(code stack only — *.md / *.txt / docs/* exclude per rev 0.2.1 N1 closure)AND 無 architecture-change AND 無 memory-rule-touching | R0(必)+ R1(必,但 fast scan)+ R6(lint reuse — cheap)| 1x |
| **Medium** | 50-300 LOC code OR partial-feature impl OR scope declares ≥ 1 REQ-XXX | + R2(req coverage)+ R3(functional flow)| 3x |
| **Heavy** | > 300 LOC code OR architectural change OR ≥ 2 REQ-XXX impl OR memory rule touch | Full R0-R6 | 6x |
| **Force-full** | User explicit `/scr --full` override OR maturity=mature | Full R0-R6(regardless of trigger)| 6x |

**LOC counting rule(rev 0.2.1 N1 closure):**
- 計算 `git diff --stat` 但 **僅含 code stack 對應 file**:`*.py / *.js / *.ts / *.html / *.css / *.sql`(對齊 § 4.10 per-stack adapter registry)
- **Exclude:** `*.md / *.txt / *.json(unless schema)/ docs/*/` — docs change 為 governance scope,自動 light tier(對齊 [[human-first-docs]] doc-only commit pattern)
- **Edge case:** `*.json` schema file(eg. `sanity_db_create_tables.sql` 對應 `generated/*.json`)算 code stack;config-only JSON(eg. `.eslintrc.json`)不算

**Detection mechanism:**

```yaml
# PR/commit metadata that SCR reads
scr_invocation:
  loc_changed: <int>          # `git diff --stat` total lines
  scope:                      # 對齊 spec scope declaration § 8.4(NEW PoC blocker)
    - REQ-024-E
    - REQ-024-F
    - REQ-025-A-5th
  architectural_change: <bool>  # author 自宣 OR auto-detect via memory rule grep
  memory_rule_touched: <bool>  # auto-detect via grep [[memory-name]] in commit diff
  force_tier: <null | light | medium | heavy | full>  # override hint
```

**Tier auto-pick algorithm(rev 0.2 baseline,Tier 3 calibrate):**

```
IF force_tier set:
  use force_tier
ELIF maturity == 'mature':
  use heavy(maturity ≥ GA 強制 full coverage)
ELIF architectural_change OR memory_rule_touched OR len(scope) >= 2:
  use heavy
ELIF loc_changed <= 50 AND no architectural_change AND no memory_rule:
  use light
ELSE:
  use medium
```

**Cost amortization invariant:** SCR 每 commit invocation 之 effective cost ≤ MVP threshold 70%(以 cost-staged 控);全 spec coverage 升級需 force_tier=full + PO 明示。

### § 4.10 Per-stack adapter layer(rev 0.2 Tier 2.5 NEW)

**Purpose:** R1 Traceability + R4 Design Compliance 之 AST-level detection 對不同 source stack 需不同 parser;per-stack adapter 實現 plug-in 介面避免 monolithic SCR core。

**Adapter API contract(rev 0.2.1 N2 closure — typed Protocol + sub-type schema):**

```python
from typing import Protocol, TypedDict

class EntryPoint(TypedDict):
    name: str             # function/method/route name
    location: Location    # file:line
    kind: str             # 'flask_route' | 'liff_handler' | 'cli_subcommand' | 'public_method' | 'invariant_guard'

class Location(TypedDict):
    file_path: str
    line_no: int
    end_line_no: int      # for span match

class ReqTag(TypedDict):
    req_id: str           # eg. 'REQ-024-E'
    location: Location
    source: str           # 'docstring' | 'comment' | 'attribute' | 'frontmatter'

class Drift(TypedDict):
    kind: str             # 'missing_param' | 'extra_param' | 'type_mismatch' | 'return_type_drift'
    spec_sig: str         # canonical signature from spec
    code_sig: str         # actual signature from code
    location: Location

class StackAst(Protocol):
    """Stack-specific AST or structured tree (Python ast.Module / JS Program / HTML lxml Element / etc)。"""
    pass

class ScrStackAdapter(Protocol):
    name: str  # 'python' | 'javascript' | 'html' | 'sql' | 'yaml'
    
    def parse_source(self, file_path: str) -> StackAst:
        """Return stack-specific AST/structured tree representation (typed Protocol)。"""
    
    def extract_entry_points(self, tree: StackAst) -> list[EntryPoint]:
        """Return public API surface (R1 anchor scope per § 5.4)。"""
    
    def extract_req_tags(self, tree: StackAst) -> list[ReqTag]:
        """Return REQ-XXX 標記 list (對齊 § 5.4 REQ-tag form per stack)。"""
    
    def signature_compare(self, code_sig: dict, spec_sig: dict) -> list[Drift]:
        """R4 signature drift detection (typed Drift return)。"""
```

**Adapter registry per rev 0.2 baseline:**

| Stack | Parser | Library | Implementation status |
|:---|:---|:---|:---|
| Python | `ast` module(stdlib)| stdlib only | rev 0.2 baseline |
| JavaScript | `esprima` OR `@babel/parser` | pip / npm | rev 0.2 baseline(JSDoc REQ-tag)|
| HTML | `lxml` OR `BeautifulSoup` | pip(lxml stdlib-derived)| rev 0.2 baseline |
| SQL | `sqlparse` | pip | rev 0.2.1 baseline(C1 closure)— `sanity_db_create_tables.sql` 是 sanity-check SSOT per `[[backend-schema-change-workflow]]` rev 1.10;`laundry_db_create_tables.sql` 是 laundry SSOT;adapter scope codify but pip impl propose-first per `[[dep-management]]` |
| YAML / JSON | `pyyaml` / stdlib `json` | stdlib + pip | rev 0.2 baseline |

**Dep alignment:** 每 adapter 之 pip dep 需 propose-first per `[[dep-management]]`(stdlib-only 為優先,Azure Linux 3.0 兼容);若 SCR 跑於 dev workstation 而非 Azure runtime,可放寬。

**Fallback chain:** Adapter unavailable for stack(eg. SQL adapter not installed)→ R1 + R4 該 stack 之 detection 降級為 regex string match(L1 of detection tier per § 5.5),emit warning「stack <X> adapter unavailable,降級 L1 detection」 不 fail。

---

## § 5. Coverage % Methodology(Tier 1.3)

> Requirement anchor: REQ-003(§ 5.1-5.3 coverage formula / partial scoring);REQ-002(§ 5.4 anchor scope matrix)

### § 5.1 Acceptance-criteria base unit

**Rule:** Coverage % 計算 base unit 是 acceptance criteria,**非 REQ 數本身**。

**Rationale:** REQ 大小不一(REQ-005 可能 1 個 AC,REQ-099 可能 8 個 AC),用 REQ 數會 distort。

**Formula:**
```
req_coverage_% = (fully_impl_AC + 0.5 × partial_impl_AC) / total_AC × 100
```

### § 5.2 3-tier partial impl scoring(0 / 0.5 / 1)

| Score | 條件 | Example(REQ-005 Export PDF)|
|:---|:---|:---|
| **0** | AC 完全無 code reference | PDF generation function 不存在 |
| **0.5** | AC 部分 impl(主功能 OR 從屬 sub-step 缺)| PDF gen 完成但 download button 缺;OR download button 完成但 PDF gen mock |
| **1** | AC 完整 impl + 對應 test pass | PDF gen + download + integration test 皆存在 |

**Detection methodology(Tier 1 baseline — rev 0.1.1 Round 1-patch C2 修正,移除 LLM Q&A 依賴):**
- **0 判斷:** R1 traceability map 對 AC `spec_to_code` list 為空 → 0
- **1 判斷:** R1 map 對 AC `spec_to_code` list 非空 + AC 內全 declarative sub-step 字面 grep 全命中 → 1
- **0.5 判斷:** R1 map 對 AC `spec_to_code` list 非空 但 AC 內 declarative sub-step 數 < 總 sub-step 數 binary heuristic → 0.5(無 LLM call)

**LLM Q&A 精細化 0.5 判斷:** defer rev 0.2(對齊 § 14.1 OQ-T2-1 detection algorithm L1-L5 tier)。rev 0.1 不依賴 LLM 確保 Tier 1 scope 不違反。

### § 5.3 Optional priority weighting(rev 0.2 enable)

未來可加 weighting:`coverage_% = Σ(AC_weight × AC_score) / Σ(AC_weight)`,P0 weight=3 / P1=2 / P2=1。本 rev 0.1 預設 equal weight。

### § 5.4 Bi-directional traceability anchor scope(rev 0.2 Tier 2.3 NEW)

**Purpose:** R1 Traceability + R2 Coverage 需明示「哪些 code 必 REQ-tag」 vs 「哪些 free pass」 — 避免 V-004 类 unspec'd impl false-flag(PoC § 13 finding)。

**Anchor scope matrix:**

| Code type | REQ-tag mandatory? | Rationale | Example |
|:---|:---:|:---|:---|
| Public API entry-point(Flask route / LIFF event handler / CLI subcommand main)| ✅ MUST | user-facing surface,功能直接對應 REQ | `@app.route('/cmd/insert_sanity_tc_definition')` / `def main(argv: list[str])` |
| Service-layer class / public method | ✅ MUST | business logic,功能對應 REQ | `class FriendBizcardService:` / `def update_friend_bizcard()` |
| Domain invariant guard function | ✅ MUST | invariant 對應 memory rule | `def _validate_profile_has_main_bizcard()` ← `[[profile-bizcard-invariant]]` |
| Internal helper(prefix `_`)| ❌ free pass | implementation detail | `_format_date()` / `_count_variants_by_intent()` |
| Cross-cutting infra(logging / error handling / retry decorator)| 🟡 optional | infra layer non-feature | `log.exception()` / `@retry(3)` |
| Test fixture / mock | ❌ free pass | test infra,not feature | `fixture_friend_with_bizcard()` |
| Deprecated kept for backwards-compat | ❌ free pass | shim by design | `# DEPRECATED rev 1.26 keep for shim` |
| Generated code(scaffolding / migrate output)| ❌ free pass | machine-generated | `migrations/0042_*.py` |

**REQ-tag form per stack(對齊 § 4.10 per-stack adapter):**

| Stack | REQ-tag syntax | Example |
|:---|:---|:---|
| Python | docstring `:requirement: REQ-XXX` OR `# REQ-XXX:` line comment | `def update_friend_bizcard():\n    """:requirement: REQ-015"""` |
| JavaScript | JSDoc `@requirement REQ-XXX` | `/** @requirement REQ-008 */ function loadProfile() {}` |
| HTML | `<!-- requirement: REQ-XXX -->` | `<!-- requirement: REQ-012 --><div id="autofill-btn">` |
| SQL | `-- requirement: REQ-XXX` | `-- requirement: REQ-013\nCREATE TABLE Sanity_Test_Result_TBL ...` |
| YAML/JSON | `requirement: REQ-XXX` field | (config schema)|

**Multi-REQ tagging:** 一個 function 可 tag 多 REQ — `:requirement: REQ-015, REQ-024-E`(comma-separated)。

**Multi-anchor classification(rev 0.2.1 N3 closure):** function 同時符合多 anchor type(eg. Flask route 含 business logic 既是「Public API entry-point」 又是「Service-layer」):
- **疊加 not 二選一** — function 同時繼承所有 matching anchor type 之 REQ-tag mandatory rule
- 若任一 anchor 要 ✅ MUST,則 function 適用 ✅ MUST
- 若全 anchor 為 ❌ free pass(eg. 純 internal helper),則 free pass
- Example:Flask route `@app.route('/cmd/insert_sanity_tc_definition')` + 內含 service logic + 觸 domain invariant guard → 3 anchor 疊加,REQ-tag 仍 1 個夠(覆蓋全 3 anchor scope)

**YAML/JSON REQ-tag form(rev 0.2.1 N4 closure):**

| Location in YAML/JSON | Syntax | Example |
|:---|:---|:---|
| **Top-level**(file-level,whole config 對應 1 REQ)| `requirement: REQ-XXX` at root | `requirement: REQ-018\nsanity_db:\n  ...` |
| **Nested**(per-key,config sub-section 對應 1 REQ)| `_requirement: REQ-XXX` sibling key(`_` prefix avoid schema collision)| `sanity_db:\n  _requirement: REQ-018\n  tables:\n    ...` |
| **Multi-REQ**(same syntax + comma-separated)| `requirement: REQ-015, REQ-024-E` OR `_requirement: REQ-015, REQ-024-E` | 同 docstring convention |

**Scope-out violations:** R1 + R2 對 free-pass scope 自動 skip,不計入「unspec'd entry-point」 SG gate dimension(避免 helper function flood)。

### § 5.5 Detection algorithm L1-L5 tier per reviewer(rev 0.2 Tier 2.1 NEW)

**Purpose:** Tier 1 baseline 為 L1 string + binary heuristic;rev 0.2 codify 完整 L1-L5 hybrid + per-reviewer tier optimal pick(trade-off detection precision vs LLM cost)。

**5-tier detection matrix:**

| Tier | Method | False Positive | False Negative | Cost(rel) | LLM call? |
|:---:|:---|:---:|:---:|:---:|:---:|
| **L1** | String exact match(`grep -r 'REQ-XXX'`)| 🟡 medium | 🟡 medium | 1x | no |
| **L2** | Regex + word boundary(`grep -wE`)| 🟢 low | 🟡 medium | 1.2x | no |
| **L3** | AST + naming convention(Python `ast` module / per-stack adapter § 4.10)| 🟢 low | 🟢 low | 3x | no |
| **L4** | LLM Q&A(「此檔有實作 REQ-XXX 嗎?」 + spec context)| 🟢 low | 🟢 low | 20x | **yes** |
| **L5** | Hybrid:L2 pre-filter → L4 confirm only for ambiguous cases | 🟢 low | 🟢 low | 4x | yes(部分)|

**Per-reviewer tier assignment(rev 0.2 baseline):**

| Reviewer | Default tier | Light tier | Heavy tier | Rationale |
|:---|:---:|:---:|:---:|:---|
| R0 Spec Cross-Layer | L2 | L1 | L3 | spec consistency 大多 syntactic;L2 regex 足夠;L3 only for semantic conflict deep verify |
| R1 Traceability | L3 | L2 | L4 | code mapping 必 AST(L3)避免 naming false neg;L4 for semantic 不明確 cases |
| R2 Req Coverage | L3 | L2 | L5 | AC coverage 計算 base unit;L3 binary 足夠;L5 hybrid for partial 0.5 細化 |
| R3 Functional | L4 | L3 | L4 | flow step 需 understand semantic;LLM 是 baseline |
| R4 Design | L3 | L2 | L4 | signature drift L3 deterministic;component-level semantic conflict L4 |
| R5 Architecture | L3 | L2 | L4 | import graph + naming pattern L3 已足夠;memory rule semantic L4 only for ambiguous |
| R6 Coding Standard | L1(reuse lint)| L1 | L1 | reuse existing ruff/mypy,no SCR-specific detection logic |

**Tier escalation rule:** R1-R5 自動 escalate light → default → heavy when:
- Confidence per detection < 0.6(L4 confirm needed)
- Multiple competing matches(eg. 2 functions 都 tag REQ-XXX,需 LLM 判斷哪個是 primary impl)
- User explicit `/scr --tier=heavy` override

**L4 LLM confidence elicitation method(rev 0.2.1 N6 closure):**

LLM 不天然 return confidence score,SCR 需 explicit prompt structure 取得 self-rated confidence。Baseline approach:

```python
# L4 LLM Q&A prompt template
prompt = """
Spec REQ-XXX: <full REQ text>
Code candidate: <function name + docstring + first 20 lines>

Answer with strict JSON:
{
  "implements_req": <true|false>,
  "confidence": <0.0-1.0>,    # 0.0 = totally unsure, 1.0 = certain
  "evidence": "<one-sentence why>",
  "alternative_candidates": [<other functions that might also implement REQ-XXX>]
}
"""
```

- **Aggregation:** SCR 多次 sample(N=3 baseline)取 median confidence(避免 LLM 單次 outlier)
- **Threshold escalate:** median confidence < 0.6 → 觸 「ambiguous match needs human review」 + log + skip auto-determination
- **Cost contribution:** 每 ambiguous case = 3 LLM calls;對齊 § 5.5 cost budget cap ≤ 100 calls(每 review run 約允許 30 ambiguous cases)
- **Future Tier 3 enhancement:** 加 cross-attention probe / multi-prompt corroboration(OQ-T3-1 confidence score 對齊;rev 0.2.1 baseline 採 self-rated)

**Cost budget cap:** SCR 單次 invocation L4 LLM call 上限 ≤ 100(rev 0.2 baseline 預估;PoC calibrate);超過 → fail-fast + emit「budget exceeded」 + propose scope narrow 給 user。

**Tier downgrade fallback:** L4 LLM unavailable(quota / network)→ 降級 L3;L3 stack adapter unavailable → 降級 L1。整 chain 配合 § 4.10 fallback chain。

### § 5.6 Coverage Gap Explicit Enumeration(rev 0.2.4 NEW — per PO 2026-06-30 real-try insight)

> Requirement anchor: REQ-003(coverage gap 判定)+ REQ-012(PM-facing enumeration output)

**PO directive:** 「若覆蓋率不100% 時要明確的指出來 那一項 requirement 沒有作 或是那一個只有部份完成」

**Purpose:** Coverage % 是 aggregate metric;PM/QA decision-making 需 per-REQ explicit status enumeration —— 明示哪些 REQ 完成 / 部分 / 未做。

**Coverage Gap Detail schema(每 SCR run mandatory output per § 9.7.1):**

```yaml
coverage_gaps:
  # 全 in-scope REQ 列出,per-REQ 三種狀態之一
  
  - req_id: REQ-019
    title: "TC JSON 24-field SSOT"
    status: complete       # complete | partial | missing
    score: 0.95            # 0.0 - 1.0 per § 5.2 partial scoring
    impl_files:
      - scripts/sanity_tc_pre_flight_check.py
      - scripts/sanity_tc_validate.py
      - scripts/sanity_tc_md_parser.py
      - scripts/sanity_tc_claude_extractor.py
      - scripts/sanity_tc_seed_from_js.py
    ship_impact: low       # low | medium | high
    pm_note: "深度涵蓋,容錯性佳"
    
  - req_id: REQ-024
    title: "MD Authoring Discipline"
    status: partial
    score: 0.7
    completed_sub_ac:      # 明示哪些 sub-AC 已做
      - "A. Structural invariants"
      - "E. Standard fake_data per operation_type"
      - "F. fake_data_intent escape valve"
    missing_sub_ac:        # 明示哪些 sub-AC 未做
      - "B. Content invariants (Traditional Chinese / English / 0 [[memory-ref]] / subject ≤ 20 / no dev jargon)"
      - "C. Semantic invariants (5 variant keys / intent ↔ scenario / target_strategy / label regex)"
    impl_files:
      - scripts/sanity_tc_pre_flight_check.py
      - scripts/sanity_tc_validate.py
      - scripts/sanity_tc_regenerate.py
    ship_impact: medium
    pm_note: "B+C 缺漏 → ship 後 MD 內容品質無自動驗證;recommended next sprint 補完"
    
  - req_id: REQ-099  # 假設 missing example
    title: "Export PDF"
    status: missing
    score: 0.0
    completed_sub_ac: []
    missing_sub_ac:        # 全部 sub-AC
      - "Generate PDF"
      - "Download button"
      - "Output ≤ 5MB"
    impl_files: []
    ship_impact: high
    pm_note: "完全未實作,P0 critical feature"
```

**Per-REQ status 判定 rule:**

| Status | Score 範圍 | 判定 |
|:---|:---:|:---|
| **complete** | ≥ 0.9 | 所有 sub-AC 全做 + impl distributed ≥ 2 file |
| **partial** | 0.1-0.89 | 至少 1 sub-AC 已做但不全 OR 全 sub-AC 做但單檔 OR limited test |
| **missing** | 0.0 | 0 file 引用 + 0 sub-AC implemented |

**Ship impact 判定 rule:**

| Ship impact | 判定 |
|:---|:---|
| **low** | 部分 sub-AC 缺,但其他 sub-AC 涵蓋 main happy path;ship 後 corner case 有風險 |
| **medium** | Critical sub-AC 缺(eg. validation logic 缺);ship 後 user-visible 行為差 OR 內容品質風險 |
| **high** | 全 REQ missing OR P0 critical sub-AC 缺;ship blocked OR 嚴重 product gap |

**PM-friendly output 必含 3 個 sub-section:**
1. ✅ **完整實作 REQ list**(complete 之 REQ)
2. 🟡 **部分實作 REQ list** with sub-AC detail(partial — PM 關鍵決策資訊)
3. 🔴 **未做 REQ list** with reason(missing — 立即 ship blocker indicator)
4. ⚪ **Out-of-scope REQ list**(scope auto-detect 排除之 REQ — 明示 「不算缺漏」 避免 PM 誤解)

對齊 `[[human-first-docs]]` PM/QA/Developer 3-role 紀律 + § 9.6 PM Lens 之 「📋 規格 ↔ 實作對照表」 output section。

---

## § 6. SG Gate Threshold Matrix(Tier 1.4)

> Requirement anchor: REQ-008(SG 4-state maturity-aware verdict + always-zero gates);REQ-006(§ 6.3 memory-rule always-zero);REQ-007(§ 6.3 lint baseline always-zero)

### § 6.1 Maturity-aware threshold

**Rule:** 反對 PO 原 hard 100% — maturity-aware threshold 從 state.md `project_maturity` field 讀取自動切換。

| Gate dimension | MVP | GA | Mature | 不可妥協 |
|:---|:---:|:---:|:---:|:---:|
| R0 Spec Cross-Layer Conflict | — | — | — | **0(always block)** |
| R2 Requirement Coverage | ≥70% | ≥95% | ≥100% | — |
| R3 Functional Compliance | ≥80% | ≥95% | ≥100% | — |
| R4 Design Compliance | ≥70% | ≥85% | ≥95% | — |
| R5 Architecture Violation | ≤3 | ≤1 | 0 | — |
| R5 Memory-rule Violation(§ 2 13 條)| — | — | — | **0(always block)** |
| Unspec'd entry-point | ≤5 | ≤2 | 0 | — |
| Missing required code(MVP/GA/mature 同)| — | — | — | **0(always block)** |
| R6 Coding Standard | — | — | — | **lint baseline 不可增** |

### § 6.2 state.md `project_maturity` field 對接

`docs/pm/<project>/state.md` 必含:
```yaml
project_maturity: MVP   # or GA / mature
maturity_signed_off_by: PO
maturity_last_updated: 2026-06-29
```

SCR run 時 read 此 field,auto-pick threshold column。

**Default:** 若 state.md 無此 field → 預設 MVP threshold(寬鬆 baseline)+ emit warning。

#### § 6.2.1 Existing state.md backfill scope(rev 0.2 corrected — Stage 5 PoC filesystem scan finding + N9 closure)

> ⚠ **rev 0.2 校正:** rev 0.1.1 § 6.2.1 list 5 處不對齊 filesystem 實際狀態(Stage 5 PoC 2026-06-29 `find docs/pm -name state.md` 揭示)。本 rev 0.2 取代 rev 0.1.1 inference list 為 **filesystem-verified state**。

**Stage 0.5 sub-steps(N9 closure — 解 「若存在」 conditional ambiguity):**

1. **Stage 0.5a:** filesystem scan(`find docs/pm -name "state.md" -type f`)取得實際存在 state.md 全集
2. **Stage 0.5b:** 對實際存在者 backfill `project_maturity` field per PO sign-off
3. **Stage 0.5c:** 對 missing-but-should-exist project,propose 「create state.md or skip」 decision per PO

**Filesystem-verified state(2026-06-29 PoC scan):**

| Path | Exists? | Proposed `project_maturity`(❓ awaits PO 拍板)| Rationale |
|:---|:---:|:---|:---|
| `docs/pm/sanity-check/state.md` | ❌ NOT EXIST | (if create:MVP)| rev 1.32.1 still iterating;sanity-check 是 mainline default UI project 應該有 state.md;Stage 0.5c decision |
| `docs/pm/dev-workflow-orchestrator/state.md` | ❌ NOT EXIST | (if create:MVP)| rev 0.1.1 still iterating;orchestrator proposal 自身應該有 state.md;Stage 0.5c decision |
| `docs/pm/pm-skill/state.md` | ✅ exists | GA | Pilot v0 dogfood 落地 + PM Skill subcommand productionized |
| `docs/pm/backend-schema-auto-sync/state.md` | ✅ exists | MVP | rev 1.10 still iterating |
| `docs/pm/phase-3-cicd-wrap/state.md` | ✅ exists | MVP | (rev 0.1.1 inference 沿用)|
| `docs/pm/spectra-review/state.md`(rev 0.1.1 漏列)| ✅ exists | MVP | spec evolution 中;enhanced-v1 已 ship 但 lite mode 仍未 deprecate |
| `docs/pm/db-auto-syncup/state.md`(rev 0.1.1 漏列)| ✅ exists | MVP | (rev 0.1.1 inference 沿用 MVP)|
| `docs/pm/mainline/state.md`(rev 0.1.1 漏列)| ✅ exists | GA | 2026-06-27 LineBOT repo unified 後 stable per `[[repo-split-phase3-migration]]` |
| `docs/pm/_archive/test-小明-solo/state.md` | ✅ exists | (archived — skip)| 在 _archive/ scope-out per archive convention |

**Total backfill scope:** Stage 0.5b ≥ 6 existing state.md;Stage 0.5c ≥ 2 propose decision。

**Future drift defense(rev 0.2 invariant):** Stage 0.5a 結果 grep 之 result 必 commit 為 immutable evidence(eg. `docs/pm/v7-spec-compliance-review/stage-0-5/filesystem-state-2026-06-29.txt`);後續 SCR rev 升,Stage 0.5 必 re-scan + diff against immutable evidence 確認 sync。

### § 6.3 Always-zero gates(不分 maturity)

以下 4 gate 永遠 0 容忍:
1. **R0 Spec Cross-Layer Conflict** — spec 自身矛盾 invalid SCR
2. **R5 Memory-rule Violation** — 13 條 invariant 不可違反
3. **Missing required code** — 標 priority="required" 之 REQ 缺 impl
4. **R6 Lint baseline 增加** — 對齊 `[[backend-lint-workflow]]` 「不增 baseline」 rule

---

## § 7. SG-Bypass Token + Audit Log(Tier 1.5)

> Requirement anchor: REQ-010

### § 7.1 Bypass 觸發條件

對齊 `[[sanity-check-bug-fix-direct-main-rule]]` — emergency direct-to-main 必須 escape valve。

**Bypass token forms:**
```bash
# 一般 path
/scr --check                                # 跑完整 SG;fail 擋 phase 5

# Emergency bypass path(僅同 session bug fix)
/scr --bypass=urgent-fix \
     --reason "PROD iOS crash blocking ship" \
     --commit-prefix fix \
     --po-confirm
```

### § 7.2 Bypass 授權 chain

| Severity | 授權層 | 必填 field |
|:---|:---|:---|
| 同 session bug fix(trigger type A)| PO inline confirm(對話內)| reason / commit hash |
| Cross-session bug fix(trigger type B)| PO async sign-off(commit message)| reason / 上次 SG pass commit / rollback plan |
| Architectural change | **No bypass** — must full SG path | — |
| Memory rule violation fix | **No bypass** — must full SG path + R5 cascade verify | — |

### § 7.3 Audit Log 必 append

**Bypass commit 必 auto-append 兩 file:**

1. `docs/pm/<project>/decision-log.md`:
```markdown
- D-scr-bypass-<id>: SG-bypass invoked by PO at <ts> | reason="..." | commit=<hash>
  | retroactive_required=yes | due_by=<next session>
```

2. `docs/release/changes/<date>-<title>.md`:
```yaml
---
sg_bypass: yes
sg_bypass_reason: "PROD iOS crash blocking ship"
sg_bypass_retroactive_due: 2026-06-30
---
```

### § 7.4 Retroactive backfill 強制(rev 0.1.1 Round 1-patch N3 — enforcement mechanism 細化)

Bypass commit 必須在下次 session(或 PO 指定 due date)retroactive 補回 SCR pass。

**Enforcement mechanism(rev 0.1.1 NEW;rev 0.2 N10 closure — dual path 明示):**
1. 每輪 SCR run 開頭,scan **雙路徑** decision-log 找未 close 之 `D-scr-bypass-*` entry(field `retroactive_required=yes`):
   - `docs/pm/<active-project>/decision-log.md`(per-project,active project per `docs/pm/active-project.txt`)
   - `docs/pm/_org/org-decision-log.md`(org-level cross-project bypass)
   - 兩路徑皆 scan;聯集為 bypass entry set
2. 對每 bypass entry,verify 對應 `due_by` date 內是否存在 retroactive backfill commit(grep commit message `Closes D-scr-bypass-<id>` pattern)
3. **Found:** 標 `D-scr-bypass-<id> CLOSED at <commit-hash>` + decision-log append close entry
4. **Not found AND past due_by:** 標 `P-bypass-overdue-<id>` + state.md `outstanding_blockers` 累加 `+1 bypass-overdue` + 阻擋 Phase 5 release note(下輪 feature ship blocker)
5. **Not found AND within due_by:** 標 `P-bypass-pending-<id>` warning,不擋 ship

**Acceptance:** state.md `outstanding_blockers` ≥ 1 之 `bypass-overdue` → 後續 SCR run 一律 fail-fast 直至 close。

---

## § 8. Invocation, Targeting & Spec Pinning(Tier 1.2 + rev 0.2.4/0.2.5 NL UX)

> Requirement anchor: REQ-011(§ 8.4 scope declaration + PENDING);REQ-013(§ 8.5-8.13 NL invocation / popup / reject / cost preview / escape / audit);REQ-012(§ 8.6 verbosity)

> **N1 rev 0.3 rename(2026-06-30):** Section originally 「Spec Version Pin / Fingerprint」(rev 0.1 Tier 1.2)— grew through rev 0.2.4 → 0.2.5 to 13 sub-sections covering spec pinning + REQ-ID/NL targeting + verbosity + NL invocation parser + popup disambiguation + help/discovery + negative reject + cost preview + escape route + audit trail + **invocation lifecycle flow chart**(§ 8.13 N11 NEW)。 Renamed to reflect actual scope — full taxonomy:
>
> | Sub-section | Topic |
> |:---|:---|
> | § 8.1 - § 8.4 | Spec version pinning + scope declaration |
> | § 8.5 - § 8.6 | REQ-ID / NL targeting + verbosity |
> | § 8.7 - § 8.12 | NL invocation UX layer(parser / popup / help / reject / cost / escape / audit)|
> | § 8.13 | **NEW rev 0.3:** Invocation Lifecycle numbered flow chart consolidating § 8.7 + § 8.10 + § 8.11 sequence |

### § 8.1 spec_pins frontmatter field

SCR report 必含 frontmatter:
```yaml
spec_pins:
  requirement:
    path: docs/pm/sanity-check/spec/sanity-check-requirement-spec.md
    rev: 1.32.1
    hash: sha256:a1b2c3...   # 對齊 hash 計算規約見下
  functional:
    path: docs/pm/sanity-check/spec/sanity-check-functional-spec.md
    rev: 0.9
    hash: sha256:d4e5f6...
  design:
    path: docs/pm/sanity-check/spec/sanity-check-design-spec.md
    rev: 0.7
    hash: sha256:g7h8i9...
code_pin:
  branch: main
  head: c29f3c3
  diff_against: 36de794   # baseline commit
```

**Hash 計算規約(rev 0.1.1 Round 1-patch N2):**
```
hash = sha256(spec body excluding frontmatter YAML block)
```

- frontmatter YAML block 定義:檔案開頭至第 2 個 `---` 分隔行(含)止之 byte range
- 排除 frontmatter rationale:frontmatter 含 mutable metadata(eg. `created` / `review_iteration`),hash 若含 → 每次 frontmatter 微改即觸 hash drift 誤報
- 規約適用 spec / proposal / decision-log;不含 review log(review log 無 frontmatter spec 對象)

### § 8.2 spec 版本選取 rule

SCR run 必用 **PR target branch HEAD spec version** — 避免 stale spec 對 fresh code review。

對 main branch:**HEAD spec rev** vs **HEAD code commit**。

### § 8.3 Drift detection between runs

連續兩輪 SCR run 比對 spec_pins hash:
- 若 spec rev 升但 code commit 不變 → 標 「spec drift detected — re-review needed」
- 若 code commit 升但 spec rev 不變 → 標 「code drift — verify spec alignment」
- 兩者皆升 → 標 「concurrent drift — full re-review mandatory」

### § 8.4 Spec scope declaration mechanism(⭐ rev 0.2 NEW — PoC BLOCKER must-add)

> Requirement anchor: REQ-011

> 🔥 **Critical PoC insight(Stage 5 dogfood 2026-06-29):** rev 1.31 L1+L2 commit fd6b30e 是 **scoped impl**(對齊 REQ-024 E + F + REQ-025 A 5th check),**不**是 comprehensive REQ-019/024/025 全覆蓋。SCR rev 0.1.1 無 scope mechanism → R2 Req Coverage 計算 56.3% < 70% MVP threshold → false-flag scoped impl 為 SG fail。
>
> 此 BLOCKER 在 rev 0.1.1 Round 2 spectra-review 未發現(spec-text-only review 無此盲點),需 Stage 5 PoC 真 dogfood 才暴露 → 證明 **Stage 5 PoC 是 spec quality discovery 的 evidence-driven critical layer**。

**Mechanism:** PR/commit 必 declare `scr_scope` metadata,SCR 對 declared scope 計算 coverage %;undeclared scope 視為 future round 不 flag。

**Declaration form(rev 0.2 baseline):**

```yaml
# Option A: PR description top YAML block
scr_scope:
  - REQ-024-E   # standard fake_data per operation_type
  - REQ-024-F   # fake_data_intent escape valve
  - REQ-025-A-5th  # 5th pre-flight check
scr_scope_rationale: "rev 1.31 audit-driven 加 escape valve;非 REQ-019 全 schema redo"

# Option B: commit message footer
scr-scope: REQ-024-E, REQ-024-F, REQ-025-A-5th
scr-scope-rationale: "rev 1.31 audit-driven 加 escape valve"
```

**SCR 讀取順序:**
1. PR description YAML block(if exists)
2. commit message `scr-scope:` footer(if exists)
3. fallback(rev 0.2.1 C2 closure;rev 0.2.2 C6 closure — sequential strategy 4-step,解 「+」 AND vs fall-through ambiguity):
   - **3a. First pass:** per-stack adapter § 4.10 `extract_req_tags()` extract REQ-tags from § 5.4 anchor form(高 confidence;structured AST-level extraction)
   - **3b. Second pass(only if 3a yields 0):** raw `REQ-\d+(-[A-Z]+)?` regex grep over git diff body(low confidence;text-level fallback)
   - **3c. Union:** 3a 與 3b 之 結果 union 為 auto-detected scope set;emit warning「auto-detected scope from <3a/3b/both> — declare explicit `scr_scope` for high-confidence SG verdict」
   - **3d. If union 仍為 empty:** fall through to fallback (4) PENDING verdict
   - Sequential rationale:3a 之 structured extraction 比 3b regex 精確,優先;3b 為 escape valve 對應 stack adapter unavailable / informal REQ reference 之 cases
4. fallback fallback(rev 0.2.1 B1 closure OPT-A — SOFT BLOCK + PENDING verdict,解 PoC blocker mitigation 自身失效):if 全無 declaration → SCR run 之 SG verdict 為 ⏸ **PENDING**(neither PASS nor FAIL — 3rd informational verdict state):
   - R2 計算 full-spec coverage 並 emit 「no scope declaration — declared scope required for SG hard verdict」 warning
   - Phase 5 release note 之前,commit author 必須補 declare(retroactive PR comment OR `git commit --amend` with `scr-scope:` footer)
   - 對齊 § 7.4 bypass enforcement mechanism — PENDING verdict 觸發 `P-scr-scope-pending-<id>` entry 到 active project + org decision-log(雙路徑 per § 7.4 step 1)
   - 若 commit author refuses to declare scope(明示 reject) → 視為 force_full + maturity-aware SG threshold apply(對齊 rev 0.1.1 behavior + emit 「explicit declined — full-spec mode 」audit entry);此 explicit choice 非 silent default
   - 對齊 § 8.4 invariant 「scope declaration is trust commitment」 — silent miss not allowed,must be explicit choice(declare scope OR explicit decline)

**Coverage % calculation update(rev 0.2 supersede rev 0.1.1 § 5.1):**

```
Scoped coverage:
  in-scope AC = ∪ AC of all declared REQ-XXX
  req_coverage_% = (fully_impl_in-scope_AC + 0.5 × partial_in-scope_AC) / total_in-scope_AC × 100

Full-spec coverage(parallel report,不參與 SG gate):
  req_coverage_full_% = (fully_impl_full_AC + 0.5 × partial_full_AC) / total_full_AC × 100
```

SG gate dimension R2 verdict 邏輯(rev 0.2.1 B1 closure 後完整定義):

| `scr_scope` declaration state | R2 base | SG verdict |
|:---|:---|:---:|
| ✅ explicitly declared(source 1 OR 2)| scoped coverage 對齊 maturity threshold | PASS / FAIL per § 6.1 matrix |
| 🟡 auto-detected via fallback (3) | scoped coverage(auto-detected scope)+ low-confidence warning | PASS / FAIL per § 6.1 matrix + advisory note |
| ⏸ no declaration, fallback (4) PENDING | full-spec coverage 並列 calculated | **⏸ PENDING — Phase 5 blocked until declare-or-decline** |
| ⏸ → explicit decline force_full | full-spec coverage 對齊 maturity threshold | PASS / FAIL per § 6.1 matrix(MVP 70% 仍可能 PASS;但 explicit choice not silent)|

Full-spec coverage 在所有 case 並列 report 作 trendline reference(rev 0.2 Tier 2.4 actionable report enhancement)。

**Undeclared scope policy(避免 abuse):**
- ✅ **Legal:** commit 改 < 50 LOC 之 light tier 不必 declare(auto-detect from grep 已足)
- ✅ **Legal:** rev 1.31-like scoped feature impl,explicit declare 3 REQ-XXX
- ❌ **Illegal:** 大型 architectural change 不 declare scope 「規避 SG fail」 → rev 0.2 強制 「LOC > 300 OR architectural_change=true 必 declare」(對齊 § 4.9 cost-staged tier=heavy 自動 mandate)
- **Reviewer audit:** PR reviewer 看到 declared scope 預期 commit 真 narrow within scope,**不**可包 scope-out feature(對齊 PoC insight「scope declaration is trust commitment」)

**`architectural_change` classification(rev 0.2.1 C3 closure):**

| Detection layer | Method | Notes |
|:---|:---|:---|
| Primary(auto-detect)| Memory rule grep — 若 commit diff touch ≥ 1 條 § 2 之 17 memory rule 對應 file/concept(eg. backend-schema-change-workflow → diff 含 `*.sql` schema file) → `architectural_change=true` | 對齊 [[audit-patch-cascade-verify]] 5-dim(a) cross-file grep dim |
| Secondary(author 自宣)| `scr_invocation.architectural_change: true` field in PR YAML | 對齊 § 4.9 cost-staged metadata schema |
| Override(escape)| `/scr --no-architectural-change` flag + emit warning + decision-log entry | for clear false-positive cases(eg. lint-only refactor 觸 memory rule grep)|
| Disagreement resolution | Auto-detect=true + author 自宣=false → 採 **stricter**(true wins)+ emit warning | 對齊 [[delete-dialog-no-undo-hint]] 慎思 invariant |

**Memory rule cross-cut:** SCR scope declaration 不可 exempt 17 條 inviolable memory rule(§ 2)— 不論 scope 內或外,memory rule violation 永 0 容忍(對齊 § 6.3 always-zero invariant)。

### § 8.5 REQ-ID + Natural Language Targeting(rev 0.2.4 NEW — per PO 2026-06-30 directive)

**PO directive:** 「允許 指定 requirement id , 或是口語描述功能 scr 找到相關的REQ ID 進行review」

**Purpose:** 擴展 SCR invocation — 除了 file/dir target,新增 「以 REQ-ID OR 自然語言 feature 描述」 為 target,讓 PM / QA 不需懂 code structure 即可 invoke 「我想看 REQ-005 export PDF 對齊狀況」 OR 「review 我們的 OTP 登入流程實作」。

**Invocation forms:**

```bash
# Form 1: Direct REQ-ID list
/spec-compliance-review --req REQ-019
/spec-compliance-review --req REQ-019,REQ-024,REQ-025
v7 review REQ-019                          # mode dispatcher equivalent

# Form 2: Natural language feature description (NL → REQ-ID auto-mapping)
/spec-compliance-review --feature "OTP 登入流程"
/spec-compliance-review --feature "TC JSON schema 驗證"
v7 review TC JSON 24-field schema           # natural language equivalent(N2 quote convention: v7 NL command no 「」 wrap)

# Form 3: Combined (precise REQ + NL refinement)
/spec-compliance-review --req REQ-019 --feature "schema validate"
```

**NL → REQ-ID auto-mapping algorithm(rev 0.2.4 baseline,Tier 3 calibrate):**

```python
# Detection chain (per § 5.5 detection tier hybrid)
def map_nl_to_reqs(nl_description: str, spec_path: str) -> list[ReqMatch]:
    """
    Map natural language description to REQ-IDs from spec.
    
    Returns ranked list of ReqMatch:
      [{"req_id": "REQ-019", "confidence": 0.92, "matched_text": "..."},
       {"req_id": "REQ-024", "confidence": 0.78, "matched_text": "..."}]
    """
    # Step 1: L2 regex keyword match against REQ titles
    candidates = grep_titles(nl_description, spec_path)
    
    # Step 2: L3 embedding similarity (if L4 LLM available)
    candidates = rank_by_semantic_similarity(candidates, nl_description)
    
    # Step 3: L4 LLM Q&A confirm top-3 candidates
    confirmed = llm_confirm(candidates[:3], nl_description, spec_path)
    
    # Step 4: Return top matches with confidence ≥ 0.7
    return [m for m in confirmed if m.confidence >= 0.7]
```

**Output behavior:**

| Match scenario | SCR behavior |
|:---|:---|
| 1 exact REQ match(confidence ≥ 0.9)| Direct review of that REQ |
| Multiple REQ matches(confidence 0.7-0.9)| Show候 list + ask user 確認 → review confirmed REQ(s)|
| Ambiguous(no match ≥ 0.7)| Show top-5 candidates + ask user clarify OR cancel |
| No match | Fall through to file/dir target OR error 「請明示 REQ-ID 或精確 feature 描述」 |

**Target resolution priority(when multiple flags provided):**

1. `--req REQ-XXX`(explicit)→ highest precedence
2. `--feature "NL"`(auto-detect)→ medium precedence
3. File/dir target → lowest precedence
4. Combined `--req + --feature` → intersection(`--feature` refines `--req` scope)

**Use case examples:**

| User intent | Invocation | Effect |
|:---|:---|:---|
| PM 想知道 「OTP 登入」 做完沒 | `/spec-compliance-review --feature "OTP 登入流程"` | NL → REQ-008 mapping → review REQ-008 impl |
| QA 想 audit 特定 REQ test 對齊 | `/spec-compliance-review --req REQ-019` | Direct REQ-019 review |
| Dev 想看 「TC JSON schema」 across all script | `v7 review TC JSON 24-field schema` | NL → REQ-019 + review across scripts/ |
| Tech lead 想 audit P0 critical REQs | `/spec-compliance-review --req REQ-019,REQ-024,REQ-025` | Comma-separated multi-REQ |

**對齊 § 8.4 scope declaration:** `--req` 之 REQ list 自動 fill `scr_scope`(等同 explicit declaration);不再 fallback to (3)/(4)。 SG verdict 即可 high-confidence。

**對齊 § 8.7 popup framework(rev 0.2.6 cascade — C4 closure):** 上 Match scenario table 之 「Ambiguous(no match ≥ 0.7)→ Show top-5 candidates + ask user clarify OR cancel」 升級為 § 8.7 multi-slot popup framework — 該 row 仍適用但走 § 8.7.1 PM-friendly popup format(用 PM 看得懂的話 + 附成本 + 預設選 + ⓧ escape);single-slot scenarios(target slot only)仍走原 single-question popup。

---

### § 8.6 Verbosity Parameter — 簡要 / 全部(rev 0.2.4 NEW — per PO 2026-06-30 directive)

**PO directive:** 「支持 參數 簡要 / 全部 output資訊」

**Purpose:** Verbosity 控制 SCR output detail level — 對 PM quick-decision 之「簡要」 模式 vs 對 audit / dev debugging 之「全部」 模式。

**Invocation forms:**

```bash
# Default: 簡要 mode (對 PM quick decision-making 優化)
/spec-compliance-review <target>
/spec-compliance-review <target> --brief        # 等同 default

# Full mode (對 audit + dev debugging 詳細 R0-R6 + appendix)
/spec-compliance-review <target> --full
/spec-compliance-review <target> --verbose      # 等同 --full

# Custom granularity (mid-level — 對 QA test planning 優化)
/spec-compliance-review <target> --medium       # PM Lens + QA Lens 詳;Developer Lens 簡;Appendix 略
```

**Verbosity matrix:**

| Mode | TL;DR | PM Lens | QA Lens | Dev Lens | Appendix | Use case |
|:---|:---:|:---:|:---:|:---:|:---:|:---|
| **簡要(brief / default)** | ✅ full | ✅ full | 🟡 summary | 🟡 summary | ❌ omit | PM quick decision(ship-or-not)|
| **medium** | ✅ full | ✅ full | ✅ full | 🟡 summary | ❌ omit | QA test planning |
| **全部(full / verbose)** | ✅ full | ✅ full | ✅ full | ✅ full | ✅ full | Audit / dev debugging |

**Per-section content per verbosity:**

| Section | 簡要 | medium | 全部 |
|:---|:---|:---|:---|
| § TL;DR | 1-3 sentence ship verdict + risk 摘要 | same | same |
| § PM Lens 風險摘要 | Plain prose 4 行 + ship decision | same | same |
| § PM Lens 📋 規格 ↔ 實作對照表 | 表格(complete / partial / missing 3 群)| same | same |
| § PM Lens 趨勢 / Time-to-Ship / Effort-Value | 表格 | same | + 計算公式 detail |
| § QA Lens 測試對齊狀況 | bullet list 已涵蓋 + gap | full sub-AC detail | full + test case template |
| § QA Lens 推薦測試重點 | top 3 | top 5 | full prioritized list |
| § Developer Lens fix list | top 3 + 1-line each | top 5 + 命令 each | full + 架構建議 |
| § Appendix(R0-R6 / SG matrix / metrics.json sidecar reference)| 🚫 omit | 🚫 omit | ✅ full sections |

**Output size estimate per mode:**

| Mode | Markdown LOC | JSON sidecar | Read time |
|:---|---:|:---:|:---:|
| 簡要 | ~80 LOC | full structured(unchanged)| 1-2 min |
| medium | ~150 LOC | full structured | 3-5 min |
| 全部 | ~400-500 LOC(對齊 rev 0.2.3 既有 v0.1 output)| full structured | 10-15 min |

**`metrics.json` sidecar 不受 verbosity 影響** — 永遠 full structured(對齊 § 9.4.3 trendline grep 需 schema 穩定)。

**Configuration source priority:**
1. CLI flag(`--brief` / `--medium` / `--full`)— highest
2. Environment variable(`SCR_VERBOSITY=brief/medium/full`)
3. `state.md` `scr_default_verbosity:` field per-project default
4. Global default = **簡要**(per PO 2026-06-30 directive — PM-friendly first)

**對齊 `[[user-working-style]]` cognitive load discipline:** Default 簡要 → 大多 invocation 對 PM/QA 是 1-2 min read,not overwhelming;`--full` opt-in 才 dump audit detail。

---

### § 8.7 Natural Language Invocation & Popup Disambiguation(rev 0.2.5 NEW — per PO 2026-06-30 directive)

**PO insight:** 「no one be able to remember the detail commands in v7 / spec-compliance-review。 I hope v7 can support nature language input」

**PO insight on disambiguation:** 「just popup a message and ask user to chose and make decision. sometime PM/QA may not really know the feature」

**Purpose:** § 8.5 既有 `--feature "NL"` 已為 REQ matching 提供 NL,但 invocation 整體仍依賴 flag 組合(target / verbosity 等)。 本 section 擴展為 **全 invocation 自然語言** — PM / QA 不需記任何 flag,SKILL 自動 parse + 歧義時主動 popup 詢問,且選項用 PM 看得懂的話。

**Intent slot model(4 slots per NL invocation):**

| Slot | 含義 | 可選值 | Source |
|:---|:---|:---|:---|
| **Action** | 動作意圖 | review / audit / check / 對齊檢查 | NL parse |
| **Target** | 對象 | file path / dir / project name / REQ-ID / NL feature description | NL parse 或 git diff |
| **Verbosity** | 詳細度 | brief(default)/ medium / full | NL parse,fallback default |
| **Focus Lens** | 視角過濾(NEW)| all(default)/ remaining_task / coverage_gaps / open_findings / blockers_only / trend_only | NL parse,fallback all |

**範例 NL invocation parsing:**

| Raw NL phrase | Action | Target | Verbosity | Focus Lens |
|:---|:---|:---|:---|:---|
| `v7 review sanity check 看還剩什麼` | review | sanity-check project | brief | **remaining_task** |
| `v7 看 namecard v3 的 OTP 流程做完沒` | review | --feature "OTP 登入流程" → REQ-008 | brief | remaining_task |
| `v7 ship 前 check 一下這個 PR` | review | git diff HEAD~1 | brief | blockers_only |
| `v7 review sanity check 全部資訊` | review | sanity-check | **full** | all |
| `v7 比較這次跟上次` | review | (carry from state.md last target) | brief | trend_only |

**Relationship to § 8.5 既有 NL→REQ algorithm(C1 closure — SSOT delineation):** § 8.5 step 1-4(L2 regex / L3 embedding / L4 LLM confirm / confidence ≥ 0.7 filter)為 § 8.7 之 **Target slot** parsing 之 sub-step;Action / Verbosity / Focus Lens 3 個 slot 為 § 8.7 NEW lexicon。 § 8.7 之 L5 popup 為 § 8.5 之 「Multiple REQ matches(confidence 0.7-0.9)→ Show list + ask user」 之擴展(從 single-slot 升 multi-slot popup framework per § 8.7.1)。 SSOT pattern:single-slot NL parsing 進 § 8.5;multi-slot full-invocation NL parsing 進 § 8.7。

**Parsing chain(對齊 § 5.5 L1-L5 detection tier):**

1. **L2 keyword match** — 對 4 slot 各自的 lexicon dict(eg. 「還剩什麼」「remaining」「沒做完」→ Focus Lens = `remaining_task`)
2. **L3 NL→REQ embedding**(reuse § 8.5 既有 algorithm)— for Target slot 之 feature description
3. **L4 LLM Q&A confirm** ambiguous slots
4. **L5 popup disambiguation**(fallback when confidence < threshold per § 8.7.1)

**Popup disambiguation contract:**

| Trigger condition | SKILL behavior |
|:---|:---|
| All slots confidence ≥ 0.9 | Echo parsed intent inline(1 行)+ § 8.10 cost preview + run |
| Any 1 slot confidence 0.7-0.9 | Single-question popup + echo + run |
| ≥ 1 slot confidence < 0.7 | **Multi-question popup**(per § 8.7.1)+ wait for user pick |
| All slots unparseable | Reject + suggest `v7 ?` for example phrasings(per § 8.8)|
| Non-SCR intent detected | Reject + redirect(per § 8.9)|

#### § 8.7.1 Popup question format(對齊 PO PM-friendly 洞察)

每個 popup question 必滿足:

1. **用 PM 看得懂的話** — 避免「REQ-scoped fallback 3a」這種術語
2. **附「會幹什麼 / 多久」** — 讓 PM 判斷成本
3. **預設選最常見的** — pre-highlight default ⭐
4. **必有 escape option** ⓧ「我打錯了,讓我重打」(對齊 § 8.11)
5. **跑前 echo final 解讀** — 1 行明示 SKILL 即將跑什麼(對齊 § 8.10)

**Example popup(PO 範例:`v7 review sanity check 看還剩什麼`,3 slot 歧義):**

```
🤔 您的指令我解讀有幾處不確定,請選擇:

Q1.「sanity check」指的是?
   ⓐ 整個 sanity-check 專案(12 個 script,3851 LOC)→ ~3 分鐘
   ⓑ 只看 pre-flight check 那個檔 → ~30 秒
   ⓒ 只看「測試 case 撰寫紀律」相關需求(REQ-019/024/025)→ ~1 分鐘
   ⓧ 我打錯了,讓我重打

Q2.「看還剩什麼」指?
   ⓐ「規格還沒做完」的部分(coverage gap)→ PM 視角
   ⓑ「之前 review 已 flag 但還沒修」的(deferred findings)→ 開發 backlog 視角
   ⓒ 兩個都看 ⭐ 預設
   ⓧ 我打錯了
```

#### § 8.7.2 Memory across invocations(state.md per-user default)

避免重複問同樣問題 — `docs/pm/<project>/state.md` 新增 sub-key:

```yaml
v7_user_intent_history:
  - phrase: "sanity check"
    resolved_to: "sanity-check project (full scope)"
    confidence_after_3_uses: 0.95
    last_used: 2026-06-30
  - phrase: "看還剩什麼"
    resolved_to: "focus=remaining_task"
    confidence_after_2_uses: 0.85
    last_used: 2026-06-30
```

**Decay rule:**
- 每次 user 接受同樣解讀 → confidence + 0.05;**reset `last_used = now`**
- 每月未用 → confidence - 0.1(避免 stale phrasing 鎖死)
- 達 confidence ≥ 0.9 後 silent default,不再 popup
- 達 confidence < 0.5 後 entry 從 state.md 移除

**Reference clock(N5 closure):** decay 之 reference 為 `last_used`(非 `first_seen`);每 30 天未用即 trigger 1 decay tick(continuous: `decay_count = floor((now - last_used) / 30 days)`;total `confidence -= decay_count × 0.1`)。 user 接受同樣解讀即 reset。 「now」 採 system local time,跨 timezone project 採 UTC(state.md `v7_decay_clock_timezone:` 可 override)。

#### § 8.7.3 Focus Lens 對 output 之影響

| Focus Lens | Output 行為 |
|:---|:---|
| `all`(default)| 全 3-role lens 顯示(per § 9.5)|
| `remaining_task` | PM Lens 只列 partial + missing(complete 摺起來,1 行 summary)+ § 9.6.4 open findings 全顯 + § 9.6.3 Time-to-Ship 強調 |
| `coverage_gaps` | 只顯 § 5.6 coverage gap table + § 9.6.1 規格↔實作對照 |
| `open_findings` | 只顯 § 9.6.4 open vs closed + 4-tier findings(BLOCKER/CONCERN 段)|
| `blockers_only` | 只顯 4-tier BLOCKER + SG Gate verdict |
| `trend_only` | 只顯 § 9.6.2 趨勢 table + § 9.4.3 trendline |

**摺起來不等於隱藏** — complete 段一律以 1 行 summary 顯示(eg. 「✅ 完整實作 6 個 REQ 已收摺,展開請加 `--full`」),讓 PM 知道有東西被收掉。

**N10 rev 0.3 closure — collapse markdown 實作決定:**

| Option | 範例 | Pros | Cons |
|:---|:---|:---|:---|
| **1-line bullet ⭐ Chosen** | `> ✅ 完整實作 6 個 REQ 已收摺,展開請加 --full` | Plain markdown portable;CI render consistent;對齊 [[human-first-docs]] readable | No actual JS collapse interaction |
| `<details>/<summary>` | `<details><summary>✅ 6 個 REQ</summary>full list</details>` | Native browser collapse interaction | HTML in markdown 可讀性差;CI 不一致 render(eg. Slack/Telegram 不支援);raw markdown 不 PM-friendly |

**Decision:** 1-line bullet — collapse 是 SCR output 「狀態指示」 不是 interactive UI element;plain markdown 對齊 multi-IDE rendering(Claude Code / Antigravity / Codex 都 consistent display);user 想看 full 直接 `--full` flag,不需 JS click。 Per `[[human-first-docs]]` plain prose 為主 invariant。

**Interaction with § 8.6 verbosity(C2 closure — 2-dim filter resolution):**

1. **Focus Lens 先過濾** — 決定「哪些 section 顯示 / 摺起來」
2. **Verbosity 再裁切** — 在 顯 的 section 內決定「每段內容多詳細」
3. **衝突解** — eg. `focus_lens=trend_only` × `verbosity=full` → 只顯 trend section(per Focus Lens),但該 section 內展開 full detail(含計算公式 + 範例 per § 8.6 full)
4. **`focus_lens=all` 等同沒 filter** → 純套用 § 8.6 verbosity matrix
5. **`verbosity=brief` × `focus_lens=blockers_only`** 等 narrow combination → 顯 1 section + 該 section brief summary(可能 30 行以下,適合 「just看哪些 ship-blocker」 super-quick scan)

---

### § 8.8 Help / Discovery —「v7 ?」(rev 0.2.5 NEW)

**PO insight:** 「PM/QA may not really know the feature」 — 新 user 第一次來 SKILL 必須能 self-discover 能做什麼,不能被迫先讀 docs。

**Trigger forms:**

- `v7 ?`
- `v7 help`
- `v7 你能做什麼`
- `v7 怎麼用`
- `/spec-compliance-review --help`(等同)

**Output behavior — plain-prose discovery card(對齊 `[[human-first-docs]]`):**

```markdown
👋 V7 SCR 是「規格對齊檢查」工具 — 確認 code 真的有按 spec 做。

你可以這樣問(不需記 flag,自然語言即可):

📋 看現況
- 「v7 review sanity check 看還剩什麼」
- 「v7 看 namecard v3 哪些 REQ 沒做完」

🚦 ship 前 check
- 「v7 ship 前 check 一下這個 PR」
- 「v7 看這次 commit 有沒有破規」

📈 比較進度
- 「v7 比較這次跟上次的差距」
- 「v7 看上週到現在改了什麼」

🎯 聚焦特定 feature
- 「v7 OTP 流程做完了嗎」
- 「v7 review REQ-019 schema validation」

📊 想看詳細
- 「v7 review sanity check 全部資訊」(switch to full mode)
- 「v7 看哪些是 blocker」(只看 blockers_only)

💡 不確定要看什麼? 直接打「v7 看一下」 — 會問你想看什麼。
```

**不要做的事:**

- ❌ 列 `--brief / --full / --req` 等 flag(對 PM 是噪音)
- ❌ 秀 SG Gate / R0-R6 等技術術語(藏在 Appendix)
- ❌ 列完整 capability matrix(只列高頻 4-5 群 use case,各 1-2 NL example,total 8-10 phrasings — N3 alignment with actual discovery card)

**Discovery card 之 example 來源:**

- High-frequency phrases from § 8.12 audit log(若有 90+ 天歷史)
- Fallback: 上述 hardcoded 8 examples(對齊 typical PM use case)
- Per-project customization(若 state.md 有 `v7_help_examples` 自訂 list)

---

### § 8.9 Negative Scope Reject(rev 0.2.5 NEW)

**Problem:** 若 SKILL 對任何 `v7 ...` input 都嘗試 parse + run,會出現 silent 誤觸發 — eg. 「v7 幫我寫一個 react component」 變成 hallucinated review garbage。

**Solution:** SKILL 必須能識別 **out-of-scope intent** 並 explicit reject + redirect。

**Rejected intent categories(non-exhaustive):**

| Category | 範例 phrase | Reject + Redirect |
|:---|:---|:---|
| Code generation | 「v7 幫我寫 component / function」 | 「V7 只做 spec 對齊 review,寫程式請改用一般 Claude Code prompt」 |
| Bug fix | 「v7 修這個 bug」 | 「V7 不修 code,只 report 違規。 修 bug 請直接描述問題 + 檔案 path」 |
| Code refactor | 「v7 重構這段」 | 「V7 不修 code。 重構請走 Phase 4 orchestrator refactor 流程」 |
| Spec writing | 「v7 幫我寫 spec」 | 「V7 review spec compliance,不寫 spec。 寫 spec 請用 PM Skill `propose` workflow」 |
| Test execution | 「v7 跑測試」 | 「V7 不執行測試,只看 code-spec 對齊。 跑測試請用 `pytest` 或 PM Skill `sanity-tc-runner`」 |
| Deploy / git ops | 「v7 deploy」 / 「v7 commit」 | 「V7 不操作 git / deploy。 ship 前 check 請改問「v7 ship 前 check 這個 PR」」 |
| Pure chitchat | 「v7 你好」 / 「v7 在嗎」 / 「v7 hi」 — explicit greeting only | 「我是 V7 SCR(規格對齊 reviewer)。 試試 `v7 ?` 看可以怎麼用」 |
| Ambiguous status query | 「v7 怎樣?」 / 「v7 how are things」 / 「v7 還好嗎」 — could be greeting OR project status request | **走 § 8.7 popup**:Q「您要看 project compliance status 還是 chitchat? ⓐ 看 status(等同 v7 review <project> compliance status)/ ⓑ chitchat(本 reject 提示)/ ⓧ 我打錯了」 — N7 rev 0.3 closure(reject scope narrowed to explicit greetings only) |

**Reject response template:**

```markdown
🚫 您要的不是 V7 SCR 的職責。

我理解您想做:**<paraphrase user intent>**

但 V7 SCR 只做「規格 vs code 對齊 review」 — 不會:
- 寫 / 改 code
- 跑測試
- 做 git / deploy 操作

**建議改用:**
- <對應正確的工具/流程,per 上表>

若您原意是想「review <某 spec area>」,可以試問:
- 「v7 review <relevant area>」
```

**Implementation note:**

- L4 LLM intent classifier 必含 negative training set(non-SCR phrasings)
- 不確定時(confidence ambiguous SCR vs non-SCR)走 § 8.7 popup,**不要默默硬跑**
- Reject 不算 invocation,**不寫 metrics.json**(對齊 § 8.12 — 只 log 完成或 cancelled run)
- Reject phrase 該 log 到 `state.md` `v7_rejected_phrases:` debug list(供 future negative training set 累積)

---

### § 8.10 Cost + Time Preview(rev 0.2.5 NEW)

**Purpose:** § 8.7 popup 確認後 / NL parsed 後,SKILL 在 **實際開跑前** echo 1 行 budget,讓 PM 在「3 分鐘 vs 30 秒」之間 informed decision。

**Preview content template:**

```markdown
> 🎯 OK 我會跑:整個 sanity-check 專案 / 詳細版 / 看 remaining task
> ⏱ 預估 ~3 分鐘 / 輸出 ~600 行
> 💰 預估 ~5k tokens
> ⚠ 跑到一半可隨時 Ctrl-C 中斷,partial output 自動清理(per § 8.11 Level 3)
```

> **N4 closure note:** 早期版本寫 「5 秒內按 Esc」 不準確 — SKILL 無 keystroke event hook;真實 escape 是 mid-run Ctrl-C(§ 8.11 Level 3 atomic cleanup)。

**Preview field requirements:**

| Field | Source | When omit |
|:---|:---|:---|
| **What will run**(target + verbosity + focus lens)| Parsed from § 8.7 | Never |
| **Estimated time** | Cost tier(§ 4.9)× LOC scope | Never |
| **Estimated output LOC** | Verbosity matrix(§ 8.6)| Never |
| **Estimated tokens** | LLM call count(R3/R4 may use L4)| 0-LLM run(skip)|
| **Cancel hint** | Always | Never |

**Threshold-based 2-stage confirm:** 若預估 ≥ 「heavy tier」(per § 4.9)— eg. > 5 min / > 10k tokens / > 1000 LOC output — SKILL **必再次 confirm**:

```
⚠ 此 review 規模較大(預估 8 分鐘 / 12k tokens / ~900 行)
要繼續嗎? [y] / [n] / [改成簡要版]
```

**Time estimate calibration:**

| Cost tier(§ 4.9)| Time | Output LOC | Token |
|:---|:---|:---|:---|
| light(< 50 LOC code)| 10-30 sec | 50-100 LOC | 0-1k |
| medium(50-300 LOC)| 30 sec - 2 min | 100-300 LOC | 1-3k |
| heavy(> 300 LOC)| 2-5 min | 300-600 LOC | 3-8k |
| force-full(全 project)| 5-15 min | 600-1500 LOC | 8-20k |

每次 invocation 結束後,actual 數字寫入 **2 places(C3 closure — SSOT delineation):**

1. **Per-invocation 完整數字** → `metrics.json` 之 `nl_intent_resolution.actual_cost`(per § 8.12 schema)— 單次 invocation 之 ground truth
2. **移動平均 + 最近 N=20 次 raw** → `state.md` 之 `v7_cost_calibration:`(per-tier rolling window;N 配置 per project,default 20)— aggregate trend for estimate refinement

> **§ 7.3 SG-Bypass audit log 是完全獨立 sink** — 不混 cost data。 3 sinks:`metrics.json` per-invocation / `state.md` aggregate / SG-Bypass audit append-only。

**對齊 `[[user-working-style]]` cost-conscious 原則:** PM/QA invocation 該被 informed about cost,而不是 silent burn budget。

---

### § 8.11 Escape Route(rev 0.2.5 NEW)

**Purpose:** Popup 跟 mid-run 都該有「我打錯了 / 我想取消」的退路 — 避免 user 被鎖在錯誤分支或 silent burn budget。

**Escape points(3 levels):**

#### Level 1: Popup 內部 escape

每個 § 8.7 popup question 必含 option ⓧ「我打錯了,讓我重打」:

```
ⓧ 我打錯了,讓我重打 → 取消本次 invocation,user 重打 NL phrase
```

選 ⓧ 之 SKILL behavior(B1 closure — Option A silent escape per PO 「打錯了」 原意):

- 立即取消本次 invocation(0 partial run)
- 0 metrics.json garbage 留 disk
- **0 audit log entry**(silent escape;§ 8.12 status enum 不含 `cancelled_popup`)— 對齊 PO 「打錯了 = 真退路 = 0 痕跡」 語意
- 若需 parser self-improvement 累積 phrase 歷史,改用 § 8.9 negative scope `v7_rejected_phrases:` debug list pattern(opt-in via state.md `v7_popup_escape_log_to_debug: true`)
- 提示 user 重打,可選 suggest correction(eg.「您是不是想說 X?」基於 § 8.7.2 state.md `v7_user_intent_history:` fuzzy match,**不是** metrics.json)

#### Level 2: Pre-run confirm escape

§ 8.10 cost preview 之 `[n]` 取消:

- 退回 prompt,user 可重新打 NL
- 0 partial run
- audit log mark `status: cancelled_preview`(per § 8.12)

#### Level 3: Mid-run Ctrl-C

跑到一半發現問錯了 → Ctrl-C 必滿足:

- ✅ Cleanup partial `metrics.json`(不留 garbage)
- ✅ Cleanup partial markdown report(若已開始 Write)
- ✅ Audit log mark `status: cancelled_mid_run`(per § 8.12)
- ✅ 短訊息回 user:「已取消,N 秒內 0 檔案異動」
- ✅ 若已有 atomic-write tmp file,清掉

**Implementation note:** Mid-run cleanup 需 atomic — partial Write 若 crash 可能 leave garbage。 建議 pattern:

1. Write 之 tmp filename 為 `<output_dir>/.scr-tmp-<timestamp>-<rand-6>.{json,md}`(timestamp + 6-char random 後綴)
2. 完成才 `mv .scr-tmp-*.json final.json` + `mv .scr-tmp-*.md final.md`
3. Ctrl-C signal handler 觸發 → 刪當前 SKILL invocation 之 tmp files(by PID match,**不刪他人 in-flight 的**)
4. Atomic guarantee — 看到 `final.json` 即代表完整 review

**N6 closure — tmp location & concurrency:** 隨機後綴 + PID-bound cleanup 防 concurrent invocation 同 target 衝突(eg. user 對同 project 並發 2 個 v7 invocation 不會互相清掉對方 tmp)。 Tmp dir 預設與 final output 同 dir(便於 cleanup);若 read-only filesystem 可 override 至 `state.md` `v7_tmp_dir:` field。

**對齊 `[[delete-dialog-no-undo-hint]]`:** Escape 取消後 0 file change,**不顯示**「已隱藏 / 可還原」 措辭 — 真的 0 file 異動,no need 提還原。

---

### § 8.12 NL Intent Resolution Audit Trail(rev 0.2.5 NEW)

**Purpose:** 每次 popup decision / NL resolution 該 log 到 `metrics.json`,讓 future SCR trend 分析能回答:

- PM 通常想看什麼?(高頻 phrasing → § 8.8 help card examples 來源)
- 哪些 phrasing 容易被誤解?(high popup-rate → § 8.7 parser 該改善)
- 哪些 default 解讀 user 經常 override?(default 該調整)
- 哪些 phrase 是 negative scope?(§ 8.9 reject set 累積)

**`metrics.json` 新增 sub-section `nl_intent_resolution`:**

```json
{
  "nl_intent_resolution": {
    "format_version": "scr-rev-0.2.6-nl-v1",
    "raw_phrase": "v7 review sanity check 看還剩什麼",
    "parsed_slots": {
      "action": { "value": "review", "confidence": 0.95 },
      "target": { "value": "sanity-check project", "confidence": 0.85 },
      "verbosity": { "value": "brief", "confidence": 1.0, "source": "default" },
      "focus_lens": { "value": "remaining_task", "confidence": 0.80 }
    },
    "popup_questions_asked": 2,
    "user_choices": { "Q1": "A", "Q3": "C" },
    "resolution_final": {
      "target": "sanity-check project (full scope)",
      "verbosity": "brief",
      "focus_lens": "remaining_task + open_findings"
    },
    "resolution_confidence_final": 0.95,
    "user_overrode_default": false,
    "memory_default_applied": false,
    "memory_default_updated": false,
    "status": "completed",
    "actual_cost": {
      "duration_seconds": 165,
      "output_loc": 612,
      "tokens_estimate": 5200
    }
  }
}
```

**`status` field values(4 states — B1 closure):**

| Status | When |
|:---|:---|
| `completed` | Full invocation 跑完 |
| `cancelled_preview` | User picked `[n]` at § 8.10 cost preview(per § 8.11 Level 2)|
| `cancelled_mid_run` | Ctrl-C(per § 8.11 Level 3)|
| `rejected_negative_scope` | Hit § 8.9 reject — log 進 `state.md` `v7_rejected_phrases:`,**不寫 metrics.json** |

> **Note(B1 Option A 對齊):** Popup ⓧ escape(§ 8.11 Level 1)**完全不寫 metrics.json**(silent escape per PO 「打錯了」 原意);若需 phrase history 進 parser self-improvement,改用 § 8.9 negative scope `v7_rejected_phrases:` debug list pattern。 故無 `cancelled_popup` status enum。

**Trend analysis use cases(future SCR feature — defer to rev 0.4+):**

```python
# How often does PM say "看還剩什麼"?
nl_phrase_frequency = aggregate("nl_intent_resolution.raw_phrase", last_90_days)

# Which phrases trigger most popups?(parser 該改善)
high_popup_phrases = filter("popup_questions_asked >= 2", group_by="raw_phrase")

# Which slot defaults does user override most?(default 該調整)
override_rate_per_slot = aggregate("user_overrode_default", group_by="slot")

# Cost estimate accuracy
cost_error = aggregate("actual_cost.duration_seconds - estimate", group_by="cost_tier")
```

**Privacy / compliance:**

- Raw phrase 是 user-typed text,**assumed 不含 secret / PII**(SKILL warn 若 phrase 含 typical secret pattern eg. `password=...`)
- 若 PO 對 logging 有疑慮,可加 `state.md` `v7_audit_opt_out: true` 退出 audit log(0 nl_intent_resolution sub-section 寫出)
- Audit log retention:per-project metrics.json 跟 review markdown 一起 git track;cross-project aggregation 留 local 不上傳

---

### § 8.13 Invocation Lifecycle — Numbered Flow Chart(rev 0.3 N11 NEW)

**Purpose:** Consolidate § 8.7(NL parse + popup)+ § 8.10(cost preview + heavy-tier gate)+ § 8.11(escape route)+ § 8.12(audit log)散在 4 section 之 sequence 為 1 numbered flow chart,便於 SKILL impl reader 不需 reconstruct。

**Per Round 2 spectra-review N11 NEW finding(commit c81690b):** prior rev 0.2.6 sections describe steps but lack consolidated lifecycle map → SKILL impl ambiguity risk(cost 1.5 → 0.3 fix-now in rev 0.3 bundle per `[[incremental-rev-cascade]]`)。

### § 8.13.1 8-Step Canonical Flow

```
┌──────────────────────────────────────────────────────────────────────┐
│  V7 SCR Invocation Lifecycle(canonical 8-step)                       │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  1. NL parse → 4-slot intent extraction (§ 8.7)                      │
│     action / target / verbosity / focus_lens                         │
│         │                                                            │
│         ▼                                                            │
│  2. Confidence threshold check (§ 8.7 popup contract)                │
│     ┌─ All ≥ 0.9 ──────────────► skip popup, goto 3                  │
│     ├─ 1 slot 0.7-0.9 ──────────► single popup → answer → goto 3    │
│     ├─ ≥ 1 slot < 0.7 ──────────► multi popup (§ 8.7.1) → goto 3    │
│     ├─ All unparseable ─────────► reject + suggest `v7 ?` (§ 8.8)   │
│     └─ Non-SCR intent ──────────► reject + redirect (§ 8.9)         │
│         │                                                            │
│         ▼                                                            │
│  3. Echo final parsed intent (1 line — per § 8.10 banner pattern)    │
│         │                                                            │
│         ▼                                                            │
│  4. Cost + Time Preview (§ 8.10 — 5-field template)                  │
│     target / time / output LOC / tokens / Ctrl-C cancel hint         │
│         │                                                            │
│         ▼                                                            │
│  5. Heavy-tier gate check (§ 8.10 — > 5min OR > 10k OR > 1000 LOC)   │
│     ┌─ Not heavy ─────────────► goto 6                              │
│     ├─ Heavy, user [y] ──────► goto 6                              │
│     ├─ Heavy, user [n] ──────► cancel(audit `cancelled_preview`)  │
│     └─ Heavy, user [改簡要] ──► verbosity = brief, goto 6           │
│         │                                                            │
│         ▼                                                            │
│  6. Run R0-R6 review                                                 │
│     Write tmp files atomically (§ 8.11 — `<dir>/.scr-tmp-*` random) │
│     Ctrl-C during run → atomic cleanup + audit `cancelled_mid_run`  │
│         │                                                            │
│         ▼                                                            │
│  7. Write audit log (§ 8.12 — metrics.json `nl_intent_resolution`)   │
│     status ∈ {completed, cancelled_preview, cancelled_mid_run,       │
│               rejected_negative_scope}                               │
│     (Popup ⓧ silent — does NOT write per § 8.11 L1 Option A)         │
│         │                                                            │
│         ▼                                                            │
│  8. Cleanup tmp → final mv + emit output                             │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

### § 8.13.2 Step Cross-Reference Matrix

| Step | Section | Key contracts |
|:---:|:---|:---|
| 1 | § 8.7 | 4-slot intent model + L2-L5 parsing chain |
| 2 | § 8.7.1 | Popup 5 mandatory conditions(PM 語言 / 附成本 / 預設選 / ⓧ escape / echo)|
| 3 | § 8.10 banner | 1-line echo of final resolved intent |
| 4 | § 8.10 | 5-field preview template |
| 5 | § 8.10 | Heavy-tier 2-stage confirm [y]/[n]/[改簡要版] |
| 6 | § 8.11 atomic | `<output_dir>/.scr-tmp-<timestamp>-<rand-6>.{json,md}` + PID-bound cleanup |
| 7 | § 8.12 | 4-state status enum + `format_version: scr-rev-0.2.6-nl-v1` |
| 8 | § 8.11 atomic | `mv .scr-tmp-*.json final.json` 完成標誌 |

### § 8.13.3 Status Audit Path Map

| Path | Step where exit | Audit log status |
|:---|:---|:---|
| Happy path completion | Step 8 | `completed` |
| User cancels at heavy-tier gate | Step 5 [n] | `cancelled_preview` |
| User Ctrl-C mid-run | Step 6 | `cancelled_mid_run` |
| Negative scope reject | Step 2 → § 8.9 | `rejected_negative_scope` |
| Popup ⓧ escape | Step 2 → § 8.11 L1 | **silent — no log entry**(per § 8.11 L1 Option A B1 closure)|
| All unparseable + help suggested | Step 2 → § 8.8 | **silent — no log entry**(per § 8.7 popup contract row 4)|

### § 8.13.4 SKILL.md impl alignment

SKILL.md v0.3+ implementing this lifecycle 應 mirror 8-step structure in code organization(eg. `dispatch_v7()` function with numbered comments per step)— maintenance / debugging future invocations 對 step-by-step structured。

---

## § 9. Reporting Schema(enhanced-v1 inherit + SCR sections)

> Requirement anchor: REQ-012(§ 9.5-9.8 3-Role human-first output);REQ-008(§ 9.2 SG Gate Decision 4-state verdict);REQ-011(§ 9.2 PENDING verdict)

### § 9.1 § 1-5 inherit from spectra-review enhanced-v1

直接 reuse spectra 5 section schema(對齊 `[[human-first-docs]]` familiarity):
- § 1 Mental Lens(4 mental acts)
- § 2 4-Tier Findings(BLOCKER / CONCERN / NIT / STRENGTH)
- § 3 Critical Hotspots(cascade depth 1-5)
- § 4 Effective Cost Matrix(impact × probability)
- § 5 Verdict(ship-as-is / fix-blockers / revise-design)

### § 9.2 § 7 SG Gate Decision(NEW — SCR-specific)

```markdown
## § 7. SG Gate Decision

**Project maturity:** MVP / GA / mature
**SG threshold applied:** (見 § 6.1 table column)

| Dimension | Required | Actual | Status |
|:---|:---:|:---:|:---:|
| R0 Spec Cross-Layer Conflict | 0 | 0 | ✅ pass |
| R2 Req Coverage | ≥70% | 96.6% | ✅ pass |
| R3 Func Compliance | ≥80% | 91.3% | ✅ pass |
| R4 Design Compliance | ≥70% | 74.2% | ✅ pass |
| R5 Arch Violation | ≤3 | 1 | ✅ pass |
| R5 Memory Rule Violation | 0 | 0 | ✅ pass |
| Unspec'd entry-point | ≤5 | 2 | ✅ pass |
| Missing required code | 0 | 0 | ✅ pass |
| R6 Lint baseline 增 | ≤0 | -2 | ✅ pass |

**SG Verdict:** ✅ PASS / ⚠ SOFT FAIL / 🔴 HARD FAIL / ⏸ PENDING(missing scr_scope declaration — must declare-or-decline per § 8.4 fallback (4) OPT-A)
**Allowed Phase transition:**
- ✅ PASS → Phase 4.5 → Phase 5 ✅
- ⚠ SOFT FAIL → Phase 4.5 → Phase 5 ✅ with PO override(對齊 § 7 SG-Bypass)
- 🔴 HARD FAIL → 🔴 blocked
- ⏸ PENDING → ⏸ blocked-pending(awaiting scope declaration per § 8.4 OPT-A;commit author 補 declare via PR comment / amend OR explicit decline force_full)
**Bypass:** none / urgent-fix (reason: ...) / pending-scope (refer § 8.4)
```

### § 9.3 § 8 Compliance Coverage Matrix(NEW — SCR-specific)

```markdown
## § 8. Compliance Coverage Matrix

### Bi-dir traceability summary

| Direction | Total | Found | Gap | Coverage |
|:---|:---:|:---:|:---:|:---:|
| Spec → Code(REQ → impl)| 87 AC | 82 + 3 partial | 2 missing | 96.6% |
| Code → Spec(entry → REQ)| 35 entry | 33 tagged | 2 unspec'd | 94.3% |

### Top 5 violations(by effective cost)

| ID | Severity | Cost | File:Line | Quick fix hint |
|:---|:---:|:---:|:---|:---|
| V-001 | 🔴 BLOCKER | 7.2 | src/api/export.py:88 | Add REQ-005 docstring tag |
| V-002 | 🟡 CONCERN | 4.5 | templates/export.html:42 | Implement download button |
...
```

### § 9.4 Actionable Compliance Report enhancements(rev 0.2 Tier 2.4 NEW)

**Purpose:** % 數字單一 metric 不夠 actionable;rev 0.2 加 top-10 / quick-wins / trendline 3 sub-section,讓 PM/Dev 看 report 立刻 know next step。

**§ 9.4.1 Top-10 violations table — extends § 9.3 above:**

- 表格已存於 § 9.3;rev 0.2 加 column 「Quick fix LOC」(estimate impl effort)
- Sort by `effective_cost = impact × probability`(對齊 spectra enhanced-v1 Effective Cost Matrix)

**§ 9.4.2 Quick wins segment(NEW):**

```markdown
## § 9.4.2 Quick Wins(low cost × high coverage gain)

| Action | Estimated impl | Coverage Δ% | Quick fix file:line |
|:---|:---:|:---:|:---|
| Add REQ-005 docstring tag in export.py:88 | 5 min | +5% | src/api/export.py:88 |
| Implement download button per templates/export.html:42 | 30 min | +3% | templates/export.html:42 |
| Tag REQ-099 in newly-added payment.py | 2 min | +2% | src/api/payment.py:1 |
```

**Selection algorithm:** quick-win = `effective_cost ≤ 1.0` AND `coverage_delta_% ≥ 2`;sort by `coverage_delta / impl_effort` desc。

**§ 9.4.3 Trendline section(NEW):**

```markdown
## § 9.4.3 Trendline(本輪 vs 上輪)

| Metric | Last round(rev N-1)| This round(rev N)| Δ |
|:---|:---:|:---:|:---:|
| R2 Req Coverage(scoped)| 92% | 96.6% | +4.6 ✅ |
| R3 Func Compliance | 88% | 91.3% | +3.3 ✅ |
| R4 Design Compliance | 70% | 74.2% | +4.2 ✅ |
| R5 Arch Violation count | 3 | 1 | -2 ✅ |
| R5 Memory Rule Violation | 0 | 0 | 0 |
| Unspec'd entry-point | 4 | 2 | -2 ✅ |
| Top-10 violation total effective cost | 32.5 | 18.7 | -13.8 ✅ |
```

**Trendline source(rev 0.2.1 C4 closure — markdown grep 改 structured sidecar):**
- 每輪 SCR report 存 `docs/reviews/<date>-scr-<target>.md`(markdown,human-friendly)
- **同 commit 並寫 `docs/reviews/<date>-scr-<target>.metrics.json` sidecar**(structured YAML 內含 frontmatter 之 `metrics:` block 全 metric 數值 + spec_pins fingerprint)
- 對齊 `[[backend-lint-workflow]]` baseline pattern(lint baseline file 之 structured data layer 分離 human-readable report)
- Trendline 計算 grep `*.metrics.json` sidecar — JSON schema 對齊 enhanced-v1 spec_version 鎖定,markdown body 改 不影響 trendline parse
- spec_pins fingerprint 對齊 § 8.3 drift detection;若 spec_pin drift detected,trendline 自動 emit「prior baseline different spec version」 warning

**§ 9.4.4 Compliance Coverage Matrix(rev 0.1.1 § 9.3 inherit + rev 0.2 enhance):**

對齊 PoC § 12 — 加 scoped vs full-spec 雙視角 enable bi-dir traceability rich view:

```markdown
## § 9.4.4 Compliance Coverage Matrix(scoped vs full-spec dual view)

### Scoped(SG gate base — REQ-XXX declared via § 8.4)
| Direction | Total | Found | Gap | Coverage |
|:---|:---:|:---:|:---:|:---:|
| Spec → Code | <N> AC | <X> impl + <Y> partial | <Z> missing | <%> |
| Code → Spec | <N> entry-point | <X> tagged | <Y> unspec'd | <%> |

### Full-spec(reference only — 不參與 SG gate)
| Direction | Total | Found | Gap | Coverage |
|:---|:---:|:---:|:---:|:---:|
| Spec → Code | <N> AC | <X> impl + <Y> partial | <Z> missing | <%> |
| Code → Spec | <N> entry-point | <X> tagged | <Y> unspec'd | <%> |
```

### § 9.5 3-Role Output Format(rev 0.2.4 NEW — per PO 2026-06-30 real-try insight)

**PO directive:** 「這樣的輸出連developer 都很難看懂， 我們來 完善輸出這一塊 讓 QA/PM/RD 都看得懂 PM 可以根據資訊決定project 是否進入下一關 注意PM 不是技術人員」

**Real-try evidence:** 2026-06-30 first PROD V7 invocation 之 output(docs/reviews/2026-06-30-scr-sanity-tc-scripts-coverage.md)— heavy YAML frontmatter + § 1 Mental Lens / § 2 R0-R6 / SG matrix 等 jargon-heavy structure → PM 看不到「能不能 ship」核心決策 information。

**Principle:** SCR output 必對齊 `[[human-first-docs]]` 3-role(👔 PM / 🔬 QA / 💻 Developer)perspective discipline — plain prose 為主,technical detail 退到 Appendix。

**Output structure(per verbosity § 8.6 modulated):**

```markdown
1. 🎯 TL;DR(1-3 sentence ship verdict — PM 最先看到)
2. 👔 PM Lens(per § 9.6)
   - 風險摘要(plain prose)
   - 📋 規格 ↔ 實作對照表(coverage gap explicit per § 5.6)
   - 📈 趨勢比較(per § 9.6.2)
   - 🗓 Time-to-Ship Estimate(per § 9.6.3)
   - 🔁 Open vs Closed Findings(per § 9.6.4)
   - 🎯 Effort vs Value Matrix(per § 9.6.5)
3. 🔬 QA Lens(per § 9.7)
   - 測試對齊狀況
   - 測試 gap 明細(per missing/partial sub-AC)
   - 推薦測試重點
   - 品質信心度
4. 💻 Developer Lens(per § 9.8)
   - 具體 actionable fixes(file:line + command)
   - (full mode only)架構補完方向 — Tier 2 future
5. Appendix(全部 mode only — § 9.6-9.8 mode-aware skip)
   - § 1 Mental Lens 4 acts
   - § 2 R0-R6 per-reviewer findings
   - § 3 Top 10 findings + Effective Cost Matrix
   - § 4 Critical Hotspots
   - § 5 SG Gate Decision matrix(9 dimensions)
   - § 6 Verdict + Next Round Focus
```

**Plain language standards(對齊 `[[human-first-docs]]`):**

| Anti-pattern(舊 output)| New 標準 |
|:---|:---|
| 「R0-R6 7-reviewer」 | 「7 個檢查維度」 |
| 「fallback (3b) low confidence」 | 「Scope 是自動推斷,信心度中等」 |
| 「memory rule invariant」 | 「治理規則」 |
| 「PASS WITH WARNINGS」 | 「✅ 可以 ship,有 N 個小提醒」 |
| 「coverage 78% AC-weighted」 | 「規格涵蓋率 78%(超過 MVP 標準 70%)」 |
| 「§ 1 Mental Lens」 | (omit in PM-facing OR rename「審查思路」 in appendix)|

**Visual indicators standard:** ✅ pass / ⚠ warning / 🔴 blocker / ⏸ pending / 🟢 low risk / 🟡 medium risk

### § 9.6 PM Lens 👔 Enhancements(rev 0.2.4 NEW)

**Tier 1 Add-ons(must-add per real-try feedback):**

#### § 9.6.1 規格 ↔ 實作對照表(coverage gap explicit)

對齊 § 5.6 Coverage Gap Explicit Enumeration。 PM-facing output 必含 4 sub-section:

1. ✅ 完整實作 REQ list(complete 之 REQ — per § 5.6 status=complete)
2. 🟡 部分實作 REQ list with sub-AC detail(partial)
3. 🔴 未做 REQ list with ship blocker reason(missing)
4. ⚪ Out-of-scope REQ list 明示 不算缺漏(prevent PM 誤解)

#### § 9.6.2 趨勢比較(Trend)— per real-try Tier 1 #1

**Purpose:** PM 需知道專案進步 vs 退步 trajectory。

**Data source:** Grep prior `*.metrics.json` sidecars(per § 9.4.3 C4 closure)— SCR run history。

**Output format:**

```markdown
### 📈 趨勢:這次 vs 上次 SCR(<prior-date>)

| Metric | 上次 | 這次 | Δ | 解讀 |
|:---|:---:|:---:|:---:|:---|
| 涵蓋率(scoped) | X% | Y% | +/-Δ | PM-friendly 1-line interpretation |
| Memory rule 違反 | N | M | +/-Δ | ... |
| Lint baseline | N | M | +/-Δ | ... |
| 涵蓋的 REQ 數 | N | M | +/-Δ | ... |
| Multi-file impl REQ | N | M | +/-Δ | ... |
```

**Trend grep algorithm:**
1. List `docs/reviews/*.metrics.json` 之 prior runs for same target slug
2. Pick latest prior run as comparison baseline
3. Compute Δ per metric
4. Generate PM-friendly 1-line interpretation per Δ direction(positive/negative/neutral)

#### § 9.6.3 Time-to-Ship Estimate — per real-try Tier 1 #2

**Purpose:** PM 需具體工時數 plan release timeline。

**Algorithm:**
- Per finding 估計 fix effort(from finding metadata field `estimated_effort_minutes`)
- Group by ship path:
  - ✅ MVP-ready(must-fix BLOCKER + 必補 SOFT FAIL)
  - 🟡 GA-ready(must-fix + recommend polish CONCERN)
  - 🌟 Production-perfect(must-fix + recommend + nice-to-have NIT)

**Output format:**

```markdown
### 🗓 距離可 ship 還要多久?

| Ship path | 內容 | 預估工時 | 累計 |
|:---|:---|:---:|:---:|
| ⚡ MVP 立即可 ship | <必補 list> | X min | X min |
| 🎯 GA-ready | + <推薦 polish list> | Y hr | X + Y |
| 🌟 Production-perfect | + <nice-to-have> | Z hr | X + Y + Z |

**PM 行動建議:** <choose path>
```

#### § 9.6.4 Open vs Closed Findings History — per real-try Tier 1 #4

**Purpose:** PM 需 trend findings 累積,防止技術債 silent grow。

**Data source:** Grep prior SCR review markdown reports 之 findings sections + match by file:line + description fuzzy match。

**Output format:**

```markdown
### 🔁 Findings 累積狀況

| Findings 來源 | 開出時間 | 狀態 | 備註 |
|:---|:---:|:---|:---|
| <prior-run-date> V-N | YYYY-MM-DD | ✅ closed / 🟡 deferred / 🔴 still open | <closure commit hash> |
| ... | ... | ... | ... |
| 本輪 V-N | <today> | 🔴 newly opened | ... |

**累積摘要:** N findings 總計,M closed,K deferred,L still open
**PM 解讀:** <plain prose interpretation>(eg. 「同一 REQ-024 B+C 連續 2 次 SCR flag → 不能再 defer,需 prioritize」)
```

#### § 9.6.5 Effort vs Value Matrix — per real-try Tier 1 #5

**Purpose:** PM 需 quick prioritization tool。

**Visualization(ASCII 4-quadrant chart):**

```markdown
### 🎯 補完任務 Effort vs Value

```
Value
  High │  <bullet 4>             <bullet 1>  ← 🌟 do next
       │  (低 effort, 高 value)   (高 effort, 高 value)
       │
   Low │  <bullet 3>             <bullet 2>  ← 🟢 quick win  /  🟡 do later
       │  (低 effort, 低 value)   (高 effort, 低 value)
       │
       └──────────────────────────────────────
       Low                 Effort                High
```

**Top 3 高 ROI 推薦:**
1. <highest ROI task — value/effort 比值最高>
2. ...
3. ...
```

#### § 9.6.6 Stakeholder Communication Template — per real-try Tier 2 #7(future cascade)

Auto-generate user-facing release note draft per finding aggregation。**Tier 2 — defer rev 0.3 cycle**(對齊 § 14.4.2)。

### § 9.7 QA Lens 🔬 Enhancements(rev 0.2.4 NEW)

**Tier 1 Add-ons:**

#### § 9.7.1 測試對齊狀況

**Output format:**

```markdown
### 🟢 已有測試對齊(直接放行)
- <REQ-X full coverage notes>

### 🟡 測試 gap(需要新增 test case)

**REQ-Y sub-X — N 個 sub-test 缺:**
- [ ] Test: <specific test case description>
- [ ] Test: ...
```

#### § 9.7.2 推薦測試重點

Top N prioritized test focus area per critical-path + complex-sub-AC:

```markdown
### 🎯 推薦測試重點
1. <area 1 — rationale>
2. <area 2 — rationale>
3. <area 3 — rationale>
```

#### § 9.7.3 品質信心度

Per maturity-aware threshold + sub-AC coverage:

```markdown
### 📊 QA 品質信心

| Level | Now | After 補完上面 |
|:---|:---:|:---:|
| Unit test coverage | X% | Y% |
| Cross-script coverage | X% | Y% |
| Spec → test traceability | X/N | Y/N |

**Verdict:** 適合 <internal testing / GA-ready / production>
```

#### § 9.7.4 Critical Path Analysis — per real-try Tier 2 #6(future cascade)

Blast radius / downstream impact analysis。**Tier 2 — defer rev 0.3 cycle**。

### § 9.8 Developer Lens 💻 Enhancements(rev 0.2.4 NEW)

**Tier 1 Add-ons:**

#### § 9.8.1 具體 actionable fixes

```markdown
### 🟡 Fix N(<tier>,<estimated effort>)
- 檔案:<file>:<line>
- 問題:<1-line description>
- 命令:<exact command to run>
- 接受標準:<verification criteria>
- 影響:<behavior impact>
```

#### § 9.8.2 架構補完方向 — per real-try Tier 2 #8(future cascade)

LLM-driven architectural suggestions(分新 module / extract utility / refactor pattern)。 **Tier 2 — defer rev 0.3 cycle**。

#### § 9.8.3 (Full mode only)Appendix — R0-R6 detail + SG matrix + Mental Lens

In `--full` verbosity mode,既有 enhanced-v1 5-section schema + § 9.2 SG Gate + § 7-8 SCR-specific 移至 Appendix。 對齊 `--brief` default skip principle。

---

## § 10. Integration with Orchestrator Phase 4.5

### § 10.1 Position in 5-tool stack

> ⚠ **Prerequisite(rev 0.1.1 Round 1-patch C3):** 本 5-tool stack 整合方案需 orchestrator proposal rev 0.1.1 → 0.1.2 amendment 加 4.5b SCR slot;本 SCR Stage 7 SKILL.md 落地之前置 condition,須優先 ship orchestrator rev 0.1.2 cascade(對齊 § 12 Stage 7 mandatory pre-step)。
> 截至 rev 0.1.1,orchestrator Phase 4.5 acceptance criteria 僅 codify spectra-review;SCR slot 為 forward-looking design,尚未在 orchestrator spec 中 codify。

對齊 orchestrator proposal rev 0.1.1 Phase 4.5 multi-tool stack(forward-looking — 待 0.1.2 落實):

```
Phase 4.5 Impl-Review(orchestrator host):
  4.5a spectra-review     → spec 內部 quality / drift
  4.5b SCR(本 proposal,NEW V7)→ code ↔ spec compliance
  4.5c ruff / mypy         → type / lint
  4.5d pytest              → behavior
  4.5e smoke test          → runtime / UI

Acceptance criteria(orchestrator gate Phase 4.5 → Phase 5):
  ALL 5 pass → ✅ Phase 5 release note
  4.5b SG fail BLOCKER → 🔴 hard block + return to Phase 4 code revision
  4.5b SG fail CONCERN → ⚠ soft block + PO override path(對齊 § 7)
```

### § 10.2 SCR 不 replace spectra-review

兩者 review 不同對象,並列共存:
- **4.5a spectra-review** target = spec text → 抓 spec internal drift
- **4.5b SCR** target = code(以 spec 為 ruler)→ 抓 code-spec compliance

PR review 時 PO 可同時讀兩 report(`docs/reviews/<date>-spectra-*.md` + `docs/reviews/<date>-scr-*.md`)。

---

## § 11. Impact Analysis

### § 11.1 對 既有 8-phase orchestrator

- **Phase 4.5 acceptance criteria 更新:** rev 0.1.1 → 0.1.2 加 4.5b SCR mandatory(MVP=optional / GA+=mandatory)
- **state.md schema 擴展:** 加 `project_maturity` field(影響所有現存 project 之 state.md 須 backfill)
- **decision-log.md schema 擴展:** 加 D-scr-bypass-* prefix convention

### § 11.2 對 既有 spectra-review SKILL.md

- 無直接修改 — SCR inherit § 1-5,不 fork spectra
- 但建議 spectra SKILL.md § Cross-SKILL Integration 加 SCR pointer

### § 11.3 對 既有 ai-principles.md

- §3 Mode Map 加 V7 entry(reference 本 spec)
- §9 Skill triggers 加 `/scr` invocation

### § 11.4 對 既有 *.py / *.js / *.html source

- **0 source change** — SCR 是 read-only review tool
- 但 future enforcement 階段需 REQ-tag 規約(Tier 2 詳)

### § 11.5 對 既有 release note convention

- `docs/release/changes/_template.md` 加 `sg_bypass:` optional field

### § 11.6 對 既有 memory rules

- 0 修改 — SCR 嵌入既有 13 條 invariant
- 但建議新增 `[[scr-bypass-audit-trail]]` memory rule 記 bypass 紀律

---

## § 12. Rollout Phases(Stage 0-7,對齊 orchestrator)

| Stage | Action | Acceptance | Reversible? |
|:---|:---|:---|:---|
| **0** | PO confirm Option C + Tier 1 + propose-first(✅ done 2026-06-29 ~18:05)| PO 簽核 | yes |
| **0.5(NEW rev 0.1.1;rev 0.2 N9 closure 細化為 3 sub-step)** | state.md `project_maturity` field backfill — Stage 0.5a filesystem scan / Stage 0.5b backfill existing / Stage 0.5c propose create-or-skip missing | 6 existing state.md backfill `project_maturity` + PO sign-off + ≥ 2 missing state.md 之 create-or-skip decision | yes |
| **1** | 寫 rev 0.1(本 spec)| Tier 1 6 items 全 codify | ✅ done 2026-06-29 |
| **2** | Round 1 spectra-review on rev 0.1 | review log file 產生 + verdict | ✅ done 2026-06-29(verdict fix-blockers)|
| **3** | PO Round 1-patch decisions → rev 0.1.1 | 0 BLOCKER outstanding | ✅ done 2026-06-29 |
| **4** | Round 2 spectra-review verify(若 0.1.1)| ship-as-is verdict | ✅ done 2026-06-29(verdict ship-as-is)|
| **5** | PoC manual SCR run — baseline scope `scripts/sanity_tc_pre_flight_check.py` + `sanity_tc_validate.py` ~370 LOC vs sanity-check req spec rev 1.32.1 | PoC report + feedback to rev 0.2 | ✅ done 2026-06-29(commit 2432c7b;scoped SG PASS 8/8 / full-spec SG fail R2)|
| **6** | rev 0.2 incorporate Tier 2(5 items)+ N4-N5 R1-patch defer + N7-N10 R2 defer + ⭐ spec scope declaration mechanism(PoC blocker)+ § 6.2.1 校正 + V-005/V-006 defer NITs | rev 0.2 spec 落地 + Round 1 spectra-review | ⏳ in progress 2026-06-29 |
| **6.5(NEW rev 0.2)** | rev 0.2 Round 1 spectra-review + iterate to 0.2.x ship-as-is | review log + verdict ship-as-is | pending |
| **6.7(NEW rev 0.2)** | Stage 5b — second PoC dogfood on different scope target(eg. orchestrator proposal vs spec OR pm-skill SKILL.md vs spec)to verify SCR cross-project portability | second PoC report + 2 finding for cross-project validation | pending |
| **7** | SCR SKILL.md 落地 + orchestrator Phase 4.5b integrate(對齊 § 10.1 prerequisite — 先 ship orchestrator rev 0.1.2 加 4.5b SCR slot)| `~/.claude/skills/spec-compliance-review/SKILL.md` 存在 + orchestrator rev 0.1.2 已 ship + per-stack adapter(§ 4.10)Python adapter 落地 | yes — skill 可 disable |

**Sequential gating:** 每 Stage Round 2 verify 後才進下一 Stage(對齊 D-004 of orchestrator decision log 之 sequential rollout 紀律)。

---

## § 13. Acceptance Criteria

> Requirement anchor: REQ-009(inviolable criteria:no auto-apply / *.py propose-first);REQ-006(inviolable:memory rule 不可違反)

### Per-stage criteria

- **Stage 1**(本 rev): § 1-16 全填 + Tier 1 6 items 皆有 § / sub-§ codify
- **Stage 2**: spectra-review log frontmatter `verdict` 之一(ship-as-is / fix-blockers / revise-design)
- **Stage 5 PoC**: SCR manual run output 2 file:
  - `docs/reviews/2026-06-XX-scr-poc-sanity-tc-impl-L1-L2.md`(SCR report)
  - 4 evidence:R2 coverage % / R3 functional pass / R5 violations / R6 lint baseline
- **Stage 7**: SKILL.md test invocation 對 1 個 known-good codebase return ✅ PASS

### Inviolable criteria

- 任何 Stage 不可違反 § 2 之 13 條 memory rule
- 任何 Stage 不可 auto-apply fix(對齊 `[[backend-change-rule]]`)
- 任何 *.py source change 必 propose-first(對齊 `[[backend-change-rule]]`)

---

## § 14. Open Questions

### § 14.1 Tier 2 deferrals(rev 0.2 已解 — closure entries)

| OQ-ID | Question | rev 0.2 closure |
|:---|:---|:---|
| OQ-T2-1 | Detection algorithm L1-L5 tier per reviewer 細部分配 | ✅ § 5.5 5-tier matrix + per-reviewer assignment table |
| OQ-T2-2 | Cost-staged tier light/medium/heavy 之 LOC 邊界值 | ✅ § 4.9 4-tier matrix(< 50 / 50-300 / > 300 / force-full)+ auto-pick algorithm |
| OQ-T2-3 | Bi-dir trace anchor scope — entry-point / service / helper free-pass 細節 | ✅ § 5.4 8-row anchor matrix + REQ-tag form per stack |
| OQ-T2-4 | Compliance Report top-10 violation / quick-wins / trendline sections | ✅ § 9.4 4 sub-section(top-10 / quick-wins / trendline / coverage matrix dual view)|
| OQ-T2-5 | Per-stack adapter — Python ast / JS esprima / HTML lxml 對接 | ✅ § 4.10 adapter API contract + 5 stack registry + fallback chain |

### § 14.2 Tier 3 deferrals(future PoC evidence-based;rev 0.2 持續 defer 至 Stage 5b/c PoC)

| OQ-ID | Question | Evidence trigger |
|:---|:---|:---|
| OQ-T3-1 | Per-violation confidence score + self-test corpus | Stage 5b 第二輪 PoC if FP rate measurable |
| OQ-T3-2 | SCR ↔ test gen integration loop | Stage 7 落地後 + test gen tool 評估 |
| OQ-T3-3 | Multi-repo / cross-service SCR | microservice 出現後 |
| OQ-T3-4 | Self-failure handling / FP escape hatch | Stage 5b PoC if 觸發 |

### § 14.3 Tier 1 pending(rev 0.1.1 內未拍板 — rev 0.2 仍 pending)

| OQ-ID | Question | Resolution by | rev 0.2 update |
|:---|:---|:---|:---|
| OQ-T1-1 | SCR skill 命名(`/spec-compliance-review` vs `/scr` vs `/v7-scr`)| ✅ **CLOSED rev 0.2.3 per PO 2026-06-30 directive 「spec-compliance-review,並在 v0~v6 裡擴充 v7 內部執行呼叫 spec-compliance-review」**:**Dual-name pattern**:V7 = operating mode(對齊 V3 / V5 mode-tool pair precedent)+ `/spec-compliance-review` = concrete skill;V7 mode internally invokes skill;user 可二選一直接 invoke skill 或經 V7 mode dispatch(對齊 V3 + `/spectra-review` user choice pattern)。**Implementation deferred:**(1)`~/.claude/skills/spec-compliance-review/SKILL.md` 寫作(Stage 7)(2)`ai-principles.md` §3 Mode Map 加 V7 entry(Stage 7 propose-first per `[[backend-change-rule]]` L1 protection)| ✅ N5 + dual-name closure rev 0.2.3 |
| OQ-T1-2 | 1-layer spec project R0 是否強制 vs 降級 syntax-only | ✅ rev 0.1.1 § 4.1 R0-lite mode 已解 | superseded |
| OQ-T1-3 | RG/FG/DG/IG/TG/ReG 6 gate 是否 Stage 7 後續 codify | future round | unchanged |
| OQ-T1-4 | SG-Bypass 是否需 PO 親自簽核 vs Claude 自主判斷 | Stage 5b PoC dogfood — rev 0.2 § 7.4 N10 enforcement mechanism 已 codify dual path | partial closure |
| OQ-T1-5 | Maturity threshold 邊界值(70/95/100)是否 final | Stage 5b PoC calibration | unchanged(Stage 5 PoC 用 MVP=70% verify but small sample size — Stage 5b further validate)|

### § 14.4 Tier 2 pending(rev 0.2 內新發現 OQ)

| OQ-ID | Question | Resolution by |
|:---|:---|:---|
| OQ-T2-6(NEW)| `scr_scope` declaration 之 metadata 真實 source 取得(PR description vs commit footer vs auto-detect grep)優先序是否 final | Stage 5b PoC 試 3 source |
| OQ-T2-7(NEW)| L4 LLM cost budget cap 100 calls 是否足夠 — Stage 5b PoC measure real call count | Stage 5b PoC |
| OQ-T2-8(NEW)| Per-stack adapter Python ast 是否須 deeper integration with `[[backend-lint-workflow]]` ruff + mypy chain | Stage 7 impl |
| OQ-T2-9(NEW)| Stage 5b PoC target — orchestrator proposal vs pm-skill SKILL.md 哪個 priority | PO sign-off |
| OQ-T2-10(rev 0.2.4 NEW)| § 9.6.6 Stakeholder Communication Template auto-gen algorithm(template engine + per-REQ description from spec)| rev 0.3 cycle |
| OQ-T2-11(rev 0.2.4 NEW)| § 9.7.4 Critical Path Analysis(blast radius / downstream impact)algorithm | rev 0.3 cycle |
| OQ-T2-12(rev 0.2.4 NEW)| § 9.8.2 Architectural Refinement Direction(LLM-driven suggestion logic — module split / utility extract / pattern refactor)| rev 0.3 cycle + LLM Q&A integration |
| OQ-T2-13(rev 0.2.4 NEW)| Business Priority per-REQ(`priority: P0/P1/P2` field in spec)— 需 sanity-check spec cascade dependency | depends on sanity-check spec amendment;PO sign-off needed |
| OQ-T2-14(rev 0.2.4 NEW)| NL → REQ-ID auto-mapping algorithm calibration(L2 regex + L3 embedding + L4 LLM confirm thresholds 校正)| Stage 7 落地後 first PROD usage measurement |
| OQ-T2-15(rev 0.2.4 NEW)| Verbosity default(per-project state.md `scr_default_verbosity:` field)— 是否強制 OR optional | Stage 7 落地後 user feedback |
| OQ-T3-5(rev 0.2.4 NEW)| Risk Indicators(security / legal / regulatory / performance — Tier 1 #9 from real-try)| Tier 3 — needs semantic LLM analysis + memory rule cross-check |
| OQ-T3-6(rev 0.2.4 NEW)| Confidence Intervals 量化(uncertainty propagation logic — Tier 1 #10 from real-try)| Tier 3 — needs statistical baseline |
| OQ-T2-16(rev 0.2.5 NEW)| § 8.7 popup threshold tuning(0.7/0.9 fine-tune per actual usage data)| rev 0.3 + Stage 7 落地後 first 30 invocation calibration |
| OQ-T2-17(rev 0.2.5 NEW)| § 8.7.2 state.md memory carry-forward for 「比較這次跟上次」 target — vs explicit ask | rev 0.3 + 待 prior-target schema decision |
| OQ-T2-18(rev 0.2.5 NEW)| § 8.8 discovery card example count + per-project customization(`v7_help_examples` opt-in)| rev 0.3 + Stage 7 落地後 audit log 提供 high-frequency phrasings 自動更新 |
| OQ-T2-19(rev 0.2.5 NEW)| § 8.8 dev `--advanced` flag list escape(讓 dev 仍可看 flag list)— ON / OFF / opt-in | rev 0.3 + dev cohort feedback |
| OQ-T2-20(rev 0.2.5 NEW)| § 8.9 chitchat reject scope + ambiguous SCR vs non-SCR fallback decision(popup vs reject)| rev 0.3 + Stage 7 first PROD reject log review |
| OQ-T2-21(rev 0.2.5 NEW)| § 8.10 heavy threshold per-project calibration(MVP project 「heavy」 vs mature project 不同)| rev 0.3 + state.md `v7_heavy_threshold:` override |
| OQ-T2-22(rev 0.2.5 NEW)| § 8.10 state.md cost calibration rolling cap N(default 20 vs per-project tune)| rev 0.3 + actual storage growth measure |
| OQ-T2-23(rev 0.2.5 NEW)| § 8.11 Ctrl-C cross-OS impl(Linux/Mac/Windows signal handler 差異)| Stage 7 impl — Linux-first,Mac/Windows defer to user feedback |
| OQ-T2-24(rev 0.2.5 NEW)| § 8.12 reject phrase log location unification — state.md `v7_rejected_phrases:` vs metrics.json `rejected_resolution` | rev 0.3 + first 90-day audit log usage pattern |
| OQ-T2-25(rev 0.2.5 NEW)| § 8.12 raw phrase privacy(PII / file path / project name mask before log)| rev 0.3 + 對 GitHub public repo 之 audit log compliance check |
| OQ-T2-26(rev 0.2.5 NEW)| § 8.12 trend analysis timing — defer rev 0.4+(audit log 累積)vs rev 0.3 同 SKILL.md v0.3 一起 | rev 0.3 cycle decision |

> **N8 closure(rev 0.2.6):** 上 11 個 OQ 為 rev 0.2.5 walkthrough 18 OQs 之 7 個 closed-by-patch(B1 / N4 / C2 covering Focus Lens 設計接受 / N5 / N6)後剩餘 11 個 — 進 § 14.4 編號軌道。

### § 14.5 PoC findings carry-forward(rev 0.2 NEW)

| Item | Status |
|:---|:---|
| V-001 REQ-019 frontmatter under-checked(pre_flight_check.py:274)| → propose-first round to sanity-check rev cascade(非 SCR critical path) |
| V-002 REQ-024 F docstring sig drift(spec-side fix)| → propose-first round to sanity-check rev cascade(非 SCR critical path) |
| V-003 REQ-024 B 5 content invariants 未 enforce | scope-out per rev 1.31 L1+L2 intent;future round |
| V-004 REQ-024 C 4 semantic invariants 0% impl | scope-out per rev 1.31 L1+L2 intent;future round + 需 § 4.10 YAML parse adapter |
| V-005 § 4.1 R0 heading levels H2/H3 only check | ✅ rev 0.2 § 4.1 V-005 closure |
| V-006 docstring「REQ-025 B #10」應 cite REQ-024 A | **歸屬(rev 0.2.1 N12 closure):** ✅ sanity-check **.py docstring 端 bug**(docstring 寫錯,非 spec 端寫錯;REQ-025 B 是 Claude prompt invariants 段,REQ-024 A 是 single-block invariant 段);→ propose-first round to `scripts/sanity_tc_pre_flight_check.py:210` docstring 修正(非 SCR critical path)|

---

## § 15. Glossary

| Term | Definition |
|:---|:---|
| SCR | Specification Compliance Reviewer(本 proposal V7 mode)|
| SG | Specification Gate(SCR 必過之 Phase 4.5 → 5 gate)|
| RG/FG/DG/IG/TG/ReG | Req Gate / Func Gate / Design Gate / Impl Gate / Test Gate / Release Gate(PO Turn 1 提及 7-gate pipeline,本 rev 只 codify SG)|
| Coverage % | Acceptance-criteria base unit 之 spec → code 對齊度量化 |
| Bi-dir traceability | Spec → code missing impl + code → spec unspec'd 雙向 gap detection |
| Maturity-aware threshold | SG threshold 依 project_maturity(MVP/GA/mature)切換 |
| SG-Bypass token | Emergency escape valve(對齊 `[[sanity-check-bug-fix-direct-main-rule]]`)|
| Spec Version Pin | SCR report frontmatter 凍結 spec rev + hash(防 drift)|
| AC | Acceptance Criteria — coverage % base unit |
| Memory-bound invariant | § 2 enumerate 之 13 條 inviolable memory rule |

---

## § 16. Revision History

| Rev | Date | Author | Change |
|:---|:---|:---|:---|
| 0.1 | 2026-06-29 | PO + Claude | Initial draft — Tier 1 only(6 items)+ § 1.1 5-turn fidelity capture |
| 0.1.1 | 2026-06-29 | PO + Claude | Round 1-patch close 9/11 + Round 2 ship-as-is — B1 + C1-C4 + N1-N3 + N6;defer N4 + N5;commit 40f42c5 |
| 0.2 | 2026-06-29 | PO + Claude | Tier 2 incorporation + R1/R2 defer carryovers + Stage 5 PoC findings — 15 item single rev cascade(commit ebeef87);Round 1 verdict fix-blockers(1 BLOCKER B1 + 4 CONCERN + 12 NIT)|
| 0.2.1 | 2026-06-29 | PO + Claude | Round 1-patch on rev 0.2 — B1 OPT-A closure § 8.4 fallback (4) PENDING verdict + C1-C4 + 6 cheap NIT(N1-N4 + N6 + N12);defer 6 NIT(N5+N7-N11)to rev 0.3 cycle(commit bcff00e);Round 2 verdict fix-concerns(2 NEW C5+C6 + 6 NEW N13-N18)|
| 0.2.2 | 2026-06-29 | PO + Claude | Round 2-patch on rev 0.2.1 — close C5 PENDING enum + C6 sequential 4-step + Round 3 ship-as-is(commit 622ee50);defer 6 NIT(N13-N18)to rev 0.3 cycle |
| 0.2.3 | 2026-06-30 | PO + Claude | OQ-T1-1 closure dual-name design — V7 mode + `/spec-compliance-review` skill mode-skill pair contract codified;commit 8e34de3 |
| 0.2.4 | 2026-06-30 | PO + Claude | Real-try driven output redesign per 4 PO directives at first PROD V7 invocation —(1) § 9.5 3-Role Output Format(👔/🔬/💻)(2) § 5.6 Coverage Gap Explicit Enumeration(3) § 8.5 REQ-ID + NL Targeting(4) § 8.6 Verbosity Parameter;+ § 9.6/9.7/9.8 PM/QA/Dev Lens enhancements;+ § 14.4 OQ-T2-10~T2-15 defer items。 Effort: ~1.5 hr。 Per `[[backend-change-rule]]`: 0 *.py / 0 SQL change(spec cascade only)。 |
| 0.2.5 | 2026-06-30 | PO + Claude | NL UX bundle per PO 2026-06-30 directive — § 8.7 NL Invocation & Popup Disambiguation(4-slot intent + Focus Lens NEW)+ § 8.8 Help Discovery + § 8.9 Negative Scope Reject + § 8.10 Cost + Time Preview + § 8.11 Escape Route + § 8.12 NL Intent Audit Trail。 6 NEW sub-sections additive。 Effort: ~1.5 hr。 |
| **0.2.6** | **2026-06-30** | **PO + Claude** | **Round 1-patch on rev 0.2.5 per PO directive 「Y go 0.2.5-patch1 全 12 items」 — Round 1 spectra-review verdict ⚠ fix-blockers closure(commit pending):** **B1 closed**(Option A silent escape)— § 8.11 Level 1 維持「0 audit log entry」 + § 8.12 status enum 移除 `cancelled_popup`(5 states → 4 states);**C1 closed** — § 8.7 加 「Relationship to § 8.5 既有 NL→REQ algorithm」 SSOT delineation(single-slot 進 § 8.5;multi-slot 進 § 8.7);**C2 closed** — § 8.7.3 加 「Interaction with § 8.6 verbosity」 2-dim filter resolution(Focus Lens 先過濾 / Verbosity 再裁切 / 衝突解 / `all` fallback / brief × blockers_only narrow combination);**C3 closed** — § 8.10 actual_cost 明 SSOT 2 places(metrics.json per-invocation + state.md rolling N=20 + § 7.3 SG-Bypass 獨立 sink);**C4 closed** — § 8.5 加 「對齊 § 8.7 popup framework」 cross-ref(Ambiguous row 升級 multi-slot popup);**N2 closed** — § 8.5 NL command 統一不用 「」 quote;**N3 closed** — § 8.8 「5-8 個 use case」 改 「4-5 群 use case 各 1-2 example total 8-10 phrasings」;**N4 closed** — § 8.10 「5 秒內按 Esc」 改 「跑到一半可 Ctrl-C」 對齊 § 8.11 L3 reality;**N5 closed** — § 8.7.2 decay clock 明示 `last_used` reference + `decay_count = floor((now - last_used) / 30 days)` formula + timezone override;**N6 closed** — § 8.11 atomic tmp 明示 `<output_dir>/.scr-tmp-<timestamp>-<rand-6>.{json,md}` 隨機後綴 + PID-bound cleanup;**N8 closed** — § 14.4 加 OQ-T2-16 ~ T2-26 11 個 walkthrough OQ(其餘 7 個由本 patch 直接 close);**N9 closed** — § 8.12 schema 加 `format_version: "scr-rev-0.2.6-nl-v1"` 防 forward-incompat。 **Defer rev 0.3 cycle:** N1 § 8 heading 「Spec Version Pin / Fingerprint」 rename / 拆 § 8B / N7 chitchat reject scope 模糊 / N10 collapse markdown impl(`<details>` vs 1-line bullet decide at SKILL.md v0.3 phase)。 **Per `[[backend-change-rule]]`:** 0 *.py / 0 SQL change(spec cascade only)。 **Per `[[delete-dialog-no-undo-hint]]`:** silent escape per Option A 對齊 0 file change 無 「可還原」 措辭。 **Per `[[audit-patch-cascade-verify]]` 5-dim:**(a)cross-file:本 spec + Round 1 review file(b)intra-file:5 cross-ref consistency check(C1/C2/C3/C4 all SSOT delineated)(c)commit-time:revision history row + decision log D-066(d)Round 2 spectra-review next-step(expected ship-as-is)(e)external state:Round 1 review verdict ⚠ fix-blockers cost matrix 2.7 hr / 26.75 hr defer / net 24.05 hr ROI realized。 **Per `[[incremental-rev-cascade]]`:** 12 cheap fix-now items 1 cohesive patch,3 NIT defer rev 0.3(per cost-staged discipline)。 **Effort:** ~1 hr spec patch + Round 1 spectra-review ~0.5 hr。 | |

---

> **Next step:** Round 2 spectra-review on rev 0.2.6(expected ship-as-is — patch closes all BLOCKER + CONCERN;NIT 3 defer rev 0.3 per [[incremental-rev-cascade]] discipline)。 Output 將存於 `docs/reviews/2026-06-30-spectra-scr-proposal-rev-0.2.6.md`。 後續:Round 2 ship-as-is verdict 後 → Track 2 SKILL.md v0.3 propose-first cascade(scope:~3 hr per SKILL 規模 + 對齊 spec 0.2.6 之 NL parser + popup contract + Focus Lens + 4-state audit + atomic tmp pattern)。
| 0.3.1 | 2026-07-02 | PO + Claude | 2026-07-02 OD-5 option A: added canonical ## Requirements section (13 discrete REQ-XXX with triad) + § cross-link anchors; schema_version → req-spec-v1.1. Content-preserving refactor (no existing prose deleted). |
| **0.3.0** | **2026-06-30** | **PO + Claude** | **rev 0.3 cycle bundle close — 4 NIT(N1/N7/N10/N11)per PO 「rev 0.3 cycle bundle(N1/N7/N10/N11)」 directive:** **N1 closed** — § 8 heading 「Spec Version Pin / Fingerprint」 → 「Invocation, Targeting & Spec Pinning」 + taxonomy table 解 section grew 4 → 13 sub-sections 之 readability 衝突。**N7 closed** — § 8.9 chitchat reject scope narrowed — pure chitchat row split 為 「pure greeting」(explicit reject)+ 「ambiguous status query」(走 § 8.7 popup;eg.「v7 怎樣?」 提示 ⓐ status query ⓑ chitchat ⓧ 我打錯)。**N10 closed** — § 8.7.3 collapse markdown 實作決定 1-line bullet ⭐(vs `<details>` HTML)— plain markdown portable per `[[human-first-docs]]`;native browser collapse 不適 multi-IDE rendering(Slack/Telegram 不支援)。**N11 closed** — NEW § 8.13 Invocation Lifecycle Numbered Flow Chart — 8-step canonical flow + step cross-reference matrix + status audit path map + SKILL.md impl alignment hint;consolidates § 8.7 + § 8.10 + § 8.11 + § 8.12 散在 4 section 之 sequence per Round 2 spectra-review finding(c81690b cost 1.5 → 0.3 fix-now per [[incremental-rev-cascade]])。 **Per `[[backend-change-rule]]`:** 0 *.py / 0 SQL change(spec cascade only,N7 popup 行為 update 留 SKILL.md cascade)。 **Per `[[delete-dialog-no-undo-hint]]`:** 全 additive(N7 narrow not remove;N10 chosen option;N11 NEW section)— 0 destructive。 **Per `[[human-first-docs]]`:** N10 explicit plain-markdown decision + N11 flow chart 對 SKILL impl reader 友善。 **Per `[[audit-patch-cascade-verify]]` 5-dim:**(a)cross-file:本 spec + decision log D-067 update + future SKILL.md cascade(b)intra-file:N1 heading + § 8.13 invocation lifecycle 對齊 § 8.7+8.10+8.11+8.12 cross-ref matrix(c)commit-time:此 commit(d)Round 1 spectra-review 不必要 — 4 NIT all cheap-fix-direct(e)external state:rev 0.2.6 Round 2 ship-as-is verdict(c81690b)+ N11 carry-forward。 **Per `[[incremental-rev-cascade]]`:** 4-NIT bundle 1 cohesive rev(non-mega-rev — 對齊 rev 0.2.4/0.2.5 bundle precedent)。 **Effort:** ~0.5 hr spec patch only。 | |
