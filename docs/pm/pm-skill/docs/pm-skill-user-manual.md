> **文件性質:** PM Skill 使用手冊(情境化引導 + 範例對話)
> **目標讀者:** PM / PO / Tech Lead / 工程師 — **第一次接觸 PM Skill 的人**
> **撰稿日期:** 2026-06-17
> **對齊版本:** PM Skill proposal rev 1.5(原 worktree timing 設計 — Phase 4 entry trigger)
> **預估閱讀:** 30-40 分鐘
> **怎麼讀:** 順著一個 project kick-off 的真實故事走,每個情境都對應一個你之後會用上的能力

> ⚠ **rev 1.17 amendment(2026-06-23)— Worktree lifecycle expanded:** 本手冊 scenario 5a「Phase 4 主開發 V2 start」描述的是 **rev ≤ 1.16 原 worktree timing**(Phase 4 entry trigger)。**從 proposal rev 1.17 起**,`/pm setup-worktree` trigger 已改成 **Phase 3 entry**(`/pm advance-phase 3` auto-trigger),Phase 3 shared infra + Phase 4 module dev 全 commit 到 `dev/<project>` worktree,Phase 5 才 merge 回 main。**Authoritative source:** [`docs/pm/pm-skill/spec/pm-skill-proposal.md`](../spec/pm-skill-proposal.md) §E.8.1 + §E.8.2。本手冊 scenario 全 update 排程到 user manual v1.9(等下次大改一起)。新 PM 看 manual 時,worktree 相關 timing 以 proposal §E.8 為準。

> ⚠ **rev 1.17.3 amendment(2026-06-23)— Worktree-Default Invariant + Mainline-as-Project:** 重大 architectural shift — mainline 變成 **reserved system project**(`docs/pm/mainline/state.md`),routing 全靠 `active-project.txt`。Emergency hotfix 不再需要 `--override-discipline` flag,改用 uniform model `/pm use mainline --reason "..."` 切到 mainline 操作再切回。**3-month grace period**(2026-06-23 → 2026-09-23)兩種 mechanism 並存,after 2026-09-23 只 mainline-switch works。新 commands:`/pm whereami`(read-only state display)。Mainline 不適用 8 個 commands(advance-phase / signoff / gate-check / setup-worktree / rollback / archive / restore / init mainline)。**Authoritative source:** proposal §E.8.8(10 sub-items)+ `docs/pm/mainline/state.md`。本手冊 scenario 全 update defer 到 user manual v1.9。新 PM 看 manual 時,mainline-as-project + worktree 相關 timing 以 proposal §E.8.8 為準。

> 📌 **rev 1.17.5 amendment(2026-06-23)— active-project.txt canonical path 對齊現實:** `active-project.txt` canonical 位置 = **`docs/pm/active-project.txt`**(top-level under `docs/pm/`)— NOT `docs/pm/_org/active-project.txt`。Pre-rev-1.17.5 spec/SKILL 寫法為 spec ↔ impl drift(reality 一直是 top-level)。rev 1.17.5 sed sweep 已 fix 5 LIVE files(16 refs):pm-skill SKILL.md / spectra-review SKILL.md / namecard-v2-ddd-guardian SKILL.md / QUICKSTART.md / .claude/commands/spectra-review.md。`_org/` namespace 保留 ORG-level shared(org-decision-log / org-roster / contract-pack / specs)— active-project.txt 不歸屬 ORG namespace。**Authoritative source:** proposal §E.8.8 📌 box + Revision History rev 1.17.5。



# PM Skill 使用手冊 — 從 Project Kick-off 開始

## 📖 前言:這份手冊怎麼讀

這份手冊**不是 command reference**(那部分在 §附錄 A 速查表),而是**用一個真實 project 的時間軸**,把 PM Skill 11 個核心使用情境串起來。

故事主角:
- **PO 王經理**(本手冊以 PO 視角為主)
- **Tech Lead 阿明**
- **工程師小華 / 小芬 / 阿凱**(3 個並行模組)
- **PM Skill**(我們的 AI 助理)
- **老闆 陳董**(每階段 sign-off + final review)

故事專案:**LINE 名片 V3 訂閱方案**(對齊既有 Phase 1.5 訂閱開發 — 已有 100+ 輪設計收斂 + 9 輪 spectra-review 的真實規格)。

> 📊 **時程估算 evidence basis(對齊 spectra Round 1 N2 fix):**
> 本手冊內所有「省 N 天 / 從 X 到 Y」的時程比較,**基準是訂閱專案 Phase 1.5 真實測量**:
> - Phase 0 規格收斂時間:9 輪 spectra-review 累積 ~20 小時(對齊 §6.4 自身 3 輪 review 結果)
> - 跨組衝突發現時點:訂閱專案多次 Phase 5 才爆 → 平均救火 3-7 天
> - daily standup 時間:既有團隊 4 人 standup 平均 30 分鐘/天
> 本手冊預估值為「PM Skill 上線後的目標值」,實際 ROI 須等試跑驗證(對齊 proposal §10.6 試跑計劃)。

> ⚠ **Auto Behavior Confidence Tier(對齊 spectra Round 3 C2 fix):**
> 本手冊內所有「**auto generate / auto detect / 自動 ...**」behavior **皆為 best-effort,並依以下三級 confidence 落地:**
>
> | Tier | Confidence | 範例 | Fallback |
> |:---:|:---:|:---|:---|
> | 🟢 high | ≥ 90% | 命令 parsing / functional.md status update / git log grep | 失敗時 PM Skill 主動 abort + 報具體錯誤 |
> | 🟡 medium | 60-90% | impact analysis / module-fit 推薦 / capacity 評估 / migration script generate | 失敗 / 結果 confidence 低 → SKILL 列出 evidence + 請 PO 拍板,**不強推結果** |
> | 🔴 low | < 60% | domain skill 評估 / cross-project common pattern / 客戶心理模型推測 | SKILL **拒絕產出結論**,僅列出 raw data 由人類判斷 |
>
> **預設規則:**所有場景 demo output 中的 auto-generate 內容皆預設 medium tier,失敗時 SKILL **退回 list of file paths + 建議手動處理**,不會 silent fail。對齊 §6.4.11 contract 預計補強 §K「PM Skill AI Behavior Confidence Tier」段落(Phase E 落地時鎖定)。

---

## 🎬 場景 0:啟用 PM Skill(只要做一次)

### 情境

王經理第一次用 PM Skill。她打開 terminal,在 repo 內。**從 rev 1.7 起 `/pm init` 必帶 project name** — 避免多 project 並行 path 衝突(對齊 PO Round 5 architectural fix)。

```bash
$ /pm init "namecard-v3-subscription"
```

### PM Skill 回應

```
🎉 歡迎使用 PM Skill v1.0

我會建立 multi-project safe 結構(per-project subfolder + org-level shared):

✅ Per-project 區(本次 init):
   docs/pm/namecard-v3-subscription/
   ├── state.md(current_phase=0)
   ├── team-roster.md(待填)
   ├── phase-gates.md(對齊 §6.3.2)
   ├── output-schemas.md(對齊 §A.5)
   ├── decision-log.md(append-only)
   └── reports/(daily / weekly / phase-end)
   
   docs/modules/namecard-v3-subscription/(空,等 Phase 1 V7 切割)
   docs/reviews/namecard-v3-subscription/(空,spectra-review 用)

✅ Org-level shared(若不存在則 auto-create,跨 project 共用):
   docs/pm/_org/
   ├── org-roster.md(全 org 工程師 + skill)
   ├── org-decision-log.md(cross-project decisions)
   ├── org-retrospectives/(跨 project lessons aggregation)
   └── contract-pack/(contract registry)
       ├── req-contract-v1.md
       ├── spectra-contract-v1.md
       └── ...(對齊 §6.4)

✅ Active project context 已設定:namecard-v3-subscription
   此 terminal session 後續所有 PM 命令預設對此 project
   (可隨時 /pm use "<other>" 切換,或 --project <X> flag 明示)

接下來建議:
  1. 填 docs/pm/namecard-v3-subscription/team-roster.md
  2. 跑 /pm start "namecard-v3-subscription" --from-verbal-brief 開始 Phase 0

💡 任何時候輸入 /pm help 看完整命令清單。
💡 多 project 並行?跑 /pm init "<another-project>" 建第 2 個(對齊場景 12)。
```

王經理試跑 `/pm help`:

```bash
$ /pm help
```

```
📚 PM Skill 命令清單(對齊 §6.4.11 §J.1 Naming Convention)

🚀 Lifecycle:
  /pm init "<project>"              啟用 PM Skill(per-project subfolder)
  /pm use "<project>"               切換 active project context(多 project 並行)
  /pm start "<project>" ...         Phase 0 啟動
  /pm status [--project <X>]        當前 Phase + state(預設 active project)
  /pm advance-phase <N>              進下個 phase(觸發該 phase SKILL)
  /pm signoff phase-N --approver <X> 階段簽核
  /pm gate-check <phase>             跑 phase acceptance criteria

📊 Reporting:
  /pm daily / weekly / health-check / kpi-eval

🔍 Validator:
  /pm validate-<phase-or-artifact> [--all]  詳見 §6.4.11 §J.1
  /pm validate-all                    跨 phase + lineage

🐛 Bug Review:
  /pm-bug-review <slug> [--finding X | --pending-only | --overrides-only]

詳細用例見:docs/pm/pm-skill/docs/pm-skill-user-manual.md
```

### 重點 takeaways

- ✅ PM Skill **不需要 server / 不需要安裝額外服務**,全 file-based
- ✅ 一個 PM Skill 服務全 project(可橫展)
- ✅ 主導權永遠在 PM 手上(state.md 是 SSOT)

---

## 🎬 場景 1:Phase 0 Project Kick-off — 老闆口頭需求 → Requirement Spec

### 情境

陳董找王經理:「下季要在訂閱方案加 4 個套餐層級,2 個月內上線。」 — 就這樣一句話。

王經理過去要花 2-3 天訪談 + 寫初稿 + 反覆對焦。現在她坐下打:

```bash
$ /pm start "namecard-v3-subscription" --from-verbal-brief
```

### PM Skill 回應

```
🎬 Phase 0 啟動 — Project Kick-off

我會幫你把模糊的口頭需求結構化成 Requirement Spec。

讓我問你幾個關鍵問題(我需要的最小資訊集):

Q1: 4 個套餐的名字 + 收費策略(免費 / 月費 / 按用量)?
Q2: 2 個月內上線 = 2026-06-17 + 2 月 = 2026-08-17 deadline?
Q3: 預算 / 範圍硬約束(eg. 不可動 V1 LIFF code / Azure Webapp Linux 3.0)?
Q4: 老闆是否確認過「驗證信箱手機 = 免費 tier 自動升等」這個機制?

(我會根據你的答案產初版 Requirement Spec 草稿,你 review 後再 spectra-review)
```

王經理 5 分鐘回答完 4 個問題。

### PM Skill 後續

```
✅ 收到。我正在做以下事:

1. 產 Requirement Spec 初版(rev .1)— 對齊 §6.4.10 Artifact Contract:
   - Frontmatter(spec_type=requirement / traceability hooks)
   - Glossary section(從 PO 答案抽 8 個術語:profile / bizcard / 主名片(main_bizcard)/ 推廣套餐 / 個人付費套餐 / 配額(quota)/ 配額單位(profile/personal_card/friend_card/push)/ 升降級 path)— 對齊 §6.4.10 §B.3 min 5,實際舒適區 ≥ 7
   - Out of Scope section(eg. 多帳號切換 → defer Phase 2.0)
   - Assumptions section(memory: profile_bizcard_invariant.md 已 active)
   - Constraints section(memory: backend_change_rule + v1_ui_retired + azure_webapp_runtime)
   - Requirements section(從你答案推導出 ~25 個 atomic REQ)

2. 對齊 working draft 模式(允許 TBD 標記未決事項,Phase 0 Exit 前清乾淨)

📄 草稿位置:docs/2026-06-17-namecard-v3-subscription-requirement.md (rev .1)
⏱  你需要 review:大約 15 分鐘
🔍 下一步建議:跑 /spectra-review <path> 找 issue
```

### 重點 takeaways

- ✅ Phase 0 **從 2-3 天縮到 1 小時**(15 min PO answer + 30 min Claude generate + 15 min PO review)
- ✅ Requirement Spec **強制對齊 §6.4.10 contract**(Glossary / OoS / Assumptions / Constraints 等)
- ✅ memory 自動 inject 為 Assumptions / Constraints(PO 不需重複輸入專案 invariant)

---

## 🎬 場景 2:spectra-review 找 issue + PO 拍板 + fix loop

### 情境

王經理跑:

```bash
$ /spectra-review docs/2026-06-17-namecard-v3-subscription-requirement.md
```

### PM Skill 回應(Round 1 review log,精簡顯示)

```
🔍 Spectra-Review Round 1 完成

🔴 BLOCKERS (1):
  B1. 推廣套餐 quota 與付費套餐 invariant 衝突(severity=8.5)
      → 推廣套餐 friend=50 vs 付費套餐 friend=30,違反「promo ≤ paid」原則
      → Fix: 統一 promo 套餐 quota ≤ paid

🟡 CONCERNS (3):
  C1. 沙龍店長 case study quota 數字 inconsistency
  C2. 退費策略未明示
  C3. 試用期延伸 vs 直接升級 path 衝突

🟢 NITS (4): 文案 polish / 用詞統一 / 排版

✅ STRENGTHS (5): 4-tier 模型清晰 / Glossary 完整 / ...

📊 Effective Cost Matrix:
  Fix all now: 1.4 vs Defer: 23.0(16x leverage)

📍 完整 review log:
  docs/reviews/namecard-v3-subscription/2026-06-17-spectra-requirement-round-1.md(對齊 Round 5 path fix)

🎯 建議:跑 /pm-bug-review 逐一拍板
```

### PO 拍板 (PM 命令)

```bash
$ /pm-bug-review namecard-v3-subscription-requirement --pending-only
```

PM Skill 一個一個 finding 引導 PO 拍板,每個 finding 顯示:
- spectra-review default(severity / fix difficulty / ROI / 推薦)
- PO 可 accept / override(改數字 + 寫 reason)/ defer / reject

```
─ B1: 推廣套餐 quota 與付費套餐 invariant 衝突 ───────
  spectra defaults:
    severity: 8.5
    fix_difficulty: 2.0
    fix_roi: 4.25
    推薦 Option B: 現在修
  
  PO 拍板?
    [a] accept default(同推薦)
    [b] override severity → 輸入新值 + reason
    [c] accept 但 fix path 不同(輸入新 fix description)
    [d] reject(REQ 設計就是要 promo > paid,需 PO 強簽)
    [e] defer
    [f] skip(留 no_decision)
  > a

  ✅ B1 accept。記錄到 docs/pm/namecard-v3-subscription/decision-log.md(對齊 Round 5 per-project path)。
  
─ C1: 沙龍 case study quota 數字 inconsistency ─────
  ...
```

5 分鐘走完所有 finding 拍板。

### Fix 後 Round 2

```bash
$ /spectra-review docs/2026-06-17-namecard-v3-subscription-requirement.md
```

```
🔍 Spectra-Review Round 2(post Round 1 fix verify)

✅ Round 1 8 個拍板 fix 全 applied,無新 BLOCKER / CONCERN
✅ Convergence rule(對齊 §6.4.10 §B.1):達 last 1 round 0 new BLOCKER

🟢 NITS (2): 文案微 polish(可選)
✅ STRENGTHS (5): 全保留

📊 Status: ⚠ 對齊 §6.4.10 standard scaling rounds_min=3,還差 1 輪
```

### Round 3 final

```bash
$ /spectra-review docs/2026-06-17-namecard-v3-subscription-requirement.md
```

```
🔍 Spectra-Review Round 3 — convergence 達標

✅ 0 BLOCKER / 0 CONCERN / 0 open NIT / 6 STRENGTH
✅ fix_rate: 100%
✅ Convergence: 連續 2 輪 0 BLOCKER + 0 new CONCERN

🎯 Verdict: ✅ ship-as-is(rev .4)

📍 Aggregate summary:
  docs/reviews/namecard-v3-subscription/_summary-requirement.md(對齊 Round 5 per-project path)
  - total_rounds: 3
  - 跨輪 fix 全收斂
  - 對齊 §6.4.10 Phase 0 Exit Bar 全部 quality bar ✅
```

### 重點 takeaways

- ✅ Round 1 自動列 finding + Effective Cost Matrix → PO 知道修哪些值得
- ✅ `/pm-bug-review` **5 分鐘走完所有拍板**(對比過去主觀討論半天)
- ✅ Round 2-3 自動 verify + convergence check,不靠人「我覺得 OK」
- ✅ 整個 Phase 0 從 **2-3 天 → 4-6 小時**

---

## 🎬 場景 3:Phase 0 Exit Gate-Check + Phase 1 進入

### 情境

王經理:「我覺得這份規格 ready 了。可以送老闆 sign-off + 進 Phase 1 嗎?」

```bash
$ /pm gate-check phase-0
```

### PM Skill 回應

```
🚪 Phase 0 Exit Gate-Check

跑全 7 條 §6.3.2 Phase 0 acceptance criteria + §6.4.10 全部 Quality Bar:

✅ 1. Requirement Spec 對齊 §6.4.10 Artifact Contract
   - /pm validate-req-spec 全 pass(對齊 §B.1-B.5)
✅ 2. spectra-review ≥ 3 rounds + 達 convergence
✅ 3. 0 BLOCKER / 0 CONCERN open
✅ 4. NITs open ≤ §C scaling cap(5,實際 0)
✅ 5. STRENGTHS ≥ §C scaling min(3,實際 6)
✅ 6. team-roster.md 完整(4 工程師專長已填)
✅ 7. state.md target_release_date / constraints 已填
✅ 8. phase-gates.md 7 階段允收標準範本 ready

⏸ 9. PM 簽核(state.md phase_0_signoff = true)
     → 需老闆 + PO 雙簽

🎯 Verdict: ✅ Ready for Phase 1 — 等 PM/老闆簽核即可

📍 簽核命令:
  $ /pm signoff phase-0 --approver PO  
  $ /pm signoff phase-0 --approver boss
```

兩個簽核後:

```bash
$ /pm advance-phase 1
```

```
🎬 Phase 0 → Phase 1 進入

✅ state.md current_phase = 1
✅ Phase 0 完整 audit trail 保留(decision-log + review logs + signoff record)
✅ Phase 1 entry conditions ready:
   - Requirement Spec (Phase 0 產出) ✅
   - team-roster.md ✅
   - phase-gates.md ✅
✅ V7 module splitter SKILL 自動啟動

下一步: V7 SKILL 會問你關於 module 切分的問題(等等會出現對話)。
```

### 重點 takeaways

- ✅ `/pm gate-check <phase>` **機械化跑全部 acceptance**,不靠人主觀
- ✅ 簽核需明示(PO + 老闆雙簽),**audit trail 完整**
- ✅ Phase 切換自動觸發下個 phase SKILL,**0 手動轉場**

---

## 🎬 場景 4:Phase 1 模組切割 — V7 SKILL 對話

### 情境

接續場景 3(剛跑完 `/pm advance-phase 1` → V7 SKILL 已自動啟動)。王經理跟 Tech Lead 阿明一起跟 V7 對話決定怎麼切模組。

(V7 SKILL 對話自動接續,無需額外命令 — 對齊 §6.4.11 §J.1 命名規約;`/pm advance-phase N` 即觸發該 phase 對應 SKILL)

PM Skill / V7 SKILL 對話:

```
🎬 Phase 1 — Module Splitting(V7 SKILL 主導)

我會幫你切模組。讀完 Requirement Spec 25 個 REQ 後,我有以下觀察:

📊 REQ 分布建議切 5 個 module(對齊 §6.4.11 §B.3 size cap 2-10):
  1. module-package-management (8 REQs)— 套餐定義 / 升降級
  2. module-quota-enforcement (6 REQs)— 配額查詢 / 扣減
  3. module-billing (4 REQs)— 收費 / 退費
  4. module-promo (3 REQs)— 推廣套餐機制
  5. module-shared-identity-binding (4 REQs)— 識別綁定(cross-cutting)

⚠ Cross-cutting REQ 偵測(對齊 §6.4.11 §B.2 cross_cutting_reqs):
  - REQ-010 「全 module 共用 error message format」
  - REQ-018 「全 module 共用 audit log scheme」
  → 我推薦:
    a) 共認 在 ≥ 2 module 的 cross_cutting_reqs(N:M)
    b) 或我幫你 split into 5 個 sub-REQ 各自 own
  > 選哪個?
```

PO + Tech Lead 討論後選 a。

```
✅ REQ-010 / REQ-018 列入 module-quota-enforcement + module-billing 的 cross_cutting_reqs

接下來請指定每 module owner(從 team-roster.md 抓):
  1. module-package-management → ?
  ...
```

王經理逐個指定 owner 後,V7 SKILL 產出:

```
📄 docs/modules/_plan.md 已產出(對齊 §6.4.11.B contract)

包含:
  - 5 module list + per-module 9 必填欄位
  - Cross-Module Dependency Graph(textual)
  - Shared Files Coordination(列 3 個共動 file:user_lib.py / theme.css / index.html)
  - Branch Naming Convention(feature/<module-slug>)
  - Phase 2 Entry Roadmap

🔍 下一步:跑 /spectra-review docs/modules/_plan.md(對齊 §B.3 rounds_min=2)
```

### 後續 spectra Round 1-2

跟場景 2 類似,**這次只要 2 輪**(對齊 §B.3 small spec scaling)。

完成後 gate-check Phase 1 → 進 Phase 2。

### 重點 takeaways

- ✅ V7 SKILL **不只切模組,還偵測 cross-cutting REQ + 提供 N:M / split 兩路徑**
- ✅ Owner 從 team-roster.md 抓,**不會出現「待定」**
- ✅ Dependency graph 自動產,人類不需手畫

---

## 🎬 場景 5a:Phase 4 主開發 — 工程師接到任務(V2 start)

### 情境

3 個工程師(小華 / 小芬 / 阿凱)各自開 module branch 工作。小華要實作 module-package-management 的 REQ-001(多身份建立)。

過去:寫 code → 改 spec → commit → 再寫 → 再改 → 規格跟 code 慢慢漂移。

現在:

```bash
$ cd modules/module-package-management
$ /v2 start task F-pkg-001
```

V2 implementation SKILL 啟動:

```
🛠 V2 implementation — task F-pkg-001(多身份建立)

讓我幫你準備好工作環境:

✅ 讀 functional.md F-pkg-001 entry:
   - derived_from_reqs: REQ-001
   - acceptance:
     1. 建立首張 profile 同時 create 至少 1 張 main_bizcard
     2. 同一 LINE user 上限 N profile
     3. 預設 main_bizcard 名稱 = profile 身份名稱

✅ 對齊 §6.4.11 §E.1 Per-Test-Case Schema,自動 generate tests.md 草稿:
   - TC-pkg-001: 建立首張 profile + 驗證 main_bizcard 建立
   - TC-pkg-002: 第 2 個 profile + 驗證 limit
   - TC-pkg-003: 預設名稱對齊

🎯 你需要寫的 code 大概:
   - identity-service.js: createProfile() 新增 main_bizcard 連動
   - card-service.js: 預設名稱邏輯

⚠ 跨模組依賴(對齊 §6.4.11 §B.2 module dependency graph):
   - F-pkg-001 acceptance #2「上限 N profile」依賴 module-quota 的 F-quota-001
   - 目前 module-quota F-quota-001 status= 🟡 in-progress(小芬負責,預估 +2 天)
   - 建議:你可先寫 unit test(mock quota 回應)不阻擋,e2e 等小芬 F-quota-001 done

💡 開始時請先在 functional.md F-pkg-001 加 execution_log entry(我會幫你)
   → status: ⏳ planned → 🟡 in-progress

開工?(我會在你 commit 時自動 update functional.md)
```

小華開工。每次 git commit 自動 update functional.md:

```
[V2 auto-update] F-pkg-001:
  - status: 🟡 in-progress
  - execution_log: append "2026-06-18 14:32 - createProfile() 加 main_bizcard 連動"
  - 對應 commit: abc1234
```

### 重點 takeaways

- ✅ V2 SKILL 自動 generate test case **草稿**(工程師仍可改 / 補)
- ✅ git commit 自動 update functional.md,**0 額外負擔**
- ✅ 跨模組依賴自動提醒,**不會等到 e2e 才知道 blocked**

---

## 🎬 場景 5b:開發中遇 blocker — 主動 surface 給 PM

### 情境

小華寫了 2 天 F-pkg-001,寫到 acceptance #3「預設 main_bizcard 名稱 = profile 身份名稱」時發現:`bizcard.set_default_name()` 不支援 emoji,但訂閱專案 PO 允許 emoji profile 名稱。

過去:小華 silently 卡 2 天(不敢提 / 想自己解 / 怕被覺得「能力不夠」)→ PM 隔週才發現。

現在小華主動 surface:

```bash
$ /v2 blocker F-pkg-001 --reason "set_default_name() 不支援 emoji,需 spec 確認 emoji profile 是否支援"
```

PM Skill 回應:

```
🚫 Blocker 已記錄 — F-pkg-001

✅ functional.md auto-update:
   - status: 🟡 in-progress → 🚫 blocked
   - blocker_reason: "set_default_name() 不支援 emoji,需 spec 確認 emoji profile 是否支援"
   - blocked_since: 2026-06-20T10:15:00+08:00
   - assignee: 小華

✅ Cross-impact 分析(對齊 §6.4.11 §B.2):
   - F-pkg-001 blocks: F-pkg-005 / F-pkg-008(下游 2 features)
   - 影響 timeline: 若 24h 內未解,Phase 4 預估晚 1 天

📍 自動觸發行動:
   1. 王經理 daily briefing 明早會 surface 此 blocker
   2. F-pkg-001 加入 PM 「需 1-on-1」清單(對齊 §6.4.8 Fix Recommendation)
   3. 寫進 decision-log:D-blocker-pkg-001 待 PO 拍板「emoji profile 是否支援」

💡 建議下一步:
   - 你可以先做 F-pkg-002 / F-pkg-003(不阻擋)
   - 或等 PM 1-on-1 拍板 emoji policy(預估 < 4h 內)
```

### 王經理視角(15 分鐘後)

王經理在 Slack 看到 PM Skill 觸發的 notification:

```
🔔 PM Skill Notification — namecard-v3-subscription

新 blocker:F-pkg-001(小華 @2026-06-20 10:15)
  blocker_reason: set_default_name() 不支援 emoji
  cross-impact: blocks F-pkg-005 / F-pkg-008
  需要 PO 拍板:emoji profile 是否支援

📍 點此進入 /pm-bug-review F-pkg-001 拍板
```

王經理 30 秒拍板「支援 emoji」,小華收到通知 + decision-log 自動更新,unblock 繼續做。

### 重點 takeaways

- ✅ `/v2 blocker` 讓工程師主動 surface 阻塞,**0 facing-the-boss 心理門檻**
- ✅ Blocker 自動 propagate 到 daily briefing + cross-impact + decision-log
- ✅ 拍板對話從「下次 standup 提一下」加速到「30 分鐘內 unblock」
- ✅ 不會再有「我以為他卡的問題我之前解過,結果他根本沒問」的失誤

---

## 🎬 場景 5c:V2 done — 跑三向 invariant 自動 sign-off

### 情境

小華 unblock 後 1 天完成 F-pkg-001。

```bash
$ /v2 done F-pkg-001
```

```
🎉 F-pkg-001 完成 — 跑 3 向 invariant 對齊 §6.4.11 §E.3a How to Enforce:

✅ every_feature_has_code_commit: 找到 3 個 commits 對齊 F-pkg-001
✅ every_feature_has_test_case: TC-pkg-001/002/003 全在 tests.md
✅ every_test_case_has_result: TC-pkg-001 ✅ pass / TC-pkg-002 ✅ pass / TC-pkg-003 ✅ pass
✅ no_stale_functional_md: functional.md mtime 對齊最新 commit
✅ execution_log_per_done_feature: 4 個 log entries
✅ actual_completion_filled: 2026-06-21

✅ functional.md auto-update:
   - status: 🟡 in-progress → ✅ done
   - actual_completion: 2026-06-21
   - blocker_resolved_at: 2026-06-20T10:45:00 (場景 5b 的 blocker)

📊 F-pkg-001 health: ✅ 全綠 — 進度可 propagate 到 daily report

🔓 Downstream unblocks:
   - F-pkg-005(原 blocked_by: F-pkg-001) → 現可開工
   - F-pkg-008(原 blocked_by: F-pkg-001) → 現可開工
```

### 萬一三向 invariant fail 怎辦

若 `every_feature_has_test_case` fail(小華忘了寫 TC):

```
❌ F-pkg-001 sign-off REJECTED

✗ every_feature_has_test_case: tests.md 找不到 TC-pkg-002
   → acceptance #2「上限 N profile」沒對應 test case

✅ 其他 5 條 invariant 全 pass

🎯 你需要先補上 TC-pkg-002 才能 done。要我幫你 generate 草稿嗎?(y/n)
> y

✅ TC-pkg-002 草稿已加入 tests.md。請 review + 跑 test 後重跑 /v2 done F-pkg-001。
```

工程師補完後重跑 done → 全綠。

### 重點 takeaways

- ✅ done 必跑 6 條 invariant check(對齊 §6.4.11.E.3a)— **spec/code/test 永不漂移**
- ✅ 自動 unblock 下游 features → 接力工程師立刻收到通知
- ✅ Invariant fail 給具體 fix 建議,**不是冰冷 reject**(SKILL 主動幫補 TC 草稿)
- ✅ 對齊 §6.4.11 §E.4a Flaky Policy:若 TC intermittent fail 走合法 flaky path(對齊場景 8)

---

## 🎬 場景 6a:PM 早上 Daily Briefing — 一頁紙看完全 project

### 情境

王經理早上 9:00 進辦公室,泡杯咖啡。

```bash
$ /pm daily
```

### PM Skill 回應

```
☀ Daily Briefing — 2026-06-18(Phase 4 Day 5)

📊 整體進度
  - 25 REQs total: 11 ✅ done / 9 🟡 in-progress / 5 ⏳ planned
  - Burndown: 仍在原 timeline 內(預估 Phase 4 結束:2026-07-15)

👥 Team Status(從 functional.md status + commit log 推導)
  - 小華(module-package-management): 8/8 features done ✅ ahead
  - 小芬(module-quota-enforcement): 3/6 features done — 正常
  - 阿凱(module-billing): 0/4 features done — ⚠ 連續 3 天無 commit
                                                  ↑ 需 attention

🚨 Anomalies(健康檢查偵測,對齊 §6.4.11 §E.3a)
  1. ⚠ module-billing F-bill-002 status='done' 但 functional.md 無 execution_log
     → 違反 §6.4.11 §E.3 三向 invariant
     → 建議找阿凱補 log

  2. 🟢 module-package-management F-pkg-001 跨模組 ref module-quota
     → 等小芬 F-quota-001 完成才能 e2e 測試,小芬預估 +2 天

  3. 🚫 module-package-management F-pkg-001 昨日有 blocker
     → 已由 PO 拍板「支援 emoji profile」於 10:45 unblock(對齊場景 5b)
     → 無需 action

📍 推薦 fix order(對齊 §6.4.8 Fix Recommendation Algorithm)
  1. Top: 找阿凱 1-on-1 看是不是 blocked(severity=6 / 影響 Phase 4 timeline)
  2. Next: F-pkg-001 execution_log 補(severity=2 / quick win)

📅 今日 commitments
  - 10:00 阿明 / 小芬:cross-module review F-quota-002
  - 14:00 PO walk-through Phase 4 mid-point check

🧪 Flaky test watch(對齊 §6.4.11 §E.4a)
  - module-quota: 1/2 flaky(對齊 §E.4a max_flaky_per_module)
  - 全 project: 1/5 flaky(對齊 max_flaky_total)
  - revisit_at 倒數:TC-quota-005 還有 42 天到 revisit deadline

—— 一頁完。你想 deep dive 哪個?
```

王經理 5 分鐘看完,知道:
1. 阿凱可能有問題,**今天要找他 1-on-1**
2. F-pkg-001 跨依賴正常等待 + blocker 已解,不需 follow up
3. 整體 timeline 仍在軌道上
4. flaky test 使用量還在 budget 內

### 重點 takeaways

- ✅ **一頁紙看完整個 project 健康度**(不用看 Jira board)
- ✅ Anomaly / blocker / flaky 三類自動偵測 — 沒漏網
- ✅ Fix order 機械化推薦 — PM 不用判斷哪個先處理
- ✅ Daily briefing **是 PM 唯一需要看的東西**(取代多個 dashboard)

---

## 🎬 場景 6b:PM 對 anomaly 採取行動 — 找阿凱 1-on-1

### 情境

王經理看完 6a daily briefing,Top recommendation 是「找阿凱 1-on-1」。她 ping 阿凱 10:30 來會議室。

談完後她發現:阿凱卡在 F-bill-001 因為 backend Stripe API 文件不清楚,2 天沒問。

### 王經理用 PM Skill 把談話結果落地

```bash
$ /pm-bug-review module-billing --finding F-bill-001
```

```
─ F-bill-001(0 commits in 3 days) ─
  spectra default severity: 6.0 (中高 — 影響 Phase 4 timeline)
  推測 root_cause: 阿凱自己 explore Stripe API
  
  PO 拍板?
    [a] mark blocker — backend Stripe API 文件需求 → 走場景 5b 流程
    [b] re-assign — 交給有 Stripe 經驗的小華
    [c] pair programming — 阿明跟阿凱 pair 1 小時 unblock
    [d] 自訂 action
  > c

  輸入 reason / commitment:
  > "阿明 14:00-15:00 跟阿凱 pair,unblock 後阿凱重啟工作流"

  ✅ 記錄到 decision-log:
     D-pm-action-bill-001: F-bill-001 → pair programming(阿明 + 阿凱 14:00)
  
  ✅ functional.md auto-update:
     - F-bill-001 status: 🚫 blocked → 🟡 in-progress(scheduled pair)
     - assignee_secondary: 阿明(pair)
     - planned_unblock_at: 2026-06-18T15:00:00
  
  ✅ 自動 propagate 到明天 daily briefing:
     - 「F-bill-001 昨日 pair programming,已 unblock,觀察今日 commit」
```

### 隔天 daily briefing 自動 follow up

明早王經理跑 `/pm daily`:

```
☀ Daily Briefing — 2026-06-19(Phase 4 Day 6)

📍 Follow-up from yesterday(對齊 §6.4.6 Action Log)
  ✅ F-bill-001 — pair programming 完成,阿凱昨晚 commit 3 個 progress
     → assignee_secondary: 阿明(pair)→ removed,阿凱獨立進行
     → 預估按時 Phase 4 結束

👥 Team Status
  - 阿凱(module-billing): 1/4 features in-progress ✅ 回到軌道
  ...
```

王經理鬆一口氣,知道阿凱回到軌道。

### 重點 takeaways

- ✅ Daily briefing → action → 明天 follow up,**形成完整 closed-loop**
- ✅ 「3 天無 commit」不再是黑箱,有結構化處理路徑(blocker / re-assign / pair / 自訂)
- ✅ Anomaly 解了還會自動 mark resolved + 明天 verify,**PM 不用記憶哪個 action 還沒 close**
- ✅ Pair programming / re-assignment 等管理動作的 commitments 全進 decision-log,**audit trail 完整**

---

## 🎬 場景 7:跨組依賴衝突 surface — Phase 2 提早抓

### 情境

Phase 4 開到第 5 天,V8 跨模組 review 自動跑了一輪。

### PM Skill 回應

```
🔍 V8 Cross-Module Review Round 3(weekly auto-run)

🟡 跨模組 spec 衝突偵測:
  module-quota.functional.md F-quota-003:
    "quota 扣減後 < 0 時 → 拋 InsufficientQuotaError"
  
  module-billing.functional.md F-bill-001:
    "升級時觸發 quota refresh,先扣後加"
  
  ⚠ 兩個 feature 同時觸發時,race condition:
     如果 billing 先扣 quota,quota service 會先 throw 後 refresh
     → 升級會 fail,user 看 error
  
  📍 推薦 fix:
     a) module-quota 加 transactional flag
     b) module-billing 改用 atomic upgrade-then-refund pattern
  
  ⏰ Phase-aware: 現 Phase 4 / 若不修 Phase 5 整合會撞牆
  
  📊 effective_cost: 6.5(現修 0.8 / Phase 5 撞牆修 8.0)

🎯 建議:今天 stand-up 跟小芬 + 阿凱對焦,選 a 或 b
```

王經理立刻 ping 小芬 + 阿凱進會議。1 小時討論決定 b,當天落地。

### 對比過去

過去:Phase 5 整合測試發現 race condition → 兩個工程師 + Tech Lead 救火 3 天 → 整個 release 推遲 1 週。

現在:Phase 4 第 5 天偵測 → 1 小時討論 → 當天 fix → **省 3 天 + 1 週延遲**。

### 重點 takeaways

- ✅ **跨組衝突 Phase 2 / Phase 4 早期 surface**(對比過去 Phase 5 整合才爆)
- ✅ V8 SKILL 自動 weekly run,**PM 不用想到就主動觸發**
- ✅ 救火成本 -10x(對齊 highlights memo §一 hook)

---

## 🎬 場景 8:Phase Gate 卡關 — `/pm-bug-review` 救援

### 情境

Phase 4 結束前,王經理跑:

```bash
$ /pm gate-check phase-4
```

```
🚪 Phase 4 Exit Gate-Check

⚠ 部分 criteria fail:

✅ 1. 全 module feature status=done
⚠ 2. 全 module test-results 100% pass — 觸發 §6.4.11 §E.4a Flaky Test Tolerance 流程
   - module-quota TC-quota-005 重跑 3 次 2 pass 1 fail(pass_rate=0.67 ≥ 0.66 floor)
   - 候選 flaky path:需 PO 拍板 + 必填 known_flaky_reason + revisit_at

✅ 3. 三向 invariant 全 pass
❌ 4. V8 最後一輪 verdict
   - V8 Round 5 找到 1 個 CONCERN:F-bill-003 acceptance 不夠 atomic
   - 已 fix?需 PO confirm

✅ 5. lint baseline 不增
⚠ 6. decision-log.md 有 2 個 pending 拍板(來自 V8 Round 4)

🎯 不能進 Phase 5。建議:
  $ /pm-bug-review module-quota --finding TC-quota-005
  $ /pm-bug-review module-billing --finding F-bill-003
```

王經理跑 `/pm-bug-review`:

```
─ TC-quota-005 (intermittent fail) ─
  spectra default severity: 5.5 (中等)
  flaky_test_tolerance(§6.4.11 §E.4a)候選 — 須完成 5 條件才能合法 mark flaky:
  
  PO 拍板?
    [a] mark flaky:對齊 §E.4a — 必填 known_flaky_reason + revisit_at(8 週內)
        + 加 retry-on-flake 邏輯;module-quota flaky count: 0/2 → 1/2(未達 cap)
    [b] hard fail(必修)— Phase 4 不可 exit,先修再說
    [c] reject — 標記 not-flaky 但仍 deferred(違反 contract,需 PO 強簽 + 風險自負)
  > a

  → 進入 flaky 流程:
    known_flaky_reason: "Azure API rate limit p99 抖動 < 5% case"
    revisit_at: 2026-08-01(Phase 5 整合後 4 週內必 revisit)
    retry mechanism: 加 retry × 3 with exponential backoff
  
  ✅ 記錄 decision-log。tests.md 加 flaky 標記。module-quota flaky count: 1/2 ✓
  ✅ §E.4a 5 條件全 ack,**未 bypass invariant 而是走合法 flaky path**
```

10 分鐘走完,gate-check 再跑全綠(flaky path 合法接受)→ 進 Phase 5。

### 重點 takeaways

- ✅ Gate-check **不是 binary pass/fail**,而是引導 PO 拍板灰色地帶
- ✅ `/pm-bug-review` 是 PO 的「拍板 console」,**所有決定都記 audit**
- ✅ 不再有「我覺得 OK 就過」的主觀判斷

---

## 🎬 場景 9:Phase 5 整合 + Phase 6 上線

### 情境

Phase 5 整合用 V2 implementation 對齊 integration branch。E2E 真機測試。

```bash
$ /pm validate-integration
```

```
🔍 Phase 5 Integration Validator

✅ E2E test results(R-XX 真機驗測對齊 memory: real-device testing)
   - 12 / 12 cases pass on iPhone / Android(Sony / Samsung)
   - 對齊 §6.4.11 §F.1 e2e_test_results schema

✅ Perf SLA(對齊 Requirement Spec §SLA)
   - api_p95: 320ms(threshold 500ms)✅
   - friend_search: 0.9s(threshold 1s)✅

✅ V3 integration review pass(spectra-review 1 輪 ship-as-is)
✅ Phase 5 ready

→ 簽核後可進 Phase 6
```

Phase 6 上線:

```bash
$ /pm validate-release
```

```
🔍 Phase 6 Release Validator

⚠ Rollback plan 狀態:
  - documented ✅
  - rehearsed ❌(對齊 §6.4.11 §G.3 rollback_plan_rehearsed 必填)
  
🎯 必須先 rehearse 才能 ship。建議:
  1. 在 staging 跑一次完整 rollback drill
  2. 寫結果到 docs/release/2026-08-17-rollback-rehearsal.md
  3. 重跑本 validator
```

王經理當下安排 rollback drill,2 小時後完成 → 重跑 → 全綠 → 簽核 → ship。

### 重點 takeaways

- ✅ Phase 6 強制 **rollback rehearsal**(對比過去「就寫 plan 沒實測」)
- ✅ Azure Webapp Linux 3.0 對齊 memory(auto check 環境)
- ✅ 沒 rehearse 就 ship 的人為錯誤被機械化阻擋

---

## 🎬 場景 10:Phase 7 Post-launch + Retrospective

### 情境

上線 7 天後,王經理跑:

```bash
$ /pm validate-post-launch
```

```
🔍 Phase 7 Post-Launch Validator(對齊 §6.4.11.H)

✅ Production stability: 7 days, 0 critical incident
✅ P0/P1 bugs: 全 closed(3 個 P1 已 fix)
✅ Perf 仍在 SLA 內
✅ User feedback collected: 23 entries(對齊 §H.2 schema)
   - 18 positive / 3 neutral / 2 negative(都是 feature request)
✅ KPI evaluation: efficiency=78%(達標)/ quality=88% / strategic=待 12 月後評估
   → overall verdict: meet

⏸ Retrospective 缺
   → 需要團隊一起寫(對齊 §H.3 5 mandatory sections)

📍 我可以立刻引導 retrospective workshop(2 小時 interactive 模式)
   要開始嗎?(y/n)
> y
```

PM Skill 進入 interactive retrospective workshop 模式(對齊 §6.4.11 §J.1 — Phase 7 SKILL 自動觸發,無需獨立命令),引導團隊用 §H.3 5 個 mandatory section 寫:

```
🎬 Retrospective Workshop(2 小時)

Section 1: What went well(team brainstorming)
  - "Cross-module 衝突 Phase 4 就抓到,沒救火"
  - "Daily briefing 取代 standup,每天省 30 分鐘"
  - "Rollback rehearsal 強制 → 上線信心高"
  - ...

Section 2: What didn't go well
  - "F-quota-005 intermittent fail 拖了 1 週"
  - "阿凱 3 天無 commit 期間其實有 blocker 沒講"
  - ...

Section 3: Lessons learned
  - "PM Skill anomaly detection 有用,但工程師仍需主動 surface blocker"
  - "下次 Phase 0 要更明示『intermittent test 容忍度』policy"
  - ...

Section 4: Recommendations for next project
  - "PM Skill 試跑成功 → 推到全 org"
  - "下個 project sprint cycle 可考慮 2 週(此次 3 週)"
  - ...

Section 5: Team consensus
  - 王經理 ✅
  - 阿明 ✅
  - 小華 ✅
  - 小芬 ✅
  - 阿凱 ✅
```

Retrospective 寫完進 Phase 7 final close:

```bash
$ /pm signoff phase-7 --approver PO --approver boss --close-project
```

```
🎉 Project namecard-v3-subscription Closed

✅ Phase 0 → 7 全 signoff trail 保留
✅ Final state: closed(state.md current_phase=closed)
✅ Retrospective lessons → feed 到 organizational knowledge base
✅ 下個 project 的 Requirement Spec 可引用本 retrospective(對齊 §6.4.11 §A iteration loop)

🎯 試跑成功!PM Skill 驗證 work。

完整文件清單:
  - Requirement Spec rev .4
  - 5 modules × R/F/P specs
  - 全 phase reports / reviews / decision-log
  - KPI evaluation + retrospective
  - audit trail 100% 保留
```

### 重點 takeaways

- ✅ Retrospective **不是寫完丟掉**,lessons feed 回下個 project 的 Phase 0(對齊 §6.4.11 §A iteration loop)
- ✅ **organizational knowledge 累積永不消失** — 工程師流動 / PM 換人都不影響
- ✅ 整個專案 audit trail 100% 保留,**可橫展可審計**

---

## 🎬 場景 11:跨 project — 用前 project lesson + override mechanism

### 情境

王經理接下一個 project,先建 per-project subfolder + Phase 0:

```bash
$ /pm init "namecard-v3-team-account"
   → 建 docs/pm/namecard-v3-team-account/(對齊場景 0 per-project 結構,不衝突既有 subscription)
$ /pm start "namecard-v3-team-account" --from-verbal-brief
```

```
🎬 Phase 0 啟動 — Project Kick-off

我自動 inject 以下 organizational knowledge:

  📋 Source(對齊 spectra Round 1 N3 fix + Round 5 path fix):
  - 前 project retrospective:`docs/pm/namecard-v3-subscription/retrospectives/` 或 `_org/org-retrospectives/`
  - 前 project Decision Log:`docs/pm/namecard-v3-subscription/decision-log.md`
  - Org-level decisions:`docs/pm/_org/org-decision-log.md`(cross-project sync entries)
  - 全 org memory(auto memory system):`memory/MEMORY.md` 索引
  - 既有 contract override history:`docs/pm/_org/org-decision-log.md` D-contract-override-* entries
  
  📋 Assumptions(從 namecard-v3-subscription Phase 7 lessons):
  - intermittent test 容忍度 policy(下次 Phase 0 要明示)
  - sprint 2 週試水(下次 project 建議)
  
  📋 Constraints(沿用 memory + 前 project):
  - backend_change_rule / v1_ui_retired / azure_webapp_runtime
  - 沿用 5 module 切法經驗
  
  ⚙ Contract Override(對齊 §6.4.10 §L):
  
  本 project 是 internal team POC,2 週驗證,規模 < 10 REQ。建議激進 override:
    - 對 §6.4.10.B.1 review_process.rounds_min 從 3 → **1** override(small spec POC,符合 §C scaling)
    - 對 §6.4.10.B.2 nits_open_max 從 5 → **8** override(POC 探索容忍小 polish)
    - reason 範例:「2 週驗證 POC,team 已熟訂閱專案經驗,review 過嚴會卡死試錯」
  
  ⚠ 偏離 default 50%+ → 觸發 PO ack(對齊 §6.4.10.L.2)
  
  > 拍板:
    [a] accept 全部 override(rounds_min=1, nits_max=8)
    [b] keep default(rounds_min=3, nits_max=5)
    [c] 自訂(輸入各欄位新值)
  > a
  
  ✅ 2 個 override 記錄到 decision-log:
     D-contract-override-1: §6.4.10.B.1.rounds_min default=3 → override=1
       | reason: 2 週 POC 驗證 + team 已熟訂閱經驗
       | deviation: 66.7% → 需 PO ack ✅
     D-contract-override-2: §6.4.10.B.2.nits_max default=5 → override=8
       | deviation: 60% → 需 PO ack ✅

接下來... [問 Q1-Q4]
```

### 重點 takeaways

- ✅ Lessons from prior projects 自動 inject,**新 PO 不用從零開始踩雷**
- ✅ Contract Override 透明合法,**PO 可客製化但留 audit trail**
- ✅ 跨 project 經驗累積 → PM Skill 「越用越聰明」

---

## 🎬 場景 12:橫展到其他 project — 多 project 並行 + Org-Level View

### 情境

3 個月後,王經理同時帶 3 個 active project:

| Project | Phase | 狀態 |
|:---|:---:|:---|
| namecard-v3-subscription | 7(觀察期)| Day 12 / 14 |
| namecard-v3-team-account | 4(主開發)| Day 8 / 18 |
| nfc-poc(NFC 探索)| 1(模組切割)| Day 2 / 5 |

3 個 PM 跑全 standup 要 90 分鐘 + 看 3 個 Jira board = 不可能。

王經理早上 9:00:

```bash
$ /pm dashboard
```

### PM Skill 回應(多 project 橫向 view)

```
🏢 PM Skill Cross-Project Dashboard — 2026-09-15
   讀取來源:docs/pm/*/state.md(掃所有 project subfolder,排除 _org)

📊 Active Projects(3 個)

┌──────────────────────────────┬───────┬─────┬──────┬───────────────────┐
│ Project                      │ Phase │ Day │ Burn │ Health           │
├──────────────────────────────┼───────┼─────┼──────┼───────────────────┤
│ namecard-v3-subscription     │ 7     │12/14│ 86%  │ ✅ stable        │
│ namecard-v3-team-account     │ 4     │ 8/18│ 44%  │ ⚠ 1 anomaly      │
│ nfc-poc                      │ 1     │ 2/5 │ 40%  │ ✅ on track      │
└──────────────────────────────┴───────┴─────┴──────┴───────────────────┘

🚨 Cross-Project Anomalies(對齊 §6.4.8 橫向 Fix Recommendation)
  
  1. ⚠⚠ Resource conflict(critical)
     - 小華 同時在 team-account F-team-003 + nfc-poc F-nfc-001 兩個 in-progress
     - 觀察:過去 7 天 commit 集中在 team-account,nfc-poc 0 commit
     - 建議:跟小華 sync,確認 nfc-poc 是否需 reassign
  
  2. 🟡 Common pattern 重複(efficiency loss)
     - team-account 跟 subscription 都遇到「emoji 名稱處理」issue
     - subscription decision-log 有 D-blocker-pkg-001 拍板「支援 emoji」
     - team-account 阿凱 2 天前提出類似問題還沒解
     - 建議:把 subscription 的 decision 引到 team-account decision-log
  
  3. 🟢 Best practice 浮現
     - subscription Phase 7 user_feedback 收集 23 entries(對齊 §H.2)
     - team-account Phase 5 將進入 integration,可借鏡 subscription 的 R-XX 真機驗測 case set
     - 建議:把 subscription test-results 加入 team-account 參考清單

📊 Cross-Project KPI Rollup(對齊 §7.5 三層 KPI)
  
  Efficiency:
    - PM standup 時間:過去 3 個月平均 5 min/day(對比啟用前 90 min)→ 94% 節省
    - 規格衝突 surface 時點:平均 Phase 2.3(目標 ≤ Phase 3)✅
  
  Quality:
    - Phase Gate fail rate: 15%(因 anomaly 自動 surface,Gate 不再 surprise)
    - flaky test ratio: 4/15 = 27%(對齊 §E.4a tolerance)
  
  Strategic:
    - 文件三件套(proposal / highlights / manual)成熟度:✅ all ship
    - 跨 project 橫展次數:3(目標 ≥ 2)✅

📋 Today's Top 3 actions
  1. 🔴 小華 resource conflict(team-account vs nfc-poc)— 立即 sync
  2. 🟡 引 subscription decision 到 team-account emoji issue
  3. 🟢 subscription Phase 7 結案前最後 walk-through

—— 90 秒看完 3 個 project。要 deep dive 哪個?
```

### 王經理視角

過去:每個 project 跑 30 min standup,3 個 project = 90 min/day 黑洞。
現在:**1 個 dashboard 5 min,multi-project anomaly 自動偵測,common pattern 自動 cross-reference**。

王經理用 `/pm dashboard` 5 min 看完,接著:

```bash
# 方式 A:全 flag 指令(對齊 CI/CD batch 使用)
$ /pm cross-project sync-decision \
  --from subscription \
  --to team-account \
  --decision D-blocker-pkg-001 \
  --reason "emoji 處理 issue 重複,同套 decision 適用"

# 方式 B:interactive prompt(對齊 Round 3 N4 fix,日常 PM 使用更友善)
$ /pm cross-project sync-decision
> source project: subscription
> target project: team-account
> decision id: D-blocker-pkg-001
> reason: emoji 處理 issue 重複,同套 decision 適用
```

```
✅ Decision 跨 project 同步:
  - subscription D-blocker-pkg-001(emoji profile 支援)
  - → 引用至 team-account decision-log 為 D-cross-team-001
  - 阿凱明早 daily briefing 會看到「emoji issue 已有 PO 拍板:支援」
  - 預估省 阿凱 1-2 天 探索時間
```

### 半年後:Org-level retrospective

3 個 project 都 ship 後,王經理跑:

```bash
$ /pm org-retrospective --window 6months
```

```
📊 Org-Level Retrospective(2026-Q3+Q4)

✅ Project 結案:3
  - namecard-v3-subscription(2026-09-30,Phase 7 closed)
  - namecard-v3-team-account(2026-12-15,Phase 7 closed)
  - nfc-poc(2026-10-30,killed at Phase 3 — stop loss exercised ✅)

📊 跨 project lessons aggregation(對齊 §6.4.11.A iteration loop)
  1. 「emoji 名稱處理」3 個 project 都遇過 → 應該寫進 org-level glossary
  2. 「intermittent test in Azure」3 個 project 都用 flaky_test_tolerance → policy 證明 work
  3. 「nfc-poc stop loss」在 Phase 3 觸發 → 對齊 §10.7 設計，stop loss work as designed
  4. 跨 project resource 衝突 1 次(小華 team-account vs nfc-poc) → 建議下季加 resource_locking mechanism

📊 Org-Level KPI 達標
  - 全 org 累積節省工時:~960 小時(3 project × 平均 320h/project,對齊前言 evidence basis;實際 ROI 須試跑驗證)
  - PM 滿意度:王經理 4.5/5(對齊 §10.7 stop-loss 試跑判定標準 ≥ 4/5)✅
  - 工程師反饋友善度:4.2/5 ✅
  - 老闆 ROI 評估:meet(對應 §九 ROI 預估)✅

📋 Recommendations for 2027 Q1
  1. PM Skill 升級 v2:加 resource_locking(對應 #4 lesson)
  2. 推廣到其他組(market validation 證實 work)
  3. Org-level glossary 落地(對應 #1 lesson)
  4. nfc-poc 觀察期延長後 revisit(stop loss 不代表永久放棄)

📍 完整 org-level retrospective 寫進:
   docs/pm/_org/org-retrospectives/2026-h2.md(append-only,對齊 Round 5 path fix)
```

### 重點 takeaways

- ✅ **單 PM 並行管理 3 個 project 從不可能變可能**(90 min standup → 5 min dashboard)
- ✅ **跨 project anomaly 自動 surface**(resource 衝突 / common pattern / best practice 橫向 share)
- ✅ **Org-level KPI rollup** 老闆視角直接答 ROI(對齊 §7.5 三層 KPI)
- ✅ **Decision 跨 project 同步**(一個 PO 拍板可省其他 project 探索時間)
- ✅ **Stop loss 不是失敗** — nfc-poc 在 Phase 3 觸發 stop loss 也算成功(對齊 §10.7 退路 1 設計)
- ✅ **lessons aggregation 形成 org-level knowledge base**,不是「丟掉的 retrospective」

---

## 🎬 場景 13:新工程師 onboarding — 中途加入 + 接替交接

### 情境

訂閱專案做到 Phase 4 Day 7。公司新 hire 一個工程師 **小林** — 接替阿凱(他要去做 nfc-poc)。

過去的痛苦:
- 小林第 1 天看到 5 個 module / 25 個 REQ / 12 份 spec / 50 條 decision-log → 茫然
- 找阿凱 onboarding 但阿凱要交接 + 自己也要去 nfc-poc,只能擠 1 小時
- 小林第 1 週只敢看 code 不敢動,**第 2 週才開始 commit,ramp-up 1-2 週**

現在小林 Day 1 早上,王經理跑:

```bash
$ /pm onboard 小林 --replace-for 阿凱 --module module-billing
```

### PM Skill 回應

```
🎓 Onboarding 小林 — 接替阿凱(module-billing)

讀完 docs/ 後我幫你準備個人化 onboarding pack:

📚 必讀清單(預估 2 小時)
  1. Requirement Spec §module-billing(15 min)
  2. functional.md module-billing(20 min,含 4 features 當前 status)
  3. decision-log 過去 14 天 D-bill-* 拍板(30 min,共 7 個拍板)
  4. 阿凱最後 5 個 commit 的 PR + execution_log(40 min)
  5. flaky test:TC-bill-002 已標 known_flaky_reason(看 §6.4.11 §E.4a Policy)
  6. cross_cutting_reqs:REQ-010 / REQ-018(對齊 §6.4.11.B.2 N:M 認領)

📋 跟你身份直接相關的 unresolved
  - 🔴 F-bill-001:阿明 pair 中(對齊場景 6b)→ 你接,先看上一次 pair 紀錄
  - 🟡 decision-log 1 個 pending:「退費邏輯 atomic vs best-effort」→ 等 PO 拍板
  - 🟡 flaky_test_tolerance: module-billing 0/2 used(對齊 §E.4a max_flaky_per_module)
                          → 你還有 2 個 flaky budget 可用

👥 該找誰(對齊 team-roster.md)
  - PO 王經理: 商業邏輯 / 拍板(每日 daily briefing 同步)
  - Tech Lead 阿明: 架構 / pair programming
  - 小芬(module-quota): 跨模組 interface(F-bill-001 ↔ F-quota-002)
  - 小華(module-package-management): 相關 cross_cutting_reqs REQ-018

⏰ Day 1-3 上手路徑(對齊 V2 SKILL 工作流)
  - Day 1: 讀完必讀清單 + `/v2 status module-billing` 看現況
  - Day 2: 接 F-bill-003(範圍最小,熟工作流)
  - Day 3: 接 F-bill-001(從阿凱 hand-over 開始,有阿明 pair 紀錄 fallback)

🔍 自動 inject 的 organizational knowledge
  - 從 namecard-v3-subscription:過去 14 天的 4 個 retrospective 中段 lessons
  - 從 memory: backend_change_rule / azure_webapp_runtime / receiver_edit_invariant
    → 影響 module-billing 的 3 條 invariant 已自動標
  - 阿凱本月 1-on-1 talk 紀錄(若有寫進 decision-log)

✅ 系統自動 update(audit trail 完整)
  - team-roster.md: 新增 小林 owner / 阿凱 status: transferring
  - _plan.md: module-billing.owner 阿凱 → 小林(effective 2026-06-25)
  - 阿凱 last_commit 標 hand-over status: ready
  - decision-log append: D-onboard-小林-001

📊 預估 ramp-up: 1-2 天(對比業界 1-2 週,節省 80%)
   評估方法: 對齊 §六商業價值 + 場景 12 跨 project 借鏡
```

### 阿凱(離開的工程師)視角

阿凱不需要再「擠 1 小時 onboarding 小林」。他跑:

```bash
$ /pm offboard 阿凱 --next-project nfc-poc
```

```
👋 Offboarding 阿凱 — 轉到 nfc-poc

✅ Hand-over check(對齊 §6.4.11 §E.3 三向 invariant):
  - module-billing functional.md: 4 features status 全 ✅ 或 🟡(無 stale)
  - execution_log: 過去 14 天 commits 全有對應 log
  - actual_completion 全 ack:3 done features 全填
  - tests.md: TC-bill-002 flaky 標 + revisit_at 已設

⚠ Half-done features 處理(對齊 Round 3 N2 fix — F-bill-001 進度 50%):
  - F-bill-001 status: 🟡 in-progress 50% 進度 → 自動 split 為 hand-over checklist:
    a) 已完成部分:functional.md execution_log 列前 8 commit 摘要
    b) 未完成部分:剩餘 acceptance criteria 自動標「pending continuation」
    c) Context dump:本機 untracked code(work-in-progress branch)自動 push 為 `wip/<feature>-acc-handover`
    d) Knowledge points:阿凱寫 5 行 free-text「我寫到哪 / 下一步該怎做 / 我擔心的點」(必填)
  - 此 checklist 自動加入 小林 onboarding pack 的「unresolved」段(對齊場景 13 個人化 pack)

⚠ Hand-over 未盡事項(已自動傳給小林):
  - F-bill-001 pair 紀錄:阿明 14:00-15:00 紀錄
  - 你寫的 retry-on-flake 邏輯在 commit ghi5678,小林需熟悉
  - decision pending D-bill-007 等 PO 拍板,小林知道即可

✅ 你可以走了。team-roster.md 已更新。
   接下來 nfc-poc Phase 1 等你 — /pm status nfc-poc 看開工狀況。
```

阿凱 5 分鐘走完 offboarding(若有 half-done features 需多 5-10 分鐘填 knowledge points)。**零會議室時間 + 完整 audit**。

### 小林 Day 1 結束(下班前)

小林跑:

```bash
$ /v2 status module-billing
```

```
📊 module-billing 當前狀態

Features:
  F-bill-001:🟡 in-progress(你接手,前任:阿凱 + 阿明 pair 中)
  F-bill-002:✅ done(完成 2026-06-15,actual_completion 已填)
  F-bill-003:⏳ planned(建議你 Day 2 先做)
  F-bill-004:⏳ planned(等 F-bill-001 完成)

Tests:
  TC-bill-001 / TC-bill-003 / TC-bill-004:✅ pass
  TC-bill-002:🧪 flaky(對齊 §E.4a,revisit_at: 2026-08-15)

最近 5 commits(阿凱):
  ghi5678 - F-bill-001 retry-on-flake 邏輯
  ...

🎯 你今天讀完必讀清單後,建議明早 pair 阿明 30 分鐘對齊 F-bill-001 context。
```

### 隔天 daily briefing 自動 follow up

王經理早上跑 `/pm daily`:

```
☀ Daily Briefing — 2026-06-26(Phase 4 Day 8)

🎓 Onboarding update
  - 小林(Day 2 onboarded yesterday):
    - 必讀清單:完成 5/6(差 #6 cross_cutting_reqs,今早繼續)
    - 今天計畫:F-bill-003 unit test + 14:00 pair 阿明 F-bill-001
    - 預估 Day 3 開始獨立 commit

👥 Team Status
  - 小林(module-billing): 0/4 features done(Day 2,正常 ramp-up)
  - 阿凱(nfc-poc): 已轉到新 project,nfc-poc Phase 1 進度...
...
```

### 重點 takeaways

- ✅ **新人 ramp-up 從 1-2 週 → 1-2 天**(對齊 §六商業價值「對組織的好處」)
- ✅ **離職 / 轉組 0 會議室負擔** — `/pm offboard` 自動驗證三向 invariant + 傳承完整 audit trail
- ✅ **個人化 onboarding pack** — 不是「全 spec 丟給你」,而是「跟你身份相關的 unresolved」精準篩選
- ✅ **memory + organizational knowledge 對 individual 同樣自動 inject**(對齊場景 11 跨 project iteration loop)
- ✅ **Audit trail 完整保存** — 「阿凱說過什麼」不再只在他腦袋,全在 decision-log + execution_log
- ✅ **Stop loss 應用** — 阿凱可以走得乾淨,工程師流動風險可控(對齊 §10.7 失敗退路設計理念)

---

## 🎬 場景 14:PM Skill 自己升級 — Contract change governance

### 情境

PM Skill 上線 6 個月,跑了 3 個 project 後 PO 累積觀察:

| 觀察 | 想改的 |
|:---|:---|
| §6.4.11 §E.4a Flaky Policy 寫 `max_flaky_per_module ≤ 2`,實務上小 module 需 3-4 個 | 鬆綁到 3 |
| 加州 / 歐盟客戶要求每 REQ 必填 `regulatory_risk: low/med/high` 對齊新合規 | 加 per-REQ 必填欄位 |
| `/pm validate-all` output 老闆 review 時希望加色彩 | 加 ANSI color |

過去:這 3 個 change 各自塞進文件,**3 個 active project 哪個對齊哪個沒對齊?沒人記得**。

現在 PO 跑:

```bash
$ /pm contract-change propose
```

### PM Skill 回應(Wizard)

```
🔧 Contract Change Proposal Wizard(對齊 §6.4.13 Contract Change Governance)

請輸入 change list(可多筆):
> 1. §6.4.11 §E.4a max_flaky_per_module: 2 → 3
> 2. §6.4.10 §B.4 per-REQ required fields: 加 regulatory_risk(enum: low/med/high)
> 3. §6.4.11 §J Master Validator output: 加 ANSI color

🧐 自動分類影響(對齊 §6.4.13 patch/minor/major):

  Change 1: max_flaky_per_module 2→3
    Type: PATCH(寬鬆規則,既有 project 自動受惠,無 breaking change)
    → 不升 version,正常 commit
    → 預估影響: 0 active project break,全受惠

  Change 2: 加 regulatory_risk required field
    Type: MAJOR(per-REQ 必填欄位增加,既有 REQ 無此欄會 validator fail)
    → 需 升至 req-contract-v2 + PO 拍板 + 12 週 deprecation 緩衝期
    → 預估影響: 3 active project 共 87 REQ 需 migration
    → 對齊 memory: backend_schema_change_workflow(SSOT 必同步)

  Change 3: validator output 加 color
    Type: PATCH(純 UX polish,無 API/schema 變動)
    → 不升 version

⚠ 衝擊評估(對齊 §6.4.11.A iteration loop 反查全 project)
  - namecard-v3-subscription Phase 7(2 週後結案):不影響(Phase 7 凍結 schema)
  - namecard-v3-team-account Phase 4(8 天進度):受 Change 2 影響 — 25 REQ 需補 regulatory_risk
  - nfc-poc Phase 1(2 天進度):受 Change 2 影響 — 12 REQ 需補(POC 階段 migration 成本低)

📋 PM Skill 自動 generate 12 週 migration plan:

  Week 0(本週):
    - PO 拍板 Change 2(MAJOR)+ 在 decision-log 公告 v2 介紹
    - Change 1 + 3 patch 直接落地 proposal rev 1.7
    - 寫 contract-pack-v1.1 ↔ req-contract-v2 對應表 至 `docs/pm/_org/contract-pack/`(對齊 Round 5 path fix)

  Week 1-4(過渡期):
    - 自動 generate v1→v2 migration script:
      對既有 REQ 補 default regulatory_risk='low'(後續 PO review 調整)
    - 各 project owner review migration result
    - PM Skill weekly briefing 追蹤 migration progress

  Week 5-12(deprecation 緩衝):
    - v1 + v2 並存,新 project **必走 v2**
    - 既有 project 可選 migrate timing
      - nfc-poc 早點 migrate(POC 階段成本低)
      - team-account Phase 5-6 整合期間 migrate(避免 Phase 4 主開發期)
    - 每週自動提醒未 migrate project + 距 EOL 天數

  ⚠ active_contract_version 機制(對齊 Round 3 N5 fix — 解工程師「該用哪個」認知負擔):
    - 每 project state.md 標 active_contract_version: req-contract-v1 | v2
    - 工程師寫新 REQ / spec 時 PM Skill 自動依此 active version 套 schema
    - 進行中 project 一旦 PO 決定 migrate(eg. team-account 在 Phase 5)
      → state.md update active_contract_version: v1 → v2
      → 自此後新增 REQ 用 v2 schema(舊 REQ 走 migration script 一次性轉換)
    - 工程師永遠看 state.md 知道「我這 project 現在該用哪個」,不靠記憶

  Week 12:
    - v1 EOL,所有 active project 必 migrated
    - 若有未 migrate,自動 block phase advance(對齊 §6.4.11 Master Validator)

🎯 拍板?
  [a] accept 全 3 changes,立即啟動 migration
  [b] 只接 Change 1 + 3(patch 級),Change 2 延後評估
  [c] 全部 defer
  [d] 自訂(逐項拍板)
> a

✅ 已落地:
  - §6.4.11 §E.4a 改 max_flaky 2→3(pm-skill-proposal.md rev 1.7)
  - §6.4.11 §J output 加 color(pm-skill-proposal.md rev 1.7)
  - §6.4.10 §B.4 加 regulatory_risk required field(rev 2.0,contract_version: req-contract-v2)
  - 自動 generate 2 個 active project(team-account / nfc-poc)的 migration PR 草稿
  - decision-log: D-contract-change-001 / 002 / 003 拍板紀錄
  - state.md outstanding_blockers 自動加 v1→v2 migration deadline tracking
  - PM Skill version 自身升至 contract-pack-v1.1

📍 後續追蹤:
  $ /pm contract-change status              # 看 migration 進度
  $ /pm contract-change rollback --change 2 # 萬一 Change 2 出問題可在緩衝期 rollback
```

### 萬一 Change 2 試了 3 週發現工程師強烈反對

```bash
$ /pm contract-change rollback --change 2 --reason "team feedback: regulatory_risk 對非合規地區 PJ 是純負擔"
```

```
🔄 Rollback Change 2 — req-contract-v2 → v1

⚠ Impact check:
  - team-account 已 migrate 10 / 25 REQ → 自動補 reverse migration
  - nfc-poc 已 migrate 全 12 REQ → 自動補 reverse migration
  - decision-log: D-contract-rollback-001 紀錄(含完整 reason)

📊 Rollback 完成,團隊 0 額外負擔。

🔍 lessons learned auto-append:
  - 加 regulatory_risk 應該對齊 project-level opt-in,不是 contract-level required
  - 已加進下次 contract change proposal wizard 的「警示模式」

→ 對齊 §10.7 失敗退路設計:**任何階段不滿意立刻停損**(這次是 contract-level stop loss)。
```

### 半年後:Contract Evolution Report

王經理跑:

```bash
$ /pm contract-change history --window 6months
```

```
📊 Contract Evolution Report(2026-Q3+Q4)

✅ Successful changes: 8
  - 5 patch(全自動 commit,0 friction)
  - 2 minor(rev x.y bump,1 週 ack 緩衝)
  - 1 major(req-contract-v1→v2,12 週 deprecation 全 project 成功 migrate)

❌ Rolled-back changes: 1
  - Change 2 regulatory_risk:3 週後 rollback(team feedback drove decision)
  - 對齊 §10.7 stop loss 設計

📈 PM Skill 自身演化健康度
  - 6 個月內 9 個 contract changes,平均 ack 時間 1.4 天
  - rollback rate: 11%(對比公開 OSS framework deprecation 經驗值,eg. semver / Kubernetes API 退場 rate 通常 < 30%;本 11% 為健康水準)
  - 全 active project 無 contract drift incident

🎯 結論: PM Skill 演化能力 work as designed。
```

### 重點 takeaways

- ✅ **PM Skill 不是 frozen tool,可隨用隨進化**(對齊 §6.4.13 governance + §6.4.11 §I Contract Version Independence)
- ✅ **patch / minor / major 自動分類** — PO 不需想清楚是哪一級,wizard 幫判
- ✅ **影響評估自動掃全 active project** — 不再「我以為沒影響結果 3 個 project 都壞」
- ✅ **12 週 deprecation timeline 強制** — 對齊 §6.4.13 governance,避免「明天就強制全部 migrate」災難
- ✅ **Contract rollback 對齊 §10.7 stop loss** — 試了不對立刻收回,**0 額外負擔**
- ✅ **完成 enterprise 鐵三角**:
  - 場景 12 跨 **project** 橫展
  - 場景 13 跨 **人**(team 變動)
  - **場景 14 跨時間(系統本身演化)** ← 回答老闆「3 年後 PM Skill 還能用嗎?」
- ✅ **Audit trail 完整**:每個 contract change + rollback 都進 decision-log + Evolution Report

---

## 🎬 場景 15:Phase 4 中途接到 customer 新需求 — 從接單到 done 全程

### 情境

訂閱專案做到 Phase 4 Day 10(共 14 天預計)。陳董打電話來:

> 「客戶 A 公司簽約後加碼:他們要求支援 SSO 用他們公司 LDAP server 登入。**這個必須跟著本次 release 一起上** — 是合約條件。」

過去的痛苦:
- 王經理腦中跑 30 個問題:這要寫哪個 module?誰有空?上線日要延嗎?既有 spec 凍結了能改嗎?如果 push 不動客戶怎辦?
- 開 1 小時緊急會議 + 又開 1 小時跟 dev team 對焦 + 自己半夜重排 timeline → 2 天後才有答案
- **2 天的 dead-air 客戶覺得我們不專業**

現在王經理立刻坐下打:

```bash
$ /pm new-requirement \
    --from "customer A 簽約加碼" \
    --description "支援 SSO 用客戶 LDAP server 登入" \
    --deadline "本次 release(Phase 6 不延)"
```

### PM Skill 回應(自動分析)

```
🆕 New Requirement — 中途接單分析

讀完描述後我自動 atomize 成 atomic REQs(對齊 §6.4.10 §B.4 schema):

📋 推導出的 atomic REQ(草稿,你 review):
  REQ-NEW-001: LDAP 配置介面(管理者可填 LDAP server URL / DN / 密碼)
  REQ-NEW-002: SSO 登入流程(用 LDAP 認證取代帳號密碼)
  REQ-NEW-003: SSO session 管理(token / refresh / 登出)
  REQ-NEW-004: SSO 帳號自動 provisioning(首次登入自動建 profile)
  
  ⚠ 需 PO 確認:
    - 是否需 fallback 到既有密碼登入?(若 SSO 掛了)
    - 多個 LDAP server 是否支援?(客戶 A 答覆不一定有多 server)
    - 同個 LINE user 已綁定既有 profile,SSO 後如何 merge?

🧐 Module-fit 自動分析:
  
  既有 5 module 中找最適配:
    - module-shared-identity-binding ✅ 最匹配
      理由:此 module 已 handle identity 綁定邏輯 + cross_cutting REQ-010
      影響:擴展 scope,owner(小芬)需評估
    - module-package-management ❌ 不適配(套餐邏輯,跟 SSO 無關)
    - module-billing ❌ 不適配
    - module-quota-enforcement ❌ 不適配
    - module-promo ❌ 不適配
  
  Option A: 加進 module-shared-identity-binding(現有)
  Option B: 切新 module-sso(獨立)
  
  📊 trade-off:
    Option A pros: 跟既有 identity 邏輯耦合,維護單一 owner
    Option A cons: module 變大,小芬負擔 +30%
    Option B pros: SSO 邏輯清晰獨立,後續其他客戶易借鏡
    Option B cons: 新 module 需重跑 Phase 1 mini(切割 + dependency + 設 owner)
                  + 跟 module-shared-identity-binding 跨模組 dependency 增加
  
  📍 我推薦 Option A,理由:
    1. SSO 本質是 identity binding 的特殊情形,語意上同屬一 domain
    2. Phase 4 Day 10 重切 module 成本高(對齊 §6.4.11 §B size cap)
    3. 跟既有 REQ-010 cross_cutting 自然延伸

👥 Capacity & Assignment 分析(從 functional.md status + 過去 14 天 commit rate):
  
  - 小芬(module-shared-identity-binding owner):
    當前進度 4/4 features done ✅ ahead of schedule
    domain 熟:identity binding ✅✅(過去 12 個 commits 含 identity 關鍵字)
    Phase 4 剩 4 天 capacity 估 ~16 工時
    LDAP 經驗 evidence:過去 commit log grep "ldap|saml|sso" 結果 0 commits
      → 需 Tech Lead 阿明手動確認 skill level(對齊 Round 3 C1 fix)
    推薦:小芬主導 + 阿明(Tech Lead)pair LDAP 部分(待阿明 confirm)
  
  - 小華 / 阿凱:commit log grep LDAP 關鍵字 0 commits + module 不匹配
  - 阿明 Tech Lead:commit log 含 "saml/sso/ldap" 8 commits → 建議 pair 角色(Tech Lead 仍需自我確認 capability)

⏱ Timeline 影響評估:
  
  REQ-NEW-001~004 估 ~20 工時(含 TC 寫 + 整合測試)
  小芬 + 阿明 pair,Day 10-14(4 天 × 5 人天 = 20 人天)→ 剛好塞進 Phase 4
  
  ⚠ 風險:
    - 若 LDAP server 配合度不佳(對接時程 unpredictable)→ 可能延 1-2 天
    - 既有 4 features 100% done 才有 capacity 接,不可同時開
  
  📊 建議 release 信心度:
    - 65% 不延 deadline
    - 25% 延 1-2 天(可吸收於 Phase 5 整合期間)
    - 10% 延 > 3 天(觸發 Phase 6 stop loss 對話)

📜 Contract considerations:
  
  ⚠ 此 REQ 為 Phase 0 之後新增,違反「Phase 0 Exit 後凍結」原則
  → 需走 §6.4.10 §L Contract Override mechanism:
    - applies_to: §6.4.10.B Phase 0 frozen-spec invariant
    - override_reason: "客戶 A 簽約加碼,陳董已承諾 release 帶上"
    - deviation: 4 atomic REQ 加在 Phase 4 mid-flight
    - 自動 PO ack required(對齊 §6.4.10.L.2 50%+ deviation)

🎯 拍板?
  [a] accept Option A(module-shared-identity-binding 擴展)+ 小芬主接 + 阿明 pair
  [b] accept Option B(新建 module-sso)— Phase 1 mini 重跑
  [c] 拒絕加碼 — 跟陳董談 push 回客戶(對齊 stop loss)
  [d] 自訂(eg. 改派 / 改 module 切法 / 加 fallback REQ)
> a
```

王經理拍 a。

### PM Skill 自動執行

```
✅ 已落地:

📋 Requirement Spec 更新(rev .5 mid-flight 增量):
  - 加 4 個 REQ-NEW-001~004(對齊 §6.4.10 §D schema 9 必填欄位)
  - 自動填 derived_from / source_evidence / priority(P0,deadline 限定)
  - cross_cutting_reqs 標記(LDAP 觸及 module-shared-identity-binding + 可能 module-package-management 升級觸發)
  - Glossary 自動加 6 個 LDAP 相關術語(DN / OU / SAML / IdP / SP / SSO session)

📋 _plan.md 更新:
  - module-shared-identity-binding.covers_reqs append [REQ-NEW-001..004]
  - module-shared-identity-binding.estimated_size: medium → large
  - dependency_graph: 新增 LDAP 外部 system dependency
  - shared_files: 加 LDAP client lib(對應 §6.4.11 §D shared_infra)

📋 functional.md(module-shared-identity-binding)新增 4 features:
  - F-shared-NEW-001~004(對齊 §6.4.11 §C.2 schema)
  - status: ⏳ planned
  - assignee: 小芬 + 阿明(pair)
  - estimated_completion: 2026-06-30(Phase 4 last day)
  - dependencies.blocked_by: F-shared-001(已 done,可立即開工)

📋 Contract Override 記錄(對齊 §6.4.10 §L):
  - D-override-mid-flight-001: Phase 0 frozen spec breach
  - reason: customer A 簽約加碼
  - ack: PO 王經理 @ 2026-06-27T11:00:00
  - cross-impact: Phase 4 timeline 65% 信心度
  - revisit_at: Phase 5 整合期間 check(若延 1+ 天)

📋 通知小芬 + 阿明(透過 Slack integration):
  - 「您接到新 features F-shared-NEW-001~004
     建議讀:Requirement Spec rev .5 + LDAP basics + 阿明 pair 安排 14:00 起跳」
  - 阿明 Slack auto: 「需 14:00-17:00 跟小芬 pair LDAP setup」

📊 Phase 4 timeline 重算:
  - 原:Phase 4 結束 2026-06-30
  - 新:Phase 4 結束 2026-07-02(2 天 buffer 含風險)
  - 已自動通知陳董:「release 信心度 65%,我們會盡力不延」

⏱ 下一步:
  $ /pm status              # 看 Phase 4 重算後 timeline
  $ /v2 status module-shared-identity-binding  # 看新 features 狀態
```

### 小芬視角(下午 1:55,proactive 接到)

小芬看到 Slack:

```bash
$ /v2 start task F-shared-NEW-001
```

PM Skill / V2 SKILL 回應:

```
🛠 V2 implementation — task F-shared-NEW-001(LDAP 配置介面)

讓我幫你準備工作環境:

✅ 讀 functional.md F-shared-NEW-001 entry:
   - derived_from: REQ-NEW-001
   - acceptance(3 條,machine-checkable):
     1. 管理者填 LDAP URL / DN / 密碼後,API 連線測試成功 → 存設定
     2. 設定無效時 UI 顯示具體錯誤(URL 不通 / DN 格式錯 / 認證失敗 各 case)
     3. 設定後 SSO 流程 (F-shared-NEW-002) 可讀此設定

✅ 自動 generate tests.md 草稿:
   - TC-shared-NEW-001: LDAP 連線測試 happy path
   - TC-shared-NEW-002: 各種錯誤 case
   - TC-shared-NEW-003: 設定可被 F-NEW-002 讀

⚠ 跨模組 / 跨外部 dependency:
   - 依賴外部 LDAP server(客戶 A 提供 test env URL: ldap://staging.customer-a.com)
   - 阿明 14:00 來 pair,他有 LDAP 經驗

🎓 LDAP 速成包(已自動 inject organizational knowledge):
   - memory: backend_change_rule(對應加 Python LDAP lib 需 PO 同意)
   - 業界 LDAP basics 摘要(5 min 讀)
   - 既有訂閱專案無 LDAP 經驗,本 feature 為先例 → 試跑結果會 feed 回下 project

💡 開工?
   → status: ⏳ planned → 🟡 in-progress
> y

✅ functional.md 已 update。
   阿明會在 14:00 自動 ping 你開始 pair。

⚠ Backend dep 提醒(對齊 memory: dep_management hard rule):
   若需新增 python-ldap package → 必先寫 propose(用途 + Azure Linux 3.0 相容性)+ PO 拍板
```

### 隔天王經理視角

```bash
$ /pm daily
```

```
☀ Daily Briefing — 2026-06-28(Phase 4 Day 11)

📊 整體進度
  - 25 REQs total + **4 mid-flight REQs**: 12 ✅ done / 13 🟡 in-progress / 4 ⏳ planned
  - Burndown: timeline 重算後仍 65% 信心度,目前 on track

🆕 Mid-flight REQ tracking(對齊 §6.4.10 §L Override audit)
  - F-shared-NEW-001(LDAP 配置介面):🟡 in-progress(小芬 + 阿明 pair 中,Day 1)
    昨 14:00 pair 完成,小芬今早 commit 2 個 progress
    LDAP test env 連線 OK ✅
  - F-shared-NEW-002~004:⏳ planned(Day 2-4 排)
  - 風險信號:無

👥 Team Status
  - 小芬:既有 4 done + 新接 4 features → 5/8 features done(53%)正常 ramp-up
  - 阿明 pair 中: 14:00-17:00 投入 LDAP
  - 小華 / 阿凱:既有 module 正常

🚨 Anomalies: 0
🧪 Flaky test watch: 1/15 全 project,1/3 module-shared-identity-binding(LDAP 連線抖動已標 flaky,觀察中)

📍 Today's Top action:
  1. 14:00 pair 第 2 天 — 預計完成 F-shared-NEW-001 + 開工 F-NEW-002
  2. 對 LDAP test env 不穩定(已 1 次 flaky),準備 fallback to mock
```

### 4 天後 — 客戶需求 done

Phase 4 Day 14,小芬跑:

```bash
$ /v2 done F-shared-NEW-004
```

```
🎉 F-shared-NEW-004 完成 — 6 條三向 invariant 全 pass

✅ 全 4 個 mid-flight features 已 done:
   - F-shared-NEW-001 ✅ done(2026-06-29)
   - F-shared-NEW-002 ✅ done(2026-06-30)
   - F-shared-NEW-003 ✅ done(2026-07-01)
   - F-shared-NEW-004 ✅ done(2026-07-02)

📊 Phase 4 結束信心度回升至 92%(超 65% 預估)
   實際延 2 天(原 6/30 → 7/02),仍在 buffer 內

📍 自動 trigger:
   - functional.md status 全 ✅ done
   - 阿明 pair 結束,小芬獨立 maintain LDAP 部分
   - decision-log: D-mid-flight-completion-001 紀錄完整 audit
   - Phase 4 gate-check ready(對齊 §6.4.11 §E.7)
   - 王經理 daily briefing 明早自動 surface:「Phase 4 可 advance」
```

陳董打給客戶 A 公司:「SSO 已落地,如期 release。」

### 重點 takeaways

- ✅ **中途接單從 2 天 dead-air → 30 分鐘拍板** — atomize / module-fit / capacity / timeline 全自動分析(前言 evidence basis;auto 行為 medium tier,fallback 對齊 §Confidence Tier)
- ✅ **Module-fit 自動推薦 + 給 trade-off**(現有擴展 vs 新建)— PM 不用腦補,有 evidence-based suggestion
- ✅ **Capacity check 看 domain skill + 當前 capacity** — 不再「我以為小芬有空結果她滿載」
- ✅ **Phase 0 frozen 違反走 §6.4.10 §L Override** — 不是 bypass,是合法 deviation + audit trail
- ✅ **Timeline 重算附信心度 %** — 老闆 / 客戶 get 「65% 不延」具體訊息,不是「應該可以」
- ✅ **memory + organizational knowledge inject 對 mid-flight 同樣 work** — LDAP basics + 跨 dep 規則自動 inject
- ✅ **Pair programming 自動觸發 + 通知** — Tech Lead 不需手動排,SKILL 偵測 capability gap 自動建議
- ✅ **完整 closed-loop**:接單 → 拍板 → 開工 → 每日追蹤 → done → Phase Gate 自動 propagate

---

## 📚 附錄 A:完整命令速查表

### Phase / Lifecycle 命令

| 命令 | 用途 |
|:---|:---|
| `/pm init "<project>" [--type production\|training\|poc\|sandbox]` | 啟用 PM Skill,建立 `docs/pm/<project>/` per-project subfolder + 共用 `_org/`;`--type` 預設 production(對齊 Round 6 lifecycle fix)|
| `/pm use "<project>"` | 切換 active project context(多 project 並行時用)|
| `/pm start "<project>"` | 進入 Phase 0(可選 `--from-verbal-brief`)|
| `/pm status [--project <X>]` | 查當前 Phase + state(預設 active project)|
| `/pm advance-phase <N>` | 進下個 phase(需 signoff)|
| `/pm signoff phase-N --approver <X>` | 階段簽核 |
| `/pm gate-check <phase>` | 跑 phase 對應 acceptance criteria |

### Project Lifecycle 管理命令(對齊 Round 6 PO fix — 練習 / 教育訓練 sandbox 清理)

| 命令 | 用途 |
|:---|:---|
| `/pm list` | 列出 active projects(per-project subfolder + state)|
| `/pm list --archived` | 列出已 archive 的 projects |
| `/pm list --filter "<pattern>"` | pattern match(eg. `training-*`)|
| `/pm archive "<project>" [--reason "..."]` | 🟢 Soft delete:move to `docs/pm/_archive/<project>/`,留 7 天可 restore;production 必填 reason |
| `/pm restore "<project>"` | 🟡 緩衝期內(7 天)從 archive 移回 active |
| `/pm delete "<project>" --force --reason "..."` | 🔴 Hard delete(真 rm):production type 預設 reject 必 `--force` + 必 reason + 過去 7 天無 commit confirm |
| `/pm archive --filter "<pattern>" --confirm` | Bulk archive(eg. 教育訓練收尾)|
| `/pm delete --filter "<pattern>" --force` | Bulk hard delete;必先 list match → user 二次確認 |

**Project Type 對應行為:**

| Type | delete 安全性 | scaling 對齊 | 預設 expiry |
|:---|:---|:---|:---|
| `production` | 預設 reject,需 `--force` + 7 天無 commit | §6.4.10 §C standard | 無 |
| `training` | 可直接 `/pm delete` 不需 force | small spec fast-track | 30 天 auto-archive |
| `poc` | 需 `--force` 但 reason 寬鬆 | small spec fast-track | 90 天 auto-archive |
| `sandbox` | 可直接 delete | small spec fast-track | 30 天 auto-archive |

**Audit trail:** 所有 archive / delete / restore 寫入 `docs/pm/_org/org-decision-log.md`,不可繞過。
**Phase 4+ active project archive 限制:** 拒絕 archive,需先走 §10.7 stop loss 流程明示放棄。

### Reporting + Cross-Project 命令

| 命令 | 用途 |
|:---|:---|
| `/pm daily` | 每日 1 頁 briefing(自動 include 全 active project)|
| `/pm weekly` | 每週 digest |
| `/pm health-check` | 整體健康度 |
| `/pm kpi-eval` | KPI 評估(對齊 §7.5 KPI 表) |
| `/pm dashboard` | 多 project 橫向 view + cross-project anomaly(對齊場景 12)|
| `/pm onboard <engineer> --replace-for <X> --module <M>` | 新工程師 onboarding pack(對齊場景 13)|
| `/pm offboard <engineer> --next-project <Y>` | 工程師離開 / 轉組 + hand-over 三向 invariant 驗證 |
| `/pm contract-change propose` | 啟動 contract change wizard(對齊場景 14 + §6.4.13)|
| `/pm contract-change status` | 看當前 migration 進度 |
| `/pm contract-change rollback --change <N> --reason "..."` | 緩衝期內 rollback contract change(對齊 §10.7 stop loss)|
| `/pm contract-change history --window <N>months` | Contract Evolution Report |
| `/pm new-requirement --from "..." --description "..." --deadline "..."` | 中途接單分析 wizard(對齊場景 15)|
| `/pm requirement impact-analysis <REQ-id>` | 看單 REQ 對 module / capacity / timeline 影響 |
| `/pm assign-feature <feature-id> --to <engineer> [--pair <X>]` | 手動指派 feature(覆寫 SKILL 推薦)|
| `/pm cross-project sync-decision [--from --to --decision --reason]` | 跨 project 同步 PO 拍板;flag 省略時 interactive prompt(對齊場景 12 方式 B)|
| `/pm cross-project resource-check` | 偵測工程師 over-allocated |
| `/pm cross-project common-pattern` | 偵測 N project 都遇到的問題 |
| `/pm org-retrospective --window <N>months` | Org-level retrospective + lessons aggregation |

### Validator 命令(對齊 §6.4.11 §J.1)

| 命令 | 用途 | Phase |
|:---|:---|:---:|
| `/pm validate-req-spec <path>` | 對齊 §6.4.10 contract | 0 |
| `/pm validate-module-plan <path>` | 對齊 §6.4.11.B | 1 |
| `/pm validate-module-spec <module>` | per-module | 2 |
| `/pm validate-module-spec --all` | 全 module batch | 2 |
| `/pm validate-shared-infra` | shared infra 完整性 | 3 |
| `/pm validate-implementation <module>` | per-module 三向 invariant | 4 |
| `/pm validate-implementation --all` | 全 module batch | 4 |
| `/pm validate-integration` | E2E + Perf | 5 |
| `/pm validate-release` | deploy + rollback rehearsal | 6 |
| `/pm validate-post-launch` | KPI + retro 完整性 | 7 |
| `/pm validate-all` | Master 跨 phase + lineage | 全 |

### Review + Bug-review 命令

| 命令 | 用途 |
|:---|:---|
| `/spectra-review <path>` | 跑 spectra-review(對應 contract 對齊 §6.4.3) |
| `/spectra-review <path> --lite` | 簡潔版(對齊 既有 SKILL Lite Mode)|
| `/pm-bug-review <target-slug>` | 走 finding 拍板 |
| `/pm-bug-review <slug> --finding <id>` | 單 finding 拍板 |
| `/pm-bug-review <slug> --pending-only` | 只看未拍板 |
| `/pm-bug-review <slug> --overrides-only` | review 既有 overrides |

### V mode SKILL 命令(對齊既有)

| 命令 | 用途 | SKILL |
|:---|:---|:---:|
| `/v1 plan-task <task>` | 寫 task plan | V1 planning |
| `/v2 start task <feature>` | 開工 feature | V2 implementation |
| `/v2 done <feature>` | 完成 + 跑三向 invariant | V2 |
| `/v2 blocker <feature> --reason "..."` | 工程師主動 surface 阻塞(對齊場景 5b)| V2 |
| `/v2 status <module>` | 查 module 當前 features / tests / 最近 commits(對齊場景 13)| V2 |
| `/v8 cross-module-review` | 跨模組 review | V8 |

---

## 📚 附錄 B:18 個情境快速索引

| 情境 | 對應 Phase | 章節 |
|:---:|:---:|:---|
| 0. 啟用 PM Skill | — | §場景 0 |
| 1. Project Kick-off | 0 | §場景 1 |
| 2. spectra-review + 拍板 + fix | 0 | §場景 2 |
| 3. Gate-check + Phase 切換 | 0→1 | §場景 3 |
| 4. 模組切割(V7)| 1 | §場景 4 |
| **5a. 工程師接到任務(V2 start)** | 4 | §場景 5a |
| **5b. 工程師遇 blocker → 主動 surface** ⭐ | 4 | §場景 5b |
| **5c. V2 done + 三向 invariant 自動 sign-off** | 4 | §場景 5c |
| **6a. PM 早上 Daily Briefing** | 4 | §場景 6a |
| **6b. PM 對 anomaly 採取行動 + Follow-up loop** ⭐ | 4 | §場景 6b |
| 7. 跨組衝突早期 surface(V8)| 2/4 | §場景 7 |
| 8. Gate-check 卡關救援 | 4→5 | §場景 8 |
| 9. Integration + Release | 5/6 | §場景 9 |
| 10. Post-launch + Retro | 7 | §場景 10 |
| 11. 跨 project 經驗累積 | next 0 | §場景 11 |
| **12. 多 project 並行 + Org-Level View** ⭐ | 全 | §場景 12 |
| **13. 新工程師 onboarding + 接替交接** ⭐ | 全(team 變動)| §場景 13 |
| **14. PM Skill 自己升級(contract change)** ⭐ | 全(系統演化)| §場景 14 |
| **15. Phase 4 中途接 customer 新需求 — 從接單到 done** ⭐ | 4 | §場景 15 |

---

## 📚 附錄 C:常見問題(FAQ)

### Q1: PM Skill 要錢嗎?
A: 不要 — 全 file-based 在你本地 repo。Claude 用量計入既有 Claude Code 訂閱(已有)。

### Q2: 工程師可以 bypass PM Skill 直接 commit 嗎?
A: 可以,但 daily briefing 會 surface anomaly(eg. functional.md 沒 update)。**PM Skill 不阻擋,但讓 bypass 透明可見**。

### Q3: 規格寫到一半 Claude 給的 default 數字我不認同怎辦?
A: 跑 `/pm-bug-review` override + 寫 reason。對齊 §6.4.4 Default vs Override Trust Hierarchy。

### Q4: 一個 project 跑完,文件累積很多怎辦?
A: 各 project 文件本身就在 `docs/pm/<project>/` per-project subfolder 內(對齊 Round 5 path fix)。結案後跑 `/pm archive "<project>"`(對齊 Round 6 lifecycle 命令)歸檔至 `docs/pm/_archive/<project>/` 釋放工作 namespace,source repo 不會膨脹。下個 project 從 `/pm init` + `_plan.md` 開始新一輪。

### Q5: 如果中途想停損(eg. Phase 3 發現方向錯誤)?
A: `/pm advance-phase` 跳不過去就是 stop loss 點。對齊 §10.7 失敗退路。前 phase audit trail 全保留,不浪費。

### Q6: 我團隊有 3 人 / 7 人 / 15 人,PM Skill 都適用嗎?
A: 適用。Phase 1 module-splitting 自動依規模調(2-10 個 module)。15 人通常切 5-7 個 module,2-3 人共享 module(對齊 §6.4.11.B.3 module_count_in_range)。

### Q7: spectra-review 跑很多輪會不會無限迴圈?
A: 不會。§6.4.10 §B.1 convergence rule:連續 2 輪 0 new BLOCKER + 0 new CONCERN 就自動收斂。標準 spec 通常 3-5 輪。

### Q8: PM Skill 跟 Jira 衝突嗎?
A: 不衝突。Jira 可保留為「老闆儀表板 UI」,PM Skill 是「真實的進度推導引擎」。daily briefing 可以同步推到 Jira(若需要)。

### Q9: 練習 project / 教育訓練 sandbox 如何清理?(對齊 Round 6 PO fix)
A: 跑 `/pm init "<project>" --type training`(或 `sandbox` / `poc`)→ 標記為非 production,delete 不需 `--force`。培訓結束後可:
- 單個:`/pm archive "<project>"` 留有價值 lesson,或 `/pm delete "<project>"` 直接清理
- 大量:`/pm delete --filter "training-*" --force`(必先 list match 二次確認)
- 自動:training/sandbox 預設 30 天自動 archive(對齊附錄 A Project Type 表)
全程 audit trail 寫入 `docs/pm/_org/org-decision-log.md`。

### Q10: 不小心 archive / delete 錯 project 怎辦?
A: archive 有 **7 天緩衝期**,跑 `/pm restore "<project>"` 移回 active。Hard delete 後 7 天內若有 git commit 仍可從 git 還原(對齊既有 git workflow)。Production project 預設 reject `/pm delete` 需 `--force` + 過去 7 天無 commit confirm,雙重防誤刪。

---

## 修訂歷程

| 版本 | 日期 | 變更 |
|:---:|:---|:---|
| 1.0 | 2026-06-17 | 初版使用手冊,11 個情境 + 4 個附錄;對齊 pm-skill-proposal.md rev 1.5 |
| 1.1 | 2026-06-17 | spectra-review Round 1 fix(C1+C2+C3+N1-N5 全 fix):場景 4/10 對齊 §6.4.11 §J.1 命名規約(去除 ad-hoc `/pm phase-N <activity>`);場景 8 對齊新加 §E.4a Flaky Policy(走合法 flaky path 非 bypass);場景 5 加 F-pkg-001 跨模組 dependency 鋪陳;場景 0 加 `/pm help` output 範例;前言加時程估算 evidence basis;場景 11 加 lessons inject source(audit-archive/retrospective + decision-log + memory)+ 雙 dramatic Override(rounds_min 3→1 + nits_max 5→8);場景 1 Glossary 5→8 term。Round 2 verify verdict=ship-as-is。2 輪累積 fix_rate=100% / Net saving=10.2。對齊 pm-skill-proposal.md rev 1.6 |
| 1.2 | 2026-06-17 | 擴展手冊深度:場景 5 拆 5a/5b/5c(加 blocker surface 流程 + V2 done invariant fail 修復路徑);場景 6 拆 6a/6b(加 1-on-1 follow-up loop 完整 demo);新增場景 12 「多 project 並行 + Org-Level View」(`/pm dashboard` 多 project 橫向 + cross-project anomaly + `/pm org-retrospective`);附錄 A 加 `/pm dashboard` / `/pm cross-project sync-decision` / `/v2 blocker` 等 5 新命令;附錄 B 索引 11 → 15 情境 |
| 1.3 | 2026-06-17 | 新增場景 13「新工程師 onboarding + 接替交接」— PO/Tech Lead/離職工程師/新人 4 視角 demo,個人化 onboarding pack(必讀清單 + unresolved + 該找誰 + Day 1-3 路徑 + memory inject)+ `/pm offboard` 三向 invariant hand-over;附錄 A 加 `/pm onboard` / `/pm offboard` / `/v2 status` 命令;附錄 B 索引 15 → 16 情境;解新人 ramp-up 1-2 週 → 1-2 天的痛點(對齊 §六商業價值) |
| 1.4 | 2026-06-17 | 新增場景 14「PM Skill 自己升級 — Contract change governance」— `/pm contract-change propose` wizard(自動分類 patch/minor/major + 影響評估全 active project + 12 週 deprecation migration timeline)+ `/pm contract-change rollback`(緩衝期內 stop loss 對齊 §10.7)+ Contract Evolution Report(半年累積健康度);附錄 A 加 4 個 `/pm contract-change` 命令;附錄 B 索引 16 → 17 情境;完成 enterprise 鐵三角(跨 project + 跨人 + 跨時間)|
| 1.5 | 2026-06-17 | 新增場景 15「Phase 4 中途接 customer 新需求 — 從接單到 done 全程」— `/pm new-requirement` wizard(atomic REQ 分解 + module-fit 推薦含 trade-off + capacity 含 domain skill 評估 + timeline 含信心度% + Phase 0 frozen 走 §6.4.10 §L Override audit trail)+ 小芬 V2 開工含 LDAP 速成包 + 4 天 closed-loop daily tracking demo;附錄 A 加 `/pm new-requirement` / `/pm requirement impact-analysis` / `/pm assign-feature` 3 命令;附錄 B 索引 17 → 18 情境;解中途接單 2 天 dead-air → 30 分鐘拍板 痛點 |
| 1.6 | 2026-06-17 | spectra Round 3 fix(C1+C2+N1-N5 全 fix):前言加 Auto Behavior Confidence Tier callout(3 級 + fallback policy)解 C2 over-promise risk;場景 15 capacity 分析改 evidence-based commit log 解 C1 domain skill ☆☆☆☆☆ schema 漂移;場景 13 /pm offboard 加 half-done features 4 步處理;場景 14 業界 cite 改 OSS framework / 加 active_contract_version 機制;場景 12 sync-decision 加 interactive prompt 方式 B;時程估算 evidence ref 落地。Round 4 verify verdict=ship-as-is。4 輪累積 fix_rate=100% / Net saving=19.3 |
| 1.7 | 2026-06-17 | **Round 5 PO Architectural Fix(spectra 漏抓)**:全面改 per-project subfolder 結構 `docs/pm/<project>/` + 新加 org-level shared 區 `docs/pm/_org/`(org-roster / org-decision-log / org-retrospectives / contract-pack)。場景 0 `/pm init` 從無參數改為必帶 project name;場景 11 加 `/pm init "team-account"` 第 2 個 project 不衝突 demo;場景 12 dashboard 顯示讀 `docs/pm/*/state.md`;場景 13 onboarding source 改 per-project path;場景 14 contract-pack 改寫進 `_org/contract-pack/`;附錄 A 加 `/pm use "<project>"` 切換命令 + 更新 `/pm init "<project>"` 必帶簽名;FAQ Q4 改為 archive 路徑說明。**對齊 §6.4 contract path 預計同步補強為 Phase E 落地時鎖定。 |
| 1.8 | 2026-06-17 | **Round 6 PO Lifecycle Fix(Option B 精簡版)**:附錄 A 加 Project Lifecycle 管理命令段(`/pm list` / `/pm archive` / `/pm restore` / `/pm delete` + bulk `--filter` + `/pm init --type` flag);Project Type 對應行為表(production/training/poc/sandbox 各自 delete 安全性 / scaling / auto-expiry);7 天 archive 緩衝 + Phase 4+ archive 拒絕 + production 雙重防誤刪 audit trail;FAQ Q4 更新為 `/pm archive`;新增 Q9(練習 / 教育訓練 sandbox 清理)+ Q10(誤 delete 救援)。解 PO 「教育訓練 project 累積」use case。 |
