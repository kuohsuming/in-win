---
date: 2026-10-07
type: removed
scope: app, spec, docs
requirements: SIM-01..SIM-16, 3.7.1
---

# 設定頁隱藏 TCP 埠；撤銷 DL-EN1 模擬器需求

- 「設備設定」不再顯示「TCP 埠 port」欄位。DL-EN1 固定使用 64000；定義檔或匯入設定中原有的 `port` 照舊保留，不會被清除。
- PO 決定不開發 DL-EN1 模擬器：規格書 3.9 的 SIM-01～SIM-16 全部劃線撤銷，編號保留不再使用。App 的 `--simulate` 開發用旗標維持現狀。
- 規格書 3.7.1 `port` 說明、需求追溯，以及畫面設計規格同步更新。
