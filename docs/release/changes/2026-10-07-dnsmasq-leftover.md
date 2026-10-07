---
date: 2026-10-07
type: fixed
scope: app, installer, spec
requirements: DSC-07, INS-04
---

# 清除 App 當掉後殘留的 dnsmasq；以停止程式停止 root 執行的 dnsmasq

- App 啟動 dnsmasq 前，掃描 `/proc` 找出相同固定命令列、但不屬於任何執行中 App 的程序（App 當掉或 `kill -9` 後殘留），先停止再啟動；屬於另一個執行中 App 的不停止並顯示原因；無法停止時顯示處理方式並定期重試。
- sudo 啟動的 dnsmasq 為 root 程序，App 帳號無法直接送訊號：安裝包新增 root 擁有、不接受參數的 `/usr/local/sbin/flatness-stop-dnsmasq`（`pkill -x -f` 固定命令列），sudoers 加入此程式（不帶參數）。App 結束、重新啟動與清除殘留皆在權限不足時改用它。
- 已安裝的工站需重新執行 `sudo ./installer/setup-bootp.sh`。
- 開發機驗證：`kill -9` 開發 App 後再啟動，日誌「發現殘留的 dnsmasq（pid …），先停止再啟動」→「已停止殘留的 dnsmasq」。
- 規格書 DSC-07 修訂（新增 A7～A9）、3.0.4 步驟 3 與 INS-04 備註同步；記錄 DL-EN1 持續重送 BOOTP（待真機驗證）。
