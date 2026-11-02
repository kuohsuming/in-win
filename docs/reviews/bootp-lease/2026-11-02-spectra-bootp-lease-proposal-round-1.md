---
target: docs/pm/bootp-lease/PROPOSAL.md（＋ Downloads/表面平整檢查系統_需求規格書.md DSC-21～DSC-23 與 G/A）
target_rev: cce9959
date: 2026-11-02
reviewer: spectra-review (v2.0)
iteration: 1
verdict: fix-blockers
schema_version: enhanced-v1
contract_version: spectra-contract-v1
mode: pm-skill-generic-doc
---

> 💡 spectra-review v2.0 active(Minerva 4 能力 framework)。若想用原版簡潔版,用 `/spectra-review --lite <target>`。

🎯 Mode: PM Skill — Generic doc (target: docs/pm/bootp-lease/PROPOSAL.md)

# Spectra-Review Round 1 — docs/pm/bootp-lease/PROPOSAL.md

本輪範圍與限制:
- 對照來源:規格書 DSC-21～23(997-999)與 G/A(1003-1008);鄰近條文 DSC-01、DSC-07、DSC-08、DSC-10、DSC-14、DSC-15、DSC-19、DSC-20、INS-04(142)、3.0.4 步驟 3(200)、3.0.7(309)、3.0.8(318-323)、PDT-01(1165)、修訂附註(1037-1038)。
- 程式碼:installer/steps/03-bootp.sh、installer/setup-bootp.sh、installer/steps/02-equip-net.sh、installer/lib/common.sh、app/flatness/{dnsmasq,sync,backend,discovery,lan,store}.py、ui/settings_dialog.py、ui/main_window.py、scripts/fake-dnsmasq.py。
- 現場證據:/etc/flatness/dnsmasq.conf(live,無 `leasefile-ro`)、/var/lib/misc/dnsmasq.leases(root 644,現含 `0 74:95:a7:15:9b:82 192.168.10.11 row-1 *`)、/var/lib/flatness/bootp/dl-en1.hosts、mosa App 日誌 `.dev/flatness.log`(2026-11-02 事件當日)、`/usr/sbin/dnsmasq` 二進位字串(2.90)。
- SKILL 提到但本 repo 沒有的檔案(docs/CONTEXT.md、docs/index.md、pm-skill-proposal.md、state.md、decision-log.md)略過;docs/ai-principles.md 已讀。
- 依呼叫者指示,本輪只寫 F1。F2(`_summary-*.md`)與 decision-log audit entry 未寫。

## § 1. Mental Lens

- **Claim → Evidence → Verdict**:提案第 1 節事件時間線、第 3 節「重新啟動會清掉記憶體租約」「setup-bootp.sh 只重寫主設定」「租約檔可讀」、第 3.3 節日誌字串,逐一對照程式碼、live 檔案與當日 App 日誌。
- **Cross-section consistency**:提案 ↔ DSC-21～23 ↔ DSC-15/DSC-20 顯示優先序 ↔ DSC-08/DSC-10/DSC-14 告警語意 ↔ 3.0.8 重複執行行為。
- **Anti-Bias**:提案與規格書出自同一作者同一天,彼此一致不代表與現場一致。本輪最重要的發現(B2)正是兩份文件共享同一個錯誤的事件敘述,只有回到 App 日誌才看得出來。
- **Understand-not-argue**:`leasefile-ro` 的方向正確且成本極低(S1、S2)。下列 finding 補的是升級路徑、事件根因的另一半,以及顯示規則的邊界,不改 PO 的提議本身。

## § 2. 4-Tier Findings

### 🔴 BLOCKERS — 落地前必修

#### B1. 重跑 setup-bootp.sh 不會重新啟動 App 的 dnsmasq;DSC-23-G1 與 DSC-22 ② 指示的處理方式當下無效

**📛 命名(Identify):** 提案 3.1 節說現有機器「執行一次 `sudo ./installer/setup-bootp.sh`(只重寫主設定,可重複執行)。之後原本的租約檔不再被讀取,不必手動刪除」(PROPOSAL.md:48)。DSC-22 ② 的警告文字叫維護人員執行同一支程式(PROPOSAL.md:57;規格書:998)。DSC-23-G1 寫「維護人員執行 setup-bootp.sh → 新機取得 IP,提示消失」(規格書:1005)。

**📣 主張(Assert):**
- Why BLOCKER:
  - `step_bootp` 寫入主設定後只做 `systemctl disable --now dnsmasq` 與 `mask`(03-bootp.sh:38-58、67-68)。這只影響已遮蔽的系統服務。App 的 dnsmasq 是 App 以 sudo 啟動的子程序(dnsmasq.py:27-28、202-221),安裝包完全不碰它。
  - 執行中的 dnsmasq 在啟動時已把舊租約讀進記憶體。主設定改了它也不會重讀,所以 B 仍持續收到 `address in use`。
  - 主機對應沒有變更時 App 不會重新啟動 dnsmasq(sync.py:154、164-165)。DSC-23-G1 的情境正是「B 已儲存、正在被拒」,維護人員跑完程式之後沒有任何東西會觸發重新啟動。結果要等到有人重新啟動 App 或再改一次設定。
  - DSC-22 ② 依「主設定是否含 `leasefile-ro`」判斷要不要檢查租約檔(PROPOSAL.md:57)。跑完 setup-bootp.sh 後主設定已含 `leasefile-ro`,警告就消失了,但執行中的程序其實仍拿著舊租約。畫面因此說「沒問題」,BOOTP 卻還在拒絕。
  - 「只重寫主設定」與實作不符。setup-bootp.sh 還會執行 `step_equip_net`,設定有差異時會跑 `netplan apply`(setup-bootp.sh:19、02-equip-net.sh:12-27),並重寫停止程式、ARP 監聽程式、sudoers 與 ufw 規則(03-bootp.sh:76-105)。這些都經 `write_if_changed` 做到冪等(common.sh:31-40),所以「可重複執行」成立,「只重寫主設定」不成立。
- Impact: 7/10 / Probability: 0.8。每一台既有機器的升級都走這條路徑,現場依照文件處理後仍拿不到 IP。
- Evidence: PROPOSAL.md:48、57;規格書:998、1005、323;installer/steps/03-bootp.sh:38-58、67-68、76-105;installer/setup-bootp.sh:17-20;app/flatness/sync.py:154、164-165;app/flatness/dnsmasq.py:27-28、232-250
- Cross-Module Impact:安裝包、執行中的 dnsmasq、DSC-22 ② 的判斷依據、DSC-23 恢復提示、操作說明書 10.1/11.4、快速安裝指南。
- Phase-aware:M1 寫錯之後,M5 的「重跑 setup-bootp.sh 後 IP 對調測試」仍會通過,因為對調會改主機對應而觸發重新啟動。這個測試遮住了缺陷,要到現場照 G1 處理時才會發現。

**🎯 追求(Pursue):**
1. 在 `step_bootp` 中,主設定有寫入(`write_if_changed` 回傳 0)時執行 `$STOP_HELPER`。App 的 `DnsmasqService` 會把它當成異常結束,2 秒後以新主設定自動重新啟動(dnsmasq.py:232-250)。這不需要新增任何 sudo 權限。App 沒在執行時 pkill 找不到程序,不影響安裝。
2. 3.0.8 補一列:「dnsmasq 主設定有變更時,停止 App 的 dnsmasq,由 App 自動以新設定重新啟動」。
3. DSC-22 ② 的判斷改為「主設定未含 `leasefile-ro`,**或** 執行中的 dnsmasq 啟動時間早於主設定的修改時間」。啟動時間取 `/proc/<pid>/stat`,dnsmasq.py:32-46 已讀過 `/proc`。
4. 3.1 節改寫為「重寫 BOOTP 相關設定(主設定、停止程式、ARP 監聽、sudoers、防火牆;內容相同者不變),並使 App 的 dnsmasq 以新設定重新啟動」。

**📊 Decision Tree:**

| Option | 動作 | 成本 | 備註 |
|---|---|---|---|
| A | 不修 | 0 | 現場照文件做,B 仍拿不到 IP,只好再找人 sudo 刪租約檔,重演事件 |
| B | 現在修(安裝包呼叫停止程式並改寫文件) | 2h | 不增加權限;重新啟動時畫面會短暫顯示「BOOTP 服務停止」並記錄日誌,需在文件中說明 |
| C | 只在文件中加「之後請重新啟動 App」 | 0.5h | 依賴人記得;DSC-22 ② 的誤判仍在 |

**📍 推薦:** Option B
**🔮 反事實:** 不修的話,下一台舊安裝的機器出現 DSC-23 提示,維護人員照著執行 setup-bootp.sh 並看到「已寫入 /etc/flatness/dnsmasq.conf」,但主畫面提示不消失,設定頁的舊租約警告卻已消失。現場會判斷為新的故障。

```yaml
- tier: 🔴 BLOCKER
  id: B1
  name: "setup-bootp.sh 不重新啟動 App 的 dnsmasq,G1 與 DSC-22 ② 的處理方式當下無效"
  evidence: ["PROPOSAL.md:48", "PROPOSAL.md:57", "規格書:1005", "installer/steps/03-bootp.sh:38-58,67-68", "app/flatness/sync.py:154,164-165", "app/flatness/dnsmasq.py:232-250"]
  severity: {score: {value: 5.6, default: 5.6, override: {by: null, at: null, reason: null}}, band: med, semantic: how_bad}
  fix_economics: {difficulty: {value: 1.0, default: 1.0, override: null}, roi: {value: 5.6, default: 5.6}, resource_estimate: {value: "2h", default: "2h", override: null}}
  cross_impact: {affected_modules: [installer, dnsmasq-runtime, lan(DSC-22②), main_window(DSC-23), docs], cascade_depth: 3, dependency_chain: "主設定改寫 → 執行中程序未重讀 → DSC-22② 誤判 / DSC-23 提示不消失"}
  phase_aware: {current_phase: 0, if_not_fixed_now_breaks_at: 6, estimated_rework_cost: medium}
  decision_tree: {options: [{id: A, action: 不修}, {id: B, action: 安裝包呼叫停止程式並改寫文件}, {id: C, action: 只改文件}], recommended_option: B, counterfactual: "照 G1 處理後 B 仍被拒,DSC-22② 警告卻已消失"}
  dependencies: {blocks: [C5], blocked_by: [], manual_blocks: []}
  severity_decay: {phase_when_found: 0, by_phase: {1: {value: 5.6, default: 5.6, override: null}, 6: {value: 7.0, default: 7.0, override: null}}}
  po_decision: {status: no_decision, decided_at: null, decided_by: null, reason: null}
```

#### B2. 事件時間線錯置:前 39 分鐘是「尚未儲存、MAC 不在主機對應」(`no address available`),不是舊租約;DSC-23 把兩種原因寫成同一句「被其他設備佔用」

**📛 命名(Identify):** 提案寫的時間線(PROPOSAL.md:14-17):
- 09:40 新機設為使用中、IP .11;
- 09:41～10:42 dnsmasq 每次回 `address in use`,共約 700 次;
- App 每次重新啟動 dnsmasq 都重讀租約檔。

DSC-23 把 `address in use` 與 `no address available` 視為同一種拒絕,顯示「<IP> 被其他設備佔用」(PROPOSAL.md:64-65;規格書:999)。驗收條件是「一小時內被拒 700 次」。

**📣 主張(Assert):** mosa 當日 App 日誌 `.dev/flatness.log` 的實際經過:

| 時間 | 日誌 | 意義 |
|---|---|---|
| 09:40:25～09:40:38 | 依序刪除 前沿(00:01:FC:DE:3A:75,當時 IP .21)、試用(00:01:FC:12:3B:11,當時 IP .11)與兩台不明設備,前兩次刪除重新啟動 dnsmasq(pid 2563) | 舊設備清除 |
| 09:41:44～10:20:31 | `BOOTP(eno2) 74:95:a7:15:9b:82 no address available` × **545** | plat1 在資料庫仍是**不明設備**,MAC 不在主機對應 |
| 09:44、09:47、09:48、10:17 | 「探頭偵測 74:95:A7:15:9B:82(192.168.10.11)失敗:timed out」× 4 | 工程人員對**尚未儲存**的設定按探頭偵測 |
| 10:20:37 | 「套用設備設定成功…新增 第 1 台 plat1…dnsmasq 已重新啟動」(pid 3523) | 這時才設為使用中 |
| 10:20:36～10:42:15 | `BOOTP(eno2) 192.168.10.11 74:95:a7:15:9b:82 address in use` × **304** | 舊租約佔用,約 22 分鐘 |
| 10:42:18～10:42:20 | App 收到 SIGTERM 結束、重新啟動,1 秒後 plat1 取得 .11 | 處理方式是重新啟動 App |

- Why BLOCKER:
  - 提案把整小時歸給舊租約。實際上 39/61 分鐘的原因是「設定尚未套用」,DSC-21 對這段時間**完全沒有幫助**。
  - 依 dnsmasq 2.90 的 BOOTP 流程,static range 下 MAC 不在主機對應時會記 `no address available`(這行沒有 IP)。現場有 545 行可證。discovery.py:5 與 scripts/fake-dnsmasq.py:47 寫的 `no address configured` 不是本機設定會出現的字串。
  - 對「使用中/維修中」設備而言,`no address available` 代表 dnsmasq 載入的主機對應沒有這個 MAC,或設定的 IP 不在 range 內。可能的情況:
    - 資料庫斷線,沿用舊主機對應(DSC-06);
    - 網段變更(DSC-11);
    - 尚未套用。
  - 上面每一種都**不是**「被其他設備佔用」。照 DSC-23 的文字顯示,會把維護人員引向錯的處理(去找佔用者、跑 setup-bootp.sh)。
  - 前 39 分鐘真正的使用者陷阱是 PDT-01 的「探頭偵測」可以對尚未儲存、BOOTP 尚未配發的 IP 執行(settings_dialog.py:1576-1595 取 `self.work` 的 `ipv4`),失敗只顯示「偵測不到」(settings_dialog.py:1601-1603)。提案沒有處理這一點。
  - 驗收條件的「一小時」「700 次」是錯誤敘述算出來的數字。實際是 22 分鐘 304 次 `address in use`,加上 39 分鐘 545 次 `no address available`。
- Impact: 6/10 / Probability: 0.8。換新機時「先設定、先偵測、後儲存」是自然的操作順序。
- Evidence: PROPOSAL.md:14-17、64-65、89-93;規格書:999、1001、1008、1165;`.dev/flatness.log`(09:40:25-10:42:20 各行);app/flatness/discovery.py:3-6、30-32;scripts/fake-dnsmasq.py:40-47、56;app/flatness/ui/settings_dialog.py:1576-1603
- Cross-Module Impact:discovery 解析、DSC-23 訊息與驗收、PDT-01 探頭偵測、測試替身 fake-dnsmasq 與 tests/test_discovery.py:28、操作說明書「拿不到 IP」章節。
- Phase-aware:M2 會依錯誤字串寫出解析器與測試,fake-dnsmasq 也會給出錯誤的綠燈。

**🎯 追求(Pursue):**
1. 第 1 節時間線依日誌重寫,把根因分成兩段:①設定未套用(39 分);②舊租約(22 分)。並註明舊租約登記者(前沿)是推論,依據是 10-07 DSC-20 測試時前排由 .11 改為 .21;租約檔內容已被覆蓋,無法再查證。
2. DSC-23 依日誌原因分開顯示:
   - `address in use`:「<IP> 被其他設備佔用(BOOTP 拒絕配發)」;
   - `no address available`:「BOOTP 主機對應沒有這台(設定尚未套用,或 IP 不在設備網段)」,IP 從設定取得(日誌行沒有 IP)。
3. 新增一條(或併入 DSC-23):設定頁對「狀態或 IP 尚未儲存」的設備按探頭偵測失敗時,提示「設定尚未儲存,BOOTP 尚未配發 <IP>;請先儲存」。設備在日誌中正以 `no address available` 被拒時,也直接顯示這個原因。
4. 驗收數字改為實測值,或改成不依賴事件的寫法(「持續被拒 ≥ 100 次」)。
5. discovery.py 的 docstring、fake-dnsmasq.py 與 test_discovery 改用真實字串。

**📊 Decision Tree:**

| Option | 動作 | 成本 | 備註 |
|---|---|---|---|
| A | 不修 | 0 | DSC-23 對兩種原因給同一個錯誤指示;最常見的「未儲存」陷阱仍在 |
| B | 現在修(改時間線、DSC-23 依原因分開、補未儲存提示) | 3h | 推薦 |
| C | DSC-23 只處理 `address in use`,另立條目處理未儲存 | 1.5h + 另一輪簽核 | 範圍較小,但 `no address available` 在本提案中仍需刪除 |

**📍 推薦:** Option B
**🔮 反事實:** 不修的話,下次換新機,工程人員在儲存前按探頭偵測,得到「偵測不到」;儲存後若資料庫恰好斷線,主畫面顯示「被其他設備佔用,請洽維護人員」;維護人員跑 setup-bootp.sh 無效(B1),問題實際上與佔用無關。

```yaml
- tier: 🔴 BLOCKER
  id: B2
  name: "事件時間線錯置;no address available 不是佔用,DSC-23 訊息錯誤,未儲存偵測陷阱未處理"
  evidence: ["PROPOSAL.md:14-17", "PROPOSAL.md:64-65", "PROPOSAL.md:89-93", "規格書:999", ".dev/flatness.log 09:40:25-10:42:20", "app/flatness/discovery.py:3-6", "scripts/fake-dnsmasq.py:47", "app/flatness/ui/settings_dialog.py:1576-1603"]
  severity: {score: {value: 4.8, default: 4.8, override: {by: null, at: null, reason: null}}, band: med, semantic: how_bad}
  fix_economics: {difficulty: {value: 1.5, default: 1.5, override: null}, roi: {value: 3.2, default: 3.2}, resource_estimate: {value: "4h", default: "4h", override: null}}
  cross_impact: {affected_modules: [discovery, main_window, settings_dialog, fake-dnsmasq, tests, docs], cascade_depth: 3, dependency_chain: "日誌原因分類 → DSC-23 訊息 → 現場處理方向"}
  phase_aware: {current_phase: 0, if_not_fixed_now_breaks_at: 2, estimated_rework_cost: medium}
  decision_tree: {options: [{id: A, action: 不修}, {id: B, action: 改時間線並分開原因、補未儲存提示}, {id: C, action: 縮小 DSC-23 範圍並另立條目}], recommended_option: B, counterfactual: "主機對應未載入時被報成佔用,維護人員往錯的方向處理"}
  dependencies: {blocks: [C2, C6], blocked_by: [], manual_blocks: []}
  severity_decay: {phase_when_found: 0, by_phase: {2: {value: 5.5, default: 5.5, override: null}, 6: {value: 6.5, default: 6.5, override: null}}}
  po_decision: {status: no_decision, decided_at: null, decided_by: null, reason: null}
```

### 🟡 CONCERNS — 應修

#### C1. DSC-23 與 DSC-20(IP 不符)、偵測不到、維修中的顯示優先序未定義

- **主張:** DSC-23 只說「取代單純的偵測不到」(規格書:999)。
  - **DSC-20 衝突:** DL-EN1 按 RST 後放棄舊 IP 並送 BOOTP。若被拒,設備沒有 IP、不會再送 ARP。主畫面 `seen_ips` 仍是舊 IP(main_window.py:1084-1092),所以「IP 不符…請按住 RST 3 秒」會繼續顯示(main_window.py:1104-1116)。這時同時出現兩個互相矛盾的指示:DSC-20 叫人再按 RST,DSC-23 叫人洽維護人員。
  - **維修中:** 維修中的方塊顯示「維修中」,不連線、不列入偵測(DSC-15,規格書:857;main_window.py:338-349),根本不會出現「偵測不到」,所以「取代偵測不到」對維修中沒有定義。DSC-20 對維修中用的是「IP 不符・維修中」(main_window.py:1107)。
  - **頂端提示:** DSC-20 規定「偵測不到時以偵測不到優先,頂端提示仍顯示」(規格書:985),DSC-23 沒有對應規則。旗標列(main_window.py:1070-1073)要新增哪一類、排在哪裡,也沒寫。
- **Evidence:** 規格書:857、985、999;app/flatness/ui/main_window.py:338-349、1070-1073、1084-1117、1305-1311
- **追求:** 在 DSC-23 加優先序:
  - BOOTP 被拒期間,該台的「IP 不符」方塊標示與 RST 提示暫停,被拒是更新的事實;
  - 維修中方塊顯示「拿不到 IP・維修中」,不進入異常橫幅(DSC-15 不阻擋作業);
  - 頂端提示新增一類,顏色同「dev」。
- Decision:A 不修(現場出現矛盾指示)/ B 現在補三句規則(0.5h)。推薦 B。

```yaml
- tier: 🟡 CONCERN
  id: C1
  name: "DSC-23 與 DSC-20/偵測不到/維修中顯示優先序未定義"
  evidence: ["規格書:857", "規格書:985", "規格書:999", "app/flatness/ui/main_window.py:338-349", "app/flatness/ui/main_window.py:1084-1117"]
  severity: {score: {value: 2.5, default: 2.5, override: {by: null, at: null, reason: null}}, band: low, semantic: how_bad}
  fix_economics: {difficulty: {value: 0.5, default: 0.5, override: null}, roi: {value: 5.0, default: 5.0}, resource_estimate: {value: "1h", default: "1h", override: null}}
  cross_impact: {affected_modules: [main_window, spec DSC-15/DSC-20], cascade_depth: 2, dependency_chain: "顯示規則 → 方塊/旗標/橫幅"}
  phase_aware: {current_phase: 0, if_not_fixed_now_breaks_at: 2, estimated_rework_cost: low}
  decision_tree: {options: [{id: A, action: 不修}, {id: B, action: 補優先序}], recommended_option: B, counterfactual: "RST 後被拒時畫面同時叫人按 RST 與洽維護人員"}
  dependencies: {blocks: [], blocked_by: [B2], manual_blocks: []}
  severity_decay: {phase_when_found: 0, by_phase: {2: {value: 3.0, default: 3.0, override: null}}}
  po_decision: {status: no_decision, decided_at: null, decided_by: null, reason: null}
```

#### C2. 「App 日誌只有一筆拒絕紀錄」與現行實作矛盾:App 本來就逐行寫入 dnsmasq 輸出

- **主張:**
  - `Backend._on_line` 把 dnsmasq 的每一行以 logger `dnsmasq` 寫入 App 日誌(backend.py:22、88-89)。
  - 事件當日 App 日誌有 304 行 `address in use`,另有 545 行 `no address available`(`.dev/flatness.log`)。
  - DSC-23 驗收要求「一小時內被拒 700 次,App 日誌只有一筆拒絕紀錄」(規格書:999;PROPOSAL.md:67)。照現行實作,這條永遠不成立;若為了通過而停止寫入 dnsmasq 原始行,又會失去 DSC-01 的稽核資料。
- **Evidence:** app/flatness/backend.py:22、88-89;規格書:999;PROPOSAL.md:67
- **追求:** 驗收改寫為「App 的拒絕警告(WARNING,logger `flatness.*`)在狀態改變時各一筆;dnsmasq 原始輸出照常保存」,或明定原始行降級或抽樣。PO 選一。

```yaml
- tier: 🟡 CONCERN
  id: C2
  name: "「App 日誌只有一筆」與逐行寫入 dnsmasq 輸出矛盾"
  evidence: ["app/flatness/backend.py:88-89", "規格書:999", ".dev/flatness.log"]
  severity: {score: {value: 3.0, default: 3.0, override: {by: null, at: null, reason: null}}, band: med, semantic: how_bad}
  fix_economics: {difficulty: {value: 0.3, default: 0.3, override: null}, roi: {value: 10.0, default: 10.0}, resource_estimate: {value: "1h", default: "1h", override: null}}
  cross_impact: {affected_modules: [backend, spec DSC-23 驗收], cascade_depth: 1, dependency_chain: "驗收文字 → M2 測試"}
  phase_aware: {current_phase: 0, if_not_fixed_now_breaks_at: 2, estimated_rework_cost: low}
  decision_tree: {options: [{id: A, action: 不修}, {id: B, action: 改驗收文字}], recommended_option: B, counterfactual: "M2 驗收必然失敗,或為了通過而刪除 dnsmasq 原始紀錄"}
  dependencies: {blocks: [], blocked_by: [B2], manual_blocks: []}
  severity_decay: {phase_when_found: 0, by_phase: {2: {value: 3.5, default: 3.5, override: null}}}
  po_decision: {status: no_decision, decided_at: null, decided_by: null, reason: null}
```

#### C3. DSC-22 ① 與 DSC-08、DSC-10、DSC-14 重疊:同一佔用者會被重複告警,而且每次替換都會跳警告

- **主張:** ①的條件是「其他**任何**狀態的設備,實際使用 IP 等於此 IP」(規格書:998)。這個條件與既有規則有四處重疊:
  - (a) 使用中、維修中、其他設備若 `ipv4` 也等於此 IP,DSC-08 已經禁止(lan.py:266-271、362-375)。①會在錯誤旁邊再加一條警告。
  - (b) 佔用者在線時,DSC-10 的 ARP 探測已回報同一個 MAC(settings_dialog.py:1172-1179、1802-1818)。同一台會出現兩條警告。
  - (c) DSC-14 替換時,舊機改為已停用,而它的 `seen_ip` 必然等於交給新機的 IP(lan.py:525-540)。所以**每一次替換**都會跳①的警告,即使舊機已經拔除。DSC-14 原本對舊機只給專用提示,而且只在舊機在線時才給(settings_dialog.py:1806-1808;規格書:856)。
  - (d) 已停用設備的 `seen_ip` 永不清除,只有 ARP 會更新(store.py:95、293),報廢多年的設備也會一直被列出。
- **Evidence:** 規格書:856、998;app/flatness/lan.py:266-271、362-375、525-540;app/flatness/ui/settings_dialog.py:1172-1179、1802-1818;app/flatness/store.py:95、293
- **追求:** ①的條件精確化為:
  - `mac ≠ 本機`,且 `seen_ip == ip`;
  - 排除 DSC-08 已報錯者:佔用者 `assigns_ip` 且 `ipv4 == ip`;
  - 排除本次編輯中替換的舊機:改用 DSC-14 的文字「舊機仍記得此 IP,請勿再接上網路」;
  - 與 DSC-10 同一 MAC 時合併成一條。
  
  另外可考慮「最後出現超過 N 天者不列」,或保留但標示出現日期(目前範例已有日期)。

```yaml
- tier: 🟡 CONCERN
  id: C3
  name: "DSC-22① 與 DSC-08/10/14 重疊,替換必跳警告"
  evidence: ["規格書:998", "app/flatness/lan.py:525-540", "app/flatness/ui/settings_dialog.py:1802-1818", "app/flatness/store.py:293"]
  severity: {score: {value: 2.8, default: 2.8, override: {by: null, at: null, reason: null}}, band: low, semantic: how_bad}
  fix_economics: {difficulty: {value: 0.5, default: 0.5, override: null}, roi: {value: 5.6, default: 5.6}, resource_estimate: {value: "1h", default: "1h", override: null}}
  cross_impact: {affected_modules: [lan, settings_dialog, spec DSC-14/DSC-22], cascade_depth: 2, dependency_chain: "告警條件 → 檢查訊息 → 確認頁"}
  phase_aware: {current_phase: 0, if_not_fixed_now_breaks_at: 3, estimated_rework_cost: low}
  decision_tree: {options: [{id: A, action: 不修}, {id: B, action: 精確化條件}], recommended_option: B, counterfactual: "每次替換都出現衝突警告,工程人員學會忽略它"}
  dependencies: {blocks: [], blocked_by: [], manual_blocks: []}
  severity_decay: {phase_when_found: 0, by_phase: {3: {value: 3.0, default: 3.0, override: null}}}
  po_decision: {status: no_decision, decided_at: null, decided_by: null, reason: null}
```

#### C4. 修訂清單與影響範圍前後不一、不完整

- **主張:**
  - **修訂清單三處說法不同:**
    - 提案開頭寫「修訂 INS-04(3.0.4 步驟 3)、DSC-07、DSC-10」(PROPOSAL.md:4);
    - DSC-21 寫「修訂 INS-04/3.0.4 步驟 3、3.0.7」(規格書:997);
    - DSC-22 寫「修訂 DSC-10」(規格書:998)。
    
    DSC-07 要改什麼,沒有任何一條寫出來(第 2 節表格也說 DSC-07「不變」,PROPOSAL.md:39)。3.0.7 不在提案開頭的清單中。
  - **漏列的條文:**
    - 3.0.8(重跑時要讓 dnsmasq 以新設定重新啟動,見 B1;規格書:323);
    - DSC-20 與 DSC-15(顯示優先序,見 C1);
    - PDT-01(未儲存時探頭偵測,見 B2);
    - INS-04 本文(142)、3.0.4 步驟 3(200)、3.0.7(309)、修訂附註(1037)都還沒加入 `leasefile-ro`。待簽核期間可以接受,但應逐一列出。
  - **影響範圍漏列的程式:** `scripts/fake-dnsmasq.py`、`tests/test_discovery.py`(字串錯誤,B2)、`main_window` 的旗標列,以及 `backend` 的拒絕狀態保存與 Signal(設定頁「最近 <時間>」需要跨對話框保存)。
- **Evidence:** PROPOSAL.md:4、39、75-83;規格書:142、200、309、323、997、998、1037
- **追求:** 提案開頭與各條「修訂」括號統一為同一份清單;刪除 DSC-07,或寫明要改的句子;補上上述條文與檔案。

```yaml
- tier: 🟡 CONCERN
  id: C4
  name: "修訂清單與影響範圍前後不一、不完整"
  evidence: ["PROPOSAL.md:4", "PROPOSAL.md:39", "PROPOSAL.md:75-83", "規格書:997", "規格書:998", "規格書:323"]
  severity: {score: {value: 2.4, default: 2.4, override: {by: null, at: null, reason: null}}, band: low, semantic: how_bad}
  fix_economics: {difficulty: {value: 0.5, default: 0.5, override: null}, roi: {value: 4.8, default: 4.8}, resource_estimate: {value: "1h", default: "1h", override: null}}
  cross_impact: {affected_modules: [spec, proposal], cascade_depth: 2, dependency_chain: "修訂清單 → 簽核範圍 → 實作範圍"}
  phase_aware: {current_phase: 0, if_not_fixed_now_breaks_at: 1, estimated_rework_cost: low}
  decision_tree: {options: [{id: A, action: 不修}, {id: B, action: 統一並補齊}], recommended_option: B, counterfactual: "簽核的範圍與實作的範圍不一致,3.0.8 與 DSC-20 沒有人去改"}
  dependencies: {blocks: [], blocked_by: [], manual_blocks: []}
  severity_decay: {phase_when_found: 0, by_phase: {1: {value: 2.4, default: 2.4, override: null}}}
  po_decision: {status: no_decision, decided_at: null, decided_by: null, reason: null}
```

#### C5. 舊租約檔留在原地:之後若 `leasefile-ro` 被拿掉(例如重跑舊版安裝包),舊租約會整批復活

- **主張:**
  - 提案說加入 `leasefile-ro` 後「不必手動刪除」租約檔(PROPOSAL.md:48)。
  - mosa 的租約檔目前仍有 `0 74:95:a7:15:9b:82 192.168.10.11 row-1 *`,這是永久租約(/var/lib/misc/dnsmasq.leases)。
  - `write_if_changed` 一律以安裝包內容覆寫主設定(03-bootp.sh:38;common.sh:31-40)。所以只要在任何機器重跑**舊版**安裝包,`leasefile-ro` 就會被移除。之後 dnsmasq 重新讀回這份檔案,事件重演,而且 DSC-22 ② 的警告要到下次設定 IP 時才會出現。
  - 安裝包以 root 執行,本來就有權限處理這個檔案。
- **Evidence:** PROPOSAL.md:48;/var/lib/misc/dnsmasq.leases(live);installer/steps/03-bootp.sh:38;installer/lib/common.sh:31-40
- **追求:** M1 在加入 `leasefile-ro` 的同一步把租約檔改名為 `dnsmasq.leases.flatness-old`(保留備查),並寫入安裝日誌。AC-5 改為「租約檔不存在,或重新啟動多次後未被修改」。

```yaml
- tier: 🟡 CONCERN
  id: C5
  name: "舊租約檔未清除,移除 leasefile-ro 時舊租約復活"
  evidence: ["PROPOSAL.md:48", "/var/lib/misc/dnsmasq.leases", "installer/steps/03-bootp.sh:38", "installer/lib/common.sh:31-40"]
  severity: {score: {value: 1.5, default: 1.5, override: {by: null, at: null, reason: null}}, band: low, semantic: how_bad}
  fix_economics: {difficulty: {value: 0.3, default: 0.3, override: null}, roi: {value: 5.0, default: 5.0}, resource_estimate: {value: "1h", default: "1h", override: null}}
  cross_impact: {affected_modules: [installer], cascade_depth: 2, dependency_chain: "安裝包版本 → 主設定 → 租約檔重讀"}
  phase_aware: {current_phase: 0, if_not_fixed_now_breaks_at: 7, estimated_rework_cost: low}
  decision_tree: {options: [{id: A, action: 不修}, {id: B, action: 安裝包改名舊租約檔}], recommended_option: B, counterfactual: "重跑舊版安裝包後,永久租約整批生效"}
  dependencies: {blocks: [], blocked_by: [B1], manual_blocks: []}
  severity_decay: {phase_when_found: 0, by_phase: {7: {value: 2.0, default: 2.0, override: null}}}
  po_decision: {status: no_decision, decided_at: null, decided_by: null, reason: null}
```

#### C6. DSC-23 的判定規則還不到可實作的程度

- **主張:**
  - **成功與拒絕行同形:** 成功配發與拒絕的日誌行格式相同,例如 `BOOTP(eno2) 192.168.10.11 74:95:a7:15:9b:82 `(10:42:20 成功,行尾只有空白)與 `… 192.168.10.11 74:95:a7:15:9b:82 address in use`。現行 `_PACKET_RE` 會丟棄 MAC 之後的文字(discovery.py:30-32、61)。提案只寫「日誌出現配發」(PROPOSAL.md:68),沒有定義成功怎麼判斷。建議的判斷:有 IP 且行尾不是已知拒絕字串。
  - **拒絕字串清單不完整:** dnsmasq 2.90 的 BOOTP 拒絕還有 `wrong network`、`ignored`、`disabled`(二進位字串可查),提案沒說要不要涵蓋。
  - **狀態存放位置未定:** 「設定頁 最近 <時間>」需要 backend 保存每個 MAC 的拒絕狀態,設定對話框之後才開啟也要讀得到。目前 `Backend` 沒有這個狀態,也沒有對應的 Signal(backend.py:26-28)。
  - **App 重新啟動後的行為未定:** 狀態歸零後是否重新記一筆日誌,沒寫。
- **Evidence:** app/flatness/discovery.py:30-32、61;app/flatness/backend.py:26-28;PROPOSAL.md:64-68;`.dev/flatness.log` 10:42:20
- **追求:** 在提案 3.3 節補四點:
  1. 拒絕字串清單,及各字串對應的訊息;
  2. 成功的判定;
  3. 狀態放在 backend,以 Signal 通知主畫面與設定頁;
  4. App 重新啟動後狀態歸零,再被拒時重新記錄。

```yaml
- tier: 🟡 CONCERN
  id: C6
  name: "DSC-23 判定規則(成功行、拒絕字串、狀態存放)未定義"
  evidence: ["app/flatness/discovery.py:30-32", "app/flatness/backend.py:26-28", "PROPOSAL.md:64-68"]
  severity: {score: {value: 2.4, default: 2.4, override: {by: null, at: null, reason: null}}, band: low, semantic: how_bad}
  fix_economics: {difficulty: {value: 0.5, default: 0.5, override: null}, roi: {value: 4.8, default: 4.8}, resource_estimate: {value: "1h", default: "1h", override: null}}
  cross_impact: {affected_modules: [discovery, backend, main_window, settings_dialog], cascade_depth: 2, dependency_chain: "解析 → 狀態 → 兩個畫面"}
  phase_aware: {current_phase: 0, if_not_fixed_now_breaks_at: 2, estimated_rework_cost: low}
  decision_tree: {options: [{id: A, action: 不修}, {id: B, action: 補判定規則}], recommended_option: B, counterfactual: "實作者自行猜測成功行格式,提示不消失或過早消失"}
  dependencies: {blocks: [], blocked_by: [B2], manual_blocks: []}
  severity_decay: {phase_when_found: 0, by_phase: {2: {value: 3.0, default: 3.0, override: null}}}
  po_decision: {status: no_decision, decided_at: null, decided_by: null, reason: null}
```

### 🟢 NITS — 可選 polish

- **N1. AC-1 的「10 秒內」最壞情況可能超過。**
  - 時間組成:重新啟動含正常停止與 1.5 秒觀察(dnsmasq.py:186-195);改用停止程式的備援路徑最多再加 5 秒(dnsmasq.py:262-265);DL-EN1 BOOTP 重送間隔實測平均約 4.3 秒(09:41-10:20 共 545 次)。三者相加會超過 10 秒。
  - 建議:改為「儲存完成後 15 秒內」,或「dnsmasq 重新啟動完成後 10 秒內」。
  - 證據:PROPOSAL.md:89;規格書:997。
- **N2. 「`--test` 確認語法」不等於「確認行為」。**
  - `dnsmasq --test` 只檢查語法(PROPOSAL.md:45),「不讀不寫租約檔」的行為要靠 AC-5 驗證。
  - 建議:3.1 節寫明這兩件事由不同方式驗證。
- **N3. DSC-22 的範例與 G1 暗示它能攔下本次事件,但事實上攔不到。**
  - 範例中的佔用者是「已停用 前沿」(PROPOSAL.md:56;規格書:1004)。本次事件裡舊設備是被**刪除**的(DSC-18),資料列與 `seen_ip` 一起消失(store.py:453-459),①不會觸發。提案 7 節已承認這個缺口(PROPOSAL.md:109)。
  - 建議:範例改用替換或停用的情境,避免讀者以為事件可以靠①攔下。
- **N4. 3.0.7「主設定含 `leasefile-ro`」的檢查沒有落點。**
  - repo 中沒有 install.sh,也沒有安裝後檢查的實作,installer/steps 只有 02、03。現有的 `dnsmasq --test` 位於 03-bootp.sh:74。
  - 建議:M1 寫明這項檢查加在 03-bootp.sh:74 之後。

```yaml
- {tier: 🟢 NIT, id: N1, name: "AC-1 10 秒最壞情況可能超過", evidence: ["PROPOSAL.md:89", "app/flatness/dnsmasq.py:186-195,262-265"], severity: {score: {value: 0.6, default: 0.6, override: {by: null, at: null, reason: null}}, band: low, semantic: how_bad}, fix_economics: {difficulty: {value: 0.1, default: 0.1, override: null}, roi: {value: 6.0, default: 6.0}, resource_estimate: {value: "1h", default: "1h", override: null}}, cross_impact: {affected_modules: [spec], cascade_depth: 1, dependency_chain: "驗收"}, phase_aware: {current_phase: 0, if_not_fixed_now_breaks_at: 6, estimated_rework_cost: low}, decision_tree: {options: [{id: A, action: 不修}, {id: B, action: 改時限}], recommended_option: B, counterfactual: "偶發驗收失敗"}, dependencies: {blocks: [], blocked_by: [], manual_blocks: []}, severity_decay: {phase_when_found: 0, by_phase: {}}, po_decision: {status: no_decision, decided_at: null, decided_by: null, reason: null}}
- {tier: 🟢 NIT, id: N2, name: "--test 只驗語法", evidence: ["PROPOSAL.md:45"], severity: {score: {value: 0.3, default: 0.3, override: {by: null, at: null, reason: null}}, band: low, semantic: how_bad}, fix_economics: {difficulty: {value: 0.1, default: 0.1, override: null}, roi: {value: 3.0, default: 3.0}, resource_estimate: {value: "1h", default: "1h", override: null}}, cross_impact: {affected_modules: [proposal], cascade_depth: 1, dependency_chain: "文字"}, phase_aware: {current_phase: 0, if_not_fixed_now_breaks_at: 6, estimated_rework_cost: low}, decision_tree: {options: [{id: A, action: 不修}, {id: B, action: 改寫}], recommended_option: B, counterfactual: "無實質影響"}, dependencies: {blocks: [], blocked_by: [], manual_blocks: []}, severity_decay: {phase_when_found: 0, by_phase: {}}, po_decision: {status: no_decision, decided_at: null, decided_by: null, reason: null}}
- {tier: 🟢 NIT, id: N3, name: "DSC-22 範例暗示能攔下本次事件", evidence: ["PROPOSAL.md:56", "規格書:1004", "app/flatness/store.py:453-459"], severity: {score: {value: 0.5, default: 0.5, override: {by: null, at: null, reason: null}}, band: low, semantic: how_bad}, fix_economics: {difficulty: {value: 0.1, default: 0.1, override: null}, roi: {value: 5.0, default: 5.0}, resource_estimate: {value: "1h", default: "1h", override: null}}, cross_impact: {affected_modules: [spec], cascade_depth: 1, dependency_chain: "範例"}, phase_aware: {current_phase: 0, if_not_fixed_now_breaks_at: 6, estimated_rework_cost: low}, decision_tree: {options: [{id: A, action: 不修}, {id: B, action: 改範例}], recommended_option: B, counterfactual: "讀者高估 ① 的涵蓋範圍"}, dependencies: {blocks: [], blocked_by: [], manual_blocks: []}, severity_decay: {phase_when_found: 0, by_phase: {}}, po_decision: {status: no_decision, decided_at: null, decided_by: null, reason: null}}
- {tier: 🟢 NIT, id: N4, name: "3.0.7 leasefile-ro 檢查沒有落點", evidence: ["installer/steps/03-bootp.sh:74", "規格書:309"], severity: {score: {value: 0.6, default: 0.6, override: {by: null, at: null, reason: null}}, band: low, semantic: how_bad}, fix_economics: {difficulty: {value: 0.1, default: 0.1, override: null}, roi: {value: 6.0, default: 6.0}, resource_estimate: {value: "1h", default: "1h", override: null}}, cross_impact: {affected_modules: [installer], cascade_depth: 1, dependency_chain: "安裝後檢查"}, phase_aware: {current_phase: 0, if_not_fixed_now_breaks_at: 1, estimated_rework_cost: low}, decision_tree: {options: [{id: A, action: 不修}, {id: B, action: 指定位置}], recommended_option: B, counterfactual: "M1 漏做檢查"}, dependencies: {blocks: [], blocked_by: [], manual_blocks: []}, severity_decay: {phase_when_found: 0, by_phase: {}}, po_decision: {status: no_decision, decided_at: null, decided_by: null, reason: null}}
```

### ✅ STRENGTHS

- **S1. DSC-21 的核心機制經程式碼驗證成立。** 所有會改變主機對應的路徑最後都進入 `backend.apply → sync.apply`(backend.py:149-155):儲存(settings_dialog.py:2000)、DSC-18 刪除(1717)、替換與匯入/還原(經 `_go_confirm → _commit`)、上移下移(1753)、校準(1425)。主機對應文字有變更就重新啟動(sync.py:154、164-165)。重新啟動是真的結束程序再啟動新程序(dnsmasq.py:181-190、252-275),不是 SIGHUP,所以記憶體中的租約會被清除。同一次儲存中兩台對調 IP 也會改變主機對應,一樣會觸發重新啟動。日誌也印證:09:40:23、09:40:29、10:20:35 每次都是「exiting on receipt of SIGTERM」,接著新的 pid。dnsmasq 2.90 的 BOOTP 流程沒有 ping 檢查,所以 `leasefile-ro` 加上重新啟動就足以消除舊租約。
- **S2. 改動面極小,不增加權限。** 不改 `COMMAND`/`DNSMASQ_CMD`(dnsmasq.py:27-28;03-bootp.sh:12),sudoers 不變,App 也不寫租約檔。主設定與租約檔都是 644,App 讀得到(live `ls -la` 已確認),所以 DSC-22 ② 的讀取可行。
- **S3. DSC-22 採「警告、不阻擋」**,與 DSC-10 的理念一致。第 7 節誠實列出刪除後無法依 `seen_ip` 告警的缺口。
- **S4. 第 1.1 節的四點根因中,1～3 點經 live 檔案確認**:主機對應與租約檔是兩份資料;租約是永久的(`infinite`);租約檔由 root 擁有。

## § 3. Critical Hotspots

| Hotspot | 等級 | 早解成本 | 晚解成本 | ratio |
|---|:---:|---|---|---|
| B1 安裝包升級路徑沒有重新啟動執行中的 dnsmasq | 🔥🔥(cost 5.6,cascade 3) | 2h(改 03-bootp.sh 與文件) | 現場重演事件,加上一次 sudo 介入,再加修文件、重發安裝包,約 1d | ~4× |
| B2 日誌原因分類(`address in use` 與 `no address available`) | 🔥(cost 4.8,cascade 3) | 4h(改文件、字串、測試替身) | M2 解析器、訊息與測試全部返工,約 1.5d | ~3× |

## § 4. Effective Cost Matrix

| ID | Tier | Impact | Prob | Effective cost | Fix 成本 |
|---|:---:|:---:|:---:|:---:|:---:|
| B1 | 🔴 | 7 | 0.8 | 5.6 | 2h |
| B2 | 🔴 | 6 | 0.8 | 4.8 | 4h |
| C2 | 🟡 | 4 | 0.75 | 3.0 | 1h |
| C3 | 🟡 | 4 | 0.7 | 2.8 | 1h |
| C1 | 🟡 | 5 | 0.5 | 2.5 | 1h |
| C4 | 🟡 | 3 | 0.8 | 2.4 | 1h |
| C6 | 🟡 | 4 | 0.6 | 2.4 | 1h |
| C5 | 🟡 | 5 | 0.3 | 1.5 | 1h |
| N1-N4 | 🟢 | — | — | 0.3-0.6 | 各 <1h |
| **合計** | | | | **≈27.0** | **≈13h** |

Saving:現在修約 13h(多為文件修改,加上安裝包約 10 行)。若 B1、B2 在 M2 至 M5 之後才發現,估計返工 2.5d,外加一次現場事件。

## § 5. Decision Log

- 本輪新拍板:無(Round 1,全部 `no_decision`)。
- 依據紀錄(非決定):事件時間線以 mosa `.dev/flatness.log` 2026-11-02 09:40:25-10:42:20 為準,取代提案第 1 節的敘述(B2)。
- Carry forward:無前輪。

## § 6. Verdict + Next Round Focus

- **Status:** fix-blockers
- **Recommend:**
  - `leasefile-ro` 的方向正確,機制經程式碼驗證(S1)。
  - 落地前須補兩點:①安裝包改主設定後要讓 App 的 dnsmasq 重新啟動(B1);②依實際日誌修正事件根因,並把 `no address available` 從「佔用」中分離出來,同時處理未儲存就按探頭偵測的陷阱(B2)。
  - C1～C6 多為一兩句規則或驗收文字,建議與 B 項同一輪修訂。
- **Next Round Focus:**
  1. B1 修正後,03-bootp.sh 呼叫停止程式與 App 自動重新啟動的互動:旗標「BOOTP 服務停止」的顯示、日誌層級。
  2. B2 新增「未儲存提示」條目的 G/A 與驗收。
  3. C1 的優先序是否與 POS-05「每個方塊」的規則一致。
  4. 修訂清單(C4)是否與規格書各條括號一致。

## § 7. Mental Lens Reflection(給 PO 的思考訓練)

> 觸發條件:重大 BLOCKER(impact ≥ 7 且 prob ≥ 0.5)本輪只有 B1 一個。B2 的 impact 為 6,未達門檻。依規則本段**不強制**,以下僅一句備忘。

- **批判思考應用:** 同一作者同一天寫的提案與規格書,會共享同一份事件記憶。這次只有回到原始日誌(545 對 304 行)才發現,一半的事件其實不是租約問題。下次的事件型提案,建議時間線一律附上日誌行號。
