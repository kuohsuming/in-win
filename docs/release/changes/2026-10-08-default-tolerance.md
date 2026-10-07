---
date: 2026-10-08
type: changed
scope: app, spec, docs
requirements: JDG-06, TBD-01
---

# 允許誤差預設值改為 0.5 mm

- 探頭允許誤差的預設值從 5 mm 改為 **0.5 mm**（PO 指示）。新增的探頭、以及設定中沒有寫允許誤差的探頭，都以 ±0.5 mm 判定。
- 已明確設定允許誤差的探頭不受影響。開發機目前的兩個探頭都設為 0.2 mm，不變。
- 設定中等於預設值（0.5 mm）時不寫入 `probes[].tolerance`。
- 規格書 JDG-06、3.7.1、TBD-01，畫面設計規格，操作說明書同步更新。JDG-06 仍待 PO 簽核。
