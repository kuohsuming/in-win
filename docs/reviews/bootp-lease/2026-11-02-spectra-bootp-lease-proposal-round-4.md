---
target: docs/pm/bootp-lease/PROPOSAL.md（＋ Downloads/表面平整檢查系統_需求規格書.md DSC-21～DSC-23 與 G/A）
target_rev: d91045e
date: 2026-11-02
reviewer: spectra-review (v2.0)
iteration: 4
verdict: ship-as-is
schema_version: enhanced-v1
contract_version: spectra-contract-v1
mode: pm-skill-generic-doc
---

> 💡 spectra-review v2.0 active(Minerva 4 能力 framework)。若想用原版簡潔版,用 `/spectra-review --lite <target>`。

🎯 Mode: PM Skill — Generic doc (target: docs/pm/bootp-lease/PROPOSAL.md)

# Spectra-Review Round 4 — docs/pm/bootp-lease/PROPOSAL.md（rev 4）

本輪範圍與限制:
- 變更來源:`git diff d54a0eb d91045e -- docs/pm Downloads`(提案 29 行、規格書 DSC-23 一列)。
- 對照來源:規格書 DSC-23(999)、G/A(1001-1009)、DSC-20(985-993)、POS-05(1133)、PDT-01(1166);其餘鄰近條文(DSC-07/08/10/14/15/19、3.0.4 步驟 3、3.0.8、6.2)本輪沒有變更,沿用第 3 輪的比對結果。
- 程式碼:installer/steps/03-bootp.sh(停止程式 heredoc :84-91)、installer/lib/common.sh、app/flatness/dnsmasq.py、ui/main_window.py、ui/settings_dialog.py(`_scan_probes` :1576-1606)。`pkill` 結束碼以本機 procps-ng 3.3.17 的 man page 確認。
- 畫面文件:docs/ui/screen-design-spec.md:108-111、docs/ui/screens-device-settings.md:36、40、46、102。
- SKILL 提到但本 repo 沒有的檔案:docs/CONTEXT.md、docs/index.md(略過)。依呼叫者指示只寫 F1,不寫 F2。

## § 1. Mental Lens

- **Claim → Evidence → Verdict**:rev 4 新增的主張逐條追證:「連上後 10 秒內未再被拒」、「逾時清除不記為恢復」、`seen_ip` 版 RST 條件、「正被拒絕只提示拒絕原因」、停止程式結束碼對應。
- **Cross-section consistency**:提案 3.3 ↔ 規格書 DSC-23 逐字比對,文字一致。這次的缺口在 3.3「日誌」與 AC-10 之間(N3),以及 PDT-01 規則與 DSC-23-A1 之間(C1)。
- **Anti-Bias**:C1 的 AC-6 ③ 預期「只提示拒絕原因」是第 3 輪 C2 自己的建議。本輪把它當新設計重審,結果發現它本身有錯。N1 的 `seen_ip` 條件同樣來自第 3 輪,也一起重審。
- **Understand-not-argue**:作者照第 3 輪的建議逐字落實,七項都有處理。剩下的問題都出在第 3 輪建議本身沒有想到的情境。

## § 2. 4-Tier Findings

### 🔴 BLOCKERS — 落地前必修

(none found)

### 🟡 CONCERNS — 應修

#### C1. 「正被拒絕則只提示拒絕原因」蓋掉了「尚未儲存」:改用新 IP 而未儲存時,畫面會叫人洽維護人員,這正是 DSC-23-A1 禁止的「把尚未儲存說成被其他設備佔用」

**📛 命名:** PROPOSAL.md:143「這台正被拒絕:只提示拒絕原因」;規格書:999「正被拒絕則只提示拒絕原因」;AC-6 ③(PROPOSAL.md:200)預期「只提示拒絕原因,不提示 RST」。

**📣 主張:**
- **探頭偵測連的是畫面上的 IP。** `_scan_probes` 用 `self.work` 中編輯後的 `d.ipv4` 呼叫 `station.scan(ip, …)`(settings_dialog.py:1578-1589),不是已儲存的 IP。
- **AC-6 ③ 的情境。** B 已儲存為 .11,因佔用一直被拒。工程人員改成 .13,還沒儲存就按「探頭偵測」:
  - 偵測連 .13 失敗;
  - 已儲存的設定是 .11,不等於 .13,所以符合 PROPOSAL.md:140「尚未儲存」;
  - B 正被拒絕(.11),所以依 :143 只顯示「拿不到 IP:192.168.10.11 被其他設備佔用……請洽維護人員」。
- **正確的處置是儲存。** 儲存 .13 後,主機對應改變,dnsmasq 重新啟動。B 一直在送 BOOTP,下一次請求就會拿到 .13,不需要維護人員。畫面上的訊息卻講 .11、叫人洽維護人員,與欄位裡的 .13 對不起來。
- 這正是 DSC-23-A1(規格書:1009)列出的錯誤行為「把『尚未儲存』說成『被其他設備佔用』」。
- **會發生。** 發現 IP 被佔用就改用另一個 IP,是很自然的反應;儲存前先按探頭偵測,也正是事件原因 A(PROPOSAL.md:20,4 次)。
- 第 3 輪 C2 原本只想拿掉 RST 句,寫成「只提示拒絕原因」時,把「尚未儲存」也一起拿掉了。
- Impact 4/10 / Probability 0.35
- Evidence:PROPOSAL.md:140、143、200;規格書:999、1009;app/flatness/ui/settings_dialog.py:1578-1589

**🎯 追求:** 依「畫面上的 IP 是否等於已儲存的 IP」分兩種情況:
- 不相等(尚未儲存):提示「設定尚未儲存,BOOTP 還沒有配發 <新 IP>;請先儲存」,不加 RST(這台正在送 BOOTP,手上沒有 IP)。拒絕原因只留在資訊列(PROPOSAL.md:138)。
- 相等:只提示拒絕原因。
- AC-6 ③ 預期改為「提示『設定尚未儲存,BOOTP 還沒有配發 192.168.10.13;請先儲存』,不提示 RST,也不提示洽維護人員」。另加 ④:被拒中、IP 未改,按探頭偵測 → 只提示拒絕原因。
- 規格書 999 與驗收欄同步修改。

| Option | 動作 | 成本 |
|---|---|---|
| A | 不修 | 規格自己違反 DSC-23-A1;現場照提示找維護人員,其實儲存就好 |
| B | 改為依畫面 IP 是否等於已儲存 IP 決定,並改 AC-6 ③、加 ④ | 0.2h |

推薦 B。

```yaml
- tier: 🟡 CONCERN
  id: C1
  name: "正被拒絕時只提示拒絕原因,蓋掉尚未儲存;違反 DSC-23-A1"
  evidence: ["PROPOSAL.md:140", "PROPOSAL.md:143", "PROPOSAL.md:200", "規格書:999", "規格書:1009", "app/flatness/ui/settings_dialog.py:1578-1589"]
  severity: {score: {value: 1.4, default: 1.4, override: {by: null, at: null, reason: null}}, band: low, semantic: how_bad}
  fix_economics: {difficulty: {value: 0.2, default: 0.2, override: null}, roi: {value: 7.0, default: 7.0}, resource_estimate: {value: "1h", default: "1h", override: null}}
  cross_impact: {affected_modules: [settings_dialog, spec PDT-01/DSC-23, 操作說明書 10.1/11.4], cascade_depth: 2, dependency_chain: "PDT-01 提示優先序 → 現場操作(儲存或找維護人員)"}
  phase_aware: {current_phase: 0, if_not_fixed_now_breaks_at: 3, estimated_rework_cost: low}
  decision_tree: {options: [{id: A, action: 不修, cost: "規格違反 A1,M3 照做"}, {id: B, action: 依畫面 IP 是否等於已儲存 IP 分流, cost: 0.2h}], recommended_option: B, counterfactual: "工程人員改用空的 IP 後被叫去找維護人員,原因 A 的 39 分鐘情境重演"}
  dependencies: {blocks: [], blocked_by: [], manual_blocks: []}
  severity_decay: {phase_when_found: 0, by_phase: {3: {value: 2.0, default: 2.0, override: null}}}
  po_decision: {status: no_decision, decided_at: null, decided_by: null, reason: null}
```

### 🟢 NITS — 可選 polish

- **N1. RST 條件的「目前沒有被拒」只對使用中、維修中有效,對「尚未儲存」分支大多不起作用。**
  - DSC-23 只判定已儲存為使用中或維修中的設備(PROPOSAL.md:106)。RST 子條件卻掛在「已儲存的設定中不是會配發 IP 的狀態」之下(:140-141)。這一支的設備多半已儲存為不明或已停用,DSC-23 不會判定它們,「目前沒有被拒」永遠成立。
  - `seen_ip` 不會清除(:90)。已停用的舊機(rev 4 在 :141 特別舉的例子)若曾按 RST、正在送 BOOTP(`no address available`),`seen_ip` 仍是舊值,畫面就會加「儲存後按住 RST 3 秒」。這台手上其實沒有 IP,儲存後自己就會拿到。
  - 建議把條件改成「最近 60 秒內沒有收到這台的 BOOTP 請求(不論是否被拒、不論狀態)」。這也正是 :143 自己寫的理由:送 BOOTP 的設備手上沒有 IP。
- **N2. 「連上後 10 秒內未再被拒」比日誌中最長的重送間隔短,且連上但仍被拒時的畫面沒有定義。**
  - 第 3 輪 S2 的日誌統計:DL-EN1 重新啟動時,重送間隔是 7.7 秒與 10.8 秒。佔用者在線時,若 B 在這段期間被按 RST 或斷電,間隔超過 10 秒就會誤判恢復,下一筆被拒又設回去。WARNING 多兩筆,AC-7 不成立。建議改為 15 秒,約為 10.8 秒的 1.4 倍。
  - 佔用者在線時,主畫面連到佔用者並維持連線,被拒狀態也一直持續。這時方塊顯示量測值還是「拿不到 IP」、能不能量測,都沒有規定。AC-11 只涵蓋偵測不到的情況。修完 DSC-21 之後,`address in use` 只會出現在舊安裝,所以機率低。建議一句話規定:被拒期間方塊固定顯示「拿不到 IP」,不顯示讀值。
- **N3. 「逾時清除」的日誌只寫在 3.3「恢復」段與 AC-10,「日誌」段與規格書都沒有。**
  - PROPOSAL.md:118 與 AC-10(:204)要求記「逾時清除」;但「日誌」段(:146)列出的 WARNING 只有「第一次被拒、原因改變、恢復」。規格書 999 也只有「狀態改變時各記一筆」,驗收欄沒有日誌項。
  - 「逾時清除」記不記 WARNING、算不算 AC-7 的一筆,實作者無從判斷。
  - 建議 :146 改為「第一次被拒、原因改變、恢復、逾時清除」,並在規格書 DSC-23 驗收欄的拔線項補「日誌記逾時清除」。
- **N4. 停止程式的結束碼對應正確,但 `|| true` 拿不到結束碼;1 的訊息說得太滿。**
  - 對應本身正確。停止程式以 `exec` 執行 `pkill`(03-bootp.sh:87),結束碼直接傳回。procps-ng 的 pkill:0 = 有符合且已送出訊號;1 = 沒有符合,或都無法送出訊號;2 = 語法錯誤;3 = 嚴重錯誤。
  - 但 PROPOSAL.md:61、:64 寫的是 `"$STOP_HELPER" || true`。這樣寫之後 `$?` 恆為 0,:63 的分流無法實作。應寫成 `rc=0; "$STOP_HELPER" || rc=$?`,`set -e`(setup-bootp.sh)下同樣不會中止。
  - 結束碼 1 也包含「App 的 dnsmasq 以不同命令列執行」(第 3 輪 N4)。「App 沒有執行 dnsmasq」宜改為「找不到 App 啟動的 dnsmasq(App 未執行,或命令列不同);下次啟動 App 時套用」。
- **N5. screens-device-settings.md 列的是設定頁項目,實際要改的是主畫面項目與主畫面截圖。**
  - PROPOSAL.md:158 寫「資訊列的 BOOTP 狀態、探頭偵測失敗的提示;重拍該頁的設定畫面截圖」。
  - 這份文件中受影響的是:
    - :36 `set_flag()` 的類型(要加「拿不到 IP」);
    - :40 `ProbeTile` 的方法(要加「拿不到 IP」狀態);
    - :102 Signal 清單(要加 BOOTP 被拒狀態);
    - :46 的主畫面截圖 `app-main-error-flags.png`。
  - 文件中沒有「資訊列」的段落;探頭偵測在 :73。建議照上列四處改寫該行,截圖改為主畫面那張。

```yaml
- {tier: 🟢 NIT, id: N1, name: "RST 條件的未被拒對未儲存分支無效;seen_ip 過期仍提示 RST", evidence: ["PROPOSAL.md:90", "PROPOSAL.md:106", "PROPOSAL.md:140-143", "規格書:999"], severity: {score: {value: 0.45, default: 0.45, override: {by: null, at: null, reason: null}}, band: low, semantic: how_bad}, fix_economics: {difficulty: {value: 0.1, default: 0.1, override: null}, roi: {value: 4.5, default: 4.5}, resource_estimate: {value: "1h", default: "1h", override: null}}, cross_impact: {affected_modules: [settings_dialog, backend], cascade_depth: 1, dependency_chain: "提示條件"}, phase_aware: {current_phase: 0, if_not_fixed_now_breaks_at: 3, estimated_rework_cost: low}, decision_tree: {options: [{id: A, action: 不修}, {id: B, action: 改為最近 60 秒內沒有收到 BOOTP 請求}], recommended_option: B, counterfactual: "對手上沒有 IP 的設備提示按 RST"}, dependencies: {blocks: [], blocked_by: [], manual_blocks: []}, severity_decay: {phase_when_found: 0, by_phase: {}}, po_decision: {status: no_decision, decided_at: null, decided_by: null, reason: null}}
- {tier: 🟢 NIT, id: N2, name: "10 秒短於重啟間隔 10.8 秒;連上但仍被拒時畫面未定義", evidence: ["PROPOSAL.md:117", "規格書:999", "round-3 S2"], severity: {score: {value: 0.3, default: 0.3, override: {by: null, at: null, reason: null}}, band: low, semantic: how_bad}, fix_economics: {difficulty: {value: 0.1, default: 0.1, override: null}, roi: {value: 3.0, default: 3.0}, resource_estimate: {value: "1h", default: "1h", override: null}}, cross_impact: {affected_modules: [backend, main_window], cascade_depth: 2, dependency_chain: "恢復條件 → WARNING 數 → AC-7"}, phase_aware: {current_phase: 0, if_not_fixed_now_breaks_at: 2, estimated_rework_cost: low}, decision_tree: {options: [{id: A, action: 不修}, {id: B, action: 改 15 秒並定義被拒期間方塊}], recommended_option: B, counterfactual: "佔用者在線且 B 重啟時提示跳動"}, dependencies: {blocks: [], blocked_by: [], manual_blocks: []}, severity_decay: {phase_when_found: 0, by_phase: {}}, po_decision: {status: no_decision, decided_at: null, decided_by: null, reason: null}}
- {tier: 🟢 NIT, id: N3, name: "逾時清除日誌未列入日誌段與規格書", evidence: ["PROPOSAL.md:118", "PROPOSAL.md:146", "PROPOSAL.md:204", "規格書:999"], severity: {score: {value: 0.3, default: 0.3, override: {by: null, at: null, reason: null}}, band: low, semantic: how_bad}, fix_economics: {difficulty: {value: 0.05, default: 0.05, override: null}, roi: {value: 6.0, default: 6.0}, resource_estimate: {value: "1h", default: "1h", override: null}}, cross_impact: {affected_modules: [backend, spec DSC-23], cascade_depth: 1, dependency_chain: "文字"}, phase_aware: {current_phase: 0, if_not_fixed_now_breaks_at: 2, estimated_rework_cost: low}, decision_tree: {options: [{id: A, action: 不修}, {id: B, action: 日誌段與規格書補一項}], recommended_option: B, counterfactual: "逾時清除記不記 WARNING 由實作者自行決定"}, dependencies: {blocks: [], blocked_by: [], manual_blocks: []}, severity_decay: {phase_when_found: 0, by_phase: {}}, po_decision: {status: no_decision, decided_at: null, decided_by: null, reason: null}}
- {tier: 🟢 NIT, id: N4, name: "|| true 拿不到結束碼;結束碼 1 訊息過度斷言", evidence: ["PROPOSAL.md:61", "PROPOSAL.md:63", "PROPOSAL.md:64", "installer/steps/03-bootp.sh:87", "pkill(1) EXIT STATUS"], severity: {score: {value: 0.2, default: 0.2, override: {by: null, at: null, reason: null}}, band: low, semantic: how_bad}, fix_economics: {difficulty: {value: 0.05, default: 0.05, override: null}, roi: {value: 4.0, default: 4.0}, resource_estimate: {value: "1h", default: "1h", override: null}}, cross_impact: {affected_modules: [installer], cascade_depth: 1, dependency_chain: "安裝日誌"}, phase_aware: {current_phase: 0, if_not_fixed_now_breaks_at: 1, estimated_rework_cost: low}, decision_tree: {options: [{id: A, action: 不修}, {id: B, action: "rc=0; helper || rc=$?;改 1 的訊息"}], recommended_option: B, counterfactual: "照抄 || true 後安裝日誌永遠記結束碼 0 的訊息"}, dependencies: {blocks: [], blocked_by: [], manual_blocks: []}, severity_decay: {phase_when_found: 0, by_phase: {}}, po_decision: {status: no_decision, decided_at: null, decided_by: null, reason: null}}
- {tier: 🟢 NIT, id: N5, name: "screens-device-settings 列錯項目與截圖", evidence: ["PROPOSAL.md:158", "docs/ui/screens-device-settings.md:36,40,46,73,102"], severity: {score: {value: 0.4, default: 0.4, override: {by: null, at: null, reason: null}}, band: low, semantic: how_bad}, fix_economics: {difficulty: {value: 0.05, default: 0.05, override: null}, roi: {value: 8.0, default: 8.0}, resource_estimate: {value: "1h", default: "1h", override: null}}, cross_impact: {affected_modules: [docs/ui], cascade_depth: 1, dependency_chain: "文件同步"}, phase_aware: {current_phase: 0, if_not_fixed_now_breaks_at: 5, estimated_rework_cost: low}, decision_tree: {options: [{id: A, action: 不修}, {id: B, action: 改列 :36/:40/:102 與主畫面截圖}], recommended_option: B, counterfactual: "M5 重拍錯的截圖,類別表漏改"}, dependencies: {blocks: [], blocked_by: [], manual_blocks: []}, severity_decay: {phase_when_found: 0, by_phase: {}}, po_decision: {status: no_decision, decided_at: null, decided_by: null, reason: null}}
```

### ✅ STRENGTHS

- **S1. 逾時清除的結果寫得完整。** PROPOSAL.md:118、AC-10、規格書 999 三處一致:都從最近一次被拒起算,使用中改為偵測不到、維修中回到維修中。維修中不列入偵測(main_window.py),所以這樣寫與程式相符。
- **S2. 10 秒確認把「連線不核對 MAC」說清楚了。** 被拒時重送間隔 3～5 秒(第 3 輪 S2),10 秒內至少會出現兩筆被拒,一般情況足以分辨。維修中不連線,這條規則不會誤用到維修中的設備。
- **S3. 停止程式的結束碼對應與 pkill 一致。** 0/1/其他三類對得上 pkill 的 0/1/2-3,而且 heredoc 用 `exec`(03-bootp.sh:87),中間沒有 shell 改寫結束碼。
- **S4. UI 文件清單大致補齊。** screen-design-spec.md 的 :110「互不取代」、:204 IP 不符、:222 方塊文字、:346 PDT-01 四處,以及原型,都已列入 3.4(PROPOSAL.md:153-159)與第 4 節(:189)。

## § 3. Critical Hotspots

本輪沒有 hotspot:最高 effective cost 1.4,cascade 都 ≤ 2(shortcut table「1-5 / ≤3 視 case,通常無 hotspot」)。

| 項目 | 早解成本 | 晚解成本 | ratio |
|---|---|---|---|
| C1 PDT-01 提示優先序(參考) | 0.2h | M3 實作與說明書返工約 0.5d | ~20× |

## § 4. Effective Cost Matrix

| ID | Tier | Impact | Prob | Effective cost | Fix 成本 |
|---|:---:|:---:|:---:|:---:|:---:|
| C1 | 🟡 | 4 | 0.35 | 1.4 | 0.2h |
| N1 | 🟢 | 3 | 0.15 | 0.45 | 0.1h |
| N5 | 🟢 | 2 | 0.2 | 0.4 | <0.1h |
| N2 | 🟢 | 3 | 0.1 | 0.3 | 0.1h |
| N3 | 🟢 | 1.5 | 0.2 | 0.3 | <0.1h |
| N4 | 🟢 | 2 | 0.1 | 0.2 | <0.1h |
| **合計** | | | | **≈3.05** | **≈0.6h** |

成本趨勢:第 1 輪 ≈27.0 → 第 2 輪 ≈18.1 → 第 3 輪 ≈5.95 → 第 4 輪 ≈3.05,比第 3 輪下降約 49%。Saving:現在修只要約 0.6 小時;若 M3 照現在的規則實作,C1 估計返工約 0.5 天(程式、說明書 10.1/11.4、AC)。

## § 5. Decision Log

**第 3 輪 finding 在 rev 4 的實際狀態(已逐項驗證):**

| R3 ID | 狀態 | 驗證 |
|---|:---:|---|
| C1 文件清單漏列 UI 文件 | 🔶 大致修好 | screen-design-spec 四處與原型已列入(PROPOSAL.md:153-159、189)。screens-device-settings 只列「資訊列、探頭偵測、設定畫面截圖」,沒有列 :36、:40、:102 與主畫面截圖 :46(N5)。 |
| C2 RST 條件改用 seen_ip、被拒優先 | 🔶 部分修好 | 條件改用 `seen_ip`、加「目前沒有被拒」、AC-6 ③ 已加(PROPOSAL.md:141、143、200;規格書:999)。但「只提示拒絕原因」把「尚未儲存」也拿掉,違反 DSC-23-A1(C1)。「目前沒有被拒」對尚未儲存的分支無效(N1)。 |
| N1 連上不核對身分 | ✅ fixed | PROPOSAL.md:117 與規格書 999 都加了「之後 10 秒內未再被拒」,並寫明理由。殘留:10 秒短於重啟時的 10.8 秒間隔(N2)。 |
| N2 逾時對維修中、日誌、起算點 | ✅ fixed | :118、AC-10、規格書 999 都寫了維修中回到維修中、從最近一次被拒起算、記為「逾時清除」。殘留:日誌段與規格書沒有列入(N3)。 |
| N3 改名後的寫入去向 | ✅ fixed | :67 改為「可能寫進已改名的檔案或產生新檔……兩者都不會讀」,結論與 dnsmasq 的行為相容。 |
| N4 安裝日誌不分情況 | ✅ fixed | :63 依結束碼 0/1/其他分三種訊息,與 pkill 一致(S3)。殘留:`|| true` 拿不到結束碼,結束碼 1 的訊息說得太滿(N4)。 |
| N5 M1 仍寫安裝後檢查 | ✅ fixed | :209 改為「停止程式與安裝日誌」。 |

- 本輪新拍板:無,全部為 `no_decision`。
- 依據紀錄(非決定):pkill(procps-ng 3.3.17)結束碼 0/1/2/3 的意義;探頭偵測連的是畫面上編輯後的 IP(settings_dialog.py:1578-1589)。

## § 6. Verdict + Next Round Focus

- **Status:** ship-as-is。沒有 BLOCKER。第 3 輪 7 項中 5 項已修、2 項部分修;有 1 項新的 CONCERN,是第 3 輪建議本身的缺陷。
- **Recommend:** 簽核前改 C1,約 0.2 小時:探頭偵測失敗時,依畫面上的 IP 是否等於已儲存的 IP 分流;AC-6 ③ 改預期,另加 ④。N1～N5 可在同一次修正中處理。
- **Next Round Focus:** 不需要第 5 輪文件審查。M3 完成後跑 V7 spec-compliance-review,重點如下:
  1. AC-6 ③、④ 的提示文字;
  2. AC-7 在 IP 衝突且 B 重新啟動時的 WARNING 筆數;
  3. 逾時清除後 DSC-20 是否用過期的 `seen_ip` 又叫人按 RST。

(§ 7 Mental Lens Reflection:本輪沒有重大 BLOCKER,不觸發。)
