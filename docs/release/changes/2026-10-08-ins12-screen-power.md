---
date: 2026-10-08
type: added
scope: spec, scripts
requirements: INS-12, INS-07
---

# 需求 INS-12：螢幕閒置關閉、喚醒不需密碼、不自動睡眠

- 規格書新增 INS-12（**待 PO 簽核**），包含 INS-12-G1 正確流程與 INS-12-A1～A3 錯誤行為：
  - 閒置 5 分鐘關閉螢幕。
  - 喚醒後直接回到 App，不鎖定、不要求密碼。
  - 電腦不因閒置自動睡眠。
- 3.0.4「產線桌面」改為與 INS-12 一致，原本寫的是「關閉螢幕保護」。3.0.7 安裝後檢查新增「螢幕與電源」一項。
- 開發機已由 `scripts/install-desktop.sh` 套用（commit e6ac583）。
