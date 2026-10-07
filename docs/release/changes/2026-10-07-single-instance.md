---
date: 2026-10-07
type: fixed
scope: app, spec
requirements: NFR-14, DSC-07, DAT-05
---

# 同一時間只執行一個 App；App 收到 SIGTERM 立即正常結束

- App 啟動時先停止其他執行中的 App（命令列含 `-m flatness`，不含自己與上層的啟動腳本）：先送 SIGTERM，5 秒內未結束再 SIGKILL；被強制停止者留下的 dnsmasq 由 DSC-07 殘留清除處理。日誌記錄「發現其他執行中的 App（pid …），先停止再啟動」。
- 修正 App 收到 SIGTERM（登出、關機、被新 App 停止）要 5 秒以上才結束：dnsmasq 經 sudo 執行且與 App 同一程序群組，sudo 不轉送同群組送來的訊號，只能等逾時改用停止程式。dnsmasq 改在獨立程序群組執行後，交接約 0.4 秒。
- 收到 SIGTERM／SIGINT／SIGHUP 時記錄日誌、關閉主畫面（寫入未寫入的結果）並直接結束事件迴圈，不依賴「最後一個視窗關閉」。
- 真機驗證：真的 dnsmasq 執行中再啟動一次 App → 舊 App 正常結束、舊 dnsmasq「exiting on receipt of SIGTERM」→ 新 dnsmasq 啟動；停止程式 `flatness-stop-dnsmasq` 在真機上有效（結束碼 0）。
- 規格書新增 NFR-14（待確認），DSC-07 註明「另一個 App 正在執行 dnsmasq」只在無法停止其他 App 時出現。
