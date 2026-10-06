# Test Plan Spec Authoring Rules

> **Owner:** PM(spec authoring governance)
> **Status:** Draft
> **Spec-Version:** 2026-07-05.2
> **Last Updated:** 2026-07-05
> **Role:** L3 Primary — test plan spec 的 **create / update / delete** 唯一 authoring 規則書(Track A 家族第 3 份)
> **Authors:** PO(kuohsuming)+ Claude(co-author)

---

## 1. Purpose

定義 Claude(及任何 AI 工具)在 **建立、更新、刪除 test plan(TP)spec** 時**必須嚴格遵守**的規則。可逐條打勾的執行規則書。

- 論述 / framework 層 → `docs/pm/5-spec-authoring-framework.md`
- 通用 spec 完整性標準(M1–M5)→ `docs/ddd-doc-maintenance.md §7`(繼承)
- 姊妹 rulebook:`requirement-spec-authoring-rules.md`(REQ,claim-ID 機制 §3.4)· `design-spec-authoring-rules.md`(DESIGN)· `test-cases-spec-authoring-rules.md`(TC)
- **本檔專注**:TP 是「**驗什麼 + 怎樣叫過**」的**策略層**(非具體 test steps —— 那是 TC)。

> **⭐ TP 恆存在(2026-07-05,D-035;5 份 spec 不可省略)**:無論 feature 多簡單,**TP 都要寫**——無 tier 省略。tier 只控**深度**(framework §6)。**最小地板(floor)= 每 claim ≥1 `validation_key_point`(帶 vkp-ID)+ `covers_req` 單值 claim-ID + ≥1 area**;簡單 feature 寫到此即合格,但不省(TP 恆在 → DESIGN `test_seam` / TC `covers_tp` 恆有 parent 可 cite)。

> **本檔是 test plan authoring 的唯一 Primary。** framework 若涉 TP authoring,應指向本檔(One Topic, One Primary — `ddd-doc-maintenance.md §3.1`)。

---

## 2. Scope

### ✅ In-scope
- TP spec 的 create / update / delete 規則
- TP sizing(1 TP = 1 claim)+ 雙向基數 + REQ→TP→TC 對映
- TP schema(含 `validation_key_point` 及其 **vkp-ID** 定義)+ area 風險加權 + gate

### ⛔ Non-goals
- 具體 test steps / assertions(= TC,`test-cases-spec-authoring-rules.md`)
- claim-ID 機制本身(= REQ rulebook §3.4,本檔**引用**)
- validator 硬 gate 實作:Track B(rulebook-first,對齊 REQ D-003)

---

## 3. 核心模型 — 1 TP = 1 claim

### 3.1 貫穿原則:每層宣告「正面 + 負空間」

REQ 三元組(golden 正 + anti 邊界)一路貫穿 5 層;TP 這層的 sizing atom = **1 claim**:

| Spec | sizing atom | 正面 | 負空間 |
|---|---|---|---|
| Requirement | 1 golden_scenario | golden | anti_examples |
| **Test Plan** | **1 claim(golden 或 1 anti)** | positive TP | boundary TP + **non-verification 宣告** |
| Test Cases | 1 Given/When/Then | positive assertion | anti-assertion |

### 3.2 TP sizing 不變式

| # | 不變式 | 說明 |
|---|---|---|
| **INV-TP1 One-claim** | **1 TP = 1 可測 claim = 1 golden_scenario 或 1 anti_example**(二選一,**不 bundle**)| 混 >1 claim → 拆 |
| **INV-TP2 Coverage** | 每 REQ 的 TP 集 = **1(golden `G1`)+ N(anti `A1..An`)** | REQ 三元組直接決定 TP 集合;每 REQ **≥1 TP**(gate)|
| **INV-TP3 Cite-parent single** | `TP.covers_req` = 恰 **1 REQ + 1 claim**(claim-ID 見 §3.3)| 0 或 >1 → validator fail |
| **INV-TP4 Observable vkp** | 每 TP **≥1** `validation_key_point`(複數 list;1 TP=1 claim,但該 claim 可有**多個可觀察允收點**):each **observable / measurable** + **trace 回 REQ acceptance**(不自己發明)| 防不可測 TC(spectra R2 教訓)|

- **痛點(pain)不是 sizing 單位**:它是 why、不直接測(對齊 REQ §3.4 pain `P<k>` 非 claim)。可測的是 golden(正)+ anti(邊界)。
- **area 是標籤非 atom**:從 claim 推(golden→happy;anti 講空狀態→edge;anti 講 PII→security)。

### 3.3 claim-ID(引用 REQ rulebook §3.4)

- `TP.covers_req` 的 claim 用 **§3.4 claim-ID**:golden = `REQ-<id>-G1`;anti = `REQ-<id>-A<k>`。
- 例:`covers_req: REQ-005-G1`(positive TP)、`covers_req: REQ-005-A2`(boundary TP,對第 2 個 anti)。
- **claim 類型由 `covers_req` claim-ID 的 `G`/`A` 前綴讀,無獨立 `claim` 欄**(claim-ID 已編碼)。
- 既有 backfill REQ 尚無 claim-ID → **lazy 賦**(§3.4 migration);賦前 `covers_req` 暫填 `REQ-005`(claim 類型記於 description),賦後轉 `REQ-005-G1`。

### 3.4 雙向基數(PO 定案)

- **⬇️ 向下(覆蓋 fan-out)**:`REQ ─1:m─▶ TP ─1:n─▶ TC` ⟹ **REQ:TP:TC = 1:m:n**
- **⬆️ 向上(trace,每手恰 1 parent)**:`TC ▶ TP ▶ REQ` ⟹ **TC:TP:REQ = 1:1:1(唯一 parent 鏈)**
- **cite-parent 單值**:`TP.covers_req` 恰 1 claim;`TC.covers_tp` 恰 1 TP。
- ⚠️ **別假設全 5 層 up 都 1:1:1**:FUNC 可 cover 多 REQ(m:n up,見 FUNC rulebook)。

### 3.5 REQ→TP→TC 全鏈對映

```
golden_scenario (G1) ──▶ positive TP ──▶ positive-assertion TC
anti_example  (Ak)   ──▶ boundary TP ──▶ anti-assertion  TC(expected_count: 0)
```

---

## 4. TP Schema(dual-layer)

### 4.1 machine-block

```yaml
- id: TP-012
  covers_req: REQ-005-G1              # ⭐ 單值 = REQ + claim-ID(§3.3);0/>1 → fail
  area: happy                         # enum: happy | edge | error | concurrent | security | performance | contract-doc
  validation_key_points:              # ⭐ 每個帶 vkp-ID(§4.2);observable + trace REQ acceptance
    - id: TP-012.vkp-1
      point: "匯出產生 PNG,含該則文字 + 時間,檔 < 500KB"
  verification_method: integration    # unit | integration | ui | load | manual | contract-assertion
  test_data_source: real-corpus(anonymized)
  environment: real-device-ios/android   # UI 例;非 UI→runtime/CI（layer-specific,見 §5 rule 5）
  priority: P1
```
**人類層(description)**:白話「這 TP 驗什麼」(base on golden/anti,3-role 視角)。

**anti 例**:`covers_req: REQ-005-A2` / `area: security` / `vkp: "匯出 payload 不含任何 card_comments 欄位"` / `priority: P0`。

### 4.2 validation_key_point ID（vkp-ID)

> **DESIGN `test_seam.for_key_point` 依賴此 ID**(DESIGN rulebook §4.1 INV-D7)—— 本檔為 vkp-ID 的**定義處**。

- **格式**:`TP-<id>.vkp-<n>`(例 `TP-012.vkp-1`)。
- **規則**:stable / monotonic / never-reuse / never-reindex(同 claim-ID §3.4 精神)—— 下游 `test_seam.for_key_point` cite 後不失效。
- 一個 TP 可有多個 vkp(策略層允收的多個可觀察點);每個 vkp = TC 一條可斷言標的。

---

## 5. 關鍵規則

1. **`validation_key_points` = TP↔TC 契約**(每個 vkp):必 **observable/measurable**(❌「運作正常」)+ trace 回 REQ acceptance / golden 的 Then(不自己發明)。
2. **TP = 策略非具體**:只放 vkp,**不放 test steps**(那是 TC)—— 守住「TP 不含 TC 複本」。
3. **area 集合 = risk-weighted**:`risk_class ∈ {safety, data, compliance, 金流}` → **error + security TP 強制**;normal → happy(+edge)。
4. **non-verification 宣告(負空間)**:某 area 不適用 → **顯式宣告不驗 + 理由**(不 silent-gap;對齊「正面 + 負空間」)。
5. **environment 必實(layer-specific,pilot 01 F1)**:**UI TP** 的 `environment` 須含 **real-device LINE WebView**(對齊 sanity + `[[android-webview-render-bug]]`);**非 UI(backend / module)TP** 的 environment = 該層真實 runtime(eg. Flask startup + MySQL / CI integration),**不套 WebView**。共通原則:environment 必為**能真實觸發該 claim** 的環境。
6. **契約型 anti 的驗證(contract-type anti;Track B pilot outreach-log-read 補)**:某些 anti 宣告的是「**刻意不做的保證**」而非「錯誤行為」(REQ rulebook §3.4 以 `[契約型 anti]` marker 標記,eg.「不承諾 已發送次數==歷史筆數」)。其 TP **不得**轉成常規行為測試(硬測「筆數一致」會製造 flaky 假測);改用:
   - `area: contract-doc`（非行為 area）
   - `verification_method: contract-assertion`（驗證方式 = **spec 中此宣告存在** + UI copy/行為不違反該宣告,非跑一條會通/會敗的行為測試)
   - `environment: spec-document review`（無需真機/runtime)
   下游 TC 以「文件斷言存在 + 無過度承諾」驗,QA 不誤判成 defect。**判準**:anti 描述「系統保證不做 X」且無可觀察的失敗行為可觸發 → contract-type;anti 描述「系統做錯 X」且可觸發觀察 → 常規行為 anti。

---

## 6. Gate + Dashboard

- **Gate(HARD)**:每 REQ **≥1 TP**(0 = 未驗需求 → fail)。
- **Dashboard**:REQ × TP count + **area 覆蓋矩陣**(count 是虛榮指標,area 完整性才是真信號):
```
REQ-005 匯出單筆筆記 | TP:3 | areas: happy✓ edge✓ security✓ error✗⚠
REQ-006 批量匯出     | TP:0 ❌
```
- 人話呈現(非 yaml);全鏈 dashboard(REQ→TP→TC→FUNC→DESIGN)等 5 份 spec 齊再做。
- **validator 機檢**(每 REQ ≥1 TP、covers_req 單值、vkp observable)= Track B(rulebook-first)。

---

## 7. CRUD + Write-time Sign-off（對齊 REQ §5.5)

- **角色**:🔬 QA = primary author;👔 PM(對齊 REQ 意圖)+ 💻 Dev(可測性 / seam)= reviewers。
- **write-time sign-off**:TP 寫入前 async per-TP 3-role sign-off,**有人決定就走**(non-blocking,對齊 REQ §5.5)。
- **CRUD**:
  - **create** — 過 INV-TP1~4 才寫入;每 REQ 的 golden + 各 anti 皆須對應 TP(INV-TP2)。
  - **update** — 改 `covers_req`/`validation_key_point` 觸發 REQ↔TP + TP↔TC 重驗;vkp **never-reindex**。
  - **delete** — 破壞性 → **PO-confirm**;預設 Deprecate;TP-ID / vkp-ID 永不重用。

---

## 8. Decision Log

裁決見 `docs/pm/spec-authoring/decision-log.md`。TP rulebook 內容源自 execution-plan §4D 定案 + REQ §3.4 claim-ID + DESIGN §4.1 vkp 依賴。

## 9. Revision

| Rev | Date | Change |
|---|---|---|
| 2026-07-05.0 | 2026-07-05 | **pilot 01 F1 fix**(backend-schema-auto-sync measure-first):§5 rule 5 `environment` 加 **UI/非 UI carve-out** —— UI→real-device WebView / backend→runtime(Flask+MySQL)/CI;§4.1 schema comment 同註。根因:規則衍生自 sanity 帶 UI 假設,backend 模組露餡 |
| 2026-07-04.1 | 2026-07-04 | spectra R1 fixes(accept,C1–C2 + N1):C1 `validation_key_points` **複數**(INV-TP4 ≥1;1 TP=1 claim 但可多 vkp;§5 rule 1 同步)/ C2 **claim 類型由 `covers_req` claim-ID `G`/`A` 讀**(無獨立 `claim` 欄)+ §3.3 過渡措辭對齊(消 TC `TP.claim` dangling)|
| 2026-07-04.0 | 2026-07-04 | 新建 Track A TP rulebook(§4D → 檔):1 TP=1 claim(INV-TP1~4)· 雙向基數 · REQ→TP→TC 對映 · dual-layer schema · **vkp-ID `TP-<id>.vkp-<n>` 定義**(收 DESIGN §4Z 依賴)· area risk-weighted + non-verification · 每 REQ ≥1 TP gate · claim-ID 用 REQ §3.4;validator = Track B |
| 2026-07-05.1 | 2026-07-05 | **契約型 anti 驗證支援**(Track B pilot outreach-log-read Phase 1 R1 surface):`area` enum +`contract-doc`、`verification_method` enum +`contract-assertion`(§4.1)+ **§5 rule 6**(契約型 anti = REQ §3.4 `[契約型 anti]` marker 者,TP 不轉常規行為測試防 flaky,改文件斷言;判準 = 保證不做 X vs 做錯 X)。motivating precedent = A3「不承諾筆數==發送次數」+ TP-004 |
