---
date: 2026-10-13
type: added
scope: spec, docs
requirements: P3D-01～P3D-09, TBD-05～TBD-07
---

# 3D 繪圖（plate3d）提案修訂與需求

- PO 提出「表面 3D 繪圖模組」提案。對照現有 App 檢視後修訂，原始版保留於 `docs/pm/plate3d/PROPOSAL.orig.md`，修訂版為 `docs/pm/plate3d/PROPOSAL.md`（差異見附錄 A）。
- 需求規格書新增 3.12 3D 繪圖（P3D-01～P3D-09）、TBD-05～TBD-07、需求追溯一列。**待 PO 簽核**，尚未實作。
- 主要決定：依實際探頭數量與讀值繪圖；有效點少於 3 個或全部在同一直線上時按下即警告拒絕；預設顯示「相對標準件」（與主畫面數值相同）；不新增 numpy、scipy；板子設定放 `config.toml [plate]`；視窗嵌入主畫面；高度放大以允許誤差為基準。
- 同日 PO 補充：探頭在板子下方（TBD-05 結案）；板子尺寸在主畫面設定長、寬、高（mm），探頭自動平均分佈在板子下方（TBD-06 結案）。修訂 P3D-05，新增 P3D-10（工具列「板子尺寸」按鍵與設定小視窗，存本機、不需密碼），不採用 `config.toml [plate]`。
