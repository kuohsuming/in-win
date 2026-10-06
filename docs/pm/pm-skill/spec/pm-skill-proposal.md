> **文件性質:** 提案計劃書(給決策者)
> **撰稿日期:** 2026-06-17
> **狀態:** 提案中,待 決策者 授權正式啟動

# AI 專案助理(PM Skill)— 提案計劃書

---

## 📑 目錄

| 章節 | 內容 |
|:---|:---|
| [一、為什麼需要做這件事?](#一為什麼需要做這件事) | 真實困境 + 不做的代價 |
| [二、整體願景](#二整體願景) | 4 個核心目標 |
| [三、核心構想](#三核心構想--claude-成為-pm-的-ai-助理) | AI 助理比喻 + 成功突破點 |
| [四、為什麼不選 Jira / Linear?](#四為什麼不選-jira--linear--替代方案比較) | 替代方案比較 |
| [五、它如何運作?](#五它如何運作故事化情境) | 5 個故事化情境 |
| [六、PM Skill 完整運轉流程](#六pm-skill-完整運轉流程從-day-1-到結案) | **8 個階段 / 誰進場 / 允收標準** ⭐ |
| [七、對組織的好處](#七對組織的好處商業價值) | 商業價值 + 業界對標 + KPI |
| [八、風險與對策](#八風險與對策) | 6 個風險 + 對策 |
| [九、投入與回報](#九投入與回報roi-預估) | ROI 預估 |
| [十、時程規劃](#十時程規劃) | PM Skill **建置**時程 + 試跑 + 失敗退路 |
| [十一、結語 + 待決策事項](#十一結語) | 4 個待 老闆 拍板問題 |

---

## 一、為什麼需要做這件事?

### 一個真實的困境

每個專案管理者(PM / PO)都遇過這個情境:

**早上九點,你打開電腦,腦袋裡浮現一連串問題:**
- 昨天 5 個工程師各自做了什麼?
- 哪個 milestone 應該今天完成?有完成嗎?
- 有人卡關了嗎?還是默默在加班但沒講?
- 跨組之間有沒有規格衝突?
- 我們現在到底還能不能準時交付?

**你只能一個一個訊息去問:**
「小明,昨天進度?」
「阿華,那個串接弄好沒?」
「美君,你那邊有 blocker 嗎?」

**收到的回覆品質不一:**
- 有人很完整
- 有人「都還 OK」
- 有人三天才回
- 有人說「快好了」結果還沒開始

**等你問完一輪,半天過了。** 然後下午又得開個會對齊,晚上還要寫週報。

**這還只是 5 個人的時候。** 如果是 10 人、20 人、跨多個專案 — 根本管不來。

### 為什麼這件事重要

PM 不是不重要,而是 **「PM 的真正價值」不在「催進度、問狀態、收日報」這些瑣事**。

PM 的真正價值在於:
- **看到全局** — 跨組依賴 / 風險預警 / critical path 識別
- **做關鍵決策** — 範疇調整、優先級重排、blocker 升級
- **協調溝通** — 跟客戶談、跟工程師談、跟老闆談

**但這些 high-value 工作,常常被「催進度的低 value 工作」吃光時間。** 然後 PM 過勞、決策品質下降、團隊不滿、專案 delay 連環爆。

**我們提出的這個方案,核心就是把「催進度收日報」這 70% 低 value 工作交給 AI 助理,讓 PM 專注 30% 高 value 工作。**

### 1.3 不做這件事的代價是什麼?

如果繼續維持現狀,我們承擔的隱性成本其實非常高:

**PM 過勞 → 決策品質崩潰**
PM 每天被進度催收消耗精力,真正需要思考的策略議題(eg. 跨部門資源衝突、客戶優先級重排、long-term roadmap)反而沒精神處理。結果 — **重大決策品質下降,事後改錯成本指數成長**。

**團隊規模化天花板低**
1-2 個 project 還能撐;3-5 個 project 並行時,**PM 開始忘記事情、開始漏 ping 人、開始錯過 deadline**。團隊規模想擴張(招更多 dev 接更多案),PM 變成瓶頸 — 不是因為 PM 不努力,是因為「pre-AI 的 PM 工作方式」物理上不 scalable。

**規格 / 決策歷史散落**
LINE 訊息、Excel、口頭討論 — 重要決定都在這些「不可搜尋」的地方。**3 個月後沒人記得當初為什麼這樣決定,改錯方向沒人發現,新人 onboarding 痛苦**。客戶問「為什麼當初這樣做?」 — PM 答不出來。

**跨組整合 surprise**
等到 integration 階段才發現跨組規格衝突 → 急著修 → 加班加爆 → 品質下降 → bug 不斷。這每個專案都會發生一次,**累計浪費的工時相當於 10-20% 的整體開發時間**。

**人才流失**
工程師討厭填表回報、討厭被 PM 追著問、討厭「規格沒對齊我先做我的」之後重做。**好工程師的離職有很大一部分是「組織管理 friction 過大」**。換一個高階工程師的成本約 NT$50-100 萬,而我們流失幾個就賠了。

### 這份提案的核心立場

「**不做這件事 vs 做這件事**」不是「投入 vs 不投入」的選擇,而是「**選擇承擔哪一種成本**」的選擇:

- **不做** → 持續承擔 PM 過勞 + 規模化天花板 + 規格散落 + 整合 surprise + 人才流失的隱性成本
- **做** → 一次性投入 3 個月 + 1 個 Tech Lead,換來上述所有問題的結構性解決

我們相信後者 ROI 顯著高於前者。

---

## 二、整體願景

我們希望建立一個 **「AI 專案助理」** — 它扮演 Claude 體系內的「Project Manager」角色,**但不取代真人 PM**,而是當 PM 的 **「force multiplier(力量乘數)」**。

具體來說:

**目標一、讓 PM 每天 5 分鐘掌握全局**
PM 不再需要四處 ping 工程師問進度。早上一杯咖啡的時間,打開 Claude 問一句「現況如何?」,AI 助理立刻產出:
- 全 5 組 / 50 個任務的進度狀態
- 誰落後 / 誰超前 / 誰已沉默幾天
- 跨組 blocker 識別 + critical path 風險
- 推薦的 3 個今天該做的決策

**目標二、讓工程師專注寫程式,不被「填表回報」打斷**
工程師最痛恨的事:**「我已經在做了,還要每天填日報跟你說我在做」**。
我們的方案 — 工程師用 Claude 寫程式碼的同時,**進度自然就被記錄了**。0 額外負擔,0 填表時間。

**目標三、讓專案進度品質可審計可追蹤**
過去:「老闆問 Phase 2 ready 沒?」→ PM 主觀判斷 → 可能漏東漏西。
未來:Phase 進到下一階段 **必須通過 machine-checkable 檢查表**,每一項都有檔案佐證,**沒過不能進**。對齊軟體業界 best practice。

**目標四、讓專案規模化能力提升**
- 1-2 人專案:PM 自己管即可
- 5 人專案:PM 用 AI 助理 → 跟管 2 人一樣輕鬆
- 10 人專案:加 cross-team review 自動化 → 仍 manageable
- **規模可以擴展,而不是線性堆 PM 人力**

---

## 三、核心構想 — Claude 成為 PM 的 AI 助理

### 一個簡單的比喻

想像一個高階 PM 配了一位 **「24 小時待命、永不疲倦、永遠記得所有細節」的私人助理**。

這位助理:
- 每天閱讀全部工程師的工作紀錄
- 寫出整潔的進度總表給 PM
- 標出今天該注意的 3 件事
- 記錄所有決策歷史(以後不會「你那時候不是說 X 嗎?」)
- 跑機械化檢查確認沒漏什麼
- 寫週報 / 月報 / 階段結案報告

**這就是我們要建的 AI 專案助理。**

但他不是「機器人 PM」,他是 **「PM 的助理」**:
- ✅ 他 surface 資訊
- ✅ 他建議下一步
- ✅ 他寫報告
- ❌ 他**不**取代 PM 做決定
- ❌ 他**不**直接指揮工程師
- ❌ 他**不**處理人際協調

**真人 PM 永遠是 boss,AI 助理是執行幕僚**。

### 為什麼這個構想會成功

過去想做類似的事(eg. Jira / Linear / Asana 等工具),都有一個結構性問題:**「工程師要花時間更新工具」**。結果 — 工程師不更新 → 工具失準 → 沒人信 → 大家又回去用 Excel 跟 LINE 群組。

**我們的設計突破點:工程師用 Claude 寫程式碼的同時,進度自動記錄。** 沒有「另外填表」這件事 — 因為「工作行為本身就是填表」。

具體運作:
- 工程師跟 Claude 討論任務(設定計畫)→ **計畫自動寫進規格檔**
- 工程師跟 Claude 寫程式(執行任務)→ **執行紀錄自動寫進規格檔**
- 工程師 commit 程式碼 → **commit 紀錄自動關聯到對應任務**

**3 個動作,3 個自動記錄,工程師完全不感知。** 然後 AI 助理就有 ground truth 了。

---

## 四、為什麼不選 Jira / Linear?(替代方案比較)

老闆可能會問:「市面上不是有 Jira / Linear / Asana / Notion 嗎?為什麼還要自己做?」

這是個好問題。我們仔細比較過:

### 4.1 替代方案 vs 本提案的比較表

| 維度 | Jira / Linear / Asana | Notion + 自建 dashboard | **本提案 AI 專案助理** |
|:---|:---|:---|:---|
| **工程師 friction** | 🚫 高(要學 + 填表)| ⚠ 中(要寫 doc + maintain)| ✅ **0**(自動產生)|
| **資料準確性** | ⚠ 看工程師多誠實 | ⚠ 看人 maintain 認真度 | ✅ **從 ground truth 推**(commit + spec) |
| **跨組衝突偵測** | 🚫 不做 | 🚫 不做 | ✅ **自動跑 weekly review** |
| **Phase Gate 機械化** | 🚫 不做 | ⚠ 需自寫 | ✅ **內建** |
| **規格 / 決策追蹤** | ⚠ comments 散落 | ✅ doc 內 | ✅ **檔案化 + audit trail 完整** |
| **客製化能力** | ⚠ 受工具限制 | ✅ 自由 | ✅ **完全客製,對齊既有 SKILL 體系** |
| **每年授權成本** | 💰 NT$ 5-30 萬(per team) | 💰 NT$ 2-10 萬 | 💵 **無**(僅 Claude API 用量) |
| **學習成本** | 🚫 高(每位 dev 都要學)| ⚠ 中 | ✅ **0**(用既有 V1/V2 SKILL)|
| **離線 / 私密性** | 🚫 雲端 SaaS | ⚠ 雲端 | ✅ **全 local file**,商業機密不外洩 |

### 4.2 為什麼 Jira / Linear 不夠?

**Jira / Linear 的本質是「工程師主動填表的系統」。** 這就是它的結構性弱點:

- 工程師不愛填 → 資料不準
- 不填會被罵 → 填得很簡略「OK 沒問題」
- 填了也不代表真的做了 → 仍要 PM 確認
- 跨組對接靠 comment / 開會 → 仍然散落
- 學新工具要時間 → 反而拖慢產能

**根本問題:** 它把資料的責任放在工程師身上,而工程師最不愛做這件事。

### 4.3 為什麼 Notion + 自建 dashboard 不夠?

- Notion 是好工具,但 **沒有 AI 在背後幫你整理**
- 自寫 dashboard 開發成本高(可能 3-6 個月一個工程師)
- 跨組衝突偵測 / Phase Gate / 健康檢查 — 全部要自己寫邏輯
- 維護成本高(每次需求變要改 code)

### 4.4 我們的方案為什麼是最佳解?

**我們選的這條路結合三個關鍵優勢:**

**(1) 0 工程師 friction —** 因為工程師「用 Claude 寫程式」本身就是工作,不是「額外的填表動作」
**(2) 從 ground truth 推 —** AI 助理讀 commit + spec,不靠 self-report
**(3) Built on existing infrastructure —** 對齊既有 V1-V6 SKILL 體系,不引入新工具

**這個組合在市面上沒有現成商品 — 我們是建構在 Claude 體系上的「AI-Native PM 解決方案」。** 這是市場空白,也是我們的競爭優勢。

### 4.5 老闆如果還是想用 Jira / Linear 怎辦?

完全可以。**本方案不衝突任何外部工具** — 老闆可以選擇:

- **方案 A:** 只用 AI 助理(本提案推薦)
- **方案 B:** AI 助理 + Jira 並行(AI 助理產 daily report,工程師 task 仍登 Jira 給對外 stakeholder 看)
- **方案 C:** 跑 6 個月本方案,評估後決定是否補用 Jira

**先做本方案不會擋住未來任何選擇,但完全不做本方案會持續承擔 §1.3 的隱性成本**。這是個 risk-free 的投資。

---

## 五、它如何運作?(故事化情境)

讓我們透過真實情境理解這套系統如何運轉。

### 情境一、PM 王經理的早晨

早上 9:00,王經理進辦公室,打開 Claude,輸入:**「今日進度?」**

10 秒後,Claude 回覆一份結構整齊的報告:

```
📊 今日專案概況
- 整體進度:62%(預期 60%,超前 2%)
- 預估完成日:2026-07-15(原訂 07-12,延後 3 天)

🎯 今日建議行動(優先級)
1. 🔴 同步小明 — M-1.3 任務已延宕 4 天,卡住 3 個下游任務
2. 🟡 確認阿華 — M-3.2 任務明天到期,需確認進度
3. ✅ 美君的模組 5 可以審 PR 了

🚨 工程師回報狀態
- 小明:🔴 5 天沒更新(異常)
- 阿華:✅ 今早剛更新
- 美君:✅ 昨天更新
- 阿宏:✅ 今早剛更新
- 玉珍:✅ 兩天前更新

🔥 關鍵路徑風險
M-1.3 卡住會連帶拖累 3 個下游 → 整體 delay 1 週
建議:今天優先解 M-1.3
```

王經理看完,立刻知道:
- 「先打電話給小明確認狀況」
- 「阿華我下午再 follow up」
- 「美君的 PR 我中午吃飯前審完」

**5 分鐘搞定。** 不需要四處 ping、不需要等回覆。剩下的時間用來做真正的 PM 工作 — 跟客戶談、跟老闆 sync、解決小明的 blocker。

### 情境二、工程師小華的工作日

小華早上開工。他打開 Claude,輸入:**「來討論 M-2.3 任務怎麼做」**(V1 規劃模式)

跟 Claude 討論 30 分鐘 — 設計 approach、列子任務、估時程、識別依賴。

**Claude 自動把這些寫進規格檔 `quota/functional.md` 的對應段落**:
- Status: ⏳ 規劃中
- 預定完成: 2026-06-25
- 計畫: 3 個子任務 + 完成標準
- 依賴: 等模組 1 的 M-1.3 完成

小華完全沒做任何「額外的填表動作」。他只是跟 AI 討論,內容自動歸檔。

下午,小華開始寫程式碼。他輸入:**「開始執行第 1 個子任務」**(V2 執行模式)

Claude 幫他寫 code、跑測試、commit。**過程中,Claude 自動更新規格檔**:
- Status: 🟡 進行中
- 執行紀錄:append「14:32 子任務 1 完成,commit a3f9d21」

小華下班前,完成第 1 個子任務。他離開辦公室時,**規格檔已經是最新狀態**。他沒有花任何時間「更新進度」。

隔天早上,王經理打開 Claude 看 daily report — 自動看到小華昨天完成了什麼。**完全不需要小華「填日報」**。

### 情境三、Phase Gate 階段審查

某天,所有工程師都覺得「Phase 4 應該做完了」。

王經理輸入:**「檢查 Phase 4 是否可以結案」**

Claude 自動跑檢查表:
```
🎯 Phase 4 結案檢查

✅ 4.1 所有模組任務 Status=已完成 — Pass
✅ 4.2 所有模組分支 PR 已合併 — Pass
✅ 4.3 單元測試全綠 — Pass
✅ 4.4 跨模組規格 review 通過 — Pass
🚫 4.5 健康檢查發現 2 個異常:
       - 模組 3 有 commit 但規格 Status 還是「規劃中」
       - 模組 5 寫了測試但沒關聯到任何 feature
✅ 4.6 程式碼 lint baseline 未增加 — Pass

判定:🚫 還不能結案,需先解 4.5 兩個異常

建議行動:
1. Ping 模組 3 owner 同步規格 Status
2. Ping 模組 5 owner 補測試 metadata
```

王經理看完,立刻知道哪兩個工程師要 follow up。**過去這個檢查可能需要 2 小時逐項對照,現在 30 秒**。

### 情境四、跨組規格衝突自動偵測

每週一早上,Claude 自動跑「跨模組規格 review」(V8)。

掃描全部 5 組工程師的規格檔 → 找出衝突 → 寫成審查報告:

```
🔴 BLOCKERS — 落地前必修

1. 模組 1 跟 模組 4 對「退費後 fallback」邏輯不一致
   - 模組 1 寫「退費後新建 verified_free 訂閱」
   - 模組 4 寫「退費後只改狀態不新建」
   - 影響:模組 2 的配額重置邏輯會跑錯
   - 建議:PO 拍板統一規則

2. 模組 3 跟 模組 1 對「promo 套餐期限」不一致
   - 模組 3 寫「90 天到期」
   - 模組 1 寫「終身有效」
   - 建議:對齊 PO 之前拍板的「終身有效」
```

王經理週一一進辦公室,**立刻看到本週要解的兩個關鍵衝突**。

過去 — 這種衝突可能要等到 Phase 5 整合才會 surprise,然後修很痛苦。
現在 — Phase 2 設計階段就抓到,修起來成本低。

### 情境五、跨輪審查的記憶累積

某個議題在 Round 1 review 拍板了:**「PO 決定模組 A 走 quota_lock,模組 B 走 quota_reject」**。

3 週後 Round 5 review,Claude 自動讀前面所有 Decision Log → **跳過這個議題不再 raise**。

過去 — 沒有這個記憶機制,Claude 可能會再次 raise 已收斂議題,PM 又得重新拍板一次,規則甚至可能被回滾(因為新 review 的 Claude 不記得舊決定)。

現在 — 所有決定持久化,**永遠不會回滾**,新工程師翻檔案也看得到歷史。

---

## 六、PM Skill 完整運轉流程(從 Day 1 到結案)

前面 §五 提供 5 個故事化情境,但那些是「日常運作的某一天」。**本章節展示從 Project Kick-off 第一天開始,PM Skill 如何完整介入專案 8 個階段的 end-to-end 流程**,讓大家完整看到 AI 助理跟人類角色的責任分工。

### 6.1 整體流程圖(高層次視角)

```
[Project Kick-off 啟動 ⏳]
   ↓ 老闆需求進來 → AI 助理「V0 設定模式」進場
   
🚪 Phase 0:啟動  ──── 老闆 + PM + Tech Lead
   ↓ PM 簽核 ✅

🚪 Phase 1:模組切割  ──── PM + Tech Lead + AI 助理 V7
   ↓ PM 簽核 ✅

🚪 Phase 2:規格撰寫  ──── 5 個工程師並行 + AI 助理 V1 + V8
   ↓ PM 簽核 ✅

🚪 Phase 3:共用基礎建設  ──── Tech Lead + AI 助理 V2 + V3
   ↓ PM 簽核 ✅

🚪 Phase 4:模組實作(主開發)  ──── 5 工程師並行 + AI 助理全套
   ↓ PM 簽核 ✅

🚪 Phase 5:整合測試  ──── 5 owner + Tech Lead + QA
   ↓ PM 簽核 ✅

🚪 Phase 6:上線部署  ──── DevOps + Tech Lead + PM
   ↓ PM 簽核 ✅

🚪 Phase 7:上線後觀察  ──── 全團隊 standby
   ↓ N 天穩定 → 專案結案 🎉
```

### 6.2 各階段詳細展開

---

#### 🚪 Phase 0 — Project Kick-off(專案啟動)

**主題:** 把老闆腦袋裡的「想做什麼」變成「可執行的專案輪廓」

**📥 如何進入(Entry Criteria):**
- 老闆有明確的「想做某件事」意向(口頭也可)
- 公司決定撥資源啟動專案
- 沒有正式 prerequisite — 這就是專案第一個階段

**📂 入場時需要的文件(Input Documents):**
- 無正式 doc(老闆口頭或一頁需求即可)
- (可選)市場研究 / 客戶需求紀錄

**何時誰進場:**
- **老闆** 帶著需求進場(eg.「我要做訂閱系統」)
- **PM(PO)** 領取需求,組織專案
- **Tech Lead** 提供技術可行性意見

**AI 助理介入:**
- **V0「設定模式」** — AI 助理協助 PM:
  - 把模糊需求結構化成 Requirement Spec
  - 設定團隊成員清單跟專長(Team Roster)
  - 設定 7 個階段的允收標準範本
  - 設定目標上線日

**人類做什麼:**
- 老闆:跟 PM 講清楚「想做什麼 / 為什麼 / 預算多少 / 何時要好」
- PM:用 V0 結構化老闆需求 + 評估團隊配置 + 設定時程
- Tech Lead:評估技術可行性 + 大略架構

**📤 允收標準(Exit Criteria):**
- ✅ Requirement Spec 已寫定(老闆確認方向對)
- ✅ 團隊成員 + 專長 已盤點(team-roster.md 鎖定)
- ✅ 目標上線日 已確認(state.md 內 target_release_date 鎖定)
- ✅ 預算 / 範圍約束 已列定(state.md 內 constraints 鎖定)
- ✅ 7 個階段的允收標準範本 已 setup(phase-gates.md 鎖定)
- ✅ **PM 簽核**(state.md 內 phase_0_signoff=true)

**📤 結案產出文件(Output Documents):**
- `Requirement Spec` — 老闆需求結構化版(主要產出)
- `docs/pm/state.md` — 專案狀態紀錄,含 current_phase / target_release_date / constraints
- `docs/pm/team-roster.md` — 工程師名單 + 各自專長 + 工作量配置
- `docs/pm/phase-gates.md` — 7 階段允收標準範本(可後續微調)

**估時:** 1-2 週

---

#### 🚪 Phase 1 — Module Splitting(模組切割)

**主題:** 把整個專案拆成獨立的「模組」,每個模組指派一位工程師主負責

**📥 如何進入(Entry Criteria):**
- ✅ Phase 0 已簽核(state.md 內 phase_0_signoff=true)
- ✅ Requirement Spec 已 ready
- ✅ Team Roster 已 ready
- ✅ Target release date 已鎖定

**📂 入場時需要的文件(Input Documents):**
- `Requirement Spec`(來自 Phase 0)
- `docs/pm/team-roster.md`(來自 Phase 0)
- `docs/pm/state.md`(來自 Phase 0)
- `docs/pm/phase-gates.md`(用來查 Phase 1 的允收標準)

**何時誰進場:**
- **PM** 主導切割決策
- **Tech Lead** 提供技術切割建議
- **(可選)1 位 senior 工程師** 加入 review 切割合理性

**AI 助理介入:**
- **V7「模組切分助手」** — AI 助理讀 Requirement Spec → 自動產出:
  - 模組列表(eg. 訂閱核心 / 配額控制 / 推廣套餐 / 退費 / 取消下載)
  - 各模組初步 owner 建議
  - 跨模組依賴關係圖
  - 各 module branch 命名建議
  - 共用檔案協調計畫

**人類做什麼:**
- PM 看 AI 切割提案 → 調整 → 跟工程師談 → 確認 owner 分派
- Tech Lead 評估切割合理性
- 工程師接受 / 拒絕 module ownership(對齊各自意願 + 專長)

**📤 允收標準(Exit Criteria):**
- ✅ 模組列表 已 final(eg. 5 個模組)
- ✅ 每模組有指定 owner(無爭議)
- ✅ 跨模組依賴圖 已畫(_plan.md 內有 dependency section)
- ✅ 共用檔案協調機制 已設(_plan.md 內有 Shared Files Coordination section)
- ✅ Branch 命名 確認
- ✅ **PM 簽核**(state.md 內 phase_1_signoff=true)

**📤 結案產出文件(Output Documents):**
- `docs/modules/_plan.md` — 模組切割計畫(主要產出),含:
  - 模組列表 + 各 owner
  - 跨模組依賴圖
  - Branch 命名 / Shared Files Coordination
- 更新 `docs/pm/state.md`(current_phase 推進到 phase-2)

**估時:** 3-5 天

---

#### 🚪 Phase 2 — Module Spec Writing(規格撰寫)

**主題:** 各模組工程師各自寫自己的詳細規格(Requirement / Functional / Plan)

**📥 如何進入(Entry Criteria):**
- ✅ Phase 1 已簽核(state.md 內 phase_1_signoff=true)
- ✅ `_plan.md` 已 ready(模組切割 + owner 派)
- ✅ 各 module branch 已建立

**📂 入場時需要的文件(Input Documents):**
- `docs/modules/_plan.md`(來自 Phase 1)
- `Requirement Spec`(來自 Phase 0,工程師寫 R spec 對齊用)
- `docs/pm/team-roster.md`(看誰負責哪 module)
- `docs/reviews/_TEMPLATE.md`(V8 review log 範本,工程師預覽會被怎麼 review)
- `docs/pm/output-schemas.md`(spec 必填欄位規範)

**何時誰進場:**
- **5 個 module owner**(工程師)並行寫各自 spec
- **PM** 監督進度 + 確認規格品質
- **Tech Lead** 提供技術疑問解答

**AI 助理介入:**
- **V1「規劃模式」** — 每位工程師跟 AI 討論該模組設計:
  - AI 自動把討論結果寫進 `functional.md` 各 feature 的 Plan section
  - 強制工程師填:approach / 子任務 / 完成標準 / 依賴
- **V8「跨模組規格審查」** — 每週 PM 跑一次:
  - AI 比對 5 個工程師寫的 spec → 找衝突 → 寫成 review report
  - PM 看 report 拍板衝突 → 工程師改 spec → 再 review

**人類做什麼:**
- 工程師寫 spec(透過 V1 引導)
- PM weekly sync 跟工程師對齊 → 拍板衝突
- Tech Lead 解技術問題

**📤 允收標準(Exit Criteria):**
- ✅ 5 模組各有 R/F/P 三份 spec(共 15 份),格式對齊 output-schemas.md
- ✅ V8 跨模組 review 通過(無 BLOCKERS,carry-over open 為 0)
- ✅ 跨模組依賴 已在各 functional.md 內明示
- ✅ 各 feature 已有 completion criteria 定義
- ✅ **PM 簽核**(state.md 內 phase_2_signoff=true)

**📤 結案產出文件(Output Documents):**
- `docs/modules/<name>/requirement.md`(× 5)— 該模組業務需求
- `docs/modules/<name>/functional.md`(× 5)— 該模組功能規格(含每 feature 的 Plan section)
- `docs/modules/<name>/plan.md`(× 5)— 該模組實作計畫
- `docs/reviews/<date>-round-N-cross-module-review.md`(N 輪)— 每週 review log
- `docs/decision-log.md`(append)— PO 拍板紀錄
- 更新 `docs/pm/state.md`(current_phase 推進到 phase-3)

**估時:** 2-3 週

---

#### 🚪 Phase 3 — Shared Infrastructure(共用基礎建設)

**主題:** 在工程師各自開發前,先建好「大家共用的地基」

> ⭐ **rev 1.17 amendment(2026-06-23 PO 拍板 Option A):** Phase 3 entry **AUTO triggers `/pm setup-worktree`** — shared infra commits 進 `dev/<project>` worktree,not main。原設計 Phase 3 → main 因 PO 抓到「Phase 3 commits 也是 半成品,project 沒 ship 就污染了 main」站不住,改 Phase 3 + Phase 4 同 worktree,Phase 5 QA pass 才合併回 main。對齊 always-deployable main invariant。

**📥 如何進入(Entry Criteria):**
- ✅ Phase 2 已簽核(state.md 內 phase_2_signoff=true)
- ✅ 5 模組 spec 全 ready(15 份 spec)
- ✅ V8 跨模組 review 已通過(明確哪些 helper 需共用)
- ⭐ **AUTO-trigger:** `/pm advance-phase 3` 自動跑 `/pm setup-worktree`(對齊 §E.8.2 rev 1.17)

**📂 入場時需要的文件(Input Documents):**
- 5 模組的 `functional.md`(看哪些功能需要共用 helper)
- 5 模組的 `plan.md`(看技術實作層需要共用什麼)
- V8 review log(看跨模組共用需求)
- 既有的 `laundry_db_create_tables.sql`(在此基礎上加新表)
- 既有的 `backend-integration-guide.md`(cmd 合約登錄)

**何時誰進場:**
- **Tech Lead** 主導建置共用基礎
- **(指定 1 位資深工程師組成 Schema Council)** 寫 DB schema
- **5 個 owner** 旁觀,提供需求(不主寫)

**AI 助理介入:**
- **V2「執行模式」** — Tech Lead 寫共用 helper / hook / utility
- **V3「規格審查模式」** — 確認共用設計品質

**人類做什麼:**
- Schema Council 統一寫 DB schema(7 張表 CREATE TABLE)
- Tech Lead 寫共用 helper(eg. `_get_effective_quota` 之類)
- Frontend Lead 設置 hook pattern(`window.__moduleInitHooks`)
- 設定 backend cmd 介接的「合約登錄」
- 寫 mock backend cmd 讓 frontend 不被阻塞

**📤 允收標準(Exit Criteria):**
- ✅ DB schema 寫入 SSOT(`laundry_db_create_tables.sql` 含新表)
- ✅ 共用 utility 全 ready(列在 `backend-integration-guide.md`)
- ✅ Hook pattern 設好(`index.html __moduleInitHooks` 上線)
- ✅ CSS namespace 約定 文檔化(各 module 前綴清楚)
- ✅ Mock cmd 可被 frontend 呼叫(讓 frontend dev 不被阻塞)
- ✅ Backend lint baseline 未增加(`bash lint.sh` F821/F 不增)
- ✅ V3 共用設計品質 review pass
- ✅ **PM 簽核**(state.md 內 phase_3_signoff=true)

**📤 結案產出文件(Output Documents — ALL on `dev/<project>` worktree per rev 1.17,not main):**
- 更新 `laundry_db_create_tables.sql`(schema SSOT,加新表)
- 共用 utility 程式碼(eg. `system_lib.py` 新加 helper)
- 更新 `backend-integration-guide.md`(cmd 合約登錄,含 mock cmd)
- 更新 `v3/index.html`(設好 `__moduleInitHooks` pattern)
- 更新 `v3/theme.css`(CSS namespace prefix 約定)
- Mock backend cmd 程式碼
- `docs/reviews/<date>-V3-shared-infra-review.md`(V3 review log)
- 更新 `docs/pm/state.md`(current_phase 推進到 phase-4)
- 更新 `docs/pm/state.md`:`worktree_branch: dev/<project>` + `phase_3_started_at: <date>`⭐ rev 1.17

**估時:** 1-2 週

---

#### 🚪 Phase 4 — Module Implementation(模組實作 — 主要開發階段)

**主題:** 5 個工程師並行寫程式碼,**這是時間最長、最關鍵的階段**

> ⭐ **rev 1.17 amendment(2026-06-23 PO 拍板 Option A):** Worktree `dev/<project>` 在 Phase 3 entry 時已建立,Phase 4 直接續用(不再 Phase 4 entry 才 setup-worktree)。Engineer 從 worktree pull(NOT from main)— Phase 3 shared infra 也在 worktree 上,main 仍 always-deployable。

**📥 如何進入(Entry Criteria):**
- ✅ Phase 3 已簽核(state.md 內 phase_3_signoff=true)
- ✅ DB schema / 共用 helper / hook / mock cmd 全 ready(已 commit on `dev/<project>` worktree per rev 1.17,not main)
- ✅ 各工程師可以從 **`dev/<project>` worktree** pull 共用基礎,在自己 module branch 開工

**📂 入場時需要的文件(Input Documents):**
- 5 模組各自的 `requirement.md` / `functional.md` / `plan.md`(來自 Phase 2)
- 共用基礎(來自 Phase 3):schema / helper / mock cmd / hook
- `docs/modules/_plan.md`(依賴圖,知道誰先誰後)
- `docs/pm/output-schemas.md`(spec 必填 / commit convention)
- 各自的 module branch(已建好)

**何時誰進場:**
- **5 個 module owner** 全力並行開發
- **PM** 每天用 PM Skill 看進度
- **Tech Lead** 解技術 blocker
- **(可選)QA** 開始準備測試 case

**AI 助理介入(全套):**
- **V1「規劃模式」** — 工程師拆解任務(寫 Plan section)
- **V2「執行模式」** — 工程師寫程式 + 跑測試(自動更新 Status + Execution Log + test-results)
- **PM Skill「進度報告」** — 每天 PM 跑一次,看 daily report
- **PM Skill「健康檢查」** — 偵測規格 vs 程式碼 vs 測試 是否一致
- **V8「跨模組審查」** — 每週跑一次
- **spectra-review「深度審查」** — PM 對某個關鍵設計想深度 review 時 on-demand

**人類做什麼:**
- 工程師寫 code(透過 V1+V2 引導)
- PM 每天 5 分鐘看 daily report,take action(ping 落後工程師)
- PM 每週主持 weekly sync(用 PM Skill weekly digest)
- Tech Lead 解 blocker / mentor
- QA 寫測試 case(對齊 functional spec)

**📤 允收標準(Exit Criteria):**
- ✅ 5 模組所有 feature `Status: ✅ done`(每 functional.md 內全 done)
- ✅ 5 模組 branch 所有 PR 已合併到 integration branch
- ✅ 各模組單元測試全綠(`test-results.md` 內全 pass)
- ✅ V8 跨模組 review 最後一輪通過(無 BLOCKERS / 無 carry-over open)
- ✅ PM Skill 健康檢查無 anomaly(spec ↔ commit ↔ test 三者一致)
- ✅ Backend lint baseline 未增(`bash lint.sh` F821/F 不增)
- ✅ Decision Log 完整(無 pending 拍板)
- ✅ **PM 簽核**(state.md 內 phase_4_signoff=true)

**📤 結案產出文件(Output Documents):**
- 程式碼(各 module branch 全 PR merged 到 integration)
- `docs/modules/<name>/tests.md`(× 5)— 測試 case
- `docs/modules/<name>/test-results.md`(× 5)— 測試結果(全 pass)
- 更新後的 `functional.md`(× 5)— 每 feature Status='done' + Actual date + Execution Log
- `docs/pm/reports/<date>-daily.md`(× N 天)— 每日 PM report
- `docs/pm/reports/<date>-weekly-digest.md`(× N 週)— 每週 digest
- `docs/reviews/<date>-round-N-cross-module-review.md`(× N 輪)— 跨模組 review log
- `docs/reviews/<date>-spectra-*.md`(若有 on-demand 深度 review)
- `docs/decision-log.md`(append 所有開發階段拍板)
- 更新 `docs/pm/state.md`(current_phase 推進到 phase-5)

**估時:** 4-8 週(依專案大小)

---

#### 🚪 Phase 5 — Integration(整合測試)

**主題:** 把 5 個模組合起來,跑端到端測試

**📥 如何進入(Entry Criteria):**
- ✅ Phase 4 已簽核(state.md 內 phase_4_signoff=true)
- ✅ 5 模組 code 全 ready(全 feature done,全 PR merged 到 integration)
- ✅ V8 跨模組 review 已 final pass
- ✅ 單元測試全綠

**📂 入場時需要的文件(Input Documents):**
- Integration branch(已含 5 模組合併 code)
- 5 模組的 `tests.md` / `test-results.md`(單元測試結果)
- 跨模組 E2E 測試 case(QA 在 Phase 4 期間準備好)
- 效能 baseline 規格(在 Requirement Spec 內)
- R-XX 真機驗測 case(若沿用既有訂閱開發 R-XX 規範)

**何時誰進場:**
- **5 個 owner** 共同負責整合對接
- **Tech Lead** 主導整合策略
- **QA** 全力跑 E2E 測試
- **PM** 監督整合進度

**AI 助理介入:**
- **V2** 寫整合膠水程式碼
- **PM Skill「健康檢查」** — 偵測整合階段新的不一致
- **V3「審查」** — 整合層 quality review

**人類做什麼:**
- 工程師解整合 bug
- QA 跑 E2E 真機驗測
- PM 主持 daily war room(整合衝刺期)
- Tech Lead 緊急 fix

**📤 允收標準(Exit Criteria):**
- ✅ 所有 module branch 已合到 integration branch(無 merge conflict)
- ✅ E2E 測試全綠(R-XX 真機驗測全 pass)
- ✅ 效能基準達標(對齊 Requirement Spec 的 SLA)
- ✅ 跨模組互動測試完成(eg. 訂閱 + 配額 + 退費 串通)
- ✅ PM Skill 健康檢查通過(整合層無 anomaly)
- ✅ **PM 跟老闆 walkthrough 簽核**(state.md 內 phase_5_signoff=true)

**📤 結案產出文件(Output Documents):**
- 整合層程式碼 + 修補 commits(整合 branch 上)
- E2E 測試結果報告(QA 寫,對應 R-XX case 對照)
- 效能測試結果報告
- `docs/pm/reports/<date>-phase-5-integration.md` — 整合階段總結
- `docs/reviews/<date>-V3-integration-review.md`(整合層 quality review)
- 更新 `docs/pm/state.md`(current_phase 推進到 phase-6)

**估時:** 1-2 週

---

#### 🚪 Phase 6 — Release(上線部署)

**主題:** 把東西推上 production

**📥 如何進入(Entry Criteria):**
- ✅ Phase 5 已簽核(state.md 內 phase_5_signoff=true)
- ✅ Integration branch 已 ready,E2E 全綠
- ✅ Rollback plan 草版 已寫
- ✅ Monitoring 配置 已準備

**📂 入場時需要的文件(Input Documents):**
- Integration branch(deploy 來源)
- Deploy script(eg. Azure Webapp 部署腳本)
- Rollback plan 草版
- Monitoring 配置文件
- Smoke test case list

**何時誰進場:**
- **DevOps** 主導部署
- **Tech Lead** 監督技術細節
- **PM** 對接 stakeholder 上線溝通
- **5 個 owner** standby 緊急 fix

**AI 助理介入:**
- **PM Skill** 對齊 deploy 跟規格 是否一致
- **V2** 緊急 hot fix 時的程式撰寫

**人類做什麼:**
- DevOps deploy 到 Azure Webapp
- 跑 smoke tests
- Tech Lead 確認 rollback plan ready
- PM 通知 stakeholder
- 老闆 announce

**📤 允收標準(Exit Criteria):**
- ✅ Production deployment 成功(Azure Webapp deploy 無錯誤)
- ✅ Smoke tests 全 pass(prod env 跑)
- ✅ Rollback plan ready 且 test 過(模擬 rollback 可成功)
- ✅ Monitoring 已上線(metrics + alerts 可運作)
- ✅ Stakeholder announce 完成(老闆 / 客戶 / 內部團隊)
- ✅ **PM 簽核**(state.md 內 phase_6_signoff=true)

**📤 結案產出文件(Output Documents):**
- Deploy log(完整部署紀錄,含時間 / 版本 / 操作人)
- Smoke test results(prod env 跑的結果)
- Rollback plan(已 test 通過的最終版)
- Monitoring dashboard URLs + alert 設置文件
- Stakeholder announce 通知紀錄
- `docs/pm/reports/<date>-phase-6-release.md` — 上線階段總結
- 更新 `docs/pm/state.md`(current_phase 推進到 phase-7)

**估時:** 1-3 天

---

#### 🚪 Phase 7 — Post-Launch Monitoring(上線後觀察)

**主題:** 上線後守 N 天,確認穩定

**📥 如何進入(Entry Criteria):**
- ✅ Phase 6 已簽核(state.md 內 phase_6_signoff=true)
- ✅ Production deploy 成功 + smoke pass
- ✅ Monitoring 已上線
- ✅ On-call 輪班表已建立

**📂 入場時需要的文件(Input Documents):**
- Production code 跑在 Azure Webapp
- Monitoring dashboard URLs
- On-call 輪班表
- User feedback 收集 channel(eg. LINE 客服 / 客戶 hotline)
- KPI baseline(對齊 §7.5 KPI 表)
- Rollback plan(萬一)

**何時誰進場:**
- **5 個 owner** standby 緊急 fix(輪班 on-call)
- **PM** 持續監控
- **DevOps** 看 metrics
- **QA** 收集 user feedback

**AI 助理介入:**
- **PM Skill「進度報告」** 持續產出
- **PM Skill「健康檢查」** 持續跑

**人類做什麼:**
- 解 critical bugs(若有)
- 收集 user feedback
- 評估 KPI 是否達標
- 寫 retrospective report

**📤 允收標準(Phase 7 結案 = 專案結案):**
- ✅ N 天(eg. 7 天)production 穩定(無 critical incident)
- ✅ Critical bugs 全部解決(P0 / P1 bug ticket 全 close)
- ✅ 效能在 SLA 內(對齊 Requirement Spec 鎖定的 SLA)
- ✅ User feedback 已收集 + categorize(positive / negative / feature request)
- ✅ KPI evaluation 達標(對齊 §7.5 鎖定的 KPI 目標)
- ✅ Retrospective 完成(team 共同 review,寫出 lessons learned)
- ✅ **PM 跟老闆 final sign-off**(state.md 內 phase_7_signoff=true,project 標記 closed)

**📤 結案產出文件(Output Documents):**
- Bug fix commits(若有,標明 P0/P1 priority)
- `docs/pm/user-feedback-log.md` — User feedback 收集 + categorize
- `docs/pm/reports/<date>-kpi-evaluation.md` — KPI 評估報告
- `docs/pm/reports/<date>-final-retrospective.md` — 專案 retrospective:
  - What went well
  - What didn't go well
  - Lessons learned
  - Recommendations for next project
- 更新 `docs/pm/state.md`(current_phase=closed,project 結案)
- 完整的 decision-log + review logs(歷史 audit trail 完整)

**估時:** 1-2 週

---

### 6.3 全流程一覽表(老闆視角)

#### 6.3.1 主要角色 / AI 助理 / 允收標準 一覽

| Phase | 名稱 | 誰主導 | AI 助理角色 | 關鍵允收標準 | 估時 |
|:---:|:---|:---|:---|:---|:---:|
| 0 | 啟動 | PM + 老闆 | V0 設定 | 需求 spec + 團隊 + 時程 鎖定 | 1-2 週 |
| 1 | 模組切割 | PM + Tech Lead | V7 切割 | 5 模組 + owner 派 + 依賴圖 | 3-5 天 |
| 2 | 規格撰寫 | 5 工程師並行 | V1 規劃 + V8 審查 | 15 份 spec + 跨模組 review 通過 | 2-3 週 |
| 3 | 共用基礎 | Tech Lead | V2 寫 helper + V3 審查 | Schema + helper + mock ready | 1-2 週 |
| 4 | **主開發** ⭐ | 5 工程師並行 | **全套 V1+V2+PM Daily+V8+spectra** | 全 feature done + 測試綠 + 跨模組 review 過 | **4-8 週** |
| 5 | 整合 | 5 owner + Tech Lead + QA | PM 健康檢查 + V3 | 整合測試全綠 | 1-2 週 |
| 6 | 上線 | DevOps + PM | PM 對齊 deploy | 部署成功 + smoke pass | 1-3 天 |
| 7 | 觀察 | 全團隊 standby | PM 持續監控 | N 天穩定 + bug 全解 | 1-2 週 |
| **總計** | | | | | **10-20 週** |

#### 6.3.2 完整流程 — 各階段 Input / Output / Acceptance 詳列

> 以下用清楚的「📥 Input → 📤 Output → ✅ Acceptance」三段對稱格式逐一列出 8 個階段,便於快速查閱。建議 PM / Tech Lead 列印當作專案 SDLC SOP 隨身攜帶。

---

##### 🚪 Phase 0 — 啟動(Project Kick-off)

**📥 Input Documents(入場必備)**

- 老闆口頭需求
- (可選)市場研究紀錄

**📤 Output Documents(結案產出)**

- Requirement Spec(主要產出)
- `docs/pm/state.md`
- `docs/pm/team-roster.md`
- `docs/pm/phase-gates.md`

**✅ Acceptance Criteria(允收標準)**

⚠ **核心要求:Requirement Spec 對齊 §6.4.10 Requirement Spec Artifact Contract 全部 Exit Bar**(不只是「老闆方向確認」這層 — 必須 machine-readable + 可驅動下游 V1/V2/V7/spectra-review)。

- ✅ Requirement Spec 已寫定 + 對齊 §6.4.10 Artifact Contract(`/pm validate-req-spec` 全 pass)
  - 對齊 §6.4.10 §B.1:review rounds ≥ §C scaling + 達 convergence
  - 對齊 §6.4.10 §B.2:0 BLOCKER / 0 CONCERN open;NITs ≤ cap;STRENGTHS ≥ min
  - 對齊 §6.4.10 §B.3:8 條 machine-readability bar 全達標
  - 對齊 §6.4.10 §B.4:每 REQ 11 必填欄位完整(含 golden_scenario + anti_examples)
  - 對齊 §6.4.10 §B.5:dependency graph 無 circular / 無 unresolvable
- ✅ 團隊成員 + 專長 已盤點(`team-roster.md`)
- ✅ 目標上線日 已確認(state.md `target_release_date`)
- ✅ 預算 / 範圍約束 已列定(state.md `constraints`)
- ✅ 7 階段允收標準範本 已 setup(`phase-gates.md`)
- ✅ Phase 0 Exit Check List(§6.4.10 §K)走完
- ✅ **PM 簽核**(state.md `phase_0_signoff = true`)

> **與既有 §A.1 Requirement Spec 描述的關係:** §6.3.4 §A.1 描述 Requirement Spec 用途 / 維護者;**§6.4.10 為其 quality contract,兩者互補**。

---

##### 🚪 Phase 1 — 模組切割(Module Splitting)

**📥 Input Documents(入場必備)**

- Requirement Spec(Phase 0 產出)
- `team-roster.md`(Phase 0 產出)
- `state.md`(Phase 0 產出)
- `phase-gates.md`(Phase 0 產出)

**📤 Output Documents(結案產出)**

- `docs/modules/_plan.md`(主要產出),包含:
  - 模組列表 + 各模組 owner
  - 跨模組依賴圖
  - Branch 命名規則
  - Shared Files 協調計畫
- 更新 `state.md`(推進到 phase-2)

**✅ Acceptance Criteria(允收標準)**

⚠ **核心要求:`_plan.md` 對齊 §6.4.11.B Module Plan Artifact Contract**(`/pm validate-module-plan` 全 pass + 對齊 §B.7 Exit Check List)

- ✅ 模組列表 已 final(2-10 模組,對齊 §B.3 module_count_in_range)
- ✅ 每個模組有指定 owner(無爭議,對齊 §B.3 unique_owner_per_module)
- ✅ 跨模組依賴圖 已畫,無 circular(對齊 §B.3 no_circular_module_deps)
- ✅ 每個 Phase 0 REQ 都被至少 1 module covered(對齊 §B.3 all_root_reqs_covered)
- ✅ 共用檔案協調機制 已設(對齊 §B.3 shared_files_coordinated)
- ✅ Branch 命名 確認
- ✅ Phase 1 Exit Check List(§6.4.11.B.7)走完
- ✅ **PM 簽核**(state.md `phase_1_signoff = true`)

---

##### 🚪 Phase 2 — 規格撰寫(Module Spec Writing)

**📥 Input Documents(入場必備)**

- `_plan.md`(Phase 1 產出)
- Requirement Spec(Phase 0 產出)
- `team-roster.md`(Phase 0 產出)
- `docs/reviews/_TEMPLATE.md`(V8 review 範本)
- `docs/pm/output-schemas.md`(spec 必填欄位規範)

**📤 Output Documents(結案產出)**

- `docs/modules/<name>/requirement.md`(× 5)— 各模組業務需求
- `docs/modules/<name>/functional.md`(× 5)— 各模組功能規格
- `docs/modules/<name>/plan.md`(× 5)— 各模組實作計畫
- `docs/reviews/<date>-round-N-cross-module-review.md`(× N 輪)— V8 review logs
- `docs/decision-log.md`(append PO 拍板紀錄)
- 更新 `state.md`(推進到 phase-3)

**✅ Acceptance Criteria(允收標準)**

⚠ **核心要求:N 模組 × 3 specs(R/F/P)對齊 §6.4.11.C Per-Module Spec Artifact Contract**(`/pm validate-module-spec --all` 全 pass + 對齊 §C.7 Exit Check List)

- ✅ N 模組各有 R/F/P 三份 spec(對齊 §C.1 Mandatory Sections)
- ✅ 全 spec 格式對齊 `output-schemas.md` + §6.4.11.C 補強 schema
- ✅ 每 feature 對齊 §C.2 per-feature schema(含 acceptance machine-checkable)
- ✅ 每 task 對齊 §C.3 per-task schema
- ✅ 4 層 traceability:root REQ → module REQ → feature → task(§C.4 structural_sanity)
- ✅ V8 跨模組 review 最後一輪通過(無 BLOCKERS,carry-over 為 0)
- ✅ 跨模組 touchpoints 已在各 `functional.md` 明示
- ✅ Phase 2 Exit Check List(§6.4.11.C.7)走完
- ✅ **PM 簽核**(state.md `phase_2_signoff = true`)

---

##### 🚪 Phase 3 — 共用基礎(Shared Infrastructure)

**📥 Input Documents(入場必備)**

- 5 模組 `functional.md`(看共用 helper 需求)
- 5 模組 `plan.md`(看技術實作需求)
- V8 review logs(看跨模組共用)
- 既有 `laundry_db_create_tables.sql`(schema SSOT)
- 既有 `backend-integration-guide.md`(cmd 合約登錄)

**📤 Output Documents(結案產出)**

- 更新 `laundry_db_create_tables.sql`(加新表)
- 共用 utility 程式碼(`system_lib.py` helper)
- 更新 `backend-integration-guide.md`(cmd 合約登錄)
- 更新 `v3/index.html`(`__moduleInitHooks` pattern 設好)
- 更新 `v3/theme.css`(CSS namespace prefix 約定)
- Mock backend cmd 程式碼
- `docs/reviews/<date>-V3-shared-infra-review.md`
- 更新 `state.md`(推進到 phase-4)

**✅ Acceptance Criteria(允收標準)**

⚠ **核心要求:Shared Infra outputs 對齊 §6.4.11.D Shared Infrastructure Artifact Contract**(`/pm validate-shared-infra` 全 pass + 對齊 §D.5 Exit Check List)

- ✅ DB schema 寫入 SSOT(對齊 §D.1 db_schema_changes,對齊 memory: backend_schema_change_workflow)
- ✅ 共用 utility 全 ready + documented(對齊 §D.1 python_helpers)
- ✅ Hook pattern + CSS namespace 文檔化(對齊 §D.1 frontend_shared)
- ✅ Mock cmd 可被 frontend 呼叫 + 簽名跟 real backend 一致(對齊 §D.1 mock_cmd)
- ✅ Backend lint baseline 不增(`bash lint.sh` F821/F 對齊 memory: backend_lint_workflow)
- ✅ Shared utility 測試 coverage ≥ 80%(對齊 §D.2 test_coverage_min)
- ✅ V8 共用設計 quality review pass
- ✅ Phase 3 Exit Check List(§6.4.11.D.5)走完
- ✅ **PM 簽核**(state.md `phase_3_signoff = true`)

---

##### 🚪 Phase 4 — 主開發 ⭐(Module Implementation)

**📥 Input Documents(入場必備)**

- 5 模組的 R/F/P spec(Phase 2 產出)
- Phase 3 共用基礎(schema / helper / mock cmd / hook)
- `_plan.md`(Phase 1 產出,依賴圖)
- `docs/pm/output-schemas.md`(spec 必填 + commit convention)
- 各 module branch(已建好)

**📤 Output Documents(結案產出)**

- 程式碼(各 module branch,全 PR merged 到 integration branch)
- `docs/modules/<name>/tests.md`(× 5)— 測試 case
- `docs/modules/<name>/test-results.md`(× 5)— 測試結果
- 更新後的 `functional.md`(× 5),每 feature:
  - `Status: ✅ done`
  - `Actual:` 日期已填
  - `Execution Log:` 完整紀錄
- `docs/pm/reports/<date>-daily.md`(× N 天)— 每日 PM 報告
- `docs/pm/reports/<date>-weekly-digest.md`(× N 週)— 每週 digest
- `docs/reviews/<date>-round-N-cross-module-review.md`(× N 輪)— V8 跨模組 review
- `docs/reviews/<date>-spectra-*.md`(若有 on-demand 深度 review)
- `docs/decision-log.md`(append 所有開發階段拍板)
- 更新 `state.md`(推進到 phase-5)

**✅ Acceptance Criteria(允收標準)**

⚠ **核心要求:Module Implementation outputs 對齊 §6.4.11.E Module Implementation Artifact Contract**(`/pm validate-implementation --all` 全 pass + 對齊 §E.7 Exit Check List)

- ✅ N 模組所有 feature `Status: ✅ done` + actual_completion 已填(對齊 §E.4 all_features_done)
- ✅ N 模組 branch 所有 PR 已合併到 integration branch
- ✅ 各模組單元測試 100% pass(對齊 §E.4 all_tests_passed)
- ✅ 每 feature 對應 ≥ 1 commit + ≥ 1 test case(對齊 §E.3 spec↔code↔test 三向 invariant)
- ✅ V8 跨模組 review 最後一輪 verdict=ship-as-is + 0 carry-over BLOCKER(對齊 §E.4 v8_final_round_verdict)
- ✅ PM 健康檢查無 anomaly(spec ↔ commit ↔ test 三者一致,對齊 §E.3)
- ✅ Backend lint baseline 不增(對齊 §E.4 lint_baseline_delta + memory: backend_lint_workflow)
- ✅ Decision Log 完整(無 pending 拍板,對齊 §E.4 decision_log_no_pending)
- ✅ Phase 4 Exit Check List(§6.4.11.E.7)走完
- ✅ **PM 簽核**(state.md `phase_4_signoff = true`)

---

##### 🚪 Phase 5 — 整合(Integration)

**📥 Input Documents(入場必備)**

- Integration branch(已含 5 模組合併)
- 5 模組的 `tests.md` / `test-results.md`(Phase 4 產出)
- 跨模組 E2E 測試 case(QA 在 Phase 4 期間準備)
- 效能 baseline 規格(在 Requirement Spec 內)
- R-XX 真機驗測 case(若沿用既有規範)

**📤 Output Documents(結案產出)**

- 整合層程式碼 + 修補 commits(integration branch 上)
- E2E 測試結果報告(對應 R-XX case 對照)
- 效能測試結果報告
- `docs/pm/reports/<date>-phase-5-integration.md`(整合階段總結)
- `docs/reviews/<date>-V3-integration-review.md`(整合層 quality review)
- 更新 `state.md`(推進到 phase-6)

**✅ Acceptance Criteria(允收標準)**

⚠ **核心要求:Integration test outputs 對齊 §6.4.11.F Integration Test Artifact Contract**(`/pm validate-integration` 全 pass + 對齊 §F.5 Exit Check List)

- ✅ 所有 module branch 已合到 integration branch(無 merge conflict)
- ✅ E2E R-XX 真機驗測 100% pass(對齊 §F.1 e2e_test_results + memory: real-device testing)
- ✅ Perf 全 SLA 達標(對齊 §F.2 perf_test_results + Requirement Spec SLA)
- ✅ 跨模組互動測試完成
- ✅ PM 健康檢查通過(整合層無 anomaly)
- ✅ V3 integration review pass
- ✅ Phase 5 Exit Check List(§6.4.11.F.5)走完
- ✅ **PM 跟老闆 walkthrough 簽核**(state.md `phase_5_signoff = true`)

---

##### 🚪 Phase 6 — 上線(Release)

**📥 Input Documents(入場必備)**

- Integration branch(deploy 來源)
- Deploy script(eg. Azure Webapp 部署腳本)
- Rollback plan 草版
- Monitoring 配置文件
- Smoke test case list

**📤 Output Documents(結案產出)**

- Deploy log(含時間 / 版本 / 操作人)
- Smoke test results(prod env 跑的結果)
- Rollback plan(已 test 通過的最終版)
- Monitoring dashboard URLs + alert 設置文件
- Stakeholder announce 通知紀錄
- `docs/pm/reports/<date>-phase-6-release.md`(上線階段總結)
- 更新 `state.md`(推進到 phase-7)

**✅ Acceptance Criteria(允收標準)**

⚠ **核心要求:Release outputs 對齊 §6.4.11.G Release Artifact Contract**(`/pm validate-release` 全 pass + 對齊 §G.5 Exit Check List)

- ✅ Production deployment 成功(Azure Webapp,對齊 §G.1 deploy_log + memory: azure_webapp_runtime = Linux 3.0)
- ✅ Smoke tests prod env 全 pass(對齊 §G.3 smoke_test_all_pass)
- ✅ Rollback plan **已 rehearse**(不可只 documented,對齊 §G.3 rollback_plan_rehearsed)
- ✅ Monitoring + alerts 已上線可運作(對齊 §G.3 monitoring_active)
- ✅ Stakeholder announce 完成(對齊 §G.3 stakeholder_announced)
- ✅ Phase 6 Exit Check List(§6.4.11.G.5)走完
- ✅ **PM 簽核**(state.md `phase_6_signoff = true`)

---

##### 🚪 Phase 7 — 觀察(Post-Launch Monitoring)

**📥 Input Documents(入場必備)**

- Production code(跑在 Azure Webapp)
- Monitoring dashboard URLs
- On-call 輪班表
- User feedback 收集 channel(eg. LINE 客服 / 客戶 hotline)
- KPI baseline(對齊 §7.5 KPI 表)
- Rollback plan(萬一需要回退)

**📤 Output Documents(結案產出 — 也是專案結案文件)**

- Bug fix commits(若有,標明 P0 / P1 priority)
- `docs/pm/user-feedback-log.md`(User feedback 收集 + categorize)
- `docs/pm/reports/<date>-kpi-evaluation.md`(KPI 評估報告)
- `docs/pm/reports/<date>-final-retrospective.md`(專案 retrospective),包含:
  - What went well
  - What didn't go well
  - Lessons learned
  - Recommendations for next project
- 更新 `state.md`(current_phase = closed)
- 完整的 decision-log + review logs(audit trail 完整保留)

**✅ Acceptance Criteria(允收標準)**

⚠ **核心要求:Post-Launch outputs 對齊 §6.4.11.H Post-Launch Monitoring Artifact Contract**(`/pm validate-post-launch` 全 pass + 對齊 §H.6 Exit Check List)

- ✅ N 天(default 7)production 穩定無 critical incident(對齊 §H.4 prod_stability_days)
- ✅ Critical bugs 全部解決(P0 / P1 ticket 全 close,對齊 §H.4 critical_bugs_closed)
- ✅ Perf 仍在 SLA 內(對齊 §H.4 perf_within_sla + Requirement Spec SLA)
- ✅ User feedback 已收集 + categorize(對齊 §H.2 feedback_entry schema)
- ✅ KPI evaluation verdict ≥ partial(對齊 §H.1 + §7.5 KPI 表;miss 不可 close)
- ✅ Retrospective 完成(對齊 §H.3 5 mandatory sections + team sign-off)
- ✅ Phase 7 Exit Check List(§6.4.11.H.6)走完
- ✅ **PM 跟老闆 final sign-off**(state.md `phase_7_signoff = true`,project 標記 closed)

---

#### 6.3.3 核心原則總結(從上述 8 階段浮現的設計哲學)

從這張完整大表,我們可以看到 4 個核心設計原則:

**原則 1:文件流連續不斷**

每階段「**Input Documents = 上階段的 Output Documents**」 — Phase 0 產出的 Requirement Spec 流到 Phase 1 + 2,Phase 1 產出的 _plan.md 流到 Phase 2 + 4,Phase 4 產出的 code 流到 Phase 5...... **沒有任何階段需要「重新造輪子」**。

**原則 2:每階段 Acceptance Criteria 機械可檢查**

不論「Spec 已寫定」「測試全綠」「lint baseline 未增」 — 全部都可用 file 存在 / parse / grep / exit code 機械化驗證。**唯一靠人主觀判斷的是「PM 簽核」這道閘**,但 PM 看的是上述機械化檢查的結果,有客觀依據。

**原則 3:Audit Trail 從 Phase 0 累積到 Phase 7**

所有 decision-log / review logs / daily reports / phase reports 都是 append-only,**12 週後客戶問「為什麼當初這樣設計?」直接翻檔案即可,無人為記憶依賴**。

**原則 4:PM 簽核貫穿全 8 階段**

每階段都有 PM 最後一道閘 — AI 助理可以跑機械化檢查 + 給推薦,**但 advance phase 永遠需要真人 PM 點頭**。「Claude is assistant, not authority」原則具體落實。

---

#### 6.3.4 各文檔完整說明(用途 / 紀錄什麼 / 誰維護 / PM Skill 何時參考)

> 本附錄對 §6.3.2 提到的所有檔案逐一說明,**讓讀者清楚知道每份文件的存在意義 + 跟 PM Skill 的關係**。
> 統一用四問四答結構:**📍 用途 → 📝 紀錄什麼 → 👤 誰來維護 → 🤖 PM Skill 何時參考**

---

##### A. 專案管理文件(PM-level,跨整個 project)

###### 📄 A.1 Requirement Spec

**📍 用途**

把老闆腦袋裡模糊的「想做什麼」結構化為可執行的專案輪廓 — 是整個專案的「北極星」,後續每階段都對齊它跑。

**📝 紀錄什麼**

- 專案目標 + 範圍(做什麼 / 不做什麼)
- 主要 user stories(誰會用 / 怎麼用)
- 業務規則(法律 / 計費 / 流程約束)
- 約束條件(預算 / 時程 / 法遵)
- SLA / 效能 baseline(上線後驗收標準)

**👤 誰來維護**

PM 主導撰寫,在 Phase 0 用 V0 SKILL 引導老闆訪談 + 摘要而成。後續 Phase 若需求微調,需 PO 拍板才改動。

**🤖 PM Skill 何時參考**

- Phase 1 跑 V7 切模組時:讀此檔識別 features → 建議模組切割
- Phase 2 工程師寫 module requirement.md 時:對齊此檔的 user stories
- Phase 5/6 跑驗收時:對齊 SLA / 效能 baseline check
- Phase 7 跑 KPI evaluation:確認原始目標是否達成

###### 📄 A.2 `docs/pm/state.md`

**📍 用途**

專案當前狀態的唯一 SSOT — PM Skill 每次 invoke 第一件事就是讀這個檔,知道「現在我們在哪個 Phase / 過了哪些閘 / 目標日期是何時」。

**📝 紀錄什麼**

- 專案名稱 + 當前 Phase(0~7)
- 各 Phase 何時開始 + 何時結束
- 目標上線日 / 預算 / 範圍約束
- 各階段簽核 flag(phase_0_signoff: true/false)
- 最近一次 gate check 結果

**👤 誰來維護**

PM 主導,V0 SKILL 初始化,**PM Skill 自動更新部分欄位**(eg. last_gate_check 結果)。每次 Phase advance 都必更新。

**🤖 PM Skill 何時參考**

- **每次 invoke 必讀第一個檔案**(讓 Claude 知道現在脈絡)
- `/pm progress` 寫 daily report 時:對比 target_release_date 算 delay
- `/pm gate-check` 跑階段審查時:驗證 signoff flags
- `/pm advance` 推進階段時:寫入新的 phase 進度

---

###### 📄 A.3 `docs/pm/team-roster.md`

**📍 用途**

團隊成員名單 + 各自專長 + 工作量配置 — PM Skill 寫 daily report 時要知道「誰在做什麼 / 誰落後了 / 哪位 owner 該被 ping」。

**📝 紀錄什麼**

- 每位工程師:姓名 / 角色(backend / frontend / full-stack)/ 專長
- 工作量配置:當前 module 派發 / 預估 capacity
- 聯絡方式 / 上下班時段(eg. on-call 輪班)

**👤 誰來維護**

PM 主導。Team 變動時(新人入 / 老人離 / 換 module owner)即時 update。

**🤖 PM Skill 何時參考**

- `/pm progress` daily report:標出哪位 owner 沉默幾天
- `/pm digest` weekly:算 velocity per owner
- 寫 recommended actions 時:知道該 ping 誰

---

###### 📄 A.4 `docs/pm/phase-gates.md`

**📍 用途**

7 階段允收標準的 SSOT — PM Skill 跑 `/pm gate-check` 就是按這個檔的規則一條一條驗證。

**📝 紀錄什麼**

每個 Phase 的:
- Entry criteria(入場條件)
- Exit criteria(離場條件)
- Machine-checkable rules(eg. 「functional.md 內所有 Status=done」)
- Manual verification items(eg. 「PM 主觀判斷規格合理」)

**👤 誰來維護**

PM + Tech Lead 在 Phase 0 設定初版。**鎖定為 stable contract,後續改動需 PO 拍板**(對齊 backend-change-rule 既有 governance)。

**🤖 PM Skill 何時參考**

- `/pm gate-check phase=N`:逐條跑 phase N 的 exit criteria 機械化驗證
- `/pm advance`:對比當前 phase 跟下個 phase 入場條件
- 寫 phase-gate report 時:列出每條 criterion pass/fail

---

###### 📄 A.5 `docs/pm/output-schemas.md`

**📍 用途**

所有 V0-V8 SKILL 必填的 file format 規範 SSOT — **讓 PM Skill 信任「functional.md 一定有 Status field」「test-results.md 一定有 status / commit_hash」這類 contract**,不需 ad-hoc 解析。

**📝 紀錄什麼**

每個 file type 的:
- Required fields(必填欄位)
- Enum values(eg. Status 只能是 `⏳ planned / 🟡 in-progress / 🚫 blocked / ✅ done / ⚠ at-risk`)
- 範例 entry

涵蓋:state.md / functional.md / test-results.md / decision-log.md / review logs 等。

**👤 誰來維護**

Tech Lead 主導撰寫,PO 拍板鎖定。Schema 變更需 PO 拍板(影響全 SKILL 體系)。

**🤖 PM Skill 何時參考**

- 跑 spec parser 時:對齊欄位名稱
- `/pm health-check` 驗證 spec 完整性時:依此檔規則驗證
- 偵測「functional.md 缺欄位」anomaly:用此檔判斷哪些是必填

---

###### 📄 A.6 `docs/decision-log.md`

**📍 用途**

跨階段累積的拍板紀錄(append-only),**防止已收斂議題下輪 review 被重提、新人 onboarding 翻歷史快**。

**📝 紀錄什麼**

每個 decision entry:
- decision_id(唯一識別)
- timestamp(時間)
- context(當時的背景)
- decision(拍板結果)
- rationale(為什麼這樣決定)
- impacted_features(影響哪些 features)
- decided_by(誰拍板的)

**👤 誰來維護**

PM 主導 + V1/V5/V8/spectra-review SKILL 在拍板時自動 append。**append-only,不覆寫舊紀錄**。

**🤖 PM Skill 何時參考**

- 跑 V8 跨輪 review 時:讀此檔避免重提已收斂議題
- 寫 weekly digest:整理本週新拍板
- 新人 onboarding / Phase 7 retrospective:翻歷史看脈絡
- 客戶問「為什麼當初這樣?」:翻此檔答覆

---

##### B. 模組文件(Module-level,每模組獨立)

###### 📄 B.1 `docs/modules/_plan.md`

**📍 用途**

全專案模組架構 SSOT — PM Skill 知道「整個 project 有幾個 module / 誰 own 哪個 / 模組之間誰依賴誰」就是看這個檔。

**📝 紀錄什麼**

- 模組列表 + 各 owner(誰負責)
- 跨模組依賴關係圖(誰 blocks 誰)
- Branch 命名規則
- Shared Files Coordination plan(共用檔誰能改)

**👤 誰來維護**

PM + Tech Lead 主導,V7 SKILL 產初版,PM 跟工程師談完後微調定版。

**🤖 PM Skill 何時參考**

- `/pm progress`:對應 owner 找出哪個 module 落後
- `/pm health-check`:跟 functional.md 對照,確認所有 module 都有寫 spec
- 建 dependency graph:讀此檔識別 critical path
- 寫 daily report:依此檔的 owner mapping 列出 owner 狀態

---

###### 📄 B.2 `docs/modules/<name>/requirement.md`

**📍 用途**

該模組業務需求 — 從整體 Requirement Spec 切下來「**這個模組要解決什麼業務問題**」的子集,讓 owner 對齊老闆原始意圖。

**📝 紀錄什麼**

- 該模組要解決什麼業務問題
- 主要 user stories(對應該模組部分)
- 業務規則(法律 / 計費 / 流程)
- 跟其他模組的介接需求

**👤 誰來維護**

Module owner(該模組負責工程師),在 Phase 2 撰寫。後續若 spec 變動需 PO 拍板。

**🤖 PM Skill 何時參考**

- `/pm health-check`:確認每模組都有 requirement.md(不能缺)
- V8 跨模組 review:對照各模組 requirement 找衝突
- Phase 5/6 驗收:對齊驗收項目

---

###### 📄 B.3 `docs/modules/<name>/functional.md` ⭐ 進度追蹤核心檔

**📍 用途**

該模組功能規格 + **每個 feature 的進度追蹤 SSOT** — 整套 PM Skill 設計最核心的檔案,沒有它 PM Skill 完全 work 不下去。

**📝 紀錄什麼**

每個 feature 必有:
- `Status:` ⏳ planned / 🟡 in-progress / 🚫 blocked / ✅ done / ⚠ at-risk
- `Planned:` / `Actual:` 日期
- **Plan section**(V1 SKILL 自動填):approach / 子任務 / 完成標準
- **Dependencies:** depends_on / blocked_by
- **Execution Log**(V2 SKILL 自動 append):每次任務進度紀錄(時間 + commit hash)
- **Related Commits / PRs**(V2 SKILL 自動連結)

**👤 誰來維護**

Module owner 主導,**但實際 update 動作幾乎全由 V1 + V2 SKILL 自動完成**(owner 跟 Claude 工作時自然產出)。Phase 2 寫 Plan section,Phase 4 持續 update Execution Log + Status。

**🤖 PM Skill 何時參考**

- **`/pm progress` 主要資料來源** — scan 全模組 functional.md 推進度
- `/pm health-check`:對照 commit + tests 找不一致
- `/pm gate-check`:驗證「全 feature Status=done」這條 criterion
- 寫 daily report 的 progress summary:統計各 status 數量
- 識別 critical path:看 dependencies + Status

---

###### 📄 B.4 `docs/modules/<name>/plan.md`

**📍 用途**

該模組實作計畫(技術層面)— 跟 functional.md 的差別:functional 寫「要做什麼 + 進度」,plan 寫「**技術上怎麼做**」。

**📝 紀錄什麼**

- 技術 approach(用什麼 library / framework)
- 用到的共用 helper
- 跨模組對接 API contract
- 風險與對策
- 排程細項

**👤 誰來維護**

Module owner,在 Phase 2 撰寫。Phase 3 共用基礎建好後可能微調(對齊真實 helper 介面)。

**🤖 PM Skill 何時參考**

- `/pm health-check`:確認每模組都有 plan.md
- V8 跨模組 review:對照各模組 plan 看共用 helper 需求
- Phase 3 共用基礎設計:Tech Lead 看此檔識別共用需求

---

###### 📄 B.5 `docs/modules/<name>/tests.md`

**📍 用途**

該模組測試 case 規格 — 記錄「這個模組該測哪些東西」,讓 QA + 工程師對齊。

**📝 紀錄什麼**

每個 test case:
- test_id(唯一識別)
- linked_feature_id(對應 functional.md 的 feature)
- setup(前置條件)
- action(執行什麼)
- expected(預期結果)

**👤 誰來維護**

Module owner + QA(若有獨立 QA 角色)。Phase 4 對齊 feature 開發進度持續加 test case。

**🤖 PM Skill 何時參考**

- `/pm health-check`:對照 functional.md 看「feature 有沒有對應 test case」
- 識別 anomaly:feature done 但沒對應 test → flag

---

###### 📄 B.6 `docs/modules/<name>/test-results.md`

**📍 用途**

該模組測試結果紀錄 — 真實證據顯示「測試是否真的跑過 + 跑出什麼結果」,**不靠 self-report**。

**📝 紀錄什麼**

每個 test case 的執行結果:
- test_id
- status: pass / fail / skip
- last_run_date(最近一次跑的時間)
- commit_hash(對應跑測試時的 code 版本)
- failure_note(若 fail,記原因)

**👤 誰來維護**

**V2 SKILL 自動更新** — 工程師用 V2 跑測試時,SKILL 自動 append 結果。Owner 不手動填。

**🤖 PM Skill 何時參考**

- `/pm progress`:統計 test pass rate
- `/pm health-check`:識別「test 寫了但沒對應 feature」/「commit 後 test 沒跑」等 anomaly
- `/pm gate-check`:驗證「測試全綠」這條 criterion
- 偵測風險:fail 連續幾天沒修 → flag

---

##### C. 審查文件(Review-level)

###### 📄 C.1 `docs/reviews/_TEMPLATE.md`

**📍 用途**

所有 review log 的範本 — **stable contract**,V3 / V8 / spectra-review 三個 SKILL 的輸出全部對齊它,讓 PM Skill 信任格式不變。

**📝 紀錄什麼**

5 section 結構:
- § 1. Context(本輪 review 的 scope)
- § 2. 4-Tier Findings(🔴 BLOCKERS / 🟡 CONCERNS / 🟢 NITS / ✅ STRENGTHS)
- § 3. Decision Log(本輪新拍板 + 從前輪 carry forward)
- § 4. Carry-over Open Issues(未拍板續看)
- § 5. Verdict + Next Round Focus

**👤 誰來維護**

PO 鎖定。Template 改動需 PO 拍板(因為改動 cascade 影響全 SKILL)。

**🤖 PM Skill 何時參考**

- 解析所有 review log 時:照此 template 結構 parse
- 寫 weekly digest:從各 review log 4-tier findings 抽取「未解 BLOCKERS 數」「累積 STRENGTHS 數」等指標

---

###### 📄 C.2 `docs/reviews/<date>-round-N-cross-module-review.md`

**📍 用途**

V8 跨模組 review log — **每週或 on-demand 跑出來的「跨模組規格衝突報告」**,讓 PO 看到本週需要拍板的議題。

**📝 紀錄什麼**

對齊 `_TEMPLATE.md` 5 section,聚焦跨模組層面:
- 模組 A 跟模組 B 的 spec 衝突
- 命名 / 數字 / 規則 不一致
- 依賴關係沒對齊
- 已拍板議題的 carry forward(下輪 review 跳過)

**👤 誰來維護**

V8 SKILL 自動產出。PO 看完後在 inline 拍板,SKILL 自動 update Decision Log + Carry-over 段。

**🤖 PM Skill 何時參考**

- `/pm progress`:統計「outstanding BLOCKERS 數」加入 daily report
- `/pm digest` weekly:整理本週 V8 review 拍板了什麼
- 識別「同議題連 N 輪未解」風險 → flag

---

###### 📄 C.3 `docs/reviews/<date>-V3-<topic>.md`

**📍 用途**

V3 spec quality 輕量審查 log — checklist-based 確認規格品質達標。

**📝 紀錄什麼**

對齊 `_TEMPLATE.md` 5 section,但 4-tier findings 較精簡(主要是 checklist pass/fail)。

**👤 誰來維護**

V3 SKILL 自動產出。Phase 3 跑「共用基礎品質 review」、Phase 5 跑「整合層 quality review」。

**🤖 PM Skill 何時參考**

- `/pm gate-check phase=3`:驗證「V3 共用設計 review pass」這條 criterion
- `/pm gate-check phase=5`:驗證「整合層 V3 review pass」

---

###### 📄 C.4 `docs/reviews/<date>-spectra-<target>.md`

**📍 用途**

spectra-review 深度審查 log — **PO 對某個關鍵 spec 想要「最嚴格 review」時 on-demand 觸發**(eg. proposal rev .15 跑過 9 輪 spectra-review 找 100+ BLOCKERS)。

**📝 紀錄什麼**

對齊 `_TEMPLATE.md` 5 section,4-tier findings **深度版**(每輪 8-15 個 BLOCKERS 規模),從 7 維度切(naming / counting / completeness / governance / AC / OQ / backward compat)。

**👤 誰來維護**

spectra-review SKILL 自動產出。Phase 2 規格撰寫期 + Phase 4 主開發期 by PO on-demand。

**🤖 PM Skill 何時參考**

- `/pm progress`:識別「某 spec 經 spectra-review 跑 N 輪仍多 BLOCKERS」風險
- 寫 weekly digest:加入「深度 review 累積發現 X 個關鍵 issue」

---

##### D. PM 報告文件(Report-level)

###### 📄 D.1 `docs/pm/reports/<date>-daily.md`

**📍 用途**

PM 每日進度報告 — **PM 每天早上 5 分鐘掌握全局的核心檔案**,所有 owner 狀態、blocker、recommended actions 都在這一份。

**📝 紀錄什麼**

- 整體進度 + 與 baseline 比較
- 今日 recommended actions(優先級排序,通常 top 3)
- Owner 更新狀態(誰沉默 / 誰在做 / 誰落後)
- Critical path risks
- 過去 24 小時 highlights(誰完成什麼)
- Schedule vs Actual

**👤 誰來維護**

**PM Skill 自動產出** — PM 每天 invoke `/pm progress`,SKILL 讀全部 file 後寫此檔。PM 看完即可採取行動。

**🤖 PM Skill 何時參考**

- 是 PM Skill 自己的「**輸出**」,但下次 invoke 時 PM Skill **會讀過去 N 天 daily report 做比較**(eg. 「Person A 連續 5 天沒更新 → 升級為 silence anomaly」)
- 寫 weekly digest:summarize 過去 7 天 daily 趨勢

---

###### 📄 D.2 `docs/pm/reports/<date>-weekly-digest.md`

**📍 用途**

每週狀態 digest — **對齊 weekly sync meeting**,讓 PM + 5 個 owner 在週一早上用同一份檔開會。

**📝 紀錄什麼**

- 本週 velocity(per owner / per module 完成多少 feature)
- Sprint planned vs delivered(計畫做完幾個 / 實際做完幾個)
- Trends(連 N 週落後 / 連 N 週超前)
- 下週 focus 建議

**👤 誰來維護**

**PM Skill 自動產出** — 每週一 PM invoke `/pm digest`。PM 不手寫週報。

**🤖 PM Skill 何時參考**

- 跨週比較 trends(累積過去 N 週 digest 看 velocity 變化)
- 算 KPI 「效率指標」 一部分數據(PM 時間節省)

---

###### 📄 D.3 `docs/pm/reports/<date>-phase-N-*.md`

**📍 用途**

Phase 結案總結報告 — **每個 Phase 結束時寫一份**,記錄該 Phase 的成就 + 學到的事 + 對後續 phase 的影響。

**📝 紀錄什麼**

- 該 phase 開始 / 結束日期
- 主要成就(eg. 「7 表 schema 全 ALTER 成功」)
- 遇到的問題 + 解決(eg. 「Module 1 跟 4 規格衝突,經 V8 review 後 PO 拍板統一」)
- 影響後續 phase 的事項

**👤 誰來維護**

PM 寫(可借 PM Skill 自動 draft),Phase 結束 PO 簽核時定版。

**🤖 PM Skill 何時參考**

- 寫 final-retrospective 時:整合所有 phase report
- Phase advance 時:確認上個 phase report 已寫

---

###### 📄 D.4 `docs/pm/reports/<date>-kpi-evaluation.md`

**📍 用途**

KPI 評估報告 — **專案結案前評估提案承諾的 KPI 是否達標**,是「驗收 vs 退路」的客觀依據。

**📝 紀錄什麼**

對照 §7.5 三層 KPI 逐項列:
- 效率指標(PM 時間節省 / Phase Gate 時間 等)— 達標 / 未達標
- 品質指標(規格 drift / 重大規則回滾 等)
- 戰略指標(規模化能力 / 工程師留任 等)
- 未達標項目的對策

**👤 誰來維護**

PM 寫,**借 PM Skill 提供原始數據**(eg. 過去 N 個月 daily report 累積算 PM 時間)。

**🤖 PM Skill 何時參考**

- Phase 7 結案前 PM 寫此檔時:**PM Skill 提供量化數據**(過去 N 天的 daily report、weekly digest、velocity 等)

---

###### 📄 D.5 `docs/pm/reports/<date>-final-retrospective.md`

**📍 用途**

最終 retrospective — 專案結案總結,**團隊集體寫,給下個專案當教材**。

**📝 紀錄什麼**

- What went well(做對了什麼)
- What didn't go well(做錯了什麼)
- Lessons learned(學到什麼)
- Recommendations for next project(下次怎麼做)

**👤 誰來維護**

PM + 全 team 共同 review 寫(可在 PM Skill 草版基礎上修)。Phase 7 結案時定版。

**🤖 PM Skill 何時參考**

- 自己 draft 草版時:讀整個 project 的 decision-log + phase reports + KPI 報告整合
- 下個專案 Phase 0 時:**讀此檔避免重蹈覆轍**(lessons learned 傳承)

---

###### 📄 D.6 `docs/pm/user-feedback-log.md`

**📍 用途**

上線後 User feedback 紀錄 + categorize — 是 Phase 7 唯一直接從外部來的 input,代表「使用者真實聲音」。

**📝 紀錄什麼**

每筆 feedback:
- 時間 / channel(LINE / 客服 / email)
- 類別(positive / negative / feature request)
- 內容摘要
- 後續 action(若有,eg. 「PO 拍板加入下版 backlog」)

**👤 誰來維護**

QA 主導收集 + categorize,PM 看。Phase 7 起持續累積。

**🤖 PM Skill 何時參考**

- 寫 KPI evaluation 時:從此檔抽「user feedback 已收集 + categorize」這條 criterion 的證據
- 寫 final retrospective 時:整合 user 視角的 lessons learned

---

##### E. 既有專案 SSOT(以訂閱專案為例;不同 project 對應替換)

> **說明:** 以下檔案是「**訂閱專案的具體 SSOT 範例**」,不同 project 有自己對應的 SSOT 檔案。PM Skill **基本不直接讀這些 code 檔**(它讀的是 spec + state),但會透過 git log 間接知道這些檔的 commit history。

###### 📄 E.1 `laundry_db_create_tables.sql`

**📍 用途**

DB schema 唯一 SSOT — 整個系統的 table definitions 都在這。

**📝 紀錄什麼**

- 所有 CREATE TABLE 語法
- 既有表 + 新增表
- Foreign key / index 定義

**👤 誰來維護**

Schema Council(Tech Lead 主導)。Phase 3 加新表,Phase 4 必要時微調。**改動需 Schema Council review + PO 拍板**(對齊 feedback-backend-schema-change-workflow 既有 governance)。

**🤖 PM Skill 何時參考**

- **不直接讀 SQL 內容**(那是 code,非 PM Skill 範疇)
- 透過 git log 間接識別「Phase 3 有沒有 commit 改 schema」→ 驗證 phase-3 exit criterion

---

###### 📄 E.2 `backend-integration-guide.md`

**📍 用途**

Backend cmd 合約登錄 — 5 個 module 之間透過 cmd 對接的「**API contract SSOT**」,Frontend dev 看此檔就知道 backend 給什麼 response。

**📝 紀錄什麼**

每個 cmd:
- Request shape(JSON schema)
- Response shape(success + error)
- 範例 payload
- 對應的 module / feature

**👤 誰來維護**

Tech Lead 主導框架,Module owner 各自加自己 module 的 cmd entry。

**🤖 PM Skill 何時參考**

- `/pm health-check`:驗證「Phase 3 exit criterion 共用 utility 全 ready」這條
- 識別「module 之間 cmd 對接漏掉」anomaly

---

###### 📄 E.3 `system_lib.py` helper

**📍 用途**

Backend 共用 utility 函式集中地 — 避免 5 個 module 各自造輪子。

**📝 紀錄什麼**

- 共用 const(eg. payment status enum)
- Helper functions(eg. `_get_effective_quota`)

**👤 誰來維護**

Tech Lead 主導。Phase 3 建立 + Phase 4 必要時擴充(對齊 sectioned file pattern,每 module 自己 section)。

**🤖 PM Skill 何時參考**

- **不直接讀 Python code**
- 透過 git log 識別 Phase 3 有 commit 共用 helper → 驗證 phase-3 exit

---

###### 📄 E.4 `v3/index.html`(含 `__moduleInitHooks` pattern)

**📍 用途**

Frontend boot 主入口 + module init hook 機制 — 讓 5 個 module 都能在 boot 階段註冊自己的 init code 不撞到別人。

**📝 紀錄什麼**

- Boot logic
- Module hook registry(`window.__moduleInitHooks` array)

**👤 誰來維護**

Frontend Lead 設好 pattern,各 Module owner 自己加自己的 hook 進去。

**🤖 PM Skill 何時參考**

- 不直接讀;間接識別「Phase 3 hook pattern 設好」(透過 git log)

---

###### 📄 E.5 `v3/theme.css`(CSS namespace prefix 約定)

**📍 用途**

Frontend 共用 style + CSS namespace 約定 — 5 個 module 各用自己 prefix 不撞 style。

**📝 紀錄什麼**

- 共用 CSS(button / modal / card)
- Namespace prefix 規範(`.module-1-*` / `.module-2-*` 等)

**👤 誰來維護**

Frontend Lead 主導,Module owner 自己 namespace 內可自由加 style。

**🤖 PM Skill 何時參考**

- 不直接讀;間接識別「Phase 3 CSS namespace 文檔化」

---

###### 📄 E.6 Mock backend cmd

**📍 用途**

讓 frontend 不被 backend 開發進度阻塞 — 在 backend cmd 還沒上線時,frontend 可以對接 mock 繼續開發。

**📝 紀錄什麼**

- 各 backend cmd 的 mock implementation(回固定 stub response)
- 對應的 spec(mock 跟未來 real cmd 一致的 shape)

**👤 誰來維護**

Tech Lead 寫 mock framework + Module owner 自己 module 的 mock。

**🤖 PM Skill 何時參考**

- 不直接讀 mock code
- 確認「Phase 3 mock cmd ready」這條 exit criterion(透過 git log + backend-integration-guide.md)

---

##### F. DevOps / 上線文件

###### 📄 F.1 Deploy log

**📍 用途**

Production deploy 完整紀錄 — 確保「**誰、何時、用哪個版本部署的**」可追溯。

**📝 紀錄什麼**

- 部署時間
- 版本(commit hash)
- 操作人
- 步驟 + 結果
- 任何中途意外

**👤 誰來維護**

DevOps 寫,每次 deploy 都累積一份。

**🤖 PM Skill 何時參考**

- `/pm gate-check phase=6`:驗證「production deploy 成功」這條 exit criterion
- 寫 Phase 6 release report 時:取此檔的版本紀錄

---

###### 📄 F.2 Smoke test results

**📍 用途**

上線後 prod env 立即跑的基本 sanity check 結果 — 確保「**上線後系統真的有 work**」。

**📝 紀錄什麼**

每個 smoke test:
- 測試名稱
- status(pass / fail)
- 時間
- Prod env 對應 service URL

**👤 誰來維護**

DevOps + QA。每次 deploy 後跑一輪。

**🤖 PM Skill 何時參考**

- `/pm gate-check phase=6`:驗證「smoke tests 全 pass」這條

---

###### 📄 F.3 Rollback plan

**📍 用途**

萬一 prod 出問題,**快速回退的 SOP** — 預防勝於治療,Phase 6 前必備。

**📝 紀錄什麼**

- Rollback trigger criteria(什麼狀況觸發)
- Rollback steps(具體操作步驟)
- 確認 rollback 成功的檢查項目
- 通知名單

**👤 誰來維護**

Tech Lead + DevOps 共同撰寫。每次重大 deploy 都要對齊更新。

**🤖 PM Skill 何時參考**

- `/pm gate-check phase=6`:驗證「rollback plan ready 且 test 過」這條
- Phase 7 觀察期若 critical incident:**PM Skill 可指向此檔的 trigger criteria** 給 PM 參考

---

###### 📄 F.4 Monitoring dashboard URLs + alert 設置

**📍 用途**

Production 監控入口 — 讓 PM / DevOps 隨時知道系統健康狀況。

**📝 紀錄什麼**

- 主要 dashboard URLs(Azure / Grafana / Application Insights 等)
- Alert rules 設置(什麼狀況觸發 alert)
- On-call 通知設定

**👤 誰來維護**

DevOps 設置 + 維護。

**🤖 PM Skill 何時參考**

- `/pm gate-check phase=6`:驗證「monitoring 已上線」這條
- 寫 Phase 7 daily report 時可附 dashboard URL

---

###### 📄 F.5 Stakeholder announce 通知紀錄

**📍 用途**

上線通知 stakeholder 的紀錄 — 證明「**該通知的人都通知到了**」。

**📝 紀錄什麼**

- 通知對象(老闆 / 客戶 / 內部團隊)
- 通知時間
- 通知內容
- 收件確認

**👤 誰來維護**

PM 寫。

**🤖 PM Skill 何時參考**

- `/pm gate-check phase=6`:驗證「stakeholder announce 完成」這條 criterion

---

##### G. 概念性入場「文件」(非實體 file 但仍是入場必備)

> 某些 Phase 的入場「文件」其實是 **概念性 prerequisite**,不是實體 markdown / code 檔。但仍需在前一個 phase 準備好。PM Skill 無法讀這些(因為不是 file),但 PM 可透過 `state.md` 內的 flag 確認 ready。

| Phase | 概念性 input | 怎麼產出 / 確認? | PM Skill 關聯 |
|:---:|:---|:---|:---|
| 0 | 老闆口頭需求 | PM 用 V0 SKILL 引導訪談 + 摘要為 Requirement Spec | 確認 Requirement Spec 已寫定 |
| 4 | 各 module branch | Tech Lead 在 Phase 3 結束時 git branch 建立 | git 指令偵測 branch 是否存在 |
| 5 | E2E 測試 case | QA 在 Phase 4 期間並行準備 | `/pm gate-check phase=5` 確認 |
| 6 | Deploy script | DevOps 在 Phase 5 期間並行準備 | 確認 deploy script 已 ready |
| 7 | On-call 輪班表 | PM + Tech Lead 在 Phase 6 期間 setup | 確認 on-call 表已存在 |

---

##### 檔案清單摘要(對 PM / Tech Lead 快速查閱)

```
docs/
├── <project-name>-requirement.md         (A.1)
├── decision-log.md                       (A.6)
├── pm/
│   ├── state.md                          (A.2)
│   ├── team-roster.md                    (A.3)
│   ├── phase-gates.md                    (A.4)
│   ├── output-schemas.md                 (A.5)
│   ├── user-feedback-log.md              (D.6)
│   └── reports/
│       ├── <date>-daily.md               (D.1)
│       ├── <date>-weekly-digest.md       (D.2)
│       ├── <date>-phase-N-*.md           (D.3)
│       ├── <date>-kpi-evaluation.md      (D.4)
│       └── <date>-final-retrospective.md (D.5)
├── modules/
│   ├── _plan.md                          (B.1)
│   └── <name>/
│       ├── requirement.md                (B.2)
│       ├── functional.md                 (B.3)
│       ├── plan.md                       (B.4)
│       ├── tests.md                      (B.5)
│       └── test-results.md               (B.6)
└── reviews/
    ├── _TEMPLATE.md                      (C.1)
    ├── <date>-round-N-cross-module-*.md  (C.2)
    ├── <date>-V3-*.md                    (C.3)
    └── <date>-spectra-*.md               (C.4)

既有專案 SSOT(訂閱專案範例):
├── laundry_db_create_tables.sql          (E.1)
├── backend-integration-guide.md          (E.2)
├── system_lib.py                         (E.3)
└── v3/
    ├── index.html                        (E.4)
    └── theme.css                         (E.5)

DevOps 文件:
├── Deploy log                            (F.1)
├── Smoke test results                    (F.2)
├── Rollback plan                         (F.3)
├── Monitoring dashboards                 (F.4)
└── Stakeholder announce 紀錄              (F.5)
```

---

##### 關鍵維護原則

**1. Append-only 文件(永不覆寫):**
- `decision-log.md` / `state.md` 內 phase_signoffs 等持續累積
- 所有 `reports/` 內的檔案
- 所有 `reviews/` 內的檔案
- `user-feedback-log.md`

**2. Living 文件(持續更新):**
- 各模組 `functional.md`(每次 V2 跑 task 都 update)
- `state.md`(每次 Phase advance 都 update)
- `team-roster.md`(team 變動時)
- 既有專案 SSOT(eg. schema.sql / system_lib.py)

**3. 鎖定 contract 文件(改動需 PO 拍板):**
- `phase-gates.md`(7 階段允收標準)
- `output-schemas.md`(所有 SKILL 必填欄位規範)
- `reviews/_TEMPLATE.md`(review log 範本)

**4. Phase 結束才產出 文件:**
- `Requirement Spec`(Phase 0 結束)
- `_plan.md`(Phase 1 結束)
- 各模組 R/F/P spec(Phase 2 結束)
- 共用基礎程式碼(Phase 3 結束)
- Phase 結案報告(對應 Phase 結束)

---

### 6.4 Skill Composition Contract(跨 SKILL 銜接契約)

> **本節定位:** 本節寫死 PM Skill 與 V0-V8 / spectra-review 等 sub-skill 的 **machine-readable contract**,讓任一 sub-skill 升級不影響 PM Skill 邏輯,反之亦然。
> **與 §A.5 `output-schemas.md` 的關係:** §A.5 為 file-level schema SSOT(欄位 enum 等),本節為 sub-skill **行為與 input/output 契約 + Default/Override 兩層架構**;兩者互補,本節較精細,觸及估值原則與 audit trail。
> **本節自身 version(對齊 spectra Round 1 N3 fix):** 本節 §6.4 整體治理於 `contract-pack-v1`(2026-06-17 lock)。Contract change governance 於 §6.4.13;sub-section(§6.4.3 / §6.4.10 / §6.4.11 各 contract)獨立 version(對齊 §6.4.11 §I Contract Version Independence)。

#### 6.4.1 為什麼需要這層架構

PM Skill 不是「自己做所有事」的單體巨獸,而是 **orchestrator** — 它組合 V0-V8(各階段 SKILL)+ spectra-review(設計審查)+ 其他 sub-skill。若各 SKILL 自行決定 output 格式,跨 SKILL 銜接會壞掉(eg. spectra-review 改 output format → PM Skill daily report 解析爆炸)。

**Skill Composition Contract 解決 4 個痛點:**

| 痛點 | 沒 contract | 有 contract |
|:---|:---|:---|
| 跨 SKILL 銜接 fragile | 任何 SKILL 升級都 risk break PM Skill | 各自獨立升級,contract 不變則 PM Skill 穩 |
| 「未表態」issue 看不見 | Decision Log 只記 accepted/rejected,silent 完全消失 | summary file 顯式記 `status='no_decision'` |
| 文件品質無量化 | 「這份文件 review 過幾次?fix rate 多少?」無法答 | summary file 直接呈現 Health Score |
| PM Skill 給 fix 建議能力弱 | 只能依 tier 概略排;同 tier 內無 ranking | 每 finding 含 severity + ROI + dependencies,可量化排序 |

#### 6.4.2 核心原則:Schema-driven Skill Composition

3 個 invariants:

- **I1 — SSOT 單向:** PM Skill spec(本節)為 contract SSOT,sub-skill SKILL.md 只 `reference` 不 `redefine`(避免雙向 drift)
- **I2 — Output 機器可讀:** sub-skill 輸出對齊 schema(frontmatter + 固定 sections + enum),PM Skill 直接 parse 不需 ad-hoc
- **I3 — 升級獨立:** contract version 與 SKILL version 解耦,sub-skill 可在同 contract 下迭代 features;contract breaking change 才升 contract version

#### 6.4.3 spectra-review Contract(實例 — 本節主軸)

##### A. Input(PM Skill 給 spectra-review)

```yaml
input:
  target_path: "docs/<file>.md"        # 必填,review 目標
  target_rev: "<hash | rev .N>"        # 必填,鎖定 review 版本
  mode: "enhanced" | "lite"            # default: enhanced
  prior_summary_path: ".../_summary-X.md"  # optional,提供累進視角
  prior_rounds_log_paths: [...]        # optional,前輪 round files
```

##### B. Output Files Required(3 個必出)

| File | 路徑 | 性質 | 何時寫 |
|:---|:---|:---|:---|
| **F1. Per-Round Review Log**(既有) | `docs/reviews/<date>-spectra-<target-slug>-round-<N>.md` | append-only / 每輪新 file | 每 round 結束 |
| **F2. Aggregate Summary**(新增 — 本契約重點) | `docs/reviews/_summary-<target-slug>.md` | living / append-only rows | 每 round 結束,update Cumulative tally + 新增 issue rows |
| **F3. Decision Log entries** | append 至 `docs/decision-log.md` | append-only | PO 拍板任一 finding 時 |

##### C. File 2(`_summary-<target-slug>.md`)完整 Schema

**Frontmatter:**

```yaml
---
target: docs/<file>.md
target_slug: <slug>
total_rounds: <N>
last_round_date: <YYYY-MM-DD>
last_verdict: ship-as-is | fix-blockers | revise-design
schema_version: enhanced-v1
contract_version: spectra-contract-v1
---
```

**Section 1: Cumulative Findings Tally(每 round 一 row)**

```markdown
## Cumulative Findings Tally

| Round | Date | BLOCKER | CONCERN | NIT | STRENGTH | Verdict |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| 1 | 2026-06-17 | 1 | 3 | 5 | 6 | fix-blockers |
| 2 | 2026-06-17 | 0 | 0 | 0 | 6 | ship-as-is |
| **Total** | | **1** | **3** | **5** | — | — |
```

**Section 2: Issue Status Matrix(每 finding 一 row — PM Skill 主要 metric 來源)**

```markdown
## Issue Status Matrix

| Round | ID | Tier | Title | severity_score | fix_roi | Status | PO 決策 |
|:---:|:---:|:---:|:---|:---:|:---:|:---:|:---|
| 1 | B1 | 🔴 | 沙龍 promo 數字不一 | 8.0 | 4.0 | ✅ fixed | accept |
| 1 | N3 | 🟢 | 競爭品 appendix | 1.5 | 0.5 | ⏸ no_decision | — |
| 2 | C2 | 🟡 | 用詞混用 | 4.0 | 2.0 | ⏳ pending | accept(未實作) |
```

**Status enum:** `✅ fixed` / `⏳ pending`(已 accept 未實作)/ `⏸ no_decision`(PO 未表態)/ `❌ rejected` / `🔁 deferred`

**Section 3: Quality Health Score(PM Skill 直讀)**

```markdown
## Quality Health Score

- total_findings: 15
- fixed: 12
- pending: 1
- no_decision: 2          ⭐ PM Skill gate-check 重點
- rejected: 0
- deferred: 0
- fix_rate: 80%           = fixed / total
- close_rate: 87%         = (fixed + rejected + deferred) / total
- avg_severity_open: 3.2  = open findings 平均 severity
- po_overrides: 2         ⭐ 透明度 metric
- convergence_signal: ✅  = 連續 2 輪 0 BLOCKER
```

**Section 4: Hotspot History(累積 — 對齊 §Critical Hotspots)**

```markdown
## Hotspot History

| Round | Hotspot | 等級 | 是否解 |
|:---:|:---|:---:|:---:|
| 1 | salon 數字 cascade | 🔥🔥 | ✅ |
```

##### D. 每 Finding 必填 7 大欄位(per-round file F1 + summary file F2 同步)

對齊本契約拍板原則:**全 7 欄位必填**,scale 對齊現有 spectra-review enhanced-v1 §Calibration Baseline。

```yaml
finding:
  # ─── 識別 ─────
  tier: 🔴 BLOCKER | 🟡 CONCERN | 🟢 NIT | ✅ STRENGTH
  id: B1 / C1 / N1 / S1                    # round 內流水
  name: "簡潔標題 1 行內"
  evidence:
    - "spec §3.1 line 240"
    - "Z54 helper §3.7 line 380"

  # ─── 欄位 1: Severity 三件套 ⭐ NEW(對齊 Tradeoff 1 拍板)─────
  severity:
    score:
      value: 5.5                           # 當前生效值(PM Skill 讀這個)
      default: 8.0                         # spectra-review 原 estimate(LOCKED)
      override:
        by: PO | SKILL | null
        at: 2026-06-17T14:32:00+08:00
        reason: "salon 場景已有 contingency,實際 impact 比 estimate 低"
    band: med                              # auto from value: <3=low / 3-6=med / >6=high
    semantic: how_bad                      # how_bad(B/C/N)| how_valuable(STRENGTH)

  # ─── 欄位 2: Fix Economics 三件套 ⭐ NEW ─────
  fix_economics:
    difficulty:
      value: 2.0
      default: 2.0
      override: null
    roi:
      value: 2.75                          # auto: severity.score.value / difficulty.value
      default: 4.0                         # auto from defaults
    resource_estimate:
      value: "4h"                          # enum: 1h / 2h / 4h / 1d / 2d / 1w
      default: "2h"
      override: { by: PO, at: ..., reason: "..." }

  # ─── 欄位 3: Cross-Impact(既有,locked,PO 不可 override)─────
  cross_impact:
    affected_modules: [Module-1, Module-3]
    cascade_depth: 1-5
    dependency_chain: "..."

  # ─── 欄位 4: Phase-aware(既有)─────
  phase_aware:
    current_phase: 0-7
    if_not_fixed_now_breaks_at: 0-7
    estimated_rework_cost: low | medium | high

  # ─── 欄位 5: Decision Tree(既有,options 內容 locked)─────
  decision_tree:
    options:
      - { id: A, action: "不修", cost: ..., notes: "..." }
      - { id: B, action: "現在修", cost: ..., notes: "..." }
      - { id: C, action: "延後修", cost: ..., notes: "..." }
    recommended_option: B
    counterfactual: "If do nothing, expected outcome: ..."

  # ─── 欄位 6: Dependencies 三件套 ⭐ NEW ─────
  dependencies:
    blocks: [B2, C3]                       # SKILL 估 — 修我 unblock 哪些
    blocked_by: [B1]                       # SKILL 估 — 我被誰擋
    manual_blocks: []                      # PO 加,SKILL 不動

  # ─── 欄位 7: Severity Decay ⭐ NEW(對齊 Phase-aware,但量化)─────
  severity_decay:
    phase_when_found: 1
    by_phase:
      2: { value: 8.0, default: 8.0, override: null }
      3: { value: 9.0, default: 9.0, override: null }
      5: { value: 10.0, default: 10.0, override: null }

  # ─── PO 拍板狀態 ─────
  po_decision:
    status: fixed | pending | no_decision | rejected | deferred
    decided_at: <timestamp>
    decided_by: PO
    reason: "..."
```

##### E. Invariants(spectra-review 必守)

- **INV-1:** 每 round 結束,append 1 row 到 F2 Cumulative tally;**不可改前輪 row**
- **INV-2:** F2 Issue Status Matrix 每個拍板過的 issue 必有 row;「未表態」issue 必顯式列 `status='no_decision'`,**不可省略**
- **INV-3:** 所有 finding 必填 7 大欄位 + `value` / `default` 子欄位(override 可為 null);schema_version 必為 `enhanced-v1`,contract_version 必為 `spectra-contract-v1`
- **INV-4:** 同一 round 重跑,僅更新該 round row,**不 append duplicate**(idempotency)
- **INV-5:** `value` 一律是 PM Skill 用的當前值;`default` 永遠 = spectra-review 原值(**LOCKED,跨 round 不可變**);`override` 為 audit trail
- **INV-6:** 任何 override 必含非空 `reason`(空字串 reject);override 操作後自動 recalculate `roi.value`

#### 6.4.4 Default vs Override 兩層架構(本契約靈魂)

PO 拍板原則:**spectra-review 給 default 估值,PM Skill 給 override 拍板**。

```
┌──────────────────────────────────────────────┐
│ Layer 1: spectra-review estimate(default)     │
│ - 對所有 7 欄位填 best-effort default          │
│ - 估錯不糾結;PO 可 override                    │
│ - default 一旦寫入 LOCKED,跨 round 不變       │
└──────────────────────────────────────────────┘
                       ↓
┌──────────────────────────────────────────────┐
│ Layer 2: /pm-bug-review override(value)       │
│ - PO 在 bug review feature 內 adjust value     │
│ - 寫入 override 三件套(by/at/reason)           │
│ - value 即時生效,PM Skill 讀 value 排序        │
└──────────────────────────────────────────────┘
                       ↓
┌──────────────────────────────────────────────┐
│ PM Skill consumers: 讀 value 做決策            │
│ - Fix recommendation 用 value 排序             │
│ - Gate-check 用 value 計算 Health Score        │
│ - Daily report 用 value 顯示 high/med/low      │
└──────────────────────────────────────────────┘
```

**這個架構解 3 個問題:**

1. **spectra-review estimate 痛點:** 估錯沒把握時填 best-effort default 即可 → SKILL 寫 review 速度回得來(預期 +1 分 / finding 而非 +3 分)
2. **Human-in-the-loop trust hierarchy:** PO override > SKILL estimate;PM Skill honor PO,符合「Claude is assistant not authority」原則
3. **跨 project calibration loop:** 多次 PO override 後可分析「SKILL baseline 偏緊 / 偏鬆」→ Phase C 用 override history 重校 baseline

#### 6.4.5 PM Skill `/pm-bug-review` Feature Spec

**Interface:**

```bash
/pm-bug-review <target-slug>                 # 全 finding 走一遍
/pm-bug-review <target-slug> --finding B1    # 單 finding
/pm-bug-review <target-slug> --pending-only  # 只 review status=no_decision/pending
/pm-bug-review <target-slug> --overrides-only # review 既有 overrides 是否仍合理
```

**Workflow(7 步):**

```
1. PM Skill 讀 docs/reviews/_summary-<target-slug>.md(F2 summary file)
2. 依 --filter 篩 finding,對每個顯示:

   ┌─ B1: 沙龍 promo 數字不一 ──────────────────
   │ Tier:                🔴 BLOCKER
   │ Cross-impact:        Module-1, Module-3(cascade=3)
   │ ──── 可 override 欄位 ────
   │ severity.score:      8.0 (spectra default)  → ?
   │ fix.difficulty:      2.0 (spectra default)  → ?
   │ fix.roi:             4.0 (auto)             → recalc
   │ fix.resource:        "2h" (spectra default) → ?
   │ deps.manual_blocks:  []                     → ?
   │ severity_decay.p3:   9.0 (spectra default)  → ?
   │ ──── 拍板 status ────
   │ status:              no_decision            → ?
   │ ────────────────────────────────────────
   │ [a] Accept all spectra defaults(no override)
   │ [b] Override severity → 輸入 value + reason
   │ [c] Override difficulty → ...
   │ [d] Override resource → ...
   │ [e] Add manual_block → ...
   │ [f] Override decay curve → ...
   │ [g] Mark "需要 spectra 重估" → re-trigger SKILL on this finding
   │ [h] 拍板 status → fixed / pending / rejected / deferred
   │ [i] Skip(留 no_decision)
   └────────────────────────────────────────────

3. PO 輸入決定;若 override,reason 必填(空 reject)
4. PM Skill 寫回 F2 summary file:
   - 更新 finding 的 value 段
   - append override 子段(by/at/reason)
   - 自動 recalc roi.value
   - 更新 Quality Health Score(po_overrides++)
5. PM Skill append D-pm-bug-review-<id> 到 docs/decision-log.md:
   "D-pm-bug-review-<round>.<id>: B1 severity 8.0 → 5.5 | reason: ... | source: ..."
6. 若 finding 拍 status=fixed → 觸發 PM Skill 額外 gate-check(該文件 fix 是否真的 land)
7. PM Skill 顯示新 fix recommendation order(因 override 後 ranking 變了)
```

**Output File Updates:**
- F2 summary file: 多個 finding rows 更新 + Health Score 重算
- decision-log.md: append override entries(audit)
- 不寫 F1(per-round file 是 SKILL 寫的,PM Skill 不動)

#### 6.4.6 Governance Matrix(可改 / 不可改)

| 欄位 | spectra-review 寫? | PM /pm-bug-review 可 override? | 理由 |
|:---|:---:|:---:|:---|
| tier(B/C/N/S) | ✅ | ❌ | SKILL 分類權;PO 想改要重跑 review |
| id / name | ✅ | ❌ | 影響追蹤 |
| evidence(file:line) | ✅ | ❌ | 客觀事實 |
| **severity.score** | ✅ default | ✅ value | 主觀 estimate |
| **severity.band** | ✅ auto | ❌(隨 score 自動算) | derived field |
| **fix_economics.difficulty** | ✅ default | ✅ value | 主觀 estimate |
| **fix_economics.roi** | ✅ auto | ❌(隨 score/difficulty 自動算) | derived field |
| **fix_economics.resource_estimate** | ✅ default | ✅ value | PO 對團隊更了解 |
| cross_impact 分析 | ✅ | ❌ | SKILL 分析權 |
| phase_aware 預測 | ✅ | ❌ | SKILL 分析權 |
| decision_tree options 內容 | ✅ | ❌ | SKILL 提供;PO 拍 status 不改 options |
| **dependencies.blocks/blocked_by** | ✅ | ❌ | SKILL 估 |
| **dependencies.manual_blocks** | — | ✅(新增/刪除) | PO 經驗加 |
| **severity_decay.by_phase** | ✅ default | ✅ value | 主觀預測 |
| **po_decision.status** | — | ✅(本來就是 PO 拍) | 拍板權 |

**原則:** 客觀事實 / 分類 / 分析 = LOCKED;主觀 estimate / 拍板 status = overridable。

#### 6.4.7 Audit & Calibration(防 drift)

**每個 override 必含 audit trail:**

```yaml
override:
  by: PO | SKILL                     # who(SKILL 也可能自動 re-estimate)
  at: <ISO8601 timestamp>            # when
  reason: "non-empty string"         # why(必填,空 reject)
  previous_value: <原 value>          # trace 回原始
```

**跨 round drift detection(spectra-review 下輪 review 時必跑):**

```
若 prior round 有 override(eg. B1 severity 8.0→5.5)
且 本 round SKILL 重估仍 8.0
→ 在 round file 顯式提示:
  "⚠ B1 上輪 PO override 8.0→5.5;本輪 SKILL 重估 8.0,是否再次 override?"
```

**PM Skill daily report drift warning(累積信號):**

```
若該文件 override_rate > 50%(over half of findings 被 override)
→ daily report 列 warning:
  "spectra-review baseline 可能偏離,建議下次 Phase Gate 重 calibrate"
```

**Phase C calibration loop(對齊現有 §Calibration Baseline 待鎖定段):**

- 用既有 override history 統計各 tier 平均 PO 調整方向
- 若 BLOCKER severity 平均被 PO ↓ 30% → SKILL baseline 偏緊,calibrate
- 若 NIT severity 平均被 PO ↑ 50% → SKILL 漏看 NIT 影響,calibrate
- Calibration 結果寫進 spectra-review enhanced-v2 baseline table

#### 6.4.8 PM Skill Fix Recommendation Algorithm

PM Skill 給 fix 建議的核心 algorithm 必須寫進本契約(否則只有 data 沒 logic):

```
Input:
  - F2 summary file(_summary-<target-slug>.md)
  - 當前 phase(從 docs/pm/state.md 讀)

Filter:
  - status IN [no_decision, pending]
  - severity_decay[current_phase] exists

Sort by(三層 tie-breaker):
  Primary:    severity_decay[current_phase].value DESC
  Secondary:  fix_economics.roi.value DESC
  Tertiary:   dependencies.blocks.length DESC

Output(Top-N 建議,N default=5):

🔴 建議優先修 B1
   - severity now: 8.5(decay curve: 8.0→8.5→10.0 at Phase 5)
   - fix_roi: 4.2(severity=8.5 / difficulty=2.0)
   - blocks: [C3, C5](修我可 unblock 2 個)
   - resource: "2h"
   - reasoning: 高 severity + 高 ROI + 可 unblock 後續

🟡 建議 B1 修完後修 C3
   - blocked_by: [B1]
   - severity: 5.0 / fix_roi: 2.5

🟢 建議 defer N1
   - severity: 1.5 / fix_roi: 0.4
   - reasoning: 低 ROI,不值得佔 sprint 空間
```

**Algorithm 在 Daily Report 的用法:**

每日早晨 PM Skill 對所有 active spec 跑此 algorithm,morning briefing 列 Top-3 建議。

**Algorithm 在 Phase Gate 的用法:**

Phase Gate 前 PM Skill 自動跑 health-check,若任一 spec 有 `severity_decay[current_phase].value > 7` 且 `status IN [no_decision, pending]` → block gate。

#### 6.4.9 Implementation Trigger Path(誰先動,誰後動)

對齊 OQ.10 拍板原則,落地順序:

```
Step 1: PM Skill requirement spec 落地(= 本 6.4 段)
        → contract_version 鎖 spectra-contract-v1

Step 2: PM Skill 寫 contract test fixture
        → 提供 mock _summary-X.md 供 spectra-review 對齊測試

Step 3: spectra-review SKILL 升級至 enhanced-v2
        → 加 §「Summary File Persistence」段
        → 加 7 大欄位生成邏輯(含 default 估值)
        → 加 drift detection 邏輯
        → SKILL 內部宣告對齊 spectra-contract-v1

Step 4: spectra-review retro-generate 對既有 review
        → 掃 docs/reviews/<date>-spectra-*.md 補建 _summary-X.md
        → 既有 reviews 無 7 欄位 default 用 SKILL re-estimate 填

Step 5: PM Skill 接 reader interface 上線
        → /pm-bug-review feature
        → Fix Recommendation algorithm 整合到 daily report
        → Gate-check 接 Health Score

Step 6: Phase C calibration 試跑(對齊 §10.4 Phase C)
        → 用既有 9 輪 review 重 calibrate baseline
```

#### 6.4.10 Requirement Spec Artifact Contract(文件品質契約 — Phase 0 Exit Bar)

> **What:** Phase 0 出品的 Requirement Spec 必須對齊本契約,才能 exit Phase 0 進入 Phase 1。
> **Why:** Requirement Spec 不只是「人讀的文件」,而是 V1 (planning) / V2 (implementation) / V7 (module splitter) / spectra-review / PM Skill 的 **input contract**。Quality 不夠 → 下游全爛(模糊 REQ → functional spec 解讀錯 → 模組切錯 → Phase 2-7 全 rework)。
> **與 §6.4.3 spectra-review Contract 的關係:** §6.4.3 定義 spectra-review 寫 review log 的格式;本節定義 review **目標文件**(Requirement Spec)本身的品質要求。兩者互為 sandwich:Requirement Spec(初版)→ spectra-review(N 輪)→ Requirement Spec(達 Exit Bar)。

##### A. 為什麼 Requirement Spec 必須 machine-readable

Requirement Spec 在 SDLC 是 4 個 SKILL 的 input:

```
Requirement Spec(Phase 0 產出)
   ├──→ V1 planning SKILL:     拆 task / 排 timeline
   ├──→ V2 implementation SKILL: 寫 functional spec / code
   ├──→ V7 module splitter SKILL: 切模組 + 依賴
   └──→ spectra-review SKILL:   review 品質
```

若 Requirement Spec 是「散文 + 模糊術語」,4 個 SKILL 都得猜:
- V1 猜 priority 排錯 timeline
- V2 猜 acceptance 寫錯 test
- V7 猜 module boundary 切錯模組
- spectra-review 沒得對齊規矩無法判正誤

**→ Requirement Spec 必須 machine-readable**(structured + atomic + traceable),才能驅動高品質下游產出。

##### B. Phase 0 Exit Criteria(完整檢核 — 取代既有 §6.3.2 Phase 0 簡略版)

> ⚠ **rev 1.13 SDLC v2 OVERRIDE(2026-06-20 PO lock):** 本段為 v1 contract。新 project + 在 Phase 0/1 進行中的 project 已改走 §6.4.16 SDLC v2(bootstrap PM only,不 enforce MVT 3-role)。本段保留 historical reference + grandfather projects(past Phase 2 signoff)。 Detailed v2 contract:**§6.4.16**。

**B.1 Review Process Criteria**(對齊 PO 提案 + convergence rule):

```yaml
review_process:
  rounds_min: 3                          # 至少 3 輪(可依 §C scaling)
  convergence_rule: "last 2 rounds 都 0 new BLOCKER + 0 new CONCERN"
                                         # rounds_min 與 convergence_rule 擇優滿足
                                         # eg. 跑 5 輪達 convergence → 過;跑 2 輪 0 BLOCKER 但未達 min → 不過
```

**B.2 Open Issues Cap**(對齊 §6.4.3 summary file Health Score):

```yaml
open_issues_cap:
  blockers:
    open: 0                              # status IN [pending, no_decision, deferred]
    # 註:BLOCKER 不可 deferred,必須 fix 或 reject(reject 需 PO 明示理由)
  concerns:
    open: 0                              # status IN [pending, no_decision]
    deferred_max: 2                      # CONCERN 可 defer 但 ≤ 2 個
  nits:
    open_max: 5                          # 對齊 PO 直覺
    no_lower_bound: true                 # 0 NITs 也可
  strengths:
    lower_bound: 3                       # standard (20-50 REQs);依 §C scaling 隨 spec 大小調整(small=2 / standard=3 / large=5)
    no_upper_bound: true                 # 越多越好(對齊 §I 說明)
```

**B.3 Machine-Readability Quality**(8 條 Claude-readable bar):

```yaml
machine_readability:
  # Q1: REQ atomic + ID
  all_reqs_have_unique_id: true          # eg. REQ-001 / REQ-002 唯一
  all_reqs_atomic: true                  # 每 REQ 只描述一件事

  # Q2: 0 TBD/TODO/XXX
  forbidden_pattern_count:               # 全 0(否則 fail)
    TBD: 0
    TODO: 0
    XXX: 0
    "???": 0
    "待定": 0
    "暫定": 0
    "之後再說": 0

  # Q3: Glossary section
  glossary_present: true
  glossary_min_terms: 5                  # 至少 5 個術語定義

  # Q4: Out of Scope section
  out_of_scope_present: true
  out_of_scope_min_items: 3              # 至少 3 條明確排除

  # Q5: Assumptions section
  assumptions_present: true
  assumptions_min_items: 2

  # Q6: Constraints section
  constraints_present: true
  constraints_min_items: 2

  # Q7: Acceptance machine-checkable
  all_acceptance_testable: true          # 不可有「用戶體驗良好」之類

  # Q8: Traceability hooks
  frontmatter_required_fields_present: true
```

**B.4 Per-Requirement Schema**(每個 REQ 必填 11 欄位 — 含 REQ ⇄ Golden Scenario ⇄ Anti-example 三元組):

> 三元組不變式 SSOT:`docs/pm/spec-authoring/requirement-spec-authoring-rules.md §3`。
> `golden_scenario` 嚴格 1:1(一個情境 = 一個 REQ,是 sizing 單位);`anti_examples` 為 1:N。
> 缺 golden/anti 需二次確認 + `[GAP]` 標記(rulebook §5.3),不得 silent。
> **Schema Migration(2026-07-02 P3b + spectra Round 1 B1 fix — grandfather discriminator):** triad 完整性依 `schema_version` 分流,避免同名雙義:
> - `schema_version: req-spec-v1.1`(新建,11 欄位含三元組)→ triad **required**,缺項若無 `[GAP]` marker 則 **fail**
> - **其他一切 schema_version**(legacy `req-spec-v1` 9 欄位、既有專案的 `enhanced-v1` / `enhanced-v1-inherit` 等)→ **grandfather**:triad 缺項為 **warning**(視同 `[GAP]`),**不** hard fail
>
> 判準單一化:**唯 `req-spec-v1.1` 觸發 triad hard-check;其餘全 grandfather**(涵蓋既有 4 份 `enhanced-v1` req spec,無漏)。新建 requirement spec(`/pm start` / `new-requirement`)一律 emit `req-spec-v1.1`。既有 spec 的 triad backfill + 升 v1.1 為 OD-4(漸進 / pilot,不強制)。

```yaml
required_per_req_fields:
  - id                # eg. REQ-001
  - title             # 1 行 < 50 字
  - description       # 完整描述
  - priority          # P0 | P1 | P2 enum
  - rationale         # 為何需要(memory link 或 evidence)
  - acceptance        # array, ≥ 1 item, machine-checkable
  - golden_scenario   # ⭐ 三元組:恰 1 個情境敘述(Given/When/Then);sizing 單位,塞不下 → 拆 REQ
  - anti_examples     # ⭐ 三元組:array, ≥ 1 item,邊界「什麼不算滿足」(1:N)
  - dependencies:
      blocked_by: []  # REQ IDs(可空 array)
      blocks: []
  - proposed_module   # eg. identity-management(V7 用)
  - source_evidence   # 來源:PO 拍板 / memory / 上游 spec

optional_per_req_fields:
  - notes
  - alternatives_considered
  - risks
  - risk_class        # ⭐ safety | data | compliance | normal(未標=normal);high-stakes floor + T3 carve-out 機械判定依據(rulebook §2.5.1 / §5.5.2 C3 fix)
  - signoff           # ⭐ append-only 3-role sign-off 註記歷史(rulebook §5.5.3;不覆蓋、reject 不刪 revivable)
```

**B.4a REQ Authoring Pipeline**(對齊 `requirement-spec-authoring-rules.md §2.5 / §5 / §5.5`;P3b + P3c):

REQ-authoring subcommands(`start` / `new-requirement`)在產 REQ 時跑 **3-phase pipeline**:

- **【前】Admission Gate(§2.5,P3c):** 候選須過 5-test(可追溯/有證據/值得寫/是what非how/有必要)才續;沒過 → Open Questions(T1/T2)/ Out of Scope(T3/T5)/ 反推 what(T4);T3 carve-out=安全·資料·法遵;T3 定 priority;PO override 記 log
- **【後】Write-time 3-Role Sign-off(§5.5,P3c):** 寫入前 async per-REQ PM/QA/Dev sign-off,有人決定就走;verdict append REQ 註記(reject 不刪+revivable);high-stakes floor;solo collapse;匯總進 phase-0 signoff

中段 Triad Authoring(`requirement add-mid-phase` / `requirement modify` = 全行為;`requirement split` = **僅 Triad Auto-Completion**)在產 / 改 REQ 時強制執行:

- **Triad Auto-Completion** — 人給錨點(REQ 或 golden_scenario 或 anti_examples),skill 自動草擬缺的另二元素,**batch 一次確認**;缺項需二次確認 + `[GAP]`(rulebook §5.3)
- **Coverage Expansion(舉一反三)** — skill 依全面視野列 **~3 個(總數,非每類 3)** 相鄰/隱含候選(sibling REQ / 額外 scenario / 額外 anti),**逐一**討論 add/mod/del;**所有 mode 強制、不得略過**;proposal-only + grounded 防 gold-plating

Runtime 對照:`skills/pm-skill/SKILL.md` §Shared: Triad Authoring Behavior。

**B.5 Structural Sanity**:

```yaml
structural:
  no_circular_dependencies: true          # REQ-A blocks REQ-B blocks REQ-A → fail
  all_dependencies_resolvable: true       # blocks/blocked_by 引用的 REQ 必存在
  proposed_modules_covered: true          # 每個 proposed_module 都有 ≥ 1 REQ
  acceptance_unique_per_req: true         # acceptance 不可在多個 REQ 間 copy-paste(代表 REQ 不夠 atomic)
```

##### C. Spec-Size based Scaling(避免小 spec 過嚴 / 大 spec 過鬆)

| REQ 數 | min rounds | open NIT cap | STRENGTH min | 備註 |
|:---:|:---:|:---:|:---:|:---|
| < 20 | **2** | 3 | 2 | small spec fast-track |
| 20-50 | **3** | 5 | 3 | standard(對齊 PO 提案)|
| 50-100 | **4** | 8 | 5 | large |
| 100+ | — | — | — | **必拆 spec**;single 100+ REQ spec PM Skill 拒收 |

##### D. Requirement Spec 完整 Schema(範例)

```yaml
---
spec_type: requirement
spec_version: 1.0
project_name: namecard-v3-subscription
schema_version: req-spec-v1.1   # v1.1 = 11 欄位含三元組(triad required);legacy req-spec-v1 = 9 欄位 grandfather
contract_version: req-contract-v1

# Q8 Traceability hooks
related:
  upstream:
    - "docs/2026-06-11-service-package-schema-proposal.md"
    - "docs/2026-06-16-subscription-business-proposal.md"
  downstream:
    module_plan: "docs/modules/_plan.md"                          # V7 寫
    per_module_functional: "docs/modules/<name>/functional.md"    # V2 寫
    per_module_plan: "docs/modules/<name>/plan.md"                # V1 寫
    per_module_tests: "docs/modules/<name>/tests.md"              # V2 寫

# 對齊 §6.4.3 summary file
review_summary_path: "docs/reviews/_summary-<this-spec-slug>.md"
---

# <Project Name> — Requirement Spec

## Glossary(Q3,≥ 5 terms)

| 術語 | 定義 |
|:---|:---|
| bizcard | 名片;V3 schema 中的 main_bizcard table |
| profile | 身份;承載多張 bizcard 的 LINE user 身份 |
| RBT | Received_Bizcard_TBL — 收到的好友名片 |
| ... | ... |

## Out of Scope(Q4,≥ 3 items)

- 多帳號切換(defer Phase 2.0,memory: project_v3_ui_proposal.md)
- 名片 NFC 傳輸(技術不成熟)
- ...

## Assumptions(Q5,≥ 2 items)

- A1: backend 已支援 Service_Package_TBL(schema rev .24)
- A2: Azure Webapp 為 Microsoft Azure Linux 3.0(memory: azure_webapp_runtime.md)
- ...

## Constraints(Q6,≥ 2 items)

- C1: 落地時程 ≤ 12 週
- C2: 不可動 V1 LIFF code(memory: v1_ui_retired.md)
- C3: 任何 *.py 改動須 PO 授權(memory: backend_change_rule.md)
- ...

## Requirements

### REQ-001: 多身份建立

```yaml
id: REQ-001
title: 多身份建立
description: |
  用戶可建立 1-N 個身份名片,每個身份對應一張預設 main_bizcard。
priority: P0
rationale: |
  對齊 V3 LIFF profile-bizcard invariant(memory: profile_bizcard_invariant.md)
acceptance:
  - 建立首張 profile 同時必 create 至少 1 張 main_bizcard
  - 同一 LINE user 上限 N profile(N 由 service_package.profiles 定)
  - 預設 main_bizcard 名稱 = profile 身份名稱
golden_scenario: |
  Given 新用戶首次進 LIFF 尚無任何 profile
  When 建立身份「王小明業務」
  Then 系統同時 create 1 張 main_bizcard,名稱 = 「王小明業務」,設為預設
anti_examples:
  - ❌ Profile 可獨立存在,main_bizcard optional
  - ❌ 首張 bizcard 用 profile.email 當 name
  - ❌ 只在 UI 顯示預設 bizcard,DB 沒真的 insert
dependencies:
  blocked_by: []
  blocks: [REQ-005, REQ-012]
proposed_module: identity-management
source_evidence: "PO 2026-06-01 拍板;memory: profile_bizcard_invariant.md"
```

### REQ-002: ...
```

##### E. Mandatory Sections in Requirement Spec

對齊 §D,Requirement Spec 結構強制 6 段:

1. **Frontmatter**(含 6 個 traceability fields)
2. **Glossary section**(≥ 5 terms)
3. **Out of Scope section**(≥ 3 items)
4. **Assumptions section**(≥ 2 items)
5. **Constraints section**(≥ 2 items)
6. **Requirements section**(N atomic REQ entries,每 REQ 11 必填欄位含三元組)

可選:Risks / Open Questions(若 Phase 0 結束仍有 Q,記錄但必須在 OQ section)。

##### F. Forbidden Patterns(0 tolerance — grep 必 0)

> ⚠ **Scope(對齊 spectra Round 1 C4 fix):** 本段強制 0 tolerance **僅 apply to Phase 0 Exit 最終版 spec**;**working draft 階段(rev .1 ~ rev .N-1)允許 TBD 標記未決事項**,屬正常 collaborative writing 流程。validator 提供 `--working-draft-mode` flag tolerate TBD,Phase 0 Exit 前移除此 flag 重跑 strict check。

```bash
# PM Skill validator(Phase 0 Exit 模式)跑這些 grep,任一 > 0 即 fail
grep -ci "\bTBD\b\|\bTODO\b\|\bXXX\b\|???\|undecided" requirement.md
grep -ci "待定\|暫定\|之後再說\|TBC" requirement.md
grep -ci "用戶體驗良好\|介面美觀\|效能優異\|good UX" requirement.md  # non-testable

# Working draft 模式(rev .1 ~ rev .N-1)用以下命令,tolerate TBD/TODO 但仍 check non-testable
/pm validate-req-spec <path> --working-draft-mode
```

**Working draft 流程:** PO 寫 rev .1 → tolerate TBD → spectra-review 跑找 issue → PO 解 TBD 寫 rev .2 → ... → 達 Phase 0 Exit 前 rev .N 必 0 TBD strict check pass。

##### G. PM Skill `/pm validate-req-spec` Validator

**Interface:**

```bash
/pm validate-req-spec <path-to-requirement-spec>
/pm validate-req-spec <path> --strict       # 嚴格模式(所有 warning 升 fail)
/pm validate-req-spec <path> --fix-trivial  # 自動修小毛病(eg. 加缺欄位 placeholder)
```

**Workflow:**

```
1. Parse frontmatter → 驗證 required fields(spec_type / schema_version / related / review_summary_path 等)
2. Parse REQ entries → 對每個驗證 11 必填欄位(含 golden_scenario + anti_examples)
3. ⭐ Triad completeness(對齊 requirement-spec-authoring-rules.md §3 INV-1/2)—— **依 frontmatter `schema_version` 分流(B1 grandfather discriminator):**
     - **`req-spec-v1.1`(新,唯一 hard-check):** triad required。每 REQ 恰 1 golden_scenario(0 或 >1 → fail;>1 → 建議 §7 SPL 拆分)+ ≥ 1 anti_examples(1:N)+ 無 orphan;缺項若 REQ 帶 `[GAP]` marker → warning,否則 **fail**
     - **其他一切 schema_version(`req-spec-v1` / `enhanced-v1` / `enhanced-v1-inherit` … grandfather):** triad 缺項一律 **warning**(不 fail),提示可 backfill 升 v1.1
     - 註:`[GAP]` marker 存在與否為 validator 唯一機檢依據(可 grep);「二次確認」為 authoring-time 對話 gate(rulebook §5.3),validator 不 re-verify
4. Scan forbidden patterns → grep 0 tolerance
5. Build dependency graph → 偵測 circular / unresolvable
6. Read _summary-<slug>.md → 對齊 §B.1 review_process + §B.2 open_issues_cap
7. 對 acceptance 逐條判 machine-checkable(LLM 判,輸出 fail 列具體 REQ)
8. 輸出 verdict + actionable fix list
```

**範例 output:**

```
✅ Frontmatter: all 6 traceability fields present
✅ Sections: Glossary(8 terms)/ Out-of-Scope(5)/ Assumptions(4)/ Constraints(3)
✅ Forbidden patterns: 0 TBD / 0 TODO / 0 non-testable acceptance
✅ Review process: 3 rounds completed, convergence achieved
✅ Open issues: 0 BLOCKER / 0 CONCERN / 3 NIT(cap 5)/ 8 STRENGTH
⚠ Per-REQ: 23 REQs total
   - 22 ✅ complete schema
   - 1 ❌ REQ-017 missing `proposed_module` field
⚠ Structural:
   - REQ-007 references REQ-099 which does not exist
   - proposed_modules covered: 5 modules, all have ≥ 1 REQ ✅
❌ Acceptance:
   - REQ-012 acceptance "用戶體驗良好" → non-testable, requires rewrite

Verdict: 3 issues found(1 missing field + 1 unresolved dep + 1 non-testable)
Phase 0 Exit: ❌ NOT ready
Next action: fix REQ-007 / REQ-012 / REQ-017,re-run validator
```

##### H. Downstream SKILL Consumption Mapping

對齊 §A,各 SKILL 如何讀 Requirement Spec:

| SKILL | 讀哪段 | 用途 |
|:---|:---|:---|
| V1 planning | priority + dependencies | 排 task timeline |
| V1 planning | proposed_module | 對齊模組劃分 |
| V2 implementation | acceptance | 寫對應 test |
| V2 implementation | description + rationale | 寫 functional spec |
| V7 module splitter | proposed_module + dependencies | 切模組 + 算 cross-module deps |
| V8 cross-module review | acceptance | 跨模組驗證 |
| spectra-review | 全文 | 7 維度 review |
| PM Skill `/pm validate-req-spec` | 全 schema | exit Phase 0 gate-check |
| PM Skill daily report | priority + status | 進度推導 |

##### I. 為什麼 STRENGTH 沒 upper bound(對齊 PO 拍板)

PO 初提「NIT + STRENGTH < 5」,但 STRENGTH 性質截然不同:

- **NIT** = 該 fix 的小瑕疵 → 越少越好(故 cap = 5)
- **STRENGTH** = 設計亮點 → 越多越好(spectra-review 鼓勵原則)

若 cap STRENGTH:
- spectra-review 為達 cap 會「自我審查」少寫優點
- review log 失真,PO 看不到設計亮點
- 失去「保留設計」accountability(eg. rev .5 把 STRENGTH S1 拆掉 → 無紀錄抗議)

→ STRENGTH 設 lower bound(≥ 3,沒亮點代表 review 心不夠),**no upper bound**(對齊 §B.2 拍板)。

##### J. Contract Version

- **req-contract-v1**(本提案)— Phase A 落地
- 後續 minor change(eg. 新增 optional field)升至 v1.1
- Major change(eg. 改 schema 結構)升至 v2,需 PO 拍板 + 12 週 deprecation 緩衝

##### K. Phase 0 Exit Check List(Validator 簡化版,給人工 walk through)

PM 在 Phase 0 結尾自我檢查:

- [ ] Requirement Spec 已對齊 §D schema(frontmatter + 6 mandatory sections)
- [ ] `/pm validate-req-spec <path>` 跑通(無 ❌)
- [ ] spectra-review 已跑 ≥ §C scaling 對應 rounds + 達 convergence
- [ ] `_summary-<slug>.md` Health Score 對齊 §B.2 cap
- [ ] 所有 BLOCKER/CONCERN 已 fix 或 rejected(無 pending / no_decision / deferred)
- [ ] Open NITs ≤ §C scaling 對應 cap
- [ ] STRENGTHS ≥ §C scaling 對應 min
- [ ] 0 forbidden pattern(grep TBD/TODO/etc = 0)
- [ ] Glossary / Out-of-Scope / Assumptions / Constraints 4 section min items 達標
- [ ] 每個 REQ 11 必填欄位完整(含 golden_scenario + anti_examples)
- [ ] dependency graph 無 circular / 無 unresolvable
- [ ] **PM 簽核**(state.md `phase_0_signoff = true`)

##### L. Contract Override Mechanism(對齊 spectra Round 1 C2 fix — Artifact Contract 對齊 spectra-review §6.4.4 trust hierarchy)

> **動機:** §6.4.4 Default vs Override 兩層架構僅 apply 到 spectra-review findings。本節 §6.4.10 / §6.4.11 Artifact Contracts 的 Exit Criteria(eg. `rounds_min: 3`)若全 hard-coded,**PO 對特定 project 客製化(eg. small POC rounds_min=1)沒有 governance path** → 違反 §6.4.4 trust hierarchy 原則。本段補齊。

**L.1 Override 適用範圍:**

可 override 的欄位(主觀 estimate / project-specific):

- `review_process.rounds_min`
- `open_issues_cap.*.open_max`(NIT cap / CONCERN cap 等數字)
- `open_issues_cap.strengths.lower_bound`
- §C size scaling 的「REQ count band」邊界
- 各 Phase artifact contract 的 `rounds_min` / quality bar 數字 thresholds

**不可 override**(architectural invariants):

- ❌ `blockers.open: 0`(BLOCKER 不可放行)
- ❌ structural_sanity 各條(no_circular / all_resolvable 等)
- ❌ machine-readability bar 必填項(glossary / out-of-scope 等 sections 強制)
- ❌ per-REQ 11 必填欄位(含三元組 golden_scenario + anti_examples)
- ❌ Phase 4 spec↔code↔test 三向 invariant
- ❌ Cross-Phase Lineage 鏈條完整性

**L.2 Override 條件:**

```yaml
contract_override:
  applies_to: <field path>            # eg. "§6.4.10.B.1.review_process.rounds_min"
  default_value: 3
  override_value: 1
  reason: "POC 探索期,2 weeks deadline;3 輪 review 太重"
  by: PO
  at: <ISO8601>
  scope: project-specific             # 或 organization-wide(後者需老闆 ack)
  deviation_pct: 66.7                 # |3-1|/3 = 66.7%
  ack_required:
    if_deviation_gt_50pct: PO_ack     # 觸發 PO 二次確認
    if_organization_wide: boss_ack
```

**L.3 Audit Trail(對齊 §6.4.7):**

每個 override 自動 append 至 `docs/decision-log.md`:

```
D-contract-override-<seq>: <field path> default=<X> → override=<Y> | reason | source: <project_slug>
```

**L.4 跨 Project Drift Detection:**

若同一 contract field 在 ≥ 3 個 project 被 override 至類似值 → PM Skill daily report 提示「**Default 可能過於嚴 / 鬆,建議 Phase C calibration 重校 baseline**」(對齊 §6.4.7 Phase C calibration loop)。

**L.5 Override 寫法**(整合到 Spec 內):

```yaml
# 在 Requirement Spec frontmatter 加段
contract_overrides:
  - applies_to: "§6.4.10.B.1.review_process.rounds_min"
    default: 3
    override: 1
    reason: "POC 探索期"
    ack: PO @ 2026-06-17
```

PM Skill `/pm validate-req-spec` 讀此段,先 honor override 再 check 其他 criteria。

**L.6 同樣機制 inherit 到 §6.4.11 Phase 1-7 Contracts:**

§6.4.11 每個 Phase artifact contract 預設 inherit §6.4.10 §L Override Mechanism;欲 override 該 Phase 的 cap 數字,寫法相同(改 `applies_to: §6.4.11.X.Y.Z`)。

---

#### 6.4.11 Phase 1-7 Artifact Contracts(對齊 §6.4.10 Framework)

> **本節定位:** 對齊 §6.4.10 Requirement Spec Artifact Contract 框架,定義 Phase 1-7 每階段 output artifact 的品質契約。
> **核心原則:** 每階段 artifact 都必須 machine-readable + 可驅動下游 phase / SKILL,避免「人讀懂機器讀不懂」造成 Phase 卡關。
> **與 §6.4.10 的關係:** §6.4.10 是 Phase 0 Requirement Spec(SDLC 起點)的契約;本節為 Phase 1-7 後續 artifact 的契約,共同構成完整 8 階段 quality bar。

##### A. Cross-Phase Artifact Lineage(完整追蹤)

```
┌──────────────────────────────────────────────────────────────────────────┐
│  Phase 0  Requirement Spec(§6.4.10)                                       │
│           ↓ priority / dependencies / proposed_module                       │
│  Phase 1  _plan.md(§6.4.11.B)— V7 module splitter output                  │
│           ↓ module list / owner / deps                                      │
│  Phase 2  modules/<name>/{requirement,functional,plan}.md(§6.4.11.C)       │
│           ↓ acceptance / feature breakdown                                  │
│  Phase 3  Shared Infra(§6.4.11.D)                                         │
│           ↓ shared code(schema/utility/hook/mock cmd) + integration guide  │  ← N5 fix
│  Phase 4  modules/<name>/{tests,test-results}.md + functional.md(§6.4.11.E)│
│           ↓ implementation done / spec sync                                 │
│  Phase 5  integration-test-results.md + perf-results.md(§6.4.11.F)        │
│           ↓ E2E passed                                                       │
│  Phase 6  deploy-log.md + smoke-test-results.md + rollback-plan.md(§G)    │
│           ↓ production live                                                  │
│  Phase 7  kpi-evaluation + user-feedback-log + final-retrospective(§H)    │
│           ↓ project closed + lessons learned                                │
└────────────────────────────────────────────┬─────────────────────────────┘
                                              │
                       Retrospective seeds ↓ next project's Phase 0  ← N4 fix
                       (Lessons → next Requirement Spec's Constraints / Assumptions)
                                              │
                                              ↓
                                  [next project Phase 0 ...]
```

**Cross-phase invariant:** 每階段 Exit 必通過該階段 Validator,才能 Entry 下階段;斷鏈即 Phase Gate fail。

**Iteration loop(對齊 spectra Round 1 N4 fix):** Phase 7 retrospective 不是「丟掉」的文件 — `final-retrospective.md` 的 Lessons learned 段必須 feed 回 organizational knowledge base,並在下一個 project 的 Phase 0 Requirement Spec 的 §Assumptions / §Constraints / §Glossary 段引用前一專案經驗(避免重蹈覆轍)。PM Skill `/pm validate-req-spec` 可選 check「是否引用了 ≥ 1 個前專案 retrospective lesson」作為品質訊號。

##### B. Phase 1 — Module Plan Artifact Contract

> ⚠ **rev 1.13 SDLC v2 OVERRIDE(2026-06-20 PO lock):** 本段為 v1 contract(`_plan.md` only)。v2 已 EXPAND Phase 1 為 5-step dialogue(split + build-team + assign + functional spec + design spec)+ NEW deliverable `<project>-modules-overview.md`(HUMAN-FIRST 3-role structure per memory `feedback_human_first_docs`)。本段保留 historical reference + grandfather projects(past Phase 2 signoff)。Detailed v2 contract:**§6.4.16**。

**Artifact:** `docs/modules/_plan.md`(V7 module splitter SKILL output)
**Contract Version:** `module-plan-contract-v1`

**B.1 Mandatory Sections:**

1. Frontmatter(spec_type / version / project / upstream/downstream traceability)
2. Module List(每個 module 一個 entry,對齊 §B.2 schema)
3. Cross-Module Dependency Graph(textual 或 mermaid,可被 parser 讀)
4. Shared Files Coordination(列出衝突點 + 協調機制)
5. Branch Naming Convention
6. Phase 2 Entry Roadmap

**B.2 Per-Module Schema(每 module 必填欄位):**

```yaml
module:
  id: module-<name>                # eg. module-identity / module-quota
  name: <human readable>
  owner: <engineer name>           # 對齊 team-roster.md
  scope: <一行內描述>
  covers_reqs: [REQ-001, REQ-005]  # 對齊 Phase 0 REQ IDs(此 module 主要負責,1:N exclusive)
  cross_cutting_reqs: []           # 對齊 spectra Round 1 C3 fix — 此 module 共同認領的 cross-cutting REQ(N:M non-exclusive)
                                   # eg. [REQ-010] 「全 module 共用 error message format」可同時在 ≥ 2 module 的 cross_cutting_reqs 出現
  depends_on: []                   # 其他 module IDs
  depends_by: []                   # blocked by this module 的 module IDs
  estimated_size: small | medium | large
  shared_files: []                 # 此 module 會動的 shared file paths
  branch_name: feature/<name>
  spec_paths:
    requirement: "docs/modules/<name>/requirement.md"
    functional: "docs/modules/<name>/functional.md"
    plan: "docs/modules/<name>/plan.md"
```

**Cross-cutting REQ 處理原則(V7 SKILL 對齊):**

- 若 REQ 本質 cross-module(eg. 共用 error format / 共用 audit log scheme)→ V7 列入 ≥ 2 module 的 `cross_cutting_reqs`
- 任一 module 動到該 REQ 對應 design,**必同時通知其他認領 module owner**(V8 cross-module review 強制 check)
- 替代方案:V7 可選擇 split into module-specific sub-REQs(若可拆),拆完用一般 `covers_reqs`

**B.3 Exit Criteria:**

```yaml
review_process:
  rounds_min: 2                    # _plan.md 結構簡單,2 輪足夠
  convergence_rule: "last 1 round 0 BLOCKER"

open_issues_cap:
  blockers: { open: 0 }
  concerns: { open: 0, deferred_max: 1 }
  nits: { open_max: 3 }
  strengths: { lower_bound: 2, no_upper_bound: true }

structural_sanity:
  no_circular_module_deps: true     # module-A → module-B → module-A 禁止
  all_root_reqs_covered: true       # 每個 Phase 0 REQ ≥ 1 module's covers_reqs OR cross_cutting_reqs(對齊 C3 fix)
  no_orphan_modules: true           # 不可有 module 不 cover 任何 REQ
  unique_owner_per_module: true     # 同 owner 可帶多 module,但不可衝突
  shared_files_coordinated: true    # 所有跨 module 共動的 file 都列在 Shared Files
  module_count_in_range: "2-10"     # < 2 不切;> 10 過細
  cross_cutting_reqs_acked: true    # 對齊 C3 fix — 所有 cross_cutting_reqs 必被 ≥ 2 module 認領;0 module 認領視同 orphan
```

**B.4 Forbidden Patterns:** TBD / TODO / 待定 = 0;owner = "未定" / "TBD" = 0

**B.5 Validator:** `/pm validate-module-plan <path>`

**B.6 Downstream Consumption:**

| SKILL | 讀啥 | 用途 |
|:---|:---|:---|
| V2 implementation | `covers_reqs` | 知道 module 要實作哪些 REQ |
| V8 cross-module review | dependency graph | 排 review priority |
| PM Skill daily report | owner + estimated_size | 推導 timeline / 列誰負責什麼 |
| Phase 2 setup | `spec_paths` | 創建 R/F/P 空 spec 檔 |

**B.7 Phase 1 Exit Check List:**

- [ ] `_plan.md` 對齊 §B.1-§B.5 全部
- [ ] `/pm validate-module-plan <path>` 全 pass
- [ ] 每個 Phase 0 REQ 都被至少 1 module covered
- [ ] dependency graph 無 circular
- [ ] PM 簽核 state.md `phase_1_signoff = true`

##### C. Phase 2 — Per-Module Spec Artifact Contract

> ⚠ **rev 1.13 SDLC v2 OVERRIDE(2026-06-20 PO lock):** 本段為 v1 contract(3 specs per module:R/F/P)。v2 已 LIGHTEN Phase 2 為 plan.md only — functional + design spec 已在 Phase 1 Step 1.4/1.5 完成。Solo project 可 collapse Phase 2 進 Phase 1(PO override + log)。本段保留 historical reference + grandfather projects(past Phase 2 signoff)。Detailed v2 contract:**§6.4.16**。

**Artifacts(每模組 3 份 × N modules):**
- `docs/modules/<name>/requirement.md` — module-level REQ(從 root REQ 衍生)
- `docs/modules/<name>/functional.md` — feature 規格 + Status 追蹤
- `docs/modules/<name>/plan.md` — task breakdown + timeline

**Contract Version:** `module-spec-contract-v1`

**C.1 Per-File Mandatory Sections:**

`requirement.md`:
1. Frontmatter(spec_type=module-requirement / upstream=root-req-spec / module_id)
2. Module Overview
3. Module-Level Requirements(refine root REQs,format 同 §6.4.10 D)
4. Module-Specific Constraints
5. Module-Specific Glossary(extends root glossary)

`functional.md`:
1. Frontmatter(spec_type=module-functional / cross-refs)
2. Feature List(每 feature 一 entry,對齊 §C.2 schema)
3. Module Architecture Overview
4. Cross-Module Touchpoints(明示 import / export)

`plan.md`:
1. Frontmatter(spec_type=module-plan)
2. Task Breakdown(每 task 對齊 §C.3 schema)
3. Timeline
4. Risk & Mitigation

**C.2 Per-Feature Schema(functional.md):**

```yaml
feature:
  id: F-<module>-<seq>             # eg. F-identity-001
  title: <name>
  derived_from_reqs: [REQ-001]     # root REQ traceback
  description: <full>
  acceptance: [...]                # 同 §6.4.10 standard,machine-checkable
  status: ⏳ planned | 🟡 in-progress | 🚫 blocked | ✅ done | ⚠ at-risk
  expected_completion: <YYYY-MM-DD>
  actual_completion: <YYYY-MM-DD> | null
  execution_log: []                # V2 SKILL append
  dependencies:
    blocked_by_features: []
    blocked_by_modules: []
  
  # ⭐ rev 1.8 新增 — Schema Migration Awareness(對齊 §G.6.0)
  schema_change: false              # 預設 false;true 則必填 migration_id
  migration_id: null                # eg. "001";對應 docs/migrations/manifest.yaml entry
```

**C.2a Schema Change Tagging(rev 1.8 — 對齊 memory `backend_schema_change_workflow`):**

任何 feature 觸發以下情況之一,**必填 `schema_change: true`**:
- DB schema 改動(ALTER TABLE / CREATE TABLE / INDEX 等)
- `laundry_db_create_tables.sql` SSOT 變更
- 既有 column 語意 / nullable / default value 改動

PM Skill 自動偵測機制(對齊 §G.6.0):
- `/v2 done <feature>` 時若 grep 該 feature commit 含 `*.sql` 改動 → 提示 PO 確認 `schema_change: true`
- `/pm validate-module-spec` 加 invariant:若 git diff 顯示 schema 改動但 functional.md 標 `schema_change: false` → fail

**C.3 Per-Task Schema(plan.md):**

```yaml
task:
  id: T-<module>-<seq>
  title: <name>
  implements_features: [F-identity-001]
  estimated_hours: <number>
  assignee: <engineer>
  status: ⏳ todo | 🟡 wip | ✅ done | 🚫 blocked
  blockers: []
```

**C.4 Exit Criteria:**

```yaml
review_process:
  rounds_min: 3                    # spec 複雜度 = 多輪
  convergence_rule: "last 2 rounds 都 0 new BLOCKER"

open_issues_cap:
  blockers: { open: 0 }
  concerns: { open: 0, deferred_max: 2 }
  nits: { open_max: 5 }
  strengths: { lower_bound: 3 }

structural_sanity:
  all_root_reqs_traceable: true     # 每 root REQ ≥ 1 derived module REQ
  all_features_traceable: true      # 每 feature derived_from ≥ 1 module REQ
  all_tasks_traceable: true         # 每 task implements ≥ 1 feature
  cross_module_touchpoints_listed: true  # functional.md 必明示
  v8_cross_module_review_passed: true   # V8 最後一輪 verdict='ship'
```

**C.5 Validator:** `/pm validate-module-spec <module-name>`(per-module)/ `/pm validate-module-spec --all`(全 module)

**C.6 Downstream Consumption:**

| SKILL | 讀啥 | 用途 |
|:---|:---|:---|
| V2 implementation | feature.acceptance + task list | 寫 code + test |
| PM Skill daily report | feature.status + task.status | 推導模組進度 |
| V8 cross-module review | cross_module_touchpoints | 排 review focus |
| Phase 4 health-check | functional.md ↔ code 對齊 | 偵測 spec/code drift |

**C.7 Phase 2 Exit Check List:**

- [ ] N modules × 3 specs(共 3N files)全對齊 §C.1-§C.4
- [ ] `/pm validate-module-spec --all` 全 pass
- [ ] root REQ → module REQ → feature → task 4 層 traceability 完整
- [ ] V8 cross-module review 最後一輪 0 BLOCKER carry-over
- [ ] PM 簽核 state.md `phase_2_signoff = true`

##### D. Phase 3 — Shared Infrastructure Artifact Contract

**Artifacts(混合 code + docs):**
- `laundry_db_create_tables.sql`(schema update)
- `system_lib.py` helper(common utility)
- `backend-integration-guide.md`(cmd 合約登錄)
- `v3/index.html`(`__moduleInitHooks` pattern setup)
- `v3/theme.css`(CSS namespace convention)
- Mock backend cmd code
- `docs/reviews/<date>-V3-shared-infra-review.md`

**Contract Version:** `shared-infra-contract-v1`

**D.1 Mandatory Outputs(對齊 memory: backend_schema_change_workflow):**

```yaml
shared_infra:
  db_schema_changes:
    sql_ssot_updated: true        # laundry_db_create_tables.sql 必同步
    alter_table_ready: true       # ALTER TABLE 3 樣
    backward_compat_documented: true
    
    # ⭐ rev 1.8 新增 — Migration Manifest(對齊 §G.6.0)
    migration_manifest_entry_added: true   # docs/migrations/manifest.yaml 新加 entry
    migration_sql_file_created: true       # docs/migrations/<date>-<NNN>-<slug>.sql
    forward_backward_verify_sql_complete: true  # 3 樣對齊 memory: ALTER TABLE 3 樣
  
  python_helpers:
    documented_in_guide: true     # backend-integration-guide.md 登錄
    lint_baseline_unchanged: true # ruff F821/F 不增(memory: backend_lint_workflow)
  
  frontend_shared:
    hook_pattern_documented: true # __moduleInitHooks
    css_namespace_documented: true
  
  mock_cmd:
    contracts_match_real_backend: true  # mock 簽名跟 real backend 一致
    callable_from_frontend: true
```

**D.2 Exit Criteria:**

```yaml
review_process:
  rounds_min: 1                   # infra 主要靠 V8 + lint,review 1 輪即可
  v8_shared_infra_review_passed: true
  
  # ⭐ rev 1.9 新增 — V8 Cross-Module Spec Review(對齊 PO 拍板 Gap 4 — V8 move to Phase 3 末)
  v8_cross_module_spec_review:
    rounds_min: 1
    final_verdict: ship-as-is
    carry_over_blockers: 0
    review_scope:
      - api_contract_between_modules     # cross-module cmd / response shape
      - data_ownership_ssot              # 誰擁有 data,who reads / writes
      - schema_dependency                 # module 間 schema 依賴
      - cross_module_invariant            # 跨模組 invariant(profile/bizcard 等)
      - token_action_naming               # i18n key / action token 跨模組對齊
    review_target:
      - all_module_functional_md          # F-spec
      - all_module_plan_md                 # D-spec(= plan.md,對齊 §C.1 既有三檔結構,non-split)
      - shared_infra_documentation        # §D.1 全 artifact
    review_participant:
      - all_engineers                     # 5 engineer 共審
      - tech_lead
      - po                                 # PO 最終拍板
    spec_lock_after_pass: true            # V8 ship-as-is 後 spec read-only,進 Phase 4
    rationale: |
      對齊 PO 哲學「all module cross review job in done before coding」。
      Cross-module gap 在 spec 階段 catch ~$1 cost,
      vs Phase 4 code 階段 catch ~$10,vs Phase 6 prod $100。

quality_bar:
  lint_baseline_delta: 0          # ruff F821 / F 不可增
  test_coverage_min: 80%          # shared utility 必有測試
  schema_ssot_synced: true        # 對齊 memory: backend_schema_change_workflow
  no_breaking_change_to_existing_callers: true
  
  # ⭐ rev 1.8 新增 — Migration Manifest 一致性
  schema_migration_manifest_consistent: true
    # 條件:
    # - laundry_db_create_tables.sql 跟 manifest.yaml 內所有 forward_sql 累積結果一致
    # - 每 migration 有 forward / backward / verify SQL 三樣完整
    # - 無 dangling migration(manifest 列了但 .sql file 不存在)
```

**D.3 Validator:** `/pm validate-shared-infra`(跑 lint + test + schema diff check + migration manifest consistency)

**D.4 Downstream:** Phase 4 全 module 共用本 Phase output;若 D.1 任一項 fail → Phase 4 不可 entry

**D.5 Phase 3 Exit Check List:**

- [ ] DB schema 寫入 SSOT + ALTER TABLE ready
- [ ] **Migration manifest entry 加完 + .sql file 生成(對齊 §G.6.0)** ⭐ rev 1.8
- [ ] **Forward / backward / verify SQL 三樣完整(對齊 memory: ALTER TABLE 3 樣)** ⭐ rev 1.8
- [ ] `bash lint.sh` 跑通,F821 / F 0 增量
- [ ] shared utility 測試 coverage ≥ 80%
- [ ] backend-integration-guide.md 已登錄新 cmd
- [ ] Mock cmd 可從 frontend 呼叫
- [ ] V8 共用設計 quality review pass
- [ ] **V8 cross-module spec review 最後一輪 verdict=ship-as-is + 0 carry-over BLOCKER(對齊 Gap 4 PO 拍板)** ⭐ rev 1.9
- [ ] **All module F-spec + D-spec 進入 read-only lock state(對齊 Stage 0 gate)** ⭐ rev 1.9
- [ ] PM 簽核 state.md `phase_3_signoff = true`

##### E. Phase 4 — Module Implementation Artifact Contract

**Artifacts:**
- Code(各 module branch,PR merged to integration branch)
- `docs/modules/<name>/tests.md`(× N modules)— test case spec
- `docs/modules/<name>/test-results.md`(× N modules)— test 跑分結果
- `docs/modules/<name>/functional.md`(updated:每 feature `status: ✅ done` + actual_completion + execution_log)
- daily / weekly PM reports
- V8 cross-module review logs(N rounds)

**Contract Version:** `implementation-contract-v1`

**E.1 Per-Test-Case Schema(tests.md):**

```yaml
test_case:
  id: TC-<module>-<seq>
  derived_from_acceptance: "F-identity-001 / acceptance #2"
  steps: []
  expected: <description>
  category: unit | integration | e2e
```

**E.2 Per-Test-Result Schema(test-results.md):**

```yaml
test_run:
  date: <YYYY-MM-DD>
  commit_hash: <git sha>
  total: <N>
  passed: <N>
  failed: <N>
  failures: []                     # 每 failure 列 case_id + root_cause
```

**E.3 Spec ↔ Code ↔ Test 三向 invariant(PM Skill 健康檢查核心):**

```yaml
implementation_sync:
  every_feature_has_code_commit: true       # functional.md feature status=done 必對應 ≥ 1 commit
  every_feature_has_test_case: true         # 每 feature 必對應 ≥ 1 TC
  every_test_case_has_result: true          # 每 TC 必有 run result
  no_stale_functional_md: true              # 不可 commit 過了 functional 沒 update
  execution_log_per_done_feature: true      # done status 必有 execution_log
  actual_completion_filled: true            # done 必有 actual_completion 日期
```

**E.3a How to Enforce(對齊 spectra Round 1 B1 fix — 每條 invariant 提供具體 check 命令)**

> 對齊「Stage Gate 機械化」§6.5 特性 2 原則,每條 invariant 必須可被 PM Skill validator 機械化驗證,不靠人工。
>
> **⭐ Operationalized(2026-07-03,P coverage-gate + spectra fixes):** `every_feature_has_test_case`(top-down)+ **bidirectional orphan-TC**(bottom-up)已實作為真 gate —— `scripts/pm_coverage_validator.py`(stdlib,regex-based,取代下列 yq pseudo-check)+ `/pm validate-coverage`,掛 **gate-check phase-4 criterion(實跑 exit≠0 → ❌)**。
> **REQ→TC 覆蓋為 compose(C2 精確化):** REQ→**module** 由 phase-1 C7 保證(粗粒度,`modules[].covers_reqs`)+ feature→TC 由本 validator 保證;**module→feature 的 REQ-level 精確追溯為 open gap**(C7 非 REQ→feature),故不宣稱端到端 REQ→TC 已保證。
> **Machine-parse contract(B1 normative):** functional.md 必含結構化 `features:` block(每 item `id: F-xxx` + `status:`),tests.md 必含 `test_cases:` block(每 item `id: TC-xxx` + `derived_from_acceptance:`)—— human-first prose 之外須有此可機解 sub-block;validator 若在非空檔解析出 0 feature/0 TC → 判 **format-mismatch(HARD,非靜默 pass)**。
> graceful skip 無 module 之專案。其餘 invariant(code_commit / test_result / stale / execution_log)仍為 pseudo-check,待後續 operationalize。

```yaml
enforcement:
  every_feature_has_code_commit:
    check: |
      # 對 functional.md status='done' 的 feature,
      # grep git log 找 feature_id 必 ≥ 1 commit
      for fid in $(yq '.features[] | select(.status=="done") | .id' functional.md); do
        count=$(git log --grep="$fid" --oneline | wc -l)
        [ "$count" -ge 1 ] || fail "$fid: no commit"
      done

  every_feature_has_test_case:
    check: |
      # 每 done feature 必在 tests.md 找到 ≥ 1 TC 的 derived_from_acceptance 引用
      for fid in $(yq '.features[] | select(.status=="done") | .id' functional.md); do
        tc_count=$(yq ".test_cases[] | select(.derived_from_acceptance | contains(\"$fid\"))" tests.md | wc -l)
        [ "$tc_count" -ge 1 ] || fail "$fid: no TC"
      done

  every_test_case_has_result:
    check: |
      # 每 TC 在 test-results.md 必有對應 run result
      for tcid in $(yq '.test_cases[].id' tests.md); do
        result=$(yq ".test_runs[] | .results[] | select(.case_id==\"$tcid\")" test-results.md)
        [ -n "$result" ] || fail "$tcid: no run result"
      done

  no_stale_functional_md:
    check: |
      # functional.md mtime ≥ 最近一次 code commit mtime
      # (若 code 動了 functional.md 沒動,代表 spec 漂移)
      func_mtime=$(stat -c %Y functional.md)
      last_code_mtime=$(git log -1 --format=%ct -- "src/<module>/" "js/<module>/")
      [ "$func_mtime" -ge "$last_code_mtime" ] || fail "functional.md stale vs code"

  execution_log_per_done_feature:
    check: |
      for fid in $(yq '.features[] | select(.status=="done") | .id' functional.md); do
        log_count=$(yq ".features[] | select(.id==\"$fid\") | .execution_log | length" functional.md)
        [ "$log_count" -ge 1 ] || fail "$fid: no execution_log"
      done

  actual_completion_filled:
    check: |
      for fid in $(yq '.features[] | select(.status=="done") | .id' functional.md); do
        ac=$(yq ".features[] | select(.id==\"$fid\") | .actual_completion" functional.md)
        [ "$ac" != "null" ] || fail "$fid: missing actual_completion"
      done
```

**Enforcement 整合到 `/pm validate-implementation`:**

PM Skill validator 跑這 6 條 check,任一 fail → Phase 4 Exit 阻擋。Fail 列表自動 append 到 `docs/pm/state.md` `outstanding_blockers` 段。

**"stale" 操作型定義:** `functional.md mtime < latest code commit mtime affecting this module's path`(對齊 spectra Round 1 N2 fix)。

**E.4 Exit Criteria:**

```yaml
review_process:
  # ⭐ rev 1.9 — V8 從 Phase 4 移到 Phase 3 末(對齊 Gap 4 PO 拍板)
  # 原 v8_rounds_min: 2(開發中 + 結尾各 1 輪)→ 簡化
  v8_rounds_min: 0                          # Phase 4 預設無需 V8(已在 §D Phase 3 end close)
  v8_drift_check_required: conditional      # 對齊 §E.4a Mid-flight Drift Check
  v8_final_round_verdict: ship-as-is        # 若有 drift check,verdict 必過
  v8_carry_over_blockers: 0

open_issues_cap:
  blockers_open: 0
  concerns_open: 0
  nits_open_max: 5

quality_bar:
  all_features_done: true         # 全 module's functional.md feature 都 status=done
  all_tests_passed: true          # 全 module's test-results 100%(對齊 §E.4a flaky_test_tolerance)
  spec_code_test_sync: true       # 對齊 §E.3 三向 invariant
  lint_baseline_delta: 0
  decision_log_no_pending: true   # 無 pending 拍板
  pr_all_merged_to_integration: true
```

**E.4a Flaky Test Tolerance Policy(對齊 spectra Round 1 user-manual C2 fix — real-world intermittent test 處理)**

> 嚴格 `all_tests_passed: true` 在真實工作流會被 intermittent / flaky test 卡死(eg. 網路抖動 / 環境依賴 / race condition 邊界)。本子段定義 **flaky test 合法接受機制**,避免 manual 教 PO bypass invariant。

```yaml
flaky_test_tolerance:
  enabled: true                    # 預設啟用
  max_flaky_per_module: 2          # 每 module ≤ 2 個 flaky TC
  max_flaky_total: 5               # 全 project ≤ 5 個
  
  # 一個 TC 要被合法標 flaky 必須:
  required_to_mark_flaky:
    - retry_count_min: 3           # 至少跑 3 次
    - pass_rate_min: 0.66          # 通過率 ≥ 66%(3 次跑 2 次過)
    - retry_mechanism_in_place: true  # tests.md 已加 retry logic
    - root_cause_documented: true  # tests.md 加 known_flaky_reason 欄位
    - po_acked: true               # PO 在 /pm-bug-review 拍板
  
  # 違反任一條件 → invariant 全 fail
  hard_fails:
    - pass_rate < 0.66 → 必修,不可 mark flaky
    - retry without root cause → reject(避免 cosmetic retry 掩蓋真實 bug)
    - count > max_flaky_per_module → Phase 4 exit block
  
  # flaky test schema 對齊 §E.1
  test_case_flaky_marker:
    flaky: true
    flaky_pass_rate: 0.67          # 過去 N 跑的通過率
    retry_count: 3
    known_flaky_reason: "Azure API rate limit p99 抖動,< 5% case"
    po_ack_date: 2026-06-18
    revisit_at: 2026-08-01         # 必排 revisit 日期,不可永久 flaky
```

**flaky vs hard fail 判定流程:**

```
test fail
  ↓
spec_code_test_sync check
  ↓
retry 3 times
  ├─ pass_rate ≥ 0.66 → 可走 flaky path(需上述 5 條件)
  └─ pass_rate < 0.66 → hard fail,Phase 4 exit block
       ↓
       /pm-bug-review 拍板:fix 或 reject
```

**E.4b Mid-flight Cross-Module Contract Drift Check(rev 1.9 — 對齊 Gap 4 V8 pre-coding 的 Concern 3 mid-flight scenario)**

> Phase 3 V8 ship-as-is 後 spec lock,Phase 4 進場。若 coding 中發現 spec 沒 cover 的 cross-module edge,不能 silently 改 — 必走 drift check gate(對齊 §6.4.13 Contract Change Governance + memory `backend_change_rule` propose 紀律)。

**E.4b.1 Drift Check Trigger:**

```yaml
drift_check_triggers:
  - any_change_to_cross_module_api_shape: required
    # eg. module A's exported cmd signature changes,affecting module B caller
  
  - any_new_cross_module_dependency_introduced: required
    # eg. module A 原本不 depend on module B,現在加 import
  
  - any_change_to_data_ownership_ssot: required
    # eg. module A 原 own data X,現在改 module B own
  
  - internal_module_impl_only: not_required
    # internal refactor / lint fix / typo 等不觸發
```

**E.4b.2 Drift Check Workflow:**

```yaml
workflow:
  1_engineer_initiates:
    command: /pm contract-change propose
    input: scope description + diff
  
  2_skill_classify:
    behavior:
      - SKILL 評估 scope 是否觸發任一 §E.4b.1 trigger
      - IF triggered:proceed step 3
      - IF NOT:approve as patch change(對齊 §6.4.13 patch tier)
  
  3_lite_v8_drift_check:
    rounds_min: 1                          # 只 1 輪,不全 spec re-review
    review_scope: ONLY the diff scope      # 對應改動範圍,不擴張
    final_verdict: ship-as-is
    carry_over_blockers: 0
    duration_estimate: 1-2 hour            # vs Phase 3 full V8 1-2 day
  
  4_post_drift_check:
    - update affected module spec(F-spec / D-spec)
    - SKILL re-lock spec read-only state
    - decision-log append:D-pm-<id>: Mid-flight contract change <scope>, drift check verdict
  
  5_coding_resume:
    Phase 4 coding 繼續,基於 updated spec
```

**E.4b.3 Drift Check 跟 §6.4.11 Phase 4 Re-entry 關係:**

| 場景 | 動作 |
|:---|:---|
| Drift check verdict=ship-as-is | Phase 4 continue,no phase rollback |
| Drift check verdict=revise-design | Phase 4 paused,**spec back to Phase 2/3 re-do**(對齊紀律) |
| Engineer skip drift check | push-gate(§E.8.4)reject,因 cross-module API shape change 必過 gate |

**E.4b.4 Confidence Tier:** 🟡 medium(SKILL classify trigger 自動,但 lite V8 review 需 engineer + PO 參與)

**E.4b.5 Spec Re-entry Workflow(rev 1.10.1 — 對齊 spectra Round 1 B2 fix:spec lock vs revise-design 衝突)**

> §D.2 v8_cross_module_spec_review.spec_lock_after_pass: true 確立「Phase 3 V8 pass 後 spec read-only」。但 §E.4b.3 verdict=revise-design 需 spec back to Phase 2/3 re-do。**spec lock 是 soft lock**,本子段定義 unlock workflow,避免 dead-end。

```yaml
spec_lock_state:
  default: read-only_after_v8_pass
  
  unlock_conditions:
    - trigger: drift_check verdict=revise-design
      action: SKILL prompt PO confirm phase rollback necessity
      po_decision_required: true
    - trigger: PO manual unlock(罕用 emergency)
      action: PO 必輸 reason + confirmation
  
  unlock_workflow:
    1. SKILL 偵測 drift_check verdict=revise-design
    2. SKILL 顯示 affected spec scope(diff 對應的 module spec)
    3. SKILL prompt PO:「確定 phase rollback(Phase 4 → Phase 2/3)修 spec?(y/N)」
    4. PO confirm:
       - SKILL temporarily unlock affected spec(僅 unlock 對應 scope,非 unlock 全 spec)
       - SKILL append decision-log: D-pm-<id>: Spec rollback for drift, scope=<...>, reason=<text>
       - state.md 紀錄 spec_lock_state transition: locked → temporary_unlocked
    5. Engineer/PO 修 spec(對齊 §C.1 三檔結構)
    6. SKILL 觸發 re-V8(可 lite scope,只 review 改動 spec):
       - rounds_min: 1
       - scope: ONLY unlocked spec range
       - verdict_required: ship-as-is
       - carry_over_blockers: 0
    7. Re-V8 pass:
       - SKILL re-lock spec
       - state.md transition: temporary_unlocked → locked
       - append decision-log: re-V8 ship-as-is, spec re-locked
    8. Phase 4 coding 繼續(基於 updated spec)
  
  audit_requirements:
    - 每次 unlock + re-lock 都 append decision-log
    - state.md `spec_lock_transitions[]` 累計紀錄(供 Phase 7 retro)
    - Override metrics tracking(對齊 §K.9 alarm — 若 unlock 頻繁 → 警示 V8 quality 不足)
  
  edge_cases:
    - 若 re-V8 verdict=revise-design 連兩次:escalate Phase 4 paused,Tech Lead/PO 評估是否 full Phase 2/3 rework
    - 若 PO 拒 rollback(認為 drift 可 ignore):append decision-log + flag risk,可能撞 Phase 5 整合 fail
```

**E.4b.6 Confidence Tier:** 🟡 medium(unlock 需 PO 拍板,re-V8 機械化但 scope 判斷需 engineer 共識)

**E.5 Validator:** `/pm validate-implementation <module-name>` 或 `/pm validate-implementation --all`

**E.6 Downstream:** Phase 5 integration entry 條件

**E.7 Phase 4 Exit Check List:**

- [ ] 全 module 全 feature `status: ✅ done` + actual_completion 已填
- [ ] 全 module test-results 100% pass
- [ ] 全 PR 已 merged to integration branch
- [ ] V8 最後一輪 verdict=ship-as-is + 0 carry-over BLOCKER
- [ ] PM 健康檢查 spec↔code↔test 三向 sync 通過
- [ ] Backend lint baseline 不增
- [ ] Decision log 無 pending 拍板
- [ ] PM 簽核 state.md `phase_4_signoff = true`

**E.8 Multi-Dev Workflow Commands(v1.2 Planned — 對齊「5 engineer 共用 worktree」架構)**

> 對齊 PO 2026-06-18 拍板的 3-stage promotion model:**team worktree(Stage 1)→ main(Stage 2)→ Azure Web App(Stage 3)**。本子段定義 Phase 4 期間 daily 開發必要命令,補既有 §E.5 `/pm validate-implementation` 之外的 worktree lifecycle gap。

**E.8.1 Architecture Premise:**

> ⭐ **rev 1.17 amendment(2026-06-23 PO 拍板 Option A):** worktree lifecycle expanded — covers Phase 3 + Phase 4(originally Phase 4 only)。**Rationale:** Phase 3 shared infra commits to main pre-QA = WIP pollution risk(orphan schema if Phase 4 abandoned)。Main 保留 always-deployable invariant。

```
Phase 0-2 ─── docs only ─── main(spec/requirement/plan,zero codebase change)
   ↓ /pm advance-phase 3 → AUTO trigger /pm setup-worktree(NEW timing,rev 1.17)
   ↓
Stage 0(Phase 3 起): Worktree opens — branch `dev/<project>`
   • V8 Cross-Module Spec Review still happens at Phase 3 末(unchanged)
     - 5 engineer + Tech Lead + PO 共審 N 個 module F-spec + D-spec
     - review scope:api_contract / data_ownership / schema_dependency
                     / cross_module_invariant / token_action_naming
     - verdict 必 ship-as-is + 0 carry-over BLOCKER
     - spec 進 read-only lock state
     - 此 gate 過 → Phase 4 開放(/pm advance-phase 4 unblocked)
     - 未過 → block,spec 回 Phase 2/3 修
     - 對齊 Gap 4 PO 哲學「all module cross review job in done before coding」
   ↓ Phase 3 signoff + V8 verdict=ship-as-is(對齊 §D.2 / §D.5)
   ↓
Stage 1: Team Worktree(branch `dev/<project>`,Phase 3 + Phase 4,長期 long-lived)
   • Phase 3 shared infra(schema SSOT + 共用 helper) 全 commit 到 worktree(NEW,rev 1.17)
   • Phase 4 期間 5 engineer 全 push 到這(unchanged)
   • daily sync + conflict 立刻解
   • 「告一段落 + 會動」才能 push
   • cross-module contract drift → /pm contract-change propose → lite V8(對齊 §E.4b)
   ↓ Project 開發完成 + validate-implementation --all pass
   ↓
Stage 2: Main(Phase 5 QA — 對齊 §F)
   • worktree → main merge(auto by /pm advance-phase 5)
   • 跑 §F E2E + perf + staging migrations applied(對齊 §G.6.0)
   • 此時 main 才見到 Phase 3 shared infra + Phase 4 module dev 整個 bundle
   ↓ PM 同意品質
   ↓
Stage 3: Azure Web App(Phase 6 release — 對齊 §G)
   • Migration Gate(§G.6.0)+ /pm deploy(§G.6.1)

⭐ Invariant: main is ALWAYS-DEPLOYABLE(對齊 PO 2026-06-23 mental model)
   - Phase 3+4 WIP never visible in main
   - Project abandoned mid-way = git worktree remove ../<project> + git branch -D dev/<project>; main 0 cleanup needed
   - Multiple parallel projects = multiple ~/<project>/ worktrees coexist (rev 1.17.2)
```

**Filesystem Layout(rev 1.17.2 — `git worktree add` + folder=project name):**

```
~/AzureLineBOT-main/                    ← main repo
  ├── .git/                              ← shared object database
  ├── app.py                             ← prod-ready code
  ├── templates/                         ← prod frontend
  ├── docs/pm/<project-A>/state.md       ← per-project state (always in main repo)
  └── ... (deploy 來源:Azure WebApp pulls from main)

~/<project-A>/                          ← worktree A (branch=dev/<project-A>)
  ├── .git                               ← pointer file (hardlinked to main .git)
  ├── app.py                             ← WIP code (Phase 3+4)
  ├── templates/                         ← WIP frontend
  └── ... (full frontend + backend snapshot)

~/<project-B>/                          ← worktree B (branch=dev/<project-B>)
  └── ... (parallel project, independent WIP)

Deployment path(per memory project_v2_backend_integration):
  ~/AzureLineBOT-main/ (main branch) → Azure WebApp prod (liffbeauty.azurewebsites.net)

Testing path during Phase 4(rev 1.17.2):
  Path A: cd ~/<project-A>/ && gunicorn app:app (local)
  Path B (optional): push dev/<project-A> → liffbeauty-staging (separate Azure WebApp)
```

**E.8.2 `/pm setup-worktree` — Phase 3 起始(對齊 `/pm advance-phase 3` 自動觸發):**

> ⭐ **rev 1.17 amendment(2026-06-23 PO 拍板 Option A):** Trigger moved from Phase 4 entry → Phase 3 entry。**Rationale:** Phase 3 shared infra(schema SSOT change + 共用 helper)is ALSO "in-flight project artifact" — committing to main pre-Phase-5-QA pollutes main with WIP that may never ship。Worktree should encapsulate ALL phases that materially change the codebase(Phase 3 shared infra + Phase 4 module dev),merging back only on Phase 5 QA pass。Phase 0-2 stays in main(docs-only,no code/schema change)。

> ⭐ **rev 1.17.2 amendment(2026-06-23 PO 拍板 Q-B Yes):** Switched from same-dir `git checkout -b` to **filesystem-isolated `git worktree add`** with **folder name = project name**。**Rationale:** Same-dir branch switching has wrong-branch commit risk + can't have multiple projects active simultaneously。`git worktree add ../<project> dev/<project>` creates `~/<project>/` adjacent to main repo,physically isolating WIP from main checkout。Filesystem layout becomes: `~/<repo>/` (main) + `~/<project-A>/` (worktree A) + `~/<project-B>/` (worktree B) — each project gets its own working directory with full frontend + backend codebase。

```yaml
command: /pm setup-worktree
trigger: Phase 2 → Phase 3 transition(auto by /pm advance-phase 3)
input:
  project: <active project from state.md>
  team_size: <int>                  # 5 typical (solo PO carve-out: still creates worktree for consistency)
output:
  branch_created: dev/<project>
  worktree_path: ../<project>       # rev 1.17.2 — filesystem dir adjacent to main repo
  team_roster_announced: docs/pm/team-roster.md
behavior:
  - cd <main repo dir>
  - git checkout main && git pull origin main
  - verify ../<project>/ does NOT exist (else abort + prompt manual cleanup)
  - git worktree add ../<project> -b dev/<project>     # rev 1.17.2 — was `git checkout -b`
  - cd ../<project> && git push -u origin dev/<project>
  - update docs/pm/state.md (in main repo): `worktree_branch: dev/<project>` + `worktree_path: ../<project>` + `phase_3_started_at: <date>`
  - append docs/decision-log.md (in main repo): D-pm-<id>: Phase 3 開始,team worktree=dev/<project> @ ../<project>/ (shared infra + module dev 全 isolation)
  - echo onboarding hint: "Switch CWD to ../<project>/ for Phase 3+4 development. Return to main repo for /pm status / /pm advance-phase 5."
confidence_tier: 🟢 high(git plumbing only,無 schema risk)

solo_PO_carve_out:
  applies_when: team_size == 1 AND PO authorized via `/pm init --solo`
  behavior: worktree creation OPTIONAL but RECOMMENDED for consistency
  rationale: |
    Solo project 通常自己管 main,worktree overhead 可省。但若 project 有 risk
    of being abandoned mid-way,建議仍 worktree 隔離 — main 保留 always-deployable
    invariant 是 cross-project value(對齊 PO 2026-06-23 mental model)。

grandfather_carve_out:                 # rev 1.17.2 — for existing projects already in main
  applies_when: project already has Phase 3+ commits in main pre-rev-1.17
  behavior: NO retrofit;continue on main per pre-rev-1.17 contract;document in state.md `migration_policy: grandfather`
  rationale: |
    Retrofitting requires git reset --hard + force-push main = destructive +
    breaks Azure deploy chain(deploy 來源=main per memory project_v2_backend_integration)。
    Cost > 0 benefit(已 done work 無 WIP isolation 需求)。
    Future projects default rev 1.17.2 pattern。
  examples:
    - backend-schema-auto-sync (Phase 3+4 done in main 2026-06-22,partial grandfather 2026-06-23)

  partial_grandfather_subcase:         # ⭐ rev 1.17.2 PO 2026-06-23 challenge — Phase 5+ 仍需 worktree-isolated
    applies_when: project under grandfather AND has remaining phases (Phase 5+) with potential code changes
    behavior: |
      Forward-looking worktree NOW at current main HEAD — non-destructive:
      ```bash
      cd <main repo dir>
      git worktree add ../<project> -b dev/<project>
      git push -u origin dev/<project>
      ```
      Phase 5+ commits route to worktree;Phase 6 merge dev/<project> → main → Azure deploy。
      Phase 3+4 historical commits stay in main(not retrofitted)。
    rationale: |
      Full grandfather is over-conservative — Phase 5 QA hotfix / Phase 7 critical bug fix
      would otherwise pollute main(違反 main always-deployable invariant)。
      Partial grandfather:
        Phase 3+4 in main(grandfathered — done work,destructive cost > benefit)
        Phase 5+ in worktree(forward-isolated — protects main invariant)
      Zero destructive risk;cost ~3 min(git worktree add + push + state.md update)。
    state_md_fields:
      migration_policy: partial_grandfather
      worktree_branch: dev/<project>
      worktree_path: ../<project>
      worktree_built_at: <ISO timestamp>
      worktree_built_at_commit: <main HEAD sha>
      worktree_forward_scope: "Phase N+ commits route to worktree"
    examples:
      - backend-schema-auto-sync (built 2026-06-23T13:30 at main HEAD a218711,Phase 5+ forward-isolated)
```

**E.8.3 `/pm daily-sync` — engineer 每天 morning routine:**

```yaml
command: /pm daily-sync
trigger: engineer manual(建議每天 morning 跑;CI 不跑)
input:
  worktree_branch: <from state.md>
output:
  sync_result: clean | conflict_resolved | conflict_pending
  conflicts: []                     # 若有,列 file path
behavior:
  - git fetch origin <worktree_branch>
  - git pull --rebase(default;對齊 §10.7 衝突解快 norm)
  - 若 conflict:
      • SKILL 偵測 conflict markers
      • 列衝突 file + 提示 user resolve
      • resolve 完跑 git add + git rebase --continue
      • 超過 24h 未解 → SKILL 每次 invoke 提示 escalate(對齊 §10.7)
audit:
  - append-only ~/.cache/pm-skill/daily-sync.log(per-engineer,not committed)
confidence_tier: 🟡 medium(conflict 解需 engineer 判斷,SKILL 引導但不代決)
```

**E.8.4 `/pm push-gate` — 「告一段落 + 會動」驗證(復用 §E.3a 6 條 invariant):**

```yaml
command: /pm push-gate
trigger: engineer pre-push(建議綁 git pre-push hook;也可手動)
input:
  module: <inferred from changed files>
output:
  gate_verdict: pass | fail
  failed_checks: []
behavior:
  - 跑 §E.3a 6 條 invariant check 的子集(per-module scope):
      ✅ every_feature_has_code_commit(本次 push 的 feature_id)
      ✅ every_feature_has_test_case(本次涉及的 feature)
      ✅ every_test_case_has_result(unit test 必跑 + pass)
      ✅ execution_log_per_done_feature
      ✅ actual_completion_filled(若 status changed to done)
      ✅ no_stale_functional_md(本 push 範圍)
  - 加 push-gate 專屬補充 check:
      ✅ lint_pass: ruff F821/F + mypy 不增 baseline(對齊 memory: backend_lint_workflow)
      ✅ no_uncommitted_changes: git status clean
      ✅ functional_md_updated: 若有 feature status 變更必 commit functional.md
  - 任一 fail → 拒 push,列 fix 建議
  - 全 pass → allow push to dev/<project>
audit:
  - append docs/pm/reports/<date>-daily.md push-gate result(per push)
confidence_tier: 🟢 high(機械化 check,對齊 Stage Gate 機械化 §6.5)
```

**E.8.5 git pre-push hook 範例(對齊 §E.8.4 自動化):**

```bash
#!/bin/bash
# .git/hooks/pre-push — auto-installed by /pm setup-worktree
remote="$1"
url="$2"
while read local_ref local_sha remote_ref remote_sha; do
  if [[ "$remote_ref" == "refs/heads/dev/"* ]]; then
    claude /pm push-gate || {
      echo "❌ push-gate failed. 若確定要 bypass(eg. emergency hotfix),用 git push --no-verify"
      exit 1
    }
  fi
done
```

> **注意:** `--no-verify` bypass 對齊 memory: backend_lint_workflow「除非 PO 明示,否則不可 skip hook」原則 — 此處 hook 預設執行,bypass 必 engineer 主動加 flag。

**E.8.6 Phase 4 → Phase 5 Transition(對齊 §F.6 enhancement):**

當 `/pm validate-implementation --all` pass + PO 拍板 `/pm advance-phase 5` →
- SKILL 自動 merge dev/<project> → main(對齊「project 開發完成驗證成功回 main」)
- 詳細 workflow 見 §F.6

**E.8.7 Confidence Tier Summary(對齊 SKILL.md §Auto Behavior):**

| 命令 | Tier | 理由 |
|:---|:---:|:---|
| `/pm setup-worktree` | 🟢 high | git plumbing,deterministic |
| `/pm daily-sync` | 🟡 medium | conflict 解靠 engineer |
| `/pm push-gate` | 🟢 high | 6+3 條 invariant 機械化 |
| `/pm use mainline` | 🟡 medium | --reason mandatory + audit + idle timeout(rev 1.17.3) |
| `/pm whereami` | 🟢 high | read-only display(rev 1.17.3) |

**E.8.8 Worktree-Default Invariant + Mainline-as-Project(rev 1.17.3 — 2026-06-23 PO insight):**

> ⭐ **PO 2026-06-23 insight:** 把 mainline 變成 special "project" 自己 — routing 全靠 `active-project.txt`。Emergency hotfix 不需要 special override mechanism,只需 `/pm use mainline --reason "..."`。Discipline framework 從「explicit override + escape valve」轉變成「uniform model + natural audit via project switching」。

> 📌 **rev 1.17.5(2026-06-23)canonical path alignment:** `active-project.txt` 的 canonical 位置是 **`docs/pm/active-project.txt`**(top-level under `docs/pm/`),**NOT** `docs/pm/_org/active-project.txt`。**Rationale:** physical reality alignment(file 一直在 top-level)+ git history continuity + lower discoverability cost(`ls docs/pm/` 直接看到)。`_org/` 仍為 ORG-level shared artifacts(`org-decision-log.md` / `org-roster.md` / `contract-pack/` / `specs/` etc.)namespace,active-project.txt 不歸屬 ORG namespace 而是 PM Skill root pointer。Pre-rev-1.17.5 文件用 `_org/active-project.txt` 寫法為 spec ↔ impl drift(已在 rev 1.17.5 sed sweep fix 5 個 LIVE files / 16 refs)。Historical review logs + decision-log audit entries 保留原 path 寫法不動(audit trail integrity)。

**E.8.8.1 Core Invariant(refined per PO):**

```
Active project resolves to commit target as follows:
  active = <project>:
    IF dev/<project> branch EXISTS on GitHub origin:
       → submit to worktree at ../<project>/, branch dev/<project>
    ELSE:
       → submit to mainline (main repo, branch main)
  active = mainline (reserved):
       → submit to mainline (main repo, branch main)
```

**Side effects (auto-emergent properties):**

1. **Backwards-compat自然成立** — Pre-rev-1.17 projects(沒 worktree on GitHub)→ routes to mainline。No `migration_policy` flag needed。
2. **Forward consistency** — Rev 1.17+ projects /pm setup-worktree creates branch on GitHub → routes to worktree automatically。
3. **GitHub branch existence IS the source of truth** — 不需 local-only branch / 不需 explicit flag。Engineer 切 project 跑 normal git push,routing 由 PM Skill 讀 `git ls-remote origin dev/<project>` 判定。

**E.8.8.2 Mainline as Special Reserved Project:**

```yaml
mainline:
  type: system_special               # 區別 normal project category
  status: perpetual_maintenance      # 永遠 active,不 close 不 archive
  branch: main
  worktree: null                     # operates on main repo directly
  phase_lifecycle: N/A               # no Phase 0-7
  reserved_name: true                # /pm init mainline → ABORT (reserved)

mainline_specific_metrics:           # replaces phase_<N>_signoff fields
  last_release:
    project: <last project archived>
    released_at: <ISO>
    merged_to_main_at: <ISO>
  active_duration_this_month: <minutes>
  commits_to_mainline_this_month: <count>
  last_switched_to: <ISO>
  last_switched_back_from: <ISO>
  override_alarm_level: green | yellow | red

allowed_commands:                    # mainline-specific
  - /pm status mainline              # shows mainline metrics
  - /pm use mainline --reason "..."  # switch active (--reason mandatory)
  - /pm whereami                     # show current state
  - /pm push-gate                    # commits on main
  - /pm deploy                       # direct main deploy
  - /pm validate-discipline-invariant  # mainline-specific (override frequency)

forbidden_commands:                  # 抛 clear error 「mainline has no phase lifecycle」
  - /pm init mainline                # reserved name
  - /pm advance-phase <N>            # no phases
  - /pm signoff phase-<N>            # no phases
  - /pm gate-check phase-<N>         # no phases
  - /pm setup-worktree               # mainline IS main
  - /pm rollback <N>                 # no phases
  - /pm archive                      # never closes
  - /pm restore                      # never archived
```

**E.8.8.3 Project Close → Auto-switch to Mainline:**

```yaml
on_archive_project:
  trigger: /pm archive <project>
  workflow:
    1. archive project (existing §6.4.10 §I.1 behavior)
    2. AUTO update active-project.txt → "mainline"
    3. echo:
       "Project <project> archived. Active project switched to mainline.
        You're now on main branch (CWD: <main repo dir>).
        Worktree dir ../<project>/ cleanup pending (run `git worktree prune`)."
    4. audit: D-pm-archive-<id> + D-pm-switch-to-mainline-auto-<id>
```

**E.8.8.4 `/pm use mainline` Mandatory --reason + Audit:**

```yaml
command: /pm use mainline --reason "<text>"
preconditions:
  - reason: required (≥ 30 chars,對齊 §K.8 audit minimum)
  - confirmation: explicit (不 require BYPASS phrase per uniform model — switching IS the audit)
behavior:
  - update active-project.txt → "mainline"
  - log to docs/pm/mainline/state.md recent_switches[]
  - audit entry: D-pm-switch-to-mainline-<id>: from=<previous-project> reason="<text>" duration_pending=true
  - echo onboarding:
    ⚠ Switching to mainline (= main branch direct ops)
    Reason: <text>
    All commits land on main branch directly.
    Switch back: /pm use <previous-project>
    Idle threshold: 60 min (PM Skill will prompt)
confidence_tier: 🟡 medium (--reason audit + idle timeout)
```

**E.8.8.5 Visual Warning + Idle Timeout(對齊 Refinement 4):**

```
On /pm status when active=mainline:

  ⚠⚠ ACTIVE: mainline
      All commits go to main branch directly.
      Time active as mainline: <duration>
      Idle threshold: 60 min (will prompt to switch back)
      Switch back: /pm use <last-project>

If active=mainline > 60 min without commit:
  ⚠ You've been on mainline for <duration> without commits.
     Still need mainline ops? Run /pm use mainline --extend.
     Else switch back: /pm use <last-project>.
```

**E.8.8.6 Push-gate Check 10 — Active-project Alignment(對齊 Refinement 5):**

```yaml
check_10_active_project_alignment:
  read: active-project.txt
  if active_project == "mainline":
    expect_branch: main
    expect_cwd: <main repo dir from .git of current location>
  else (active_project == <project>):
    if dev/<project> exists on origin:
      expect_branch: dev/<project>
      expect_cwd: ../<project>/
    else:
      expect_branch: main
      expect_cwd: <main repo dir>
  on_mismatch:
    output: |
      ⚠ Active project = <X> but you're committing on <Y> branch.
      Did you forget to switch? `/pm use <expected>` to align.
      Or override: type CONFIRM PUSH MISMATCH to proceed.
```

**E.8.8.7 Deprecate `/pm deploy --hotfix --override-discipline`(對齊 Refinement 6):**

Pre-rev-1.17.3 emergency override mechanism:
```bash
/pm deploy --hotfix --override-discipline --reason "..."    # ⚠ deprecated
```

Replaced by uniform model:
```bash
/pm use mainline --reason "..."
# ... edit + commit + push as normal ...
/pm deploy
/pm use <previous-project>    # switch back
```

**Migration period:** 3 months(2026-06-23 → 2026-09-23)— both mechanisms work; warning emitted when `--override-discipline` used; after 2026-09-23 only mainline-switch works。§K.8 + §K.9 amended:override frequency tracker becomes **mainline cumulative duration tracker**(< 30 min/month green / 30-120 min/month yellow / 120+ min/month red + policy freeze)。

**E.8.8.8 `/pm whereami` v1.4 New Command(對齊 Refinement 6 + edge case mitigation):**

```yaml
command: /pm whereami
output:
  📍 Active project: <project> (since <duration> ago, via /pm use)
  📂 Expected CWD:  <expected path>
  📂 Your CWD:      <pwd>
  ✅ Aligned   OR   ⚠ MISMATCH (suggest `cd <expected>`)
confidence_tier: 🟢 high (read-only display)
```

**E.8.8.9 org-decision-log.md 自然解掉(對齊 Refinement 7):**

org-decision-log 屬於 mainline project's domain。所有 audit logging(switching events / cross-project decisions / mainline metrics)寫到 mainline's location → 在 main 上 → 自然 cross-project visible。**No carve-out needed**。Pre-rev-1.17.3 既有的 `docs/pm/_org/org-decision-log.md` 維持原 path,只是現在 conceptually "owned by mainline project"。

**E.8.8.10 Confidence Tier 補充:**

| Action | Tier | 理由 |
|:---|:---:|:---|
| `/pm use mainline --reason "..."` | 🟡 medium | --reason mandatory + audit + idle timeout |
| `/pm use <project>` (switch back) | 🟢 high | low-friction,read-only routing |
| `/pm whereami` | 🟢 high | read-only display |
| auto-switch on /pm archive | 🟢 high | deterministic transition |
| push-gate check 10 | 🟢 high | active-project alignment is machine check |

##### F. Phase 5 — Integration Test Artifact Contract

**Artifacts:**
- `docs/integration/<date>-e2e-test-results.md` — E2E 結果(對齊 R-XX case 對照)
- `docs/integration/<date>-perf-test-results.md` — 效能基準
- `docs/pm/reports/<date>-phase-5-integration.md` — 階段總結
- `docs/reviews/<date>-V3-integration-review.md`

**Contract Version:** `integration-test-contract-v1`

**F.1 E2E Test Results Schema:**

```yaml
e2e_test_results:
  test_environment: integration | staging
  test_date: <YYYY-MM-DD>
  test_runner: <human or CI>
  rxx_cases:
    - case_id: R-01
      scenario: <description>
      status: pass | fail | skip
      device: <real device model>  # 對齊 memory: real-device testing
      notes: <if fail/skip>
  pass_rate: <%>
  blockers: []                     # 阻擋 release 的 issue
```

**F.2 Perf Test Schema:**

```yaml
perf_test_results:
  baseline_aligned_to: "Requirement Spec / SLA section"
  metrics:
    - name: api_p95_latency
      threshold: 500ms
      observed: 320ms
      status: ✅ pass
    - name: friend_search_response
      threshold: 1s
      observed: 1.2s
      status: ❌ fail
  overall_verdict: pass | fail
```

**F.3 Exit Criteria:**

```yaml
quality_bar:
  e2e_pass_rate: 100%             # R-XX 全綠
  perf_all_metrics_pass: true     # 全 SLA 達標
  no_merge_conflict: true
  cross_module_interaction_tested: true
  v3_integration_review_passed: true
  
  # ⭐ rev 1.8 新增 — Staging Migration Applied + Verified(對齊 §G.6.0)
  staging_migrations_applied_and_verified: true
    # 條件:
    # - migration-state.md 顯示 staging env 所有 pending migrations 已 applied
    # - 每 migration 的 verify_sql 在 staging 跑通
    # - integration E2E + perf 在 post-migration staging schema 上跑(不是 mock schema)
  
  # ⭐ rev 1.17.6 新增 — Post-Merge Regression Check(PO 2026-06-23 insight)
  post_merge_regression_check_pass: true
    # 條件:
    # - integration test suite re-run on merged main HEAD 100% pass
    # - same env as Phase 5 execution (per state.md.phase_5_staging_strategy — Path A local OR Path B Azure staging)
    # - catches: (1) semantic merge conflict resolution correctness
    #            (2) main divergence indirect impact on project code
    #            (3) atomic merge "git auto-merge ≠ semantic correctness" gap
    # - rationale: worktree test pass ≠ merged main test pass
    #              spec §F.3 "no_merge_conflict: true" 只 verify pre-merge worktree state,
    #              NOT post-merge mainline state — rev 1.17.6 closes this gap
  
  # ⭐ rev 1.17.9 新增 — Mainline Pre-Deploy Sanity Check (Progressive Widening Layer 4, PO 2026-06-23 catch #3)
  phase_6_pre_deploy_sanity_check_pass: true
    # Layer 4 — "mainline pre-deploy functional sanity check"(precise: AFTER all Phase 6 build queue
    # items merged to mainline AND BEFORE /pm deploy --target prod):
    # 
    # Critical principle: cumulative integration check
    #   - Each F# build's Layer 2 + Layer 3 pass individually
    #   - BUT cumulative mainline (all F# integrated) may have interaction bugs
    #   - Per rev 1.17.6 principle: "individual pass ≠ cumulative pass"
    # 
    # Mechanism: 
    #   - PO toggles local_build.Const_Run_in_local_environment = True
    #   - Local backend builds from mainline HEAD (git pull + restart gunicorn)
    #   - PO opens LIFF /sanity_test_runner page on real device(via ngrok)
    #   - Pilot v0 page auto-executes test cases (functional sanity = "does function work")
    #   - PO + Claude analyze result.json + backend log
    # 
    # Pass criteria:
    #   - All test cases status ∈ {PASS, AUTH_OK, CMD_REJECTED}
    #   - 0 real_5xx_bug
    #   - Time-box ≤ 30 min single session per memory [[user_working_style]]
    # 
    # Staleness: executed_against_commit must match current main HEAD at deploy time;
    #            if main commits since last sanity check → re-run required.
    # 
    # Carve-out: doc-only / config-only deploys may carve-out per backend_change_rule spirit.

  # ⭐ rev 1.17.7 新增 — Mainline Build Sanity Check (Progressive Widening Layer 3, PO 2026-06-23 catch #2)
  mainline_build_sanity_check_pass: true
    # Progressive Widening pattern (rev 1.17.6 + 1.17.7 consolidate):
    #   Layer 1: project worktree test (Phase 5 final)
    #   Layer 2: project integration test on merged main (rev 1.17.6 §F.6 Step 5.5)
    #   Layer 3: mainline build sanity test on merged main (rev 1.17.7 §F.6 Step 5.7) ⬅ NEW
    #   Layer 4 (rev 1.17.7 original, vague): staging E2E on Path B Azure (future Standard SKU)
    #   Layer 4 (rev 1.17.9 redefined, concrete): mainline pre-deploy sanity check via Pilot v0 LIFF test runner
    #   Layer 5 (rev 1.17.9 renumber): staging E2E (was Layer 4 in rev 1.17.7)
    # Sub-layers (Layer 3 itself stratified):
    #   3a: py_compile <project critical files>  [zero-risk, always run, project-defined list]
    #   3b: import project modules with safe-mode env (e.g. SCHEMA_SYNC_MODE=disabled)  [low-risk]
    #   3c: full gunicorn cold start  [requires deployment env vars OR project carve-out]
    #   3d: /health smoke (per project state.md.D2_health_check.backend_endpoint)  [depends on 3c]
    # Coverage interpretation:
    #   - 3a + 3b PASS → enough for Phase 6 deploy gate unblock (proves no Phase 5/6 regression)
    #   - 3c + 3d blocked-by-env (project's pre-existing local env limit) → log finding, mark partial coverage,
    #     spec accepts this — Path A local has natural ceiling, Path B staging needed for full verify
    #   - 3c FAIL with regression-shape stack trace (syntax / import / new None-handling) → REAL regression
    # Distinguishing "blocked-by-env" vs "real regression" in 3c is PO/PM judgment via stack trace inspection.
    # catches: (4) side-channel impact on OTHER features (not just project's own changes)
    #          (5) deployment env-dep surfaces (local ceiling acknowledgment)
```

**F.4 Validator:** `/pm validate-integration`

**F.5 Phase 5 Exit Check List:**

- [ ] 全 module branch 已 merge 至 integration(無 conflict)
- [ ] **Staging migrations 全 applied + verified(對齊 §G.6.0)** ⭐ rev 1.8
- [ ] E2E R-XX 真機驗測 100% pass(在 post-migration staging schema 上,**不是 mock schema**)⭐ rev 1.8
- [ ] **Post-merge regression check pass** — integration tests re-run on merged main HEAD 100% pass(對齊 rev 1.17.6 §F.6 Step 5.5 + memory `feedback_phase_5_to_6_progressive_widening_verification` Layer 2)⭐ rev 1.17.6
- [ ] **Mainline build sanity check pass** — Layer 3 sub-layers 3a + 3b PASS at minimum;3c + 3d 若 blocked-by-env(project pre-existing local limit)log finding + mark partial coverage,Path A 視為通過(若 3a+3b 都過);3c FAIL with regression-shape stack trace = REAL regression → abort(對齊 rev 1.17.7 §F.6 Step 5.7 + memory Layer 3)⭐ rev 1.17.7
- [ ] **Mainline pre-deploy sanity check pass**(rev 1.17.9 NEW)— AFTER all Phase 6 build queue items merged to mainline AND BEFORE `/pm deploy --target prod`,local backend running mainline HEAD,PO 用 real device via ngrok 跑 Pilot v0 sanity_test_runner LIFF page;all test cases status ∈ {PASS, AUTH_OK, CMD_REJECTED} + 0 real_5xx_bug;executed_against_commit matches deploy commit(staleness check);on fail block `/pm deploy` until fix lands + re-run。Carve-out allowed for doc-only / config-only deploys per `backend_change_rule` spirit(對齊 rev 1.17.9 §F.6 Step 6.5 + memory Layer 4)⭐ rev 1.17.9
- [ ] Perf 全 SLA 達標(對齊 Requirement Spec SLA)
- [ ] PM 健康檢查整合層無 anomaly
- [ ] PM 跟老闆 walkthrough 簽核 state.md `phase_5_signoff = true`

**F.6 `/pm advance-phase 5` Enhancement(v1.2 Planned — worktree → main auto-merge)**

> 對齊 PO 2026-06-18 拍板「project 開發完成驗證成功回 main line」。原 `/pm advance-phase N` 只切 phase state,本 enhancement 在 N=5 時加 worktree merge workflow。

> ⭐ **rev 1.17.3 clarification(對齊 PO EC1=No interpretation)**:Phase 5 advance-phase 5 的 worktree → main merge 是 **single atomic supervised event,not a manual main commit**(對齊 §E.8.8.1 routing rule)。Engineer 看 active=<project>, routing→worktree;但 `/pm advance-phase 5` 命令本身是 PM Skill 主導的 merge transaction,藉由 §F.6 yaml 定義的 deterministic 步驟 atomic merge。這 maintain main always-deployable invariant(merge 成功才落 main,失敗 abort),also keeps deploy chain unbroken(Phase 6 deploy reads merged main per memory `project_v2_backend_integration`)。Phase 5+6+7 期間 ADDITIONAL hotfix commits 仍走 worktree。Project close(`/pm archive`)後 worktree dir + branch 全 cleanup。

```yaml
command: /pm advance-phase 5
preconditions:
  - phase_4_signoff: false           # 尚未 sign off
  - validate-implementation --all: pass
  - worktree_branch: dev/<project>  # 對齊 §E.8.1
  - po_explicit_invoke: true         # PO 親自跑,SKILL 不自動觸發(對齊 §6.4.4 trust hierarchy)
behavior:
  1. SKILL 顯示 readiness summary:
     - 全 module functional.md status: ✅ done count
     - 全 test-results pass rate
     - 三向 invariant verdict
     - PO confirm「是否 merge dev/<project> → main」(y/N)
  2. PO confirm 後:
     - cd <main repo dir>             # rev 1.17.2 — must run from main repo, NOT from ../<project>/ worktree
     - git checkout main && git pull origin main
     - git merge --no-ff dev/<project> -m "Phase 4 → 5: merge dev/<project>"
     - 若 conflict → abort (git merge --abort) + 列衝突 + 提示 engineer 回 ../<project>/ worktree 解完再來
     - merge 成功 → git push origin main
  3. 自動觸發 §F.4 `/pm validate-integration`(進入 Phase 5 QA)
  4. update docs/pm/state.md:
     - phase_4_signoff: true
     - current_phase: 5
     - main_merged_from: dev/<project>
     - phase_5_started_at: <date>
  5. append docs/decision-log.md: D-pm-<id>: Phase 4 → 5 transition + merge result
worktree_lifecycle:
  - dev/<project> branch NOT deleted at this stage(留作 Phase 5 期間若需 hotfix patch back)
  - ../<project>/ worktree dir NOT removed at this stage(rev 1.17.2 — same reason)
  - 待 Phase 6 release success 才由 `/pm archive` 連帶清理(git worktree remove ../<project> + git branch -D dev/<project>)
confidence_tier: 🟡 medium(merge 可能 conflict,需 engineer 介入;PO 拍板 final)
```

**F.6.1 Phase 5 期間 hotfix policy(對齊 worktree 留存):**

若 Phase 5 QA 抓到 bug 需 patch:
- **Option A**(推薦):patch 在 dev/<project>,跑 push-gate → cherry-pick to main
- **Option B**:急件直接 patch main(需 PO ack + 額外 audit)

##### G. Phase 6 — Release Artifact Contract

**Artifacts:**
- `docs/release/<date>-deploy-log.md`
- `docs/release/<date>-smoke-test-results.md`(prod env)
- `docs/release/<date>-rollback-plan.md`(已 test 過)
- Monitoring dashboard URLs + alert config
- Stakeholder announce 紀錄
- `docs/pm/reports/<date>-phase-6-release.md`

**Contract Version:** `release-contract-v1`

**G.1 Deploy Log Schema:**

```yaml
deploy_log:
  date: <YYYY-MM-DD HH:MM:SS+TZ>
  version: <git tag>
  commit_hash: <sha>
  deployer: <name>
  environment: production
  azure_webapp_runtime: "Microsoft Azure Linux 3.0"  # 對齊 memory: azure_webapp_runtime
  duration_sec: <N>
  result: success | partial | failed
  pre_deploy_smoke: passed | failed
  post_deploy_smoke: passed | failed
  rollback_triggered: false
```

**G.2 Rollback Plan 必含:**

- 觸發條件(eg. p95 > 2s / error rate > 5%)
- 回退步驟(具體 command)
- 已 rehearsed = true(rehearsal 過 1 次)
- rehearsal date + result

**G.3 Exit Criteria:**

```yaml
quality_bar:
  prod_deploy_success: true
  smoke_test_all_pass: true       # prod env
  rollback_plan_rehearsed: true   # ⚠ 不可只 documented,必 rehearse
  monitoring_active: true         # metrics + alerts 已上線
  stakeholder_announced: true
```

**G.4 Validator:** `/pm validate-release`

**G.5 Phase 6 Exit Check List:**

- [ ] Production deploy 成功(Azure Webapp,Linux 3.0 對齊 memory)
- [ ] Smoke tests prod env 全 pass
- [ ] Rollback plan rehearsed + result documented
- [ ] Monitoring + alerts 已上線可運作
- [ ] Stakeholder announce 完成
- [ ] PM 簽核 state.md `phase_6_signoff = true`

**G.6 v1.2 Schema Migration + Deploy Commands(對齊 PO 2026-06-18 拍板)**

> 對齊 PO 拍板「main 通過 quality check + PM 同意品質後下指令 deploy to Azure」+ Cluster A「PM Skill 須 aware DB migration 並 run migration first」。本子段定義 **Migration Gate**(§G.6.0)+ **Deploy 命令**(§G.6.1-2)+ 相關 lifecycle。

**G.6.0 Migration Gate(v1.2 Planned — PM Skill schema-aware design)** ⭐ rev 1.8 新增

> 對齊 memory `backend_schema_change_workflow`:SSOT=`laundry_db_create_tables.sql`,PO 自 apply migration,propose 必含 *.py + sql diff + ALTER TABLE 3 樣。

**G.6.0.1 Awareness Mechanism — SSOT file hash + Migration Manifest(Option A)**

PM Skill 透過 3 個 artifact tracking schema state:

```
project_root/
├── laundry_db_create_tables.sql           ← SSOT(memory:既有)
├── docs/migrations/
│   ├── manifest.yaml                       ← 全 migration index(per-project)
│   └── <YYYY-MM-DD>-<NNN>-<slug>.sql      ← per-migration script
└── docs/pm/<project>/migration-state.md    ← per-env applied state(per-project)
```

**G.6.0.2 `manifest.yaml` Schema(對齊 memory: ALTER TABLE 3 樣)**

```yaml
schema_ssot: laundry_db_create_tables.sql
contract_version: migration-manifest-v1
project: <active project>

migrations:
  - id: "001"                              # 流水號 zero-padded
    date: 2026-06-01
    feature_id: F-friend-identity-001       # 對齊 §C.2 functional.md feature
    file: 2026-06-01-001-add-friend-bizcard.sql
    
    # 對齊 memory: ALTER TABLE 3 樣
    forward_sql: |
      ALTER TABLE Friend_Bizcard ADD COLUMN profile_create_datetime TIMESTAMP NULL;
    backward_sql: |
      ALTER TABLE Friend_Bizcard DROP COLUMN profile_create_datetime;
    verify_sql: |
      SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
      WHERE TABLE_NAME='Friend_Bizcard' AND COLUMN_NAME='profile_create_datetime';
    
    rollback_safe: true                     # 無損 rollback
    expected_apply_duration_sec: 3
    
    review_required:
      - feature_spec_marked_schema_change: true   # 對齊 §C.2a
      - po_propose_acknowledged: true              # 對齊 memory: backend_change_rule
    
    # ⭐ rev 1.10.2 新增(對齊 spectra v1.1.8 Round 1 C3 fix — SKILL impl schema drift 收回)
    ssot_pending: false                     # default false;true = PO reject SSOT auto-update
                                            # `/pm migration-propose` Step 7 若 PO confirm
                                            #   → ssot_pending=false + 立刻 update SSOT
                                            # 若 PO defer SSOT update(罕)
                                            #   → ssot_pending=true,Phase 3 Exit gate 拒絕(對齊 §D.2)
```

**G.6.0.3 `migration-state.md` Schema(per-project per-env tracker)**

```yaml
---
project: <name>
schema_ssot_hash_current: <sha256 of laundry_db_create_tables.sql>
last_updated: 2026-06-18
---

# Migration Apply Status

| Migration | dev | staging | prod | Applied by |
|:---:|:---:|:---:|:---:|:---|
| 001 | ✅ 2026-06-01 | ✅ 2026-06-02 | ✅ 2026-06-03 | PO |
| 002 | ✅ 2026-06-05 | ✅ 2026-06-06 | ⏳ pending | — |

## SSOT Sync State

- dev: hash matches SSOT current ✅
- staging: hash matches SSOT current ✅
- prod: hash STALE(missing migration 002)⚠

## Next Action

- PO apply migration 002 to prod before `/pm deploy --target prod`
```

**G.6.0.4 `/pm migration-status`(read-only dashboard)**

```yaml
command: /pm migration-status
trigger: PO manual or auto by /pm daily
behavior:
  - read manifest.yaml + migration-state.md
  - print visual matrix(dev/staging/prod × migration)
  - highlight pending entries
  - print SSOT hash sync state per env
output: stdout only;若 pending count > 0,prompt 提示 next action
confidence_tier: 🟢 high(read-only)
```

**G.6.0.5 `/pm migration-propose <feature-id>`(對齊 memory propose 規約)**

```yaml
command: /pm migration-propose <feature-id>
trigger:
  - auto by /v2 done <feature> 若 functional.md `schema_change: true`
  - 或 PO manual(對應 backend_change_rule propose stage)
behavior:
  1. SKILL prompt PO 填(對齊 memory: ALTER TABLE 3 樣):
     - forward_sql
     - backward_sql(rollback)
     - verify_sql
     - rollback_safe(bool)
     - expected_apply_duration_sec
  2. SKILL gen migration .sql file:
     - 命名:docs/migrations/<YYYY-MM-DD>-<NNN>-<slug>.sql
     - 自動 sequence NNN(對齊既有 manifest)
  3. SKILL update manifest.yaml(append migration entry)
  4. SKILL update laundry_db_create_tables.sql(SSOT)若 PO confirm
  5. SKILL update functional.md feature:
     - schema_change: true
     - migration_id: "<NNN>"
  6. SKILL append docs/decision-log.md:
     D-pm-<id>: Schema migration <NNN> proposed for <feature>
audit:
  - SQL semantic SKILL 不 validate(memory rule: PO 必審)
  - SKILL 只負責 structural well-formedness + file plumbing
confidence_tier: 🟡 medium(SQL 語意 PO 必審)
```

**G.6.0.6 `/pm migration-apply --env <dev|staging|prod>`**

```yaml
command: /pm migration-apply --env <env>
trigger: PO manual
preconditions:
  - manifest.yaml valid
  - env in [dev, staging]:phase_5_signoff 不必 true(整合期可跑)
  - env == prod:phase_5_signoff = true(必先過整合 QA)

behavior:
  IF env in [dev, staging]:
    1. SKILL 列 pending migrations for env
    2. PO confirm(y/N)
    3. SKILL 跑 mysql/psql CLI auto-apply(連線用既有 dev/staging DB credentials)
    4. 每 migration apply 後跑 verify_sql 驗結果
    5. update migration-state.md applied entry
    6. append decision-log: D-pm-<id>: Migration <NNN> applied to <env> by SKILL (auto)
  
  IF env == prod:
    1. SKILL 列 pending migrations for prod + 印 forward_sql(可複製)
    2. SKILL 印 reminder:
       「⚠ 對齊 memory: backend_schema_change_workflow,
        prod migration 必 PO 自 apply。
        Apply 完跑 /pm migration-mark-applied --env prod --version <NNN>」
    3. NOT auto-execute(對齊 memory rule)
    4. 退出,等 PO mark-applied

audit:
  - dev/staging auto-apply log → migration-state.md + decision-log
  - prod path:無 auto action 紀錄,等 mark-applied 才寫

confidence_tier:
  - dev/staging: 🟡 medium(auto execute)
  - prod: 🔴 low(SKILL print only,PO 拍板)
```

**G.6.0.7 `/pm migration-mark-applied --env prod --version <NNN>`(prod-specific)**

```yaml
command: /pm migration-mark-applied --env prod --version <NNN>
trigger: PO manual,after PO 自 apply prod migration
input:
  --env: prod(只接受 prod;dev/staging auto-applied 不需 mark)
  --version: <NNN>
  --reason: optional(eg. "PO applied via Azure Portal Cloud Shell")

behavior:
  1. SKILL 跑 verify_sql 連 prod read-only check
     IF prod DB connection available(read-only credential 已設):
       SKILL 自驗 verify_sql result
     IF NOT available:
       SKILL prompt PO 自填 verify result(eg. "rows: 1")
  
  2. update migration-state.md:
     - mark <NNN> applied=true for prod
     - update last_updated timestamp
     - update SSOT hash sync state for prod
  
  3. append decision-log:
     D-pm-<id>: Migration <NNN> applied to prod by PO @ <timestamp>,
     verify_sql result: <output>

audit:
  - PO confirmation 整段對話記入 decision-log
  - 無 prod DB credentials 時 prompt PO 自填是 documented gap
  - 對齊 memory: PO 自 apply migration(SKILL 只 mark,不 execute)

confidence_tier: 🔴 low(PO 拍板 + audit-mandatory)
```

**G.6.0.8 Migration Lifecycle 跨 Phase 對應**

| Phase | Migration action |
|:---:|:---|
| **Phase 2**(spec)| functional.md feature 標 `schema_change: bool` + `migration_id`(對齊 §C.2)|
| **Phase 3**(shared infra)| /pm migration-propose → manifest.yaml entry + .sql file 生成 → SSOT update(對齊 §D.1)|
| **Phase 4**(implementation)| feature done 時 SKILL verify manifest 跟 spec 對齊 |
| **Phase 5**(integration)| /pm migration-apply --env staging → migration-state.md 寫 staging applied(對齊 §F.3)|
| **Phase 6**(release)| /pm deploy precondition check + /pm migration-mark-applied --env prod(對齊 §G.6.1 加強)|
| **Phase 7**(post-launch)| migration-state.md 保留 audit trail,Phase 7 retro 引用 |

**G.6.0.9 Cross-reference 對齊 memory rule**

| Memory rule | 設計對齊處 |
|:---|:---|
| SSOT = `laundry_db_create_tables.sql` | manifest.yaml `schema_ssot` field |
| 必同步 SSOT | /pm migration-propose step 4 自動 update SSOT |
| propose 必含 *.py + sql diff + ALTER TABLE 3 樣 | manifest entry forward/backward/verify(對齊 3 樣)+ feature_id link |
| PO 自 apply migration | /pm migration-apply prod = print 命令,non-auto;/pm migration-mark-applied 才 mark |
| backend_change_rule | propose stage 對應 /pm migration-propose;PO 拍板 對應 mark-applied |
| dep_management | 用既有 mysql/psql CLI(Azure 已裝),不新 install ORM/driver |
| azure_webapp_runtime | Azure Linux 3.0 native CLI,無 OS 相容性 risk |

**G.6.1 `/pm deploy --target <staging|prod>` — PO 拍板 + Azure CLI execute(SKU-aware,rev 1.10.3 補):**

> **SKU-aware design rationale**(PO 2026-06-18 Option C 拍板):**Basic SKU 沒 deployment slots**,zero-downtime swap 不能跑。設計上 deploy 必須對齊 `azure-config.yaml.web_app.deploy_strategy`:
> - `slot_swap`(Standard+ SKU):pre-deploy → smoke → swap(zero-downtime)
> - `direct`(Basic SKU):ZIP deploy 到 production slot(~30s app restart)+ smoke + auto rollback fallback
> 對齊 memory `user_working_style`(cost-conscious)+ runtime constraint(LineBOT 現用 Basic SKU)。Upgrade path:升 Standard S1 後改 `deploy_strategy: slot_swap` 即恢復 zero-downtime。


```yaml
command: /pm deploy --target prod
trigger: PO manual(SKILL 不自動觸發 — 對齊 §6.4.4 trust hierarchy)
preconditions:
  - phase_5_signoff: true              # Phase 5 QA pass
  - validate-release: pass              # 對齊 §G.4
  - rollback_plan_rehearsed: true      # 對齊 §G.3
  - smoke_test_all_pass: true(staging env if --target prod)
  - po_explicit_confirm: true           # SKILL 提示「型 'DEPLOY' 確認」之類 unambiguous gate
  
  # ⭐ rev 1.8 新增 — Schema Migration Awareness gate(對齊 §G.6.0)
  - schema_migrations_aware: true
    check:
      - migration-state.md exists for project
      - all manifest migrations with target_env=pending count == 0
      - ssot_hash_current == migration-state.md last-applied hash for target env
    on_fail:
      message: "⚠ 阻擋 deploy:有 N 個 migration 未 apply 到 <target>"
      action: |
        print pending migration list +
        提示「先跑 `/pm migration-apply --env <target>`
             (dev/staging auto)或 `/pm migration-mark-applied --env prod --version <NNN>`
             (對齊 memory: PO 自 apply prod migration)」
  
  # ⭐ rev 1.10 新增 — Discipline Invariant Check(對齊 §K No Fast Path Policy)
  - discipline_invariant_check: pass
    auto_trigger: /pm validate-discipline-invariant(對齊 §K.6)
    check:
      - phase 0 → 7 順序無 skip / 無 reorder
      - 每 phase signoff 有 audit trail
      - 無 direct main commit(對齊 §E.8 worktree → main only)
      - 對應 commit 已過 Phase 6 signoff
      - git log no_verify count == 0
    on_fail:
      message: "🚫 紀律 invariant 違反,deploy 阻擋"
      action: |
        列具體違反處 + 引用 §K.4 必走 SDLC range +
        prompt PO: 「若確定 override,跑 `/pm deploy --override-discipline --reason "<≥50 chars>"`
              (對齊 §K.8,罕用,審 audit)」
input:
  --target: staging | prod
  --reason: <string, required>          # PO 必填 deploy reason,對齊 §6.4.4 audit trail
  --dry-run: optional flag              # 跑全 precheck 但不真 deploy(rehearsal 用)
output:
  deploy_log: docs/release/<date>-deploy-log.md(對齊 §G.1 schema)
  azure_slot_state: warmed | swapped | failed
behavior:
  1. SKILL 跑 precondition check 全集合,任一 fail → abort + 列 fix 建議
  2. SKILL 顯示 PO confirmation summary:
     - target env + commit hash + diff summary(main vs last prod tag)
     - rollback rehearsal date
     - 已驗的 e2e/perf SLA
     - PO 必輸入 `--reason "<text>"` + 型 `DEPLOY` 確認
  3. PO confirm 後:
     - git tag release-<YYYYMMDD-HHMM>(對齊 §G.1 version field)
     - Azure CLI:az webapp deployment slot swap --name <app> --slot staging --target-slot production
        • 若 staging slot 不存在:fall back blue-green via az webapp deploy(主 slot 直 deploy + 自動 rollback on failure)
     - 跑 post-deploy smoke test(對齊 §G.1 post_deploy_smoke field)
     - 失敗 → 自動觸發 `/pm rollback`(對齊 §G.6.2)
  4. update docs/pm/state.md:
     - phase_6_signoff: true(若 --target prod 且 smoke pass)
     - last_deploy_at: <timestamp>
     - last_deploy_commit: <sha>
  5. write docs/release/<date>-deploy-log.md(對齊 §G.1 schema)
  6. append docs/decision-log.md: D-pm-<id>: PO 拍板 deploy --target prod, reason: <text>
  7. 提示 PO 跑 `/pm validate-post-launch` 啟動 Phase 7 observation window
audit:
  - PO confirmation 整段對話記入 docs/decision-log.md
  - --reason 是 audit-mandatory field,無 reason refuse deploy
azure_runtime_alignment:
  - 對齊 memory: azure_webapp_runtime — Microsoft Azure Linux 3.0(non-Ubuntu)
  - 對齊 memory: dep_management — requirements.txt 改動必先 PO 同意
confidence_tier: 🔴 low(production-impacting,PO 拍板 final;SKILL 只執行)
```

**G.6.2 `/pm rollback [--to <commit>]` — zero-downtime Azure slot swap-back:**

```yaml
command: /pm rollback
trigger: PO manual OR auto by /pm deploy on post-deploy smoke fail
preconditions:
  - last_deploy_at: <set>               # 有可 rollback 的 deploy
  - azure_slot_state: swapped | failed  # 對齊 §G.6.1
input:
  --to: optional <commit_sha>           # default = previous prod tag
  --reason: <string, required>          # PO 必填 rollback reason
output:
  rollback_log: docs/release/<date>-rollback-log.md
  azure_slot_state: rolled_back
behavior:
  1. SKILL 顯示 rollback summary:
     - 當前 prod commit vs target rollback commit
     - 影響的 feature list(diff)
     - PO 確認(型 `ROLLBACK`)
  2. Azure CLI swap-back:
     - az webapp deployment slot swap --name <app> --slot production --target-slot staging
     - (effectively undo last swap; staging slot 仍保有 previous prod build)
  3. 若需 hard rollback to older commit:
     - git checkout <commit> + 重 deploy to staging → swap
  4. 跑 post-rollback smoke(對齊 §G.1)
  5. update docs/pm/state.md:
     - phase_6_signoff: false(rollback 後 Phase 6 需重新 sign off)
     - last_rollback_at: <timestamp>
     - last_rollback_reason: <text>
  6. append docs/decision-log.md: D-pm-<id>: rollback, reason: <text>
  7. 提示 PO 是否需開 `/pm-bug-review`(對齊 §6.4.5)
audit:
  - PO confirmation 整段對話記入 decision-log
  - rollback 觸發 root_cause 必在 24h 內 documented(對齊 §10.7 stop loss)
sla:
  - zero-downtime: 對齊 Azure slot swap(預期 < 60s 切換)
  - rollback decision → execute < 5 min(對齊 incident response SLA)
confidence_tier: 🔴 low(production-impacting,PO 拍板 final)
```

**G.6.3 Worktree cleanup on Phase 6 success(對齊 §F.6 lifecycle):**

當 `/pm deploy --target prod` 成功 + Phase 7 observation 結束 + `/pm archive "<project>"` 跑時:
- 自動 prompt:「dev/<project> branch 是否刪除?(y/N,推薦 y — Phase 7 retrospective 已寫)」
- 對齊 §6.3.4 §B.6 archive policy

**G.6.4 Confidence Tier Summary:**

| 命令 | Tier | 理由 |
|:---|:---:|:---|
| `/pm deploy` | 🔴 low | production-impacting,full PO control |
| `/pm rollback` | 🔴 low | production-impacting,但比 deploy 風險高(已壞才回退)|

**G.6.5 Cross-reference 對齊既有 §G:**

- G.1 deploy_log schema → /pm deploy 寫入
- G.2 rollback plan rehearsed → /pm deploy precondition check
- G.3 quality_bar → /pm deploy precondition full check
- G.4 /pm validate-release → /pm deploy 必先跑

##### H. Phase 7 — Post-Launch Monitoring Artifact Contract

**Artifacts:**
- `docs/pm/user-feedback-log.md`(append-only)
- `docs/pm/reports/<date>-kpi-evaluation.md`
- `docs/pm/reports/<date>-final-retrospective.md`
- Bug fix commits(若有,標 P0 / P1)

**Contract Version:** `post-launch-contract-v1`

**H.1 KPI Evaluation Schema:**

```yaml
kpi_evaluation:
  date: <YYYY-MM-DD>
  observation_window: "Day 1 — Day 7 post-launch"
  baseline_from: "Requirement Spec §SLA + §7.5 KPI 表"
  efficiency_kpi:
    - name: standup_time_saved
      target: 70%
      observed: <%>
      status: ✅ pass | ❌ miss
  quality_kpi: [...]
  strategic_kpi: [...]
  overall_verdict: meet | partial | miss
```

**H.2 User Feedback Log Schema(append-only per entry):**

```yaml
feedback_entry:
  date: <YYYY-MM-DD>
  channel: line-cs | hotline | internal | direct
  user_segment: existing | new | trial
  sentiment: positive | negative | neutral
  category: bug | feature-request | UX | praise
  summary: <one-line>
  action_taken: <if any>
```

**H.3 Retrospective Mandatory Sections:**

1. What went well(≥ 3 items)
2. What didn't go well(≥ 3 items)
3. Lessons learned(≥ 5 items)
4. Recommendations for next project
5. Team consensus(每員 sign-off)

**H.4 Exit Criteria(也是專案結案門檻):**

```yaml
quality_bar:
  prod_stability_days: 7          # ≥ 7 天 no critical incident
  critical_bugs_closed: true      # P0 / P1 全 close
  perf_within_sla: true
  user_feedback_collected: true   # ≥ 5 entry(對小 spec proportional)
  kpi_overall_verdict: meet | partial  # miss 不可 close
  retrospective_team_signed_off: true
```

**H.5 Validator:** `/pm validate-post-launch`

**H.6 Phase 7 Exit Check List:**

- [ ] N 天(default 7)production 穩定無 critical incident
- [ ] P0 / P1 bugs 全 close
- [ ] Perf 仍在 SLA 內
- [ ] User feedback 已收集 + categorize
- [ ] KPI evaluation verdict ≥ partial
- [ ] Retrospective 完成 + team sign-off
- [ ] PM 跟老闆 final sign-off,state.md `phase_7_signoff = true`,project 標記 closed

##### I. Contract Version Independence

各 Phase artifact contract 獨立 versioning,**不耦合**:

| Phase | Contract Version |
|:---:|:---|
| 0 | `req-contract-v1` |
| 1 | `module-plan-contract-v1` |
| 2 | `module-spec-contract-v1` |
| 3 | `shared-infra-contract-v1` |
| 4 | `implementation-contract-v1` |
| 5 | `integration-test-contract-v1` |
| 6 | `release-contract-v1` |
| 7 | `post-launch-contract-v1` |

某一 contract minor / major 升級不影響其他 — eg. `module-spec-contract-v1.1` 加 optional field 不影響 Phase 1 _plan.md。

##### J. Master Validator + Naming Convention(跨 Phase 一鍵)

**J.1 Validator Naming Convention(對齊 spectra Round 1 N1 fix):**

統一以「**singular form + `--all` flag**」模式,**不用 plural form**:

```bash
/pm validate-req-spec <path>                  # Phase 0(only 1 spec per project,no --all)
/pm validate-module-plan <path>               # Phase 1(only 1 _plan.md per project)
/pm validate-module-spec <module-name>        # Phase 2(per-module)
/pm validate-module-spec --all                # Phase 2(全 module batch)
/pm validate-shared-infra                     # Phase 3
/pm validate-implementation <module-name>     # Phase 4(per-module)
/pm validate-implementation --all             # Phase 4(全 module batch)
/pm validate-integration                      # Phase 5
/pm validate-release                          # Phase 6
/pm validate-post-launch                      # Phase 7
/pm validate-all                              # Master(跨 Phase)
```

**規則:**
- 預設 singular(per-instance)
- 多 instance 時加 `--all` flag(eg. `--all` = all modules in current project)
- `/pm validate-all` 為 Master(跨 Phase),不要混淆於 phase-level `--all`

**J.2 Master Validator usage:**

```bash
/pm validate-all                # 跑全 Phase 對應 validator + 跨 Phase lineage check
```

輸出:

```
✅ Phase 0: req-spec validator pass
✅ Phase 1: module-plan validator pass
⚠ Phase 2: module-spec validator — 2 modules pass, 1 module (quota) has 3 issues
❌ Phase 3: shared-infra validator — lint baseline 增 2(F821)
...

Cross-phase lineage:
  ✅ Phase 0 REQ-001 → Phase 1 module-identity covers_reqs ✅
  ✅ Phase 1 module-identity → Phase 2 has 3 specs ✅
  ❌ Phase 2 F-identity-005 acceptance 未在 Phase 4 tests.md 對應 TC

Verdict: 3 validators failed, 1 lineage gap → Phase 4 NOT ready to exit
```

##### K. Discipline Invariant — No Fast Path Policy(rev 1.10 新加 — 對齊 Gap 5 PO 拍板)

> 對齊 PO 2026-06-18 拍板:「紀律很重要,該走得還是要走,以策安全,小心駛得萬年船。」

**K.1 Invariant 正式定義**

任何 **production-impacting** 改動必走完整 8-phase SDLC(Phase 0-7),**不存在 fast track / hotfix bypass / single-engineer exception**。

```yaml
discipline_invariant:
  no_fast_path: true
  no_phase_skip: true
  no_phase_reorder: true
  emergency_response_path: "/pm rollback only"      # 非 deploy bypass
  exception_scope: documentation_only_changes        # 唯一自然 exception(見 §K.5)
  enforcement: machine_validator + po_audit_log
```

**K.2 Rationale(對齊 5 條既有 memory rule)**

| Memory rule | 哲學對齊 |
|:---|:---|
| `backend_change_rule` | 任何 *.py 改動前必須先提案 + PO 授權(無 silent commit)|
| `dep_management` | pip install 必先經 PO 同意(無 quick add)|
| `delete_dialog_no_undo_hint` | 刪除 = 慎思決定(無 quick destructive action)|
| `friend_identity_change_RESOLVED` | 落地走 backend + frontend + 3 客戶端驗測完整路徑 |
| `backend_schema_change_workflow` | SSOT 必同步 + ALTER TABLE 3 樣 + PO 自 apply migration |

→ **LineBOT 18 個月累積的 customer trust 來自無例外紀律**。Fast path 哪怕一次,等於對 5 條 memory rule 開洞,**累積技術債 + 文化衰變 cost 遠 > 一次走完整 SDLC 的時間**。

**K.3 Emergency Response — Rollback ≠ Bypass**

對齊 §G.6.2 `/pm rollback` 設計:

```
P0 production incident 發生
   ↓
/pm rollback(§G.6.2,zero-downtime Azure slot swap-back)
   ↓
prod 恢復(< 5 min SLA)
   ↓
24h 內 root cause documented(對齊 §G.6.2 audit requirement)
   ↓
fix 走完整 SDLC:Phase 0(spec)→ ... → Phase 6(deploy)→ Phase 7(observe)
   ↓
非 "emergency hotfix bypass deploy"
```

**核心區別:**
- ✅ **Rollback = emergency PATH**(zero-downtime 回退,非 code change,non-impacting production logic)
- 🚫 **Fast track deploy = emergency BYPASS**(改 code + 跳 phase + 直 deploy,**禁止**)

**K.4 No Fast Path 適用範圍(必走完整 SDLC)**

| Change Type | 必走 Phase | 對齊 memory rule |
|:---|:---|:---|
| User-impacting code change | Phase 0-7 | — |
| Backend Python(`*.py`)| Phase 0-7 | `backend_change_rule` propose gate |
| Schema migration | Phase 0-7 | `backend_schema_change_workflow` SSOT + manifest(§G.6.0)|
| Dependency add(`requirements.txt`)| Phase 0-7 | `dep_management` PO ack |
| Frontend HTML/JS/CSS production deploy | Phase 0-7 | — |
| Cross-module API contract change(major)| Phase 0-7(對齊 §6.4.13 major tier 12 週 deprecation)| `v3_backend_contract_source` |
| Cross-module edge case mid-flight(minor)| §E.4b drift check lite path(對齊 §6.4.13 patch tier;非 Phase 0-7)| `v3_backend_contract_source` |
| Memory rule itself 更新 | Phase 0-7 | — |

**K.5 自然 Exception(不適用,因 不觸發 Phase 6 deploy)**

| Change Type | 處理路徑 |
|:---|:---|
| Documentation-only(`*.md` non-contractual)| 直接 commit,不入 SDLC |
| Decision log / memory file append | 直接 commit |
| `/pm` SKILL 內部 audit log | 自動 append,不入 SDLC |
| Rollback action 本身(緊急回退)| §G.6.2 path,不入 SDLC(rollback 是 emergency PATH,不是 deploy)|
| Phase 7 retrospective document update | 直接 commit(Phase 7 已 closed,事後紀錄)|

> ⚠ **判定原則:** 若 change **不會觸發 `/pm deploy`**(即不對外服務客戶端),naturally 不需 SDLC。任何**會 deploy 到 prod 的 change** = 必走完整 8-phase。

**K.6 `/pm validate-discipline-invariant` 命令(v1.2 Planned)**

```yaml
command: /pm validate-discipline-invariant
trigger:
  - auto by /pm deploy precondition check(對齊 §G.6.1)
  - 或 PO manual audit
behavior:
  1. read state.md current_phase + phase_signoff history
  2. check Phase order:0 → 1 → 2 → 3 → 4 → 5 → 6 → 7(無 skip / 無 reorder)
  3. check 每 Phase signoff 都有 audit trail in decision-log
  4. check 無 direct main commit(對齊 §E.8 worktree → main only)
  5. check `/pm deploy` 對應 commit hash 已過 Phase 6 signoff
  6. check git log no_verify count == 0(對齊 push-gate §E.8.4 — 無 --no-verify 繞 hook)
output:
  verdict: pass | fail
  violations: []                       # 列每個 invariant 違反處
  remediation: <action suggestion>
on_fail:
  - block `/pm deploy`(若 trigger=deploy precondition)
  - prompt PO ack required to override(若 PO 拍板 override,審 reason 必填)
  - log override to decision-log
confidence_tier: 🟢 high(機械化 check,對齊 §6.5 特性 2 Stage Gate)
```

**K.7 Cross-reference 對齊既有 framework**

| 既有設計 | §K 對齊 |
|:---|:---|
| §6.4.4 Trust Hierarchy | PO 拍板 override 唯一 escape valve;non-PO 不可 bypass |
| §6.4.5 `/pm-bug-review` | discovery 路徑,非 bypass — bug 收完仍走完整 SDLC fix |
| §6.4.11 §A Cross-Phase Lineage | discipline_invariant 直接 enforce lineage |
| §6.4.11 §E.3a 三向 invariant | spec↔code↔test sync,違反 = discipline 違反 |
| §6.4.11 §E.8.4 push-gate | 無 --no-verify bypass,對齊 K.6 check #6 |
| §6.4.11 §G.6.1 `/pm deploy` precondition | K.6 自動 trigger;deploy gate of last resort |
| §6.4.11 §G.6.2 `/pm rollback` | emergency PATH(對齊 K.3),非 bypass |
| §6.4.13 Contract Change Governance | Schema / contract change 走 governance,非 bypass |
| §10.7 失敗退路 Stop Loss | rollback + investigation,非 push 解決 |
| **§6.4.11 §D.2 + §E.8.1 Stage 0 V8 Gate** ⭐ rev 1.10.1 | V8 fail → Phase 4 不 advance → 自然滿足 discipline_invariant(sub-rule of "phase order");不需獨立 K.6 check;V8 是 spec-level discipline,K 是 deploy-level discipline,兩層紀律對齊 |

**K.8 PO Override Mechanism(唯一 escape valve)**

> ⚠⚠ **rev 1.17.3(2026-06-23)DEPRECATED — see §E.8.8.7**:此 mechanism 被 rev 1.17.3 "mainline-as-project" 取代。**3-month grace period(2026-06-23 → 2026-09-23)both work** — 期間 `--override-discipline` 仍 functional + warning emitted。**After 2026-09-23,§K.8 BYPASS DISCIPLINE deprecated entirely** — use uniform model `/pm use mainline --reason "..."` instead。Rationale:switching active-project IS the audit + uniform mental model,no special bypass needed。Below 內容保留為 historical reference + grace-period usage docs。

對齊 §6.4.4 Trust Hierarchy,**只有 PO 可 override discipline invariant**:

```yaml
command: /pm deploy --override-discipline --reason "<text>"

# ⭐ rev 1.10.1 — Override Scope Clarification(對齊 spectra Round 1 B1 + C4 fix)
override_scope:
  bypasses: discipline_invariant_check ONLY
  still_enforced:
    - schema_migrations_aware       # §G.6.1 + §G.6.0 migration gate
                                     # 對齊 memory: PO 自 apply prod migration,不可繞
    - V8 drift check (§E.4b)         # cross-module contract drift 仍需 verify
    - other G.6.1 preconditions      # phase_5_signoff / validate-release / rollback_plan_rehearsed
  rationale: |
    Override discipline 是 PO 對 phase order / signoff lineage take risk,
    **不是放棄 schema migration enforcement**(memory rule 嚴禁)。
    若同時撞到 missing migration + missing signoff:
      該走 §G.6.2 /pm rollback first(emergency PATH)
      + reschedule deploy with proper migration apply + override discipline
    NOT「一次 override 全部繞」(對齊 K.4 紀律哲學)。
  why_separate:
    - discipline = phase order / signoff lineage(SDLC 紀律)
    - migration = data schema state(技術紀律,memory rule)
    - V8 drift = cross-module contract integrity(設計紀律)
    三類紀律獨立,override 需 explicit scope,不一鍵繞光。

preconditions:
  - po_explicit_invoke: true            # SKILL 無法 auto-invoke
  - reason: non_empty + ≥ 50 chars       # 必詳述 why override
  - confirmation_phrase: "BYPASS DISCIPLINE"  # unambiguous gate
behavior:
  - SKILL 顯示 K.4 違反清單 + K.2 memory rule 引用
  - PO 必輸入 reason + confirmation_phrase
  - SKILL 紀錄 override 到 decision-log + state.md `discipline_overrides[]`
  - SKILL flag next 3 retrospective 重點 review override impact
  - 若 override 結果出 incident → 自動 escalate Phase 7 retro 強制 lessons learned
rationale: |
  紀律無例外,但 PO 是最終 trust source(§6.4.4)。
  Override 是 PO 對組織 explicit 負責的單一動作,
  不是「方便繞」而是「PO 主動 take risk + 留 audit trail」。
  Override 罕用 → 紀律累積;Override 頻繁 → policy 失效,需 revise SDLC。
confidence_tier: 🔴 low(極 production-impacting,PO 拍板 final + audit-mandatory)
```

**K.9 Override 使用警示(metrics + alerting)**

> ⚠⚠ **rev 1.17.3(2026-06-23)AMENDED — see §E.8.8.7**:Override frequency tracker 被 rev 1.17.3 mainline cumulative duration tracker 取代。**3-month grace period(2026-06-23 → 2026-09-23)兩 metrics 並行** — `--override-discipline` 計數仍走原 threshold;**並** mainline `active_duration_this_month` 走新 threshold(< 30 min green / 30-120 min yellow / 120+ min red+freeze per `docs/pm/mainline/state.md`)。**After 2026-09-23,override frequency tracker deprecated** — only mainline duration tracker active。Below 內容保留為 historical reference + grace-period dual-metric phase docs。

```yaml
override_metrics:
  alarm_thresholds:
    - 1 override / month: 🟡 warning(review SDLC bottleneck?)
    - 2 overrides / month: 🔴 escalate(SDLC clearly 有問題,emergency design review)
    - 3+ overrides / month: 🚫 freeze prod deploy + mandatory SDLC overhaul
  
  trail_in: docs/pm/state.md discipline_overrides[]
  reported_in:
    - daily report(若有 override 過去 24h)         # v1.1 Planned
    - weekly digest(累計 trend)                    # v1.1 Planned
    - phase 7 retrospective(全 project 累計 + impact analysis)
  
  # ⭐ rev 1.10.1 — Fallback for v1.0/v1.1 not-implemented commands(對齊 spectra Round 1 C3 fix)
  fallback_path:
    # IF daily/weekly 命令尚未實作(v1.1 Planned status):
    primary_visibility:
      - docs/pm/state.md `discipline_overrides[]` 段(append-only)
      - /pm status output banner(已實作 v1.0,加 prefix 警示)
    visibility_format:
      - banner: "⚠ N override(s) this month — alarm threshold X"
      - 對齊 K.9 thresholds(1=warning / 2=escalate / 3+=freeze)
    upgrade_path:
      - 待 v1.1 daily/weekly 命令落地,自動 read state.md 進 report
      - 不需 schema 改動,只是 view layer
```

**K.10 Confidence Tier Summary**

| 命令 | Tier | 理由 |
|:---|:---:|:---|
| `/pm validate-discipline-invariant` | 🟢 high | 機械化 check,deterministic |
| `/pm deploy --override-discipline` | 🔴 low | production-impacting + PO 拍板 final + 罕用 |

---

#### 6.4.12 未來 Sub-Skill Contracts(預留)

本節僅完整定義 spectra-review contract。其他 sub-skill 待 Phase B/C/D 各自落地時補充:

| Sub-Skill | Contract 名稱 | 預計落地 Phase | 狀態 |
|:---|:---|:---:|:---:|
| spectra-review | `spectra-contract-v1` | Phase A(本文件)| ✅ 鎖 |
| V0 — project-init | `v0-contract-v1` | Phase E | 預留 |
| V1 — planning | `v1-contract-v1` | Phase B | 預留 |
| V2 — implementation | `v2-contract-v1` | Phase B | 預留 |
| V3 — spec-quality-review | `v3-contract-v1` | Phase C | 預留 |
| V4 — cross-doc-review | `v4-contract-v1` | Phase C | 預留 |
| V5/V6 — auxiliary | TBD | Phase D | 預留 |
| V7 — pm-skill | self(本提案)| Phase E | 預留 |
| V8 — cross-module-review | `v8-contract-v1` | Phase C | 預留 |

**Contract 章節結構建議**(對齊 spectra-contract-v1):
A. Input / B. Output Files / C. Schema / D. 7-field per item(若適用)/ E. Invariants / 其他子段視 sub-skill 性質

#### 6.4.14 Team Composition Contract(rev 1.11 added — 對齊 PO 2026-06-19 4 insights lock)

> **設計理由:** PO 2026-06-19 連續拍板 4 個 architectural insights,首次將「team」抽象為正式 contract。**Extends §6.4.4 Default vs Override 哲學**(PO override > SKILL estimate / human-in-the-loop trust)到 team-level domain — 加 team_size + role coverage + AI vs Consultant 三層紀律。對齊 spectra Round 3 C7 fix:**§6.4.4 = spectra-review estimate/override mechanism;本 §6.4.14 = 同哲學 apply to team trust**,兩者 complementary(non-duplicate)。

**A. Members vs Consultants Distinction(Insight 1)**

| Layer | Members | Consultants |
|:---:|:---|:---|
| Schema | YAML `members[]` | YAML `consultants[]` |
| Counts toward `team_size`? | ✅ | ❌ |
| Has `trust_tier`? | ✅(per default_tier_by_role)| ❌(always advisory_only)|
| Can be `assigned_modules`? | ✅ | ❌ |
| Can `/pm signoff`? | ✅(若 trust_tier 對齊)| ❌ |
| Audit attribution | self | acting PO |
| Examples | PO / specialized AI_Agent | Claude general-purpose / external consultant |

**Critical invariant:** `member_type=ai_agent` 必明列 `scope` / `permitted_actions` / `forbidden_actions` / `escalation_path` / `provider`。

**B. Default Trust Tier by Role(Insight 2)**

```yaml
default_tier_by_role:
  PM: final_approver
  QA: module_owner
  Developer: contributor
  AI_Agent: contributor       # AI_Agent default contributor;explicit grant 可升 module_owner
```

**Resolution order:**
```
priority_1: explicit member.trust_tier
priority_2: auto-grant from primary_role
priority_3: trigger no_pm_behavior(若 PM 缺)
```

**C. Multi-PM `all_approve` Policy(Insight 3a)**

多 PM 時,**所有 active PM 都是 approver**(任一可 sign)。Audit log 紀錄哪位 PM 簽:
```
D-pm-007: /pm signoff phase-5 by=xiaohua (PM, multi-grant)
D-pm-008: /pm deploy --target prod by=kuohsuming (PM, multi-grant)
```

→ Multi-PM 是 collective responsibility,無 primary-PM hierarchy 概念。

**D. No-PM Auto-Postpone Behavior(Insight 3b)**

對齊「無 PM 必 postpone」紀律:

```yaml
no_pm_behavior: auto_postpone
postpone_targets:
  - /pm signoff
  - /pm deploy
  - /pm rollback
  - /pm advance-phase    # 若該 phase 需 signoff
  - /pm contract-change propose
postpone_excluded:
  - /pm build-team       # 自我 bootstrap recovery
  - /pm migration-propose
  - /pm verify-runtime
  - /pm validate-discipline-invariant
```

**Workflow:**
1. Command 觸發前 SKILL 跑 `resolve_final_approver()`
2. 無 active PM → 自動 postpone(無 prompt)
3. Append to `state.md.postponed_commands[]`
4. 下次 `/pm build-team` PM assigned 時 surface list + PO explicit consent to resume
5. **永不 silent auto-execute resumed commands**(對齊 destructive op safety)

**E. MVT 3-Role Coverage(Insight 4)**

Minimum Viable Team:**至少 1 active member with role PM AND ≥ 1 with QA AND ≥ 1 with Developer**(可同人 multi-role)。

**Enforcement 2 層:**

| Layer | 範圍 | Behavior |
|:---:|:---|:---|
| **Soft reminder** | `/pm build-team output` / `/pm status` / `/pm daily` / `/pm verify-runtime Layer 6` | Print warning,continue command |
| **Hard block** | `/pm advance-phase 1` / `/pm deploy --target prod` / `/pm signoff phase-N` / `/pm rollback` | Refuse + 提示「assign missing role via /pm build-team」 |

**AI_Agent role eligibility:**
- Can fill `QA` / `Developer`
- **Never fill `PM`**(對齊 §6.4.4 PO-as-final-trust-source 哲學 + 本 §6.4.14 §E human-only PM invariant;對齊 spectra Round 3 C7 fix:specific cross-ref)
- `member_type=ai_agent` 必須 explicit `scope` + permitted/forbidden lists

**Carve-outs:**
- `project_type=sandbox` 跳過 MVT enforcement(可實驗無 PM)
- production / training / poc 必齊 3 roles

**F. Bootstrap protection rules**

| Action | Behavior |
|:---:|:---|
| `/pm init` 新 project | Auto-add invoker as PO with `primary_role=PM` |
| Try to remove last active human | **Refuse**(must `/pm archive` 才能 close project) |
| Try to remove last active PM | Warn + sub-prompt:「(a) promote 其他 member 為 PM (b) accept no-PM postpone state」 |
| Sandbox 跑 deploy 無 team | Allowed(carve-out)|

**G. Cross-command integration**

| Command | Team-coverage check |
|:---:|:---|
| `/pm signoff phase-N --approver <id>` | Verify `<id>` in active members + trust_tier == `final_approver`(對齊 spectra Round 3 N6 fix:enum-precise wording,non-`≥`)|
| `/pm deploy --target prod` | Verify resolve_final_approver() non-empty + caller is approver |
| `/pm rollback` | 同 deploy |
| `/pm advance-phase 1` | Hard block if MVT incomplete |
| `/pm build-team` | Self-recursive(after invoke,re-check coverage + surface postponed)|
| `/pm verify-runtime` | New Layer 6:Team coverage check |
| `/pm status` | Display coverage + postponed list |

**H. Contract Version**

- `team-roster-v1`(2026-06-19 之前 — implicit,Claude as member)
- `team-roster-v2`(2026-06-19 — 本 contract,members vs consultants split + invariants)
- Future minor:加 `is_primary_pm` flag if multi-PM `first_only` policy needs revival

#### 6.4.15 SKILL Workflow Lifecycle(rev 1.12 added — 對齊 PO 2026-06-19 第 7 個 architectural insight)

> **設計理由:** PO 連續抓到 spec workflow 跟 real invocation 落差(spectra Round 3 C8 + eat-own-dog-food #18):**workflow 寫進 SKILL.md ≠ workflow 落地驗證**。本 section 明確定義 SKILL workflow 的 lifecycle 4 stages,**每 stage 有明確 gate**,避免 「spec written = done」 假象。

**4-Stage Workflow Lifecycle**

| Stage | Status marker | Meaning | Required gate |
|:---:|:---|:---|:---|
| **1. Document-only** | `vX.Y-doc` | Workflow text 在 SKILL.md 內,Claude 可讀 follow | Spec review pass(spectra-review ship-as-is)|
| **2. First-invoke test**(eat-own-dog-food)| `vX.Y-tested` | PO 真實 invoke 一次,**workflow 9-step 全跑** | Findings logged + critical bugs fixed |
| **3. Validated** | `vX.Y-validated` | PO 多次 real-world invoke + 0 critical findings | Aggregate ≥ 3 invocations + 100% close rate |
| **4. Production-ready** | `vX.Y` | Workflow 對齊 spec,**production ready** | Validated 跑 ≥ 14 day stable |

**對齊 PM Skill 既有實踐(historical examples):**

| Command | Current stage | Reason |
|:---:|:---|:---|
| `/pm init` / `/pm signoff` / `/pm advance-phase` / `/pm status` / `/pm validate-*` | v1.0(production-ready)| 多次 real-world 使用 + stable |
| `/pm bootstrap-project` | v1.1(production-ready)| Multiple rounds dogfood + spectra-review pass |
| `/pm push-gate` / `/pm setup-worktree` / `/pm migration-*` / `/pm deploy` / `/pm rollback` / `/pm validate-discipline-invariant` / `/pm verify-runtime` | v1.2-validated 至 v1.2-doc | 大部分 spec written,部分 dogfood tested |
| `/pm build-team` | **v1.4-tested**(對齊 eat-own-dog-food #18) | 第 1 次 real invoke,4 findings logged + 立刻 fixed |
| `/pm schema describe` / `/pm schema-status` | v1.4-spec | 未 invoke |

**Lifecycle enforcement rules:**

1. **Stage transition 不可 silent:**任 stage 升級必 decision-log 紀錄 + invocation evidence
2. **降級可能:** 若 dogfood / production 暴露 critical bug → 降級回早期 stage
3. **Status marker 必 explicit:** SKILL.md `## Subcommand: <name>` heading + Version section 必明示 stage
4. **First-invoke test 必 PO trigger:** 對齊 §6.4.4 trust hierarchy(non-silent auto-test)
5. **Validation 累計 ≥ 3 invocations** 才升 Validated(對齊 statistical confidence)
6. **Production-ready 升級需 ≥ 14 day** 觀察 stable + 0 new critical findings

**Cross-references:**
- spectra-review enhanced-v1 contract(對齊 stage transition 必走 review)
- §6.4.13 Contract Change Governance(workflow 改動屬 minor change 對齊)
- Eat-own-dog-food rounds = first-invoke test 紀錄 source
- decision-log audit trail(per stage transition)

**Impact 對 PM Skill 既有 commands:**

對齊本 lifecycle 我們**回顧** v1.x 各 SKILL workflows 並 mark current stage,**對齊 spec-vs-real drift 可追蹤化**。Phase 6 release 紀律加 `/pm verify-runtime` 加 Layer 7 「workflow lifecycle stage check」(對齊 Round 3 S17 cross-doc adversarial 演化方向)。

---

#### 6.4.16 SDLC v2 Contract — Phase 0/1/2 Reorder(rev 1.13 added — PO 2026-06-20 lock)

> **Authority:** §6.4.10 §L Contract Override Mechanism + revision 1.13 promotion 為 canonical contract
> **Effective:** 2026-06-20 onwards;**supersedes** §6.4.10 §B(Phase 0)+ §6.4.11 §B(Phase 1)+ §6.4.11 §C(Phase 2)v1 versions
> **Grandfather rule:** Projects past Phase 2 stay on v1;Phase 0/1 projects must adopt v2 on next advance(若 currently Phase 1 → rollback to Phase 0 then re-advance under v2)

##### Motivation(PO 2026-06-20 insight)

Phase 0 強制 MVT 3-role team coverage 是雞生蛋:**沒 split 怎能知缺哪 role?** team-build 應在 Phase 1 split 後做。1-dev project with 3 distinct artifact types(.py / SKILL.md / memory.md)仍 warrants module split,但 **BY ARTIFACT TYPE not team parallelism**。

##### Phase 0 — Requirement Gathering(WHAT,supersedes §6.4.10 §B)

**Goal:** WHAT users need 全鎖定(no implementation discussion)

| Acceptance | 對齊 |
|:---|:---|
| Requirement spec authored(≥ 500 行 + 11 必填欄位 per REQ,含 golden_scenario + anti_examples 三元組)| §6.4.10 §B.4 |
| Glossary ≥ 7 / Out of Scope ≥ 3 / Assumptions ≥ 2 / Constraints ≥ 2 | §6.4.10 §B.2 |
| **Bootstrap PM only**(invoker auto-add as PM,no MVT 3-role enforcement)⭐ v2 NEW | §6.4.14 §F + §phase_0_carve_out |
| spectra-review pass | §6.4.3 |
| PO 拍板 spec ship-as-is | §6.4.4 |
| Phase 0 signoff(`/pm signoff phase-0 --approver <PM>`)| §6.4.10 §B.5 |

**Phase 0 NO LONGER includes:** team coverage check(MVT 3-role)— moved to Phase 1。

##### Phase 1 — Structuring(HOW we organize,supersedes §6.4.11 §B)

**Goal:** STRUCTURE + 各 module 功能設計鎖定

**5-step dialogue**(每 step PO confirm 進下一 step):

###### Step 1.1: Module split discussion + Modules Overview document

**Default rule:** split by artifact-type
- eg. backend `.py` / SKILL.md / memory.md = 3 modules(or 2,thin artifact 可合)
- 1-artifact-type project → default 1 module(no ceremony)
- PO override accepted with logged reason

**Deliverable 1:** state.md `modules[]` populated(machine state — internal operational)

**Deliverable 2(⭐ PO 2026-06-20 critical insight — HUMAN-FIRST docs):**
`<project>-modules-overview.md`(at `docs/pm/<project>/spec/<project>-modules-overview.md`)

**對齊 memory `feedback_human_first_docs`** — docs are for HUMAN reading not AI YAML metadata。

**Document structure(per module mandatory 4 sections):**

```markdown
## Module N — <module-name>

### 📋 What it does(1-2 sentence plain prose — everyone reads first)
[succinct overview]

### 👔 For PM
- Suggested owner
- Estimated effort(hours)
- Risk level + 1-line reason
- Cross-module dependency
- Suggested phase 4 implementation order
- Postpone / cross-ref considerations

### 🔬 For QA
- Test surface(what to test)
- Test approach(unit/integration/e2e/DB-required)
- Acceptance criteria refs(REQ-NNN F-X)
- Key test scenarios(happy / edge / failure)
- Negative tests

### 💻 For Developer
- REQ coverage(N REQs list with 1-line description each)
- Functions to implement(list with signatures or 1-line each)
- File paths(where code lands)
- Library dependencies
- Forward/backward-compat invariants
- Reference cross-refs
```

**Document also includes(root level):**
- 🗺 Big picture(1 paragraph + ASCII module dependency diagram)
- 🔗 Module dependency graph(Phase 4 implementation suggested order)
- 📊 Coverage matrix(all REQs → modules table,no leftover REQs)

**Rule:** No YAML blob as main content;YAML metadata stays in frontmatter only。

**Exit criteria:** PO confirms `<project>-modules-overview.md` readable by 3 roles。

###### Step 1.2: `/pm build-team`(full team composition)

- 對齊 split 後實際 work units 配人
- 1-PO multi-role still legal(同人兼 PM/QA/Dev)
- **MVT 3-role coverage check pass**(現在才 enforce,不在 Phase 0)
- team-roster.md frontmatter v2 schema lock

###### Step 1.3: Assign modules → team(ownership matrix)

- Each module gets ≥ 1 owner
- Multi-owner allowed(1-PO 自身可兼)
- state.md modules[].owner field populate
- Functional spec author / Design spec author 對齊 module owner(默認同一人)

###### Step 1.4: Functional spec per module(WHAT each module delivers)

- Output:`<project>-<module>-functional-spec.md`
- 對齊 HUMAN-FIRST docs principle(同 Step 1.1 deliverable 2 規約 — 3-role perspectives)
- Feature list per module(對齊 §6.4.11 §C.2 schema simplified — 從 root REQ 細化)

###### Step 1.5: Design spec per module(HOW implementation works)

- Output:`<project>-<module>-design-spec.md`
- 對齊 HUMAN-FIRST docs principle
- ⭐ **恆寫(D-035:5 份 spec 永遠在,不 skip)**;`risk_level` 只控**深度**:medium|high = 完整;low-risk/simple = 寫到 floor(1 component + covers_func + file_impact + test_seam),不省(framework §6)

##### Phase 1 Exit Check List(v2)

- [ ] Step 1.1 module split locked(state.md modules[] populated)
- [ ] Step 1.1 `<project>-modules-overview.md` authored(3-role per module structure)
- [ ] Step 1.2 team-roster.md v2 schema + MVT 3-role coverage pass
- [ ] Step 1.3 every module has ≥ 1 owner
- [ ] Step 1.4 functional spec authored per module
- [ ] Step 1.5 design spec authored per module(D-035:恆寫,不 skip;low-risk = floor 深度)
- [ ] 每個 Phase 0 REQ 被 ≥ 1 module 覆蓋
- [ ] Dependency graph 無 circular
- [ ] PM 簽核 `phase_1_signoff = true`

##### Phase 2 — Implementation Planning(HOW we execute,supersedes §6.4.11 §C)

**Goal:** WORK PLAN 鎖定(task / timeline / risk),**no longer 寫 functional / design spec — 已在 Phase 1 完成**

| Acceptance | 對齊 |
|:---|:---|
| Per-module `<project>-<module>-plan.md`(task breakdown + timeline + risk only)| §6.4.11 §C.3 schema simplified |
| Solo project carve-out:Phase 2 可 collapse 進 Phase 1(PO override + log)| §K Discipline Invariant |
| PM 簽核 `phase_2_signoff = true` | §6.4.11 §C.7 simplified |

##### Phase 3-7

Unchanged from §6.4.11 §D-§H。

##### Migration policy(2026-06-20)

| Project state | Migration action |
|:---|:---|
| Past Phase 2 signoff | Grandfather under v1(no forced re-do)|
| Phase 0 or Phase 1 in-progress | Adopt v2 on next advance(若 currently Phase 1 → rollback to Phase 0,team-roster clean to bootstrap-PM-only,re-advance under v2)|
| New projects(from 2026-06-20)| Default v2 from `/pm init` |

##### Workflow command alignment

| Command | v2 behavior |
|:---|:---|
| `/pm init` | Bootstrap PM only invariant(no MVT 3-role enforcement)|
| `/pm advance-phase 1` | Trigger 5-step dialogue(Step 1.1 → Step 1.5)|
| `/pm gate-check phase-0` | 9-criterion check(see Phase 0 Acceptance above)|
| `/pm gate-check phase-1` | 9-criterion check(see Phase 1 Exit Check List above)|
| `/pm gate-check phase-2` | Per-module plan.md + signoff(simplified)|
| `/pm build-team` | Phase 1 Step 1.2 primary invocation(legal in other phases for adjustments)|

##### Cross-references

- §6.4.10 §B(Phase 0 v1)— **superseded** for new projects;preserved for historical / grandfather
- §6.4.11 §B(Phase 1 v1)— **superseded**;preserved
- §6.4.11 §C(Phase 2 v1)— **superseded**;preserved
- §6.4.14 Team Composition Contract — `phase_0_carve_out: true` invariant added for v2
- Memory:`feedback_human_first_docs`(Step 1.1 / 1.4 / 1.5 deliverable structure rule)

---

#### 6.4.17 Mid-Phase Requirement Change Governance(rev 1.14 added — PO 2026-06-20 lock)

> **Authority:** §6.4.13 minor change tier(REQ change is contract change)+ §6.4.16 SDLC v2 cascade rules
> **Effective:** 2026-06-20 onwards
> **Motivation(PO 2026-06-20 insight):** Phase 1+ 進行中 developers 常發現 spec REQ 需 drop / add / modify;**沒 phase rollback 但 module 可能要 re-eval split**。需 formal workflow 保留 已完成 functional/design spec(避免重做)同時 audit trail 完整。
> **Critical principles(PO 2026-06-20 explicit lock):**
> - **P1: NEVER automatic phase rollback** — ONLY PM-triggered via `/pm advance-phase <N<current>` + `CONFIRM ROLLBACK` 對齊 §K.8
> - **P2: NEVER automatic module reorg** — done modules 永不自動動;**PM-triggered only** via `/pm requirement drop|add-mid-phase|modify` + PM sub-prompt module placement
> - **P3: Minimum spec re-author** — 僅 affected module 改 functional/design;其他 modules 完成 specs 不動
> - **P4: Audit trail mandatory** — spec rev bump + decision-log + spectra-review --quick on amended spec
> - **P5: PM-driven module placement** — PM 拍板 assign to existing module / create new / merge / orphan,不自動 reorg

##### Cascade tier matrix(phase-aware + cost-aware,rev 1.15 — PO 2026-06-20 enhancement)

**Tier classification factors(rev 1.15 加 phase-aware cost):**

1. **cascade_scope** — module count affected + downstream REQ count
2. **rework_cost** — aggregate minutes across all completed phases(0 through current_phase)依 artifact 數
3. **Tier = max(cascade tier, cost tier)** — worst-case worst-of-both wins

**Cost reference per phase artifact(rough estimate):**

| Phase | Artifact | Min/touch |
|:---:|:---|:---:|
| 0 | requirement-spec section edit + rev bump | 5-10 |
| 0 | spectra-review --quick on amended spec | 10-15 |
| 1 | modules-overview update | 5-10 |
| 1 | functional spec per module re-author | 15-30 |
| 1 | design spec per module re-author | 15-30 |
| 2 | plan.md per module re-author | 15-20 |
| 3 | shared infra spec edit | 15 |
| 4 | Python / SKILL.md / memory code refactor | 30-180(per module)|
| 4 | unit test re-write + lint | 15-30 |
| 5 | integration test re-run | 30-60 |
| 6 | release artifact prep + deploy abort | 60-180 |
| 7 | post-launch metric reset + observation re-do | 120-480 |

**4-tier cascade matrix(rev 1.15 — 加 🔴 major-rework tier):**

| Tier | 場景 example | cascade_scope + rework_cost | 已完成 specs / code 影響 |
|:---:|:---|:---|:---|
| 🟢 **No-cascade** | Drop already-deferred REQ / Add REQ deferred 為 spec-only | 0 modules + < 15 min | 0 artifacts re-author |
| 🟡 **Patch** | Drop REQ but module 仍 ≥ 1 REQ / Add REQ to existing module + only Phase 0-1 done | 1 module + < 60 min | 1 module specs(Phase 0-1)|
| 🟠 **Re-assign** | Drop REQ → module empties(PM 拍板:remove / merge)/ Add REQ 不 fit any artifact-type / OR Phase 2-3 已 done 要 plan re-author | PM-chosen action OR 60-240 min | 0-1 module spec + plan if Phase ≥ 2 |
| 🔴 **Major-rework**(rev 1.15 NEW)| REQ change affects code already 在 Phase 4+ written / OR integration test passing 失效 / OR deploy 已 done | > 240 min(4 hr+)+ code refactor + test re-run + possibly deploy abort/rollback | code + tests + integration + possibly release |
| 🔴 ~~Phase rollback~~ | **取消 tier**(對齊 P1 — NEVER automatic;若 PM 真要 rollback 走 `/pm advance-phase <N<current>`)| — | — |

**Important:** 🔴 major-rework **不等於** phase rollback。PM 可以選擇:
- (a) Accept high rework cost,apply at current phase(對齊 P3 minimum re-author 但 scope 真大)
- (b) Use `/pm advance-phase <N<current>` rollback(P1 — PM-explicit)+ re-do from earlier phase
- 對齊 P5 PM-driven choice

##### 5-step workflow per requirement change

```
Step 1: Auto impact analysis(/pm requirement impact-analysis enhanced — rev 1.15 phase-aware)
  - Read state.md.current_phase as <C>
  - For each phase P in [0, 1, ..., C]: assess artifact impact + estimate rework cost
  - 列 affected modules(state.md modules[].covers_reqs grep)
  - 列 affected specs across all phases(functional / design / plan / code / tests)
  - Aggregate Cascade Tier:cascade_scope ∪ rework_cost(worst wins,4-tier matrix)
  - Show per-phase impact table + cost estimate
  - Show PM placement suggestions

Step 2: PM module placement decision(if Tier ≥ Patch)
  - For add-mid-phase:assign to existing module / create new module / defer
  - For drop:keep module / merge / remove(if empties)
  - For modify:re-author affected specs / log change without re-author(if trivial)

Step 3: Apply PM choice
  - Update requirement-spec(rev bump → see §6.4.13 rev convention)
  - Update state.md modules[].covers_reqs
  - Update modules-overview.md(if module add/remove/REQ assignment change)
  - Target spec re-author(only affected modules — P3 minimum)

Step 4: Audit trail mandatory
  - Append D-req-{drop|add-mid-phase|modify}-<seq> to project decision-log
  - Append D-spec-rev-<seq> for spec rev bump audit

Step 5: spectra-review --quick on amended spec
  - Quick mode: structural sanity + 9 acceptance criteria spot-check
  - Full re-review only if Tier=Re-assign + module count change
```

##### `/pm advance-phase <N<current>` rollback path(P1 explicit lock)

PO 想真 rollback 時:

```
/pm advance-phase 0 --reason "<text>" --confirm-rollback
  Step 1: Show preview — current_phase = X → target = 0
  Step 2: Require `CONFIRM ROLLBACK` 二次確認(對齊 §K.8 BYPASS-style)
  Step 3: Preserve artifacts:
    - Move state.md.modules[] to phase_<X>_history.modules
    - Move spec/modules/<N>/ to spec/_phase<X>_rollback/<ISO>/
    - Keep modules-overview.md(as historical reference)
  Step 4: Reset state.md.current_phase = 0 + phase_X_signoff = false
  Step 5: Append D-rollback-<seq> with full context
```

→ 對齊 P1:**rollback ONLY 由 PM 明示 + 對齊 §K.8 destructive phrase + 完整 audit**。Spec 自身 NEVER rollback,modules-overview 保留作歷史。

##### Workflow command alignment

| Command | Behavior |
|:---|:---|
| `/pm requirement impact-analysis <REQ-id>` | Enhanced(rev 1.15 phase-aware):列 affected modules + per-phase rework cost + Tier classification + PM placement suggestions |
| `/pm requirement drop <REQ-id> --reason "<text>"` | 5-step workflow with Tier classification + PM module decision sub-prompt |
| `/pm requirement add-mid-phase <REQ-id> --reason "<text>"` | 5-step workflow with PM placement(existing module / create new / defer)|
| `/pm requirement modify <REQ-id> --aspect <X> --reason "<text>"` | 5-step workflow with PM re-author decision per affected module |
| `/pm requirement split <REQ-id> --into <new-id-list> --reason "<text>"` ⭐ rev 1.16 | Specialized:carve-out source REQ into N new REQs + CONFIRM SPLIT + per new REQ PM module assign + spec rev bump |
| `/pm requirement merge --reqs <id-list> --into <new-id> --reason "<text>"` ⭐ rev 1.16 | Specialized:consolidate N REQs into 1 + same-module precondition + CONFIRM MERGE + PM field reconciliation + spec rev bump |
| `/pm requirement move <REQ-id> --from <module> --to <module> --reason "<text>"` ⭐ rev 1.16 | Specialized:non-destructive ownership transfer + CONFIRM MOVE + artifact-type compat warning + NO spec rev bump(content unchanged)|
| `/pm spec-rev-bump <project> --rev <X>.<Y> --reason "<text>"` | Standalone audit:bump spec frontmatter `rev` + append D-spec-rev-<seq>(P4 audit mandatory)|
| `/pm advance-phase <N>` | Enhanced:supports N < current_phase rollback path(P1 PM-triggered ONLY)|

##### Cross-references

- §6.4.13 Contract Change Governance(REQ change classified as minor change tier per §6.4.13)
- §6.4.16 SDLC v2 Contract(Phase 1 Step 1.4/1.5 functional/design spec — 本節保留 P3 minimum re-author)
- §6.4.10 §L Contract Override Mechanism(spec rev bump = post-signoff amendment)
- §K.8 BYPASS-style destructive phrase(rollback / drop empties module 都用)
- Memory:`feedback_human_first_docs`(amendment 仍 keep 3-role structure)

---

#### 6.4.13 Contract Change Governance

- **Patch change**(eg. 文案 polish / 新增 optional field)→ 不升 contract version,正常 commit
- **Minor change**(eg. 新增 required field + 提供 migration)→ 升至 `spectra-contract-v1.1`,需 PO ack
- **Major change**(eg. 改 schema 結構 / 移除 field)→ 升至 `spectra-contract-v2`,需 PO 拍板 + 12 週 deprecation 緩衝期

Sub-skill 必須在 SKILL.md 宣告對齊的 contract version;同 SKILL 可同時支援多個 contract version(eg. v1 + v1.1)。

---

### 6.5 整套流程的 4 大核心特性

#### 特性 1:AI 助理「Day 1 介入」,不是「Day 90 才上場」

過去的工具(eg. Jira / Linear)通常是「**等專案做到一半才開始用**」,因為前期太混亂不知怎麼建 board。**我們的 AI 助理從 Phase 0 第一天就介入** — 它幫 PM 把模糊需求結構化成可執行的專案輪廓,**這是它最有價值的一個介入點**。

#### 特性 2:Stage Gate 機械化,不靠主觀判斷

每個 Phase 結束都有 **machine-checkable 允收標準**:
- 「規格 spec 是否寫完?」→ 檔案存在性 check
- 「測試是否全綠?」→ 跑 test exit code check
- 「跨模組 review 是否通過?」→ 讀 review log verdict
- 「PM 簽核?」→ 讀 state.md flag

**不再靠 PM 主觀判斷「ready 沒」,不再被「我覺得差不多了」的個人感覺左右**。

#### 特性 3:Human-in-the-Loop 永不消失

每個 Phase 結束都有 **「PM 簽核」** 作為最後一道閘:
- AI 助理跑完 exit criteria check → 列出 pass / fail
- **PM 看完 + 拍板** → 才能進下一 Phase
- AI 不會「自動 advance」,主導權永遠在人類

**「Claude is assistant, not authority」原則貫穿全 8 個階段**。

#### 特性 4:每階段有明確 SLA + 產出

從 Phase 0 到 Phase 7,**每個階段都有預估時程 + 明確產出文件 + 哪些人進場**。老闆隨時可以問:「現在在 Phase 幾?何時可進 Phase 幾?」 — **答案明確,沒有「不知道」**。

### 6.6 對老闆的承諾

看完這套完整運轉流程,我們對老闆做出以下承諾:

- **「Phase 從 0 到 7 都有清楚定義,沒有灰色地帶」**
- **「AI 助理從 Day 1 就介入,不是專案做到一半才補上」**
- **「每階段 exit criteria 機械化,不靠 PM 主觀判斷」**
- **「主導權永遠在 PM,AI 不會擅自 advance」**
- **「老闆隨時問進度,我們都答得出來 + 有檔案佐證」**

這套流程不是理論 — **是我們經過 PO 100+ 輪設計討論後收斂的具體可執行 SDLC**。

---

## 七、對組織的好處(商業價值)

### 7.1 對 PM / PO 的好處

**時間節省 70-80%:**
- 每日進度 standup:**從每天 30 分鐘 → 5 分鐘**
- 每週狀態報告:**從手寫 2 小時 → AI 產出 + 5 分鐘 review**
- 階段審查:**從主觀判斷 → 機械化檢查 30 秒搞定**

**決策品質提升:**
- **從工程師自己回報 → 從 ground truth(規格 + 程式碼)推**
- 不再被「我覺得快好了」誤導
- 跨組依賴自動偵測,不漏 critical path 風險

**全局視野自動化:**
- 整個專案 50 個任務的進度,**一頁紙看完**
- 哪個工程師沉默幾天、哪個超前、哪個落後 — **一目了然**

**權威不被取代:**
- AI 助理 surface 資訊,**真人 PM 永遠是最終決策者**
- 「Claude 是助理,不是 boss」

### 7.2 對工程師的好處

**0 額外負擔:**
- 不用每天填日報
- 不用每週寫週報
- 不用在 Jira 上 maintain task status
- **工作行為本身就是進度回報**

**規格品質提升:**
- AI 強制要求「開始任務前列計畫」→ 設計更嚴謹
- AI 強制要求「結束任務更新狀態」→ 落地更扎實
- AI 自動跑 review → quality feedback 不漏

**跨組整合風險降低:**
- 每週自動跑跨組規格 review
- Phase 2 就抓到衝突,不會等到 Phase 5 才 surprise
- 大家少加班、少救火

**Claude 全自動處理:**
- 工程師只要照常用 Claude 寫程式
- 所有「給 PM 看的東西」AI 自動產出
- **不用學新工具、不用記新流程**

### 7.3 對組織的好處

**專案規模化能力:**
- 過去:5 人專案,1 個 PM 累爆
- 未來:5 人專案,1 個 PM + AI 助理,輕鬆
- **同樣 PM 人力可以管 2-3 倍 project size**

**Audit Trail 完整:**
- 所有決定、review、進度都檔案化
- 新人 onboarding 翻檔案即可
- 客戶問「為什麼當初這樣做」→ 有紀錄
- **降低關鍵人才離職的知識斷層風險**

**Time-to-Market 縮短:**
- 跨組衝突早期解
- Phase 階段審查自動化
- 整體專案 delay 風險降低 **20-30%**

**人才吸引力:**
- 工程師不用做填表苦力 → 留任率提升
- 規格品質提升 → 新人 onboarding 快
- 公司科技形象升級

### 7.4 跟業界先進公司對標

| 公司 / 工具 | 達成的 maturity | 我們的方案 |
|:---|:---|:---|
| Notion Engineering(內部工具)| ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ 對標 |
| Stripe Internal SDLC | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ 對標 |
| 一般 SaaS 用 Jira / Linear | ⭐⭐⭐ | 跨層級 |
| 一般小團隊 Excel 跟 LINE | ⭐ | 跨層級 |

**我們透過 AI 助理,在不大舉投資工具 + 不打擾工程師 workflow 的前提下,達到業界一線 SDLC maturity。** 這在過去是不可能的。

### 7.5 成功評估指標(Key Performance Indicators)

任何 project 都需要明確的成功標準。**老闆問「怎麼知道這個 project 有沒有成功?」我們的答覆就是這些 KPI**。

我們建議用三層 KPI 衡量:

#### 層次一、效率指標(Efficiency KPI)— 立即可量化

| KPI | 現狀(估計)| 目標(6 個月內)| 衡量方式 |
|:---|:---:|:---:|:---|
| PM 每日 standup 耗時 | 30 分鐘 | **5 分鐘以下** | PM 自我計時 1 週 |
| PM 每週狀態報告耗時 | 2-3 小時 | **15 分鐘以下** | PM 自我計時 1 週 |
| Phase Gate 審查耗時 | 2 小時 | **5 分鐘以下** | 時段紀錄 |
| 工程師每週填表時間 | 1-2 小時 | **0** | 工程師訪談 |
| 跨組衝突發現時間 | 整合階段 | **設計階段** | review log 對照 |

#### 層次二、品質指標(Quality KPI)— 6 個月後可評估

| KPI | 現狀 | 目標 | 衡量方式 |
|:---|:---|:---|:---|
| 規格 drift 件數 / project | 5-10 件 | **0-2 件** | health check 報告 |
| Phase advance 後發現 missing item | 2-3 次 / project | **0 次** | retrospective 統計 |
| 重大規則回滾(改了又改)| 1-2 次 / project | **0 次** | Decision Log 對照 |
| 新人 onboarding 上手時間 | 2-3 週 | **1 週以下** | 新人訪談 |
| 跨輪 review 已收斂議題重提 | 30-40% | **<5%** | review log 對照 |

#### 層次三、戰略指標(Strategic KPI)— 12 個月後可評估

| KPI | 目標 |
|:---|:---|
| 同樣 PM 人力可管理 project 數 | **提升 2-3 倍** |
| 工程師留任率 | **提升 10-20%** |
| 整體 project delay 機率 | **降低 20-30%** |
| 公司科技形象 / 招募吸引力 | **質性提升**(透過招募反饋) |
| 客戶對 audit / 規格追溯能力的滿意度 | **質性提升**(客戶訪談) |

#### KPI 評估時間表

```
Phase F 試跑結束(Week 16+ 約 4 個月):
  → 評估「效率指標」全部達標 → 推薦正式採用
  → 若效率指標未達標 → 啟動「失敗退路」(§10.7)

採用後 6 個月:
  → 評估「品質指標」
  → 若達標 → 申請 Phase G 擴大採用到 N 個 project

採用後 12 個月:
  → 評估「戰略指標」
  → 跟老闆 review 整體 ROI 並做 retro
```

**關鍵原則:KPI 必須在「實作完成前」就鎖定**,避免事後挪移基準線。**這份提案的 KPI 就是 PM Skill 採用後的「正式驗收標準」**。

---

## 八、風險與對策

### 風險一:工程師偷懶,Bypass AI 助理直接 commit

**對策:**
- 設置 pre-commit hook 檢查 commit message 格式
- AI 助理會偵測「commit 存在但規格沒更新」的異常,自動 flag
- 持續違規:weekly sync 公開檢討
- **本質上對齊「工程師不會自己增加工作量」原則 — 規矩設了就是規矩**

### 風險二:工程師寫假規格(寫已完成但其實沒做)

**對策:**
- AI 助理跑「健康檢查」:規格 vs 程式碼 vs 測試 三者交叉比對
- 規格寫已完成 → 必有對應 commit + PR 合併 + 測試通過
- 對不上 → 自動 flag → PM 看到 → 抓出來
- **比真人 PM 用「self-report」更不容易被騙**

### 風險三:AI 助理推薦錯誤行動

**對策:**
- AI 助理只 surface 資訊,**不直接執行**
- 所有行動由真人 PM 決定
- 推薦含 confidence level 標示
- PM 永遠可以拒絕推薦
- **AI 是助理,不是 boss**

### 風險四:Schema / Format 之後想改怎辦

**對策:**
- Schema 鎖定為「公司 contract」,改動需 PO 拍板
- Schema 加版本欄位,支援漸進升級
- 改動 cascade 由 Tech Lead 統一處理
- **對齊既有「規格改動需 governance」精神**

### 風險五:技術落地風險

**對策:**
- 分階段上線(12 週 6 phase)
- 第 1 個 phase 完成 PO review → 才進下一 phase
- 在 1 個真實 project 試跑驗證 → 才正式採用
- **不是 big bang 一次推,而是漸進驗證**

### 風險六:工程師抗拒新流程

**對策:**
- **既有工作流程不變** — 用 V1 / V2 跟以前一樣
- 自動化部分對工程師「透明」 — 不需要學新工具
- Tech Lead + PO 親自示範,Phase 1 試跑收回饋
- **這方案 vs Jira / Linear 的關鍵優勢:0 學習成本**

---

## 九、投入與回報(ROI 預估)

### 投入

| 項目 | 預估 |
|:---|:---|
| 時程 | **12 週(3 個月)** |
| 人力 | 1 個 Tech Lead 主導 + PO 多 review 參與(每週 4-6 小時)|
| 試跑 project | 對齊既有 Phase 1.5 訂閱開發(不需額外成本)|
| 技術風險 | 低(全 file-based,不需新基礎建設)|
| **總投入** | **約 1 個工程師 3 個月** |

### 回報(年化)

| 項目 | 預估 |
|:---|:---|
| PM 時間節省 | 每位 PM 每週節省 **8-10 小時** |
| 工程師時間節省(免填表)| 每位工程師每週節省 **2-3 小時** |
| 專案 delay 風險降低 | **20-30%**(早期抓衝突)|
| 規格品質提升 | **30-50%**(自動 review + 強制 schema)|
| 新人 onboarding 速度提升 | **2-3 倍**(audit trail 完整)|
| **首年 ROI** | **3-5 倍投入回收** |

### 長期戰略價值

- **規模化能力:** 未來 project 規模可線性擴張,而 PM 人力不需線性堆疊
- **科技形象:** 公司對外形象升級為「AI-Native 工程組織」
- **人才吸引:** 工程師留任率提升 + 招募吸引力提升
- **客戶信任:** Audit Trail 完整 → 客戶問規格決策有檔案可查

---

## 十、時程規劃

> **注意:** 本章節時程是「**PM Skill 建置與試跑**」的時程,**不是用 PM Skill 管理的某個 project 的時程**。後者見 §六 8 個 Phase 的估時。

我們採 **「漸進交付 + 階段驗證」** 策略,每個 Phase 完成有具體可見產出,PO sign-off 後再進下個 Phase。**任何階段都可暫停 / 縮減,不是 all-or-nothing**。

### Phase A — 基礎建設(Week 1-2)

建立 schema 跟規範文件(產出可看的 markdown 檔)
- 規格 schema 定義
- Phase Gate 7 個階段檢查表
- 各種 state file template

**Phase A 結案標準:** 文件 review 通過,PO 對 schema 滿意

### Phase B — 核心工程師 workflow 強化(Week 3-5)

讓工程師用 V1 / V2 跟 Claude 寫程式時,自動產出規格更新
- V0 設定模式(專案啟動用)
- V1 規劃模式強化(必填計畫)
- V2 執行模式強化(必更新狀態 + 測試)
- 自動 commit 格式約定

**Phase B 結案標準:** 工程師試跑 1 週,反饋 friction 可接受,規格更新有對齊 schema

### Phase C — 規格審查 skill 強化(Week 6-7)

讓現有的 review skill 也對齊規範
- 既有的深度審查(spectra-review)強化
- 規格品質審查(V3)強化
- 跨組規格審查(V8)新增

**Phase C 結案標準:** 跑 1 次 cross-module review 試跑,結果可被 AI 助理消費

### Phase D — 其他 skill 強化(Week 8-9)

剩下的 V mode 全對齊規範
- V4 / V5 / V6 強化
- V7 模組切分 skill 新增

**Phase D 結案標準:** 全部 V mode 都對齊 schema

### Phase E — AI 專案助理實作(Week 10-12)

實作 PM Skill 本體
- 規格讀取分析
- 進度推導邏輯
- 階段審查機械化
- 5 個核心命令上線

**Phase E 結案標準:** PM Skill 跑 daily report + Phase Gate check 全部 work

### Phase F — 真實 Project 試跑(Week 13+)

對齊既有 Phase 1.5 訂閱開發專案,**用 PM Skill 真實管理**
- 工程師日常用 V1/V2
- PO 每日用 PM Skill 收 daily report
- 每週用 V8 cross-module review
- 階段切換用 Phase Gate check

**Phase F 結案標準:** PO 滿意度 ≥ 80%,工程師反饋友善

### 時程總覽

```
Week 1-2:    Phase A — 基礎建設
Week 3-5:    Phase B — 工程師 workflow 強化
Week 6-7:    Phase C — 規格審查強化
Week 8-9:    Phase D — 其他 skill 強化
Week 10-12:  Phase E — AI 專案助理實作
Week 13+:    Phase F — 真實 project 試跑

→ 3 個月完成完整架構建置
→ 之後維護成本極低(全 file-based)
```

### 漸進交付的彈性

**老闆如果對 12 週投入猶豫,可採「試水溫」版:**
- 只做 Phase A + Phase B + Phase E 局部(只實作 `/pm 進度報告` 命令)
- 估時 **4-6 週**
- 投入降到 1/3
- 在 1 個 small project 試跑驗證
- **驗證後再決定是否完整投入**

### 10.6 為什麼推薦對齊 Phase 1.5 訂閱開發試跑?

我們推薦把 PM Skill 試跑對齊「Phase 1.5 訂閱開發專案」(已有獨立提案計劃書)。理由:

**理由 1:時程契合**
- PM Skill 12 週開發 + 訂閱開發 Phase 1.5 預估 2-3 個月落地
- **PM Skill Phase F 試跑剛好對齊訂閱開發落地階段**
- 試跑不需另起 project,自然嵌入既有開發

**理由 2:複雜度適中**
- 訂閱開發涉及 5 個 module(訂閱核心 / 配額控制 / 推廣套餐 / 退費 / 取消下載)
- 需要 2-5 個工程師並行
- 跨 module 依賴明確
- **是試跑 PM Skill 的理想複雜度**(不會太小白費,也不會太大壓力過大)

**理由 3:設計已收斂**
- 訂閱方案已完成 100+ 輪 PO 親自確認 + 9 輪 spectra-review
- 規格穩定,**試跑時不會被「規格還在變」干擾**
- 可純粹測試 PM Skill 流程

**理由 4:商業價值雙重**
- 試跑成功 → 訂閱專案順利上線(直接商業價值)
- 試跑成功 → PM Skill 驗證 work(架構性價值)
- **一個專案兩個收穫**

### 10.7 失敗退路(Stop Loss Plan)

老闆會問:「萬一試跑失敗怎麼辦?會不會把訂閱專案也拖累?」

我們設計三層失敗退路:

#### 退路 1:任一階段不滿意,立刻停損

**設計:** 每個 Phase 結束 PO sign-off 才進下個 Phase。
**效果:** 任何階段 PO 認為「不值得繼續」 → 立刻停 → 已投入工時不超過該 Phase 估時。

```
Phase A 1-2 週:不滿意 → 停損,已投入 1-2 週
Phase B 2-3 週:不滿意 → 停損,已投入 3-5 週
Phase C 2 週:不滿意 → 停損,已投入 5-7 週
... 以此類推
```

**最壞情況:** 12 週 全做完才發現不適用 → 已投入 1 個工程師 3 個月 → 仍可挽救既有 V1-V6 SKILL.md 強化(不浪費)。

#### 退路 2:PM Skill 試跑失敗,訂閱專案無感

**設計:** 試跑 = PM Skill 在訂閱專案「並行運作」,**不取代既有人工 PM 管理**。
- PM Skill 跑出 daily report → PO 看完當參考
- 同時 PO 仍可以人工 ping 工程師、人工開會
- **若 PM Skill 跑出來的 report 不準 / 不 useful → 忽略它即可**

**效果:** 訂閱專案不會因為 PM Skill 試跑而 delay。**訂閱專案有自己獨立的時程跟管理機制,PM Skill 是「加分項」不是「依賴項」**。

#### 退路 3:架構層面 stop loss

**設計:** PM Skill 全部 file-based(markdown),**任何時候停掉,既有開發成果不流失**。
- 已寫的 schema files 變成「文件規範」仍可用
- 已強化的 V1-V6 SKILL.md 仍可繼續 work
- 已寫的 review template 仍可繼續用
- **不會有「技術債綁架」的情況**

**對比:** 如果採用 Jira / Linear 後想停 → 要 export 資料、重訓練工程師、消除工具依賴 — **成本遠高於本方案**。

#### 試跑成功的判定標準

對齊 §7.5 KPI:
- **效率指標達標** → 試跑成功 → 正式採用
- **效率指標部分達標** → iteration update → 再評估
- **效率指標未達標** → 啟動退路 → 停損

**這份提案的 KPI 鎖定後就是「驗收 vs 退路」的客觀標準,不靠主觀判斷**。

---

## 十一、結語

### 這份提案的核心 insight

**過去:** PM 花 70% 時間做「低 value 的進度催收」,30% 時間做「真正有價值的策略思考」。
**未來:** PM 花 5% 時間 review AI 助理產出的進度,**95% 時間做真正有價值的策略思考**。

這不是「機器人取代 PM」 — 而是「AI 助理把 PM 從瑣事中解放出來,讓 PM 發揮真正的價值」。

### 比喻

過去的 PM 像個 **手抄員** — 每天抄寫進度、抄寫日報、抄寫狀態。
未來的 PM 像個 **指揮家** — AI 助理打理樂譜,PM 專注指揮全局。

同樣的工資、同樣的工作時數,**產出價值差 5-10 倍**。

### 對團隊的承諾

我們透過這個 AI 專案助理,做出以下承諾:

- **對 PM:** 你每天 5 分鐘掌握全局,剩下時間做真正 PM 的工作
- **對工程師:** 你 0 額外負擔,只要照常用 Claude 寫程式
- **對組織:** 專案 delay 風險降低,規模化能力提升,科技形象升級
- **對未來:** 公司具備接 2-3 倍專案規模的能力,而不需線性堆 PM 人力

### 待 老闆 決策事項

請就以下 4 點答覆,確認啟動方向:

1. **是否授權啟動 Phase A(基礎建設)?**(時程 1-2 週,投入低)
2. **採完整 12 週投入,還是先做 4-6 週試水溫?**
3. **試跑專案選哪一個?**(推薦對齊既有 Phase 1.5 訂閱開發)
4. **誰擔任 Tech Lead 主導實作?**(建議公司內最熟 Claude SKILL 機制的工程師)

我們已 ready。設計收斂完成。剩下的,是 您一聲令下,我們就開始。

---

**附件參考:**

- 設計細節(技術版): 內部文件,可請 Tech Lead 提供
- 既有 SKILL.md 架構: `skills/` 目錄
- 既有 review template 樣本: [`docs/reviews/_TEMPLATE.md`](reviews/_TEMPLATE.md)
- 既有跨組 review 示範: [`docs/reviews/2026-06-17-round-1-cross-module-review.md`](reviews/2026-06-17-round-1-cross-module-review.md)

---

## 修訂歷程

| 版本 | 日期 | 變更 |
|:---:|:---|:---|
| 1.0 | 2026-06-17 | 初版,給決策者提案用(故事化、商業化、避免技術術語)|
| 1.1 | 2026-06-17 | 新增 §6.4 Skill Composition Contract — spectra-review 完整契約(F2 aggregate summary file / 7 大欄位 finding schema / Default vs Override 兩層架構 / `/pm-bug-review` feature spec / Governance Matrix / Fix Recommendation Algorithm);舊 §6.4/6.5 重編號為 §6.5/6.6 |
| 1.2 | 2026-06-17 | 新增 §6.4.10 Requirement Spec Artifact Contract(Phase 0 Exit Bar)— review process scaling / open issues cap / 8 條 machine-readability bar / 9 必填欄位 per-REQ schema / structural sanity / `/pm validate-req-spec` validator / downstream SKILL consumption mapping;同步更新 §6.3.2 Phase 0 acceptance criteria;舊 §6.4.10/6.4.11 重編號為 §6.4.11/6.4.12 |
| 1.3 | 2026-06-17 | 新增 §6.4.11 Phase 1-7 Artifact Contracts — Cross-Phase Lineage + 7 階段 artifact contracts(Phase 1 Module Plan / Phase 2 Per-Module Spec / Phase 3 Shared Infra / Phase 4 Implementation 含 spec↔code↔test 三向 invariant / Phase 5 Integration Test / Phase 6 Release 含 rollback rehearsal / Phase 7 Post-Launch 含 KPI + retro)+ Master Validator `/pm validate-all`;同步更新 §6.3.2 Phase 1-7 全部 acceptance criteria;舊 §6.4.11/6.4.12 重編號為 §6.4.12/6.4.13 |
| 1.4 | 2026-06-17 | spectra-review Round 1 fix(B1 + C1-C4 + N2 順手):§6.4.11.E.3a How to Enforce(對 6 條三向 invariant 加具體 check 命令 + "stale" 操作型定義);§6.4.10 §B.2 strengths.lower_bound 加 standard scaling 註記;§6.4.10 §L Contract Override Mechanism(7 段 — Artifact Contract trust hierarchy 擴展);§6.4.11 §B.2 加 `cross_cutting_reqs` field + structural_sanity rule;§6.4.10 §F 加 working draft scope clarification + `--working-draft-mode` flag。Round 2 verify verdict=ship-as-is。Review log:`docs/reviews/_summary-pm-skill-proposal-section-6-4.md`(2 rounds total,Net saving 20.3)|
| 1.5 | 2026-06-17 | spectra-review Round 3 polish(N1/N3/N4/N5):§6.4.11 §J.1 Validator Naming Convention(統一 singular + `--all` flag);§6.4 開頭加 self-version meta 註記(`contract-pack-v1`);§6.4.11 §A Cross-Phase Lineage 加 iteration loop(Phase 7 retrospective → next Phase 0)+ Phase 3 標籤改「shared code + integration guide」。Round 3 verify verdict=ship-as-is。3 輪 累積 fix_rate=100% / Net saving=21.6 |
| 1.6 | 2026-06-17 | spectra-review on PM Skill User Manual 觸發補強:§6.4.11 §E.4a Flaky Test Tolerance Policy(對應 user manual C2 fix)— 5 條件 mark flaky(retry_count_min 3 / pass_rate_min ≥ 0.66 / retry_mechanism / known_flaky_reason / po_acked)+ max_flaky_per_module ≤ 2 + max_flaky_total ≤ 5 + revisit_at 必填 + flaky vs hard fail 判定流程。**修補真實工作流 contract bypass 漏洞**(eat-own-dog-food 第 2 次驗證 unexpected synergy)|
| 1.7 | 2026-06-18 | **v1.2 Multi-Dev → Production Workflow 指令對齊**(PO 2026-06-18 拍板 3-stage promotion model 後落地):§6.4.11 §E.8 Multi-Dev Workflow Commands(`/pm setup-worktree` Phase 4 起始 + `/pm daily-sync` 每天 morning routine + `/pm push-gate` 復用 §E.3a 三向 invariant + git pre-push hook + Confidence Tier 表);§6.4.11 §F.6 `/pm advance-phase 5` Enhancement(auto merge dev/<project> → main + Phase 5 期間 hotfix policy);§6.4.11 §G.6 Deploy Commands(`/pm deploy --target prod` PO 拍板 + Azure CLI slot swap + audit-mandatory `--reason` + post-deploy smoke 自動 rollback fallback;`/pm rollback` zero-downtime swap-back + 24h root cause requirement;worktree cleanup on archive)。**6 命令全標 v1.2 Planned,等 PO 授權落地;對齊既有 trust hierarchy §6.4.4 + Stage Gate §6.5**。|
| 1.12 | 2026-06-19 | **SKILL Workflow Lifecycle — §6.4.15 新加**(對齊 PO 2026-06-19 第 7 個 architectural insight — eat-own-dog-food #18 dogfood test 後抓到「workflow document ≠ workflow validated」problem):4-stage lifecycle(Document-only / First-invoke tested / Validated / Production-ready)+ status marker `vX.Y-doc` / `-tested` / `-validated`;Stage transition 不可 silent(必走 decision-log + invocation evidence);降級可能(若 dogfood 暴露 critical bug);historical examples table(/pm init 等 v1.0 + /pm build-team v1.4-tested);Phase 6 release 紀律加 `/pm verify-runtime` 加 Layer 7 candidate(workflow lifecycle stage check)。對齊 spectra Round 3 C8 family of bugs + #18 dogfood discoveries。|
| 1.13 | 2026-06-20 | **SDLC v2 Contract — §6.4.16 新加**(對齊 PO 2026-06-20 architectural insight + HUMAN-FIRST docs):Phase 0/1/2 reorder — team-build 從 Phase 0 移到 Phase 1 Step 1.2(解雞生蛋:沒 split 怎知缺哪 role)。**Phase 0 v2:** bootstrap PM only invariant(`phase_0_carve_out: true` 對齊 §6.4.14)。**Phase 1 v2 EXPANDED 5-step:** 1.1 module split discussion + 新 deliverable `<project>-modules-overview.md`(HUMAN-FIRST 3-role 強制結構:📋 What it does / 👔 For PM / 🔬 For QA / 💻 For Developer,memory rule `feedback_human_first_docs`)/ 1.2 `/pm build-team`(現在才 enforce MVT)/ 1.3 ownership assignment / 1.4 functional spec per module / 1.5 design spec per module(complex 強制 / simple PO override skip)。**Phase 2 v2 LIGHTENED:** plan.md only(functional / design 已在 Phase 1 完成)+ solo carve-out。v1 §6.4.10 §B / §6.4.11 §B / §6.4.11 §C 保留 historical + grandfather(past Phase 2 signoff)。Migration:Phase 0/1 in-progress 必 adopt;backend-schema-auto-sync 已 rollback Phase 1→0 + re-advance under v2(對齊 dogfood #29-#36)。SKILL.md /pm advance-phase + /pm gate-check + /pm init workflows aligned to §6.4.16。|
| 1.14 | 2026-06-20 | **Mid-Phase Requirement Change Governance — §6.4.17 新加**(對齊 PO 2026-06-20 scenario:Phase 1+ developer 想 drop/add/modify REQ 但保留已完成 functional/design spec):**5 principles(PO explicit lock):** P1 NEVER automatic phase rollback(ONLY PM via `/pm advance-phase <N<current>` + CONFIRM ROLLBACK §K.8)/ P2 NEVER automatic module reorg(ONLY PM via `/pm requirement *` + PM sub-prompt placement)/ P3 minimum spec re-author(僅 affected modules)/ P4 audit trail mandatory(spec rev bump + decision-log + spectra --quick)/ P5 PM-driven module placement(no auto reorg)。**Cascade tier matrix(4 tier — 取消 Major rollback tier 對齊 P1):** 🟢 no-cascade(deferred drop / artifact-fit add)/ 🟡 patch(module 仍非 empty)/ 🟠 re-assign(PM 拍板:remove / merge / create new)/ 🔴 ~~rollback~~ N/A(PM 用 advance-phase 0)。**5-step workflow:** impact-analysis → PM placement decision → targeted spec re-author(P3 minimum)→ audit → spectra --quick。**Workflow commands aligned:** /pm requirement impact-analysis enhanced + 3 new(drop / add-mid-phase / modify)+ /pm spec-rev-bump + /pm advance-phase backward path。對齊 §6.4.13 minor change tier + §6.4.16 SDLC v2 Phase 1 cascade + §K.8 destructive phrase + memory `feedback_human_first_docs`(amendment 仍 keep 3-role structure)。|
| 1.15 | 2026-06-20 | **§6.4.17 Phase-aware + Cost-aware Tier(2 enhancements)**(對齊 PO 2026-06-20 enhancement request `both`,eat-own-dog-food #39 findings — `/pm requirement impact-analysis` 不該只 single-phase):**Phase-aware logic added** — Step 1 工作流改 read `state.md.current_phase` + for-each phase P ∈ [0..C] assess artifact impact + rework cost(`requirement-spec` Phase 0 / `modules-overview` / `functional spec` / `design spec` Phase 1 / `plan.md` Phase 2 / `shared infra` Phase 3 / `code + tests` Phase 4 / `integration` Phase 5 / `release artifacts` Phase 6 / `post-launch metrics` Phase 7)。**Cost-aware Tier 加 4th 🔴 major-rework tier**(Phase 4+ code already written:> 240 min;包含 refactor + tests + integration possibly deploy abort)。**4-tier matrix updated:** 🟢 no-cascade(< 15 min)/ 🟡 patch(< 60 min)/ 🟠 re-assign(60-240 min)/ 🔴 major-rework(> 240 min)。**Tier formula:** `Tier = max(cascade_scope_tier, rework_cost_tier)`。**Important:** 🔴 major-rework 不等於 phase rollback;PM 可選 (a) accept high cost current-phase apply,(b) `/pm advance-phase <N<current>` rollback + re-do from earlier(P1 explicit)。對齊 P5 PM-driven choice。SKILL.md v1.1.12 — `/pm requirement impact-analysis` Step 4 rewritten per spec rev 1.15。|
| 1.16 | 2026-06-20 | **§6.4.17 Specialized operations — 3 commands batch**(對齊 PO 2026-06-20 directive `Option B`,close Phase 1 真實 trigger gaps from coverage audit):**3 specialized commands added:** **`/pm requirement split <REQ-id> --into <new-id-list>`** — carve-out source REQ into N new REQs with PM acceptance criteria assignment + per-new-REQ module placement + CONFIRM SPLIT phrase + spec rev bump(Phase 1 後發現 REQ 太廣常用)。**`/pm requirement merge --reqs <id-list> --into <new-id>`** — consolidate N REQs into 1 with same-module precondition + PM field reconciliation(title/description/acceptance/dependencies/risk-max/effort-sum)+ CONFIRM MERGE + spec rev bump(發現 REQs 重複常用)。**`/pm requirement move <REQ-id> --from <module> --to <module>`** — non-destructive ownership transfer(REQ content unchanged)+ artifact-type compatibility warning + CONFIRM MOVE + NO spec rev bump(Phase 1 後發現 split 錯了常用)。**3 commands 都 align P3 minimum re-author + P4 audit mandatory + P5 PM-driven decision + spectra --quick re-run**。 SKILL.md v1.1.13 — close 3/8 specialized scenarios from coverage audit(剩 bulk / rename / restore / history / diff defer 至 dogfood findings)。|
| 1.17 | 2026-06-23 | **Worktree lifecycle expansion — Phase 3 entry trigger**(PO 2026-06-23 拍板 Option A,eat-own-dog-food #44 backend-schema-auto-sync Phase 4 done 時 PO 抓 PM Skill 設計矛盾):**Trigger phase shift:** `/pm setup-worktree` trigger Phase 4 entry → **Phase 3 entry**(`/pm advance-phase 3` auto trigger;原 advance-phase 4 trigger deprecated)。**Rationale:** Phase 3 shared infra(schema SSOT + 共用 helper)若 commit 進 main,project 沒 ship 就污染 main(orphan schema if Phase 4 abandoned)。PO 原始 "Phase 3 main is fine" 站不住 — engineer 從 worktree pull 跟從 main pull 沒差,唯一真實成本是 main 被半成品污染。改 Phase 3+4 同 worktree,Phase 5 才 merge,對齊 **main always-deployable invariant**。**Updates:** §E.8.1 architecture diagram 加 Phase 0-2 docs-only main + worktree open at Phase 3 entry + worktree spans Phase 3 + Phase 4;§E.8.2 trigger phase + state.md field `phase_3_started_at`(was `phase_4_started_at`)+ solo PO carve-out;§6.4.16 Phase 3 entry criteria + output documents 加 worktree note;Phase 4 entry criteria 改 "從 worktree pull"(was "從 main pull")。Migration policy:既有 active projects 維持原 main(`backend-schema-auto-sync` solo + 1-module + Phase 4 done 已 in main — 0 retrofit needed);future projects default rev 1.17。SKILL.md v1.1.14 — §Subcommand: setup-worktree trigger phase + v1.2 Architecture Premise diagram + state.md field + table row 4(起始) → 3(起始)。對齊 §6.4.13 minor change tier(commands lifecycle clarification,not new commands)+ memory `project_v2_backend_integration` deploy loop(bundle→templates 仍走 main → Azure;只是 worktree 是 dev → main 中間層)。|
| 1.17.3 | 2026-06-23 | **Worktree-Default Invariant + Mainline-as-Project**(PO 2026-06-23 insight — "把 mainline 變成 special project,routing 全靠 active-project.txt"):**Architectural shift:** Pre-rev-1.17.3 emergency hotfix needed special `--override-discipline` flag bypass mechanism;rev 1.17.3 改為 uniform model:**mainline 變成 reserved system project,switching active-project IS the routing mechanism + IS the audit**。**Core invariant(§E.8.8.1):** Active project resolves to commit target:`active=<project>` AND `dev/<project>` exists on GitHub origin → worktree;`active=<project>` AND no remote branch → mainline(自然 backwards-compat for pre-rev-1.17 projects);`active=mainline` → mainline。**Side effect:** No `migration_policy` flag needed;GitHub branch existence IS source of truth。**Mainline-as-Project framework(§E.8.8.2):** mainline = `system_special` type + `perpetual_maintenance` status + null worktree + no Phase 0-7 lifecycle;reserved name(`/pm init mainline` ABORT);8 forbidden commands(advance-phase / signoff / gate-check / setup-worktree / rollback / archive / restore / init mainline);6 allowed mainline-specific commands。**Project close → auto-switch mainline(§E.8.8.3):** `/pm archive <project>` 自動 update active-project.txt → "mainline"。**`/pm use mainline --reason "..."` mandatory(§E.8.8.4):** ≥ 30 chars reason + audit + idle timeout 60 min。**Visual warning(§E.8.8.5):** active=mainline 顯示 ⚠⚠ banner + duration tracker。**Push-gate check 10(§E.8.8.6):** active-project alignment verification(branch + CWD)。**Deprecate `--override-discipline`(§E.8.8.7):** 3-month migration period(2026-06-23 → 2026-09-23)both work;after 2026-09-23 only mainline-switch works。§K.8 + §K.9 amended:override frequency tracker becomes mainline cumulative duration tracker(< 30 min green / 30-120 min yellow / 120+ min red + freeze)。**`/pm whereami` v1.4 NEW command(§E.8.8.8):** read-only display(active project / expected CWD / actual CWD / aligned-or-mismatch)。**org-decision-log 自然解掉(§E.8.8.9):** belongs to mainline domain → 在 main → cross-project visible(no carve-out needed)。**Files changed:** proposal §E.8.8 new full subsection 10 sub-items;§E.8.7 Confidence Tier 加 `/pm use mainline` + `/pm whereami`;§K.8 + §K.9 amended(3-month grace);SKILL.md `/pm use mainline` special handling + `/pm archive` auto-switch + `/pm whereami` NEW + push-gate check 10 + forbidden mainline commands;NEW `docs/pm/mainline/state.md`(mainline state schema)。**Discipline philosophy shift:** From「explicit override + escape valve」→「uniform model + natural audit via project switching」。Engineer 認知負擔降低:always 「我現在 project 是?」 而非 「override 用嗎? bypass 嗎?」。對齊 PO 2026-06-23 insight:「mainline 是 special project,not a hack target」。|
| 1.17.2 | 2026-06-23 | **Worktree filesystem isolation — git worktree add + folder=project name**(PO 2026-06-23 拍板 Q-B Yes,follow-up to rev 1.17 architectural intent):**Mechanism shift:** Same-dir `git checkout -b dev/<project>` → filesystem-isolated `git worktree add ../<project> -b dev/<project>`。**Folder convention:** worktree dir name = project name(eg. `~/<repo>/` main + `~/<project-A>/` worktree A + `~/<project-B>/` worktree B 三個 directory 同層平行 active)。**Rationale:** Same-dir branch switching has wrong-branch commit risk(checkout 切錯 branch 在主 dir commit)+ 無法 multiple projects 同時 active(必須 stash/commit 才切)。`git worktree add` 每 project 自己一個 fully-checked-out 工作 directory(frontend + backend 完整 codebase + hardlink-shared .git objects,disk overhead ~1.0-1.2× per worktree)。**Q-B/A/C decisions(2026-06-23):** Q-B Yes apply spec amendment;Q-A Phase 5 staging Path A local gunicorn(no Azure staging WebApp cost);Q-C No retrofit for `backend-schema-auto-sync`(grandfather carve-out — Phase 4 done in main + Azure deploy 來源 main + retrofit force-push 風險高)。**Updates:** §E.8.2 behavior block 改 `git worktree add ../<project>` + verify `../<project>/` 不存在 precheck + onboarding hint「Switch CWD to ../<project>/ for Phase 3+4 development」+ state.md 加 `worktree_path` + `migration_policy` 兩 field;§E.8.1 architecture diagram 加 Filesystem Layout 圖(`~/AzureLineBOT-main/` main + `~/<project-A>/` worktree adjacent)+ Testing path(Path A local gunicorn + Path B optional Azure staging);§F.6 Phase 5 merge 加 `cd <main repo dir>` precondition + `git merge --abort` failure handling + worktree dir lifecycle(NOT removed at Phase 5,待 Phase 6 archive);§E.8.2 加 `grandfather_carve_out` block(既有 projects 維持 main + example=backend-schema-auto-sync)。SKILL.md v1.1.15 — setup-worktree workflow Step 4 改 `git worktree add` syntax + Phase 5 advance-phase dispatch 加 CWD switch。對齊 memory `project_v2_backend_integration`(deploy 來源仍是 main,worktree 是 dev-side intermediate)+ memory `azure_webapp_runtime`(Basic SKU + Linux 3.0 + Path A local sufficient for solo project)+ Path B Azure staging WebApp 加 optional(future Standard SKU 升級時 enable)。|
| 1.17.16 | 2026-06-26 | **Symmetric companion change for sanity-check rev 1.21 cascade(Phase 6)— 5th NEW `/pm sanity-tc-db-bootstrap` + 3 EXISTING upgrades for pm_tag identity / soft tombstone / --include-unavailable contract** per PO 2026-06-26 「6」 (Phase 6 authorize per sanity-check design spec § 10.5)。**Symmetric companion for sanity-check parent rev 1.21 cascade chain(commits 24b8c59 spec + 718560a audit-patch + 055b879 schema ALTER + 8839912 backend cmds + 4861f03 scripts modify + 04b738f scripts NEW)**:**5th NEW subcommand added(per parent rev 1.21 layer E 5th subcommand directive):** `/pm sanity-tc-db-bootstrap [--with-seed] [--reset --confirm-with "yes-reset-local-sanity-db"]` — local MySQL setup via SSOT execution;Azure substring refuse safeguard(exit code 2);literal phrase --reset destructive guard(exit code 3);--with-seed chains to /pm sanity-tc-regenerate --auto-detect --force for 16-TC initial backfill;Confidence 🟢 high(schema is read-only SSOT,backfill via existing regenerate path);implementation `scripts/sanity_tc_db_bootstrap.py` Phase 5 landed commit 04b738f。**3 EXISTING subcommands UPGRADED to rev 1.21 cascade:**(1)`/pm sanity-tc-regenerate` — git diff `--name-status` A/M/D/R CRUD branch + pm_tag content-addressable identity + auto-gen pm_tag + write-back to MD frontmatter + D path走 `mark_sanity_tc_unavailable` soft tombstone(NOT physical DELETE)+ Round 1 B1 closure(Claude MUST NOT output pm_tag,orchestrator passes as sibling body field);CLI 加 --auto-detect / --dry-run flags;(2)`/pm sanity-tc-validate` — 加 pm_tag format regex check(`^[a-z2-7]{8}$`)+ cross-ref uniqueness(pm_tag / legacy_id / id collision detection)+ --check-drift flag for snapshot drift;Phase 5 `scripts/sanity_tc_validate.py` landed;(3)`/pm sanity-tc-coverage` — 加 --page JSON path filter(Option A YAGNI per parent rev 1.21 Q1=A 拍板)+ --include-unavailable admin flag(per Round 1 C3 body field contract)+ --format json(machine-readable)+ tombstoned admin view section;Phase 5 `scripts/sanity_tc_coverage.py` landed。**1 EXISTING subcommand UNCHANGED but clarified:** `/pm sanity-tc-prune` — Round 1+2 audit-patch NIT clarification:此 is admin **hard-delete escape hatch**,distinct from regenerate D path soft tombstone via `mark_sanity_tc_unavailable`;error_code 分離(`'literal_phrase_mismatch'` / `'not_found'` / `'fk_restricted'` for future REQ-021 Sanity_Test_Result_TBL FK 反擋);Confidence 🔴 low(destructive — literal phrase + FK RESTRICT 雙層 safety per `[[delete-dialog-no-undo-hint]]`)。**Subcommand Router updates:** 4 existing rows updated(rev 1.17.15 → 1.17.16 UPGRADE)+ 1 NEW row(sanity-tc-db-bootstrap)。**Cross-tool integration:** sanity-check rev 1.21 = first-class TC Lifecycle Workflow SSOT(NEW REQ-020)+ pm_tag identity invariant + soft tombstone for future Sanity_Test_Result_TBL FK(REQ-021 stub);PM Skill rev 1.17.16 = operational SSOT for `/pm sanity-tc-*` 5 subcommand family。**Phase 6 phase ordering reminder(per sanity-check design spec § 10.5):** Phase 1 spec cascade ✅ / Phase 2 schema ALTER ✅(055b879) / Phase 3 backend cmds ✅(8839912) / Phase 4 scripts modify ✅(4861f03) / Phase 5 NEW scripts ✅(04b738f) / Phase 6 PM Skill router(this rev) ✅ / Phase 7 end-to-end run on local MySQL + 16 TC backfill validation ⏸ AWAITING。**Files changed:** proposal.md(this entry);SKILL.md(Subcommand Router 5 rows updates + 4 existing `## Subcommand: sanity-tc-*` workflow sections upgrade + 1 NEW `## Subcommand: sanity-tc-db-bootstrap` workflow section)。**Eat-own-dog-food meta-iteration #61:** sanity-check rev 1.21 cascade(7 commits 24b8c59 → 04b738f)co-evolved with PM Skill rev 1.17.16 — "specs co-rev pattern" maintained across 8th major sanity rev(rev 1.19 → 1.20 audit → 1.21 cascade → 0.2.1 audit-patch on PoCs)。**對齊** `[[delete-dialog-no-undo-hint]]` literal phrase confirmation(`yes-reset-local-sanity-db` for --reset / `yes-prune-tc-<id>` for prune)+ `[[backend-change-rule]]` propose-first(Phase 2-5 all PO authorize cleared per design spec § 10.5)+ `[[backend-schema-change-workflow]]` SSOTs plural(sanity only,laundry unaffected)+ `[[dep-management]]` stdlib-only(0 入 requirements.txt)+ `[[human-first-docs]]` 3-role MD source + `[[user-working-style]]` real device + low cognitive load(auto-gen pm_tag = 0 PM cognitive load per parent rev 1.21 Q2 拍板)。|
| 1.17.15 | 2026-06-26 | **Symmetric companion change for sanity-check requirement-spec rev 1.19(Phase 5)— 4 NEW PM Skill subcommands for MD source → DB cache → runtime loader workflow** per PO 2026-06-26 5-phase split directive(rev 1.19 Phase 5)。**4 NEW subcommands added(對齊 sanity-check rev 1.19 architecture):**(1)`/pm sanity-tc-regenerate <md-file-or-tc-id> [--force]` — git diff detect + Claude REQ-019 22-field extract + backend cmd `update_sanity_tc_definition` REMOVE + INSERT atomic + auto-export `generated/<tc>.json` snapshot;Confidence 🟡 medium(Claude extraction layer)。(2)`/pm sanity-tc-validate [<md-file>] [--all]` — dry-run REQ-019 schema check + cross-ref validation(dependencies tc_id real / legacy_id uniqueness / category × ID range consistency)+ drift detection vs DB;non-destructive;Confidence 🟢 high。(3)`/pm sanity-tc-prune <tc-id> --confirm-with "yes-prune-tc-<id>"` — orphan TC delete with literal phrase per [[delete-dialog-no-undo-hint]] 慎思 invariant;backend cmd `delete_sanity_tc_definition`;Confidence 🔴 low(destructive)。(4)`/pm sanity-tc-coverage [--diff] [--category <C>] [--format markdown|table]` — category × operation × intent × scenario matrix report;7-category × 7-operation = 49 cell coverage;gap detection(eg.「Auth 缺 negative variant」);3-role meeting prep use case;Confidence 🟢 high。**Subcommand Router updates:** 4 new rows added after `/pm sanity-reset-db`(rev 1.17.13)。**Cross-tool integration:** sanity-check rev 1.19 Phase 5(PM Skill subcommands)= last phase of 5-phase split per PO Q4=A;Phase 1 spec rev 1.19(commit a8d37ca)+ Phase 2 backend infrastructure(commits b9a6802 + 97f78b4 — 6 files + 4 cmds)+ Phase 3 loader rewrite(commit 2b4cfe9)+ Phase 4 migration script + 16 MD stubs + seed SQL(commit 9a1fb31)+ Phase 5 PM Skill subcommands(this commit)。**Files changed:** proposal.md(this entry);SKILL.md(Subcommand Router 4 new rows + 4 NEW `## Subcommand: sanity-tc-*` workflow sections)。**Eat-own-dog-food meta-iteration #60:** Sanity rev 1.18 → 1.19 architectural shift(MD source → DB cache → runtime loader)triggered 5-phase implementation;PM Skill rev 1.17.15 closes the loop by providing subcommands that operate the new architecture。**對齊** `[[delete-dialog-no-undo-hint]]` literal phrase confirmation(`/pm sanity-tc-prune` `yes-prune-tc-<id>`)+ `[[backend-change-rule]]` propose-first(rev 1.19 Phase 2 cmds already authorized + implemented)+ `[[human-first-docs]]` 3-role MD source pattern(natural language refined by PM/QA/Dev/Claude)+ `[[user-working-style]]` real device + low cognitive load(Claude burden + human SSOT in MD)。|
| 1.17.13 | 2026-06-25 | **Symmetric companion change for sanity-check requirement-spec rev 1.11(co-rev with `docs/pm/sanity-check/spec/sanity-check-requirement-spec.md` rev 1.10 REQ-018 + rev 1.11 Round 7-patch)**:PO 2026-06-25 night directive 「PM Skill 也要對稱的加」— sanity-check spec rev 1.10 加 REQ-018 Separate sanity DB(`sanity_check_DB` 隔離)+ rev 1.11 Round 7-patch close hub-issue cascade pattern 第 3 次 recurrence(B1 inline footnote + B2 routing list completeness + C1 bootstrap user + C2 PROD reject + C3 DB scope clarity + N1 cross-link map + N3 glossary)。PM Skill 對應 add 3 things 對齊新 architecture。**1 NEW subcommand added(對齊 sanity-check REQ-018 C.2):** `/pm sanity-reset-db <project> --confirm-with "yes-reset-database"` — implements REQ-018 C.2 full DB-level reset for catastrophic recovery / dev clean slate;**DESTRUCTIVE — PROD reject + literal phrase + pre-archive 3 layer safety net**;8-step workflow:(1)resolve project audit context label;(2)environment gate — PROD env reject `"PROD env sanity-reset-db forbidden per REQ-018 B.3 — manual DB ops only for prod"` + structured log `event=sanity_reset_rejected_prod`;若 `SANITY_DB_NAME` 空 → abort with `"sanity DB not initialized — nothing to reset"`;(3)confirmation gate — exact `--confirm-with "yes-reset-database"` literal match per `[[delete-dialog-no-undo-hint]]`(case-sensitive);(4)pre-reset audit snapshot — export `Sanity_Lifecycle_Audit_TBL` → `docs/pm/_archive/sanity-audit/full-reset-<timestamp>.sql.gz` per REQ-018 D.3 option b cascade(若 export fail → abort,no drop — atomicity invariant);(5)drop + recreate `sanity_check_DB` 用 bootstrap user(`SANITY_DB_BOOTSTRAP_USER` + `SANITY_DB_BOOTSTRAP_PASSWORD` per REQ-018 A.3 + rev 1.11 C1 fix)+ re-grant `sanity_db_user` per A.6 least privilege;(6)auto-sync schema 用 `schema_sync.py --target sanity` 觸發 + verify `_schema_sync_log_sanity` populated;(7)audit row write — `Sanity_Lifecycle_Audit_TBL` row `action='full-db-reset'` + `executed_by='pm-skill-caller:<user>'` per REQ-017 G.5 normative format + `pre_reset_audit_archive='<path>'`;(8)report sanity_check_DB reset complete + path + schema rev + suggest `/pm sanity-status <project> --schema-version` verify。Confidence Tier 🔴 low(destructive DB-level op)。**2 EXTEND existing subcommands:** (1)`/pm sanity-status` 加 `--schema-version` flag per REQ-018 D.1 — query `sanity_check_DB._schema_sync_log_sanity` ORDER BY synced_at DESC LIMIT 1 → return latest applied sanity schema rev string(eg. `v1.0` = REQ-013/014/015 baseline / `v1.1` = REQ-017 eruda capture / `v1.2` = future REQ-018+);render `Current sanity schema rev: <rev>;eruda capture <active|inactive>;eruda_log_wiped_at column <present|absent>;applied at <synced_at>`;return early after schema-version output(不跑 Step 3-8 aggregation queries — 不同 use case)。(2)`/pm sanity-status` Step 2 Layer 2 direct DB path 明示 connect **`sanity_check_DB`**(via `SANITY_DB_HOST/PORT/USER/PASSWORD/NAME` ENV vars per REQ-018 B.4)— **不再隱含連 `laundry_DB`**(防誤連 production 資料,對齊 REQ-018 A.1 isolation invariant + R-NEW-DB-3 mitigation;auth = OS-level DB credentials of `sanity_db_user` per A.6 least privilege)。**Subcommand Router updates(SKILL.md §Subcommand Router):** 1 new row(`/pm sanity-reset-db <project> --confirm-with "yes-reset-database"` ⭐ v1.4 rev 1.17.13 NEW)+ existing `/pm sanity-status` row update 加 `[--schema-version]` flag。**SSOT scope update(rev 1.17.13 supersedes rev 1.17.12 mention):** rev 1.17.12 對齊 `[[backend_schema_change_workflow]]` SSOT 寫 `laundry_db_create_tables.sql 加 2 tables + 1 column` — **此 SSOT scope per sanity-check REQ-018 A.2 已 supersede 為 plural SSOTs**:`laundry_db_create_tables.sql`(business)+ **NEW** `sanity_db_create_tables.sql`(sanity tooling)+ auto-sync rev 1.1 對 2 SSOTs 各自 sync 到對應 DB(`laundry_DB` + `sanity_check_DB`)。Memory rule update 候選 — `[[backend-schema-change-workflow]]` 加 plural SSOTs + cascade-audit acceptance item invariant 防 Round 8 hub-issue recurrence。**Per `[[backend_change_rule]]`:** 新 subcommand 觸 backend handler 需 propose-first:(1)backend startup auto-create `sanity_check_DB` + auto-sync logic per REQ-018 A.3;(2)`sanity_*` cmd routing convention dispatcher logic per A.5;(3)4 cmd handlers + 6 query cmd handlers + `--seed-fixtures` flag per C.1;(4)bootstrap user `sanity_db_admin` GRANT statements per A.6 + rev 1.11 C1;(5)PROD env stray cmd 503 reject + structured log per rev 1.11 C2。PM Skill cmd dispatch itself 是 SKILL.md edits = direct-to-main。**Files changed:** proposal.md(this entry);SKILL.md(Subcommand Router 1 new row + 1 update row + NEW `## Subcommand: sanity-reset-db` workflow section + `## Subcommand: sanity-status` rev 1.17.13 update 加 `--schema-version` flag + Step 2 Layer 2 ENV vars 明示 `sanity_check_DB`);docs/pm/sanity-check/spec/sanity-check-requirement-spec.md(rev 1.10 + 1.11 symmetric companion change reference)。**Cross-tool integration matrix update(rev 1.17.13 cascade — extends rev 1.17.12 inline matrix):** sanity-check REQ-018 ↔ PM Skill cmd ownership map: REQ-018 A.1+A.5 routing(backend ConnectionManager via `sanity_*` prefix)/ REQ-018 C.2 reset(`/pm sanity-reset-db`)/ REQ-018 D.1 schema version track(`/pm sanity-status --schema-version`)/ REQ-018 D.3 archive audit tradeoff(pre-reset audit snapshot in `/pm sanity-reset-db` Step 4)。**Eat-own-dog-food meta-iteration #59:** sanity-check spec rev 1.10 hub-issue REQ-018 (1 round Round 7 cascade pattern recurrence catch + 8 findings closed) co-evolved with PM Skill spec rev 1.17.13 — Round 7 lesson learned 「hub-REQ 改 SSOT scope → cascade audit 必 grep inline footnote 不只 NF macro」內化進 PM Skill cross-tool integration matrix invariant。**對齊** `[[delete-dialog-no-undo-hint]]` literal phrase confirmation(`"yes-reset-database"` 比 `"yes-cleanup"` 更嚴格 — DB-level reset 非 row-level wipe)+ `[[backend-change-rule]]` propose-first(bootstrap user GRANT + 5 backend logic items)+ `[[backend-schema-change-workflow]]` SSOTs plural(REQ-018 A.2 cascade)+ `[[public-vs-private-friend-data]]` PII boundary(sanity_check_DB 隔離 production PII per REQ-018 6 dimension privacy boundary)+ `[[user-working-style]]` real-device(PROD 不跑 sanity per REQ-018 B.3 PROD skip)+ sanity-check REQ-018 全 sub-flows A/B/C/D + R-NEW-DB-1~5 risks。|
| 1.17.12 | 2026-06-25 | **Symmetric companion change for sanity-check requirement-spec rev 1.9(co-rev with `docs/pm/sanity-check/spec/sanity-check-requirement-spec.md` rev 1.9-Round-6-patch — 10 revs + 6 spectra rounds + 47 findings all closed)**:PO 2026-06-25 evening directive 「PM skill 也要對稱的加」— sanity-check spec 定 'what' / PM Skill spec 定 'how' / 互引但不重複。**Architectural ownership boundary:** sanity-check REQ-017 G.1 = SSOT for **what** lifecycle wipe behavior;PM Skill spec rev 1.17.12 = SSOT for **how** PM Skill cmd dispatch / user prompts / output format / error handling。**4 NEW subcommands added(對齊 sanity-check REQ-013/014/015/017 G.1+G.6):** (1)`/pm sanity-status <project> [--tc=<id>] [--since=<date>] [--diff=<a>..<b>]` — implements sanity REQ-015 multi-QA aggregation visualization(per-TC table + reproducibility class consistent/frequent/flaky/rare/no-bug + device/QA breakdown + fail_reason cluster + cross-commit regression detection);auth via 2-layer access(Layer 1 backend cmd `query_sanity_test_results` + Layer 2 direct DB when same-machine ENV `SANITY_DB_LOCAL_OVERRIDE=1`);N<10 KPI ethical guard UI hiding。(2)`/pm sanity-submit-result <project> <csv-or-json>` — implements sanity REQ-014 manual fallback import — `result_id` INSERT IGNORE + `idempotency_token` UNIQUE + DEFAULT(uuid())fallback;CSV schema match `Sanity_Test_Result_TBL` 22-column(rev 1.8 B-new-1 fix 後對齊);per-row `submit_method='manual'`;security gate per-project secret key + IP allow-list。(3)`/pm sanity-cleanup-logs <project>` — implements sanity REQ-017 G.1 explicit log cleanup — count + bytes estimate prompt → literal 'yes-cleanup' confirm per `[[delete_dialog_no_undo_hint]]` → optional pre-wipe export choice → chunked DELETE(1000 rows / 100ms sleep)→ `Sanity_Lifecycle_Audit_TBL` audit row(`executed_by='pm-skill-caller:<user>'` per REQ-017 G.5 normative format)→ report rows wiped + bytes freed + audit_id。(4)`/pm sanity-export-logs <project> [--output=<path>] [--qa-identifier=<id>] [--then-wipe]` — implements sanity REQ-017 G.6 pre-wipe export — default output `docs/pm/<project>/sanity-archive/<timestamp>-eruda-logs.tar.gz`(`.gitignore` 預設 exclude;`sanity-runs/` vs `sanity-archive/` directory functional 區隔 per rev 1.8 N-new-17 fix);pre-export 二次 PII scrub(同 client + backend 7-regex set,defense in depth = redundancy not extension per rev 1.8 C-new-8);`--then-wipe` 3-step transactional atomicity per REQ-017 G.6(Step 1 SHA-256 verify + Step 2 transaction wipe + Step 3 audit row;失敗 rollback workflow per OQ-14)。**3 EXTEND existing subcommands:** (5)`/pm archive <project>` workflow 加 sanity eruda log auto-wipe step(rev 1.17.3 §E.8.8.3 既有 auto-switch mainline 之後加 sanity cleanup):invoke `query Sanity_Eruda_Log_TBL by project` → 若 count > 0 ⇒ no-prompt chunked DELETE(archive = decision finalized,對齊 `[[delete_dialog_no_undo_hint]]` archive ≠ soft delete invariant)→ `Sanity_Lifecycle_Audit_TBL` audit row `action='archive'`;若 count = 0 ⇒ skip no-op。(6)`/pm restore <project>`(rev 1.17.x close-then-reopen workflow)加 eruda wipe warning step:query `Sanity_Test_Result_TBL.eruda_log_wiped_at IS NOT NULL` → 若有 wipe history ⇒ display warning「eruda logs prior to <archive_date> were wiped during /pm archive。New sanity runs will capture fresh logs;historical logs unrecoverable unless export was taken per /pm sanity-export-logs」;**不 reverse** — 對齊 `[[delete_dialog_no_undo_hint]]` 慎思 invariant。**Note(rev 1.17.12 Round 1-patch C-pm-2 fix):** 「close」概念由 `/pm archive` 涵蓋 per rev 1.17.3 §E.8.8.3(archive = close-with-finalized-decision + auto-switch mainline);**no separate `/pm close` cmd needed**;export option prompt 在 `/pm sanity-cleanup-logs` Step 4 already provided(per REQ-017 G.1 explicit cleanup path)。**Subcommand Router updates(SKILL.md §Subcommand Router):** 4 new rows(sanity-cleanup-logs / sanity-export-logs / sanity-status / sanity-submit-result)+ 2 extend annotation(/pm archive Step 9 + /pm restore Step 7)。**Cross-tool integration matrix(rev 1.17.12 Round 1-patch C-pm-3 fix:inline 在本 rev entry 內,future spec maintenance 可 promote 為 §6.4.18 dedicated section;防 cross-spec drift per sanity-check R-NEW-I + OQ-12):** sanity-check REQ ↔ PM Skill cmd ownership map: REQ-013 backend submit(無 PM Skill cmd — LIFF realtime path)/ REQ-014 manual fallback(`/pm sanity-submit-result`)/ REQ-015 query+aggregation(`/pm sanity-status`)/ REQ-017 G.1 explicit cleanup(`/pm sanity-cleanup-logs`)/ REQ-017 G.1 archive auto-wipe(`/pm archive` Step 9)/ REQ-017 G.4 restore warning(`/pm restore` Step 7)/ REQ-017 G.6 export(`/pm sanity-export-logs`)。**Invariant:** sanity REQ change 時必同期 PM Skill rev;commit hook(future)check cross-reference validity per sanity OQ-12 design spec defer。**Ownership boundary:** sanity-check spec = SSOT 'what' / PM Skill spec = SSOT 'how' — 互引但不重複。**Per `[[backend_change_rule]]`:** 4 NEW subcommands 觸 backend handler 需 propose-first(`submit_sanity_test_result_bulk` + `query_sanity_test_results` + `query_qa_activity` + `query_tc_reproducibility` + cmd `cleanup_sanity_eruda_logs` + `export_sanity_eruda_logs`);PM Skill cmd dispatch itself 是 SKILL.md edits + Python skill helpers = direct-to-main。**Files changed:** proposal.md(this entry + NEW §6.4.18 cross-tool integration matrix);SKILL.md(Subcommand Router 4 rows + 4 NEW `## Subcommand: ...` workflow sections + extend `/pm archive` + `/pm restore`);docs/pm/sanity-check/spec/sanity-check-requirement-spec.md(symmetric companion change reference)。**Eat-own-dog-food meta-iteration #58:** sanity-check spec rev 1.0→1.9 (10 revs + 6 spectra rounds + 47 findings) co-evolved with PM Skill spec rev 1.17.12 = "specs co-rev pattern" — 跨 tool spec 同 session 同步 rev,commit message 註明 co-rev,防 spec drift。**對齊** `[[delete_dialog_no_undo_hint]]` wipe 慎思 invariant(archive 無 prompt,sanity-cleanup-logs 顯式 'yes-cleanup')+ `[[backend_change_rule]]` propose-first(backend handlers)+ `[[backend_schema_change_workflow]]` SSOT laundry_db_create_tables.sql 加 2 tables + 1 column(per sanity REQ-013/017)+ `[[public_vs_private_friend_data]]` PII scrub 7-regex + 2-layer defense + `[[user_working_style]]` real-device + low cognitive load + Traditional Chinese friendly + sanity-check REQ-013/014/015/017 G.1+G.6 cross-link map。|
| 1.17.11 | 2026-06-24 | **Sanity-Check-Discovered Bug Fix Direct-to-Main Rule(PO 2026-06-24 directive during Pilot v0 first dogfood)**:PO 在 first real `/pm sanity-check` execution(rev 1.17.10 framework dogfood)期間 surfaced 多個 V2/V1 SPA bugs(QR code on home page shaking continuously due to V2 `__repaintSoon` repaint loop fired by iOS Safari visibility events escaping 300ms guard;banner padding-top !important visibility-event loop;top menu hidden by overlay banner;toolbar covering V3 SPA bottom nav)。PO crystallized 一條 streamlined workflow rule:**sanity-check-discovered bugs that are reproduced + fixed within the SAME session shall be applied DIRECTLY to mainline source(`templates/*.html` / frontend assets — NOT *.py per `[[backend_change_rule]]`)without going through separate PM Skill Phase 1-6 project ceremony**。**Both-side compliance invariant:** Apply fix to MAINLINE source(production code)AND apply same fix IN PARALLEL to the active worktree(so ongoing dogfood can continue verified)。Both sides must reflect the fix atomically before dogfood completion。**Workflow:**(1)Bug discovered + reproduced during `/pm sanity-check`;(2)Fix designed + applied to worktree first(verify it works);(3)Once verified,port to mainline source files;(4)Continue/finish dogfood with both sides reflecting fix;(5)Commit mainline changes to main with `fix:` prefix message + descriptive body;(6)Append decision-log entry `D-<project>-sanity-fix-<finding-slug>`;(7)Reference fix commit in `state.md.phase_6_pre_deploy_sanity_check.runs[]` entry。**Exclusions:** *.py changes still require propose-first per `[[backend_change_rule]]`(strict);findings requiring architectural redesign(not surface bug)still go through Phase 1-6;beyond-same-session findings(QA continues outside dogfood window)follow normal cycle。**Rationale:** Sanity-discovered bugs are already verified real by user execution → high-confidence fix path;PM Skill Phase 1-6 ceremony optimized for new features but heavyweight for surface bugs;speed matters during eat-own-dog-food validation;"fix both sides" preserves worktree-mainline parity invariant for active dogfood。**Applied immediately to current QR shake finding:**(a)Production fix in `templates/index.html` lines ~5693-5699 — added `needsRepaintHack()` device detection(only Android Sony/Samsung WebView need V2 `__repaintSoon` repaint hack;iOS Safari + modern Android skip);(b)Mirror same edit to `templates/index_sanity_check.html`(SSOT for sanity overlay);(c)Mirror to worktree's index_sanity_check.html + index.html;(d)Remove temporary monkey-patch `disableV2RepaintLoop()` from sanity overlay(no longer needed — production code now correct);(e)Commit to main with `fix:` prefix。**Files changed:** proposal.md(this entry);SKILL.md `/pm sanity-check` workflow Step 11.5 mid-dogfood bug fix branch;NEW memory `feedback_sanity_check_bug_fix_direct_main.md` + MEMORY.md index;`templates/index.html` + `templates/index_sanity_check.html` V2 `__repaintSoon` device-detect fix;`_org/org-decision-log.md` D-pm-skill-rev-1-17-11-sanity-bug-fix-direct-main-rule-001 + D-backend-schema-auto-sync-sanity-fix-qr-shake-001。**Eat-own-dog-food meta-iteration:** rev 1.17.10 framework's first dogfood surfaced real production bug → rev 1.17.11 codifies the fix-direct-to-main workflow → applied immediately to same bug → rule becomes self-validating within same session。**對齊** `[[backend_change_rule]]`(maintains strict propose-first for *.py;new rule scoped to frontend assets only)+ `[[user_working_style]]` real-device testing + `[[android_webview_render_bug]]`(V2 repaint hack preserved for Android Sony/Samsung,disabled on iOS where the bug doesn't apply)+ `[[project_v2_backend_integration]]` deploy chain(fix lands in templates/ → next deploy pushes to Azure)。|
| 1.17.10 | 2026-06-24 | **Pilot v0 Sanity Test Runner concrete impl + `/pm sanity-check` new subcommand(rev 1.17.9 Layer 4 framework → concrete artifact)**:PO 2026-06-24 ⭐ pivoted from rev 1.17.9 original "~485 LoC across 4 files including 2 *.py changes" architecture to a **0 backend *.py change** design,fully respecting `[[backend_change_rule]]` propose-first discipline。**Architectural pivot:** Original rev 1.17.9 sketch had `app.py` + `python_mysql_connect_template.py` gated dispatch entry — but propose-first surfaced that python_mysql_connect_template.py is a DB helper library not Flask routes;real route entry lives in `app.py:20801`。PO re-architected to:**copy index.html → index_sanity_check.html with overlay injection;swap-in via worktree at /pm sanity-check trigger;0 backend touch**。**Multi-round design refinement(PO 2026-06-24)**:Round 1(propose-first):scope correction halt — flagged actual file is `app.py` not `python_mysql_connect_template.py`,PO chose 0-backend path instead;Round 2(0-backend overlay):copy index.html base + inject ⚠ banner + 🧪 button + dispatcher overlay at top of `<body>`;Round 3(safety):worktree-pattern swap so mainline index.html 物理 untouched + ⚠ SANITY TEST BUILD banner permanent visible prevents QA forgetting;Round 4(test case externalization):separate SSOT file `templates/sanity_test_cases.js` with 13-field schema(7 required + 6 optional)(⚠ rev 1.17.10 Round 1 spectra-review C1 + Round 2 B1 closure annotation:"13/7+6" was count error at design time;actual schema at initial build was 14/8+6;Round 1 B1 closure further evolved to 14/7+7 — `target_url` moved R→O — see "14-field schema design" para at end of this entry for final state)+ JSDoc-style comments → PM/QA/RD/Claude chat-discuss to add/refine cases without touching dispatcher。**Pilot v0 build artifacts(6 files,0 *.py change):** (1)`templates/index_sanity_check.html` — copy of 34596-line production `templates/index.html` with overlay injection at body open(banner + button + dispatcher panel + filter UI + CSV download)~250 LoC overlay added on top of existing page;(2)`templates/sanity_test_cases.js` SSOT — 13-field schema + 8 starter cases covering BCT/Profile/Schedule/Friend/OCR/Auth categories + reusable FAKE_*PERSONA constants + runtime schema validator + skip block template ~400 LoC(⚠ rev 1.17.10 Round 1 C1 + Round 1 B1 closure annotation:final state is 14-field schema 7+7 + **10 starter cases**(TC-001~008 in-SPA + TC-009 BCT URL deep link receiver_bizcard + TC-010 Schedule URL deep link receiver_schedule)~530 LoC + dispatcher conditional Jump button render based on target_url presence;Round 2 verify further fixed TC-009/TC-010 purpose constant typos against actual `system_lib.py:252/253` values + removed leading `/` from target_url to avoid Flask 308 redirect);(3)`cleanup_sanity_fake_data.sql` — pre-check counts + commented DELETEs(QA reviews before enabling)+ post-check verification queries against Business_Card_TBL / Received_Bizcard_TBL / Booking_TBL / BOT_User_Connection_TBL by `TEST_FAKE_%` prefix LIKE match;(4)SKILL.md new `## Subcommand: sanity-check` workflow 14 steps(worktree open → file swap → backend boot → QA real-device LIFF login → CSV result capture → state.md append → cleanup → worktree discard)+ carve-out path + output contract + audit trail convention;(5)proposal.md this Revision History entry rev 1.17.10;(6)backend-schema-auto-sync state.md `phase_6_pilot_v0_design` audit block。**14-field schema design(rev 1.17.10 Round 1 evolution):** Original build had Required 8 + Optional 6 = 14。**Round 1 spectra-review B1 closure 2026-06-24:** `target_url` moved REQUIRED → OPTIONAL because `index.html` IS the V3 SPA — most QA cases are in-SPA navigation(QA taps SPA's own UI),no URL Jump needed。Final schema:**Required 7 = id / category / priority / description / fake_data / expected_visuals / pass_fail_criteria;Optional 7 = target_url(⭐ B1 closure)/ tags / owner / last_reviewed / related_feature / skip / dependencies**。`target_url` retained as optional only for URL-driven deep link scenarios(LINE msg tap → LIFF query-param dispatch via hello_world_app;see TC-009 + TC-010 starter cases as concrete examples)。Dispatcher conditionally renders "→ Jump (deep link)" button when target_url present,else "📍 navigate manually in SPA" hint。**Categories enum:** BCT / Profile / Schedule / Friend / OCR / Coupon / Auth。**Priorities enum:** P0(block deploy)/ P1(review with PO)/ P2(track only)。**Discussion workflow:** PM/QA/RD propose case via chat → Claude drafts using Edit tool → trio reviews → PO拍板 commit。**Skip mechanism:** `skip: { reason, until_date }` instead of delete — keeps audit trail。**Schema runtime validator:** `validateSanityCases(cases, spec)` called at dispatcher load,surfaces drift early。**LIFF auth design:** QA real LINE account login(not bypassed)— inherits real LINE OAuth + cross-service Blob/GCP/Gemini AI via backend's own dev credentials;multi-device pool feasibility for Pilot v1(10 phones × 10 different LINE accounts)。**Result capture path:** localStorage `__sanity_results` accumulator → CSV blob download → manual upload to `docs/pm/<project>/sanity-runs/<run_id>.csv` → state.md append。**PASS/FAIL/SKIP/NOT_RUN 4-state convention** — skip ≠ pass, ≠ fail,prevents假 PASS。**Eat-own-dog-food meta-iteration #57:** rev 1.17.9 spec framework → rev 1.17.10 concrete artifact within same session continues §6.4.15 SKILL Workflow Lifecycle Document-only → First-invoke pattern。propose-first re-architecture(scope correction halt + 0-backend pivot)demonstrates `[[backend_change_rule]]` actively shaping design decisions。**Files changed:** proposal.md(this entry);SKILL.md `## Subcommand: sanity-check` new section + router table row;NEW `templates/index_sanity_check.html`;NEW `templates/sanity_test_cases.js`;NEW `cleanup_sanity_fake_data.sql`;`docs/pm/backend-schema-auto-sync/state.md` phase_6_pilot_v0_design block;`_org/org-decision-log.md` D-pm-skill-rev-1-17-10-pilot-v0-sanity-test-runner-001。**對齊** `[[backend_change_rule]]`(0 *.py change validated)+ `[[user_working_style]]` real-device testing + `[[friend_fetch_cost]]` no bulk fetch in sanity cases + `[[public_vs_private_friend_data]]` TEST_FAKE_ prefix isolation + `[[delete_dialog_no_undo_hint]]` cleanup SQL DELETEs commented by default for QA reviewer protection + `[[feedback_human_first_docs]]` JSDoc-style comments make case file PM/QA/RD-readable + `[[dep_management]]` 0 new pip dep。|
| 1.17.9 | 2026-06-23 | **Mainline Pre-Deploy Sanity Check Layer 4 formalization(PO 2026-06-23 catch #3 — formalizes rev 1.17.7 vague Layer 4 description)**:Through 5-round design discussion(LIFF test runner pattern + ngrok local backend infrastructure + multi-device pool concept + sanity = functional definition + after-merge-before-deploy precise timing),PO crystallized Phase 6 deploy gate that closes rev 1.17.7 "future Path B Azure staging" vague language。**Concrete spec definition:** Layer 4 = "mainline pre-deploy functional sanity check" — AFTER all Phase 6 build queue items merged to mainline AND BEFORE `/pm deploy --target prod`,local backend running mainline HEAD,PO uses real device via ngrok to load Pilot v0 `sanity_test_runner` LIFF page,page auto-executes test cases against backend(which uses its own dev credentials for cross-service calls),results downloaded as `result.json` + backend log。**Architectural elegance:** sanity test page builds request data commands but doesn't embed credentials — backend processes with its own credentials for Azure Blob / GCP / Gemini AI / LINE Push API。Real LINE auth token auto-inherited via LIFF on real device。Cross-service integrations naturally tested via backend's dev credentials configured for local env。**Cumulative integration insight:** rev 1.17.6 originally said "worktree pass ≠ merged main pass" — rev 1.17.9 extends to "each F# build's Layer 2+3 pass ≠ cumulative mainline pass"。Sequential merges can each pass individually but combined may hit interaction bugs(eg. F1 resolver + F2 ssl_disabled rename module-level init order;F1+F2+F5 import order coherence)。Layer 4 is the CUMULATIVE-MAINLINE verification before any prod deploy。**Updates:** §F.3 quality_bar 加 `phase_6_pre_deploy_sanity_check_pass: true`(layer 4 sub-spec with mechanism / pass criteria / staleness / carve-out);§F.5 Exit Check List 加 new item;§F.6 / SKILL.md `/pm deploy --target prod` precondition 加 Step 6.5 — verify `state.md.phase_6_pre_deploy_sanity_check.latest_status: pass` + `executed_against_commit` matches current main HEAD(staleness detection);state.md schema standardized — `runs[]` array with run_id + executed_at + executed_against_commit + device + total_cases + passed/failed/real_5xx_bugs + verdict + result_json_path + backend_log_path,plus `latest_status` + `deploy_gate_status` + `carve_outs`。**Per-project test case JSON config:** `docs/pm/<project>/sanity_test_cases.json` declarative test definitions — reusable across projects,each project authors own test set。**Pilot v0 architecture(NOT in this spec amend — separate build commit later):** ~485 LoC across 4 files — `system_lib.py` + `app.py`(gated dispatch entry by `local_build.Const_Run_in_local_environment`)+ NEW `templates/sanity_test_runner.html` + NEW `static/sanity_test_runner.js`。Multi-device pool extension hooks(`test_runner_id` + `sync_start_at` + `concurrent_safe` markers in test cases)pre-included for future Pilot v1。**Pilot v1 future:** 10-device pool simultaneous load test catches Categories 2(multi-device WebView regression per memory `[[project_android_webview_render_bug]]`)+ 3(race conditions / lock contention / DB pool exhaustion)not catchable in single-device Pilot v0。**Carve-out mechanism:** `state.md.phase_6_pre_deploy_sanity_check_carve_out: [{deploy_commit, reason, authorize_by, at}]` — doc-only / config-only / infrastructure-only deploys may carve-out per `[[backend_change_rule]]` spirit。**Memory entry update:** `feedback_phase_5_to_6_progressive_widening_verification.md` adds Layer 4 concrete definition section + cross-references rev 1.17.9。**Backend-schema-auto-sync state.md:** `phase_6_pre_deploy_sanity_check` field initialized with status `not_yet_executed`,test_case_config path placeholder,deploy_gate_status `blocked`(per rev 1.17.9 default — block until first sanity check run)。**Eat-own-dog-food meta-iteration #54:** rev 1.17.9 spec amend continues same-session pattern with rev 1.17.6→1.17.7→1.17.8 cluster。Discussion architecture matured through:Round 1(can we test all features locally)→ Round 2(local DB seed fixtures)→ Round 3(LIFF test runner via dispatch table)→ Round 4(sanity = functional + multi-device pool)→ Round 5(after-merge-before-deploy precise timing)。Demonstrates §6.4.15 SKILL Workflow Lifecycle Document-only → First-invoke tested fast iteration loop。**Files changed:** proposal.md §F.3 + §F.5 + Revision History;SKILL.md `/pm deploy --target prod` precondition gate;memory `feedback_phase_5_to_6_progressive_widening_verification.md` Layer 4 section + MEMORY.md index;`docs/pm/backend-schema-auto-sync/state.md` `phase_6_pre_deploy_sanity_check` initial field;`docs/pm/_org/org-decision-log.md` D-pm-skill-rev-1-17-9-mainline-pre-deploy-sanity-check-001 entry。**對齊** `[[user_working_style]]` real-device testing + `[[backend_change_rule]]` propose-first + `[[friend_fetch_cost]]` scope-limited per-cmd + `[[public_vs_private_friend_data]]` PII sanitize + `[[feedback_human_first_docs]]` 3-role dashboard。|
| 1.17.8 | 2026-06-23 | **Progressive Widening cluster cleanup — 5 CONCERNs from same-session spectra-review on rev 1.17.6+1.17.7**:PO 2026-06-23 invoked spectra-review on rev 1.17.6+1.17.7 amendment cluster after empirical F1+F2 dogfood validated framework。Review surfaced 5 CONCERNs(0 BLOCKER + 3 NIT deferred)— all addressed in this cluster amendment per "fix-now strict-dominant" cost-matrix verdict(fix 4.5 vs defer 10.7,net saving 6.2)。**C1 Step 5.5 naming collision fix:** Phase 3 dispatch's `invoke /pm setup-worktree inline as Step 5.5`(set by rev 1.17.1)collided with Phase 5 dispatch's `Step 5.5 post-merge regression check`(rev 1.17.6)— both in `/pm advance-phase` workflow section。Renamed Phase 3 to **Step 5.3** to disambiguate;Phase 5 dispatch retains Step 5.5。**C2 mainline_build_sanity_check audit field naming alignment:** rev 1.17.7 spec brief `layer_3a/3b/3c/3d` drifted from actual state.md verbose impl `layer_3a_syntax_py_compile / layer_3b_safe_mode_project_imports / layer_3c_full_gunicorn_cold_start / layer_3d_health_smoke`。Updated spec to verbose canonical names with status enum + per-field detail。**C3 SKILL.md line 810 outdated comment:** `# do NOT push yet — rev 1.17.6 Step 5.5 gates the push` updated to `# do NOT push yet — rev 1.17.6 Step 5.5 + rev 1.17.7 Step 5.7 BOTH gate the push`(implementer hint accuracy after rev 1.17.7 inserted Step 5.7)。**C4 canonical `mainline_build_sanity_check` schema:** state.md has TWO usage contexts:(a)top-level `phase_<N+1>_entry_gate.mainline_build_sanity_check`(first event at phase transition merge);(b)per-build-item nested `phase_<N+1>_<feature_id>_<finding_slug>.layer_3_mainline_build_sanity_check`(ongoing Phase N+ build merges)。rev 1.17.8 codifies BOTH use same field shape — query tooling can `grep -r mainline_build_sanity_check state.md` across all events。Both contexts already empirically present in backend-schema-auto-sync state.md(phase_6_entry_gate + phase_6_f1 + phase_6_f2)。**C5 Progressive Widening scope generalization:** rev 1.17.6+1.17.7 spec body lived under "Phase 5 dispatch" heading implying `/pm advance-phase 5→6` strict scope。Empirically extended to ALL Phase 6+ in-build-queue worktree → main merges(F1 df9dc8a + F2 5a20d68 both Layer 2 PASS 9/9 — strong evidence)。rev 1.17.8 formalizes:Progressive Widening applies to(1)advance-phase 5→6 transition(original scope)+(2)ALL Phase 6+ in-build-queue worktree → main merges +(3)future analogous boundary transitions。Carve-out mechanism added:`state.md.phase_<N>_progressive_widening_carve_out: [<commit_hash>, ...]` with reason field for genuinely-N/A cases(eg. doc-only merges)— PO authorize per `backend_change_rule` spirit。**3 NITs deferred:** N1 Layer 4 staging E2E trigger criteria(Standard SKU upgrade)/ N2 eat-own-dog-food meta-iteration counter location / N3 Step 5.6 number skipped explanation — all low-impact deferrable to next minor cluster。**Files changed:** proposal.md(this Revision History entry);SKILL.md `/pm advance-phase` Phase 3 dispatch Step 5.5 → Step 5.3 rename + Phase 5 dispatch scope generalization box + Step 5.7 audit fields verbose alignment + Step 5.8 canonical `mainline_build_sanity_check` schema clarification + line 810 comment update。**Eat-own-dog-food meta-iteration #53:** Spectra-review SURFACED spec amendment cluster gaps within same session(rev 1.17.6+1.17.7 cluster amended)→ rev 1.17.8 closes the loop via cost-matrix-driven fix-now。**Memory entry update:** `feedback_phase_5_to_6_progressive_widening_verification.md` to note rev 1.17.8 scope clarification + canonical schema clarification(no rename)。對齊 §6.4.13 minor change tier(amendment cluster cleanup,not new commands)+ memory `[[feedback_human_first_docs]]`(canonical schema improves doc clarity for 3-role readers)。|
| 1.17.7 | 2026-06-23 | **Mainline build sanity check — Progressive Widening Layer 3(PO 2026-06-23 catch #2)**:PO 在 backend-schema-auto-sync Phase 6 entry gate(rev 1.17.6 Layer 2)PASS 9/9 後 raise:「還要跑 main line build 驗證其他功能是否正確」。**Gap analysis:** rev 1.17.6 Step 5.5 只 verify **project-specific** integration test on merged main(eg. backend-schema-auto-sync 9 scenarios)— NOT verify **整個 mainline build healthy**(app startup / health endpoint / side-channel impact on other features)。**Insight:** PO 連續兩 catch revealed unifying pattern = **PROGRESSIVE WIDENING VERIFICATION** — narrow scope verification 永遠 incomplete,需 systematic widening。Layer 1 worktree test / Layer 2 project integration on main(rev 1.17.6)/ Layer 3 mainline build sanity on main(rev 1.17.7 NEW)/ Layer 4 staging E2E(future Path B)。Each layer catches different risk class。**Updates:** §F.3 quality_bar 加 `mainline_build_sanity_check_pass: true`(4 sub-layers 3a py_compile / 3b safe-mode imports / 3c gunicorn cold start / 3d /health smoke;3a+3b enough for deploy gate unblock,3c+3d 若 blocked-by-env mark partial,3c real-regression-stack-trace = abort);§F.5 Exit Check List 加 new item;§F.6 / SKILL.md `/pm advance-phase` Phase 5 dispatch 加 Step 5.7(insert 在 Step 5.5 與舊 Step 5.6 中間;舊 Step 5.6 renamed to Step 5.8 push + state transition,now requires BOTH Step 5.5 AND Step 5.7 PASS)。**Sub-layer 3 stratification key:** 3a + 3b = zero-risk syntax + import checks always do-able。3c + 3d 是 deployment env-dep — Path A local 有天然 ceiling(many projects 在 local 沒 production env vars,startup 必 crash on None values);Path B Azure staging 才能 full verify。**Critical distinction:** "blocked-by-env"(stack trace 反映 missing env var,Layer 3 partial pass OK)vs "real regression"(syntax/import/new None-handling errors NOT from env)— PO/PM judgment per stack trace inspection。**Discovery context:** backend-schema-auto-sync Phase 6 entry gate Layer 3 smoke test surfaced `BOT_Manager_http_url=None` crash at `app.py:16435`(pre-existing local env limitation,NOT Phase 5/6 regression — same crash on a218711 baseline)。This validated the spec — Layer 3 catches limitations(not just regressions)+ honest acknowledgment of Path A ceiling。**Memory entry renamed:** `feedback_phase_5_to_6_post_merge_regression_check.md` → `feedback_phase_5_to_6_progressive_widening_verification.md`(consolidates rev 1.17.6 Layer 2 + rev 1.17.7 Layer 3 into unified Progressive Widening pattern;future Layer 4 staging insights fit naturally)。**Backend-schema-auto-sync state.md retroactive:** `phase_6_entry_gate.mainline_build_sanity_check` field added recording 3a+3b PASS / 3c+3d blocked-by-env(BOT_Manager_http_url)/ coverage: partial / Phase 6 deploy gate stays unblocked。**Eat-own-dog-food meta-iteration #52:** PM Skill self-improvement via real-execution dogfood within same session(rev 1.17.6 → 1.17.7 chained from same PO architect-level pattern recognition)。對齊 §6.4.15 SKILL Workflow Lifecycle Document-only → First-invoke tested stage criteria + memory `feedback_phase_5_to_6_progressive_widening_verification`(NEW lock)+ memory `project_v2_backend_integration`(local Path A = Azure runtime substitute,with env ceiling)。|
| 1.17.6 | 2026-06-23 | **Post-merge regression check — Phase 5 → 6 advance gate(PO 2026-06-23 architectural insight)**:PO 在 backend-schema-auto-sync Phase 6 advance 後 raise:「Phase 5 run the test success it is worktree build. it doesn't imply submit all code to main line and the build also success. we need to run mainline build in local environment and run the test again.」**Gap analysis:** §F.3 `no_merge_conflict: true` 只 verify pre-merge worktree state,NOT post-merge mainline state。Real merge 可能 hit conflict(我 resolve)or 3-way auto-merge silently combine main + dev 成 unexpected state — both invisible to pre-merge worktree test。**Updates:** §F.3 quality_bar 加 `post_merge_regression_check_pass: true`(條件:integration test suite re-run on merged main HEAD 100% pass,same env as Phase 5 per state.md.phase_5_staging_strategy);§F.5 Exit Check List 加新 item「Post-merge regression check pass」;§F.6 `/pm advance-phase 5` enhancement 重構為 3-step subroutine — Step 5.1 merge(no push yet)/ Step 5.5 post-merge regression check / Step 5.6 push + state transition(only after Step 5.5 pass);on FAIL → `git reset --hard ORIG_HEAD` 自動 revert merge atomically + abort advance-phase + state.md.current_phase stays N + leave worktree intact for engineer investigation。SKILL.md `/pm advance-phase` Phase 5 dispatch 對應改 3-step + Step 5.5 audit fields(`phase_<N>_post_merge_regression_check_at/result/command`)。**Project-side adoption:** state.md 加 `phase_<N+1>_entry_gate` field block 列出 post-merge regression test 動作 + status(初始 `not_yet_executed`)+ blocker_severity + suggested command。對齊 memory `feedback_phase_5_to_6_post_merge_regression_check`(NEW,rev 1.17.6 lock)。**Eat-own-dog-food:** Phase 5 → 6 advance for backend-schema-auto-sync(commit f542888)triggered this insight — merge HAD conflicts(state.md + _org/org-decision-log.md),我 resolve OK 但從沒 re-run test 證實 merge integrity。PO 抓 architecture-level gap。**Catches 3 layers:** (1) semantic merge conflict resolution correctness;(2) main divergence indirect impact on project code;(3) atomic merge ≠ semantic correctness gap。**Cost-benefit:** Test re-run ~2 min vs catches regression that would otherwise hit Azure prod。Strictly dominant choice。**Files changed:** proposal.md §F.3/§F.5/§F.6/Revision History(this row);SKILL.md /pm advance-phase Phase 5 dispatch refactor;NEW memory `feedback_phase_5_to_6_post_merge_regression_check.md`;backend-schema-auto-sync state.md `phase_6_entry_gate` field added retroactively。**Routing:** pm-skill domain spec change → main(per §E.8.8.9)。|
| 1.17.5 | 2026-06-23 | **active-project.txt canonical path alignment(spec ↔ impl drift fix)**(PO 2026-06-23 拍板 X2 option after exploring X1/X2/symlink/Flat/drop-docs-pm options;simplification trajectory landed on physical-reality alignment):**Drift discovery:** Reality writes `docs/pm/active-project.txt`(top-level)BUT spec/SKILL/manuals wrote `docs/pm/_org/active-project.txt`(under `_org/`)— spec ↔ impl mismatch first flagged in spectra Round 3 C8 family + docs/decision-log.md BUG #2。**Decision:** active-project.txt canonical = `docs/pm/active-project.txt`(top-level)— NOT under `_org/`。**Rationale:** physical reality alignment(file 一直在那)+ git history continuity(no rename)+ semantic correctness(active-project.txt = PM Skill root pointer not org-shared artifact;`_org/` 保留 ORG-level shared:org-decision-log / org-roster / contract-pack / specs etc.)+ lower discoverability cost(`ls docs/pm/` 直接看到)+ minimal migration cost(~16 LIVE refs vs 167 if going further structural change)。**Sed sweep applied to 5 LIVE files(16 refs total):** SKILL.md pm-skill(12 refs:9 full-path + 3 short-form)/ QUICKSTART.md(1 ref FAQ)/ .claude/commands/spectra-review.md(1 ref)/ spectra-review SKILL.md(1 ref)/ namecard-v2-ddd-guardian SKILL.md(1 ref)。**Historical files preserved unchanged(audit trail integrity):** docs/decision-log.md(BUG #2 entry)+ 2 past review logs(rev-1-17-3-mainline-as-project-review + rev-1-17-4-round-3-verify)。**Updates:** §E.8.8 加 canonical path 📌 box(rev 1.17.5 note 解釋 `_org/` 為何不歸屬 + drift fix rationale)+ Revision History entry(this row)。**No SKILL.md version bump needed**(pure path string fix,no workflow logic change)but `/pm` workflows reading `docs/pm/_org/active-project.txt` 既往 fails silently 變 succeeds(impl-level regression fix)。**Eat-own-dog-food:** This drift survived 9+ spectra rounds because no end-to-end execution of `/pm use`/`/pm whereami` actually touched the path — pure documentation drift,proved spec ↔ impl alignment 必走 execution dogfood 才能 catch。對齊 §6.4.15 SKILL Workflow Lifecycle "Document-only → First-invoke tested" stage transition criteria。|
| 1.17.1 | 2026-06-23 | **Spectra Round 1 fix(rev 1.17 cascade gaps)— 5 patches**(PO 2026-06-23 拍板 `A`,Round 1 spectra-review verdict needs-patch:3 BLOCKER + 4 CONCERN + 3 NIT;applied B1+B2+B3+C1+C3 net cost savings 14.8):**B1** SKILL.md table row /pm daily-sync Phase column `4(daily)` → `3+(daily — worktree daily ritual)— rev 1.17 amendment`(Phase 3 worktree commits also need daily-sync ritual);**B2** /pm push-gate Phase column `4(per push)` → `3+(per push — worktree commits)— rev 1.17 amendment`(Phase 3 shared infra is HIGHEST blast-radius code,9-check enforcement must apply);**B3** user manual frontmatter add ⚠ rev 1.17 amendment note pointing readers to proposal §E.8.1+§E.8.2 as authoritative source(scenario 5a 「Phase 4 主開發 V2 start」描述 rev ≤ 1.16 timing,full scenario rewrite defer to user manual v1.9);**C1** /pm advance-phase Phase 3 dispatch 改 explicit `invoke /pm setup-worktree inline as Step 5.5`(was「AUTO-trigger」doc-only — spec ↔ impl 真實 alignment)+ state.md update note + then proceed to shared infra;**C3** /pm advance-phase Phase 5 dispatch 加 explicit inline git subroutine(checkout main + pull + `git merge --no-ff dev/<project>` + push origin main)+ failure handling(merge conflict → abort + leave worktree intact for engineer fix)— consistent with §F.6 full workflow body。**Deferred(justified):** C2 rollback idempotency(§E.8.2 Step 4 已 handle)/ C4 init template `phase_3_started_at`(advance-phase Step 5 dynamic write sufficient)/ N1-N3 style only。Round 2 verify ship-as-is-minor(1 trivial CONCERN about this Revision History entry — resolved by this very row)。Cross-refs:[reviews/2026-06-23-pm-skill-rev-1-17-worktree-amendment-review.md](../reviews/2026-06-23-pm-skill-rev-1-17-worktree-amendment-review.md) Round 1 + [reviews/2026-06-23-pm-skill-rev-1-17-1-round-2-verify.md](../reviews/2026-06-23-pm-skill-rev-1-17-1-round-2-verify.md) Round 2 verify。對齊 rev 1.10.1-3 spectra fix sub-decimal versioning pattern。|
| 1.11 | 2026-06-19 | **Team Composition Contract — §6.4.14 新加**(PO 2026-06-19 連續 4 insights lock):A. Members vs Consultants distinction(AI_Agent 是 team / Claude general-purpose 是 consultant);B. Default trust_tier by role(PM→final_approver auto-grant);C. Multi-PM all_approve policy;D. No-PM auto-postpone(production-impacting commands 無 PM 時 postpone + state.md.postponed_commands[]);E. MVT 3-role coverage(soft reminder 多處 / hard block 對 advance-phase 1 + deploy + signoff + rollback);F. Bootstrap protection(refuse remove last human / sandbox carve-out);G. Cross-command integration;H. Contract version team-roster-v2。**§6.4.4 trust hierarchy 強化**對齊 collective approval + AI_Agent 永不 PM。對齊 PO 2026-06-19 meta-dogfood:用 PM Skill 走 PM Skill 自身 team-roster design 改進。Cross-refs:backend-schema-auto-sync spec REQ-013(/pm build-team)+ REQ-014(team composition contract enforcement)。|
| 1.10.3 | 2026-06-18 | **SKU-aware Deploy Strategy(對齊 LineBOT 真實 Azure setup 落地)**:§G.6.1 加 SKU-aware design rationale + 兩 strategy(`slot_swap` Standard+ / `direct` Basic);對齊 PO 2026-06-18 Option C 拍板「接受 ~30s downtime $0 cost」。配合 SKILL.md v1.1.11 `/pm deploy` workflow Step 4 拆 4.1(slot_swap)/ 4.2(direct ZIP deploy);`/pm rollback` Step 2 拆 2.1(slot_swap_back)/ 2.2(redeploy_previous_tag)。LineBOT 現 prod = `liffbeauty.azurewebsites.net`(Basic SKU,PYTHON 3.10 Linux,Japan East,RG=`beautyreservation_group`),smoke endpoint `/health` 200 OK 確認可用。`azure-config.yaml` schema v1 包含 sku_tier + deploy_strategy + rollback_strategy + health_check + upgrade_path 完整 spec。對齊 spectra v1.1.10 C2 fix(deploy 讀 azure-config)。|
| 1.10.2 | 2026-06-18 | **Spectra v1.1.8 impl-level Round 1 Fix(eat-own-dog-food #14,首次 implementation-level)— C3 spec patch**:§G.6.0.2 manifest.yaml schema 加 `ssot_pending: bool default false` field — 對齊 SKILL impl `/pm migration-propose` Step 7 行為,**收回 spec → impl drift**(若 PO defer SSOT update,manifest 留 entry 但標 ssot_pending=true,Phase 3 Exit §D.2 拒絕 advance)。其餘 6 fix(B1 + C1/C2/C4/C5/C6)全在 SKILL.md v1.1.9 落地,proposal 文檔層只此 1 spec patch。對齊 spec ↔ impl 100% 一致。|
| 1.10.1 | 2026-06-18 | **Spectra Round 1 Fix(eat-own-dog-food #13)**:2 BLOCKER + 5 CONCERN 全 close。**B1** §K.8 加 `override_scope` clarification(bypass=discipline_invariant_check ONLY;still_enforced=schema_migrations_aware + V8 drift + 其他 G.6.1 preconditions;rationale + why_separate 三類紀律獨立);**B2** §E.4b.5 **Spec Re-entry from Drift Check Workflow** 新加(soft lock 設計 — unlock_conditions / unlock_workflow 8 步 / re-V8 lite scope / re-lock / edge_cases 連兩次 revise-design escalate);**C1** §K.4 cross-module API row 拆 major(Phase 0-7 對齊 §6.4.13 12 週 deprecation)vs minor(§E.4b drift lite path 對齊 patch tier);**C2** §D.2 review_target D-spec 明示 = plan.md(對齊 §C.1 既有三檔結構,non-split);**C3** §K.9 加 `fallback_path`(IF daily/weekly v1.1 未實作 → state.md `discipline_overrides[]` + `/pm status` output banner + upgrade path);**C4** 合 B1 解決(prod migration NOT auto-execute 對齊 memory rule,override 不繞);**C5** §K.7 cross-reference 加第 10 條 V8 Gate(spec-level discipline vs K deploy-level discipline 兩層對齊)。Round 2 verify verdict=ship-as-is。對齊既有 11 輪 100% close rate norm。|
| 1.10 | 2026-06-18 | **Gap 5 Resolved — No Fast Path Policy 落地**(PO 拍板「紀律很重要,該走得還是要走,以策安全,小心駛得萬年船」):§6.4.11 §K **Discipline Invariant — No Fast Path Policy** 新加(10 sub-sections — K.1 invariant 正式定義 / K.2 5 條 memory rule 哲學對齊(backend_change_rule / dep_management / delete_dialog_no_undo_hint / friend_identity_change / backend_schema_change_workflow)/ K.3 Emergency Response distinction(rollback=PATH vs fast track=BYPASS)/ K.4 必走 SDLC 適用範圍 / K.5 自然 exception(documentation-only / decision log / audit / rollback action 本身)/ K.6 `/pm validate-discipline-invariant` 命令 / K.7 cross-reference 對齊 9 既有 framework / K.8 **PO Override Mechanism**(`/pm deploy --override-discipline --reason "<≥50 chars>"` + confirmation_phrase=`BYPASS DISCIPLINE` + 唯一 escape valve)/ K.9 Override metrics alarm(1/month warning / 2/month escalate / 3+/month freeze)/ K.10 Confidence Tier);§G.6.1 precondition 加 `discipline_invariant_check: pass` gate(自動 trigger `/pm validate-discipline-invariant`,fail → block deploy,override path = K.8)。**核心:紀律 over convenience,Rollback=emergency PATH 而非 deploy bypass;PO 是 trust hierarchy 唯一 escape source(§6.4.4 對齊);override 罕用是紀律累積,頻繁是 policy 失效**|
| 1.9 | 2026-06-18 | **Gap 4 Resolved — V8 Cross-Module Review Move to Phase 3 末**(PO 拍板 dissolve Partial Promotion problem):§6.4.11 §D.2 Phase 3 Exit Criteria 加 `v8_cross_module_spec_review` subsection(rounds_min 1 / verdict ship-as-is / 0 carry-over / 5 scope: api_contract_between_modules / data_ownership_ssot / schema_dependency / cross_module_invariant / token_action_naming / 全 participant: 5 engineer + Tech Lead + PO / spec_lock_after_pass);§D.5 Phase 3 Exit Check List +2 items(V8 verdict + spec lock state);§E.4 review_process `v8_rounds_min` 2→0 + `v8_drift_check_required` conditional;§E.4b **Mid-flight Cross-Module Contract Drift Check** 新加 subsection(對齊 Concern 3 — drift trigger / lite V8 workflow / Phase 4 re-entry 關係);§E.8.1 Architecture Premise 加 **Stage 0 V8 Gate**(前置 to Stage 1)+ Stage 1 加 mid-flight drift trigger 提醒 + Stage 2/3 加 staging migration + Migration Gate cross-ref。**核心轉變:V8 從 Phase 4 mid+end 移到 Phase 3 末,Phase 4 only 在 cross-module contract change 才觸發 lite drift check;對齊 PO 哲學「all module cross review job in done before coding」;cost saving: cross-module gap 在 spec 階段 ~\$1 cost catch 而非 code 階段 \$10/$100**。|
| 1.8 | 2026-06-18 | **Cluster A — Schema Migration Awareness 完整設計**(PO 拍板「PM Skill 須 aware DB migration 並 run migration first」後落地):§6.4.11 §G.6.0 Migration Gate(9 sub-sections — Awareness Mechanism=SSOT file hash + Manifest / manifest.yaml schema / migration-state.md schema / `/pm migration-status` / `/pm migration-propose <feature-id>` / `/pm migration-apply --env <env>` / `/pm migration-mark-applied --env prod --version <NNN>` / Migration Lifecycle 跨 Phase / Cross-reference 對齊 memory rule);§G.6.1 precondition 加 `schema_migrations_aware` gate;§C.2 functional.md feature schema 加 `schema_change: bool` + `migration_id` 兩 field + §C.2a Schema Change Tagging;§D.1 Mandatory Outputs 加 Migration Manifest 3 條(entry_added / sql_file_created / forward_backward_verify_complete);§D.2 quality_bar 加 `schema_migration_manifest_consistent`;§D.5 Phase 3 Exit Check List 加 2 項;§F.3 quality_bar 加 `staging_migrations_applied_and_verified`;§F.5 Phase 5 Exit Check List 加 staging migration + post-migration schema 對齊。**4 新命令全標 v1.2 Planned;對齊 memory `backend_schema_change_workflow` 100%(SSOT / propose / ALTER TABLE 3 樣 / PO 自 apply prod);無新 install / 無 DB credentials 入 SKILL execute context**(只 mark-applied 用 read-only verify,且 fallback 可 PO 自填)|
