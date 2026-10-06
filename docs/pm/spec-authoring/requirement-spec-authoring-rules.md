# Requirement Spec Authoring Rules

> **Owner:** PM(spec authoring governance)
> **Status:** Draft
> **Spec-Version:** 2026-08-12.0
> **Last Updated:** 2026-08-12
> **Role:** L3 Primary — requirement spec 的 **create / update / delete** 唯一 authoring 規則書
> **Authors:** PO(kuohsuming)+ Claude(co-author)

---

## 1. Purpose

定義 Claude(及任何 AI 工具)在 **建立、更新、刪除 requirement spec** 時**必須嚴格遵守**的規則。這份是「可逐條打勾」的執行規則書,不是論述。

- 論述 / framework 層(WHY 5 spec)→ 見 `docs/pm/5-spec-authoring-framework.md`
- 通用 spec 完整性標準(M1–M5)→ 見 `docs/ddd-doc-maintenance.md §7`(本檔**繼承**,不重造)
- 本檔專注:requirement 層的 authoring 規則 + 三元組不變式 + CRUD 行為

> **本檔是 requirement spec authoring 的唯一 Primary。** 其他文件(§7 完整性標準、framework §3.1、`_spec-template.md`)若涉 REQ authoring,應指向本檔,不得另立平行裁決(One Topic, One Primary — `ddd-doc-maintenance.md §3.1`)。

> **⭐ REQ 恆存在(2026-07-05,D-035;5 份 spec 不可省略)**:REQ 是 5-spec 家族的根,永遠寫,無 tier 省略。tier 只控**深度**(framework §6)。**最小地板(floor)= 三元組(1 golden `G1` + ≥1 anti `A1`)**;簡單 feature 寫到此即合格,但不省。

---

## 2. Scope

### ✅ In-scope
- requirement spec 的 create / update / delete 規則
- REQ ⇄ Golden Scenario ⇄ Anti-example 三元組不變式 + **claim-ID 機制(§3.4,下游追溯共同單位)**
- decision-time(討論結論)+ write-time(動檔)兩段式 gate
- 觸發點:V4 建/改 spec、PM skill phase 0/1、任何階段的維護

### ⛔ Non-goals
- Test Plan / Functional / Test Cases / Design spec 的 authoring 規則(各自未來另立 rulebook)
- validator / machine-checkable schema 硬 gate(列為後續 phase,見 §12;現階段為 rulebook-first 軟約束)
- 取代 `ddd-doc-maintenance.md §7` 的通用 M1–M5(本檔繼承之)

---

## 2.5 Requirement Admission Gate（候選需求准入閘門）

> **兩階段模型的第一階段**:判斷「候選需求該不該收 + priority」,發生在 §3 三元組 / §4 authoring **之前**。
> 現有規則講「怎麼寫好一個需求」(§3/§4);本節講「這候選是否真實、該不該收、priority 多少」。
> **輸入**:人給的片段,或 §5.4 Coverage Expansion 舉一反三的 ~3 候選。

### 2.5.1 五項准入測試

| # | Test | 判準 | 失敗去處 |
|---|---|---|---|
| **T1 可追溯** | 指得出對應 user need / 業務目標 | → Open Questions |
| **T2 有證據** | 真實回報 / 資料,非「未來可能」 | → Open Questions |
| **T3 值得寫** | 頻率 × 影響夠高 | → Out of Scope |
| **T4 是 what 非 how** | 不含實作細節 | → 反推 what 重塑 / 降 Design 層 |
| **T5 有必要** | 不做會出事 | → Out of Scope |

⭐ **T3 carve-out**:**安全 / 資料完整 / 法遵**類需求**免 T3**(freq×impact 再低也收)。
**機械判定 marker(C3 fix)**:此類以 per-REQ metadata `risk_class: safety | data | compliance` 標記(§B.4 optional field);未標 = 預設 `normal`。`risk_class != normal` 即 high-stakes(§5.5.2 floor 據此判定)。

### 2.5.2 路由（失敗不同 test → 不同去處）

- **T1 / T2 fail**(不確定,可能真)→ **Open Questions**(待證據再議,revivable)
- **T3 / T5 fail**(拒收)→ **Out of Scope**(附理由,revivable)
- **T4 fail**(錯類 — 它是 how 非需求)→ 反推底層 what 重塑;或它屬 **Design spec**(非 REQ)
- **全 pass** → 進 §3 三元組 + §4 authoring

> 路由去處(Open Questions / Out of Scope)皆為 §template 既有 section + **revivable holding**,非墳墓(見 §5.5.3)。

### 2.5.3 適用範圍 + PO override

- 閘門**一律套**（含人明確要求的需求 —— 也須過 T1/T2/T5)
- **PO 可 override**(強制收 / 強制拒),override 記 decision-log,不 silent
- 閘門是「強制檢視」非「強制否決」

### 2.5.4 Priority 統一來源

- **T3 的 freq × impact 評分同時決定「收不收」+ `P0/P1/P2`**(統一 §4 checklist R3 priority 來源,不再各自為政)
- 可共用 spectra-review `effective_cost = impact × probability` calibration 尺

### 2.5.5 與 Coverage Expansion 的接點

- §5.4 舉一反三的 ~3 候選 → 每個**先過准入閘門**;提示時附 5-test 判定(例:「此候選 T2 無證據 → 建議進 Open Questions」),人不盲收
- 這是准入閘門對 Coverage Expansion 的**防 gold-plating 強化**

---

## 3. 核心模型 — REQ ⇄ Golden Scenario ⇄ Anti-example 三元組不變式

**每條 requirement 是一個三元組,三者同生同滅、互相補齊。**

| 元素 | 角色 | 面向 |
|---|---|---|
| **REQ-ID** | request 本體(WHAT / user can X)| — |
| **Golden Scenario** | 描述**情境**(這 request 長什麼樣、happy path)| 正面 |
| **Anti-example** | 描述**邊界**(什麼**不算**滿足這 request)| 反面 |

### 3.1 四條不變式

| # | 不變式 | 說明 |
|---|---|---|
| **INV-1 Completeness** | 每條 REQ 應配 golden scenario + ≥1 anti-example | 缺項處置見 §5.3(可不附,但需二次確認 + 標記)|
| **INV-2 Cardinality** | **1 REQ = 1 golden scenario(嚴格 1:1)**;anti-example 為 **1:N** | golden scenario 是 sizing 單位 |
| **INV-3 Bidirectional reconciliation** | add/update/delete **任一元素** → 必回頭補齊另外兩個 | 見 §5(Triad Auto-Completion)|
| **INV-4 Split** | 一個 golden scenario 描述不完 = REQ 太大 → 拆成多個 REQ | 見 §7 |
| **INV-5 Claim-ID stability** | 每 claim(golden/anti)有穩定 ID `REQ-<id>-G/A<k>`;stable / monotonic / never-reuse / never-reindex | 下游 TP/FUNC/DESIGN/code 追溯的共同單位,見 §3.4 |

### 3.2 三元組 smell(違反即需處理)
- 🔴 orphan golden scenario(無對應 REQ)
- 🔴 orphan anti-example(無對應 REQ)
- 🔴 REQ 缺 golden scenario / 缺 anti-example(未經 §5.3 二次確認)
- 🔴 REQ 掛 >1 golden scenario → 太大,該拆(§7)
- 🔴 claim-ID 被 **reindex / reuse**(違反 §3.4 stable / never-reuse)→ 下游 `@implements` / `covers_req` 追溯失效

### 3.3 為何是三元組(rationale)
1. **天然餵養下游 5-spec cascade**:golden scenario → Test Cases 的 positive assertion;anti-example → anti-assertion(framework §3.4)。REQ 層即編碼「正面+邊界」,cascade 更緊。
2. **行為導向 sizing**:以 golden scenario 數當右尺寸判準,比 LOC 分級(framework §6)客觀。兩者並存(tier 決定寫幾份 spec,golden-scenario 決定 REQ 顆粒度)。

### 3.3a 與 5-spec framework 的收斂(N4 fix)

`docs/pm/5-spec-authoring-framework.md` 是**論述層**(WHY 5 spec);本 rulebook 是 requirement 層的**執行 SSOT**。收斂關係:
- framework **§8 Anti-Example per REQ Pattern** → 被本檔 INV-1 三元組**吸收並升為強制**(anti-example 從「recommended」變 required 1:N)
- framework **§6 feature-size tier(LOC)** → 與本檔 golden-scenario sizing **並存不衝突**:LOC tier 決定「寫幾份 spec」,golden-scenario(1:1)決定「REQ 顆粒度」
- framework **§3.4 Test Cases positive/anti-assertion** → golden_scenario / anti_examples 為其上游 seed
- 若 framework 與本檔對 requirement authoring 執行細節衝突,**以本檔為準**(One Topic, One Primary)

### 3.4 Claim ID 機制（下游追溯的共同單位)

> **claim = golden + anti**;每個 claim 有穩定 ID,成為 TP / FUNC / DESIGN / code 追溯的**共同單位**。§4N/§4O runtime flow + DESIGN rulebook §4.2 `@implements` / `test_seam` 皆依賴此機制。

**格式**:`REQ-<id>-<類型><序>`

| 類型 | 元素 | 是 claim? | 序 |
|---|---|---|---|
| **G** | golden scenario | ✅ | 恆 `G1`(INV-2 golden 嚴格 1:1)|
| **A** | anti-example | ✅ | `A1` / `A2` …(1:N,依加入序)|
| **P** | 痛點(pain,若有記)| ❌ **非 claim** | `P1` …(有 ID 供未來,**無下游覆蓋義務**;deferred)|

- 例:`REQ-005-G1`(golden)、`REQ-005-A1` / `REQ-005-A2`(兩個 anti)、`REQ-005-P1`(痛點,非 claim)。
- **與 split ID 相容(D-007)**:claim 尾綴接在 REQ-id 之後 → 拆分後 `REQ-005a-G1`、`REQ-005a-A1`。

**ID 規則(4 條)**:
1. **stable**:一旦賦予,該 claim 內容更新**不改 ID**。
2. **monotonic**:新 anti 取當前最大 +1(A1→A2→A3);golden 恆 G1。
3. **never-reuse**:刪除的 anti 序號**不回收**(刪 A2 後下一個是 A4,非 A2)。
4. **never-reindex**:既有 claim 的 ID **永不因增刪他項而位移**。

**為何**:下游一旦 cite `REQ-005-A2`,即使該 REQ 後續增刪 anti,`A2` 仍指同一 claim → 追溯不斷、`@implements` 不失效(對齊 §3.2 smell)。

**下游引用點(本機制的消費者)**:
- `TP.covers_req` = `{REQ-id, claim}`(TP 驗證的目標 claim)
- FUNC `user_journey.step.realizes` / `failure_mode.handles` = claim
- DESIGN `implements` → code `@implements FUNC-x.step-N (realizes REQ-005-G1)`
- DESIGN `test_seam.for_claim` = claim

**migration(既有 v1.1 backfilled triad)**:
- 新 v1.1 triad **必賦 claim-ID**(golden `G1` + 各 anti `A<k>`)。
- 既有 backfilled(backend-schema 14 / sanity 25 / scr 13)= **grandfather**:下次 touch 該 REQ、或首個下游 cite 它時 **lazy 賦 ID**;不強制一次全 backfill(對齊漸進 + measure-first)。
- **validator 機檢**(claim-ID presence + never-reindex)= **Track B**(rulebook-first,對齊 D-003;現階段 authoring-time 遵守)。

#### 3.4.1 Project-qualified identity(跨 project 唯一;2026-07-05 spectra R1 B1,PO 混合方案)

> **根因**:REQ-id 僅 **project 內唯一**(afv/backend/sanity/scr 皆有 REQ-001)。REQ 的真身是 `(project, REQ-id)`。任何**跨 project 聚合**的工具/agent 若把 identity 塌成裸 `REQ-id` → last-wins 碰撞(A.4 staleness 假綠即此)。

**canonical 全域 identity = `<project>:REQ-<id>-<類型><序>`**(冒號分隔),`<project>` = 該 spec frontmatter `parent_project`(module spec)或檔名 project 段(REQ spec)。例:`afv:REQ-001-G1`、`sanity:REQ-004-A2`。

**兩形式,按場景用**(不 mass-rename 既有裸 id):

| 場景 | 形式 | 理由 |
|---|---|---|
| **spec 內引用**(covers_req / realizes / handles / test_seam,同 project)| **bare** `REQ-001-G1` | 專案內無歧義,可讀;project 由該檔 frontmatter **`parent_project`** 界定(⛔ 不是 `upstream_spec`,見下方規則 2) |
| **跨 project 工具解析**(A.1-A.4、Track B agents)| 依 **`parent_project`** 先 qualify 再比對,不用全域裸 map | A.4 已示範(`collect_file_hashes` 按檔 + `resolve_upstream`) |
| **code 註解 `@implements`**(離開 spec、無 frontmatter 可依)| **qualified** `@implements afv:REQ-001-G1` | 裸 id 在 code 單看無法解析到 project |
| **agent 之間傳 id**(Track B 訊息/structured output)| **qualified** | 同上,跨邊界無上下文 |

**規則**:
1. 工具/agent **不得**建立全域裸 `{REQ-id → X}` map;identity key 一律含 project(`(project, REQ-id)` 或 `<project>:REQ-id`)。
2. spec 內 bare id 的 project 解析源 —— **`parent_project` 為唯一權威**(PO 2026-08-12 裁決,D-19):

   | 欄位 | 是否參與 project 解析 |
   |---|---|
   | `parent_project` | ✅ **唯一解析源**。缺則工具回報 unresolved,**不猜**。 |
   | `upstream_spec` | ⛔ **不參與解析**。它的語意是「上游**文件**指標」(這份 spec 的需求從哪來),**不是** project 命名空間。 |

   > **為什麼要明訂**(2026-08-12,LINE↔LIFF parity 三份 spec 實例):
   > 本規則原文把兩個欄位並列為解析源。三份 spec 的 frontmatter 同時有
   > `upstream_spec: mainline` 與各自的 `parent_project: <檔名段>` ⇒ **先讀哪一個決定了答案**,
   > 而先讀 `upstream_spec` 會把三份全部塌回 `mainline`。
   > 那正是本節開頭要修的 last-wins 碰撞 —— `mainline` 這個命名空間**已證實有裸 ID 重複**
   > (`occupation-aware-crm-lens` 有 REQ-001..031、`extraction-datetime-invariant` 有 REQ-001/002)。
   > ⚠️ 兩個獨立的 resource-manager agent 各自撞到並提報同一個歧義 ⇒ 不是個案,是規則本身有洞。
   >
   > ⭐ **本條的失效方式是靜默的**:欄位齊全、驗證器全綠,只有跨 project 聚合工具會拿到錯的
   > 命名空間,而它不會叫。⇒ 這是「規則寫了但沒人證明它被正確解讀」的形狀。
3. 既有裸 code 註解 / spec = **grandfather**;下次 touch 時 lazy 升 qualified(對齊 claim-ID lazy backfill)。

---

## 4. Authoring Checklist(逐條打勾)

### Part 0 — 適用閘門
- **P0-1** 觸發:create / update / delete **三元組任一元素**,不論 mode
- **P0-2** discuss mode(V1/V6)→ 先跑 §5 decision-time → popup;答「是」才離開 discuss-only 動檔
- **P0-3** execute mode(V2/V4)→ 直接跑 Part 1–4 write-time(delete 仍須 PO-confirm,見 §8)

### Part 1 — 結構強制(缺一即 reject;繼承 §7.5 / §7.6)
- **S1** Frontmatter 齊全:`Owner / Status(Draft|Active|Deprecated)/ Spec-Version(YYYY-MM-DD.N)/ Last Updated`
- **S2** §Purpose 一句話存在
- **S3** §Core Rules/Invariants ≥ 1 條明文
- **S4** §Open Questions 存在(用 `[OPEN]` 標記;無則寫「無」)
- **S5** §Scope:In-scope + ⛔ Non-goals 兩者都在
- **S6** 每條 REQ 有唯一 `REQ-XXX` ID anchor

### Part 2 — 每條 REQ 逐條檢(create/update)
- **R1** testable、「user can X」句型
- **R2** AC 可量測 —— ❌禁 vague(「效能好」「順」);必含 metric / threshold / 可觀察結果
- **R3** Priority tier 明標(P0 / P1 / P2),不得 silent
- **R4a** 恰有 **1** 個 golden scenario(1:1)
- **R4b** ≥ 1 個 anti-example(1:N;描述邊界)—— 缺項走 §5.3
- **R4c** golden scenario 塞不下單一情境 → 觸發 §7 SPL,不得硬塞
- **R5** 涉資料 → 補 D1/D2(input/output 欄位型別 + error/edge 處理已說明,即使「TBD by BE」)
- **R6** 涉狀態 → 補 S1/S2(狀態清單 + 每個 transition 的 trigger)

### Part 3 — 全文一致性(create/update/delete)
- **C1** 不與其他 canonical doc 產生未解衝突(M4);有衝突標明以哪份為準
- **C2** 引用的 REQ-ID / 文件都存在(防 copy-paste rot)
- **C3** 不引用 archive 或已刪文件
- **C4** 🔑 終極自問:「依這份 spec,另一個工程師/Claude 能否獨立完成同樣實作?」= yes(§7.3)
- **C5** 無 orphan golden scenario(每個 map 恰 1 REQ)
- **C6** 無 orphan anti-example(每個 map ≥ 1 REQ)

### Part 4 — CRUD delta → 見 §6
### Part 6 — Split → 見 §7

---

## 5. Decision-time 行為 — Triad Auto-Completion + Coverage Expansion

**兩層行為(人給片段,Claude 補全)**:
- **§5.1–5.3 補全當前三元組**:使用者只寫「錨點元素」,Claude 自動草擬另外兩個並提示是否加入(batch)
- **§5.4 擴大覆蓋面**:Claude 依全面視野列舉 ~3 個相鄰/隱含候選,逐一與人討論 add/mod/del

### 5.1 對稱 propose 矩陣

| 入口(使用者寫的錨點)| Claude 自動草擬並提示 |
|---|---|
| **REQ**(結論=新增 request)| golden scenario + anti-example |
| **Golden Scenario** | REQ 描述 + anti-example |
| **Anti-example** | REQ 描述 + golden scenario |
| **REQ 太大**(觸發 SPL)| 拆分方案:N ×(REQ + golden scenario + anti-example)|

### 5.2 popup 流程(discuss mode)— conditional 2-step(D-036 修訂 D-008)

> **⭐ 觸發邊界(D-036 §5.1 — 不污染一般 V1 討論):** 本流程僅在討論**收斂到「現在要 author / 改這條 REQ」**時啟動(掛既有 Authoring Gate 觸發面,**不擴大**)。**單純提 feature 想法 ≠ 觸發**;使用者可明說「**先討論、先別 spec**」(brainstorm) → 想法暫存 Open Questions(§2.5 T1/T2),等說「變成需求」才進流程。架構問答 / bug 診斷 / 探索 brainstorm 皆不觸發。

**vocab ↔ spec 欄位對映(discuss 用語 = 既有欄位,欄位名不變):**

| discuss 用語 | spec 欄位 | 追溯 |
|---|---|---|
| description | `Statement` | — |
| **pain point** | **`Why`**(既有;per-REQ 慣例,§4/template 具名化) | 餵 §2.5 准入 necessity |
| golden scenario | `golden_scenario` | claim-ID `G1` |
| anti-example | `anti_examples` | claim-ID `A1..An` |

```
結論觸發(動到三元組任一元素;已過 §2.5 准入)
   │
   ├─[V1/V6] Claude 精煉 description(Statement)+ 草擬 Why(pain point)
   │
   ├─ 🟦 STEP-1 確認【conditional — 僅 Statement 有實質改寫時】
   │      顯示 before/after diff;「描述這樣對嗎?」(未實質改寫 → 略過,直接 step-2)
   │
   ├─ [sizing gate §7 SPL-1] 一個 golden 裝得下嗎?裝不下 → 拆(§5.1 propose 矩陣,含 golden 草稿)
   │
   └─ 🟦 STEP-2 確認【三元組 batch 一次】
        「建議 golden scenario + anti-example 如下,是否加入?」
        [採用建議] / [我調整後加入] / [不附(需二次確認)]
```

- **確認粒度(D-036 修訂 D-008):anchor 單 REQ 由「整組一次」拆為 conditional 2-step**(描述 step-1 + 三元組 step-2)。
- **「多筆變更 batch 一次列全」保留**(D-036 C3-R2):用於 §5.4 舉一反三(~3 候選一張清單)+ §7 SPL 多子 REQ 一次審核形狀。
- **舉一反三(§5.4)定序在三元組(step-2)確認之後**跑;**若觸發源是 SPL,拆分不自動觸發舉一反三**(scope-creep guard,§7 + pm-skill SKILL.md:1200)。
- popup 選項可用 preview 顯示草擬內容供比對。

### 5.3 「不附」的處置(缺項 gate)

依 PO 裁決(D-005):**可以不附,但需二次確認。**

1. 使用者選「不附」→ Claude **再次詢問確認**:「確定 REQ-XXX 不配 golden scenario / anti-example?此為三元組不完整。」
2. 二次確認「是」→ 允許缺項,但該 REQ 的缺元素**必須標 `[GAP]`**(附 integration-notes / decision-log 記錄,30 天後升 `[OPEN]`;marker 語意見 `ddd-doc-maintenance.md §7.4`)
3. 二次確認「否」→ 回到 §5.2 採用/調整建議

> 缺項**不得 silent** —— 必留 `[GAP]` 痕跡,保持可追溯。

**機檢邊界(spectra Round 1 C3 fix):** 「二次確認」是 **authoring-time 對話 gate**(發生在建檔當下);validator / gate-check 的**唯一機檢依據是 `[GAP]` marker 存在與否**(可 grep),**不** re-verify 二次確認是否真的發生。即:`req-spec-v1.1` spec 中缺 golden/anti 且無 `[GAP]` → fail;帶 `[GAP]` → warning。

### 5.4 Coverage Expansion(片段 → 全面)

**前提:人給的是片段描述,Claude 有全面視野。** 除了補全當前三元組(§5.1–5.3),Claude 還要主動補人**漏掉的覆蓋面**。

**觸發**:§5 錨點三元組處理完後**強制接續執行** —— **所有 mode 皆必做,不得略過**(不限 discuss mode)。

**行為**:
1. Claude 依錨點 + domain context **舉一反三**,**列舉 ~3 個(總數,跨類合計,非每類 3 個)「相鄰/隱含但人未提」的候選**:
   - **sibling REQ**(相鄰需求 — 人這個 request 通常伴隨的其他 request)
   - **額外 golden scenario**(若成立 → 經 §7 拆為新 REQ)
   - **額外 anti-example**(人漏掉的邊界)
2. **逐一**與人討論每個候選:**add / modify / delete / 略過**(≠ 錨點三元組的 batch 確認)
3. 被採納的候選 → 回到 §5.1–5.3 補其完整三元組 + write-time 規則

**delete 情境**:人刪某元素時,Claude 列舉 ~3 個「可能一起該刪 / deprecate 的相關項」(cascade 候選),同樣逐一討論。

**Guardrails(防 gold-plating)**:
- **舉一反三,~3 總數上限** — 從人給的一個片段推 ~3 個相鄰候選(跨類合計,非每類 3 個);不 exhaustive,只 surface 最可能漏的,避免 overwhelming
- **候選必 grounded** — 從錨點語意 + domain 推導,禁憑空亂加(對齊 framework §10 gold-plating smell)
- **全部是 proposal** — 人逐一裁決;Claude **不自動寫入**未經同意的候選(避免「擅自擴大 spec」;本行為只「強制擴大討論面」,採納與否仍在人)

**Mode 執行方式(N3 fix)**:「逐一討論」的呈現隨 mode 不同,行為本身**所有 mode 皆強制**:
- **discuss(V1/V6)**:逐一互動式 popup,每候選一次 add/mod/del 裁決,答完才動檔
- **execute(V2/V4)**:一次列出 ~3 候選清單(附建議),使用者一輪內逐項回覆(inline batch 回覆),Claude 依裁決寫入;不逐一 blocking popup(避免打斷 execute 節奏),但清單**必列全**、每項**必有裁決**(不得靜默略過)

**粒度對比**:

| 行為 | 對象 | 確認方式 |
|---|---|---|
| §5.1–5.3 Triad Auto-Completion | 錨點**當前**三元組缺的 2 元素 | **conditional 2-step**(D-036 修訂 D-008:描述 step-1 + 三元組 step-2 batch;「多筆 batch 一次列全」保留)|
| §5.4 Coverage Expansion | **額外** ~3 個相鄰候選 | **逐一討論**(D-011;定序在三元組確認後,split 不自動觸發)|

---

## 5.5 Write-time 3-Role Async Sign-off

> **write-time 最後一關**:REQ 三元組齊(過 §2.5 准入閘門 + §5.1 Auto-Completion)後、**寫入 spec 前**的 3-role sign-off。
> 對齊 framework §7 reviewer matrix(PM=intent / QA=testability / Dev=feasibility)+ memory `[[human-first-docs]]`。

### 5.5.1 流程（async / per-REQ / non-blocking）

1. REQ 以 `status: pending-signoff` 暫存(未 finalize)
2. 派 3 張 per-REQ sign-off 任務進各角色 pending queue(重用 PM skill `new-requirement` pending-action infra):
   - 👔 **PM** → intent / priority / 可追溯
   - 🔬 **QA** → **testability**(golden_scenario 的 Then 可觀察?anti_examples 可成 anti-assertion?)
   - 💻 **Dev** → feasibility(建得出?藏 how / 隱形依賴?)
3. **有人決定就走(non-blocking,first decisive verdict)** —— 首個決定性 verdict 即走,不等其他人:
   - `approve` → 立即寫入(status: active)
   - `reject` → Out of Scope(不刪,見 §5.5.3)
   - `request-change` → 打回重塑三元組
4. 其餘角色任務**不關閉、轉 async advisory**:晚到的 dissent → 走 `/pm requirement modify`(living spec,**不 re-litigate、不 block**)
5. **Accountability**:記「written on `<role>` `<verdict>` @`<date>`;others pending」

### 5.5.2 High-stakes floor

- **安全 / 資料完整 / 法遵**類 REQ **不套**「有人決定就走」→ 保留較強 gate(不可單一 casual approve 定案;reject 不可被忽略)
- **機械判定(C3 fix)**:high-stakes ⇔ `risk_class ∈ {safety, data, compliance}`(per-REQ metadata,§B.4 optional;未標=`normal`)。validator / skill 據此欄位判定是否套 floor,不靠人肉猜

### 5.5.3 Verdict Annotation（無 terminal 狀態,全可修 / 救回）

- 每個 verdict **append** 成 REQ 的 `signoff` 歷史(append-only,不覆蓋)
- **reject → status out-of-scope 但不刪**,帶完整 signoff 歷史 + `revivable`;日後條件變 → re-admit(過 §2.5)/ modify → 回 active,再 append accept。全程 trail 可追溯「rejected → revived」
- **accept** → 照常 living spec 可 modify
- 因無 terminal 狀態,**自然涵蓋「PO override reject」**(任何人日後皆可改)
- signoff 註記 = **per-REQ metadata(append-only)**,隨 REQ / state.md + 鏡射 decision-log;**不進 11 核心欄位**(同 N1 分類的 status/effort/risk)

### 5.5.4 team_size 自適應

- `team_size > 1`:真 3-role async(3 張任務,有人決定就走)
- `team_size == 1`(solo PO):collapse 成 **1 張**,AI 附 👔/🔬/💻 三視角預審,PO 一次回 `{verdict, comment}`

### 5.5.5 不雙重 gate

- per-REQ 3-role sign-off 結果**匯總成** Phase 0 signoff 證據,不另開獨立 gate

### 5.5.6 Bulk-migration / backfill 也須事後補 sign-off(B1 fix)

- **不因「是遷移」而免 §5.5。** backfill / bulk-import / 結構重構(如 OD-4 / OD-5)大量產生或改寫 REQ triad 時,產物**同樣須事後補 3-role sign-off**(至少 🔬 QA-testability lens);未補者該 REQ 標 `signoff: pending`,不得視為已審
- validator(P4)只檢 triad **presence + cardinality**,**不檢 quality**;quality(golden 可測、anti 抓對邊界)須靠 §5.5 sign-off,兩者互補不可互替
- bulk 產物的 sign-off 可 sample(每 spec 抽樣 + 全新 REQ 全審),但**必留記錄**(decision-log)

---

## 6. CRUD Delta

### 6.1 CREATE(新增)
- **CR1** 全 Part 1 + Part 2 通過
- **CR2** `Spec-Version = YYYY-MM-DD.1`
- **CR3** 一筆 changeset(Rule B)
- **CR4** 三元組補齊(§5;缺項走 §5.3)

### 6.2 UPDATE(更新)
- **UP1** Rule C dependency check 必做(`dependency-map.md`)
- **UP2** 動核心規則/invariant/AC → Spec-Version 遞增 + cascade 下游(TP/FUNC/TC/DESIGN)標 `spec_dirty` + decision-log `D-XXX` + changeset
- **UP3** non-breaking(typo / 補 example / 加 open question)→ 不遞增版號、可免 changeset
- **UP4** 不得孤兒化下游引用
- **UP5** 若動的是 golden scenario / anti-example → 回檢對應 REQ 語意是否仍成立(INV-3)

### 6.3 DELETE(刪除)
- **DE1** 掃引用:誰 cite 這條 REQ / golden / anti(下游 spec + integration notes + code + 其他 REQ)
- **DE2** **預設 Deprecate(`Status: Deprecated`)優先於硬刪**
- **DE3** 若硬刪 → 清乾淨所有下游引用
- **DE4** **REQ-ID 永不重用**(D-007;拆分用字母後綴 005a/005b,源 ID 不回收給別的 REQ)
- **DE5** decision-log `D-XXX` + reason + **PO-confirm** + changeset
- **DE6** 三元組一起處理:刪 REQ → 連帶 deprecate/移除其 golden + anti(INV-3)

---

## 7. Split Rule(SPL)

- **SPL-1** sizing 單位 = golden scenario:**一個情境 = 一個 REQ**
- **SPL-2** REQ 太大(需 >1 scenario)→ 拆成 N 個 REQ,每個各自 1:1 配 golden scenario + ≥1 anti-example
- **SPL-3** ID 規則(D-007,**對齊 PM skill `/pm requirement split` §6.4.17**):原 REQ 以**字母後綴**拆為子 REQ(例:REQ-005 → REQ-005a / REQ-005b),源 ID 被取代不再單獨存在;禁 ID 衝突(不得與既有 REQ-id 重複)
- **SPL-3a** 巢狀拆分(N2 fix):005a 再拆 → **append `-N` 數字後綴**(`REQ-005a-1` / `REQ-005a-2`),不用 005aa(避免字母歧義);巢狀 ≥ 2 層代表原 REQ 顆粒度規劃有問題,建議先評估 `/pm requirement merge` 回收再重拆
- **SPL-4** decision-log 記拆分理由 + 原→新 mapping
- **SPL-5** decision-time 時 Claude 直接給拆分建議(每個新 REQ 已配三元組草稿),使用者審核拆分形狀(§5.1)

---

## 8. Mode Boundary

| Mode | 三元組 CRUD 結論出現時的行為 |
|---|---|
| **V1 / V6**(discuss)| 攤開影響 + Triad Auto-Completion 草擬 → **整組 popup 問** → yes 才離開 discuss-only 動檔 |
| **V2 / V4**(執行/提案)| 依既有授權直接依 write-time 規則做,**不需 popup** |
| **所有 mode(強制)**| §5.4 **Coverage Expansion 必做** — 舉一反三列 ~3 相鄰候選,逐一討論 add/mod/del(不得略過)|
| **delete(任何 mode)**| ⚠️ 例外:破壞性 → **PO-confirm 一律必做**(DE5) |

---

## 9. Resolved Decisions

完整記錄見 `docs/pm/spec-authoring/decision-log.md`。摘要:

| D | 裁決 |
|---|---|
| D-003 | rulebook-first;validator 硬 gate 列後續 phase |
| D-004 | 三元組不變式(REQ ⇄ golden ⇄ anti)|
| D-005 | 缺項處置 = 可不附,但需二次確認 + `[GAP]` 標記 |
| D-006 | anti-example 基數 = 1:N |
| D-007 | 拆分 ID = **字母後綴 005a/005b**(對齊 PM skill split;源 ID 被取代;ID 永不重用)— rev 2026-07-02 修訂,原「deprecate+新號」遷就既有 mature tool |
| D-008 | popup 確認粒度 = 整組一次(batch)— ⚠️ **[superseded-by D-036]** anchor 單 REQ → conditional 2-step(描述 step-1 + 三元組 step-2);「多筆 batch 一次列全」仍有效 |
| D-036 | Discuss-mode 互動式 authoring(修訂 D-008):conditional 2-step(描述→sizing gate §7→三元組)+ 舉一反三定序在後〔split 不自動觸發〕+ vocab↔欄位對映(pain point=`Why`)+ §5.1 觸發邊界(不污染一般 V1 討論);confirm gate=orchestrator、agent 只草擬;零 schema 欄位改動 + template +Why 1 行(discuss 必/execute optional)|
| D-009 | 觸發範圍 = 三元組任一元素 CRUD(decision-time + popup,cross-mode)|
| D-011 | Coverage Expansion:Claude 列舉 ~3 相鄰候選,**逐一**討論 add/mod/del(§5.4;proposal-only 防 gold-plating)|
| D-017 | Requirement Admission Gate(§2.5):5 test(可追溯/有證據/值得寫/是what非how/有必要)+ 路由(Open Questions / Out of Scope / 反推 what)+ T3 carve-out(安全/資料/法遵)+ T3 統一 priority 來源 + 一律套但 PO override |
| D-018 | Write-time 3-Role Async Sign-off(§5.5):async per-REQ,**有人決定就走**(non-blocking first decisive verdict);high-stakes floor;**Verdict Annotation**(無 terminal,reject 不刪、revivable);team_size 自適應;匯總進 Phase 0 signoff |

---

## 10. 與現有文件的關係(One Topic, One Primary)

| 文件 | 關係 |
|---|---|
| `ddd-doc-maintenance.md §7`(M1–M5 完整性)| **本檔繼承**;通用最低標準仍以 §7 為準,本檔在其上加 REQ 專屬規則 |
| `5-spec-authoring-framework.md §3.1`(REQ 論述)| 論述層;REQ authoring 的**執行規則指向本檔** |
| `docs/_spec-template.md`(通用模板)| REQ 專屬模板見 `_requirement-spec-template.md`(本目錄)|

> ⚠️ §7 與 `_spec-template.md` 為受保護檔;於其加「指向本檔」的 pointer 需另取得 PO 授權(見 §11 OQ-1)。

---

## 11. Open Questions

- **[FIXED 2026-07-02 OD-1]** ~~OQ-1~~ `ddd-doc-maintenance.md §7` 已加「指向本 Primary」pointer(PO 授權);`docs/_spec-template.md` **不存在**(pre-existing 參照 drift),故無需該處 pointer。
- **[FIXED 2026-07-02 P4]** ~~OQ-2~~ validator 已實作:`scripts/requirement_spec_triad_validator.py`(token-based 三元組完整性 + schema_version 分流)+ lint.sh Stage 5 BLOCKING。下游引用完整性驗證仍為未來增強(目前檢三元組 presence)。
- **[OPEN] OQ-3** feature-size tier(framework §6)與本規則的正式交互規範(Trivial 是否可免 non-goals / anti-example)—— 待 pilot 後定。

---

## 12. Rollout

| Phase | 內容 | 狀態 |
|---|---|---|
| **P1(本次)** | rulebook + template + decision-log(軟約束)| ✅ this proposal |
| **P2** | 接線:CLAUDE.md 常駐硬規則 + `ai-principles.md §3` V4 pointer | ✅ this proposal(已授權)|
| **P3a** | PM skill schema 對接:§B.4 加 golden_scenario + anti_examples(9→11 欄位)+ `/pm validate-req-spec` triad completeness check + gate-check phase-0 C1 | ✅ 2026-07-02(D-007 對齊 005a/005b)|
| **P3b** | PM skill 行為接線:`start` / `new-requirement` / `add-mid-phase` / `modify` 套 Triad Auto-Completion + Coverage Expansion(共用 §Shared: Triad Authoring Behavior 區塊)| ✅ 2026-07-02 |
| **P3c** | PM skill wiring:§2.5 Admission Gate(前關)+ §5.5 Write-time 3-Role Sign-off(後關)接進 `start` / `new-requirement`;§Shared header 加 3-phase pipeline;spec §B.4a 對應 | ✅ 2026-07-02 |
| **P4** | **triad-only** CI 硬 gate:`scripts/requirement_spec_triad_validator.py`(stdlib only;schema_version 分流;檢 golden 恰1 + anti≥1 presence/cardinality,**非** quality、**非** 11 欄位)+ lint.sh **Stage 5 BLOCKING**。11 欄位完整性仍 skill 層 `/pm validate-req-spec`;quality 靠 §5.5 sign-off | ✅ 2026-07-02(全 v1.1 spec pass)|
| **OD-5** | scr spec option A 重構:新增 `## Requirements` 13 REQ-XXX + triad + § 交叉錨點 → req-spec-v1.1(content-preserving)| ✅ 2026-07-02 |

---

## 13. Revision History

| Rev | Date | Author | Change |
|---|---|---|---|
| 2026-07-01.1 | 2026-07-01 | PO + Claude | Baseline — 2026-07-01 V1→V4 session:三元組不變式 + Triad Auto-Completion + CRUD delta + 兩段式 gate |
| 2026-07-02.1 | 2026-07-02 | PO + Claude | D-007 修訂遷就 PM skill split(005a/005b);P3a PM skill schema 對接落地(§B.4 11 欄位 + validate-req-spec triad check)|
| 2026-07-02.2 | 2026-07-02 | PO + Claude | OD-4 discriminator 補洞(非 v1.1 一律 grandfather,涵蓋既有 enhanced-v1);OD-1 ddd §7 pointer;N1-N4 nits(aspect 分類 / SPL-3a 巢狀 ID / Coverage Expansion execute mode / framework 收斂 §3.3a)|
| 2026-07-02.3 | 2026-07-02 | PO + Claude | §2.5 Requirement Admission Gate(5-test 准入 + 路由 + priority 統一);§5.5 Write-time 3-Role Async Sign-off(有人決定就走 + Verdict Annotation revivable)|
| 2026-07-02.4 | 2026-07-02 | PO + Claude | P4 validator 落地(scripts/requirement_spec_triad_validator.py + lint.sh Stage 5 BLOCKING;OQ-2 fixed);OD-5 scr option A 重構(13 REQ + triad → v1.1);REQ-010 backfill 補漏 |
| 2026-07-02.5 | 2026-07-02 | PO + Claude | spectra Round 2 fixes:B1 §5.5.6 bulk-migration 也須事後 sign-off + scr 13 QA 審(REQ-004 fixed);C1 validator cardinality(恰1 golden);C2 §12 P4 triad-only 明示;C3 `risk_class` marker(§2.5.1/§5.5.2)|
| 2026-07-04.0 | 2026-07-04 | PO + Claude | §3.4 **Claim-ID 機制**(claim = golden+anti;`REQ-<id>-G/A<k>`,pain `P<k>` 非 claim deferred;stable/monotonic/never-reuse/never-reindex;split 相容 `005a-G1`;下游 TP/FUNC/DESIGN `@implements`/`test_seam` 引用;既有 backfill lazy 賦 ID grandfather;validator=Track B)+ INV-5 + smell;**解鎖 §4N/§4O + DESIGN §4.2 pending 依賴**(D-028)|
| 2026-07-05.0 | 2026-07-05 | PO + Claude | §3.4.1 **Project-qualified identity**(spectra R1 B1 root cause;PO 混合方案):REQ 真身=`(project, REQ-id)`;canonical `<project>:REQ-id`;spec 內 bare / 跨 project 工具依 `upstream_spec` qualify / code `@implements` + agent 訊息用 qualified;工具**不得**建全域裸 map;既有 grandfather lazy 升(D-034)|
| 2026-08-12.0 | 2026-08-12 | PO + Claude | §3.4.1 規則 2 **`parent_project` 定為唯一 project 解析源**(PO 裁決 D-19):原文把 `upstream_spec` 與 `parent_project` **並列**為解析源 ⇒ 兩者不同值時「先讀哪一個」決定答案。實例:LINE↔LIFF parity 三份 spec 同時有 `upstream_spec: mainline` 與各自的 `parent_project: <檔名段>`,先讀 `upstream_spec` 會把三份全塌回 `mainline` —— 而該命名空間**已證實有裸 ID 重複**(`occupation-aware-crm-lens` REQ-001..031、`extraction-datetime-invariant` REQ-001/002),正是本節開頭要修的 last-wins 碰撞。⭐ 由**兩個獨立的 resource-manager agent 各自撞到並提報**⇒ 規則本身有洞,非個案。⚠️ 失效方式**靜默**(欄位齊全、驗證器全綠,只有跨 project 聚合工具拿到錯命名空間且不會叫)。⇒ 明訂:`parent_project` = ✅ 唯一解析源(缺則 unresolved,不猜);`upstream_spec` = ⛔ 不參與解析(語意是「上游**文件**指標」,非 project 命名空間);§3.4.1 兩形式表同步訂正 |
