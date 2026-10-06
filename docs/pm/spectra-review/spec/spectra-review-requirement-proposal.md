> **文件性質:** Skill Requirement Proposal — 內部技術規格(Tech Lead / Skill maintainer 用)
> **撰稿日期:** 2026-06-17
> **狀態:** 提案中,待 PO 拍板
> **依據:**
>   - 既有 `userSettings:spectra-review` SKILL.md
>   - 《密涅瓦的思考習慣訓練》(Minerva)4 大能力 framework
>   - PO + Claude 多輪 v1 discuss 設計收斂(2026-06-17)
> **整合脈絡:** 對齊 [PM Skill 提案計劃書](../../pm-skill/spec/pm-skill-proposal.md) Schema-driven Skill Composition 架構

# Spectra-Review SKILL Requirement Proposal — 引進 Minerva 4 大能力

## 0. Executive Summary

本提案強化既有 `spectra-review` SKILL,引進《密涅瓦的思考習慣訓練》4 大能力框架(批判思考 / 問題解決 / 複雜系統 / 決策思維),讓 spectra-review 從「**抓 BLOCKER 工具**」升級為「**訓練 PO 思考習慣的教練**」。

### 核心 Mapping(4 能力 → 4 強化點)

| Minerva 能力 | 既有 spectra-review 強項 | 強化點 | Output 變化 |
|:---|:---|:---|:---|
| **1. 批判思考** | 7 維度 review 既有 | 加 **Methodology section: Mental Lens** | 每輪 review 開頭明示 7 維度套用 4 能力的思考路徑 |
| **2. 問題解決** | 4-tier finding 已有 | 4-tier finding **強制三步驟結構**(命名 / 主張 / 追求) | 每個 issue 完整可執行,不再「issue 模糊 / fix 含糊」 |
| **3. 複雜系統** | V4 cross-doc review 已有 | 加 **Cross-Impact Analysis** field | 每個 finding 必標 cross-module / cross-spec impact + 識別臨界點 |
| **4. 決策思維** | Verdict 三選一(主觀)| 加 **Decision Tree** 段,量化 effective cost | Verdict 從主觀升為量化,給 PO 明確修不修的數字依據 |

### 預期效益

- **PO 創作力提升:** review 過程中內化 4 能力,寫下次 spec 時自我訓練
- **review 收斂速度加倍:** 9 輪 → 預計 3-5 輪
- **跨模組衝突早期發現:** 從 Phase 5 integration 提前到 Phase 2 規格期
- **PM Skill 整合加值:** Effective Cost 量化提供 daily report impact ranking
- **跨 project 累積:** Decision Log + Effective Cost 量化成為「組織知識資產」

### 投入

- **時程:** 對齊 PM Skill 整體 Phase C(Review Skills 強化,2 週)
- **改動範圍:** spectra-review SKILL.md + `_TEMPLATE-spectra.md` 新增 + output schemas 微調
- **PO 投入:** Phase A 鎖定 4 能力強化點(1 次 review)

---

## 1. 背景與動機

### 1.1 既有 spectra-review 的優勢

PO 在 V3 LIFF 訂閱方案開發過程中,跑了 **9 輪 spectra-review** 對 proposal 做深度審查,累積找出 100+ BLOCKERS / CONCERNS / NITS。這個過程驗證 spectra-review 的核心價值:

- **7 維度系統化:** naming / counting / completeness / governance / AC / OQ / backward compat
- **4-tier output:** BLOCKERS / CONCERNS / NITS / STRENGTHS 清晰分級
- **批判性視角:** 不 rubber-stamp,主動找問題
- **PO 認可:** 多輪 review 後 spec 品質明顯提升

### 1.2 既有的 4 個結構性限制

但同一段歷程也暴露 4 個結構性限制:

#### 限制 1:Issue 描述「為什麼是 issue」常常含糊
- BLOCKER 標題寫了,但「為什麼這是 BLOCKER」沒明文
- PO 看 review 要反問:「這 issue 對什麼有影響?」
- 結果:review 後仍要 PO 自己想 impact

#### 限制 2:跨 spec / 跨 module impact 沒 surface
- review single proposal 抓 issue OK,但「**這 issue 對其他 module / spec 的 cascade**」沒明示
- V4 cross-doc review 找到 10 個 conflict 是「事後 review」,**沒在 single review 階段就 surface**
- 結果:Phase 5 integration 才爆 — 對齊提案企劃案要解的核心痛點

#### 限制 3:Verdict 太主觀
- "ship as-is / fix BLOCKERS / revise" 三選一靠 PO 主觀
- 沒有「**如果不修這個 BLOCKER 會怎樣**」的反事實 simulation
- 結果:PO 拍板有時靠直覺,review 累積不會自動量化

#### 限制 4:PO 沒從 review 學到思考習慣
- review 抓問題,PO 修問題,**下次寫 spec 仍重複犯同類錯**
- spectra-review 是「**抓 fish**」,不是「**教釣 fish**」
- 結果:9 輪 review 才收斂,如果 PO 自己變強應該 3-5 輪就夠

### 1.3 為什麼選擇引進 Minerva 4 能力

《密涅瓦的思考習慣訓練》是 **全球頂尖大學的思考訓練 framework**,核心特色:
- 不教知識,**教「怎麼想」**
- 4 能力涵蓋從「分析」到「決策」完整光譜
- **practical** — 每個能力都有可操作的實踐方式

跟 spectra-review 4 個結構性限制 **完美對應**:
- 批判思考 → 限制 1(issue 含糊)
- 複雜系統 → 限制 2(跨 spec impact 缺)
- 決策思維 → 限制 3(verdict 主觀)
- 問題解決 → 限制 4(PO 沒學會思考習慣)

引進不是「強加 framework」,而是「**用 framework 填補既有缺口**」。

---

## 2. 4 能力 → 4 強化點 完整 Mapping(核心對應表)

### 2.1 能力 1 → 強化點 1:批判思考 → Methodology(Mental Lens)

| 維度 | Minerva 主張 | spectra-review 強化 |
|:---|:---|:---|
| 評估宣稱 | 對 claim 提問「站得住腳?」 | review 開頭明示 7 維度套用「Claim → Evidence → Verdict」結構 |
| 檢查邏輯 | cross-section consistency | 7 維度内 每維度都跑 cross-reference |
| 排除偏見 | 客觀檢查,不感情用事 | review 加 「Anti-Bias Self-Check」:「我這判斷可能錯,反例是什麼?」 |
| 理解而非爭辯 | 不只 reject,要 propose | 每個 BLOCKER 必含 Fix(對齊問題解決) |

**SKILL 改動:** 在 Methodology section 加「Mental Lens」段,明示這 4 個 mental act 怎麼在 review 過程套用。

---

### 2.2 能力 2 → 強化點 2:問題解決 → 4-tier finding 強制三步驟

**「命名 → 主張 → 追求」三步驟對應 4-tier finding 每個 item 強制 schema:**

| Minerva 三步驟 | 在 finding 內的 required field |
|:---|:---|
| 📛 命名(Identify) | `name`: 簡潔標題(eg. "Promo Quota Invariant 全 resource ≤ paid 未驗證") |
| 📣 主張(Assert) | `assertion`: 為什麼這是 issue + impact + probability + 引用 |
| 🎯 追求(Pursue) | `fix`: 具體 recommend(可執行,不模糊) |

**強制 schema 確保每個 BLOCKER/CONCERN 都完整可執行**。

**SKILL 改動:** Output schema 加 3 個 required fields,V3 SKILL / V8 SKILL 對齊。

---

### 2.3 能力 3 → 強化點 3:複雜系統 → Cross-Impact Analysis

**「森林火災案例」對應 spec drift 早期偵測:**

| Minerva 主張 | spectra-review 強化 |
|:---|:---|
| 全局觀 | 每個 finding 必填 `cross_module_impact` field |
| 臨界點識別 | Verdict 段加「Critical Hotspots」段 — 識別「一個小改 cascade 多 module」的 fragile points |
| 系統交互作用 | finding 加「dependency chain」分析 |
| 早期介入 | review 結尾加「Phase-aware recommendation」— 若此 issue 不在當前 phase 解,Phase X 會爆 |

**SKILL 改動:** Output schema 加 `cross_impact` 跟 `phase_aware` fields;Verdict 段加 Critical Hotspots subsection。

---

### 2.4 能力 4 → 強化點 4:決策思維 → Decision Tree(量化效用)

**「決策樹計算效用值」對應 verdict 量化:**

| Minerva 主張 | spectra-review 強化 |
|:---|:---|
| 避免確認偏誤 | 每個 BLOCKER 強制問「反事實 — 如果不修?」 |
| 效用值量化 | 算 `impact_score(0-100) × probability(0-1) = effective_cost` |
| 決策樹 | Option A(修)cost vs Option B(不修)cost 比較 |
| 反事實推導 | 寫「If do nothing, expected outcome:」 |

**SKILL 改動:** Output schema 加 Decision Tree section;Verdict 段給 effective cost matrix。

---

## 3. 各能力強化點詳細設計

### 3.1 強化點 1 詳細設計 — Methodology(Mental Lens)

**新 SKILL.md 段落範例:**

```markdown
## Mental Lens(必先讀,套用到 7 維度 review)

Spectra-review 跑 7 維度時,每維度都用以下 4 個 mental act:

1. **Claim → Evidence → Verdict**
   - Claim: spec 內的某個聲明(eg. "promo quota ≤ paid")
   - Evidence: spec 內哪行 / 哪段支撐這 claim?
   - Verdict: 證據是否足夠?是否有 counter-example?

2. **Cross-section consistency check**
   - 這聲明在 §A 跟 §B 是否一致?
   - 用詞 / 數字 / 範圍是否對齊?

3. **Anti-Bias Self-Check**
   - 我是不是因為熟悉這設計就放過了?
   - 我這判斷可能錯,反例是什麼?
   - 如果我是新人看這 spec,會困惑嗎?

4. **Understand-not-argue stance**
   - 不只說「這 issue」,要說「PO 為什麼這樣設計」
   - propose Fix 時對齊 PO 原意,不是強加自己偏好
```

**對 PO 的好處:** review 結束後 PO 自然吸收這 4 個 mental act,下次寫 spec 自我訓練。

---

### 3.2 強化點 2 詳細設計 — 4-tier Finding 強制三步驟

**現狀 format(自由發揮):**
```
1. Promo Quota Invariant 沒驗證未來 resource
   - Fix: 改 default 0
```

**強化後 format(三步驟強制):**
```markdown
#### B1. Promo Quota Invariant 全 resource ≤ paid 未驗證

**📛 命名(Identify)**
- spec §3.1 wrote "promo quota ≤ paid all resources" invariant
- Z54 helper 只驗 9 個 known resources,未涵蓋 future-added resources

**📣 主張(Assert)**
- **Why this is BLOCKER:** Phase 3+ 加 new resource 時,invariant 失效 → promo 可超越 paid → business model 反向
- **Impact level:** 8/10(business model 失效)
- **Probability:** 70%(Phase 3 加 enterprise resource 時極可能發生)
- **Evidence:** §3.1 line 240(invariant 聲明)+ §3.7 line 380(helper 實作)
- **Cross-Module Impact:**
  - Module 1(Sub schema): 需要 alter behavior
  - Module 3(Promo): 直接受影響
  - Module 5(admin tool): 新增 resource 流程要改

**🎯 追求(Pursue)**
- Z54 helper 改 `paid_limits.get(resource, 0)` default 0
- 加 schema 註解 enforce「所有 resource 都驗」
- backend test 加 `test_promo_quota_invariant_all_resources()` 涵蓋 future case

---
```

**對 PO 的好處:** PO 看一眼就知道「issue / why / how to fix」完整鏈條,不用反問。

---

### 3.3 強化點 3 詳細設計 — Cross-Impact Analysis

**新 finding required field:**

```yaml
cross_impact:
  affected_modules: [Module-1, Module-3, Module-5]
  cascade_depth: 2  # 1=直接, 2=間接, 3=遠端
  dependency_chain: "Module-3 promo logic → Module-1 sub creation → Module-5 admin"
  
phase_aware:
  current_phase: 2  # 規格撰寫
  if_not_fixed_now_breaks_at: 4  # Phase 4 主開發時爆
  estimated_rework_cost: high  # 越晚發現越貴
```

**Verdict 段新增「Critical Hotspots」:**

```markdown
## Critical Hotspots(臨界點熱區)

從本輪 review 找出的「**牽一髮動全身**」的 fragile points:

1. **`auth_tier` 命名概念**(Hotspot 等級: 🔥🔥🔥)
   - 改動會 cascade: V3 spec / frontend SKILL / backend SKILL / Schema / Module 1+3+4
   - 早期解(Phase 2): 改 5 處 spec
   - 晚期解(Phase 5): 改 5 處 spec + 5 處 code + 5 處 test → 成本 10x

2. **promo quota invariant**(Hotspot 等級: 🔥🔥)
   - 改動 cascade: 1 個 helper + 1 個 schema 註解 + 5 個 test
   - 建議現在解
```

**對 PO 的好處:** PO 知道「**哪些 issue 必須現在解,哪些可以延後**」,優先級量化。

---

### 3.4 強化點 4 詳細設計 — Decision Tree(量化效用)

**每個 BLOCKER 新增 Decision Tree 段:**

```markdown
**📊 Decision Tree**

| Option | Action | Cost(impact × probability) | Notes |
|:---|:---|:---:|:---|
| A | 不修(do nothing) | **80**(impact=10 × prob=0.8) | Phase 3 加新 resource 時必爆,屆時重 design 成本高 |
| B | 現在修(Z58 default 0) | **5**(impact=2 × prob=0.5) | 一行 default 改,後續 backend test 補 |
| C | 延後到 Phase 3 修 | **40**(impact=8 × prob=0.5) | 至少不在 Phase 2 卡,但 Phase 3 加 resource 時需特別注意 |

**📍 推薦:** Option B(差距 75 vs Option A)
**🔮 反事實:** 若不修,Phase 3+ 加新 resource 時 promo 套餐可能配置出「比 paid 更好的 free」反向情境
```

**Verdict 段新增「Effective Cost Matrix」:**

```markdown
## Effective Cost Matrix(本輪量化決策依據)

| Finding | Severity | If Fixed Now | If Deferred | Recommended |
|:---|:---|:---:|:---:|:---|
| B1. Promo Invariant | 🔴 | 5 | 80 | **Fix Now** |
| B2. ai_ocr Anchor | 🔴 | 10 | 50 | **Fix Now** |
| C1. Naming inconsistency | 🟡 | 3 | 15 | Fix Now |
| C2. CSS namespace | 🟡 | 8 | 8 | Defer OK |
| N1. Audit log format | 🟢 | 2 | 2 | Optional |

**總體 Recommendation:** Fix B1+B2+C1 immediately(total cost 18),defer C2+N1
```

**對 PO 的好處:** PO 拍板有量化依據,不靠主觀直覺;**review 累積這些數字 → 跨 project 形成「組織決策資料庫」**。

---

## 4. 強化後的 Review Log 完整範例

### Before(既有 spectra-review,簡化)

```markdown
**🔴 BLOCKERS**

1. Promo Quota Invariant 沒驗證未來 resource
   - Fix: 改 default 0

**Recommend:** fix BLOCKERS + #X then apply
```

### After(引進 Minerva 4 能力後)

```markdown
# Spectra-Review Round N — <target>

> **Date:** YYYY-MM-DD
> **Target:** docs/foo-proposal.md rev .15
> **Methodology:** Minerva 4 能力 framework(批判思考 / 問題解決 / 複雜系統 / 決策思維)

## Mental Lens(本輪 review 套用的 4 個 mental act)
- ✅ Claim → Evidence → Verdict
- ✅ Cross-section consistency
- ✅ Anti-Bias Self-Check
- ✅ Understand-not-argue stance

---

## 🔴 BLOCKERS(落地前必修)

### B1. Promo Quota Invariant 全 resource ≤ paid 未驗證

**📛 命名(Identify)**
- spec §3.1 wrote "promo quota ≤ paid all resources"
- Z54 helper 只驗 9 個 known resources,未涵蓋 future-added

**📣 主張(Assert)**
- Why BLOCKER: Phase 3+ 加新 resource 時 invariant 失效 → business model 反向
- Impact level: 8/10
- Probability: 70%
- Evidence: §3.1 line 240, §3.7 line 380
- **Cross-Module Impact:**
  - affected_modules: [Module-1, Module-3, Module-5]
  - cascade_depth: 2
  - dependency_chain: Module-3 → Module-1 → Module-5
- **Phase-aware:**
  - current_phase: 2
  - if not fixed now breaks at: Phase 4
  - estimated_rework_cost: high

**🎯 追求(Pursue)**
- Z54 helper 改 default 0
- 加 schema 註解 enforce
- backend test 加涵蓋 future case

**📊 Decision Tree**

| Option | Action | Cost | Notes |
|:---|:---|:---:|:---|
| A | 不修 | **80** | Phase 3 爆,重 design 貴 |
| B | 現在修 | **5** | 一行 default 改 |
| C | 延後 Phase 3 | **40** | 卡到時點不對 |

**📍 推薦:** Option B
**🔮 反事實:** Phase 3+ 加新 resource 時 promo 配置成「比 paid 更好」反向

---

## Critical Hotspots(臨界點熱區)

1. **B1 Promo Invariant**(Hotspot 等級: 🔥🔥)
   - 改動 cascade: 1 helper + 1 schema 註解 + 5 test
   - **建議現在解**

---

## ✅ STRENGTHS
- 7 表三層分工設計優雅
- promo 走 Rule 3 切換對齊既有 N4

---

## Effective Cost Matrix

| Finding | Severity | Fix Now Cost | Defer Cost | Action |
|:---|:---|:---:|:---:|:---|
| B1 Promo Invariant | 🔴 | 5 | 80 | **Fix Now** |
| B2 ai_ocr Anchor | 🔴 | 10 | 50 | **Fix Now** |

**Total cost if fix all now:** 15
**Total cost if defer all:** 130

---

## Verdict

**Status:** ⚠ Need fix BLOCKERS before apply
**Iteration:** 3/N
**Recommend:** Fix B1+B2 immediately(total cost 15 vs deferred cost 130)
**Next Round Focus:** 驗證 fix 是否正確套用,跨輪 Decision Log carry forward

---

## Mental Lens Reflection(給 PO 的思考訓練)

本輪 review 想分享給 PO 的觀察:

- **批判思考應用:** B1 是「invariant 看起來有寫,但未涵蓋 future case」 → 下次寫 spec 時自問「我這 invariant 是 universal 還是 case-by-case?」
- **複雜系統應用:** B1 cascade 3 個 module,**這就是經典臨界點** → 下次寫 spec 時自問「這 invariant 改動會影響幾個 module?」

(只在重大 finding 加 Reflection,避免每個都教讓 PO 累)
```

---

## 5. 對 PO 創作力 + 效率的具體助益

### 5.1 創作力提升 ⭐

每跑一輪 review,PO 自然吸收 4 能力,寫下次 spec 時自我訓練:

| 自問 | 對應能力 |
|:---|:---|
| 「我這 claim 站得住腳嗎?」 | 批判思考 |
| 「issue 命名清楚嗎?主張完整嗎?」 | 問題解決 |
| 「這改動會 cascade 多少 module?」 | 複雜系統 |
| 「不做的反事實是什麼?」 | 決策思維 |

**累積到第 N 個 project,PO 自然成為「Minerva-trained PO」 — 整個組織受益。**

### 5.2 效率提升 ⭐

- **4-tier finding 三步驟強制** → 看一眼就懂,不用反問
- **Decision Tree 量化** → PO 拍板速度倍增(不糾結)
- **Critical Hotspots 識別** → 一次解多 issue(以前可能分輪解)
- **跨輪 Decision Log 累積** → 收斂從 9 輪降到 3-5 輪
- **Mental Lens Reflection** → PO 自我訓練,下個 project 一開始就更穩

---

## 6. 對 PM Skill 整合的加值

`spectra-review` 強化後產出 **更結構化、更量化** 的 review log,讓 PM Skill 接收更精準:

| 強化點 | PM Skill 受益 |
|:---|:---|
| **Decision Tree 量化** | PM Skill 寫 daily report 時抽 `effective_cost` 給 actions 排優先級 |
| **Cross-Impact Analysis** | PM Skill 識別 critical path 時用 `affected_modules` + `cascade_depth` |
| **Phase-aware field** | PM Skill 跑 `/pm gate-check` 時知道「這 BLOCKER 卡哪個 phase」 |
| **Effective Cost Matrix** | PM Skill weekly digest 整理「本週 cost saved by fixing now」KPI 數據 |
| **三步驟強制 schema** | PM Skill parser 對齊 stable contract,不解析 ambiguous text |

**對齊 PM Skill「Schema-driven Skill Composition」核心架構** — review log 變成 PM Skill 可信任的 structured input。

---

## 7. 風險與對策

| # | 風險 | 對策 |
|:--:|:---|:---|
| 1 | Review report 字數 2-3x | **選擇性套用** — BLOCKER 全套用,NIT 精簡;PO 可指定 `/spectra-review --lite` 模式 |
| 2 | PO 學習曲線 | 前 1-2 輪附 mini 教學,後續省略;Mental Lens Reflection 只在重大 finding 加 |
| 3 | Effective Cost 量化過於主觀 | impact / probability 用 calibration table,PO 鎖定後標準化 |
| 4 | 跟既有 spectra-review backward-compat | 既有 inline 4-tier 維持為「base mode」,Minerva 4 能力是「enhanced mode」可選 |
| 5 | SKILL.md 改動需 PO 鎖定 | 對齊既有 governance,一次 review 通過後鎖定 |
| 6 | Decision Tree 數字 PO 不信任 | 提供「歷史對照」 — 過去 9 輪 review 的 effective cost 重新算給 PO 看 |
| 7 | 跨 project 標準化 | impact / probability calibration 設「組織 baseline」,新 project 沿用 |

---

## 8. SKILL.md 改動範圍

### 8.1 新增 sections

```markdown
新加 sections in SKILL.md:

## Mental Lens(批判思考)
   - 4 個 mental act 詳述
   - 跟 7 維度的映射

## Finding Schema(問題解決)
   - 三步驟強制 schema 規範
   - required fields: name / assertion / pursuit
   - optional: cross_impact / decision_tree

## Cross-Impact Analysis(複雜系統)
   - cascade_depth / dependency_chain / phase_aware
   - Critical Hotspots 段格式

## Decision Tree(決策思維)
   - effective_cost 計算公式
   - 反事實段
   - Effective Cost Matrix verdict 段

## Reflection Section(訓練 PO)
   - 只在重大 finding 加
   - 對齊 4 能力哪個維度
```

### 8.2 修改既有 sections

| 既有 section | 改動 |
|:---|:---|
| Output Format | 加入新 schema,backward-compat 標 「base mode」 vs 「enhanced mode」 |
| What to Check | 7 維度内每維度加「套用 Mental Lens」說明 |
| Verdict 段 | 加 Critical Hotspots + Effective Cost Matrix |

### 8.3 Backward-Compat 策略

- **既有 9 輪 review log** 不需重做(舊版仍 valid)
- 既有 SKILL invoke `/spectra-review <target>` 預設走 enhanced mode
- `/spectra-review --lite <target>` 走 base mode(維持既有行為)
- Output schema 加 version field:`schema_version: "enhanced-v1"`

---

## 9. 落地計畫

對齊 PM Skill 提案企劃案的 **Phase C(Review Skills 全強化,2 週)**:

### Phase A:設計鎖定(3-5 天)

- ✅ 本提案 PO review + 拍板 4 能力強化點 mapping
- ✅ Mental Lens 4 個 mental act 鎖定 wording
- ✅ Finding schema required fields 鎖定
- ✅ Decision Tree 量化公式 calibration

### Phase B:SKILL.md 落地(5-7 天)

- ✅ 更新 `spectra-review` SKILL.md(對齊 §8 改動範圍)
- ✅ 建立 `docs/reviews/_TEMPLATE-spectra.md`(extends base `_TEMPLATE.md`)
- ✅ 更新 `docs/pm/output-schemas.md` 加 spectra-review schema 段
- ✅ Backward-compat 測試(跑 `/spectra-review --lite` 確認既有行為維持)

### Phase C:試跑驗證(3-5 天)

- ✅ 對 1 個既有 proposal 跑 enhanced spectra-review
- ✅ PO 評估 output 是否符合預期
- ✅ Effective Cost Matrix 數字 calibrate
- ✅ iterations 收斂(預期從 9 輪降到 3-5 輪)

### Phase D:對接 PM Skill(3-5 天)

- ✅ PM Skill 加入 parser 讀 spectra-review schema 新 fields
- ✅ Daily report 加 `effective_cost` ranking
- ✅ Critical Hotspots 整合到 PM `/pm health-check`
- ✅ Cross-project 累積 calibration baseline

**總計:** 約 2 週(對齊 PM Skill Phase C)

---

## 10. Open Questions

| OQ | 議題 | 待 PO 拍板 |
|:--:|:---|:---|
| 1 | Mental Lens 4 mental act 的 wording 是否完全採我提的版本?還是 PO 想自訂? | PO 用自己 framing 可能更貼近實際思考路徑 |
| 2 | Decision Tree 量化的 impact scale(0-10 vs 0-100)?probability scale(0-1 vs %)? | 影響跨 project 一致性 |
| 3 | Effective Cost 公式是 `impact × probability` 還是更複雜(eg. 含 time-to-fix)? | 越複雜越主觀,trade-off |
| 4 | Reflection Section 是否每輪都寫?還是只重大 finding? | 字數 vs 訓練效益 trade-off |
| 5 | 強化後 SKILL.md 預期長度 | 從目前 ~100 行 → 預估 ~300 行,是否接受? |
| 6 | enhanced vs lite mode 是「opt-in」還是 default | 推薦 default enhanced + lite 為 opt-out |
| 7 | 既有 9 輪 review log 是否補 enhance metadata? | 推薦不補(成本高,新 project 開始用)|
| 8 | 4 能力是否套用到 V3 / V8 review? | 推薦套用 — 三個 review SKILL 一致 |
| 9 | Calibration baseline 何時鎖定? | 推薦 Phase C 試跑後鎖定 |

---

## 11. Verdict + Recommendation

### 整體 Verdict

✅ **強烈推薦引進 Minerva 4 能力到 spectra-review**。

理由:
1. 4 能力跟 spectra-review 4 個結構性限制 **完美對應**,不是 forced fit
2. 引進不打破 backward-compat(enhanced mode opt-in)
3. 對 PO 創作力 + 效率有具體可見的提升路徑
4. 對 PM Skill 整合加值顯著(Schema-driven 架構更完整)
5. 跨 project 累積成為「組織知識資產」

### 預期 ROI(對齊 PM Skill 整體 ROI)

| 投入 | 產出 |
|:---|:---|
| 2 週 SKILL 強化(對齊 PM Skill Phase C) | review 收斂從 9 輪 → 3-5 輪 |
| 1 次 PO 鎖定 review | review 品質提升 → spec quality 提升 |
| 跨 project calibration baseline | 跨 project 規格決策資料庫累積 |

**首年 ROI 估計:** **5-10 倍投入回收**(主要來自 review 輪數降低 + PO 創作力提升)

---

## 12. References

- 既有 `userSettings:spectra-review` SKILL.md
- 既有 9 輪 spectra-review 累積 — `2026-06-11-service-package-schema-proposal.md` Revision history
- 《密涅瓦的思考習慣訓練》— Minerva 4 大能力 framework
- [PM Skill 提案計劃書](../../pm-skill/spec/pm-skill-proposal.md) — Schema-driven Skill Composition 上下文
- [Review Template](reviews/_TEMPLATE.md) — base schema
- [Sample Round 1 Cross-Module Review](reviews/2026-06-17-round-1-cross-module-review.md) — format 範本

---

## 13. Revision

| Rev | 日期 | 變更 |
|:---|:---|:---|
| 1.0 | 2026-06-17 | 初版,引進 Minerva 4 大能力(批判思考 / 問題解決 / 複雜系統 / 決策思維)強化 spectra-review,訓練 PO 思考習慣,對齊 PM Skill Schema-driven Skill Composition 架構 |

---

**作者備註:** 本提案不只強化一個 SKILL,而是**透過 spectra-review 把 Minerva 思考訓練機制 embed 到 PO 跟 Claude 的日常協作裡**。每跑一輪 review,PO 都在訓練自己的批判思考 / 問題解決 / 複雜系統 / 決策思維能力。**這不是工具升級,是思考方式升級**。

我們建請 PO 拍板 §10 Open Questions,授權啟動 Phase A 設計鎖定。技術團隊已 ready,設計收斂完成。**剩下的,是 PO 一聲令下,我們就開始**。
