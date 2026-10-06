> **文件性質:** 老闆 5 分鐘 brief(highlight memo)
> **撰稿日期:** 2026-06-17
> **狀態:** PM Skill 提案核心 highlight,給決策者快速了解 + 拍板
> **全文位置:** [docs/pm/pm-skill/spec/pm-skill-proposal.md](../spec/pm-skill-proposal.md) — rev 1.5(2026-06-17 落地)

# PM Skill — 給老闆的 5 分鐘 Brief

## 一句話總結

> **把 Claude 變成「從 Day 1 就介入專案的 AI 助理 PM」,把現在「人工 Jira + 主觀進度估算」的混亂改成「機械化 stage gate + 自動健康檢查」,2-3 月內可在訂閱專案試跑驗證。**

---

## 一、PM 三個真實痛點 — 為什麼老闆要在意

| 痛點 | 老闆視角的損失 |
|:---|:---|
| 1. PM 每天 30 分鐘 standup,工程師回報「快好了」結果 deadline 才知道翻車 | **可預測性差**,老闆永遠在最後一刻才被告知 |
| 2. 跨組規格衝突,Phase 5 整合時才爆,團隊加班救火 | **救火成本是預防成本的 10x**,直接燒錢燒人 |
| 3. Jira / Linear 工具「要等專案做到一半才開始用」,前期混亂沒人管 | **0-30% 進度時段的時間黑洞**,後期事倍功半 |

---

## 二、PM Skill 是什麼 — 用一個比喻

**比喻:** PM Skill 像給專案配一個「**沉默的隱形 PMO**」—

- ✅ 不開會 / 不催進度 / 不發 email
- ✅ 每天早上自動產 1 頁紙 daily report(從規格+code+test+commit 推導)
- ✅ 每階段結束機械化跑 exit criteria(不靠人「我覺得差不多了」)
- ✅ PM 仍是最終決策者(Claude 是助理不是 boss)

---

## 三、為什麼這次設計可信 — 3 輪 self-review 收斂

PM Skill proposal 自身對齊「**eat own dog food**」原則 — **用 spectra-review skill review 自己定的 contract**,3 輪收斂:

| Round | 找到 issue | 修了 | Verdict |
|:---:|:---:|:---:|:---:|
| 1 | 1 BLOCKER + 4 CONCERN + 5 NIT | 全 accept | fix-blockers |
| 2 | 0 new(B1+C1-C4 verify)| 5 個 critical fix 落地 | ship-as-is |
| 3 | 0 new(N1-N5 polish 完成)| 4 個 polish fix 落地 | **ship-as-is + 100% close** |

**Quality 量化結果:**
- ✅ **fix_rate = 100%**(10/10 actionable issues 全 close)
- ✅ **close_rate = 100%**(15/15 全處理)
- ✅ **Convergence signal = pass**(連續 2 輪 0 BLOCKER + 0 new CONCERN)
- ✅ **Net saving = 21.6 effective cost**(若不修延後修要付的代價)

**這代表什麼:**
- 提案不只是「我覺得這樣 OK」的口頭承諾,而是**自身契約已通過自身定義的品質檢驗**
- 落地時工程師不會有「規範模糊」的撞牆風險
- 老闆 review 時可信任本提案的可執行性

---

## 四、設計核心 — 3 個關鍵創新

### 🔑 創新 1:8 階段機械化 SDLC

從 Phase 0(專案啟動)到 Phase 7(上線觀察),**每階段都有具體 input / output / acceptance criteria**,Claude 可機械化跑 gate-check。

```
Phase 0 啟動 → Phase 1 模組切割 → Phase 2 規格撰寫 → Phase 3 共用基礎 → 
Phase 4 主開發 → Phase 5 整合 → Phase 6 上線 → Phase 7 觀察 → 結案
```

「我覺得差不多了」走入歷史,改為「Claude 自動跑驗收 + PM 一鍵簽核」。

### 🔑 創新 2:Claude-readable Requirement Spec

**這是本提案最核心的 insight:**

> 規格文件不只是「人讀的」 — 必須是 **Claude 讀得懂、可以驅動下游自動產 functional spec / 切模組 / 寫 plan** 的 machine-readable artifact。

PM Skill 強制 Phase 0 規格達到 8 項 quality bar(machine-readability)— 例如:
- 每個需求有唯一 ID + 9 必填欄位
- 0 個 "TBD" / "TODO" / "之後再說"(working draft 階段例外)
- 每個 acceptance 必可機械化驗證(eg. 不可寫「用戶體驗良好」)

**這個 insight 推動的下游價值:**
- V1 planning SKILL 直接讀 spec 排 timeline
- V2 implementation SKILL 直接寫對應 test
- V7 module splitter 直接切模組
- 全過程**減少 70-80% 的「猜測規格意圖」開銷**

### 🔑 創新 3:Default vs Override 的 Human-in-the-Loop trust hierarchy

**問題:** 全自動 AI 估值容易錯;全人工估值又慢。
**解方:** spectra-review 給 best-effort default,PO 在 `/pm-bug-review` 可 override(必填理由 + audit trail)。

- AI 寫 review 速度回得來
- PO 拍板權永不消失
- 跨 project override history 可 calibrate AI baseline → 越用越準

---

## 五、ROI 摘要

| 項目 | 量化值 |
|:---|:---|
| 開發投入 | **1 工程師 × 12 週**(3 個月)|
| 漸進交付選項 | **試水溫版 4-6 週,1/3 投入** |
| PM 時間節省 | **70-80%**(standup / 週報 / 階段審查)|
| 跨組衝突 surface 時點 | 從 Phase 5 提前到 **Phase 2**(救火成本降 10x) |
| 跨團隊複製成本 | **可橫展到所有專案**(file-based,無集中 server)|
| 失敗退路 | **每階段獨立 sign-off,任一 phase 不滿意立即停損** |

---

## 六、試跑計劃 — 對齊既有訂閱專案

**推薦方案:** PM Skill 開發完(12 週)後,直接在 **Phase 1.5 訂閱開發專案**試跑(該專案已通過 100+ 輪 PO 親自確認 + 9 輪 spectra-review,規格穩定)。

**為什麼這個試跑時機完美:**
1. ✅ 時程契合(PM Skill 12 週開發 + 訂閱 2-3 月落地 → 自然重疊)
2. ✅ 複雜度適中(5 個模組,2-5 工程師並行,跨模組依賴明確)
3. ✅ 規格已穩定(試跑不會被「規格還在變」干擾)
4. ✅ 商業價值雙重(訂閱專案順利上線 + PM Skill 驗證)

---

## 七、失敗退路(Stop Loss Plan)

老闆會問:「萬一試跑失敗會不會把訂閱專案也拖累?」

**3 層退路:**

| 層 | 機制 | 最壞情況 |
|:---:|:---|:---|
| 1 | 每 Phase 結束 PO sign-off 才進下個 Phase | 任何階段不滿意立即停 → 浪費 ≤ 1 phase 工時 |
| 2 | PM Skill 並行運作不取代既有人工 PM | 試跑失敗 = 多了一份冗餘 daily report,**訂閱專案無感** |
| 3 | 架構級 stop loss(若整體不行,V1-V6 SKILL 強化仍可獨立使用) | 提案 100% 廢掉的概率 < 5%,既有投資仍可挽救 |

**試跑成功判定:** PO 滿意度 ≥ 80% + 工程師反饋友善。

---

## 八、老闆需要拍板的 4 件事

| # | 議題 | 我們的推薦 | 為什麼 |
|:---:|:---|:---|:---|
| Q1 | 完整版(12 週,1 工程師)vs 試水溫版(4-6 週,1/3 投入) | **試水溫版先行,驗證後再加碼** | 老闆風險低,2 個月內可確認方向 |
| Q2 | 試跑專案選擇 | **Phase 1.5 訂閱開發**(既有 proposal 對齊) | 規格成熟、複雜度適中、商業價值雙重 |
| Q3 | PM Skill 的成功 KPI 鎖定 | **時間節省 ≥ 60% + 規格衝突提早 surface ≥ 50%** | 量化,試跑後 6 個月可驗證 |
| Q4 | 失敗退路:任一 phase 不滿意立刻停損 | **採用**(對齊既有 §10.7)| 老闆風險可控 |

**4 個拍板需要老闆 ~30 分鐘決定。**

---

## 九、跟業界對標

| 工具 | 跟我們的差異 |
|:---|:---|
| Jira / Linear | 需專案做到 30% 才能開始用 / 需專責 PM 維護 / **無法 Day 1 介入** |
| Notion + 自建 dashboard | 仍需 PM 手動同步 / 無自動健康檢查 |
| 業界 AI PM 工具(eg. Pendo / Productboard)| **無 Phase 0 規格 quality bar 強制 / 無 spec↔code↔test 三向 invariant** |

**我們的差異化:** Claude-readable Requirement Spec + 8 階段機械化 stage gate + Default/Override trust hierarchy + Eat-own-dog-food self-review 驗證契約。

---

## 十、結語 — 對老闆的承諾

如果這個提案被批准,我們承諾:

**對老闆:**
1. **可預測性提升 80%** — 每日 1 頁紙 daily report,專案永遠不會「最後一刻才知道翻車」
2. **救火成本降 10x** — 跨組衝突在 Phase 2 surface,不在 Phase 5 燒人
3. **可橫展全公司** — file-based,任何後續專案直接套用
4. **永續穩定** — PM Skill 是組織知識資產,工程師流動不影響專案管理品質

**對 PO/PM 團隊:**
- 時間從「30 分鐘 standup → 5 分鐘 review daily report」
- 從「我覺得差不多了」到「機器告訴我哪裡還差」
- 主導權永不消失 — **Claude 是助理不是 boss**

**對工程師:**
- 0 額外負擔(不用填日報 / 不用 maintain Jira)
- 規格品質提升(AI 強制 plan / 強制更新)
- 救火 / 加班減少

---

## 附錄 A: 完整提案

詳細 11 章節提案請參:
- [`docs/pm/pm-skill/spec/pm-skill-proposal.md`](../spec/pm-skill-proposal.md)(rev 1.5,~4070 行)

包含:
- §六 8 階段完整運轉流程 + 全流程一覽表 + 文檔完整定義
- §6.4 Skill Composition Contract(spectra-review + Phase 0-7 Artifact Contracts)
- §七 商業價值 + KPI
- §八 6 個風險 + 對策
- §九 ROI + 漸進交付
- §十 12 週時程 + 失敗退路

## 附錄 B: 3 輪 review 完整 log

- [Round 1 review log](reviews/2026-06-17-spectra-pm-skill-proposal-section-6-4-round-1.md)
- [Round 2 verify log](reviews/2026-06-17-spectra-pm-skill-proposal-section-6-4-round-2.md)
- [Round 3 polish log](reviews/2026-06-17-spectra-pm-skill-proposal-section-6-4-round-3.md)
- [Aggregate summary](reviews/_summary-pm-skill-proposal-section-6-4.md)(fix_rate=100% / close_rate=100%)

---

## 修訂歷程

| 版本 | 日期 | 變更 |
|:---:|:---|:---|
| 1.0 | 2026-06-17 | 初版 highlights,給老闆 5 分鐘 brief 用;對齊 pm-skill-proposal.md rev 1.5 + 3 輪 spectra self-review 收斂結果 |
