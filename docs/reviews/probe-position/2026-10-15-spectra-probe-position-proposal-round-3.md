---
target: docs/pm/probe-position/PROPOSAL.md
target_rev: 3498c2e (rev 3)
date: 2026-10-15
reviewer: spectra-review (v2.0)
iteration: 3
verdict: ship-as-is
schema_version: enhanced-v1
contract_version: spectra-contract-v1
mode: pm-skill-generic-doc
---

> 💡 spectra-review v2.0 active(Minerva 4 能力 framework)。若想用原版簡潔版,用 `/spectra-review --lite <target>`。

🎯 Mode: PM Skill — Generic doc (target: docs/pm/probe-position/PROPOSAL.md)

# Spectra-Review Round 3 — docs/pm/probe-position/PROPOSAL.md

本輪範圍與限制:
- 對象是 rev 3(commit 3498c2e)。先逐項驗證第 2 輪 13 個 finding 的修正,再找新問題,重點放在 rev 3 改動的段落:§5.5 狀態優先順序表、§5.1 `render`/`startup`/`apply(names=None)`、`initdb` 匯入名稱、§5.3 自動帶入條件、§5.7 Excel 當日位置規則、§5.8 降版列、§10 依賴段落。
- 對照來源:規格書 3.13 POS-01～09(規格書:1074-1092)、3.7.1 欄位表(規格書:460-477),以及程式碼(各 finding 的 evidence)。
- 第 3 節 PO 決定不重新討論;第 10 節只檢查依賴段落是否清楚。
- SKILL 提到但本 repo 沒有的檔案(docs/CONTEXT.md、pm-skill-proposal.md 等)略過。依呼叫者指示只寫 F1,不更新 F2 與 decision-log。

## § 1. Mental Lens

- **Claim → Evidence → Verdict**:rev 3 新增的程式行為描述逐句對照原始碼,例如「`sync.startup` 讀名稱」(sync.py:103-121)、「舊版讀定義檔不驗證」(sync.py:94-116、definition.py:22-32)、「新增探頭預設『探頭 N』」(settings_dialog.py:1219-1227、lan.py:51-54)。
- **Cross-section consistency**:§5.2 顯示名稱規則與 §5.1、§5.3 的訊息範例互相對照;§5.5 表格的「只顯示最前面的一個」與各列的內容對照;提案 §5.3 與規格書 POS-09 對照。
- **Anti-Bias**:F2 把第 2 輪全部標為 fixed,本輪不採信,逐項回到 rev 3 原文確認。
- **Understand-not-argue**:rev 3 的修正方向都正確。以下 finding 都是文字修訂可以補上的缺口,不需要改設計。

### 第 2 輪修正驗證

| R2 ID | 結果 | 依據 |
| --- | --- | --- |
| C1 | 成立 | 表格補上整台設備異常(PROPOSAL.md:239),對應 `_on_detected` 的 `s.error` 分支(main_window.py:1240-1245);頂端提示改為各自顯示(PROPOSAL.md:233);維修中加 IP 不符沿用現行顯示(main_window.py:439)。規格書 POS-05 已同步(規格書:1078)。表格另有一個既有的歧義,見本輪 C1 |
| C2 | 成立 | `render` 一律帶名稱,`startup` 讀名稱,`names=None` 表示不變(PROPOSAL.md:121);§6 sync.py 列與 §7 校準後保留名稱的驗收都已補上(PROPOSAL.md:302、326)。這個修正帶出一個部署順序的新問題,見本輪 C4 |
| C3 | 成立 | 規格書 POS-04 改為「UI-11 的縮放以『列』計算」(規格書:1077),與 PROPOSAL.md:227 一致 |
| C4 | 成立 | §0 改為「每個事項下都列出依賴它的段落」(PROPOSAL.md:13),§10 四點都列出依賴段落(PROPOSAL.md:362-365) |
| N1 | 成立 | 條件 1 改為「探頭 N」格式,條件 2 加預設名稱(PROPOSAL.md:186-187);但規格書沒有跟著改,另外新設備的預設名稱沒有涵蓋,見本輪 C3 |
| N2 | 成立 | PROPOSAL.md:264 寫明位置取當日最後一筆 |
| N3 | 大致成立 | 降版列改寫(PROPOSAL.md:279);描述仍不完整,見 N4 |
| N4 | 成立 | grep 改為全部的「排」逐一分類,並列出已知要改的地方(PROPOSAL.md:328) |
| N5 | **部分成立,重開為 C2 與 N2** | 佔用者改為「以顯示名稱(§5.2)稱呼」,但 §5.2 的規則會讓已設定位置的佔用者顯示為「排1 點3」;另外「只設其一」的兩種訊息格式仍然並存 |
| N6 | 成立 | §6 補上 `PointResult`、`MemorySink`、`_download`、`import_file`、`initdb`(PROPOSAL.md:303、306、307) |
| N7 | 成立 | PROPOSAL.md:225 |
| N8 | 成立 | §9 新增一條(PROPOSAL.md:354) |
| N9 | 成立 | §6 寫明內嵌 Schema 整份改為與程式相同(PROPOSAL.md:291) |

## § 2. 4-Tier Findings

### 🔴 BLOCKERS — 落地前必修

(none found)

本輪的問題都可以用文字修訂解決,不會造成資料遺失,也不會讓實作方向錯誤。

### 🟡 CONCERNS — 應修

#### C1. 狀態表中「IP 不符」與探頭狀態、量測結果互斥,和「照常量測」矛盾

**📛 命名(Identify):** §5.5 寫「方塊同時符合多個狀態時,依下列優先順序顯示最前面的一個(IP 不符例外,見第 1 列)」(PROPOSAL.md:233)。IP 不符是第 4 列,探頭無回應／未校準是第 5 列,量測結果是第 6 列(PROPOSAL.md:240-242)。

**📣 主張(Assert):**
- 照字面讀,使用中設備 IP 不符、但仍連得上時,這台每個方塊只顯示「IP 不符」:量測值、合格／偏高／偏低、探頭無回應都被蓋掉。可是第 4 列自己寫「照常量測」,結果橫幅也照常判定,作業員卻看不到是哪一點不合格。
- 現行程式的 IP 不符是整排的邊框與排頭標示,方塊內容不受影響(main_window.py:419-441、1086-1103)。改成一台對多個方塊後,沒有排頭可以標,所以要寫明它在方塊上是「附加標示」還是「取代內容」。目前括號只排除了第 1 列(維修中),等於明示其他列都互斥。
- 連得上又 IP 不符的情況不常見(例如 ARP 記到的舊 IP 還沒更新,`lan.ip_mismatch` 只比對 seen_ip 與設定值,lan.py:361-363),但 M3 的 UI 測試要依這張表寫,歧義會直接變成實作差異。
- Impact 4/10 / Probability 0.4 → 1.6
- Evidence: PROPOSAL.md:233、240-242;app/flatness/ui/main_window.py:419-441、1086-1103;app/flatness/lan.py:361-363
- Cross-Module Impact:main_window(ProbeTile 顯示)、M3 UI 測試、DSC-20 驗收
- Phase-aware:M3 實作前要定案。

**🎯 追求(Pursue):** 把互斥範圍限定在整台狀態(第 1～3 列)與探頭內容(第 5～6 列)之間;IP 不符改寫為「附加標示:警告色框加『IP 不符』字樣,方塊內容依第 5～6 列照常顯示;與第 2、3 列同時成立時只顯示第 2、3 列」。括號改為「IP 不符為附加標示,見第 4 列」。

**📊 Decision Tree:**

| Option | 動作 | 成本 | 備註 |
| --- | --- | --- | --- |
| A | 不修 | 0 | M3 依字面實作,IP 不符時看不到量測結果 |
| B | 現在修(改寫第 4 列與括號) | 0.5h | 推薦 |

**📍 推薦:** Option B
**🔮 反事實:** 第 2 台 ARP 記到舊 IP 時,分佈在兩排的 4 個方塊只顯示「IP 不符」;橫幅顯示不合格,作業員卻找不到是哪一點。

```yaml
- {tier: 🟡 CONCERN, id: C1, name: "IP 不符在方塊上與探頭狀態、量測結果互斥,和「照常量測」矛盾", evidence: ["PROPOSAL.md:233", "PROPOSAL.md:240-242", "app/flatness/ui/main_window.py:419-441"], severity: {score: {value: 1.6, default: 1.6, override: null}, band: low, semantic: how_bad}, fix_economics: {difficulty: {value: 0.3, default: 0.3, override: null}, roi: {value: 5.3, default: 5.3}, resource_estimate: {value: "1h", default: "1h", override: null}}, cross_impact: {affected_modules: [main_window, M3 測試], cascade_depth: 2, dependency_chain: "狀態表 → ProbeTile 顯示 → M3 驗收"}, phase_aware: {current_phase: 0, if_not_fixed_now_breaks_at: 3, estimated_rework_cost: low}, decision_tree: {options: [{id: A, action: 不修}, {id: B, action: 改為附加標示}], recommended_option: B, counterfactual: "IP 不符時量測結果被蓋掉"}, dependencies: {blocks: [], blocked_by: [], manual_blocks: []}, severity_decay: {phase_when_found: 0, by_phase: {3: {value: 2.0, default: 2.0, override: null}}}, po_decision: {status: no_decision}}
```

#### C2. 佔用者「以顯示名稱稱呼」與 §5.2 規則衝突,會產生「排1 點3 已由 排1 點3 使用」

**📛 命名(Identify):** §5.1 寫「訊息以顯示名稱(§5.2)稱呼佔用者,例『排1 點3 已由 第 2 台 中排 探頭 1 使用』」(PROPOSAL.md:140);§5.3 選單範例「3(已由 第 2 台 中排 探頭 1 使用)」(PROPOSAL.md:179)。

**📣 主張(Assert):**
- 佔用者一定已設定位置。依 §5.2,已設定位置的探頭顯示名稱是「排名稱＋位置名稱」(PROPOSAL.md:154)。所以照規則,範例裡的佔用者應該寫成「排1 點3」(自動帶入後位置名稱就是「點3」),訊息變成「排1 點3 已由 排1 點3 使用」。工程人員最需要知道的「是哪一台的哪個探頭」反而不見了。
- 兩個範例用的其實是「未定」的格式(第 N 台 名稱 位置名稱),和 POS-02 的範例「第 2 台 中排 左」一致(規格書:1075)。範例是對的,規則寫錯了。
- §5.3 變更清單的範例「第 2 台 中排 探頭 1:未定 → 排1 點2」(PROPOSAL.md:204)也是同一種情況:位置一改,顯示名稱就跟著變,沒有寫用改之前還是改之後的名稱。
- 這是第 2 輪 N5 的修正方式帶出來的:N5 建議「佔用者用『第 N 台 名稱 位置名稱』」,rev 3 改成「用顯示名稱」。
- Impact 3/10 / Probability 0.7 → 2.1
- Evidence: PROPOSAL.md:140、154-157、179、204;規格書:1075(POS-02)
- Cross-Module Impact:lan.validate 訊息、settings_dialog 選單與變更清單、§5.2 使用處清單
- Phase-aware:M1(`lan.validate` 訊息)就會用到。

**🎯 追求(Pursue):** §5.2 加一種稱呼「設備稱呼:第 N 台＋DL-EN1 名稱＋位置名稱」,用在佔用者、衝突訊息、設定頁變更清單(不論是否已設定位置);顯示名稱只用在作業員看的地方(橫幅、頂端、3D、Excel)。把 §5.1 的「以顯示名稱(§5.2)」改為「以設備稱呼(§5.2)」,§5.2 使用處清單中的「設定頁變更清單與檢查訊息」移到設備稱呼。

**📊 Decision Tree:**

| Option | 動作 | 成本 | 備註 |
| --- | --- | --- | --- |
| A | 不修 | 0 | 實作者照規則或照範例,結果不一 |
| B | 現在修(§5.2 分兩種稱呼) | 0.5h | 推薦 |

**📍 推薦:** Option B
**🔮 反事實:** 選單顯示「3(已由 排1 點3 使用)」,工程人員要逐台打開設備才找得到佔用者。

```yaml
- {tier: 🟡 CONCERN, id: C2, name: "佔用者以顯示名稱稱呼,已設定位置時變成「排1 點3 已由 排1 點3 使用」", evidence: ["PROPOSAL.md:140", "PROPOSAL.md:154", "PROPOSAL.md:179", "PROPOSAL.md:204", "規格書:1075"], severity: {score: {value: 2.1, default: 2.1, override: null}, band: low, semantic: how_bad}, fix_economics: {difficulty: {value: 0.3, default: 0.3, override: null}, roi: {value: 7.0, default: 7.0}, resource_estimate: {value: "1h", default: "1h", override: null}}, cross_impact: {affected_modules: [lan.validate, settings_dialog, §5.2], cascade_depth: 2, dependency_chain: "§5.2 規則 → 驗證訊息 → 選單標示"}, phase_aware: {current_phase: 0, if_not_fixed_now_breaks_at: 1, estimated_rework_cost: low}, decision_tree: {options: [{id: A, action: 不修}, {id: B, action: 分顯示名稱與設備稱呼}], recommended_option: B, counterfactual: "佔用訊息自我指涉,看不出佔用者"}, dependencies: {blocks: [], blocked_by: [], manual_blocks: []}, severity_decay: {phase_when_found: 0, by_phase: {1: {value: 2.5, default: 2.5, override: null}}}, po_decision: {status: no_decision}}
```

#### C3. 自動帶入:新設備的預設名稱「左／左中／右中／右」不在條件內;規格書 POS-09 少了「預設點名稱」條件

**📛 命名(Identify):** §5.1 寫「新增探頭的預設值仍是『探頭 N』(`settings_dialog._on_probe_count`)」(PROPOSAL.md:92);§5.3 自動帶入條件 1 是「符合『探頭 N』的格式」,條件 2 含「原本所選點的預設名稱」(PROPOSAL.md:186-187)。

**📣 主張(Assert):**
- **新設備的探頭不是「探頭 N」**:設備第一次設為 DL-EN1 時,`lan.set_status` 帶入 `default_config()`,4 個探頭叫「左」「左中」「右中」「右」(lan.py:51-54、412-414);`installer/dl-en1.json` 也是這 4 個名稱。只有之後再增加的探頭才是「探頭 N」(settings_dialog.py:1219-1227)。
  - 結果:新增一台 DL-EN1 後逐一選點,4 個名稱都不會自動帶入,畫面出現「排3 左」在第 4 點這種情況。PO 的決定是「選了點就自動帶入點名稱…手動改過的不覆蓋」(PROPOSAL.md:61),這 4 個名稱不是工程人員手動取的。
  - 而且「左、左中…」正是「依探頭順序推定位置」的舊做法留下的名稱,本提案要拿掉的就是這種推定。
- **規格書與提案不一致**:POS-09 只有三個條件:「探頭 N」、等於原本所選點的名稱、被清空(規格書:1082);提案條件 2 多了「或等於原本所選點的預設名稱」。§0 規定兩者不一致時以規格書為準(PROPOSAL.md:11),所以照規則實作時,這個新增的條件會被忽略。呼叫者也要求 POS 條文與提案一致。
- Impact 3/10 / Probability 0.7 → 2.1(每新增一台 DL-EN1 都會遇到)
- Evidence: PROPOSAL.md:11、61、92、186-187;app/flatness/lan.py:51-54、412-414;app/flatness/ui/settings_dialog.py:1219-1227;installer/dl-en1.json;規格書:1082
- Cross-Module Impact:lan.default_config、settings_dialog 自動帶入、規格書 POS-09、安裝範例定義檔
- Phase-aware:M2 實作前要定案。

**🎯 追求(Pursue):** 擇一:(a) `default_config()` 的預設探頭名稱改為「探頭 1」～「探頭 4」,§6 lan.py 列加上「`default_config` 預設名稱」;或 (b) 條件 1 改為「新增探頭或新設備的預設名稱(探頭 N,或 左／左中／右中／右)」。建議 (a),比較單純,也和「不依順序推定位置」一致。另外把「或等於原本所選點的預設名稱」補進規格書 POS-09。

**📊 Decision Tree:**

| Option | 動作 | 成本 | 備註 |
| --- | --- | --- | --- |
| A | 不修 | 0 | 新設備不會自動帶入;規格書與提案不一致 |
| B | 現在修(改預設名稱並同步 POS-09) | 0.5h | 推薦 |

**📍 推薦:** Option B
**🔮 反事實:** 新增第 4 台後,4 個探頭依位置排列,名稱卻還是「左…右」,主畫面大字和實際的點對不上。

```yaml
- {tier: 🟡 CONCERN, id: C3, name: "新設備預設探頭名稱「左…右」不觸發自動帶入;POS-09 少「預設點名稱」條件", evidence: ["PROPOSAL.md:92", "PROPOSAL.md:186-187", "app/flatness/lan.py:51-54", "app/flatness/lan.py:412-414", "規格書:1082"], severity: {score: {value: 2.1, default: 2.1, override: null}, band: low, semantic: how_bad}, fix_economics: {difficulty: {value: 0.3, default: 0.3, override: null}, roi: {value: 7.0, default: 7.0}, resource_estimate: {value: "1h", default: "1h", override: null}}, cross_impact: {affected_modules: [lan.default_config, settings_dialog, spec POS-09], cascade_depth: 2, dependency_chain: "預設名稱 → 自動帶入條件 → 主畫面大字"}, phase_aware: {current_phase: 0, if_not_fixed_now_breaks_at: 2, estimated_rework_cost: low}, decision_tree: {options: [{id: A, action: 不修}, {id: B, action: 改預設名稱並同步 POS-09}], recommended_option: B, counterfactual: "新增設備的探頭名稱停在左…右"}, dependencies: {blocks: [], blocked_by: [], manual_blocks: []}, severity_decay: {phase_when_found: 0, by_phase: {2: {value: 2.5, default: 2.5, override: null}}}, po_decision: {status: no_decision}}
```

#### C4. 啟動改為讀 `plate_position_name` 後,沒有寫明升級時要先執行 `sql/in-win.sql`

**📛 命名(Identify):** rev 3 規定「`sync.startup` 從資料庫讀設備時一併讀名稱(`store.load_names()`)」(PROPOSAL.md:121);`inspection_point` 新增三欄(PROPOSAL.md:146);§8 只寫「M1～M4 全部完成後才部署」(PROPOSAL.md:343)。

**📣 主張(Assert):**
- 以前的資料表變更(`calibration`、`zero_offset`、`seen_ip`)只影響寫入。這次 rev 3 把新資料表放進啟動的讀取路徑。如果產線電腦先換 App、還沒執行 SQL:
  - `startup` 讀名稱失敗,整個啟動走「無法讀取資料庫,使用上次的設定」(sync.py:105-110);維修中設備從主畫面消失(PROPOSAL.md:354)。
  - 設定頁讀資料時若也讀名稱,會進入唯讀(settings_dialog.py:557-564)。
  - 每片結果的 INSERT 帶新欄位而失敗,全部留在本機暫存,頂端持續顯示「資料庫無法寫入」(store.py:259-264、results.py)。
- 安裝程式本身不會執行 SQL(installer/ 下沒有任何 .sql 呼叫,只有開發用的 scripts/dev-mysql.sh:30),所以順序全靠人工。資料不會遺失(有暫存),但上線當天會看到一連串假的資料庫異常。
- Impact 5/10 / Probability 0.3 → 1.5
- Evidence: PROPOSAL.md:121、146、343;app/flatness/sync.py:103-110;app/flatness/ui/settings_dialog.py:557-564;app/flatness/store.py:246-267;scripts/dev-mysql.sh:30
- Cross-Module Impact:sync.startup、store、results 暫存、安裝說明
- Phase-aware:M1 定 `load_names` 行為時就要決定;M5 安裝說明要寫。

**🎯 追求(Pursue):** 兩項都做:
1. §8 加一句「部署:先以管理員帳號執行 `sql/in-win.sql`,再更新 App」,§6 文件清單的安裝說明加「升級步驟」。
2. §5.1 寫明 `load_names()` 遇到資料表不存在(MySQL 1146)時記錄錯誤並回傳預設名稱,不當成資料庫無法連線。

**📊 Decision Tree:**

| Option | 動作 | 成本 | 備註 |
| --- | --- | --- | --- |
| A | 不修 | 0 | 依部署紀律;順序錯時整台工站顯示資料庫異常 |
| B | 現在修(部署步驟＋缺表時用預設) | 0.5h | 推薦 |

**📍 推薦:** Option B
**🔮 反事實:** 換版當天先開 App,主畫面顯示「無法讀取資料庫」,維修中設備消失,結果全進暫存,直到有人想到要執行 SQL。

```yaml
- {tier: 🟡 CONCERN, id: C4, name: "啟動讀新資料表,升級未先執行 SQL 時整台走資料庫異常路徑", evidence: ["PROPOSAL.md:121", "PROPOSAL.md:146", "PROPOSAL.md:343", "app/flatness/sync.py:103-110", "app/flatness/ui/settings_dialog.py:557-564"], severity: {score: {value: 1.5, default: 1.5, override: null}, band: low, semantic: how_bad}, fix_economics: {difficulty: {value: 0.3, default: 0.3, override: null}, roi: {value: 5.0, default: 5.0}, resource_estimate: {value: "1h", default: "1h", override: null}}, cross_impact: {affected_modules: [sync, store, results, 安裝說明], cascade_depth: 3, dependency_chain: "缺表 → startup StoreError → 唯讀與暫存"}, phase_aware: {current_phase: 0, if_not_fixed_now_breaks_at: 6, estimated_rework_cost: low}, decision_tree: {options: [{id: A, action: 不修}, {id: B, action: 部署步驟加缺表容錯}], recommended_option: B, counterfactual: "上線當天假性資料庫異常"}, dependencies: {blocks: [], blocked_by: [], manual_blocks: []}, severity_decay: {phase_when_found: 0, by_phase: {6: {value: 2.0, default: 2.0, override: null}}}, po_decision: {status: no_decision}}
```

### 🟢 NITS — 可選 polish

```yaml
- {tier: 🟢 NIT, id: N1, name: "狀態表第 5 列漏了「未設定允收標準」(方塊顯示 ERR,橫幅列出)", evidence: ["PROPOSAL.md:241", "app/flatness/ui/main_window.py:1255-1258"], pursue: "第 5 列改為「探頭無回應、未校準、未設定允收標準」", severity: {score: {value: 0.4, default: 0.4}}, po_decision: {status: no_decision}}
- {tier: 🟢 NIT, id: N2, name: "「只設其一」仍有兩種訊息格式:§5.1「第 N 列(ID n)位置須…」與 §5.3「探頭 n:位置須…」(R2-N5 的另一半)", evidence: ["PROPOSAL.md:142", "PROPOSAL.md:181"], pursue: "統一為 _entry_issues 的格式,§5.3 改為引用 §5.1", severity: {score: {value: 0.5, default: 0.5}}, po_decision: {status: no_decision}}
- {tier: 🟢 NIT, id: N3, name: "條件 2 的「點k」與段首「選定第幾點為 k」用同一個 k,讀起來像新的點", evidence: ["PROPOSAL.md:184", "PROPOSAL.md:187"], pursue: "原本的點改用 j:「等於點 j 目前的名稱,或等於預設名稱『點j』」", severity: {score: {value: 0.3, default: 0.3}}, po_decision: {status: no_decision}}
- {tier: 🟢 NIT, id: N4, name: "降版列不完整:舊版啟動時 render 驗證失敗(lan._entry_issues → bootp.validate 不允許 row/point),頂端持續顯示「設備設定有錯誤,沿用上次的設定」,維修中設備從主畫面消失;任何設備的立即儲存(校準、刪除、排序)都會失敗,不只帶位置的設備", evidence: ["PROPOSAL.md:279", "app/flatness/sync.py:111-116", "app/flatness/lan.py:290-307", "app/flatness/bootp.py:134"], pursue: "補上這三點,讓現場知道降版後看到的錯誤是預期的", severity: {score: {value: 0.4, default: 0.4}}, po_decision: {status: no_decision}}
- {tier: 🟢 NIT, id: N5, name: "P3D-03 拒絕訊息「例如只有 1 排…至少需要 2 排探頭」在 5×5 格下不完整:探頭分在 2 排但都在同一點(同一直行)也會拒絕,訊息卻說需要 2 排", evidence: ["PROPOSAL.md:259", "app/flatness/plate3d/model.py:92", "app/flatness/plate3d/model.py:157"], pursue: "§5.6 註明訊息改為「至少需要 2 排且 2 個不同的點」或「不在同一直線上的探頭」", severity: {score: {value: 0.4, default: 0.4}}, po_decision: {status: no_decision}}
```

### ✅ STRENGTHS

- `names=None` 的語意(名稱不變,沿用資料庫,不是省略欄位)寫得精確,並列出校準、刪除、排序三條路徑與對應的驗收(PROPOSAL.md:121、326),把第 2 輪 C2 的漏洞完整補上。
- 狀態表把方塊與頂端提示分開說明,頂端各自累加,直接對應 DSC-20 的「頂端提示仍顯示」,POS-05 也同步改寫。
- Excel 以(`device_key`、`probe_id`)為一欄、位置取當日最後一筆,與現有取名稱的做法一致(export.py:32-36),第二工作表依同一欄產生,不會出現兩套規則。
- 降版列改成以程式實際行為描述(舊版 `load_existing` 不驗證),並給出可操作的降版前步驟。
- §10 每一點都列出依賴段落,PO 改選時的修改範圍一目了然。

## § 3. Critical Hotspots

| Finding | effective_cost | cascade_depth | 等級 | 早解 vs 晚解 |
| --- | :---: | :---: | :---: | --- |
| C4 升級順序 | 1.5 | 3 | 無(1-5 且 ≤3) | 現在加一句部署步驟與缺表容錯約 1h;上線當天才發現,要現場排除假性資料庫異常並補寫暫存,約 0.5d |

本輪沒有達到 hotspot 門檻的 finding。

## § 4. Effective Cost Matrix

| ID | Impact | Prob | Effective cost | 修正成本 |
| --- | :---: | :---: | :---: | :---: |
| C1 | 4 | 0.4 | 1.6 | 1h |
| C2 | 3 | 0.7 | 2.1 | 1h |
| C3 | 3 | 0.7 | 2.1 | 1h(含規格書 POS-09) |
| C4 | 5 | 0.3 | 1.5 | 1h |
| N1–N5 | — | — | 合計約 2.0 | 合計約 1h |
| **總計** | | | **約 9.3**(第 1 輪約 45、第 2 輪約 15.9) | **約 5h(全部是文字修訂)** |

本輪 tally(供 F2 append):Round 3|2026-10-15|BLOCKER 0|CONCERN 4|NIT 5|STRENGTH 5|ship-as-is。

## § 5. Decision Log

- 本輪沒有新的 PO 決定,所有 finding 的 `po_decision` 都是 `no_decision`。
- 沿用的前提:第 3 節 11 項 PO 決定;第 10 節 4 點仍延後給 PO,依賴段落已列清楚。
- 第 2 輪的處理結果:R2-N5 部分重開(C2、N2);其餘 12 項成立。C3 與 C4 是 rev 3 修正 R2-N1、R2-C2 時帶出的新問題,不是重開。

## § 6. Verdict + Next Round Focus

- **Status:** ship-as-is(BLOCKER 0、CONCERN 4、NIT 5、STRENGTH 5)
- **Recommend:**
  - 送 PO 簽核前修 C2、C3:兩者都牽涉規格書條文(POS-02 範例、POS-09 條件),簽核後再改要重新確認。
  - C1、C4 是一兩句的文字修訂,可以一起修。
  - NIT 可在 M1 開工前順手處理。
- **Convergence:** effective cost 從 45 → 15.9 → 9.3,本輪沒有 BLOCKER,剩下的都是單段文字。修完 C1～C4 後不需要第 4 輪全面審查,只要確認這 4 處即可。
- **Next Round Focus(若有):**
  - §5.2 若分成「顯示名稱」與「設備稱呼」,檢查所有使用處的歸屬。
  - POS-09 與 §5.3 自動帶入條件逐字一致。

(本輪沒有 BLOCKER,不附 § 7 Reflection。)
