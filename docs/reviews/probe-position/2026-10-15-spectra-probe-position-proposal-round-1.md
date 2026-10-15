---
target: docs/pm/probe-position/PROPOSAL.md
target_rev: b0aaba7
date: 2026-10-15
reviewer: spectra-review (v2.0)
iteration: 1
verdict: fix-blockers
schema_version: enhanced-v1
contract_version: spectra-contract-v1
mode: pm-skill-generic-doc
---

> 💡 spectra-review v2.0 active(Minerva 4 能力 framework)。若想用原版簡潔版,用 `/spectra-review --lite <target>`。

🎯 Mode: PM Skill — Generic doc (target: docs/pm/probe-position/PROPOSAL.md)

# Spectra-Review Round 1 — docs/pm/probe-position/PROPOSAL.md

本輪範圍與限制:
- 對照來源:需求規格書 3.13 POS-01～09、POS-G1/G2、POS-A1～A5,以及 DEF-04、DEF-08、EDT-03、EDT-05、DSC-06、DSC-09、DSC-14、DSC-15、DSC-20、UI-04、UI-11、P3D-02～05、EXP-03、3.7.1、NFR-01;程式碼見各 finding 的 evidence。
- 第 3 節的 PO 決定視為已定案,本輪不重新討論;第 10 節的待決事項只在「其他段落依賴它卻沒寫明」時才列出。
- SKILL 提到但本 repo 沒有的檔案(docs/CONTEXT.md、docs/index.md、pm-skill-proposal.md、state.md、decision-log.md)略過。
- 依呼叫者指示,本輪只寫 F1。F2(`_summary-*.md`)與 decision-log audit entry 未寫,留待 PO 決定是否補上。

## § 1. Mental Lens

- **Claim → Evidence → Verdict**:第 5、6 節對程式碼的說法逐一對照原始碼,例如「跨設備驗證放在 `bootp.validate`」「同一交易內儲存」「同 DSC-06 的做法」「description 空白」。
- **Cross-section consistency**:對照提案第 3、4、5、10 節,以及提案與規格書 POS 條文、已簽核的 3.7.1/DSC/EXP/UI 條文。
- **Anti-Bias**:提案與規格書出自同一作者、同一天,彼此一致不代表與程式碼一致,所以每項都以程式碼為準。
- **Understand-not-argue**:原設計刻意「識別不變、只加位置屬性」,方向正確。下列 finding 只補實作上的斷點,不改 PO 決定。

## § 2. 4-Tier Findings

### 🔴 BLOCKERS — 落地前必修

#### B1. 位置不可重複的檢查放錯層:`bootp.validate` 看不到維修中設備,也看不到設定頁其他設備

**📛 命名(Identify):** 第 5.1 節寫「跨設備驗證(`bootp.validate`…):使用中與維修中所有探頭的 `(row, point)` 不可重複」,第 6 節也把這項檢查歸給 `bootp.py`。

**📣 主張(Assert):**
- Why BLOCKER:照字面實作,POS-02 與 POS-A2 會失守。
  - `bootp.validate` 驗證的是定義檔,而定義檔只含「使用中」(`lan.definition_from` → `live_devices`,lan.py:187-189;3.7.1 `dl_en1`「只含使用中」),維修中設備永遠不會進入這個檢查。
  - 設定頁每台設備的即時檢查是 `lan._entry_issues` 用**單台**呼叫 `bootp.validate({"dl_en1": [entry]})`(lan.py:265-270),看不到其他設備。
  - 真正的跨設備檢查在 `lan.validate` 的 `groups`(lan.py:290-330),目前涵蓋 key、name、ipv4 三個欄位,範圍是 `is_dl_en1`,也就是使用中加維修中。
- Impact: 7/10 / Probability: 0.8(照提案寫就一定漏)
- Evidence: PROPOSAL.md:102、PROPOSAL.md:217;app/flatness/lan.py:187-189、265-270、290-330;app/flatness/bootp.py:57-168;sync.py:39-52(`render` 先跑 `lan.validate` 再跑 `definition.validate`)
- Cross-Module Impact:bootp.py、lan.py(validate、occupied_text)、settings_dialog(選單佔用顯示)、sync.render(啟動、套用、匯入 UPL、還原 UPL-10 都走這裡)
- Phase-aware:M1 就會寫錯,M2 的選單佔用邏輯也會跟著寫在錯的資料上。

**🎯 追求(Pursue):** 拆成兩層並寫進第 5.1 節與第 6 節:
1. `bootp.validate`:單台內同時存在、範圍 1～5、`row`/`point` 只設其一;**定義檔內**跨台重複,處理上傳的定義檔,只有使用中。
2. `lan.validate`:使用中加維修中的 `(row, point)` 不可重複,加入 `groups`,訊息沿用 `occupied_text` 的「已由…使用」(DSC-08-A4 的格式)。已停用不計入(DSC-09)。

另外寫明:匯入定義檔(`lan.import_definition`,lan.py:514)後,檔案內的位置可能與既有**維修中**設備衝突,由 `lan.validate` 拒絕並說明(POS-02「匯入…有重複位置時拒絕」)。

**📊 Decision Tree:**

| Option | 動作 | 成本 | 備註 |
|---|---|---|---|
| A | 不修 | 0h 現在;上線後 POS-A2 重現 | 維修中探頭的位置可被別台搶走,改回使用中時才爆 |
| B | 現在修(改提案兩段文字) | 0.5h | 實作成本不變,只是放對地方 |
| C | M1 實作時再說 | 0.5h + 返工風險 | 測試會照錯的設計寫 |

**📍 推薦:** Option B
**🔮 反事實:** 不修的話,M1 單元測試「重複位置」照提案寫在 `bootp.validate`,測試全綠;上線後中排設為維修中,另一台把探頭設在中排原本的位置,可以存檔;中排改回使用中時整份設定驗證失敗,工程人員卡在設定頁。

```yaml
- tier: 🔴 BLOCKER
  id: B1
  name: "位置唯一性檢查放錯層(bootp.validate 看不到維修中與其他設備)"
  evidence: ["PROPOSAL.md:102", "PROPOSAL.md:217", "app/flatness/lan.py:187-189", "app/flatness/lan.py:265-270", "app/flatness/lan.py:290-330"]
  severity: {score: {value: 5.6, default: 5.6, override: {by: null, at: null, reason: null}}, band: med, semantic: how_bad}
  fix_economics: {difficulty: {value: 1.0, default: 1.0, override: null}, roi: {value: 5.6, default: 5.6}, resource_estimate: {value: "1h", default: "1h", override: null}}
  cross_impact: {affected_modules: [bootp, lan, settings_dialog, sync], cascade_depth: 3, dependency_chain: "lan.validate → sync.render → apply/startup/import"}
  phase_aware: {current_phase: 0, if_not_fixed_now_breaks_at: 1, estimated_rework_cost: medium}
  decision_tree: {options: [{id: A, action: 不修}, {id: B, action: 現在修}, {id: C, action: 延後修}], recommended_option: B, counterfactual: "維修中探頭位置被搶,改回使用中時整份設定無法儲存"}
  dependencies: {blocks: [C7, C8], blocked_by: [], manual_blocks: []}
  severity_decay: {phase_when_found: 0, by_phase: {1: {value: 6.5, default: 6.5, override: null}, 3: {value: 7.5, default: 7.5, override: null}}}
  po_decision: {status: no_decision, decided_at: null, decided_by: null, reason: null}
```

#### B2. `description` 必填(1～10 字)與「位置名稱空白」的前提矛盾;POS-09 的自動帶入對新增探頭永遠不會觸發

**📛 命名(Identify):** 提案多處假設位置名稱可以是空白:
- 第 5.2 節範例第 3 列的位置名稱是空的(PROPOSAL.md:137)。
- 「若位置名稱為空…就自動改成新點的名稱」(PROPOSAL.md:141)。
- 「`description` 空白時顯示『探頭 N』」(PROPOSAL.md:171)。

程式碼與 3.7.1 的規定是 `description` 必填、1～10 字:
- 程式碼:dl-en1.schema.json:38-41、bootp.py:150-153。
- 規格書 3.7.1:「探頭 `description` 是 1～10 字」。
- 設定頁新增探頭時,預設位置名稱是「探頭 N」(settings_dialog.py:1219-1227)。

**📣 主張(Assert):**
- Why BLOCKER:PO 決定「選了點就自動帶入點名稱」(第 3 節)。依提案的規則「空白」或「等於原本所選點的名稱」才自動帶入:
  - 新增探頭的位置名稱是「探頭 4」,兩個條件都不成立,所以**永遠不會自動帶入**。
  - 升級前就有的探頭(「左」「右中」)也不會自動帶入。這一點符合 PO「手動改過的不覆蓋」。
  - 結果只有工程人員先清空位置名稱,自動帶入才會作用,PO 決定實際上不會發生。
  - 「空白時顯示探頭 N」寫的是一條永遠走不到的分支。若實作者把它當成要放寬 Schema,又會改動 3.7.1 的正式規格。
- Impact: 6/10 / Probability: 0.9
- Evidence: PROPOSAL.md:135-141、171;app/flatness/dl-en1.schema.json:38-41;app/flatness/bootp.py:150-153;app/flatness/ui/settings_dialog.py:1219-1227;規格書 POS-09 驗收「探頭位置名稱為空時選第 2 點」
- Cross-Module Impact:Schema、bootp、settings_dialog、主畫面方塊、3D 標籤、POS-09 驗收條件
- Phase-aware:M1 決定 Schema,M2 實作自動帶入,兩者都依賴這個前提。

**🎯 追求(Pursue):** 維持 `description` 必填(不動 3.7.1),把自動帶入條件改成「位置名稱尚未被手動命名」,也就是符合以下任一項:
- 等於預設的「探頭 {id}」;
- 等於原本所選點的名稱;
- 編輯中暫時為空白。

另外補兩點:
- 把點改回「未定」時,位置名稱怎麼處理。建議若仍等於原點名稱就保留不動。
- 「原本所選點的名稱」要拿同一次編輯中**修改後**的點名稱來比,還是已儲存的點名稱來比。建議兩者都視為自動名稱。

刪除「`description` 空白時顯示探頭 N」一句,或改寫為「位置名稱即預設的『探頭 N』」。規格書 POS-09 驗收的「為空時」建議同步改為「為預設名稱『探頭 N』時」。

**📊 Decision Tree:**

| Option | 動作 | 成本 | 備註 |
|---|---|---|---|
| A | 不修 | 0 | 自動帶入形同虛設,PO 驗收 POS-09 時才發現 |
| B | 現在修(改條件,不改 Schema) | 1h | 推薦,沿用現有必填規則 |
| C | 放寬 description 為選填 | 4h+ | 牽動 3.7.1、Schema、DEF-08(`probe_description NOT NULL`,in-win.sql:59)、Excel 標題 |

**📍 推薦:** Option B
**🔮 反事實:** 不修的話,M2 依字面實作;POS-G1 現場設定時,工程人員選了第 2 點,位置名稱仍是「探頭 1」;3D 標籤變成「排1 探頭 1」;PO 認為功能沒做。

```yaml
- tier: 🔴 BLOCKER
  id: B2
  name: "description 必填與「空白」前提矛盾,POS-09 自動帶入不觸發"
  evidence: ["PROPOSAL.md:135-141", "PROPOSAL.md:171", "app/flatness/dl-en1.schema.json:38-41", "app/flatness/ui/settings_dialog.py:1219-1227"]
  severity: {score: {value: 5.4, default: 5.4, override: {by: null, at: null, reason: null}}, band: med, semantic: how_bad}
  fix_economics: {difficulty: {value: 1.0, default: 1.0, override: null}, roi: {value: 5.4, default: 5.4}, resource_estimate: {value: "1h", default: "1h", override: null}}
  cross_impact: {affected_modules: [schema, bootp, settings_dialog, main_window, plate3d], cascade_depth: 3, dependency_chain: "自動帶入規則 → description 值 → 方塊大字/3D 標籤/Excel 標題"}
  phase_aware: {current_phase: 0, if_not_fixed_now_breaks_at: 2, estimated_rework_cost: medium}
  decision_tree: {options: [{id: A, action: 不修}, {id: B, action: 改條件}, {id: C, action: 放寬 Schema}], recommended_option: B, counterfactual: "新增探頭選點後名稱仍為「探頭 N」,PO 驗收失敗"}
  dependencies: {blocks: [C3], blocked_by: [], manual_blocks: []}
  severity_decay: {phase_when_found: 0, by_phase: {2: {value: 6.0, default: 6.0, override: null}, 6: {value: 7.0, default: 7.0, override: null}}}
  po_decision: {status: no_decision, decided_at: null, decided_by: null, reason: null}
```

#### B3. 只改排/點名稱時無法儲存;名稱寫入的交易位置與影響範圍都寫錯

**📛 命名(Identify):** 第 5.1 節說名稱「與設備設定在同一個交易內儲存(`store.transaction()`),預覽、確認、套用一起」(PROPOSAL.md:118)。

**📣 主張(Assert):**
- Why BLOCKER:POS-03 的驗收條件「第 1 排改名『前排』並儲存」正好是**只改名稱**的情況,但目前的儲存流程會擋下它:
  - 確認頁的變更清單來自 `lan.diff(self.original.values(), self._devices())`(settings_dialog.py:1521),只比對設備。
  - 只改名稱時 `preview.empty` 為真,畫面顯示「沒有任何變更」,儲存鍵停用(settings_dialog.py:1537-1538、1578);`_commit` 遇到 empty 直接 return(settings_dialog.py:1580-1583)。
  - 交易在 `sync.apply` 內開啟(sync.py:142),`backend.apply(old, new, …)` 與 `sync.apply` 的參數只有設備清單;但第 6 節影響範圍沒有列 `sync.py`。
  - `MemoryStore.transaction` 的還原快照只包含 `_rows`(store.py:117-129),名稱失敗時不會一起還原。
- Impact: 6/10 / Probability: 0.9
- Evidence: PROPOSAL.md:117-119、213-228;app/flatness/ui/settings_dialog.py:1521、1537-1538、1578-1583;app/flatness/sync.py:128-163;app/flatness/backend.py:147-150;app/flatness/store.py:117-129
- Cross-Module Impact:settings_dialog(`is_dirty`、確認頁、`_commit`)、`lan.Preview`、backend.apply、sync.apply、store(兩種 Tx)
- Phase-aware:M1 的 store 介面與 M2 的儲存流程都要先定案。

**🎯 追求(Pursue):** 第 5.1、5.2、6 節補上:
1. `Preview` 加入名稱變更項目,`empty` 要把名稱變更算進去;`is_dirty` 也要比對名稱。
2. `sync.apply(…, names=None)` 在同一個 `store.transaction()` 內呼叫 `tx.save_names(...)`。只改名稱時定義檔與 BOOTP 內容相同,不改寫、不重啟 dnsmasq(DSC-06,`_write` 已具備這個行為)。
3. `MemoryStore` 的快照要包含名稱。
4. 第 6 節影響範圍加入 `app/flatness/sync.py`。
5. M1/M2 測試加入「只改名稱 → 可儲存、重新啟動後保留」與「寫入失敗 → 名稱與設備一起還原」。

**📊 Decision Tree:**

| Option | 動作 | 成本 | 備註 |
|---|---|---|---|
| A | 不修 | 0 | POS-03 的第一條驗收就失敗 |
| B | 現在修(改提案) | 1h | 實作約 0.5 天,原本就躲不掉 |
| C | 名稱改為即時儲存(同 DSC-17) | 1h | 違反 POS-03「一併預覽、確認、套用」,需要 PO 改決定,不推薦 |

**📍 推薦:** Option B
**🔮 反事實:** 不修的話,M2 完成後工程人員把第 1 排改名「前排」,按儲存卻顯示「沒有任何變更」;實作者臨時另開一條寫入路徑,繞過 EDT-03 的預覽與還原。

```yaml
- tier: 🔴 BLOCKER
  id: B3
  name: "只改名稱時預覽為空、無法儲存;交易在 sync.apply 而影響範圍沒有列入"
  evidence: ["PROPOSAL.md:117-119", "app/flatness/ui/settings_dialog.py:1521", "app/flatness/ui/settings_dialog.py:1578-1583", "app/flatness/sync.py:128-163", "app/flatness/store.py:117-129"]
  severity: {score: {value: 5.4, default: 5.4, override: {by: null, at: null, reason: null}}, band: med, semantic: how_bad}
  fix_economics: {difficulty: {value: 1.5, default: 1.5, override: null}, roi: {value: 3.6, default: 3.6}, resource_estimate: {value: "1h", default: "1h", override: null}}
  cross_impact: {affected_modules: [settings_dialog, lan.Preview, backend, sync, store], cascade_depth: 4, dependency_chain: "settings 確認頁 → backend.apply → sync.apply → store.transaction → Tx"}
  phase_aware: {current_phase: 0, if_not_fixed_now_breaks_at: 2, estimated_rework_cost: medium}
  decision_tree: {options: [{id: A, action: 不修}, {id: B, action: 現在修}, {id: C, action: 改即時儲存}], recommended_option: B, counterfactual: "POS-03 驗收「改名並儲存」直接失敗"}
  dependencies: {blocks: [C2], blocked_by: [], manual_blocks: []}
  severity_decay: {phase_when_found: 0, by_phase: {1: {value: 6.0, default: 6.0, override: null}, 2: {value: 7.0, default: 7.0, override: null}}}
  po_decision: {status: no_decision, decided_at: null, decided_by: null, reason: null}
```

### 🟡 CONCERNS — 應修

#### C1. 設備狀態對應表缺少維修中方塊的建法、狀態優先順序,以及「頂端摘要」對應的元件

- **Assert:**
  - 第 5.4 節要求「該台每個方塊灰色『維修中』」。但目前維修中的排**沒有方塊**,只有一個虛線說明框「維修中:不連線、不量測(N 個探頭)」(main_window.py:356-365),而且 `standards()` 只包含使用中(backend.py:166-168)。
  - 以下情況提案都沒有寫:
    - 維修中設備裡位置未定的探頭,要不要放進「未設定位置」區。
    - 「偵測不到 + IP 不符」的優先順序。DSC-20 規定偵測不到優先,但頂端提示仍要顯示。
    - 「維修中 + IP 不符」怎麼顯示。現行排頭會寫「IP 不符・維修中」(main_window.py:440)。
    - 「IP 不符」要標在方塊的哪個位置。UI-04 的設備狀態列,還是外框?
  - 「頂端摘要」對應哪個元件也不清楚:
    - 現行 `sum_text` 只有一行「N 個量測點異常」(main_window.py:1162-1174)。
    - IP 不符走的是 `set_flag("ip", …)`(main_window.py:1102)。
    - 提案的「第 N 台 名稱 偵測不到」與「維修中(灰色)」要放進哪一個?多台同時發生時怎麼列?
  - `_on_detected`、`show_result`、`_clear_tiles`、`_fade_ok` 都以 `row.tiles[pid]` 逐排走訪(main_window.py:1180-1184、1229-1270、1401-1432),全部要改用 `(key, pid)` 對應。這是第 9 節自己點名的最大風險,卻沒有狀態矩陣可以據以實作與測試。
- **Pursue:** 第 5.4 節改成完整矩陣,列為「整台狀態 × 探頭狀態」,欄為「方塊外框、設備狀態列文字、排頭、頂端元件」,並註明優先順序:偵測不到 > 整台異常 > 維修中 > IP 不符 > 探頭異常。另外明定:
  - 維修中探頭位置未定時,放進「未設定位置」區並顯示灰色。
  - 「頂端摘要」= 新增的 `set_flag("dev", …)`,最多列 2 台,其餘以「等 N 台」表示,與 UI-11 的規則一致。
- Evidence: PROPOSAL.md:176-185;main_window.py:356-365、425-457、1085-1105、1162-1174、1217-1270
- Impact 6 / Prob 0.6 → 3.6

```yaml
- {tier: 🟡 CONCERN, id: C1, name: "狀態對應缺維修中方塊、優先序、頂端元件", evidence: ["PROPOSAL.md:176-185", "app/flatness/ui/main_window.py:356-365", "app/flatness/ui/main_window.py:1162-1174"], severity: {score: {value: 3.6, default: 3.6, override: null}, band: med, semantic: how_bad}, fix_economics: {difficulty: {value: 1.5, default: 1.5, override: null}, roi: {value: 2.4, default: 2.4}, resource_estimate: {value: "2h", default: "2h", override: null}}, cross_impact: {affected_modules: [main_window, backend], cascade_depth: 2, dependency_chain: "狀態矩陣 → M3 實作與 UI 測試"}, phase_aware: {current_phase: 0, if_not_fixed_now_breaks_at: 3, estimated_rework_cost: medium}, decision_tree: {options: [{id: A, action: 不修}, {id: B, action: 補矩陣}], recommended_option: B, counterfactual: "M3 各自猜優先序,UI 測試與 DSC-20 驗收衝突"}, dependencies: {blocks: [], blocked_by: [], manual_blocks: []}, severity_decay: {phase_when_found: 0, by_phase: {3: {value: 4.5, default: 4.5, override: null}}}, po_decision: {status: no_decision}}
```

#### C2. 「資料庫無法連線時沿用上次讀到的名稱(同 DSC-06 的做法)」與程式碼不符,重新啟動後就會遺失

- **Assert:**
  - DSC-06 的做法是沿用**磁碟上的定義檔**:`sync.startup` 失敗時改用 `load_existing(files)`(sync.py:107-113)。
  - 名稱沒有任何檔案快取,backend 只有記憶體中的 `_cache`(backend.py:53)。
  - 結果:App 在資料庫停機時啟動,探頭位置(在 dl-en1.json 內)正確,排頭卻變回「排1」～「排5」,3D 標籤也一樣。這與 POS-03「重新啟動後保留」的精神不一致。
- **Pursue:** 擇一寫明:
  - (a) 套用成功時把名稱寫進本機快取檔,與定義檔同目錄,用 `atomic_write`;資料庫無法連線時讀這個檔。
  - (b) 存在 QSettings,與板子尺寸相同(plate3d/config.py:75-81)。

  另外把「同 DSC-06 的做法」改成實際的機制。
- Evidence: PROPOSAL.md:119;sync.py:101-113;backend.py:53、117-125
- Impact 5 / Prob 0.4 → 2.0

```yaml
- {tier: 🟡 CONCERN, id: C2, name: "名稱離線快取不存在,重開後回預設", evidence: ["PROPOSAL.md:119", "app/flatness/sync.py:101-113", "app/flatness/backend.py:53"], severity: {score: {value: 2.0, default: 2.0, override: null}, band: low, semantic: how_bad}, fix_economics: {difficulty: {value: 1.0, default: 1.0, override: null}, roi: {value: 2.0, default: 2.0}, resource_estimate: {value: "2h", default: "2h", override: null}}, cross_impact: {affected_modules: [backend, sync], cascade_depth: 2, dependency_chain: "startup → 主畫面排頭/3D 標籤"}, phase_aware: {current_phase: 0, if_not_fixed_now_breaks_at: 1, estimated_rework_cost: low}, decision_tree: {options: [{id: A, action: 不修}, {id: B, action: 檔案快取}], recommended_option: B, counterfactual: "MySQL 停機重開 App 時排頭名稱變回預設"}, dependencies: {blocks: [], blocked_by: [B3], manual_blocks: []}, severity_decay: {phase_when_found: 0, by_phase: {1: {value: 2.5, default: 2.5, override: null}}}, po_decision: {status: no_decision}}
```

#### C3. 自動帶入點名稱後,探頭層級的訊息與標題會出現同名,無法分辨

- **Assert:**
  - 依 POS-09,位置名稱會變成「點2」。同一台 DL-EN1 可以有兩個探頭分別在第 1 排第 2 點、第 3 排第 2 點,兩者的 description 都是「點2」。
  - 以下地方都用「DL-EN1 名稱 + description」稱呼探頭,這兩個探頭會變成同名的「中排 點2」(提案改稱後是「第 2 台 中排 點2」):
    - 結果橫幅的探頭異常與不合格點(main_window.py:1251、1414-1427)
    - Excel 測量值欄標題與「不合格點」(export.py:35、54)
    - P3D-02 的無數據清單
    - 第 5.2 節的變更清單
  - 第 5.4 節只改了**整台**的稱呼,探頭層級的稱呼沒有規定。第 10 節第 3 點只處理 Excel 標題。
- **Pursue:** 第 5 節定一條全系統共用的「探頭顯示名稱」規則:
  - 已設定位置:「排名稱 位置名稱」,與 3D 標籤相同(例「排1 點2」)。
  - 未定:「第 N 台 名稱 探頭 id」。
  - 套用範圍:橫幅、Excel、3D 拒絕訊息、變更清單。

  第 10 節第 3 點可以直接引用這條規則。
- Evidence: PROPOSAL.md:141、185、272;main_window.py:1251、1414-1427;export.py:35、54
- Impact 5 / Prob 0.7 → 3.5

```yaml
- {tier: 🟡 CONCERN, id: C3, name: "探頭層級稱呼未定義,自動帶入後同名", evidence: ["PROPOSAL.md:185", "app/flatness/ui/main_window.py:1414-1427", "app/flatness/export.py:35"], severity: {score: {value: 3.5, default: 3.5, override: null}, band: med, semantic: how_bad}, fix_economics: {difficulty: {value: 1.0, default: 1.0, override: null}, roi: {value: 3.5, default: 3.5}, resource_estimate: {value: "1h", default: "1h", override: null}}, cross_impact: {affected_modules: [main_window, export, plate3d, lan.diff], cascade_depth: 3, dependency_chain: "description 自動帶入 → 所有以名稱稱呼探頭的訊息"}, phase_aware: {current_phase: 0, if_not_fixed_now_breaks_at: 3, estimated_rework_cost: medium}, decision_tree: {options: [{id: A, action: 不修}, {id: B, action: 定義共用顯示名稱}], recommended_option: B, counterfactual: "作業員看到「中排 點2 偏高」卻有兩個點2"}, dependencies: {blocks: [], blocked_by: [B2], manual_blocks: []}, severity_decay: {phase_when_found: 0, by_phase: {3: {value: 4.0, default: 4.0, override: null}}}, po_decision: {status: no_decision}}
```

#### C4. SSOT 與影響清單不完整:已簽核條文、程式檔、文件都有遺漏

- **Assert:**
  - 第 9 節列出受影響的已簽核需求有 DEF-04、EDT-05、DSC-15、P3D-05、TBD-06。以下遺漏:
    - **DSC-20**:頂端文字「IP 不符:<排名稱>(第 N 排)」,與 POS-06「不再出現第 N 排」直接衝突。第 5.4 節卻寫「沿用 DSC-20 的頂端提示」(PROPOSAL.md:182)。
    - **UI-11**:「排(DL-EN1)」「每排 6 個探頭」。
    - **EXP-03**:「各排 DL-EN1 的 MAC(每排一欄)」。
    - **3.7.1**:`key`「第幾排,決定量測畫面由上而下的順序」、`name`「排名稱」、「探頭依 `id` 由左至右」。規格書內嵌的 JSON Schema 也沒有 `row`、`point`(規格書約 510-530 行),而它是「測試驗收的正式依據」。
    - **DSC-09/DSC-12**:「排名稱」。
    - **P3D-04**:「維修中的排」。
    - **CAL-01/02**:例句「第 1 排探頭 2」。
  - 第 6 節程式檔遺漏:
    - `sync.py`(見 B3)。
    - `results.py` 與 `MainWindow.MemorySink.export`(Excel 要拿到目前設定,見 C6)。
    - settings_dialog.py:40 的維修中說明「主畫面保留該排」。
    - `lan.diff` 的「位置」「排名稱」標籤(lan.py:624-631)。
    - `LanDevice.name` 的 docstring。
  - 第 6 節文件遺漏:`docs/ui/screens-device-settings.md`,以及 changeset(CLAUDE.md 的 Definition of Done)。
  - 程式碼中有 25 處使用 `row_label`、「排名稱」或「該排」,POS-06 的驗收要求一處都不能留,卻沒有清點清單。
- **Pursue:**
  - 第 9 節改成完整的條文清單,逐條寫出「修訂方式」。
  - 第 6 節補齊上述檔案。
  - M5 加上 grep 驗收:`第 .* 排` 只出現在板子排的語境。
- Evidence: PROPOSAL.md:182、213-228、264;規格書 3.7.1 表與內嵌 Schema、DSC-20、UI-11、EXP-03;settings_dialog.py:40、425;lan.py:92-96、624-631
- Impact 5 / Prob 0.8 → 4.0

```yaml
- {tier: 🟡 CONCERN, id: C4, name: "受影響條文與影響範圍清單不完整(含 DSC-20 與 POS-06 衝突)", evidence: ["PROPOSAL.md:182", "PROPOSAL.md:213-228", "PROPOSAL.md:264"], severity: {score: {value: 4.0, default: 4.0, override: null}, band: med, semantic: how_bad}, fix_economics: {difficulty: {value: 1.5, default: 1.5, override: null}, roi: {value: 2.7, default: 2.7}, resource_estimate: {value: "2h", default: "2h", override: null}}, cross_impact: {affected_modules: [spec, sync, results, export, settings_dialog, lan, docs], cascade_depth: 4, dependency_chain: "簽核範圍 → 實作範圍 → POS-06 驗收"}, phase_aware: {current_phase: 0, if_not_fixed_now_breaks_at: 0, estimated_rework_cost: medium}, decision_tree: {options: [{id: A, action: 不修}, {id: B, action: 補齊清單}], recommended_option: B, counterfactual: "PO 簽核範圍少於實際改動;DSC-20 仍要求顯示第 N 排"}, dependencies: {blocks: [], blocked_by: [], manual_blocks: []}, severity_decay: {phase_when_found: 0, by_phase: {5: {value: 5.0, default: 5.0, override: null}}}, po_decision: {status: no_decision}}
```

#### C5. UI-11「未設定位置區也算一排」與「每列最多 5 格」互相矛盾

- **Assert:**
  - 未設定位置區是「每列最多 5 格」(PROPOSAL.md:170)。升級後 mosa 的 10 個探頭全部未定,這個區就有 2 列;最多可達 8 台 × 15 個 = 120 個探頭,也就是 24 列。
  - 若把它當成一排計算縮放,`_fit` 用各排高度相加後比較(main_window.py:943-969),區塊高度會被低估,「至少 4 排不捲動」的保證失效。
  - UI-11 的驗收「4 台各 4 個探頭 → 16 方塊一次顯示」在升級當下(全部未定,共 4 列)是否仍成立,提案沒有說明。
- **Pursue:** 改成「未設定位置區每一列各算一排」,或明定這個區塊固定在畫面底部、可以單獨捲動。§7 補一條 UI-11 驗收:全部未定的 16 個探頭不捲動即可看到。
- Evidence: PROPOSAL.md:170-172;main_window.py:934-969;規格書 UI-11
- Impact 4 / Prob 0.6 → 2.4

```yaml
- {tier: 🟡 CONCERN, id: C5, name: "未設定位置區多列卻算一排", evidence: ["PROPOSAL.md:170-172", "app/flatness/ui/main_window.py:943-969"], severity: {score: {value: 2.4, default: 2.4, override: null}, band: low, semantic: how_bad}, fix_economics: {difficulty: {value: 0.5, default: 0.5, override: null}, roi: {value: 4.8, default: 4.8}, resource_estimate: {value: "1h", default: "1h", override: null}}, cross_impact: {affected_modules: [main_window], cascade_depth: 1, dependency_chain: "縮放計算"}, phase_aware: {current_phase: 0, if_not_fixed_now_breaks_at: 3, estimated_rework_cost: low}, decision_tree: {options: [{id: A, action: 不修}, {id: B, action: 每列算一排}], recommended_option: B, counterfactual: "升級當天主畫面出現捲軸或方塊過小"}, dependencies: {blocks: [], blocked_by: [], manual_blocks: []}, severity_decay: {phase_when_found: 0, by_phase: {3: {value: 3.0, default: 3.0, override: null}}}, po_decision: {status: no_decision}}
```

#### C6. Excel 依「匯出當時的設定」排列,但沒有說明資料怎麼傳入、找不到的點怎麼排;第 10 節第 1 點對下游的影響也沒有寫明

- **Assert:**
  - `export.write_xlsx(path, records, day)` 只拿得到紀錄(export.py:23-41),呼叫端是 `ResultWriter.export`(results.py:91-104)與 `MemorySink.export`(main_window.py:86-95),兩者都沒有設定可用。提案只列了 `export.py`。
  - 當日紀錄中有些 `(key, id)` 在目前設定已不存在,例如探頭被刪、設備被停用或刪除(DSC-18)。這些點排在哪裡沒有規定,「未定排在最後」也不涵蓋。
  - 第 10 節第 1 點若 PO 選「保存」,以下都要一起改:
    - `inspection_point` 要 ALTER(注意 `flatness_sim.inspection_point` 是 LIKE 建立的,補欄位要兩邊都做,參照 in-win.sql:168-198)
    - `results.to_record`
    - 本機暫存檔的格式(舊暫存檔沒有這兩欄)
    - `store.write_inspection`、`read_inspections`
    - 匯出排序

    但第 5.6、6、8 節都沒有寫出「若第 10 節第 1 點為是」的分支。
- **Pursue:**
  - 第 5.6 節補:「設定中找不到的點,排在未定之後,依 key、id 排列」。
  - 寫明位置資料的傳遞方式,例如 `write_xlsx(…, positions)`,由 backend 提供。
  - 第 6、8 節加入第 10 節第 1 點的條件列。
- Evidence: PROPOSAL.md:202-207、270;export.py:23-41;results.py:29-36、91-104;in-win.sql:54-74、168-198
- Impact 5 / Prob 0.6 → 3.0

```yaml
- {tier: 🟡 CONCERN, id: C6, name: "Excel 排序資料來源與缺漏點未定義;第 10 節第 1 點的下游分支未列", evidence: ["PROPOSAL.md:202-207", "PROPOSAL.md:270", "app/flatness/export.py:23-41", "app/flatness/results.py:91-104"], severity: {score: {value: 3.0, default: 3.0, override: null}, band: med, semantic: how_bad}, fix_economics: {difficulty: {value: 1.0, default: 1.0, override: null}, roi: {value: 3.0, default: 3.0}, resource_estimate: {value: "1h", default: "1h", override: null}}, cross_impact: {affected_modules: [export, results, main_window, store, sql], cascade_depth: 3, dependency_chain: "第 10 節第 1 點 → 資料表 → 暫存檔 → 匯出"}, phase_aware: {current_phase: 0, if_not_fixed_now_breaks_at: 4, estimated_rework_cost: medium}, decision_tree: {options: [{id: A, action: 不修}, {id: B, action: 補規則與分支}], recommended_option: B, counterfactual: "已刪除探頭的舊紀錄在 Excel 中位置不定;PO 答「保存」後 M1 範圍突然擴大"}, dependencies: {blocks: [], blocked_by: [], manual_blocks: []}, severity_decay: {phase_when_found: 0, by_phase: {4: {value: 3.5, default: 3.5, override: null}}}, po_decision: {status: no_decision}}
```

#### C7. 設備生命週期與資料路徑的邊界情況沒有寫,測試清單也缺

- **Assert:** 第 7、8 節只涵蓋重複、只設其一、升級、斷線、分散兩排。以下情況沒有說明:
  - **已停用改回使用中(DSC-09)**:舊位置可能已被別台佔用。行為應是驗證失敗並標出佔用者,還是自動改為未定?POS-02 只說「已停用不佔用」。
  - **替換(DSC-14)**:`lan.replace` 會深複製 config(lan.py:461-476),位置會跟著新機走,`clear_zero` 只清歸零。這是正確行為,但提案沒寫,也沒有測試。
  - **刪除中間探頭使 ID 遞補(EDT-06)**:位置應跟著表格列(實體感測頭)走;而 `_on_field_edited` 重建 probe dict 時只保留 id、description、zero、tolerance(settings_dialog.py:1191-1199),沒寫清楚就會丟失位置。
  - **從備份還原(UPL-10)**:還原升級前的備份等於把全部位置清成未定,變更清單要列出來。
  - **降版**:Schema 的 `additionalProperties: false`(dl-en1.schema.json:37)。舊版 App 讀到有 `row`/`point` 的資料庫設定會驗證失敗,`sync.startup` 改沿用舊檔,設定頁全部報錯。提案的「舊資料照常對應」只考慮升級方向。
- **Pursue:** 新增一節「生命週期與資料路徑」逐項寫出行為,並在 M1/M2 測試清單逐條對應。降版至少寫一句「升級後不支援降版;要降版須先把位置清為未定」。
- Evidence: PROPOSAL.md:92、232-239、247-249;lan.py:398-433、461-476、514-537;settings_dialog.py:1191-1199、1246-1258;dl-en1.schema.json:37
- Impact 6 / Prob 0.5 → 3.0

```yaml
- {tier: 🟡 CONCERN, id: C7, name: "停用復用/替換/ID 遞補/還原/降版 未定義且無測試", evidence: ["PROPOSAL.md:232-249", "app/flatness/lan.py:461-476", "app/flatness/ui/settings_dialog.py:1191-1199", "app/flatness/dl-en1.schema.json:37"], severity: {score: {value: 3.0, default: 3.0, override: null}, band: med, semantic: how_bad}, fix_economics: {difficulty: {value: 1.0, default: 1.0, override: null}, roi: {value: 3.0, default: 3.0}, resource_estimate: {value: "2h", default: "2h", override: null}}, cross_impact: {affected_modules: [lan, settings_dialog, sync, tests], cascade_depth: 3, dependency_chain: "設備狀態轉換 → 驗證 → 儲存"}, phase_aware: {current_phase: 0, if_not_fixed_now_breaks_at: 2, estimated_rework_cost: medium}, decision_tree: {options: [{id: A, action: 不修}, {id: B, action: 補一節 + 測試}], recommended_option: B, counterfactual: "刪除中間探頭後位置全部消失,或停用機改回時無法儲存且原因不明"}, dependencies: {blocks: [], blocked_by: [B1], manual_blocks: []}, severity_decay: {phase_when_found: 0, by_phase: {2: {value: 4.0, default: 4.0, override: null}}}, po_decision: {status: no_decision}}
```

#### C8. 選單的佔用規則只寫了「第幾點」,沒有寫「第幾排」與選取順序

- **Assert:**
  - 第 5.2 節只說「第幾點選單中,同一排已被佔用的點停用」。POS-02 的要求是「已被佔用的**組合**停用」。
  - 以下情況沒有規定:
    - 先選點、後選排。
    - 已選好排與點之後,把排改到該點已被佔用的排。
    - 某一排 5 點都滿了,「第幾排」選單要不要停用這一排。
    - 同一張探頭表中尚未儲存的其他列算不算佔用。比照 `_fill_rows` 用 `self._devices()`(工作中的副本)的做法(settings_dialog.py:792-805),應該要算。
- **Pursue:** 補上規則:兩個選單都依「另一個選單目前的值」停用衝突項目;改排造成衝突時,把點重設為「未定」並在該列標紅;佔用的判斷包含本次編輯中尚未儲存的值。
- Evidence: PROPOSAL.md:140;settings_dialog.py:792-805;規格書 POS-02
- Impact 4 / Prob 0.6 → 2.4

```yaml
- {tier: 🟡 CONCERN, id: C8, name: "排選單與選取順序的佔用規則缺漏", evidence: ["PROPOSAL.md:140", "app/flatness/ui/settings_dialog.py:792-805"], severity: {score: {value: 2.4, default: 2.4, override: null}, band: low, semantic: how_bad}, fix_economics: {difficulty: {value: 0.5, default: 0.5, override: null}, roi: {value: 4.8, default: 4.8}, resource_estimate: {value: "1h", default: "1h", override: null}}, cross_impact: {affected_modules: [settings_dialog], cascade_depth: 1, dependency_chain: "選單 → 驗證訊息"}, phase_aware: {current_phase: 0, if_not_fixed_now_breaks_at: 2, estimated_rework_cost: low}, decision_tree: {options: [{id: A, action: 不修}, {id: B, action: 補規則}], recommended_option: B, counterfactual: "改排後出現重複位置,只能靠儲存時的驗證擋下"}, dependencies: {blocks: [], blocked_by: [B1], manual_blocks: []}, severity_decay: {phase_when_found: 0, by_phase: {2: {value: 3.0, default: 3.0, override: null}}}, po_decision: {status: no_decision}}
```

### 🟢 NITS — 可選 polish

```yaml
- {tier: 🟢 NIT, id: N1, name: "DL-EN1 欄位標題「編號」與片的「編號」(DAT-01、Excel 第一欄)同名", evidence: ["PROPOSAL.md:127", "app/flatness/export.py:49"], pursue: "改為「台號」或「第幾台」", severity: {score: {value: 0.8, default: 0.8}}, po_decision: {status: no_decision}}
- {tier: 🟢 NIT, id: N2, name: "「位置名稱」同時指探頭 description 與排/點名稱區塊", evidence: ["PROPOSAL.md:133", "PROPOSAL.md:142"], pursue: "名稱區塊改稱「排與點名稱」", severity: {score: {value: 0.6, default: 0.6}}, po_decision: {status: no_decision}}
- {tier: 🟢 NIT, id: N3, name: "3D 拒絕訊息範例「第 2 台 中排 探頭 3」與 POS-07 範例「第 2 台 中排 左」不一致", evidence: ["PROPOSAL.md:196", "規格書 POS-07"], pursue: "依 C3 的共用顯示名稱規則統一", severity: {score: {value: 0.5, default: 0.5}}, po_decision: {status: no_decision}}
- {tier: 🟢 NIT, id: N4, name: "plate_position_name:seq 沒有 1～5 的 CHECK;updated_at 沒有 ON UPDATE,UPSERT 後不會更新", evidence: ["PROPOSAL.md:109-111"], pursue: "加 CHECK (seq BETWEEN 1 AND 5),並加 ON UPDATE CURRENT_TIMESTAMP(3) 或在 UPSERT 中明確設定", severity: {score: {value: 0.6, default: 0.6}}, po_decision: {status: no_decision}}
- {tier: 🟢 NIT, id: N5, name: "第二工作表的欄名實際是「排」,不是「位置」;第一工作表的 MAC 欄標題仍是「<name> DL-EN1 MAC」", evidence: ["PROPOSAL.md:206", "app/flatness/export.py:50", "app/flatness/export.py:83"], pursue: "寫明改為「DL-EN1」欄(內容「第 N 台」),MAC 標題改為「第 N 台 <name> MAC」", severity: {score: {value: 0.6, default: 0.6}}, po_decision: {status: no_decision}}
- {tier: 🟢 NIT, id: N6, name: "_entry_issues 只把 id、description 的錯誤轉成中文列號,row/point 的錯誤會顯示原始路徑", evidence: ["app/flatness/lan.py:275-280"], pursue: "第 6 節 lan.py 列出要擴充這段正規表示式,使錯誤訊息符合 POS-01 的訊息", severity: {score: {value: 0.5, default: 0.5}}, po_decision: {status: no_decision}}
- {tier: 🟢 NIT, id: N7, name: "每個階段都推送,但 M3 到 M4 之間主畫面與 3D 的位置規則不一致", evidence: ["PROPOSAL.md:254"], pursue: "註明 M1～M4 全部完成前不部署到 mosa", severity: {score: {value: 0.7, default: 0.7}}, po_decision: {status: no_decision}}
- {tier: 🟢 NIT, id: N8, name: "沒有提到 changeset(Definition of Done)", evidence: ["PROPOSAL.md:213-228"], pursue: "M5 加 docs/release/changes/ 條目", severity: {score: {value: 0.4, default: 0.4}}, po_decision: {status: no_decision}}
```

### ✅ STRENGTHS

- 識別完全不變:量測點仍以 `device_key + probe_id` 識別(in-win.sql:69、lan.py:445-450),位置只是屬性,直接排除了 POS-A3 的風險。
- 位置存在既有的 JSON 欄位,`lan_device` 不需要 DDL;`dependentRequired` 沿用 `zero_offset/zeroed_at` 的既有寫法(dl-en1.schema.json:47),一致又容易測。
- 升級時刻意不猜位置(POS-A1),第 9 節也誠實寫出代價(升級後 3D 暫時不能用),並要求上線前安排設定。
- 對權限的說明正確:App 帳號有 `flatness.*` 的 SELECT、INSERT、UPDATE 權限(in-win.sql:207),UPSERT 不需要 DELETE。
- 3D 座標公式與 POS-07、POS-G1 的數值驗算一致:(1−0.5)/5×1000=100,(5−0.5)/5×600=540;第 2、4 點分別在 30% 與 70%。
- 第 10 節的待決事項都附有建議與代價,適合 PO 直接拍板。

## § 3. Critical Hotspots

| Finding | effective_cost | cascade_depth | 等級 | 早解 vs 晚解 |
|---|:---:|:---:|:---:|---|
| B3 名稱儲存路徑 | 5.4 | 4 | 🔥🔥🔥 | 現在改提案約 1h;M2 後才發現,要改確認頁、backend、sync、store 與測試,約 1d(約 8×) |
| B1 唯一性檢查層級 | 5.6 | 3 | 🔥🔥 | 現在約 1h;上線後要現場排查並補資料,約 1d+(約 8×) |
| B2 description/自動帶入 | 5.4 | 3 | 🔥🔥 | 現在約 1h;M6 現場驗收失敗再改,約 0.5d 加上重新設定(約 4×) |
| C4 SSOT 清單 | 4.0 | 4 | 🔥🔥 | 現在約 2h;簽核後才發現 DSC-20 衝突,要再走一輪簽核 |

## § 4. Effective Cost Matrix

| ID | Impact | Prob | Effective cost | 修正成本 |
|---|:---:|:---:|:---:|:---:|
| B1 | 7 | 0.8 | 5.6 | 1h |
| B2 | 6 | 0.9 | 5.4 | 1h |
| B3 | 6 | 0.9 | 5.4 | 1h |
| C1 | 6 | 0.6 | 3.6 | 2h |
| C2 | 5 | 0.4 | 2.0 | 2h |
| C3 | 5 | 0.7 | 3.5 | 1h |
| C4 | 5 | 0.8 | 4.0 | 2h |
| C5 | 4 | 0.6 | 2.4 | 1h |
| C6 | 5 | 0.6 | 3.0 | 1h |
| C7 | 6 | 0.5 | 3.0 | 2h |
| C8 | 4 | 0.6 | 2.4 | 1h |
| N1–N8 | — | — | 合計約 4.7 | 合計約 1.5h |
| **總計** | | | **約 45** | **約 16h(全部改提案文字)** |

Saving 的估法:現在只改提案,約 2 人日;若到 M2～M6 才發現,估計 6～8 人日的返工,外加一輪 PO 重新簽核。

## § 5. Decision Log

- 本輪沒有新的 PO 決定;所有 finding 的 `po_decision` 都是 `no_decision`。
- 沿用的前提:第 3 節的 11 項 PO 決定(2026-10-15)。本輪沒有質疑其中任何一項;B2 與 C3 是在落實這些決定,不是推翻。
- 第 10 節的 4 個待決事項維持 open;只有第 1 點因為下游沒寫分支,記為 C6。

## § 6. Verdict + Next Round Focus

- **Status:** fix-blockers(BLOCKER 3、CONCERN 8、NIT 8、STRENGTH 6)
- **Recommend:**
  - 先修 B1(把唯一性檢查拆成 bootp 與 lan 兩層)、B2(自動帶入的條件改成「預設名稱、原點名稱或空白」)、B3(名稱併入 Preview 與 sync.apply 的交易)。
  - C4 的 DSC-20 衝突應該在 PO 簽核 POS 之前補進第 9 節,否則簽核範圍不完整。
  - 其餘 CONCERN 可以在同一版一起補。
- **Next Round Focus:**
  - 第 5.4 節的狀態矩陣(C1)。
  - 新增的「生命週期與資料路徑」節(C7)。
  - 第 9 節的完整條文清單,以及規格書內嵌 Schema 的同步(C4)。
  - 探頭顯示名稱規則(C3)是否已套用到橫幅、Excel、3D。

(重大 BLOCKER,即 impact ≥ 7 且 probability ≥ 0.5,只有 B1 一項,未達 2 項,所以本輪不附 § 7 Reflection。)
