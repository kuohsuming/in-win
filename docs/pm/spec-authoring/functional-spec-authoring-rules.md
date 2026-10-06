# Functional Spec Authoring Rules

> **Owner:** PM(spec authoring governance)
> **Status:** Draft
> **Spec-Version:** 2026-07-05.0
> **Last Updated:** 2026-07-04
> **Role:** L3 Primary — functional spec 的 **create / update / delete** 唯一 authoring 規則書(Track A 家族第 5 份,收尾)
> **Authors:** PO(kuohsuming)+ Claude(co-author)

---

## 1. Purpose

定義 Claude(及任何 AI 工具)在 **建立、更新、刪除 functional(FUNC)spec** 時**必須嚴格遵守**的規則。可逐條打勾。

- 論述 / framework → `docs/pm/5-spec-authoring-framework.md`
- 姊妹 rulebook:`requirement-spec-authoring-rules.md`(REQ §3.4 claim-ID)· `test-plan-spec-authoring-rules.md`(TP)· `test-cases-spec-authoring-rules.md`(TC)· `design-spec-authoring-rules.md`(DESIGN)
- **本檔專注**:FUNC 是「**用戶要看到的行為**」(user journey + failure modes),**非 impl detail**(那是 DESIGN),**非 test scenarios**(那是 TP/TC)。

> **本檔是 functional authoring 的唯一 Primary。**(One Topic, One Primary)Track A 5-spec rulebook 家族至此**齊 5/5**。

> **⭐ FUNC 恆存在(2026-07-05,D-035,PO 反轉「Small 省 FUNC」)**:無論 feature 多簡單,**FUNC 都要寫**——不再有 tier 省略。tier 只控**深度**(framework §6)。**最小地板(floor)= ≥1 `user_journey`(≥1 step `realizes` golden)+ ≥1 `failure_mode`(`handles` anti)+ `covers_req` list**;簡單 feature 寫到此即合格(可能 1-2 行),但不省。FUNC 扛「行為/旅程」層(REQ=what、DESIGN=how 皆無此),簡單也不冗餘。

---

## 2. Scope

### ✅ In-scope
- FUNC spec 的 create / update / delete 規則
- **三角互驗**(REQ/FUNC/TP 任兩驗第三)+ 兩子結構基數
- FUNC schema(結構化 user_journey + failure_modes,claim 引用)+ `@implements`/`@enforces` 下沉程式碼

### ⛔ Non-goals
- impl detail(interface / file / DB)= DESIGN;test scenarios = TP/TC
- claim-ID 機制本身 = REQ §3.4(本檔**引用**)
- validator 硬 gate 實作:Track B(rulebook-first)

---

## 3. 核心模型 — 三角互驗 + FUNC = 1 user journey

### 3.1 三角互驗:共同單位 = claim(§3.4 claim-ID)

REQ / FUNC / TP **任兩個驗第三個**,前提 = 三者共享 **claim**(`REQ-<id>-G1` golden / `REQ-<id>-A<k>` anti,per REQ §3.4):
- **REQ** 擁有 claim(golden + N anti)· **TP** verifies 1 claim(1 TP=1 claim)· **FUNC** `realizes`(golden)/ `handles`(anti)

| 用哪兩個 | 驗第三個 | 機械檢查 |
|---|---|---|
| REQ + FUNC | **TP** | FUNC realizes/handles 的每 claim → 必有 TP;否則 TP 漏 |
| REQ + TP | **FUNC** | 每有 TP 的 claim → FUNC 必 realizes/handles;否則 FUNC 漏 |
| FUNC + TP | **REQ** | FUNC/TP 的 claim → 必都是 REQ 宣告的;否則 REQ 漏 / gold-plating |

### 3.2 兩子結構、兩基數（PO 定案)

- **測試側 REQ→TP→TC**:下 1:m:n / **上 1:1:1(唯一鏈)**(cite-parent 單值)
- **行為/建構側 REQ→FUNC→DESIGN→Code**:**m:n mesh**(流程/元件天生共用)
- 兩者在 **TC ↔ FUNC 交叉連**(TC `covers_tp`→TP→claim ↔ FUNC realizes/handles 同 claim)
- ⚠️ 故 **FUNC 的 up-trace 非 1:1:1**:一個 FUNC 可 cover 多 REQ(`covers_req` list,m:n)

### 3.3 不變式

| # | 不變式 | 說明 |
|---|---|---|
| **INV-F1 One-journey** | 1 FUNC = **1 user journey**(1 條 happy path);混多 journey → 拆 | sizing atom = journey |
| **INV-F2 Claim-grounded** | `covers_req` = **list ≥1**(m:n);每 `step.realizes` / `FM.handles` 的 claim **∈ covered REQ 的 claims** | claim 用 §3.4 ID |
| **INV-F3 Negative space** | **≥1 `failure_mode`**(handles anti-example)| 正面 journey + 負空間 FM |
| **INV-F4 No silent modality shift** | 每個行為(step/FM)**必 trace 到 claim**;realizes 不到任何 claim 的 outcome = 憑空多做(gold-plating)| 雙向:claim→行為 + 行為→claim |
| **INV-F5 Trace sink** | `realizes`/`handles` → 程式碼註解 `@implements`/`@enforces`(function 層,延伸 `@governed-by`)| 見 §5.2 |

> **INV-F1 × INV-F2 消歧**:1 FUNC = 1 journey(單一 happy path),但該 journey **可跨多 REQ**(realizes 多個 REQ 的 claim)→ 故 `covers_req` 是 list(m:n)。**1 journey ≠ 1 REQ**。

---

## 4. FUNC Schema(dual-layer)

### 4.1 machine-block

```yaml
- id: FUNC-export-note
  covers_req: [REQ-005]                 # ✅ list ≥1（m:n）
  user_journey:                          # ✅ 結構化 steps（非散文）
    - step: 3
      action: 點「匯出」→ 系統產生單則 PNG → 彈出分享 sheet
      observable: PNG 生成 + 分享 sheet 顯示
      realizes: REQ-005-G1               # ⭐ claim 引用跟著這一步（golden）
  failure_modes:                         # ✅ ≥1（負空間）
    - id: FM-1
      handles: REQ-005-A2                # ⭐ claim（anti）
      trigger: 筆記含私人 card_comments
      response: 匯出 payload 過濾 card_comments
      user_message: (silent)
  data_validation: <opt — input format / boundaries / error template>
  ux_pattern: <opt — reuse 或 justify NEW>
  integration_points: <opt — external API / 他 module 契約，必 cite>
```
**人類層(prose,3-role)**:👔 PM = 用戶要看到的行為(非 impl)· 🔬 QA = 每 step observable 可否成 TP · 💻 Dev = journey → DESIGN 的實作起點。**不含 test scenarios**(TP/TC 的事)。

### 4.2 claim 引用（§3.4)
- `step.realizes` = golden claim(`REQ-<id>-G1`);`FM.handles` = anti claim(`REQ-<id>-A<k>`)。
- 既有 backfill REQ 尚無 claim-ID → lazy 賦(§3.4);賦前 realizes/handles 暫記 REQ + 描述,賦後轉正式 ID。

---

## 5. 關鍵規則

### 5.1 行為導向、非 impl、非散文
- FUNC = **用戶可觀察行為**;impl detail(檔案/簽章/DB)下放 DESIGN(過細 = 錯層)。
- **結構化 per-step**(step/action/observable/realizes),非純散文——散文只有 Claude 讀得順,追溯流不到 code。
- 新 UX pattern 必 **justify**(reuse 優先)。

### 5.2 追溯線下沉程式碼（`@implements` / `@enforces`,INV-F5)
```
REQ-005-G1 → FUNC-export-note.step-3 → DESIGN.exportNoteToPng()（@implements）→ code
```
```python
def export_note_to_png(note_id):
    """
    @implements FUNC-export-note.step-3 (realizes REQ-005-G1): 產生單則 PNG
    @enforces   FUNC-export-note.FM-1  (REQ-005-A2): 過濾 card_comments，防外洩
    """
```
- **好處**:code 自帶「實現哪個需求」+ 人可 debug/review + 防危險 refactor(看到 `@enforces` 就知牽動需求)+ validator 檢 `@implements` 指向存在的 FUNC step。
- ⭐ **這是 §4N/§4O 上溯的 FUNC 節點**:runtime bug / build 不清 → 沿 `@implements` 爬回 FUNC.step → claim → REQ golden/anti,四層診斷定缺陷起源層。

### 5.3 禁 silent modality shift（INV-F4）
- 每 step/FM 必 trace claim;**realizes 不到任何 claim 的 outcome = 憑空多做** → 砍或反推 REQ(准入閘 §2.5)。
- 雙向:REQ 的每 claim 必被某 FUNC realizes/handles(gap)+ 每 FUNC 行為必 trace claim(gold-plating)。

---

## 6. Gate + 三角互驗檢查

- **Gate(HARD)**:每 REQ 有 ≥1 FUNC child(framework G3,**REQ-level 粗篩**);**precise gate = claim-level** —— 每 REQ claim(golden + 各 anti)被某 FUNC step/FM realizes/handles(INV-F4),比 G3 細。
- **三角互驗**(§3.1)= coverage validator 家族的一環:`REQ↔FUNC`(claim realizes/handles)+ 與 `REQ↔TP`、`TP↔TC`、`FUNC↔DESIGN` 交叉。
- **TC↔FUNC 交叉連驗**:TC 經 `covers_tp`→TP→claim,與 FUNC realizes/handles 同 claim → 兩子結構在此對齊。
- **validator 機檢**(REQ↔FUNC claim 覆蓋、`@implements` 指向存在 step)= Track B。

---

## 7. CRUD + Write-time Sign-off（對齊 REQ §5.5)

- **角色**:👔 PM = primary author(行為 = 用戶要看到的);🔬 QA(每 step 可測?)+ 💻 Dev(journey 可實作?)= reviewers。
- **write-time sign-off**:async per-FUNC,**有人決定就走**(non-blocking)。
- **CRUD**:
  - **create** — 過 INV-F1~F4 才寫入;每 covered REQ 的 golden + anti 皆須被某 step/FM realizes/handles。
  - **update** — 改 `covers_req`/`realizes`/`handles` 觸發三角互驗重驗 + `@implements` cascade-check(下游 DESIGN/code)。
  - **delete** — 破壞性 → **PO-confirm**;預設 Deprecate;FUNC-ID 永不重用。

---

## 8. Decision Log

裁決見 `docs/pm/spec-authoring/decision-log.md`。FUNC rulebook 源自 execution-plan §4G 定案(三角互驗 + 結構化 per-step realizes/handles + 追溯下沉)。**Track A 5-spec rulebook 家族至此齊 5/5。**

## 9. Revision

| Rev | Date | Change |
|---|---|---|
| 2026-07-04.1 | 2026-07-04 | spectra R1 fixes(accept,N2–N3):N2 §6 gate 註明 claim-level 才 precise(G3 REQ-level 粗篩)/ N3 INV-F1×F2 消歧(1 journey 可跨多 REQ,故 covers_req list)。(C1/N1 屬 §4P,見 exec-plan rev 1.13)|
| 2026-07-04.0 | 2026-07-04 | 新建 Track A FUNC rulebook(§4G → 檔,收尾 5/5):三角互驗(REQ/FUNC/TP 任兩驗第三,共同單位 claim §3.4)· 兩子結構基數(測試側 1:1:1 / 行為側 m:n mesh,TC↔FUNC 交叉連)· INV-F1~F5(One-journey / claim-grounded covers_req list / ≥1 failure_mode / no silent modality shift / trace sink)· 結構化 user_journey + failure_modes schema · `@implements`/`@enforces` 下沉程式碼(§4N/§4O 上溯節點)· REQ→FUNC G3 gate;claim-ID 用 §3.4;validator = Track B |
