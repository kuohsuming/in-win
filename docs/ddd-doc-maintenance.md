# DDD Document Maintenance Guide

> **Purpose:** Lightweight maintenance rules for docs-first development
> **Status:** Governance guide only
> **Not SSOT:** This file does not replace L1/L2/L3 source documents
> **Audience:** Frontend, Backend, PM, QA, AI assistants
> **Last Updated:** 2026-03-29

---

## 1. Core Rule

先看文件能不能支撐這次開發。

- 如果文件已明確定義：照文件寫 runtime
- 如果文件不清楚、互相衝突、或產品決策改變：先改文件，再改 runtime

一句話：**文件先行，runtime 對齊。**

---

## 2. File Hierarchy

- **L1 / L1 Draft**：allowlist / contract / copy SSOT
- **L2**：architecture / domain / repository / persistence governance
- **L3 Primary**：某主題唯一主規格
- **L3 Supporting**：只補充 sequence / checklist / shared UI note
- **Archive**：歷史參考，不參與現行裁決

---

## 3. Writing Rules

### 3.1 One Topic, One Primary

每個 bounded context / topic 只允許一份 **Primary**。

- 新裁決只能寫在 Primary
- Supporting 不得重寫 Primary 的核心決策
- 若 Supporting 與 Primary 衝突，一律以 Primary 為準

### 3.2 Keep Layers Clean

- `action-inventory.md` 不寫業務規則
- `domain-model.md` 不寫 save timing / localStorage / temp cleanup
- UI spec 不直接定義 service method 清單
- Supporting checklist 不應變成第二份 spec

### 3.3 Archive Is Not Law

- `docs/archive/` 只放備份、舊版、歷史對照稿
- archive 內容不得覆蓋主層 canonical docs

### 3.4 Integration Notes Are The Home For Integration Analysis

**允許放入 integration notes 的內容：**

- 前後端整合狀態（哪些已接線 / 哪些是 mock / 哪些是 [GAP]）
- legacy mapping、payload gap、owner 對齊、landing map
- 指向 Primary / contract doc 的引用與說明
- gap table：描述缺口現狀，不定義如何解決
- API shape **舉例**（非 authoritative）：需明確標注 `// 僅作參考，SSOT 見 [contract-doc]`

**禁止放入 integration notes 的內容（嚴格限制）：**

| 禁止內容 | 正確落點 |
|---|---|
| API request / response schema 的正式 contract（含欄位說明、錯誤碼定義） | `*-contract.md` 或 Primary spec |
| 新的產品裁決、business rule、invariant | Primary spec（需 `Spec-Version` 更新） |
| 後端 onboarding 接線指引（"後端做完這清單才能上線"）| `backend-integration-guide.md` 或 Primary spec §Acceptance Criteria |
| 獨立於 tasks.md 的實作 checklist | `tasks.md` 或 Primary spec §Acceptance Criteria |
| 安全邊界聲明（security invariant） | `security-governance.md` 或 Primary spec §Security |
| 欄位命名決策（canonical field name） | `domain-model.md` 或 Primary spec §Data Contract |

**整體限制：**

- integration notes 不得只靠 integration notes 中的內容取得 authoritative 地位
- 若某段落的讀者需要「照它實作」，它就不應該在 integration notes——應升格至 Primary / contract doc
- 不得只留在聊天、PR 說明、或臨時 TODO
- 若同一輪整合跨多個 bounded context，可先建立一份 Supporting integration note 作為總表，再把 feature-specific 結論分流回各 topic integration notes / Primary docs
- integration notes 不得重寫 Primary 的核心產品裁決

**自我檢查問題（寫完每個新段落後問）：**

> 「若後端工程師只讀這段就去實作，這合適嗎？」
> 若答案是「是」→ 此段不應在 integration notes，應升格至 Primary / contract doc。

### 3.5 Frontend-Initiated Integration Annotation Rule

- 若整合由 frontend 啟動，分析一律以 `v2` UI surface 為錨點，legacy/backend source 僅作 reference
- 這次整合造成的文件增減，必須以清楚的小節標題或段落標記，例如 `Frontend-Initiated Integration`
- 這次整合造成的 runtime 程式增減，必須以簡短鄰近註解或可辨識命名標明屬於本次整合
- 若修改的是既有 `v2` 原生 runtime 檔案，註解至少應點出：這是本次整合、目前調整了哪個責任點、以及是否仍屬 transitional / backend-authoritative 行為
- changeset title / summary 應點出這是 frontend-initiated integration
- 若 `AzureLineBOT_ai` 的 legacy 檔案需要被注記或修改，應先複製到 `v2` 的明確 staging / reference / integration 路徑，再於 `v2` 內處理；不要直接在 legacy repo 原路徑上修改
- 這類 working copy 至少要明寫三項：`Frontend Notes`、`Backend Notes`、`Removal Status`
- `Removal Status` 建議固定使用：`Keep`、`Candidate Remove`、`Promoted`、`User Decision Required`
- 若未取得使用者明確決定，預設必須標記為 `User Decision Required`；不得自行刪除
- `Candidate Remove` 只代表可討論，不代表可直接刪除
- `Promoted` 代表該 copy 已升格成正式 `v2` 資產，不再視為可跟著 working copy 一起刪除
- 這條「copy into v2 first」規則屬暫行 integration governance，未來若 legacy track 結束，可與相關 staging copy 一併移除

### 3.6 Runtime Reverse Traceability Rule

每個 runtime 檔案必須能**反向追溯到管轄它的 spec**。

- 查詢工具：`runtime-spec-map.md`（所有 runtime 檔案 → Primary Spec 的反向對照表）
- 第一次在 V2/V5 任務中觸碰某 runtime 檔案時，若尚無 `@governed-by` header，必須在頂部加入：

```js
// @governed-by: docs/[primary-spec].md, docs/[integration-notes].md
// @layer: Router|Handler|Service|UseCase|Policy|Store|Gate
// @spec-map: docs/runtime-spec-map.md
```

- 「第一次觸碰時加」是增量策略；不需要一次性補完所有檔案
- 已標記的檔案：`script.js`、`js/store.js`、`content.js`

---

## 4. Change Workflow

> **前置條件**：本 workflow 遵守 `ai-principles.md §4.1` 的三條不可覆寫規則（Rule A/B/C）。

1. 先找這次主題的 canonical doc
2. **Dependency Impact Check（Rule C）**：列出本次修改影響的所有前後關聯文件與程式，查 upstream / downstream
   - File-level 查詢工具：`dependency-map.md §1–§6`（L1/L2/governance/runtime 的依賴清單）
   - Topic-level 查詢工具：`dependency-map.md §8`（Cross-Topic Dependency Map）— 觸發條件命中時升級細表
   - 若任務是 Wave 1 高風險主題（Auth Handshake / Settings Profile / Service Activation / Friend Add / OCR Flow / Identity Manager / Card Share-Send / Received Bizcard）→ 先讀 `ai-contract-pack-index.md` 對應條目
   - 規格清楚 → 納入同一任務一起改
   - 規格不清楚 → **停下來討論確認後再進行**
3. 若有新裁決，先改 Primary — **Spec-First Gate（Rule A）**
4. 若屬前後端 / legacy 整合分析，將 mapping / gap / owner / landing map 寫入對應 `*-integration-notes.md`
5. 再看 Supporting 是否需要改成引用或補充驗收
6. 最後才改 runtime code
7. 新增一筆 changeset 到 `release/changes/` — **Release Note Mandatory（Rule B）**
8. 若文件已 sunset / 備份 / 被取代，移入 `docs/archive/`

---

## 5. PR Self-Check

送出前至少確認：

- 這次改動的主題，是否只有一份 Primary 在定義核心規則？
- Supporting 文件有沒有偷偷新增新的產品裁決？
- 新增文件時，是否已標明是 Primary / Supporting / Reference Only？
- 這次整合分析是否已落到對應 `*-integration-notes.md`，而不是只停留在聊天？
- 若本輪是 frontend-initiated integration，文件與程式增減是否已清楚標註？
- 若本輪建立了 legacy working copy，是否已清楚標出 `Frontend Notes`、`Backend Notes`、`Removal Status`？
- 若本輪改了既有 `v2` 原生 runtime 檔案，是否已補上可辨識的 integration 鄰近註解？
- 這次變更若影響 action / copy / architecture boundary，是否已更新對應 L1/L2/L3？
- 若這次更動了某份 Primary spec 的核心業務規則或 data contract，是否已更新 `Spec-Version`？
- 若這次是新建 Primary spec，是否已補上最低結構（§7.5：Owner / Status / Spec-Version / Purpose / Invariants / Open Questions）？
- 是否把歷史備份誤留在 `docs/` 主層？

---

## 6. Backend Reading Rule

提供給後端時，**不建議把整個 `v2/docs` 當成「全部都要讀」的必讀清單**。

建議做法：

1. 先看 `docs/index.md`
2. 再看核心集合：
   - `action-inventory.md`
   - `copy-inventory.md`（有 UI key 對接需求時）
   - `system-architecture-flow.md`
   - `domain-model.md`
   - `repository-interfaces.md`
3. 最後只補讀與該需求直接相關的 L3 Primary

一句話：**可以提供整個 `v2/docs`，但後端的正式閱讀路徑應由 `docs/index.md` 導覽，不是整包亂讀。**

---

## 7. Spec Completeness Standard

> **Purpose**：定義「spec 是否清楚到可以寫 code」的判斷標準，讓 Rule A（Spec-First Gate）有明確的 pass/fail 判據。
>
> **Requirement spec 專屬（2026-07-02 OD-1）**：本節（M1–M5 + Type-Specific）為**所有 Primary spec 通用**的最低標準。**requirement spec** 在此之上另有專屬 authoring 規則（REQ ⇄ Golden Scenario ⇄ Anti-example 三元組不變式、create/update/delete CRUD delta、Coverage Expansion），其唯一 Primary 為 [`docs/pm/spec-authoring/requirement-spec-authoring-rules.md`](pm/spec-authoring/requirement-spec-authoring-rules.md)。撰寫 / 維護 requirement spec 時，本節 + 該 rulebook 兩者皆須通過。

---

### 7.1 Universal Minimum（所有 Primary spec 通用）

以下五項為**必要條件**。任一缺失 → spec 不清楚 → 必須補完後才能動 code。

| # | 條件 | 說明 |
|---|---|---|
| M1 | **Owner 已明確** | 哪個 bounded context / team / layer 負責此 spec 的決策 |
| M2 | **核心業務規則已列出** | 即使只有一條 invariant，也必須明文；不得只有標題沒有內容 |
| M3 | **Open questions 已明確標記** | 未解決的問題必須用 `[OPEN]` 或 `[?]` 顯性標出；不得讓讀者「猜」 |
| M4 | **不與其他 canonical doc 產生未解衝突** | 若有衝突，必須在 spec 中標明以哪份為準及原因 |
| M5 | **至少有一個具體場景或範例** | 純抽象描述不算完整；一個 example / happy-path 即可 |

---

### 7.2 Type-Specific Requirements

依 spec 類型，在 Universal Minimum 之上加：

#### 涉及資料（data contract / API / payload）

| # | 條件 |
|---|---|
| D1 | Input / output 資料結構已定義（欄位名、型別、必填/選填） |
| D2 | Error / edge case 處理方式已說明（即使只是「TBD by BE」也算已說明） |

#### 涉及狀態（stateful flow / 狀態機）

| # | 條件 |
|---|---|
| S1 | 狀態清單已列出（例：`pending → active → suspended`） |
| S2 | 每個狀態轉移的觸發條件已描述 |

#### 涉及 FE ↔ BE 跨層

| # | 條件 |
|---|---|
| X1 | FE 責任 vs BE 責任的切分已明確（哪邊負責驗證、計算、持久化） |
| X2 | 對應 integration notes 已存在或已排入建立計畫 |

---

### 7.3 Spec「不清楚」的判斷標準

以下任一情況成立 → spec 不清楚 → **必須停下來討論，不得繼續改 code**：

- 缺少 M1–M5 任一項
- data contract 存在但欄位型別缺失（對應 D1）
- 有狀態機但沒有 trigger 描述（對應 S1/S2）
- FE/BE 責任未分（對應 X1），且本次改動跨層
- Spec 引用了 archive 或已不存在的文件
- Spec 中有 `[TBD]`、`待討論`、`？` 等標記，且本次改動正好依賴該未解區域

> **判斷的最終依據是：「依照目前的 spec，另一個工程師能否獨立完成同樣的 implementation？」**
> 答案是否 → spec 不清楚。

---

### 7.4 遇到不完整 spec 的處置流程

```
Spec 不完整？
├─ 缺少 M1–M5（Universal Minimum）
│   └─ 輸出 Doc Change Proposal，告知使用者缺什麼，等確認後才繼續
├─ 缺少 Type-Specific（D/S/X）
│   ├─ 若本次改動剛好依賴該缺項 → 停下來討論
│   └─ 若本次改動不依賴該缺項 → 加 [GAP] 標記 + 在 integration notes 補缺口列表，可繼續
└─ 衝突未解
    └─ 停下來，列出衝突雙方，請使用者裁決，才繼續
```

**標記種類總表**（語意鎖死，不得混用 — 完整 Partial Exit 規則見 `skills/namecard-v2-ddd-guardian/references/task-closeout.md §10`）：

| 標記 | 語意 | 使用條件 |
|---|---|---|
| `[GAP]` | 已知缺口，本輪**主動**選擇不處理 | 必須同時在 integration-notes 補記錄；30 天後升級為 `[OPEN]` |
| `[TRANSITIONAL]` | 可運作但**不是最終路徑**；等待外部依賴 | 需在 integration-notes 標記外部依賴及清理時機 |
| `[DEFERRED ref]` | 本輪**明確不做**，不是忘了 | **必須**填入 ref（issue / task ID / integration-notes §section） |
| `[ACCEPTED ref]` | 風險已知且**暫時接受** | **必須**綁定三欄位：誰接受 / 為何接受 / 何時重開（缺一不可） |
| `[FIXED ref]` | 已解決的 spec 缺口 | 附 integration-notes §section ref；不是 partial exit 標記 |
| `[OPEN]` | 超過 30 天未清理的 `[GAP]` 升級形態 | 需在下次任務優先處理 |

**`[GAP]` 不能替代 Universal Minimum（M1–M5）**；M1–M5 缺一不可。`[GAP]` 只能用於 Type-Specific 或已知的 runtime 缺口。

---

### 7.5 新建 Primary Spec 的最低要求

新建一份 `*-spec.md` 或 `intent-map-*.md`，在第一個 commit 時至少需包含：

```markdown
# [Topic] Spec

> Owner: [bounded context / team]
> Status: Draft | Active | Deprecated
> Spec-Version: YYYY-MM-DD.1
> Last Updated: YYYY-MM-DD

## 1. Purpose
（一句話說這份 spec 管什麼）

## 2. Core Rules / Invariants
（至少一條業務規則）

## 3. Open Questions
（目前未解問題，用 [OPEN] 標記；若無，寫「無」）
```

沒有上述最低結構的文件 → 不算 Primary spec → 不能作為 Rule A 的 spec 存在依據。

---

### 7.6 Spec-Version 規則

**格式**：`Spec-Version: YYYY-MM-DD.N`（N 從 1 開始，同日多版遞增）

**何時更新**：

| 情況 | 動作 |
|---|---|
| 新建 Primary spec | 設為 `YYYY-MM-DD.1` |
| 更動核心業務規則、invariant、data contract | 更新為當日日期 + 遞增序號 |
| 補充 Open Questions、修改 example | 不需更新 Spec-Version（non-breaking） |
| Typo fix / 格式調整 | 不需更新 |

**意義**：
- Integration notes 的 `Verified Against` 可引用 `Spec-Version` 確認對齊的 spec 版本
- Rule C（Dependency Impact Check）時，若 integration notes 的 `Spec-Version` 與 Primary spec 不符，需確認是否需同步更新
- 不替代 git history；`Spec-Version` 是語意版本，不是 git commit hash
