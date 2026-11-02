---
target: docs/pm/bootp-lease/PROPOSAL.md（＋ Downloads/表面平整檢查系統_需求規格書.md DSC-21～DSC-23 與 G/A）
target_rev: 1430b54
date: 2026-11-02
reviewer: spectra-review (v2.0)
iteration: 2
verdict: ship-as-is
schema_version: enhanced-v1
contract_version: spectra-contract-v1
mode: pm-skill-generic-doc
---

> 💡 spectra-review v2.0 active(Minerva 4 能力 framework)。若想用原版簡潔版,用 `/spectra-review --lite <target>`。

🎯 Mode: PM Skill — Generic doc (target: docs/pm/bootp-lease/PROPOSAL.md)

# Spectra-Review Round 2 — docs/pm/bootp-lease/PROPOSAL.md（rev 2）

本輪範圍與限制:
- 對照來源:規格書 DSC-21～23(997-999)、說明與 G/A(1001-1009);鄰近條文 INS-04(142)、3.0.4 步驟 3(200)、3.0.7(303-316)、3.0.8(318-328)、DSC-06(848)、DSC-07(849)、DSC-08(850)、DSC-10(852)、DSC-11(853)、DSC-14(856)、DSC-15(857)、DSC-19(965)、DSC-20(985-993)、POS-05(1133)、PDT-01(1166)、索引表(1265、1281)、修訂附註(1030-1041)。
- 程式碼:installer/steps/03-bootp.sh、installer/setup-bootp.sh、installer/lib/common.sh、app/flatness/{dnsmasq,backend,discovery,arpwatch,lan,sync,store}.py、ui/main_window.py、ui/settings_dialog.py、scripts/fake-dnsmasq.py、tests/test_discovery.py。
- 現場證據:/etc/flatness/dnsmasq.conf(live,仍無 `leasefile-ro`)、/var/lib/misc/dnsmasq.leases(root 644,`0 74:95:a7:15:9b:82 192.168.10.11 row-1 *`)、/var/lib/flatness/bootp/dl-en1.hosts、`.dev/flatness.log`(2869 行)、`/usr/sbin/dnsmasq` 2.90。本機沒有 `strings`,改以 Python 抽取二進位中的可列印字串。複製主設定並加入 `leasefile-ro` 後執行 `dnsmasq --test`,結果 `syntax check OK`。
- SKILL 提到但本 repo 沒有的檔案(docs/CONTEXT.md、docs/index.md、pm-skill-proposal.md、references/*.md、state.md、decision-log.md)略過。
- 依呼叫者指示,本輪只寫 F1,不寫 F2 與 decision-log。

## § 1. Mental Lens

- **Claim → Evidence → Verdict**:rev 2 聲稱修掉的 12 項逐一回到程式碼與日誌驗證(§ 5)。新加入的機制(安裝包呼叫停止程式、租約檔改名、DSC-22 ② 啟動時間條件、DSC-23 判定表、PDT-01 提示條件)逐條追到實作層。
- **Cross-section consistency**:提案 3.1 第 3、4 點 ↔ 3.2 ② 的條件;3.3 主畫面表 ↔ POS-05「互不取代」;提案第 4 節修訂表 ↔ 規格書各條「修訂」括號。
- **Anti-Bias**:rev 2 是依第 1 輪建議修的。第 1 輪的 B1 建議(停止程式、`/proc` 啟動時間)本身就是本輪審查的對象。C1、C2 的根源正是第 1 輪建議寫得不夠完整,本輪不因「是自己建議的」而放過。
- **Understand-not-argue**:rev 2 的方向都對。本輪的 finding 集中在這些機制寫成文字後的邊界:安裝包的執行順序、兩個機制互相抵消、「尚未儲存」的適用範圍、DHCP 行。

## § 2. 4-Tier Findings

### 🔴 BLOCKERS — 落地前必修

(none found)

C1 的 effective cost 為 3.6,落在「CONCERN 升 BLOCKER 邊界」區間。照提案字面實作,首次安裝會中止,建議與簽核同輪修正。

### 🟡 CONCERNS — 應修

#### C1. 安裝包呼叫停止程式的位置與失敗處理沒寫清楚;照字面實作,首次安裝會中止,設定錯誤時 dnsmasq 每 2 秒重啟一次

**📛 命名:** 提案 3.1 第 3 點寫「`03-bootp.sh` 在主設定寫入後執行停止程式」「App 沒在執行時,停止程式找不到程序,不影響安裝」(PROPOSAL.md:60-63)。第 4 點寫「加入 `leasefile-ro` 時把租約檔改名」(PROPOSAL.md:64)。第 7 點寫在 `--test` 之後檢查,失敗就中止(PROPOSAL.md:75)。

**📣 主張:**
- **首次安裝時停止程式還不存在。** 主設定在 03-bootp.sh:38-58 寫入,停止程式到 03-bootp.sh:84-91 才寫入。「主設定寫入後」立刻呼叫,新機器上會得到 `command not found`(結束碼 127)。
- **App 沒在執行時 `pkill` 回傳 1。** 停止程式是 `exec /usr/bin/pkill -TERM -x -f …`(03-bootp.sh:87),找不到程序時結束碼為 1。setup-bootp.sh:11 設了 `set -euo pipefail`,所以安裝會在主設定寫入之後、防火牆與 sudoers(03-bootp.sh:76-105)之前中止。這與「不影響安裝」相反。`mv` 遇到不存在的租約檔也會一樣中止。
- **停止早於檢查,會讓 dnsmasq 不斷重啟。** 若在 `dnsmasq --test`(03-bootp.sh:74)與新的 `leasefile-ro` 檢查之前就停止,而之後檢查失敗(`fail`),App 會以有問題的主設定一直重啟:`_read` 判定異常結束 → `_schedule_retry` 等 2 秒 → `_spawn`。這條路沒有 settle 檢查,也沒有退避(dnsmasq.py:232-250)。結果是每 2 秒一筆 ERROR,而且畫面一直顯示「BOOTP 服務停止」。
- **sudoers 寫入晚於停止。** sudoers 在 03-bootp.sh:99-104 寫入。日後 `DNSMASQ_CMD` 若有變更,先停止的話,App 的重啟會因為 `sudo -n` 被拒而失敗,直到 sudoers 寫完。
- Impact 6/10 / Probability 0.6。每一條新產線的首次安裝都會走到這裡。mosa 的 M6 真機測試已經有停止程式,App 也在執行,所以測不出這個問題。
- Evidence:PROPOSAL.md:60-64、75;installer/steps/03-bootp.sh:38-58、74、84-91、99-104;installer/setup-bootp.sh:11;app/flatness/dnsmasq.py:232-250

**🎯 追求:** 3.1 第 3、4 點改寫為:
1. 主設定寫入時記下 `conf_changed=1`;
2. 租約檔改名以 `[[ -f /var/lib/misc/dnsmasq.leases ]]` 先確認存在;
3. 在 `step_bootp` **最後**(`--test`、`leasefile-ro` 檢查、停止程式與 sudoers 都寫完之後)執行 `[[ $conf_changed ]] && { "$STOP_HELPER" || true; }`,並寫入安裝日誌;
4. 3.0.8 那一列一併註明「最後一步才執行」。

| Option | 動作 | 成本 |
|---|---|---|
| A | 不修 | 新機首次安裝中止,要重跑一次(重跑時主設定未變更,不會再呼叫停止程式) |
| B | 現在補 4 句 | 0.5h |

推薦 B。

```yaml
- tier: 🟡 CONCERN
  id: C1
  name: "停止程式的位置與失敗處理未定:首次安裝中止、設定錯誤時重啟迴圈"
  evidence: ["PROPOSAL.md:60-64", "PROPOSAL.md:75", "installer/steps/03-bootp.sh:38-58,74,84-91,99-104", "installer/setup-bootp.sh:11", "app/flatness/dnsmasq.py:232-250"]
  severity: {score: {value: 3.6, default: 3.6, override: {by: null, at: null, reason: null}}, band: med, semantic: how_bad}
  fix_economics: {difficulty: {value: 0.5, default: 0.5, override: null}, roi: {value: 7.2, default: 7.2}, resource_estimate: {value: "1h", default: "1h", override: null}}
  cross_impact: {affected_modules: [installer, dnsmasq-runtime, main_window(BOOTP 服務停止)], cascade_depth: 3, dependency_chain: "停止時機 → App 重啟用到的主設定/sudoers → BOOTP 可用性"}
  phase_aware: {current_phase: 0, if_not_fixed_now_breaks_at: 1, estimated_rework_cost: low}
  decision_tree: {options: [{id: A, action: 不修, cost: "首次安裝中止"}, {id: B, action: 現在補順序與 || true, cost: 0.5h}], recommended_option: B, counterfactual: "新產線首次安裝於步驟 3 中止,sudoers 未寫入,App 無法啟動 dnsmasq"}
  dependencies: {blocks: [], blocked_by: [], manual_blocks: []}
  severity_decay: {phase_when_found: 0, by_phase: {1: {value: 3.6, default: 3.6, override: null}, 6: {value: 5.0, default: 5.0, override: null}}}
  po_decision: {status: no_decision, decided_at: null, decided_by: null, reason: null}
```

#### C2. DSC-22 ② 的第二個條件與租約檔改名互相抵消;條件成立時,要讀的檔案已經不在

**📛 命名:** ② 的觸發條件有兩個:「主設定沒有 `leasefile-ro`」,或「執行中的 dnsmasq 啟動時間早於主設定的修改時間」。成立時讀 `/var/lib/misc/dnsmasq.leases`(PROPOSAL.md:92-97;規格書:998)。

**📣 主張:**
- 第二個條件只在「安裝包已寫入新主設定,但 dnsmasq 還沒重啟」時成立。依 rev 2 的設計,同一次安裝也已經把租約檔改名(PROPOSAL.md:64),App 讀原路徑會讀不到,所以不會發出警告。執行中的 dnsmasq 這時記憶體裡仍有舊租約,BOOTP 照樣拒絕。這正是第 1 輪 B1 要防的「畫面說沒問題」情況。
- 有了 C1 的停止程式,這段期間只剩約 2 秒;只有停止程式失敗時才會更久。所以這個條件不是失效,就是根本用不到。
- 「啟動時間取自 `/proc/<pid>/stat`」:App 手上的 pid 是 sudo 的,不是 dnsmasq 的(dnsmasq.py:207、218)。日誌裡 `已啟動 pid=3521` 對應的是 `dnsmasq[3523]`,其他次也一樣(1701/1706、6638/6643)。要用 sudo 的啟動時間近似可以,但文件不該說是「dnsmasq 的」。另外 starttime 換成實際時間要用 btime,精度只到 1 秒。
- Impact 3/10 / Probability 0.9(條件成立時必定讀不到)。
- Evidence:PROPOSAL.md:64、92-97;規格書:998;app/flatness/dnsmasq.py:207、218;`.dev/flatness.log`:4、1788

**🎯 追求:** 兩個做法請 PO 選一個:
- (a) 刪掉第二個條件,讓 C1 的停止程式負責讓新設定生效。
- (b) 第二個條件改成獨立的提示:「dnsmasq 尚未以新設定重新啟動」,並改讀 `dnsmasq.leases.flatness-old`。啟動時間改由 `DnsmasqService._spawn` 記錄 `time.time()`,不必讀 `/proc`。

推薦 (a)。dnsmasq.py 的影響範圍那一列也一併刪除(PROPOSAL.md:171)。

```yaml
- tier: 🟡 CONCERN
  id: C2
  name: "DSC-22② 第二條件與租約檔改名互相抵消"
  evidence: ["PROPOSAL.md:64", "PROPOSAL.md:92-97", "規格書:998", "app/flatness/dnsmasq.py:207,218", ".dev/flatness.log:1788"]
  severity: {score: {value: 2.7, default: 2.7, override: {by: null, at: null, reason: null}}, band: low, semantic: how_bad}
  fix_economics: {difficulty: {value: 0.3, default: 0.3, override: null}, roi: {value: 9.0, default: 9.0}, resource_estimate: {value: "1h", default: "1h", override: null}}
  cross_impact: {affected_modules: [lan(DSC-22②), dnsmasq.py, installer], cascade_depth: 2, dependency_chain: "改名 → ② 讀不到 → 不警告"}
  phase_aware: {current_phase: 0, if_not_fixed_now_breaks_at: 4, estimated_rework_cost: low}
  decision_tree: {options: [{id: A, action: 不修, cost: "實作一段永遠不會觸發的程式"}, {id: B, action: 刪除第二條件, cost: 0.3h}, {id: C, action: 改為獨立提示並讀 .flatness-old, cost: 2h}], recommended_option: B, counterfactual: "M4 實作 /proc 讀取與比對,測試只能用人造檔案,現場永遠不觸發"}
  dependencies: {blocks: [], blocked_by: [C1], manual_blocks: []}
  severity_decay: {phase_when_found: 0, by_phase: {}}
  po_decision: {status: no_decision, decided_at: null, decided_by: null, reason: null}
```

#### C3. 主畫面「未配發」的文字仍寫「設定尚未儲存」,但主畫面上的設備一定已經儲存

**📛 命名:** 判定表把 `no address available` 解讀為「設定尚未儲存,或 IP 不在設備網段」(PROPOSAL.md:110),主畫面提示用同一句(PROPOSAL.md:125;規格書:999)。

**📣 主張:**
- 主畫面只顯示**已儲存**的使用中與維修中設備(lan.py:133-134;backend.py:40、153)。定義檔與主機對應由同一次產生、同一次寫入(sync.py:125-126、162-163),所以已儲存的使用中或維修中設備一定在主機對應裡。資料庫斷線時,兩份都沿用舊檔(sync.py:115-118),彼此仍然一致。
- 因此主畫面上這台出現 `no address available`,原因不可能是「尚未儲存」。實際可能的情況:
  - **主機對應的 IP 不在 dnsmasq 的配發網段。** dhcp-range 來自 site.conf(03-bootp.sh:22-25、47);App 驗證用的是設備網卡的網段(backend.py:60-67)。以 DSC-11 為例:改網段並重裝後,App 啟動時因 IP 不在網段而不改寫主機對應(sync.py:119-124),舊 IP 全部落在新的 dhcp-range 之外,每一台都會收到 `no address available`。
  - **主機對應被手動修改或沒有更新。**
- 第 1 輪事件中「尚未儲存」的 39 分鐘,plat1 是「不明設備」,根本不在主畫面上。那一段只有設定頁的 PDT-01 提示能處理,rev 2 也已經加了這個提示。
- Impact 5/10 / Probability 0.3。這是第 1 輪 B2「原因寫錯」的殘留,方向反過來了。
- Evidence:PROPOSAL.md:110、125;規格書:999;app/flatness/lan.py:133-134;app/flatness/sync.py:115-126、162-163;installer/steps/03-bootp.sh:47

**🎯 追求:**
- 主畫面「未配發」改為:「第 N 台 名稱 拿不到 IP:BOOTP 沒有配發(主機對應的 IP 不在 dnsmasq 配發網段,或主機對應未更新),請洽維護人員」。
- 判定表的「意思」欄改為「dnsmasq 載入的主機對應沒有這台的可用 IP」。
- 「設定尚未儲存」只留在設定頁(PDT-01)。

```yaml
- tier: 🟡 CONCERN
  id: C3
  name: "主畫面「未配發」文字含不可能成立的「設定尚未儲存」"
  evidence: ["PROPOSAL.md:110", "PROPOSAL.md:125", "規格書:999", "app/flatness/lan.py:133-134", "app/flatness/sync.py:115-126,162-163"]
  severity: {score: {value: 1.5, default: 1.5, override: {by: null, at: null, reason: null}}, band: low, semantic: how_bad}
  fix_economics: {difficulty: {value: 0.2, default: 0.2, override: null}, roi: {value: 7.5, default: 7.5}, resource_estimate: {value: "1h", default: "1h", override: null}}
  cross_impact: {affected_modules: [main_window, spec DSC-23, 操作說明書], cascade_depth: 2, dependency_chain: "訊息文字 → 現場處理方向"}
  phase_aware: {current_phase: 0, if_not_fixed_now_breaks_at: 3, estimated_rework_cost: low}
  decision_tree: {options: [{id: A, action: 不修, cost: "DSC-11 改網段時整排顯示「尚未儲存」"}, {id: B, action: 改文字, cost: 0.2h}], recommended_option: B, counterfactual: "改網段後所有設備顯示「設定尚未儲存」,工程人員反覆按儲存無效"}
  dependencies: {blocks: [], blocked_by: [], manual_blocks: []}
  severity_decay: {phase_when_found: 0, by_phase: {}}
  po_decision: {status: no_decision, decided_at: null, decided_by: null, reason: null}
```

#### C4. 判定表套用到 DHCP 行時不成立:佔用會被判為「未配發」,DHCPREQUEST 與 DHCPNAK 行會被判為「恢復」

**📛 命名:** rev 2 把範圍從「BOOTP 請求」擴大為「BOOTP／DHCP 請求行」(PROPOSAL.md:105;規格書:999)。成功的判定是「有 IP,行尾沒有上述字串」(PROPOSAL.md:112)。

**📣 主張:**依 dnsmasq 2.90 的 DHCP 流程(二進位字串已確認),有三個問題:
- **佔用會被判為「未配發」。** 主機對應的 IP 被別的 MAC 租用時,DHCPDISCOVER 不記 `address in use`。dnsmasq 先另記一行 `not using configured address %s because it is leased to %s`(這行沒有請求者的 MAC),接著在 static range 下配不出位址,記 `DHCPDISCOVER(eno2) <mac> no address available`。依表格會歸為「未配發」。
- **DHCPREQUEST 行一律會被判為「恢復」。** DHCPREQUEST 行一定帶著請求的 IP、行尾沒有拒絕字串,所以每一行都符合「已配發」。拒絕的結果記在之後的 DHCPNAK 行。
- **DHCPNAK 行也會被判為「恢復」。** DHCPNAK 的原因字串 `address not available`、`wrong address`、`lease not found`、`wrong server-ID`、`static lease available`、`address reserved` 都不在表內,而這種行帶有 IP。注意 `address not available` 和 `no address available` 是不同的字串。
- DSC-23 只處理 DL-EN1(使用中、維修中),DL-EN1 只送 BOOTP。事件當日日誌中 DHCP 行為 0 筆。
- scripts/fake-dnsmasq.py:52-63 本身就會產生 DHCPREQUEST 與 DHCPACK 行,所以 M2 的測試很容易把錯的規則測成綠燈。
- Impact 4/10 / Probability 0.3
- Evidence:PROPOSAL.md:105-112;規格書:999;app/flatness/discovery.py:28-32;scripts/fake-dnsmasq.py:52-63;`/usr/sbin/dnsmasq` 字串(`not using configured address %s because it is leased to %s`、`address not available`、`wrong address`、`lease not found` 等);`.dev/flatness.log`(`DHCP[A-Z]*(` 0 筆)

**🎯 追求:**
- DSC-23 限定只看 **BOOTP** 行,在 DSC-23 與提案第 7 節註明「DHCP 不納入」。
- 若 PO 要涵蓋 DHCP,判定表要另寫:成功只認 DHCPACK;DHCPNAK 視為拒絕;佔用要對上 `leased to` 那一行。

```yaml
- tier: 🟡 CONCERN
  id: C4
  name: "判定表套用到 DHCP 行時,佔用被判未配發、REQUEST/NAK 被判恢復"
  evidence: ["PROPOSAL.md:105-112", "規格書:999", "scripts/fake-dnsmasq.py:52-63", "/usr/sbin/dnsmasq strings", ".dev/flatness.log"]
  severity: {score: {value: 1.2, default: 1.2, override: {by: null, at: null, reason: null}}, band: low, semantic: how_bad}
  fix_economics: {difficulty: {value: 0.1, default: 0.1, override: null}, roi: {value: 12.0, default: 12.0}, resource_estimate: {value: "1h", default: "1h", override: null}}
  cross_impact: {affected_modules: [discovery, backend, tests, fake-dnsmasq], cascade_depth: 2, dependency_chain: "判定規則 → 狀態 → 主畫面"}
  phase_aware: {current_phase: 0, if_not_fixed_now_breaks_at: 2, estimated_rework_cost: low}
  decision_tree: {options: [{id: A, action: 不修, cost: "M2 寫出錯誤的 DHCP 規則"}, {id: B, action: 限定 BOOTP, cost: 0.1h}, {id: C, action: 補完整 DHCP 規則, cost: 3h}], recommended_option: B, counterfactual: "日後有 DL-EN1 或其他設備走 DHCP 時提示忽隱忽現"}
  dependencies: {blocks: [], blocked_by: [], manual_blocks: []}
  severity_decay: {phase_when_found: 0, by_phase: {}}
  po_decision: {status: no_decision, decided_at: null, decided_by: null, reason: null}
```

#### C5. PDT-01 提示的條件「狀態或 IP 尚未儲存」不精確:有時會說錯「BOOTP 還沒有配發」,改 IP 的情況又漏了按 RST

**📛 命名:** 探頭偵測失敗時,「這台的狀態或 IP 尚未儲存」就提示「設定尚未儲存,BOOTP 還沒有配發 <IP>;請先儲存」(PROPOSAL.md:133-135、186;規格書:999;G1 1006「儲存後再偵測成功」)。

**📣 主張:**
- **(a) 狀態改了,不代表 BOOTP 還沒配發。** 維修中或「設有 IP 的其他設備」改成使用中,但 IP 沒改時,主機對應早就配發這個 IP(lan.py:84-86、205-218;DSC-15 規定維修中保留配發)。這時偵測失敗(例如設備沒上電)卻提示「BOOTP 還沒有配發」,說的不是事實。
- **(b) 已有 IP 的設備改 IP,只儲存還不夠。** 已在使用的設備改成新 IP 但尚未儲存時,提示「請先儲存」。可是儲存後 DL-EN1 仍記得舊 IP,要按 RST 才會重新要 IP(PROPOSAL.md:69;DSC-20)。照提示操作,再偵測仍會失敗,DSC-23-G1 的「儲存後再偵測成功」不成立。
- **條件可以做得精確。** 設定頁已保存儲存前的版本 `self.original`(settings_dialog.py:637、2007)。
- Impact 4/10 / Probability 0.5。改 IP 是常見操作。
- Evidence:PROPOSAL.md:69、133-135、186;規格書:999、1006;app/flatness/lan.py:84-86、205-218;app/flatness/ui/settings_dialog.py:637、1576-1603

**🎯 追求:**
- 提示條件改為「已儲存的版本(`self.original`)不會把此 MAC 配發為此 IP」,也就是 `not orig.assigns_ip or orig.ipv4 != work.ipv4`。
- 若這台原本已有 IP(`orig.ipv4` 有值,或 `seen_ip` 不等於新 IP),提示再加一句「儲存後按住 DL-EN1 的 RST 鍵 3 秒,使其重新取得 IP」。
- AC-6 補一個「改 IP」案例。

```yaml
- tier: 🟡 CONCERN
  id: C5
  name: "PDT-01「尚未儲存」條件不精確,改 IP 漏 RST"
  evidence: ["PROPOSAL.md:133-135", "PROPOSAL.md:186", "規格書:1006", "app/flatness/lan.py:84-86", "app/flatness/ui/settings_dialog.py:637"]
  severity: {score: {value: 2.0, default: 2.0, override: {by: null, at: null, reason: null}}, band: low, semantic: how_bad}
  fix_economics: {difficulty: {value: 0.3, default: 0.3, override: null}, roi: {value: 6.7, default: 6.7}, resource_estimate: {value: "1h", default: "1h", override: null}}
  cross_impact: {affected_modules: [settings_dialog, spec PDT-01/DSC-23, 操作說明書], cascade_depth: 2, dependency_chain: "提示條件 → 現場操作順序"}
  phase_aware: {current_phase: 0, if_not_fixed_now_breaks_at: 3, estimated_rework_cost: low}
  decision_tree: {options: [{id: A, action: 不修, cost: "改 IP 時照提示儲存後仍失敗"}, {id: B, action: 改條件並加 RST 句, cost: 0.3h}], recommended_option: B, counterfactual: "工程人員改 IP、儲存、偵測仍失敗,回到事件當天的困惑"}
  dependencies: {blocks: [], blocked_by: [], manual_blocks: []}
  severity_decay: {phase_when_found: 0, by_phase: {}}
  po_decision: {status: no_decision, decided_at: null, decided_by: null, reason: null}
```

#### C6. 與 POS-05「各種狀態的頂端提示各自顯示、互不取代」衝突,POS-05 卻不在修訂表;同一台會同時出現「偵測不到」與「拿不到 IP」兩條頂端提示

**📛 命名:** rev 2 規定:方塊「拿不到 IP」取代「偵測不到」;新增一類頂端提示;被拒期間暫停「IP 不符」(PROPOSAL.md:120-129)。修訂表列了 DSC-15、DSC-20、PDT-01(PROPOSAL.md:150-159)。

**📣 主張:**
- **與 POS-05 衝突,但 POS-05 沒列入修訂。** POS-05(規格書:1133,已簽核)規定方塊上的整台狀態有三種(偵測不到或設備異常、維修中、IP 不符),而且「各種狀態的頂端提示各自顯示、互不取代」。DSC-23 新增第四種方塊狀態,又讓它取代偵測不到、暫停 IP 不符,直接改變了 POS-05。
- **同一台會出現兩條頂端提示。** 現行程式中,連不上的設備會同時進入兩個地方:「dev」頂端提示「第 N 台 偵測不到」,以及異常橫幅「DL-EN1 偵測不到」(main_window.py:1305-1311、1342)。照 POS-05 的「互不取代」,新類型的提示會跟「dev」並列。結果同一台同時顯示「偵測不到」與「拿不到 IP」。第 1 輪 C1 的頂端提示部分只修了一半。
- **維修中被拒時的顏色與 DSC-15 不一致。** 維修中被拒的頂端提示寫「同上,顏色同設備異常」,也就是紅色(ng)。可是現行「維修中」頂端提示用中性色(main_window.py:1070-1073),DSC-15 也規定維修中不阻擋作業。
- Impact 4/10 / Probability 0.7
- Evidence:PROPOSAL.md:120-129、150-159;規格書:857、1133;app/flatness/ui/main_window.py:1070-1073、1305-1311、1342

**🎯 追求:**
- 修訂表加入 POS-05。
- DSC-23 補一句:「被拒期間,該台在『dev』頂端提示與異常橫幅中以『拿不到 IP(原因)』取代『偵測不到』,不另外多一條。」也可以改成由新類型取代該台在「dev」中的那一項。
- 維修中被拒的頂端提示改用「maint」的顏色。

```yaml
- tier: 🟡 CONCERN
  id: C6
  name: "與 POS-05 互不取代衝突;dev 提示/橫幅與新提示重複"
  evidence: ["PROPOSAL.md:120-129", "PROPOSAL.md:150-159", "規格書:1133", "app/flatness/ui/main_window.py:1070-1073,1305-1311,1342"]
  severity: {score: {value: 2.8, default: 2.8, override: {by: null, at: null, reason: null}}, band: low, semantic: how_bad}
  fix_economics: {difficulty: {value: 0.3, default: 0.3, override: null}, roi: {value: 9.3, default: 9.3}, resource_estimate: {value: "1h", default: "1h", override: null}}
  cross_impact: {affected_modules: [main_window, spec POS-05/DSC-15/DSC-23], cascade_depth: 2, dependency_chain: "顯示優先序 → 頂端提示列 → 現場判讀"}
  phase_aware: {current_phase: 0, if_not_fixed_now_breaks_at: 3, estimated_rework_cost: low}
  decision_tree: {options: [{id: A, action: 不修, cost: "同台兩條矛盾提示;POS-05 與 DSC-23 文字衝突"}, {id: B, action: 修訂表加 POS-05 並補取代規則, cost: 0.3h}], recommended_option: B, counterfactual: "頂端同時顯示「第 1 台 偵測不到」與「第 1 台 拿不到 IP」"}
  dependencies: {blocks: [], blocked_by: [], manual_blocks: []}
  severity_decay: {phase_when_found: 0, by_phase: {}}
  po_decision: {status: no_decision, decided_at: null, decided_by: null, reason: null}
```

#### C7. 被拒狀態沒有逾時;設備拔除或改由其他方式連上後,「拿不到 IP」會一直顯示

**📛 命名:** 提示消失的條件只有兩個:BOOTP 配發成功,或最近一次被拒之後收到的 ARP 顯示設定的 IP(PROPOSAL.md:112-114)。狀態只在 App 重新啟動時歸零(PROPOSAL.md:118)。

**📣 主張:**
- **設備拔除後提示不會消失。** 處理拿不到 IP 時,把設備拔下、斷電是常見的動作。之後既沒有配發也沒有 ARP,主畫面就一直顯示「拿不到 IP:<IP> 被其他設備佔用,請洽維護人員」。實際上這台已經不在,應該顯示「偵測不到」。
- **主畫面已連上也不算恢復。** ARP 監聽重啟期間有 30 秒空窗(backend.py:51-53),期間可能看不到 ARP。這時就算主畫面已連上設備,提示也不會消失。
- **ARP 恢復可能延遲。** ARP 事件要先寫入資料庫,才經 `devices_seen` 送到畫面(backend.py:94-104;discovery.py:126-145)。資料庫斷線時,依 ARP 判定恢復會延遲到資料庫恢復。
- 依日誌,DL-EN1 被拒時每 3~5 秒重送一次(PROPOSAL.md:20;日誌 545 行 / 39 分),逾時門檻很好訂。
- Impact 4/10 / Probability 0.5
- Evidence:PROPOSAL.md:112-118;規格書:999;app/flatness/backend.py:51-53、94-104;app/flatness/discovery.py:126-145

**🎯 追求:**
- 新增恢復條件:最近一次被拒後 60 秒內沒有再被拒,就清除狀態;主畫面量測連線成功也視為恢復。
- ARP 恢復直接在 `Backend._on_arp_line` 判定,不等資料庫寫入。
- 驗收新增一條:「被拒中拔除設備 → 60 秒內改回『偵測不到』」。

```yaml
- tier: 🟡 CONCERN
  id: C7
  name: "被拒狀態無逾時,拔除後提示永遠留著"
  evidence: ["PROPOSAL.md:112-118", "規格書:999", "app/flatness/backend.py:51-53,94-104", "app/flatness/discovery.py:126-145"]
  severity: {score: {value: 2.0, default: 2.0, override: {by: null, at: null, reason: null}}, band: low, semantic: how_bad}
  fix_economics: {difficulty: {value: 0.3, default: 0.3, override: null}, roi: {value: 6.7, default: 6.7}, resource_estimate: {value: "1h", default: "1h", override: null}}
  cross_impact: {affected_modules: [backend, main_window, settings_dialog], cascade_depth: 2, dependency_chain: "狀態生命週期 → 顯示"}
  phase_aware: {current_phase: 0, if_not_fixed_now_breaks_at: 2, estimated_rework_cost: low}
  decision_tree: {options: [{id: A, action: 不修, cost: "過時提示,誤導處理"}, {id: B, action: 加逾時與連線成功恢復, cost: 0.3h}], recommended_option: B, counterfactual: "設備已拔除,畫面仍要求洽維護人員處理佔用"}
  dependencies: {blocks: [], blocked_by: [C4], manual_blocks: []}
  severity_decay: {phase_when_found: 0, by_phase: {}}
  po_decision: {status: no_decision, decided_at: null, decided_by: null, reason: null}
```

### 🟢 NITS — 可選 polish

- **N1. 安裝包觸發的重啟,日誌會記成 ERROR「異常結束」。**
  - `_read` 會記 `log.error("dnsmasq 異常結束(結束碼 …):… exiting on receipt of SIGTERM;2 秒後自動重新啟動")`(dnsmasq.py:236-237)。
  - DSC-07 列出的停止來源是「App 結束、重新啟動、清除殘留」(規格書:849),沒有安裝包。
  - 建議:3.1 第 3 點寫明會出現這行 ERROR;安裝日誌先記一筆「由安裝包停止 App 的 dnsmasq」。「DSC-07 不修訂」(PROPOSAL.md:161)要保留的話,補一句理由。
- **N2. 租約檔改名會覆蓋舊的備份。**
  - 依「新版 → 舊版 → 新版」的順序重跑安裝包時,第二次 `mv` 會覆蓋第一次的 `.flatness-old`,事件當時的證據就沒了。
  - 依 dnsmasq 原始碼(🟡,憑記憶,未在本機驗證):沒有 `leasefile-ro` 時,dnsmasq 啟動後一直開著租約檔並以 rewind/ftruncate 重寫。改名後到停止之前,改名後的檔案仍可能被改寫。
  - 建議:改名為 `.flatness-old.<YYYYmmddHHMMSS>`,或目標已存在就不覆蓋。
- **N3. 「兩者都完成前,DSC-22 ② 會提示尚未升級」言過其實(PROPOSAL.md:74)。**
  - 先跑安裝包時,舊版 App 根本沒有 DSC-22。
  - 先更新 App 時,② 只在要設定的 IP 剛好在租約檔裡時才警告。
  - 建議改為「先更新 App 時,設定的 IP 若被舊租約登記,② 會警告」。
- **N4. 3.0.7 的 `leasefile-ro` 檢查不可能失敗。**
  - 它檢查的是安裝包剛用同一段 heredoc 寫出的檔案(03-bootp.sh:38-53)。
  - 可以保留,當作防止日後改壞的保險。但行為驗證仍要靠 AC-5,不要把這項檢查當成驗證。
- **N5. DSC-22 ① 的「最後於 <時間> 使用 <IP>」用的是 `last_seen`。**
  - `last_seen` 任何請求都會更新,`seen_ip` 只由 ARP 更新(store.py:88、95、288、293),所以這個時間可能晚於設備實際使用該 IP 的時間。
  - 建議改為「最後出現 <時間>」。另外,規格書 G1 寫「10/07」,提案寫「10/07 13:51」(PROPOSAL.md:87;規格書:1005),格式不一致。
- **N6. 規格書索引表沒有納入 DSC-21~23。**
  - 規格書:1265 為「DSC-08~DSC-20」,1281 為「DSC-01~DSC-20」。
  - 建議簽核時一併改為 DSC-23。

```yaml
- {tier: 🟢 NIT, id: N1, name: "安裝包觸發重啟記為 ERROR 異常結束", evidence: ["app/flatness/dnsmasq.py:236-237", "規格書:849", "PROPOSAL.md:161"], severity: {score: {value: 0.6, default: 0.6, override: {by: null, at: null, reason: null}}, band: low, semantic: how_bad}, fix_economics: {difficulty: {value: 0.1, default: 0.1, override: null}, roi: {value: 6.0, default: 6.0}, resource_estimate: {value: "1h", default: "1h", override: null}}, cross_impact: {affected_modules: [installer, docs], cascade_depth: 1, dependency_chain: "日誌判讀"}, phase_aware: {current_phase: 0, if_not_fixed_now_breaks_at: 6, estimated_rework_cost: low}, decision_tree: {options: [{id: A, action: 不修}, {id: B, action: 文件註明並由安裝日誌先記}], recommended_option: B, counterfactual: "維護時看到 ERROR 誤判故障"}, dependencies: {blocks: [], blocked_by: [C1], manual_blocks: []}, severity_decay: {phase_when_found: 0, by_phase: {}}, po_decision: {status: no_decision, decided_at: null, decided_by: null, reason: null}}
- {tier: 🟢 NIT, id: N2, name: "租約檔改名覆蓋前次備份", evidence: ["PROPOSAL.md:64", "規格書:997"], severity: {score: {value: 0.4, default: 0.4, override: {by: null, at: null, reason: null}}, band: low, semantic: how_bad}, fix_economics: {difficulty: {value: 0.1, default: 0.1, override: null}, roi: {value: 4.0, default: 4.0}, resource_estimate: {value: "1h", default: "1h", override: null}}, cross_impact: {affected_modules: [installer], cascade_depth: 1, dependency_chain: "備查檔"}, phase_aware: {current_phase: 0, if_not_fixed_now_breaks_at: 1, estimated_rework_cost: low}, decision_tree: {options: [{id: A, action: 不修}, {id: B, action: 加時間戳}], recommended_option: B, counterfactual: "事件證據遺失"}, dependencies: {blocks: [], blocked_by: [], manual_blocks: []}, severity_decay: {phase_when_found: 0, by_phase: {}}, po_decision: {status: no_decision, decided_at: null, decided_by: null, reason: null}}
- {tier: 🟢 NIT, id: N3, name: "「DSC-22② 會提示尚未升級」言過其實", evidence: ["PROPOSAL.md:74"], severity: {score: {value: 0.4, default: 0.4, override: {by: null, at: null, reason: null}}, band: low, semantic: how_bad}, fix_economics: {difficulty: {value: 0.1, default: 0.1, override: null}, roi: {value: 4.0, default: 4.0}, resource_estimate: {value: "1h", default: "1h", override: null}}, cross_impact: {affected_modules: [proposal], cascade_depth: 1, dependency_chain: "文字"}, phase_aware: {current_phase: 0, if_not_fixed_now_breaks_at: 6, estimated_rework_cost: low}, decision_tree: {options: [{id: A, action: 不修}, {id: B, action: 改寫}], recommended_option: B, counterfactual: "升級順序判斷錯誤"}, dependencies: {blocks: [], blocked_by: [], manual_blocks: []}, severity_decay: {phase_when_found: 0, by_phase: {}}, po_decision: {status: no_decision, decided_at: null, decided_by: null, reason: null}}
- {tier: 🟢 NIT, id: N4, name: "3.0.7 leasefile-ro 檢查同義反覆", evidence: ["PROPOSAL.md:75", "installer/steps/03-bootp.sh:38-53"], severity: {score: {value: 0.2, default: 0.2, override: {by: null, at: null, reason: null}}, band: low, semantic: how_bad}, fix_economics: {difficulty: {value: 0.1, default: 0.1, override: null}, roi: {value: 2.0, default: 2.0}, resource_estimate: {value: "1h", default: "1h", override: null}}, cross_impact: {affected_modules: [installer], cascade_depth: 1, dependency_chain: "檢查"}, phase_aware: {current_phase: 0, if_not_fixed_now_breaks_at: 6, estimated_rework_cost: low}, decision_tree: {options: [{id: A, action: 不修}, {id: B, action: 註明是保險}], recommended_option: B, counterfactual: "誤以為已驗證行為"}, dependencies: {blocks: [], blocked_by: [], manual_blocks: []}, severity_decay: {phase_when_found: 0, by_phase: {}}, po_decision: {status: no_decision, decided_at: null, decided_by: null, reason: null}}
- {tier: 🟢 NIT, id: N5, name: "DSC-22① 時間用 last_seen 非使用該 IP 時間", evidence: ["PROPOSAL.md:87", "規格書:1005", "app/flatness/store.py:88,95,288,293"], severity: {score: {value: 0.4, default: 0.4, override: {by: null, at: null, reason: null}}, band: low, semantic: how_bad}, fix_economics: {difficulty: {value: 0.1, default: 0.1, override: null}, roi: {value: 4.0, default: 4.0}, resource_estimate: {value: "1h", default: "1h", override: null}}, cross_impact: {affected_modules: [settings_dialog], cascade_depth: 1, dependency_chain: "訊息"}, phase_aware: {current_phase: 0, if_not_fixed_now_breaks_at: 4, estimated_rework_cost: low}, decision_tree: {options: [{id: A, action: 不修}, {id: B, action: 改「最後出現」}], recommended_option: B, counterfactual: "時間誤導"}, dependencies: {blocks: [], blocked_by: [], manual_blocks: []}, severity_decay: {phase_when_found: 0, by_phase: {}}, po_decision: {status: no_decision, decided_at: null, decided_by: null, reason: null}}
- {tier: 🟢 NIT, id: N6, name: "索引表未納入 DSC-21~23", evidence: ["規格書:1265", "規格書:1281"], severity: {score: {value: 0.3, default: 0.3, override: {by: null, at: null, reason: null}}, band: low, semantic: how_bad}, fix_economics: {difficulty: {value: 0.1, default: 0.1, override: null}, roi: {value: 3.0, default: 3.0}, resource_estimate: {value: "1h", default: "1h", override: null}}, cross_impact: {affected_modules: [spec], cascade_depth: 1, dependency_chain: "追溯"}, phase_aware: {current_phase: 0, if_not_fixed_now_breaks_at: 5, estimated_rework_cost: low}, decision_tree: {options: [{id: A, action: 不修}, {id: B, action: 改範圍}], recommended_option: B, counterfactual: "追溯表漏列"}, dependencies: {blocks: [], blocked_by: [], manual_blocks: []}, severity_decay: {phase_when_found: 0, by_phase: {}}, po_decision: {status: no_decision, decided_at: null, decided_by: null, reason: null}}
```

### ✅ STRENGTHS

- **S1. 第 1 輪 B1 的修法建立在真實存在的機制上。**
  - 停止程式是 `pkill -x -f '<DNSMASQ_CMD>'`(03-bootp.sh:87),只會比對到 dnsmasq 本身,不會比對到 sudo(sudo 的命令列前面多了 `sudo -n`)。
  - dnsmasq 結束後 sudo 也跟著結束,`_read` 收到 EOF。這時 generation 沒變、`_wanted` 仍為 True,因此記錄異常結束、通知「BOOTP 服務停止」,2 秒後 `_spawn`(dnsmasq.py:223-250)。
  - 已有測試 `test_crash_auto_restarts` 涵蓋這條路徑(tests/test_discovery.py:114)。「約 2 秒」成立。
- **S2. 第 1 節時間線與日誌一致。**
  - `no address available` 共 545 行,09:41:44~10:20:31;`address in use` 共 304 行,10:20:36~10:42:15。
  - 主畫面每 13 秒逾時一次(10:20:40、10:20:53、10:21:06…)。
  - 恢復那一行行尾沒有字串(日誌第 2827 行)。
- **S3. 修訂清單統一。**
  - 提案第 4 節列出 8 條。規格書 DSC-21(3.0.4、3.0.7、3.0.8)、DSC-22(DSC-10、DSC-14)、DSC-23(DSC-15、DSC-20、PDT-01)的「修訂」括號,合起來剛好是這 8 條。
  - 「DSC-07 不修訂」有寫明理由。
- **S4. 驗收條件可以量測。**
  - AC-1 改為「dnsmasq 重新啟動完成後 15 秒內」;AC-7 不再依賴事件數字;AC-9 鎖住 DSC-14 與 ① 不重複。
  - 第 6 節註明 AC-3 不可用對調 IP 代替。這正好封住第 1 輪指出的「測試遮住缺陷」。

## § 3. Critical Hotspots

| Hotspot | 等級 | 早解成本 | 晚解成本 | ratio |
|---|:---:|---|---|---|
| C1 安裝包呼叫停止程式的位置與失敗處理 | 🔥(cost 3.6,cascade 3,依個案判定) | 0.5h(改 4 句文字) | 新產線首次安裝中止,加上現場排查、重發安裝包,約 0.5d | ~8× |

其他 finding 的 cost 都在 3 以下,cascade 也 ≤ 2,不列 hotspot。

## § 4. Effective Cost Matrix

| ID | Tier | Impact | Prob | Effective cost | Fix 成本 |
|---|:---:|:---:|:---:|:---:|:---:|
| C1 | 🟡 | 6 | 0.6 | 3.6 | 0.5h |
| C6 | 🟡 | 4 | 0.7 | 2.8 | 0.3h |
| C2 | 🟡 | 3 | 0.9 | 2.7 | 0.3h |
| C5 | 🟡 | 4 | 0.5 | 2.0 | 0.3h |
| C7 | 🟡 | 4 | 0.5 | 2.0 | 0.3h |
| C3 | 🟡 | 5 | 0.3 | 1.5 | 0.2h |
| C4 | 🟡 | 4 | 0.3 | 1.2 | 0.1h |
| N1-N6 | 🟢 | — | — | 0.2-0.6 | 各 <0.2h |
| **合計** | | | | **≈18.1** | **≈3h** |

與第 1 輪(≈27.0)相比,總成本下降約 33%,而且沒有 BLOCKER。Saving:現在修只要約 3 小時的文字修改;若在 M1 到 M4 實作後才修,估計返工 1~1.5 天。

## § 5. Decision Log

**第 1 輪 finding 在 rev 2 的實際狀態(已逐項驗證):**

| R1 ID | 狀態 | 驗證 |
|---|:---:|---|
| B1 安裝包沒有讓執行中的 dnsmasq 重啟 | ✅ fixed | PROPOSAL.md:60-63、70-74;規格書:997。重啟路徑實際存在(S1)。副作用見本輪 C1(順序)、C2(與改名抵消)。 |
| B2 時間線錯置、`no address available` 與佔用混為一談 | ✅ fixed(有殘留) | 時間線與日誌一致(S2)。判定表分出原因;PDT-01 提示已加入(PROPOSAL.md:133-135);驗收數字改了(AC-7);fake-dnsmasq 與 tests 列入影響範圍(PROPOSAL.md:174)。殘留:主畫面「未配發」仍寫「設定尚未儲存」(C3)。 |
| C1 顯示優先序 | 🔶 partial | IP 不符暫停、維修中方塊、頂端提示類型都補上了(PROPOSAL.md:120-129)。沒處理:與「dev」頂端提示、異常橫幅重複,以及 POS-05 衝突(C6)。 |
| C2 「App 日誌只有一筆」 | ✅ fixed | PROPOSAL.md:137-139、AC-7:187;規格書:999 |
| C3 DSC-22 ① 重複告警 | ✅ fixed | PROPOSAL.md:82-88 排除 DSC-08、替換的舊機改用 DSC-14 文字、與 DSC-10 合併;AC-9 |
| C4 修訂清單不一致 | ✅ fixed(有殘留) | 第 4 節與規格書括號一致(S3)。殘留:POS-05 漏列(C6)、索引表(N6) |
| C5 舊租約檔留在原地 | ✅ fixed(有殘留) | PROPOSAL.md:64;AC-5。殘留:改名覆蓋前次備份(N2)、與 ② 互相抵消(C2) |
| C6 判定規則不夠具體 | ✅ fixed(BOOTP)/ 殘留 | 拒絕字串、成功判定、backend 狀態與 Signal、重新啟動後歸零都已定義(PROPOSAL.md:103-118)。殘留:DHCP 行(C4)、狀態沒有逾時(C7) |
| N1 AC-1 10 秒 | ✅ fixed | AC-1 改為重新啟動完成後 15 秒內(PROPOSAL.md:181) |
| N2 `--test` 只驗語法 | ✅ fixed | PROPOSAL.md:56 |
| N3 DSC-22 範例 | ✅ fixed | 範例改為已停用的舊機 .12(PROPOSAL.md:87);第 7 節承認 ① 抓不到前沿(PROPOSAL.md:206) |
| N4 3.0.7 檢查的位置 | ✅ fixed | PROPOSAL.md:75 指定在 `--test` 之後。另見 N4(本輪):這項檢查不可能失敗 |

- 本輪新拍板:無,全部為 `no_decision`。
- 依據紀錄(非決定):dnsmasq 2.90 的 BOOTP 拒絕字串以二進位字串為準。DHCP 佔用會另記一行 `not using configured address … leased to …`,並非 `address in use`(C4)。

## § 6. Verdict + Next Round Focus

- **Status:** ship-as-is。本輪沒有 BLOCKER,設計方向不需改變。
- **Recommend:**
  - 簽核前出一版 rev 3 文字修正,處理 C1~C7,約 3 小時,都是一兩句的修改。
  - C1 最優先:照現在的字面實作,首次安裝會中止。
  - C2 建議直接刪除第二個條件。
  - C4 建議限定只看 BOOTP 行。
- **Next Round Focus(若有第 3 輪):**
  1. C1 修正後 `step_bootp` 的完整順序:寫入、改名、檢查、停止程式、sudoers、停止。
  2. C6 補上的取代規則與 POS-05 新文字是否一致。
  3. C7 的逾時數值與 AC。

(§ 7 Mental Lens Reflection:本輪沒有重大 BLOCKER,不觸發。)
