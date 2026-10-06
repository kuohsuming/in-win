# Output Profiles(類型驅動的欄位組)

Phase 2.5 通過審查、留下來的需求/問題,要格式化成給 AI 與執行用的結構。
**欄位不是固定模板,也不是逐條自由發揮,而是由「類型」決定。** 這份檔定義各類型該有的欄位組。

## 怎麼用(機制)
1. **先分類 domain**(這是什麼題目)→ 決定用哪個 profile。分類本身是**提議,需使用者核可**;請求跨類時,允許掛多個 domain 或分段套用不同 profile。
2. **每條再分 item_type**(需求/限制/假設/風險/問題)→ 決定這條的欄位形狀與驗收方式。
3. 照 profile 填欄位;**欄位由具體的問題與需求決定,不是每欄都要存在**。判準:少了它,人或後續 AI 會不會判斷錯、或無法驗收?會就留,不會就省。
4. 具體條目可在**有理由時**增減欄位,並附一句讓人可否決;**省略決策關鍵面向時必須提示**。
5. **命名沿用下方「受控詞彙」,出現才用、語意固定,不自創同義詞**——這是「欄位數量自由、但機器仍可一致解讀」的關鍵。
6. **底線**:凡「需求」類條目,至少要能回答「要什麼(statement)」與「怎樣算做到(success_measure)」。

---

## 受控詞彙(共用欄位名 → 對應 Phase 1 element)

| 欄位 | 對應 element | 意思 |
|------|--------------|------|
| `id` / `title` | — | 追溯用編號與一句話名稱 |
| `domain` | — | 題目類型(決定 profile) |
| `item_type` | — | 條目性質:需求/限制/假設/風險/問題 |
| `intent` | 真實目標 | 這條為哪個目標服務(job-to-be-done) |
| `motivation` | 脈絡/痛點 | 為什麼需要:誰、什麼情境、卡在哪、後果 |
| `statement` | 需求描述 | 要什麼——**描述意圖,不描述解法** |
| `boundary` | 可動/不可動+範圍+限制 | `in_scope`／`out_of_scope`／`hard_constraints`(附「誰說了算」) |
| `priority` | 取捨優先序 | Must / Should / Could / Won't |
| `success_measure` | 成功標準 | **怎樣算做到,要可判斷**(形式隨 domain 變) |
| `positive_case` / `negative_case` | — | 「算數 / 不算數・越界」的具體對照 |
| `stakeholders` | 利害關係人 | 誰決定、誰受影響、誰反對 |
| `risk` | 風險與失敗代價 | 做錯多痛、可不可逆、什麼絕不能發生 |
| `options` / `tradeoffs` | 既有嘗試與選項 | 檯面上的方案(含不做)與其取捨 |
| `status` | — | proposed / confirmed / rejected |
| `origin` | — | user_stated / ai_inferred(揣摩補全來的) |
| `open_questions` | — | 上交人裁的爭議 |

---

## item_type → 欄位形狀(不分領域,先套這層)

| item_type | 一定要有 | 不需要 / 重點不同 |
|-----------|----------|-------------------|
| **需求** | `statement` + `success_measure` | — |
| **限制** | `statement` + 來源(誰說了算)+ 剛性(硬約束/可談判) | 不需 `success_measure` |
| **假設** | `statement` + 如何驗證或證偽 + 若為假的影響 | `origin` 常為 ai_inferred |
| **風險** | `statement` + 可能性 + 影響 + 緩解方向 + 連到哪條需求 | 不需 `success_measure` |
| **問題(problem)** | `statement`(症狀)+ 推測根因(標提議)+ 影響 + 佐證 | 尚無解,不填 success |

---

## Domain Profiles

每個 profile 給:適用時機 / 預設必要欄位 / 建議欄位 / 「怎樣算做到」在該領域的範本。

### A. 產品・功能需求
- **適用**:要做或改一個產品功能。
- **必要**:`intent`、`statement`、`boundary`、`success_measure`、`priority`
- **建議**:`motivation`(使用者痛點)、`positive_case`/`negative_case`(使用情境/反例)、`stakeholders`、`risk`、edge_cases
- **達成範本**:可量測的行為或指標——條件式「當 X 則 Y」或數值門檻,e.g.「新用戶首日啟用率 ≥ 40%,可埋點量測」。

### B. 產品推廣(Go-to-market・行銷)
- **適用**:把已有產品/服務推向市場、獲取或轉換受眾。
- **必要**:`intent`(推廣目標:認知/獲客/轉換/留存/營收,擇定)、`target_audience`(**哪個分群,要具體**)、`key_message`(主打的價值主張)、`success_measure`(行銷 KPI)
- **建議**:`channel`(通路)、`funnel_stage`(漏斗位置)、`budget`(預算上限)、positioning/`competitor`(定位與競品)、`motivation`(受眾痛點)、`boundary`/constraints(品牌調性、法規、合規)、`risk`
- **達成範本**:漏斗指標 + 目標值 + 量測方式 + 期間,e.g.「首月經 X 通路獲取 500 註冊,CAC ≤ 300,ROAS ≥ 2」。
- **正/反例**:什麼樣的訊息與受眾算「命中痛點」vs「離題/自嗨」。

### C. 商業提案(Business proposal)
- **適用**:提出商業構想/投資/合作,爭取決策者批准或資源。
- **必要**:`intent`(要對方做的**那一個決定**)、`statement`(提案核心)、`success_measure`(批准條件或商業門檻)、`stakeholders`(決策者/買單者)
- **建議**:market(市場/機會規模)、business_model(如何賺錢)、financials(成本/收益/回收期)、`options`(替代方案含「不做」)、`risk`、`boundary`(資源與範圍)、`tradeoffs`
- **達成範本**:決策動作 + 商業門檻,e.g.「董事會批准並撥款 X」「毛利率 ≥ Y%,18 個月內回收」。

### D. 策略決策(Strategic decision)
- **適用**:在多個重大方向間做選擇。
- **必要**:`intent`(要決定什麼)、`options`(**選項全集,含維持現狀**)、decision_criteria(判準與權重)、`success_measure`(怎樣算選對)
- **建議**:`tradeoffs`(各選項取捨)、`risk`(尤重可逆性與最壞情況)、`stakeholders`、`boundary`(不可動的前提)、assumptions
- **達成範本**:多為判準對齊而非單一數字,e.g.「符合判準 X/Y/Z、且無不可逆的致命風險」,或一組事後可檢核的領先指標。

### E. 流程・營運改善(Process / Operations)
- **適用**:改善既有流程或營運環節。
- **必要**:`statement`(要改什麼)、`motivation`(現況痛點/瓶頸)、`success_measure`(改善指標)、`boundary`(範圍、不可動的系統或規則)
- **建議**:current_state(現況基線)、`stakeholders`(執行者/受影響者)、`risk`(過渡期風險)、`positive_case`/`negative_case`(改善後 vs 退化)
- **達成範本**:流程指標的前後對比,含基線與目標,e.g.「單件處理時間從 3 天降到 1 天,錯誤率 < 1%」。

### F. 內容產出(Content)
- **適用**:寫作/溝通類成品(文案、報告、講稿、貼文)。
- **必要**:`intent`(讀者讀完要做的**一個動作**)、`target_audience`(讀者的起點與立場)、`statement`(要傳達什麼)、`success_measure`(怎樣算有效)
- **建議**:`key_message`、tone(語氣/品牌聲音)、channel/length、`boundary`(不能說/敏感點)、`positive_case`/`negative_case`(命中 vs 離題)
- **達成範本**:讀者行為或反應,e.g.「≥ X% 點擊 CTA」「決策者回覆同意會面」;較軟時給可判斷的代理標準。

### G. 個人決策(Personal)
- **適用**:個人生活/職涯選擇。
- **必要**:`intent`(底層**真正在意的價值**)、`options`(含被忽略的第三條路)、decision_criteria(判準)、`success_measure`(怎樣算對得起自己)
- **建議**:`tradeoffs`、`risk`(可逆性/最壞情況)、timeframe、assumptions(分清情緒 vs 事實)
- **達成範本**:多為價值對齊,e.g.「符合我最不想犧牲的 X,且最壞情況我承受得住」。
- **注意**:提供思考架構與資訊,**不替人做決定、不給斷言式建議**。

### Z. 自訂 / 混合
- **適用**:請求跨多類、或不合任何一類。
- **作法**:允許一份文件掛多個 domain 或分段套用不同 profile;或直接從受控詞彙挑面向,臨時組一個 profile,把選用的欄位當**提議**交人核可。
- **底線不變**:凡「需求」類條目,至少含 `statement` + `success_measure`。

---

## Solution Profile(解法的輸出格式)

Phase 3 產出的每個解法,用這組欄位呈現。**規矩同需求 profile**:欄位依具體方案增減(不是每欄都填)、命名進 `glossary.md`、標 `origin`。
**必要集**:`summary` + `requirement_fit` + `success_metrics`(至少講清「是什麼、滿不滿足需求、怎麼算成功」)。

**分兩層,因為讀者與時機不同——人先決策、後執行:**

### 決策層(給決策的人:選不選這個方案)
| 欄位 | 意思 |
|------|------|
| `summary` | 概述,能獨立存在的 TL;DR:方案是什麼 + 攻擊哪個根因/需求,並濃縮「關鍵取捨 / 成本量級 / 主要風險」各一句 |
| `rationale` | 完整說明(for human):為什麼這樣設計、**為什麼是這個方案、放棄了什麼**——講邏輯與取捨,不是只列優點 |
| `requirement_fit` | 逐條對回需求(= 追溯矩陣):每條標 `完全滿足 / 部分 / 未滿足`,**未滿足附代價**。對映需求的 `success_measure / positive_case / negative_case`。價值在誠實,不報喜 |
| `vs_alternatives` | 與競品/對標對象比較(收斂自 Phase 2.7 對標矩陣,聚焦「本方案 vs 對標」) |
| `cost_effort` | 成本 / 資源 / 時程——多方案比較時沒有這欄無法選 |
| `risks_assumptions` | 這方案在什麼假設下才成立、最可能出錯處——防止方案被當成保證 |
| `success_metrics` | 上線後看什麼數字判斷有效(繼承需求 `success_measure`)——沒有它就無法驗收 |

### 執行層(給執行者:選了之後怎麼做)
**在決策層方案被核可選定後才展開**——沒選上的方案不必寫詳細步驟,省力。

| 欄位 | 意思 |
|------|------|
| `plan_for_human` | 里程碑級步驟:誰、大概何時、關鍵決策點——不是螺絲級細節 |
| `plan_for_ai` | **機器可執行**步驟:前置條件、輸入/輸出、用什麼工具、判斷分支、完成判準。**涉及實際動作(改檔/呼叫 API/發訊息)的步驟,標明「需人授權才執行」**——AI 執行也要有閘門 |

> right-size:快速諮詢可能只需 `summary` + `requirement_fit` + `plan_for_human` 三欄;完整提案才全開。別讓每個小方案被迫填滿。

---

## 一條完整條目長怎樣(產品推廣範例,示意)

```
id: PROMO-03
domain: 產品推廣
item_type: 需求
intent: 為新上線的方案建立目標客群的認知並帶進試用
motivation: 產品已上線 2 個月,但目標客群(中小企業財務)幾乎沒聽過;自然流量停滯
statement: 針對中小企業財務決策者,做一波以「省下對帳工時」為主訊息的獲客推廣
target_audience: 10–50 人公司的財務主管/老闆,目前用 Excel 手動對帳
key_message: 每月省下 8 小時對帳工時
channel: [LinkedIn 廣告, 財會社群內容, EDM]
funnel_stage: 認知 → 試用註冊
success_measure: 首月取得 500 試用註冊,CAC ≤ 300,試用轉付費 ≥ 15%(可追蹤)
budget: 上限 30 萬(行銷總監確認)
positive_case: 一位手動對帳的財務主管看到「省 8 小時」點進來註冊試用
negative_case: 把訊息打給大型企業 IT 部門(非目標、不痛)
risk: 若試用轉付費 < 5%,代表訊息命中但產品留不住,應先修產品再加碼投放
status: proposed
origin: ai_inferred(從「沒人知道我們」揣摩推廣目標,待確認)
open_questions: 主訊息要打「省時」還是「降錯誤率」?— 需你裁
```
