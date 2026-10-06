# Design Spec Authoring Rules

> **Owner:** PM(spec authoring governance)
> **Status:** Draft — **§3 Component Markup Contract(UI)定稿 + §4 通用 DESIGN authoring 已補;非 UI impl-detail 具體寫法仍參 framework §3.5**
> **Spec-Version:** 2026-09-05.3
> **Last Updated:** 2026-09-05
> **Role:** L3 Primary — design spec 的 **create / update / delete** 唯一 authoring 規則書(Track A 家族第 2 份)
> **Authors:** PO(kuohsuming)+ Claude(co-author)

---

## 1. Purpose

定義 Claude(及任何 AI 工具)在 **建立、更新、刪除 design spec** 時**必須嚴格遵守**的規則。可逐條打勾的執行規則書,不是論述。

- 論述 / framework 層(WHY 5 spec、DESIGN 在 cascade 的位置)→ 見 `docs/pm/5-spec-authoring-framework.md §3.5`
- 通用 spec 完整性標準(M1–M5)→ 見 `docs/ddd-doc-maintenance.md §7`(本檔**繼承**,不重造)
- 姊妹 rulebook:`requirement-spec-authoring-rules.md`(REQ 層,已上線)
- 本檔專注:design 層的 authoring 規則,**首發交付 = §3 Component Markup Contract(UI 版面穩定)**

> **本檔是 design spec authoring 的 Primary。** §3 裁決 **UI markup 契約**(UI 專屬);§4 裁決**通用 DESIGN authoring**(App Shell / 覆蓋 / 追溯 / test seam / sign-off,UI 與非 UI 皆適用)。非 UI 的 impl-detail 具體寫法(interface signature 風格、SQL DDL)仍參 framework §3.5(§4.5)。framework §3.5 / `_spec-template` 若涉 DESIGN authoring 規則,應指向本檔(One Topic, One Primary — `ddd-doc-maintenance.md §3.1`)。

> **⭐ DESIGN 恆存在(2026-07-05,D-035;5 份 spec 不可省略)**:無論 feature 多簡單,**DESIGN 都要寫**——不再有 tier / risk_level 省略(舊「Small 省 / low-risk skip」已廢除)。tier 只控**深度**(framework §6)。**最小地板(floor)= ≥1 component + `covers_func`(cite FUNC)+ `file_impact` ≥1 + `test_seam`;UI 加 markup 契約(INV-D1~5)**;簡單 feature 寫到此即合格,但不省。**無 spine 降級**(FUNC 恆在 → `covers_func` 直接 cite FUNC,不改 cite claim-ID)。

---

## 2. Scope

### ✅ In-scope
- design spec 的 create / update / delete 規則
- **§3 Component Markup Contract(UI 專屬)**:markup 契約 + 5 條版面穩定不變式 + 結構快照 gate
- **§4 通用 DESIGN authoring**:§4.0 App Shell 契約 / §4.1 DESIGN↔FUNC+TP 完整性不變式 / §4.2 DESIGN↔Code 追溯(`@implements`)/ §4.3 test seam / §4.4 CRUD + sign-off / §4.5 非 UI DESIGN
- cite parent:每 DESIGN cite `covers_func`(list,m:n)

### Non-goals
- 非 UI DESIGN 的 **impl-detail 具體寫法**(interface signature 風格、SQL DDL、演算法):參 framework §3.5(§4.1–4.4 的覆蓋/追溯/seam/sign-off 規則仍適用)
- validator 硬 gate 實作 + 引擎 `describe()`:列為 Track B build 期(**rulebook-first**,對齊 REQ 規則 D-003)
- claim-ID 機制本身(`REQ-<id>-G<k>`/`A<k>`)= REQ rulebook 的產物(本檔**引用**,見 §4.2 依賴註)

> **版面問題治理範圍**:§3 專治「改一點點,整個排版都變」的 fragility,不涵蓋純視覺美學(色彩搭配、間距美感)——那屬設計品味,非可機檢契約。

---

## 3. Component Markup Contract（UI 版面穩定契約）

### 3.1 動機 — 5 個根因 → 5 條可機檢不變式

「小改動炸整個排版」在 vanilla HTML/CSS/JS 幾乎必是以下組合。本節把**每個根因**變成一條**元件層級宣告 + 可機檢不變式**:

| 根因 | 對應不變式 |
|---|---|
| 全域 CSS cascade + 後代選擇器 → 改一處外洩全站 | **INV-D2** scoping |
| 隱式文檔流沒收束(無 max-width / overflow / 換行策略)→ 長字串推歪整排 | **INV-D1** layout_contract |
| Magic number 散落 → 改一個沒對齊其他 | **INV-D3** token-only |
| 壞狀態沒被想過(空 / 缺資料 / 溢出)| **INV-D4** negative_space |
| markup 結構被重組 → 整棵 reflow | **INV-D5** frozen skeleton |

### 3.2 每 component 的宣告(machine-block)

每個 UI component 在 DESIGN spec 的 machine-block 宣告:

```yaml
component:
  id: DESIGN-<module>-<seq>
  covers_func: [FUNC-xxx]             # 追溯,陣列多值(DESIGN↔FUNC 為 mesh m:n;framework §3.5 單值 Parent: 是其最小情形)
                                      # 🔴 2026-10-02 訂正:本行原寫 `[FUNC-xxx.step-N]` —— 那是 `implements` 的語法(見下方 §4.2)。
                                      #   `covers_func` 只收**裸 FUNC id**:spine validator 的 `FUNC_ID` 是 `^FUNC-[A-Za-z0-9-]+$`,
                                      #   帶 `.step-N` 會被判 `bad-covers_func`,⚠️ 而 Stage 6 是 HARD 且會早退
                                      #   ⇒ 照抄這一行會讓整輪 lint 死在 Stage 6,後面約 130 道一道都不跑。
                                      # ⚠️ 本行曾與 §4.1.1 第 4 條自相矛盾(那條寫「`covers_func` ⊇ implements 的每一個 FUNC **前綴**」),
                                      #   且已咬過人一次:`report-entry-parity-design-spec.md` 第 161 行留著當事人的訂正註解。
  skeleton:                            # 凍結骨架 = slot 契約
    region: <grid-area 名>             # 掛在哪個命名版面區(app shell 的 template-area;區塊 registry 契約見 §4.0,待補)
    tag: <semantic landmark>           # article / section / nav …
    slots: [title, body, actions]      # code 只填 slot,不改結構
  tokens:                              # 只准引 token,不准硬寫值(見 3.5)
    spacing: [--space-md]
    color:   [--color-fg]
    type:    [--font-body]
  layout_contract:                     # 盒子界線 = cascade 防火牆
    max_width:   --width-card          # token 或白名單常數(100% / none / auto),見 3.5
    overflow:    ellipsis              # clip | ellipsis | scroll | wrap(WebView 保證屬性,見 3.6)
    white_space: normal                # ⭐ 必填,WebView-safe 換行防線(含 overflow-wrap/word-break;長無空白字串靠此斷行):normal | nowrap | pre-wrap
    text_wrap:   pretty                # 選填 progressive-enhancement;須有 white_space/overflow fallback,不得為唯一防線
    reflow_isolation: true             # → 編譯成 contain: layout style(見 3.6)
  negative_space:                      # 涵蓋該 component 適用的壞狀態(不適用者顯式 n/a + 理由,見 INV-D4)
    - long_string
    - empty_state
    - missing_data
    - overflow_boundary
  snapshot_ref: docs/pm/<project>/modules/<module>/fixtures/DESIGN-<module>-<seq>.sig.json  # git-tracked golden 參考檔(非 throwaway)
```

### 3.3 五條版面穩定不變式

| ID | 不變式 | 檢法 |
|---|---|---|
| **INV-D1** | 每 component 必宣告 `layout_contract`(至少 `max_width` + `overflow` + `white_space` 換行防線〔含 `overflow-wrap`〕;`text_wrap` 選填 enhancer)| 缺 = **HARD** |
| **INV-D2** | component 規則須 scoped 在 `[data-component]` root;禁跨 component 後代選擇器(**豁免白名單見 §3.4**)| naming/selector gate = **HARD** |
| **INV-D3** | **顏色 / 間距 / 尺寸**值須引 token;**禁新增** magic number(**gate 範圍 + 常數白名單見 §3.5**)| grep gate = **HARD**(僅擋新值,舊值機會性遷移)|
| **INV-D4** | 每 component 必宣告 `negative_space`:`long_string` **恆必含**(任何含文字 slot 皆適用);`empty_state` / `missing_data` / `overflow_boundary` 按性質,不適用須顯式 `n/a` + 一句理由 | 缺宣告 / 未顯式 n/a = **HARD**(對齊「正面 + 負空間」+ REQ `[GAP]` 精神;覆蓋按性質非一刀切)|
| **INV-D5** | `skeleton` 結構凍結;改結構(增刪 / 重排 slot・region)= 破壞性 → **人閘**(逐項差異審核)| snapshot diff 觸發人審(**enforcement 待 §3B snapshot gate 落地;此前為 rulebook 宣示**)|

### 3.4 INV-D2 scoping 機制:`[data-component]` 強制 + BEM 軟約定

- **強制邊界(可機檢)**:**component 規則**須錨在 `[data-component="X"]`(否則 = HARD 違規)—— cascade 防火牆,greppable。
- **完整豁免白名單**(不受此限,避免誤殺合法全域規則):at-rules(`@keyframes` / `@media` / `@font-face` / `@supports`)、CSS reset、`:root`(token 宣告)、`[data-region]`(app shell)、元素選擇器 `html`/`body`、明列的全域 state 前綴(`.is-*` / `.has-*`)。白名單外的未 scoped 選擇器才判 HARD。
- **軟約定**:component 內部 class 用 BEM 風(`card__title`)僅為可讀性,非強制。
- **runtime-create 優勢**:中央引擎在每個 component root 蓋 `data-component` attr——**單一施力點**,非散落各檔。

### 3.5 tokens:語意單層(無 primitive 層,YAGNI)

- **只做語意 token**:`--color-fg/bg/accent/danger/muted/border`、`--space-xs/sm/md/lg/xl`、`--text-sm/base/lg`、`--radius-sm/md`、`--z-base/overlay/modal/toast`(⭐ LIFF 疊層必納)、**`--width-*`/`--size-*` sizing 家族**(供 `layout_contract.max_width` 等引用)。
- **INV-D3 gate 範圍 + 常數白名單**:強制 token 只鎖 **顏色 / 間距 / 尺寸** 三類(drift 真痛點);全域字面值白名單放行 `0` / `100%` / `none` / `auto` / `1px`(hairline) / `transparent` / `currentColor` / grid `Nfr`。白名單外的具體 px / hex 才判違規。
- **不做** primitive→semantic 雙層(`--blue-500`)——無 theming 需求,YAGNI;日後需要再加。

#### 3.5.1 兩類 token 不同管(2026-08-31 補;現況實測驅動)

> 上面那份名單把所有 token 當成同一種東西。**它們不是。**
> 2026-08-31 實測 `templates/v3-app.css` `:root`:16 顆實際存在,其中 **`--text-input` 的性質與其餘 15 顆不同**。

| | **A 類 · 美學 token** | **B 類 · 約束 token** |
|:--|:--|:--|
| 例 | `--space-md` `--text-base` `--text-chip` `--color-border` | `--text-input: 16px`、`--color-muted` / `--color-danger` / `--color-accent`(對比度) |
| 值代表什麼 | 一個**設計選擇** | 一個**平台契約門檻** |
| 改值的後果 | 看起來不一樣 | **功能壞掉** |
| 誰能改 | 設計判斷 | ⛔ **不得憑設計理由調降** |
| 怎麼守 | 人眼 + 真機(**+ detect-only 衛生掃**,見下) | **機械 gate**(可靜態查) |

> **A 類的 detect-only 衛生掃(2026-08-31 落地,`lint.sh` Stage 19.6 /
> `scripts/css_numeric_health_check.py`)**:A 類**對錯要人判**,⛔ 不可做成 BLOCKING
> (否則會有人為了過 lint 去改設計)。但「疑似**意外**」是機械可判的 —— 現行兩條:
> ① 分數 px 字級,且 ±1px 內存在次數 ≥10 倍的整數鄰值(`14.5px ×1` vs `14px ×87`);
> ② 同 rule block 內重複宣告 `font-size`(前者為死碼)。
> ⭐ 那個 **10 倍比值就是防 gold-plating 的閘**:分數不是罪,**孤立**才是。
> ⚠️ 「只出現一次」**刻意不是**判準 —— §3.5.2 已裁定一次性值不得 token 化,
> 報表列出它們但每行標明「不是違規」,防止有人看到報表就跑去修。

**B 類的判準(三條全中才算)**:① 值由**外部平台行為或外部標準的演算法**決定,
非本專案憑設計理由可協商;② 違反時**無畫面症狀或症狀與成因不相關**;
③ **桌面環境目視驗不到**。

> ⚠️ **2026-09-01 修正判準措辭 —— 原文套不進「對比度」這個實例**:
> · ① 原寫「值由外部**平台行為**決定」。對比度的**演算法**確實是外部標準(WCAG SC 1.4.3),
>   但**門檻**(本專案 5.5 / 4.0)是 PO 拍板的,不是平台逼的。
>   ⇒ 擴充成「平台行為**或外部標準的演算法**」,並把不可協商性繫在
>   「⛔ 不得憑**設計理由**調降」而非「值的來源」—— 那才是 B 類的本質。
> · ③ 原寫「桌面環境**量不到**」。⚠️ 不精確:`--text-input` 的 Stage 19.5 和對比度的
>   Stage 19.7 **都是在桌面上靜態算出來的**。真正量不到的是**目視** ——
>   桌面螢幕亮、室內光線穩,淺字看起來永遠沒事。⇒ 改為「桌面環境**目視**驗不到」。
> ⭐ 這兩處不是新增條款,是把 2026-08-31 寫給單一實例(`--text-input`)的措辭,
>   在出現第二類實例後校正回它本來就想講的意思。

**已登記的 B 類**:

| token | 值 | 門檻來源 | 守門 |
|:--|:--|:--|:--|
| `--text-input` | `16px` | iOS WKWebView / Chrome for Android:表單控制項 `font-size < 16px` 時 focus 自動放大整頁**且不還原** | `lint.sh` Stage 19(真瀏覽器)+ **Stage 19.5**(CSS 宣告靜態掃) |
| `--color-muted` | `#515157` | 對比度 **≥ 5.5:1**(一般文字)/ **4.0:1**(大字),對**最差的表面**算 | **Stage 19.7**(`scripts/css_token_contrast_check.py`) |
| `--color-danger` | `#a21919` | 同上 | 同上 |
| `--color-accent` | `#1a46c1` | 同上 | 同上 |
| `--color-bg` / `--color-chip-bg` | `#fff` / `#d8d8e0` | **表面側** —— 自身不是文字色,但改暗會讓落在其上的字全體掉對比 ⇒ 一樣受 Stage 19.7 拘束 | 同上 |

> 規則 SSOT = `docs/ui-notes.md §0`「iOS Font Zoom Prevention」。
> ⚠️ 該規則是**通用行動規範,不是 REQ** —— `v3-app.css` 曾誤引 `REQ-520/521`(實為
> 「指認前出示名片照片」與「行業別未知遮蔽」,與本規則無關),2026-08-31 已更正。
>
> **[2026-09-02 訂正 —— 本句原文已不成立]** 原寫「對比度門檻的 SSOT = 本節」。
> **SSOT 已於 2026-09-02 遷至 [`docs/ui-notes.md §0.A` 條文表 `UI-C-01`](../../ui-notes.md)**
> (PO 拍板;該檔同日由 L3 Descriptive 提升為 **L2 現行 UI 契約**)。
> 本節自此為**下游引用**:數值一律以 `ui-notes.md §0.A` 為準,
> ⛔ 不得在兩處出入時以本節為準。
> **為什麼搬**:門檻是產品約束,而本檔是「怎麼寫 spec」的方法論規則書 ——
> 產品約束住在方法論文件裡,查「介面該長怎樣」的人不會翻到這裡,
> 那正是 2026-09-02 追查出的「規格被繞過」的機制之一。
>
> **[2026-09-05 合併註記]** 本段與 `origin/main` 的 `7142d8e`(§4.6 標記紀律收尾)撞在同一句。
> 對方改的是**同一句原文**的標記寫法,⛔ 不是要推翻 SSOT 搬遷 ——
> ⇒ 取本段(PO 2026-09-02 已拍板),並依 §4.6 重寫其標記。
>
> 以下數值敘述保留(與 `ui-notes.md §0.A` 一致),供本節 B 類 token 判定時就近參照:
> 演算法出自 WCAG 2.1 SC 1.4.3;**門檻是本專案自訂**:
> **5.5:1 一般文字 / 4.0:1 大字** —— 嚴於 WCAG AA(4.5 / 3.0),寬於 AAA(7.0 / 4.5)。
> ⭐ [2026-09-01 PO 拍板] 原話:「我會在意太陽下或任何環境字都要清楚」。
> ⚠️ 取中間值的理由是明文的:AA 的 4.5 只是「室內正常光線可讀」,⛔ 不等於強光下可讀;
> 但把**次要灰字**壓到 AAA 的 7.0,它會深到看不出是次要資訊 —— 資訊層次是真實成本。
> ⚠️ 判準取**最差的表面**:同一顆字色可能落在 `--color-bg`(#fff) 或
> `--color-chip-bg`(#d8d8e0) 上,後者較暗 ⇒ ⛔ 不得只驗白底就宣稱過關。
>
> **⭐ 表面側與文字側是蹺蹺板,⛔ 不得分開決定(2026-09-01 實證)**
> PO 真機回報「灰底真的太淺了」——`--color-chip-bg` 舊值 `#f0f0f5` 對頁面白底只有
> **1.14**,chip 幾乎看不出是個 chip(SC 1.4.11 對元件邊界要 3.0,而該 chip `border:none`
> ⇒ **底色就是它唯一的邊界**)。但底色**一加深,落在它上面的字就掉出門檻** ——
> 實測連 `#e8e8ee`(1.14→1.22,幾乎看不出差別)都會讓字掉到 5.19。
> ⇒ 底色與字色**必須同批一起移動**,⛔ 不得只改一邊。
> ⚠️ 且加深底色**買不到 1.4.11 的 3.0**:要達 3.0 底得深到 `#9191b6`,那時字必須近黑
> (`--color-accent` 得變成 `#0a1a49`)—— **藍色 chip 這個設計就不存在了**。
> ⇒ 2026-09-01 取 `#d8d8e0`(1.42):明顯看得出是 chip,且保住色彩身分;
> ⭐ **明確記載本專案在此處未達 SC 1.4.11**,那是有意識的取捨,⛔ 不是漏掉。

**對 INV-D3 的影響**:B 類**不適用**「僅擋新值、舊值機會性遷移」的寬鬆條款 ——
舊值一樣是 bug,必須修。A 類維持原條款不變。

**未宣告但存在的 token(2026-08-31 對帳)**:`--color-chip-bg` `--text-chip`(A 類,
屬既有 `--color-*` / `--text-*` 家族,補登記於此)、`--text-input`(B 類,見上表)。
⚠️ **2026-09-01 更正**:`--color-chip-bg` 已**不再是純 A 類** —— 它是 Stage 19.7 的
**表面側**輸入,改暗會讓落在其上的字全體掉對比 ⇒ 已補登記於上方 B 類表。
⭐ 「它只是個底色」這個直覺是錯的:對比度是**一對**顏色的性質,⛔ 不是單顆的性質。
⚠️ 名單中 `--space-lg/xl` `--text-lg` `--radius-sm/md` `--z-base/toast` **尚未建立** ——
依 YAGNI **不預先建**,用到時再加,不視為違規。
- **反萃非發明**:token 清單從既有 V2 CSS audit 重複值歸類而來,不從零造。
- **遷移策略**:INV-D3 只擋**新** magic number;舊值機會性搬,不一次翻新。

#### 3.5.2 回填(retrofit)—— INV-D3 未設想的第三種動作(2026-08-31 立)

> `INV-D3` 逐字寫著「**僅擋新值,舊值機會性遷移**」。
> **「機會性」= 順手改到才改。** 有計劃地把既有字面值成批換成 `var()` 是 **campaign**,
> ⇒ 現行條款**既不允許也不禁止,它沒設想過這件事**。本節補上。

**三種動作,性質完全不同 —— ⛔ 不得混談**

| 動作 | 值變不變 | 可證明性 | 需要的驗證 |
|:--|:--:|:--|:--|
| 新增字面值 | — | — | `INV-D3` 擋(HARD) |
| **回填** | ❌ **不變** | ✅ **可證明零視覺變化** | computed-style diff 即足 |
| **改值** | ✅ 變 | ❌ 不可證明 | 真機 + 互動後 harness |

⭐ **回填是唯一可以在沒有真機的情況下證明安全的動作。** 這是它值得單獨立條的理由。

**R1(HARD)—— 回填的值必須 byte-identical**

```
#86868b → var(--color-muted)   且 --color-muted: #86868b     ✅ 回填
#86868b → var(--color-muted)   但 --color-muted: #888        ⛔ 不是回填(這是改值)
```

**R2(HARD)—— 回填與改值不得同批**

> **前例(2026-08-09 → 08-10,一天內退版)**:該批同時做了兩件事 ——
> 建 38 顆 token(回填)**且**把 24 處固定 px 圓角改成 `--r-pill:999px`(改值)。
> 真機按「新增紀錄」時整顆鈕變直立橢圓反白 ⇒ PO 判退。
> 還原方式是 `git show eb63bb5^ | diff` **byte-identical 整批回退** ——
> ⭐ **38 顆 token 連同那 24 處一起被丟掉。**
>
> ⇒ 分批做,改值那批出事時回填不受牽連。**這是 R2 唯一的理由,也足夠。**

**R3(HARD)—— 回填批的驗收條件是「差異必須為 0」**

逐元素 computed-style 比對,回填前後**完全相同**。
⚠️ 這是回填**獨有**的判準:因為值沒變,差異必須是 **0**,⛔ 不是「差異在容忍範圍內」。
⇒ 任一處差異非 0 ⇒ 該處**不是回填而是改值**,退出本批另案處理。

**範圍判準(防 gold-plating)**

實測 `templates/v3-app.css`(2026-08-31,已剝註解):

```
色碼    1014 次 / 187 種    前 10 種佔 50%    出現 >=10 次:20 種    只出現 1 次:90 種
字級     395 次 /  19 種    前 3 種(13/12/14px)佔 70%
var()   現有 35 處
```

- **門檻:出現 >=10 次才進回填名單。**
- ⛔ **不得 token 化:只出現 1 次的那 90 種** —— 它們不是設計決策,是一次性值;
  token 化只會產生 90 個沒人複用的名字,**比硬寫更難維護**。
- ⚠️ 中間帶(2–9 次)逐案判斷,**預設不收**。

**與 §3.5.1 B 類的關係**

B 類(約束 token)**不受本節管** —— 它們的舊值本來就是 bug,必須修,
那是**修正**不是回填,一律不適用 R2 的分批要求。

### 3.6 reflow_isolation → CSS containment + WebView 支援底線

- `reflow_isolation: true` **編譯成** component root 的 `contain: layout style`——瀏覽器層級保證「元件內重排不外溢」,直接根治「改一點點整棵 reflow」(不只是宣告)。
- **enforcement = 選填 opt-in(非任何 INV 必填)**:`contain: layout` 有 clip 副作用(可能截斷 sticky / dropdown / overflow menu)→ 由 component 視內容宣告採用與否;有 overflow 子內容(選單、彈層)者**建議** `true`,純靜態內容可省。gate 只驗「宣告了就正確編譯」,不強制每 component 開。
- ⭐ **WebView 支援底線(硬規則)**:`layout_contract` 的**主要防線**只准用 **LINE WebView 保證支援**的屬性 —— `max-width` / `overflow` / `white-space`(schema `white_space` 欄位,INV-D1 必填)/ `contain`。
- **Progressive-enhancement(選填,須有 fallback,不得為唯一防線)**:`text-wrap: balance/pretty`(Chrome 114+)、`content-visibility: auto`(Chrome 85+)在舊 Android WebView 可能被靜默忽略 → 只能當加分;底層仍須有 `overflow` / `white-space` 保護,否則屬性失效時版面照炸(呼應 memory `android-webview-render-bug`)。
- **Tier 2 真機閘**須明列「驗這些屬性在目標 WebView **實際生效**」—— 防宣告層 sig.json 假綠(見 §3B)。

---

## 3A. Runtime-Create 專用約定（本 repo 現況:所有 element 皆 runtime-created）

> 本 repo(Namecard V3 SPA)所有網頁 element 皆由 config + runtime-create 引擎在執行期生成,`templates/index.html` 無靜態 markup。§3 的契約**全數適用**,但**錨點**從「靜態 HTML 檔」移到「config + 引擎 registry」。

| §3 機制 | runtime-create 下的落點 |
|---|---|
| skeleton(INV-D5)| 凍的是 **config/descriptor(引擎輸入)** + **引擎 component registry(node type → 產什麼樹)**;config 本身即宣告式 SSOT |
| tokens(3.5)| CSS custom properties 靜態載入,套 runtime DOM 一樣 — 零差異 |
| scoping(3.4)| 引擎一處蓋 `data-component` attr — 施力點最集中 |
| containment(3.6)| 引擎在 component root 加 `contain` — 套 runtime DOM 一樣 |
| **snapshot(sig.json)** | ⭐ **取自引擎 `describe()` 純路徑,非 parse 靜態 HTML**(見 3A.1)|

### 3A.1 snapshot 取法:引擎 `describe()` 純函式路徑

靜態 HTML 是空的、parse 不到 DOM。解法**不是**跳 headless,而是:

> 給 runtime-create 引擎一個 **`describe()` / dry-run 純路徑**:吃 config,回傳「它*會*建出的 component 樹」成 plain JSON(tag / data-component / **data-testid**〔test_seam hook,見 §4.3〕/ slot / 宣告的 layout 屬性),**完全不碰真 DOM**。`sig.json = engine.describe(config)`,stdlib validator diff 它。

- ⭐ **純函式前置條件(硬規則)**:`describe()` 須對 `(config, registry)` **純**(無副輸入、可重現)。任何 runtime 分支(locale / feature flag / platform / viewport)**須顯式參數化為 describe() 輸入**,並對每個關鍵組合各存一份 sig.json fixture。**無法純化的 component 退 Tier 2**(否則 snapshot flaky → gate 失信);**Tier 2 落地前,此類走人工 real-device 檢查**(逃生門不留空窗)。
- **輸出決定性** = f(config, registry);兩者凍 → 輸出凍
- **抓 config 漂移**:改 config 讓版面重組 → describe() 輸出變 → fail
- **抓引擎漂移**:改 render 邏輯 → 對固定 config fixture 的 describe() 輸出變 → fail
- 全程 **stdlib、無 headless、無 dep**

### 3A.2 layout config vs content data — 快照只凍結構

- ✅ **凍**:layout config(哪些 component、順序、slot 名)+ registry
- ❌ **忽略**:填進 slot 的文字 / 圖 / user data(namecard 內容每人不同,非版面)
- **slot 是分界線**:骨架宣告 slot,內容填 slot;快照只看 slot 存在與結構,不看填了啥。

---

## 3B. 結構快照 Gate（Tier 分級）

| Tier | 抓什麼 | 成本 / dep | 狀態 |
|---|---|---|---|
| **Tier 1** | 結構 + 宣告層漂移(INV-D1~D5 全部靜態可抓)| **stdlib、無 dep、無 headless** | 首選,Track B build 期實作 |
| **Tier 2** | cascade 解析後「真的炸了嗎」殘差(視覺回歸)| headless 截圖 diff → **需 dep**([[dep-management]] 須 PO 授權);真機留人閘 | **defer** |

- **關鍵洞見**:§3.1 的 5 根因**全部靜態就抓得到**(結構重組 / 缺 max-width / 冒 magic number / 跨 scope 選擇器 / 缺 negative_space)——故 Tier 1 已覆蓋高價值,Tier 2 僅補殘差。
- **sig.json diff 規則**:結構增刪 / 重排 = fail;layout 宣告漂移 = fail;文字 / 顏色 / 字型 = 忽略。
- **預期改動處置**:diff 非預期 → fail;預期 → 更新 fixture 且**人審 diff**(對齊逐項差異審核 OD-D)。
- **掛點**:build pipeline `ux-ui-designer` agent 產 DESIGN → gate 守(對齊 framework G6 executable gate)。

---

## 4. 通用 DESIGN Authoring（UI 與非 UI 皆適用）

> §3 是 UI 專屬的 markup 契約;§4 是**所有 DESIGN**(含非 UI)都須守的覆蓋 / 追溯 / 可驗 / sign-off 規則。共同貫穿單位 = **claim ID**(`REQ-<id>-G<k>` golden / `REQ-<id>-A<k>` anti;REQ rulebook 產物,本檔引用)。

**machine-block 組合(哪些欄用在哪種 DESIGN):**

| 欄群 | UI DESIGN | 非 UI DESIGN | 出處 |
|---|:---:|:---:|---|
| **共用**:`id` / `covers_func` / `implements` / `test_seam` / `file_impact` / `interface_signatures` / sign-off | ✅ | ✅ | §4 |
| **UI 專屬**:`skeleton` / `tokens` / `layout_contract` / `negative_space` / `snapshot_ref` | ✅ | ✖(不填)| §3 |

→ **UI DESIGN = 共用 + UI 專屬;非 UI DESIGN = 僅共用**(不填 skeleton/layout_contract,亦不套 §3 INV-D1~D5)。

**INV 分類(UI vs 通用):** **UI INVs = D0–D5**(§4.0 shell + §3 markup,僅 UI DESIGN 適用)/ **通用 INVs = D6–D8**(§4.1/4.2 覆蓋+追溯,UI 與非 UI 皆須)。

### 4.0 App Shell 契約（**UI-scoped**;`skeleton.region` 的 SSOT)

> §3 的 `skeleton.region` 引用「命名版面區」;這些區的 registry 就在此宣告。App shell = 頂層版面骨架,**1 份 / app、硬凍**;runtime-create 只往 region 內填,永不增刪 / 重排 region。
> **UI-scoped**:App shell 是 UI 版面骨架 → INV-D0 屬 **UI INVs**(見 §4 開頭分類);**僅 UI-bearing 專案有此檔,純後端專案無 app shell**。

**machine-block(1 份 / app,置 `docs/pm/<project>/_shell/shell.md` — 專案級,非模組):**
```yaml
app_shell:
  grid_template: |                     # 頂層 grid-template-areas(凍結)
    "header"
    "main"
    "actions"
  regions:                             # skeleton.region 的合法值域
    - { name: header,  purpose: 品牌 / 導覽 }
    - { name: main,    purpose: 卡片 / 清單 / 編輯器切換掛載點 }
    - { name: actions, purpose: 固定底部操作列 }
```

| ID | 不變式 | 檢法 |
|---|---|---|
| **INV-D0** | 每 component `skeleton.region` 必**引用 app shell registry 已存在的 region**;region 增 / 刪 / 改名 = 破壞性 → **人閘**(逐項差異審核)| 未知 region = **HARD**;registry 變更觸發人審 |

- **runtime-create 落點**:app shell 也 runtime-created → shell registry = 引擎的**頂層 config**;`engine.describe()` 快照涵蓋 shell 樹(region 增刪 → 快照變 → 人審)。

### 4.1 DESIGN↔FUNC + DESIGN↔TP 完整性不變式（雙重上游約束）

> **DESIGN 的雙重上游(PO 定案)**:對 **FUNC = 實作**(每 `FUNC.step / failure_mode` → DESIGN component,`@implements`);對 **TP = 可驗(非實作)**——DESIGN 不 implement TP,而是 **expose `test_seam`** 讓 TC 能斷言 TP 的 `validation_key_point`。

**claim 收斂點**——每個 claim,DESIGN 同時要有「怎麼做」+「怎麼驗」:
```
REQ-005-G1 (claim)
  ├─ FUNC-export-note.step-3   realizes   (行為)
  ├─ TP-012                    verifies   (驗證 validation_key_point)
  └─ DESIGN-card-03            @implements step-3 + test_seam(for_key_point TP-012.vkp-1)讓 TP-012 驗得到
```

**component machine-block 擴充欄(在 §3.2 UI 欄位之外,所有 DESIGN 通用):**
```yaml
  implements:                          # 對 FUNC = 實作;→ 程式碼 @implements(見 4.2)
    - FUNC-export-note.step-3
    - FUNC-export-note.FM-2
  test_seam:                           # ⭐ 對 TP = 可驗;綁到 TP 的 validation_key_point(非只 claim)
    - { for_claim: REQ-005-G1, for_key_point: TP-012.vkp-1, exposes: "exportNoteToPng() 回傳 PNG bytes + data-testid=export-done" }
```

| ID | 不變式 | 方向 | 檢法 |
|---|---|---|---|
| **INV-D6** | 每 `FUNC.step / FM` → 必有 ≥1 DESIGN `implements`(無未實作行為);每 `implements` → 指向存在的 FUNC step(無憑空多做)| FUNC ↔ DESIGN 雙向 | 缺 = gap / 多 = gold-plating,皆 **HARD**(對映 framework G4,提前到設計時抓)|
| **INV-D7** | 每 `TP.validation_key_point` → 必有 `test_seam` **暴露其 observable**(綁 `for_key_point`,非只 claim);每 `test_seam` → 指向存在的 TP validation_key_point | TP ↔ DESIGN 雙向(via test_seam)| 缺 / 未達 key_point = 不可驗 / 多 = 無主 seam,皆 **HARD** |

> **一句話(PO)**:DESIGN 必 cover 全部 FUNC items(`implements`,不多做)+ 全部 TP items(`test_seam`,不多做);每 claim 在 DESIGN 層同時有「怎麼做」與「怎麼驗」;**gap 在進 code 前就抓**。

#### 4.1.2 `INV-D7` 第三格的執行者 —— 以及兩條⛔ 一律不要再試的路（2026-10-05 立）

> ⭐ **`INV-D7` 的「多 ＝ 無主 seam」已有執行者**（`coverage_spine_integrity`：重複認領 0 條）。
> ⚠️ ⭐ **而那道計數只問「有沒有人暴露」與「是不是恰好一個人」** ——
> ⇒ ⛔ 一律不問「那個人暴露的，是不是這條 `validation_key_point` 要的那一件事」。

**⇒ 作者紀律（兩條，寫完 seam 當場問）：**

| # | 問題 | ⛔ 一律不合格的樣子 |
|:--:|---|---|
| 1 | 這條 `exposes` 對**同一個 TP 的其他 vkp** 也成立嗎？ | 成立 ⇒ 它描述的是兄弟那一條的機制（實例：`TP-bil-048.vkp-1` 原本寫的是 `vkp-2` 的呼叫計數器）|
| 2 | 這條 `point` 綁了幾個斷言？我覆蓋了幾個？ | 覆蓋不全而⛔ 一律沒說 ⇒ **其餘那幾個看起來有人負責** ⇒ 必須逐字寫「本條的 X 半邊」＋ 指名其餘住哪（或逐字說它⛔ 一律還沒有擁有者）|

**機檢**：`scripts/spec_vkp_scope_declaration_check.py`（lint Stage 165，兩道判準皆**只用結構**）。

> 🔴 ⭐ **以下兩條路實跑過、都失敗了 —— ⛔ 一律不要再試一次。**
>
> | 候選判準 | 實跑結果 |
> |---|---|
> | ① **絕對重疊**：`exposes` 與它自己的 `point` 的共同 token 數 | 647 條裡 **470 條零重疊** ⇒ **73% 誤報** —— ⭐ 成因是 `exposes` 描述**機制**而 `point` 描述**觀察**，兩者本來就用不同的字 |
> | ② **相對重疊**：兄弟 vkp 的重疊比自己高 | 只噴 10 條，⭐ **而它⛔ 一律沒抓到已知的那一條** —— 實查 `TP-bil-048.vkp-1` 修前的 `exposes` 與該 TP 的**三個** vkp 都是**零**共同 token |
>
> ⇒ ⭐ **判準寫下來：那條缺陷的錯⛔ 一律不是「像隔壁」，而是「跟三個都不像」**
> ⇒ 唯一看得見它的信號就是**絕對零重疊**，⇒ 而那正是 73% 誤報的那個信號。
> ⇒ ⭐ **∴ 兩個候選是同一個信號的兩種讀法，而真陽就落在誤報分不開的那一堆裡。**
> ⚠️ 依本 repo 的規約「一個沒有被突變測過的檢查器，它的『綠』⛔ 一律不是證據」
> ＋「⭐ 一個會誤報的 gate 會被關掉」⇒ 兩條都⛔ 一律不得上線。
>
> ⭐ 而這⛔ 一律不是放棄：**它是一個實跑出來的否定結果**
> （`[[feedback_gate_criteria_must_be_dry_run_first]]`）⇒ 下一個人該接手的是
> **結構判別器**（上述 Stage 165 的兩道），⛔ 一律不是第三種 token 相似度。

> 🔴 ⭐ **第二道的存在理由，是第一道的自我評價被實測翻掉。**
> 第一道的篩是「該 REQ 被 >1 份 design spec 認領」，⇒ 而 2026-10-05 那輪最嚴重的三條
> （`TP-bil-200.vkp-1`／`200.vkp-2`／`203.vkp-2`）**它全部抓不到** ——
> `REQ-843` 只有一份 design spec 認領，而那三條的子句**真的住在別份檔**
> （而那兩份檔⛔ 一律不認領 `REQ-843`）。
> ⇒ ⭐ **判準：`covers_req` 的擁有者數⛔ 一律不等於「子句住在幾份檔裡」。**

> ⭐ **第二道判準（跟上改寫）**：一條 `point` 自述被**改寫／廢止／翻案**過，
> 而擁有它的 `exposes` ⛔ 一律沒有提到那次改寫 ⇒ 該 `exposes` 必須被重讀。
> ⚠️ ⭐ 它翻出來的第一件事⛔ 一律不是措辭 —— 是 `surface` 的 §1.5 **整節**都是
> `REQ-812` 2026-09-15 翻案**之前**的設計，而 code 早已落地。
> ⇒ 🔴 ⭐ 當時十二道 gate 全綠，因為該檔的 `upstream_spec_rev` 是**當天**的值
> —— 被後來幾批「本檔內容零變更，僅同步上游釘選」推上去的。
> ⇒ ⭐ **判準：`upstream_spec_rev` 追上了⛔ 一律不代表內容追上了。**
> ⚠️ 而「僅同步釘選」這個動作本身就是在簽名說「我讀過那次改動了」。

---

#### 4.1.1 `implements` 與 `test_seam` 的擁有權判準（spectra Round 14 `B1` 立；2026-09-04）

> ⭐ **這兩個欄位問的⛔ 不是同一個問題。** 把它們當成一件事一起搬，會**兩個方向都出錯**：該搬的沒搬、不該搬的搬走了，⇒ 而 `INV-D6`／`INV-D7` 的計數**全部是綠的**（每個 FUNC item 有人認、每個 vkp 有人暴露 —— 它們只檢「有沒有人」，⛔ 一律不檢「是不是這個人」）。

| 欄位 | 它問的問題 | 成立的判準 | 判紅的樣子 |
|---|---|---|---|
| `implements` | **誰讓這個行為成立** | 本檔的 `file_impact` 裡，**指得出哪一個檔／哪一節做了這件事** | 指不出落點 ⇒ 這條是別人的 |
| `test_seam` | **誰讓這件事驗得出來** | 本檔交付的東西讓它**可觀察**，且 `exposes` 指得出 `§` 座標 | 指不出座標 ⇒ 本檔沒有暴露它 |

**⭐ 兩者可以合法地分開。** 一份只建資料表的設計，可以擁有一條 seam 而**沒有**對應的 `implements`：

```
REQ-822-A3「凍結後停止催款」
  test_seam  TP-bil-086.vkp-1  ✅ 「訊息類型可依 Scheduled_Action_TBL.action_type 計數（§3.1）」
                                  ⇒ 建表的那份設計讓「催款次數 = 0」驗得出來
  implements FUNC-billing-frozen.FM-62  ⛔ 一律不成立
                                  ⇒ 讓催款停下來的是排程寫入端或訊息層，建表的那份沒有任何東西讓它停
```

⇒ ⭐ **一份設計能證明某件事發生了，而它⛔ 不是讓那件事發生的東西。**

**registry 型設計怎麼合法認領行為** —— 靠**逐列指名執行者座標**。若本檔有一張表逐列寫著「這個檢查放在 `unsettled_days_scan` 的逐帳號迴圈裡」，那本檔就是「決定檢查點放在哪」的那份設計 ⇒ 認領成立。沒有這張表就沒有落點 ⇒ ⛔ 不得比照。

**一條 `exposes` 只講一件事。** 一句話同時聲明兩件事時，⭐ **錯的那一半會被對的那一半掩護** —— 拆成兩條，各自帶自己的座標。

**寫完自檢（每份 DESIGN 各跑一次，⛔ 不得合併跑）：**

1. 逐條 `implements` 問：**本檔哪個 `file_impact` 條目做了它?** 答不出 ⇒ 移交。
2. 逐條 `test_seam` 問：**`exposes` 裡的 `§` 座標指向本檔的哪一節?** 答不出 ⇒ 移交。
3. 一個 FUNC item 被兩份 DESIGN 認領時（`INV-D6` 允許 ≥1），⛔ 必須在**兩份**裡各寫一行理由說明分工。⚠️ 只寫在一份裡，另一份的讀者看到的仍是「沒有人說為什麼」。
   ⭐ **理由⛔ 必須寫在**認領處**（`implements` 旁），⛔ 不得只寫在 Revision History**
   —— ⚠️ 看 `implements` 的人⛔ 一律不會往版本紀錄裡看（spectra Round 20 `C1`）。
   ⭐ **並且：新立一條紀律時，⛔ 一律要回頭掃它管轄的既有實例。**
   ⚠️ 本條就是實例：`FUNC-billing-signup.step-1` 是**第一條**雙認領，而本規則是它之後才立的
   ⇒ 後續三次補註（`FM-67`／`FM-59`／`FM-118`）**三次都沒有想到還有第四條**。
4. **`covers_func` 與 `implements` ⛔ 必須同進同出**（spectra Round 16 `B1`，2026-09-04 立）：
   `covers_func` ⊇ `{implements 用到的每一個 FUNC 前綴}`。
   ⚠️ ⭐ **而 `coverage_spine_integrity.py` 只驗 dangling**（「宣告的那個 FUNC-id 存不存在」）——
   反方向「用到的都宣告了嗎」⛔ 一律沒有人檢 ⇒ ⭐ **它的失敗方式是全綠**
   （`[[feedback_zero_regression_harness_needs_reverse_anchor]]`：零回歸 harness 必須雙向）。
5. **一個欄位一旦有兩份副本，就⛔ 必須有一條斷言綁住它們**（同上輪次）：
   `covers_func` 同時住 frontmatter 與 machine-block ⇒ 兩處⛔ 必須逐字相同。
   ⚠️ ⭐ 實例：`phase5` 的 rev `0.5` 逐字寫著「`covers_func` 補 signup／return」——
   ⇒ ⭐ **那件事做了，在兩個地方裡的一個**，而 gate 讀的正好是做對的那一個。
6. **frontmatter 的欄位名⛔ 一律小寫**（spectra Round 16 `C3`）：
   全 repo 三支讀 `status` 的 validator 皆為**大小寫敏感的小寫** ⇒ ⭐ 寫成 `Status:` 的文件對它們是隱形的。
9. **frontmatter 必填欄位**（spectra Round 20 `N1`）：`spec_type` · `schema_version` · `status` ·
   `upstream_spec` ＋ `upstream_spec_rev` · `covers_req` · `upstream_pins`；UI DESIGN 另加 §3.2 的欄位。
10. **`status` 的值域**（同上）：frontmatter 用 `Draft` / `Approved`（**文件成熟度**）；
   `Sign-off` 段用 `pending` / `signed-off`（**流程狀態**）—— ⭐ 兩者⛔ 一律不得互換。

8. **座標紀律的下一格：`§` ⛔ 必須是「本檔的」**（spectra Round 19 `B1`，2026-09-04 立）：
   Round 13 只寫了「`exposes` ⛔ 必須含一個 `§`」，⛔ 一律沒說那個 `§` 在哪一檔
   ⇒ ⭐ 實測 **26 條** seam 的每一個 `§` 都冠著別人的名字（`phase0 §…`／`phase5 §…`）。
   ⇒ ⭐ 判準升級：**每條 `exposes` ⛔ 必須至少有一個**⛔ 一律不冠他檔名**的 `§`，或句中明寫「本檔／本階段／本節的 X」。**
   ⚠️ ⭐ 理由回到 `§4.1.1` 的表：`test_seam` 問的是「**本檔交付的東西**有沒有讓它可觀察」——
   ⇒ **一條只說「這個欄位在 phase0 §3.1」的 `exposes`，描述的是 phase0 的交付。**
   ⭐ 可機檢：`§` 前 14 字內出現 `phase[0-7]`／`surface`／`階段 N` 即視為他檔座標。

7. **`Sign-off` 段⛔ 必須以 `status: <流程狀態>` 收尾**（spectra Round 16 `C1`）——
   ⚠️ ⭐ frontmatter 的 `status: Draft` 救不了這條：**兩個欄位語意不同**
   （`Draft` 是文件成熟度、`pending` 是 sign-off 流程狀態），而人盤點流程時查的是後者。

### 4.2 DESIGN↔Code 追溯（`@implements` 下沉程式碼)

> 延伸 repo 既有 **`@governed-by`**(檔案層,`ddd-doc-maintenance §3.6`)→ **function 層**。程式碼自帶「實現哪個需求」,人可 debug / review、防危險 refactor。

**machine-block 擴充欄:**
```yaml
  file_impact:                         # 建 / 改 / 刪哪些檔(≥1)
    - { path: static/js/card.js, change: modify }
  interface_signatures:                # 真型別(非 pseudocode);非 UI 亦含 SQL DDL
    - "exportNoteToPng(note: Note) -> bytes"
  migration_rollback: <path|n/a>       # schema/config 變則必;含 rollback path
```

> ⚠️ ⭐ **`change: modify` 帶著一個沒有寫出來的前提**（spectra Round 20 `C2`）——
> 它對**今天的 repo** 可能為假、對**該 spec 執行時**為真。
> ⇒ ⭐ **被 `modify` 的檔若由另一份 design spec `create`，該順序依賴 ⛔ 必須寫進〈依賴與前置〉。**
> ⚠️ 否則任何拿 `file_impact` 對 repo 核對的工具都會得到假紅，而**真的缺一個檔時看起來一樣**。

**程式碼註解(function 層):**
```js
// @implements FUNC-export-note.step-3 (realizes REQ-005-G1): 產生單則 PNG
// @enforces <invariant>                                       // 牽動需求的不變式
function exportNoteToPng(note) { ... }
```

| ID | 不變式 | 方向 | 檢法 |
|---|---|---|---|
| **INV-D8** | 每 DESIGN → ≥1 code entry(`file_impact`);每 code entry `@implements` → 指向存在的 FUNC step(且該 step 有 DESIGN)| DESIGN ↔ Code 雙向 | 未實作設計 / 未 spec 程式碼,皆 **HARD**(對映 framework G5)|

- **依賴註**:`@implements ... (realizes REQ-<id>-G<k>)` 的 claim-ID 尾綴依賴 **REQ rulebook 的 claim-ID 機制**(✅ **已落地 §3.4,2026-07-04**)。既有 backfill spec 的 claim-ID 為 lazy 賦(grandfather);未賦前 `(realizes ...)` 可暫省、`@implements FUNC-xxx.step-N` 為必要骨幹。
- validator(Track B)檢 `@implements` 指向存在的 FUNC step + `covers_func`/`implements`/`@implements` 三處一致。

### 4.3 Test Seam 設計（可測性,QA 不可協商)

- **`test_seam` 必填**(§4.1 已納 schema):每 `test_seam = {for_claim, for_key_point, exposes}` 宣告「為驗證哪個 claim 的哪個 validation_key_point、暴露什麼 hook / fixture / 可觀察 DSL」。
- **設計時檢**:每 TP 的 **validation_key_point** 必有對應 seam 暴露其 observable(INV-D7)——**缺 seam = QA blocker**(TC 寫不出 → 退回 Dev 補設計,對映 framework「Missing test seam」anti-pattern)。
- **seam 形式**:優先 **可觀察 hook**(`data-testid`、回傳值、狀態 DSL,對齊 sanity `system_state_assertions`),而非侵入式 mock;UI component 的 `data-testid` seam **收進 §3B `sig.json` describe() 快照**(視同結構;seam 增刪 → 快照變 → 抓得到),與「文字 / 顏色忽略」區隔。
- **反 gold-plating**:seam 只為既有 TP claim 開,不預留「未來可能要測」的 hook。

### 4.4 CRUD Delta + Write-time Sign-off（對齊 REQ rulebook §5.5)

- **角色**(對齊 framework §3.5):**💻 Dev = primary author**;**👔 PM**(matches intent)+ **🔬 QA**(testable seams)= reviewers。
- **write-time sign-off**:DESIGN 寫入前,async per-DESIGN 派 3-role sign-off，**有人決定就走**(non-blocking,對齊 REQ rulebook §5.5「有人決定就走」+ Verdict Annotation 無 terminal)。high-stakes(`risk_class != normal`)保留較強 gate;solo = collapse 1 張。
- **CRUD delta**:
  - **create** — 過 **INV-D6/D7**(通用)+ **UI 另過** §4.0 INV-D0 + §3 INV-D1~D5,才寫入。
  - **update** — 改 `implements`/`test_seam`/`file_impact` 觸發 §4.1/4.2 雙向重驗;改 `skeleton` = 破壞性(INV-D5)。
  - **delete** — 破壞性 → **PO-confirm 必做**;預設 Deprecate 優先於硬刪;DESIGN-ID 永不重用(對齊 REQ delete 規則)。

### 4.5 非 UI DESIGN（後端 module / SQL / 演算法)

- **§4.1–4.4 全適用**(covers_func / implements / test_seam / file_impact / interface_signatures / migration_rollback / sign-off / CRUD)——覆蓋、追溯、可驗、sign-off 不分 UI。
- **§3(markup 契約)不適用**:skeleton / tokens / layout_contract / negative_space / sig.json 為 UI 專屬。
- **impl-detail 具體寫法**(interface signature 風格、`ALTER TABLE` DDL、data flow、performance budget、security / PII boundary):參 **framework §3.5** 既有欄位(對齊 `[[backend-schema-change-workflow]]`)。
- **db_schema 變更**:走既有 backend schema 流程([[backend-change-rule]] propose-first;SSOT plural + startup auto-sync)。

### 4.6 標記紀律 —— 給 AI 讀的文件禁用裝飾性標記（PO 2026-09-04 立;write-time)

> 適用:**讀者是 AI 的文件**(REQ / DESIGN / FUNC / TP / TC / 提案 / review log)。
> 一句話:**標記不是資訊,句子才是。**

| 規則 | 內容 |
|---|---|
| `⛔` 的值域 | **只准接兩種**:①**禁令**(不得 / 不可 / 一律 / 禁)②**區辨**(X 不是 Y / 非 / 不代表 / 不等於) |
| 禁用 | `⛔` 接連接詞(而 / 且 / 但)、接粗體 `**`、接另一個 `⛔`、或單純語氣 |
| 重複標記 | `⛔⛔` / `⭐⭐⭐` 一律禁 —— 強調靠把句子寫清楚,不靠疊符號 |
| **作者自檢**(寫完必跑) | 把所有標記刪掉,**資訊有沒有少?** 沒少的那些即干擾 ⇒ 刪 |
| 可機檢紅線 | 把 `⛔` 後的空白與 `*` 剝掉,開頭**不是** `不得`／`不可`／`禁`／`一律`／`必須`／`不是`／`非`／`不代表`／`不等於`／`刻意` ⇒ 判紅;另加 `⛔⛔`／`⭐⭐` 疊字判紅。⚠️ **不得寫成「`⛔ **` 命中即判紅」** —— 那會把合法的 `⛔ **不得…**` 誤判,而會誤報的 gate 會被關掉。另:被反引號包起來的符號是在**講**它、不是在**用**它 ⇒ 豁免(否則本規則自己的說明文字會判紅)。⚠️ **該豁免必須在執行腳本裡實作** —— 2026-09-04 實例:phase1 spec 的「標記約定」那一行寫著 `` `⛔` 只用於… ``,而清理腳本只看「符號後面接什麼字」⇒ 它後面接的是反引號 ⇒ 被判為裝飾刪掉 ⇒ **讀者無法從該檔得知那條規則講的是哪一個符號**。⭐ 判準:**一條規則若有豁免條款,那個豁免必須跟執行者一起交付 —— 否則規則會先吃掉自己。** |

**為什麼**:裝飾標記對 AI 讀者除了佔 token,還**主動誤導** —— 「被標記」暗示「這裡有邊界」。
實測(2026-09-04,`bizcard-billing-phase0-schema-design-spec.md` 1,217 行):687 個 `⛔` 中僅 **21%** 是禁令或區辨、**32%** 是純裝飾
⇒ 符號失去鑑別力 ⇒ 讀者學會忽略它 ⇒ **真正那 10% 的禁令跟著一起被忽略**。
⇒ **沒有標記只是沒有捷徑;壞掉的標記是一條把人帶到錯地方的捷徑。**

⇒ review 端由 `spectra-review` SKILL **維度 H** 兜底(兩份 SKILL 副本皆已寫入)。


### 4.7 「檢查表」狀態欄的值域（spectra phase3 Round 3 `B1` 立;phase6 Round 3 `B2` 升為 rulebook)

> 適用:design spec 內任何一張**狀態欄用 emoji 表示進度**的檢查表(如 `08` code review 檢查表)。

| 值 | 意思 |
|:--:|---|
| `✅` | **本階段已經成立** —— ⭐ 有執行者、**且它已經寫好** |
| `🟡` | 本階段已把它**設計完**,而**執行者還沒寫** |
| `🔴` | 本階段已知它**不成立**(含「設計上做不到」與「已判定為缺陷」) |
| `—` | ⛔ 一律不屬本階段 |

⭐ **判準:一張「檢查表」的狀態欄,讀者一律讀成「驗過了」,⛔ 不是「想過了」。**

⚠️ ⭐ **為什麼要升成 rulebook(⛔ 一律不是抄六份)**:
本值域立於 2026-09-04 的 phase3 Round 3,⇒ 而 **2026-09-05 實查:全 repo 只有 phase3 一份寫了它**,
其餘六份 design spec 合計 **24 格 `✅`** —— ⭐ **而該專案至今⛔ 一律沒有寫過任何一行 `.py`**
(十份 design spec 皆 `status: pending`,各自逐字寫「sign-off 前⛔ 不得產生任何 `.py`」)
⇒ ⭐ **在本值域下那 24 格沒有一格成立。**
⇒ 對齊 `[[feedback_scope_by_signature_not_discipline]]`:
**同型缺陷修過一輪還漏 ⇒ ⛔ 一律停止補個案** —— ⭐ 判準要住在**一個地方**,而⛔ 不是六份副本。

✅ ⭐ **2026-09-05 已有 gate**:`lint.sh` **Stage 50**(`scripts/spec_status_column_check.py`,BLOCKING)。
範圍＝`spec_type: design-spec` ＋ 首欄表頭是 `#` ＋ 有一欄叫「狀態」;
`status: Draft|pending` 的檔內該欄出現 `✅` 即判紅,值域外亦判紅。
⚠️ ⭐ **範圍是實跑兩次收出來的,⛔ 一律不是一次寫對**:
① 首版判準是「有一欄叫狀態」⇒ 對 **OQ 表**(狀態欄寫「待 PO 拍板」)、`delivered` 值域表、
〈依賴與前置〉表**全部誤報**;② 第二版忘了限定 `design-spec` ⇒ requirement spec 的 OQ 表仍中。
⇒ ⭐ **一條讀起來完全合理的判準,實跑一次就證明它會誤報 —— 而會誤報的 gate 會被關掉。**


### 4.8 節標題裡⛔ 一律不寫「清單的長度」（spectra phase5 Round 4 立;phase6 Round 6 再立;Round 10 升為 rulebook)

> 適用:design spec 的**節標題**(`##` / `###` / `####`)。

| | |
|---|---|
| ⛔ **禁止** | 標題裡出現「幾個／幾種／幾列／幾類／幾張」而那個數字 ＝ **某張表或某份清單的長度**(例:「五個產物」「四個判準」「三種情境各自…」) |
| ✅ **允許** | 數字是**內容本身**而⛔ 一律不是清單長度(例:「兩條 SQL 的歸屬」「一個新模組」「兩層用詞」) |
| ✅ **例外** | 數目由**上游 AC 逐字釘死**時可寫,⇒ 而⛔ 一律必須在括號裡指名那條 AC(例:「三種可客觀判定的情境(`REQ-830-AC-3`)」)—— ⚠️ 它變的時候上游會先變 |

⭐ **理由(⛔ 一律不是排版偏好,是兩次實測)**:
**標題是唯一一個改表時不會被順手看到的地方** —— 改的人在表格裡。
⇒ 而讀者 `⌘F` 到那一節時,**標題是他讀到的第一行**。
⚠️ ⭐ 更貴的一種:**標題裡的數字⛔ 一律不會被表格反駁,它會被表格掩護**
—— 讀者發現不一致時會去看表,而表是對的。

⚠️ ⭐ **兩次獨立發生(2026-09-05 同一天)**:
`phase5` rev `0.9` 標題寫「四個產物」而 Round 4 之後是五個 ⇒ 該檔立了這條;
`phase6` §1.1「四個判準」「§3.3 三種情境」在 Round 1–3 被改成六／五而標題留著 ⇒ 該檔又立了一次。
⇒ ⭐ **同一條紀律一天之內在兩份檔各自被「發現」一次,而兩次都留在自己那份檔裡。**
⇒ 對齊 `[[feedback_scope_by_signature_not_discipline]]`:**判準要住在一個地方,⛔ 一律不是 N 份副本。**

🔴 ⭐ **本節⛔ 一律刻意沒有 gate(PO 2026-09-05 拍板)** ——
⚠️ 它的**例外**是「上游 AC 逐字釘死且括號指名該 AC」,⇒ ⭐ **那是語意判斷,正規式判不出來**
⇒ 它一定會誤報。⚠️ ⭐ 而更貴的是:若把它與 §4.7 的 gate 寫在同一支,
⭐ **它一誤報,§4.7 那一半會跟著被一起關掉。**
⇒ ⭐ **判準:一條規則能不能進 gate,問的⛔ 一律不是「它重不重要」,是「它的例外能不能被判定」。**
⭐ **且驗它的檢查⛔ 一律不得是 needle 型**:phase6 Round 6 用固定關鍵詞掃過一次而漏了 5 處,
⇒ Round 10 用真判準重跑才抓到。

---

### 4.9 編號清單的列序⛔ 一律不得中途反向（spectra phase6 Round 10／16／20 各立一次;2026-09-05 改成 gate)

> 適用:spec 內任何一段**連續的編號清單** —— markdown 表的首欄編號(`| 3 |`／`| **D-9** |`)、
> YAML 的 `- AC-<n>:` 與 `- id: <TP>.vkp-<n>`。

| | |
|---|---|
| ⛔ **禁止** | 一段清單裡的編號**中途反向**(`1…8, 10, 9`)、或**重號**(兩條 `D-2`) |
| ✅ **允許** | 一路遞增**或**一路遞減 —— ⚠️ 本 repo **兩種慣例並存**(`bizcard-billing` 家族新到舊、`report-entry-parity` 家族舊到新) |
| ✅ **允許** | **跳號**(`1, 4, 9`)—— 那是「ID 永不重用」的正常結果 |

⭐ **真正的規則⛔ 一律不是「要排序」,是「插入時的錨要取最大編號」** ——
⚠️ 錨取「上一次插入的那一列」時,它插對的那幾次是**巧合**。

⚠️ ⭐ **為什麼這一條直接跳過「寫一條散文判準」那一步**:
同一個錯在 2026-09-04～09-05 兩天內發生 **六次**,
⇒ ⭐ **而第三／四／五／六次全部發生在「剛剛才修好它、並且寫下一條判準」之後的同一天**
(其中一次:判準逐字寫「⛔ 一律不得用上一次插入的那一列當錨」,兩輪後我加 `D-10` 用的錨正是 `D-9`)。
⇒ ⭐ **寫下「這是第 N 次」⛔ 一律不會讓第 N+1 次不發生。**
⇒ ⭐ **判準(升為通則):當同一個錯誤出現第三次時,⛔ 一律不得再寫第三條散文 ——
那時候要問的是「這件事能不能用一支程式判定」。** 能,就寫 gate;⛔ 一律不能,就寫下它為什麼不能(§4.8)。

✅ ⭐ **gate**:`lint.sh` **Stage 49**(`scripts/spec_numbered_sequence_check.py`,BLOCKING)。
⚠️ ⭐ **它的範圍也是實跑收出來的**:首版判準寫「⛔ 必須遞增」⇒ **當場 140 紅,而其中絕大多數是對的寫法**
(`decision-log.md` 與每一份 Revision History 都是刻意由新到舊)⇒ 改成**單調**;
且 `FM-<n>` **刻意排除** —— 它的編號是全域取空號,而位置跟的是 `handles:` 的 anti 順序,兩者本來就不一致。

## 4Z. TODO — 尚待補（隨 Track B / 後續)

- **coverage validator 家族**(Track B):`REQ↔TP · REQ↔FUNC · TP↔TC · FUNC↔DESIGN(implements)· TP↔DESIGN(test_seam)· DESIGN↔Code(@implements)`——本檔 §4.1/4.2 的不變式對應的機檢實作。
- **跨 rulebook 依賴(2 個 ID 機制,✅ 皆已落地)**:(a) **claim-ID** — REQ rulebook **§3.4**(D-028);`@implements ... (realizes REQ-<id>-G<k>)` 尾綴依賴之;(b) **validation_key_point ID** — TP rulebook **§4.2**(`TP-<id>.vkp-<n>`);`test_seam.for_key_point` 依賴之,INV-D7 據此機檢。既有 backfill spec 的 ID 為 lazy 賦(grandfather),未賦前對應欄位可暫省、骨幹(FUNC step / claim)為必要。
- **INV↔驗法歸屬**(now 明列,實作在 Track B):
  - **`sig.json` describe() diff**:INV-D0(shell 樹)· D2(scoping)· D5(結構凍結)
  - **DESIGN yaml 靜態解析**:INV-D1/D3/D4(欄位/值 presence)· D6(implements↔FUNC)· D7(test_seam↔TP key_point)
  - **code 註解 grep**:INV-D8(`@implements` ↔ FUNC step ↔ file_impact)

---

## 5. Decision Log

裁決紀錄見 `docs/pm/spec-authoring/decision-log.md`(本節相關:**D-026**(§3 建立)+ **D-027**(§4 通用 authoring)+ spectra R1/R2/R3/R4 **D-spectra-designrules-1/2/3/4**)。

## 6. Revision

| Rev | Date | Change |
|---|---|---|
| 2026-09-05.2 | 2026-09-05 | ⭐ **新增 §4.8「節標題裡⛔ 一律不寫清單的長度」**(spectra phase6 Round 10 `B2`)。⚠️ ⭐ **同一條紀律 2026-09-05 一天之內在 phase5 與 phase6 各被獨立立了一次,而兩次都留在自己那份檔裡** ⇒ 升為 rulebook(同 §4.7 的處置)。⭐ 界定範圍:只管「數字 ＝ 清單長度」,⛔ 一律不管「數字 ＝ 內容本身」;例外＝上游 AC 釘死且括號指名。⭐ 並記下**驗它的檢查⛔ 一律不得是 needle 型**(Round 6 用固定關鍵詞掃過而漏 5 處)。|
| 2026-10-05.0 | 2026-10-05 | ⭐ **新增 §4.1.2 `INV-D7` 第三格的執行者**（PO 2026-10-05「accept recommends, 2->1 ->3 . go」；log:`docs/reviews/2026-10-05-spectra-bizcard-billing-design-spec-family-round-5-fixes.md`）。⭐ 兩條作者紀律 ＋ 機檢 `scripts/spec_vkp_scope_declaration_check.py`（lint Stage 165）。🔴 ⭐ 並**逐字記下兩條實跑失敗的路**（絕對 token 重疊 73% 誤報／兄弟 vkp 相對重疊⛔ 一律沒抓到已知的那一條）＋ 它們為什麼是同一個信號 ⇒ ⛔ 一律不要再試第三種 token 相似度。⭐ 另記兩條判準：**`covers_req` 的擁有者數⛔ 一律不等於「子句住在幾份檔裡」**、**`upstream_spec_rev` 追上了⛔ 一律不代表內容追上了**。 |
| 2026-09-05.1 | 2026-09-05 | ⭐ **新增 §4.7「檢查表」狀態欄的值域**(spectra phase6 Round 3 `B2`,log:`docs/reviews/2026-09-05-spectra-bizcard-billing-phase6-rounds.md`)。⚠️ ⭐ **該值域立於 2026-09-04 的 phase3 Round 3,而實查全 repo 只有 phase3 一份寫了它** —— 其餘六份合計 **24 格 `✅`**,⇒ 而該專案至今零行 `.py` ⇒ **沒有一格成立**。⭐ 升為 rulebook 而⛔ 一律不抄六份(對齊「停止補個案」)。|
| 2026-09-05.0 | 2026-09-05 | ⭐ **本檔自身的 §4.6 收尾** —— 清掉 a11y／對比度段落裡最後 5 處違反 §4.6 的 `⛔`(`:142` 純語氣改 `⚠️`;`:162` 兩處補值域詞;`:180`／`:189` **把標記移到真正的區辨那半句**)。⚠️ ⭐ **它們是合併 `main` 時浮出來的**:`2026-09-04.0` 那次清理與 §4.6 條文本身(2026-09-05 由另一條線寫入)各自只看到自己那一半 ⇒ ⭐ **兩邊都以為清乾淨了,而合併後的檔仍有 5 處。**⇒ 判準:**一條規則與它的執行者若在兩條線上各自演進,「各自都綠」⛔ 一律不代表合起來是綠的** —— 收尾判準只能跑在合併後的檔上。⛔ 一律零條文變更(只動標記)。 |
| 2026-09-04.3 | 2026-09-04 | ⭐ **§4.1.1 補第 9／10 條 ＋ 第 3 條補句 ＋ §4.2 補 `change: modify` 的前提**(spectra Round 20)。⭐ 本輪的做法是**逐條問「這條紀律沒說的那一格是什麼」** —— 八條裡兩條有洞、四條實跑乾淨、兩條靜態不可判;⚠️ ⭐ **兩個洞都⛔ 一律不是靠撞到實例找出來的**。零 DB、零 `.py`、零 pip。 |
| 2026-09-04.2 | 2026-09-04 | ⭐ **§4.1.1 補第 8 條:座標⛔ 必須是「本檔的」**(spectra Round 19 `B1`)。⚠️ ⭐ **這是同型的第三次** —— Round 13 寫了「⛔ 必須有 `§`」而沒寫「`§` 要在本檔」;Round 16 寫了「宣告的 id 要存在」而沒寫「用到的要宣告」。⇒ ⭐ 判準:**每寫下一條紀律,一律要再問一次「它沒說的那一格是什麼」。**零 DB、零 `.py`、零 pip。 |
| 2026-09-04.1 | 2026-09-04 | ⭐ **§4.1.1 補第 4–7 條**(spectra Round 16,log:`docs/reviews/2026-09-04-spectra-bizcard-billing-func-tp-phase0-round-16.md`)。**④** `covers_func` ⊇ `implements` 用到的 FUNC 前綴 —— ⚠️ ⭐ `coverage_spine_integrity.py` **只驗 dangling**,反方向⛔ 一律沒有人檢 ⇒ 失敗方式是全綠(實例:`phase5` 的 machine-block 少兩個 id 而 gate 逐字回「spine OK (58 refs)」)。**⑤** 一個欄位有兩份副本時⛔ 必須有斷言綁住它們。**⑥** frontmatter 欄位名⛔ 一律小寫(三支 validator 皆大小寫敏感)。**⑦** `Sign-off` 段⛔ 必須以 `status:` 收尾 —— ⭐ 盤點流程狀態的人 grep 的是它,⛔ 不是 frontmatter 的成熟度。⚠️ 雙向 gate 本身是 `scripts/*.py` ⇒ **需 PO 授權**,腳本已備於 scratchpad(帶突變自檢),本輪⛔ 一律不落地。 |
| 2026-09-04.0 | 2026-09-04 | ⭐ **新增 §4.1.1 `implements` 與 `test_seam` 的擁有權判準**(spectra Round 14 `B1`,來源:`docs/reviews/2026-09-04-spectra-bizcard-billing-phase0-round-14.md`)。⇒ 兩欄問的⛔ 不是同一個問題:`implements` 問「誰讓這個行為成立」(判準:`file_impact` 裡指得出落點)、`test_seam` 問「誰讓這件事驗得出來」(判準:`exposes` 指得出 `§` 座標)。⚠️ `INV-D6`／`INV-D7` 只檢「有沒有人」,⛔ 一律不檢「是不是這個人」⇒ 兩欄各自搬錯時**計數全綠**。含 registry 型設計的合法認領形狀(逐列指名執行者座標)、「一條 `exposes` 只講一件事」、以及三步寫完自檢(雙認領⛔ 必須兩份都寫理由)。<br>⚠️ 順帶清掉本檔自己違反 §4.6 的 5 處裝飾性 `⛔`(標題／`不視為違規`／`不適用` 等)——⭐ **一份帶著自己規則違例的 rulebook,讀者會學到那條規則是可以不遵守的。** |
| 2026-07-04.0 | 2026-07-04 | cascade:REQ §3.4 **claim-ID**(D-028)+ TP §4.2 **vkp-ID**(D-029)皆落地 → §4.2 依賴註 + §4Z 跨 rulebook 依賴註更新為「✅ 已落地」(lazy 賦 grandfather 說明保留) |
| 2026-07-03.8 | 2026-07-03 | spectra §4 R3 fixes(accept,C1 + N1):C1 **INV-D0/App Shell UI-only 誤置通用** → §4.0 標題+開頭註 UI-scoped、§4.4 create gate 把 D0 移 UI bracket、§4 開頭加 **UI INVs=D0–D5 / 通用 INVs=D6–D8** 分類句;N1 shell 檔僅 UI-bearing 專案有(§4.0 註)。**UI/通用 INV 邊界無歧義 → §4 定稿** |
| 2026-07-03.7 | 2026-07-03 | spectra §4 R2 fixes(accept,C1 + N1 + N2):C1 §4.3 描述對齊 §4.1 schema(`test_seam = {for_claim, for_key_point, exposes}` + 「每 validation_key_point 必有 seam」,消 R1 漏傳的舊 2 欄/「TP claim」措辭)/ N1 §4Z 明列 2 個跨 rulebook ID 依賴(claim-ID + vkp-ID)/ N2 claim 收斂 diagram 標 `for_key_point`。**§4 schema-prose 自洽 → 定稿** |
| 2026-07-03.6 | 2026-07-03 | spectra §4 R1 fixes(accept,C1–C2 + N1–N3):C1 `test_seam` 綁 `for_key_point`(非只 claim)+ INV-D7 檢暴露 validation_key_point observable(校回 exec-plan §4H 原意,補可測性洞)/ C2 machine-block **組合表**(UI=共用+UI專屬 / 非 UI=僅共用)/ N1 INV↔驗法歸屬明列(sig.json / yaml / code grep 三分)/ N2 app shell 改 `_shell/` 專案級路徑 / N3 `data-testid` seam 收進 §3A.1 describe() 快照 |
| 2026-07-03.5 | 2026-07-03 | **§4 通用 DESIGN authoring 補全**(D-027):§4.0 App Shell 契約(INV-D0,`skeleton.region` SSOT)/ §4.1 DESIGN↔FUNC+TP 完整性不變式(INV-D6 implements 雙向 / INV-D7 test_seam 雙向;claim 收斂點)/ §4.2 DESIGN↔Code 追溯(INV-D8;`@implements` 下沉,延伸 @governed-by 到 function 層)/ §4.3 test seam(QA 不可協商)/ §4.4 CRUD + 3-role sign-off(對齊 REQ §5.5)/ §4.5 非 UI DESIGN(§4.1–4.4 適用、§3 不適用、impl-detail 參 framework §3.5);§4Z 留 Track B validator 家族 + claim-ID 依賴 |
| 2026-07-03.4 | 2026-07-03 | spectra R4 fixes(accept;verdict ship-as-is,澄清級):C1 `reflow_isolation` 定位 = **選填 opt-in**(非 INV 必填;`contain` clip 副作用故由 component 視內容宣告;gate 只驗宣告即正確編譯)/ N1 `skeleton.region` forward-ref → 補 **§4.0 App Shell 契約**待辦(頂層 grid-template-areas registry SSOT)。**§3 表-body drift 清零 + 核心機制 enforcement 定位完成 → 真正定稿** |
| 2026-07-03.3 | 2026-07-03 | spectra R3 fixes(accept,C1 + N1 + N2):C1 INV 表 D2/D3 row 對齊 §3.4/§3.5 白名單(消「一律」絕對語氣殘留)/ N1 `white_space` 必填欄語意含 `overflow-wrap`(長無空白字串斷行防線)/ N2 全形括號改半形。**§3 Component Markup Contract 內部完全自洽 → 定稿** |
| 2026-07-03.2 | 2026-07-03 | spectra R2 fixes(accept recommends,C1–C2 + N1–N3):C1 wrap 屬性三處對齊(schema 加 `white_space` 必填欄 + INV-D1 必填集改 max_width/overflow/white_space、text_wrap 降選填 + §3.6 交叉錨)/ C2 INV-D3 gate 範圍鎖顏色·間距·尺寸 + 全域字面值白名單放寬(1px/transparent/Nfr…)/ N1 非純 component 逃生門補「Tier 2 前走人工真機檢」/ N2 sig.json 標 git-tracked golden / N3 INV-D4 `long_string` 恆必含消歧 |
| 2026-07-03.1 | 2026-07-03 | spectra R1 fixes(accept recommends,C1–C6 + N1–N3):C1 WebView 支援底線(§3.6)/ C2 describe() 純函式前置(§3A.1)/ C3 sizing token + 常數白名單(§3.5)/ C4 INV-D4 negative_space 按性質 + n/a escape / C5 INV-D2 完整豁免白名單(§3.4)/ C6 Primary 範圍收斂 UI markup(§1)/ N1 fixture 路徑 / N2 covers_func mesh 註 / N3 INV-D5 enforcement 待 gate |
| 2026-07-03.0 | 2026-07-03 | 新建;首節草稿 §3 Component Markup Contract(5 不變式 + runtime-create describe() 快照 + Tier 分級 gate);4 鎖定決策(D-026);§4 其餘節 TODO |
