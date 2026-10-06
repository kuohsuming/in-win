<!--
@produced-by: orchestrator (Claude)
@authorized-by: PO (kuohsuming) 2026-08-13 —— 原話：「寫進 rulebook 的通則：任何 validator 在
  『本次沒有解析到任何待檢對象』時，不得輸出成功訊號，必須輸出一個與成功在字面上可區分的狀態。」
@scope: 本 repo 所有 gate / validator（`scripts/*.py`、`lint.sh` 的各 Stage）
@sibling: requirement- / functional- / design- / test-plan- / test-cases-spec-authoring-rules.md
  ⇒ 那五本管「spec 該怎麼寫」；本本管「**檢查 spec 的東西**該怎麼寫」。
-->
---
title: "Validator Authoring Rules — gate 自己不許說謊"
spec_version: 2026-08-13.0
status: Active
schema_version: validator-rules-v1
---

# Validator Authoring Rules

> **一句話**：gate 分不出「查了，沒問題」與「根本沒查到東西」時，
> 它預設會說前者。本本就是為了關掉這個預設。

---

## §1 核心規則（VR-1）

> **VR-1 —— 零對象不得報成功**
>
> 任何 validator 在「本次沒有解析到任何待檢對象」時，**⛔ 不得輸出成功訊號**。
> 必須輸出一個與成功**在字面上可區分**的狀態。

「字面上可區分」的意思是：**把兩份輸出並排，人一眼看得出哪份是「檢查過且相符」、哪份是「什麼都沒檢查」。**
⛔ 只有 exit code 不同不算 —— 沒有人在讀 exit code，人讀的是那一行字。

### 反例（真實發生過）

```
✅ staleness clean
```

這一句同時涵蓋「11 條 pin 逐一比對相符」與「一條 pin 都沒解析出來」。
2026-08-12 的 F-O3 就是這樣：repo 內 **5 份 FUNC spec 全部用 flow-list 寫法**，
`_covered_reqs()` 一律回空集合 ⇒ 全部被當「非下游」跳過 ⇒ **一份都沒被檢查過**，
而報表上與「檢查過且相符」**逐字相同**。

### 正例（現行 `coverage_staleness.py` 的修法）

```
⏸ 0 downstream covered —— **沒有任何 covers_req 被解析出來，本次沒有檢查任何東西**（⛔ 這不是通過）
```

---

## §2 為什麼這條值得單獨成規（失效方向是不對稱的）

一個 gate 壞掉有兩個方向：

| 方向 | 症狀 | 會不會被發現 |
|---|---|---|
| **誤報**（該綠判紅）| 有人被擋住、抱怨、來查 | ✅ **必然被發現** —— 它會妨礙到人 |
| **漏報**（該紅判綠）| 什麼都沒發生 | 🔴 **不會被發現** —— 而且會讓 review **停止追問** |

⇒ 兩個方向的成本**差好幾個數量級**，但寫 gate 的人通常只在腦子裡演練誤報那一邊
（因為那一邊會痛）。VR-1 就是把注意力硬拉到漏報那一邊。

⭐ 更糟的是：**綠色會產生信任**。
`[[feedback_dead_code_makes_rules_look_alive]]` 記的那次，有定義零呼叫的死碼
躲過 **14 輪 review + 一次真機 QA** —— 不是因為沒人看，是因為「看起來有做」讓人停止追問。
一個恆綠的 gate 比沒有 gate **更危險**，因為沒有 gate 時人還會自己查。

---

## §3 這條規則是從七個實例歸納出來的（⛔ 不是憑空的原則）

2026-08-12 ~ 08-13 一批 spec 工作中，逐一實跑咬出七個同類缺口。
它們分兩個家族，但**失效方向完全相同**：

### 家族 A —— ID 沒有 project 限定，validator 用全域表解析

| # | 缺口 | 失效形狀 |
|---|---|---|
| **F-O1** | `REQ-RPT-001` 這種帶前綴的 ID 只有一個 validator 認得 | 那批 REQ 在覆蓋率統計裡**整批消失**，lint 仍 EXIT=0 |
| **F-O4** | `TP-004.vkp-1` 解析到**別的 project** 同名定義上 | ⭐ 最嚴重：不是「沒查」而是「**查了、查錯對象、回報通過**」|
| （既有 D-034）| REQ-id 僅 project 內唯一，validator 塌成全域 last-wins | pin 記成別人的 hash ⇒ 改 REQ 永不報 stale |

### 家族 B —— validator 對 spec 的「長相」做了一個**沒寫下來的假設**

| # | 假設 | 破掉時 |
|---|---|---|
| **F-O3** | 下游一定用單值 `covers_req: REQ-x` | flow-list `[a, b]` ⇒ 回空集合 ⇒ 印 `✅` |
| **FM-cov** | `_blocks()` 以「下一個 `id:` 行」切塊 | `- id: FM-1` 本身就是 id 行 ⇒ **只查 step 不查 FM**，一半 claim 隱形 |
| **F-O5** | `upstream_pins:` 行不帶註解；區塊內不夾註解 | 整塊 pin 隱形，退化成「沒有 pin」而「沒有 pin」只印 🟡 |
| **F-O6** | 下游一定用 `covers_req` 表達覆蓋 | DESIGN 用 `for_claim:` ⇒ **連 🟡 都不印，整個從報表消失** |
| **F-O7** | 上游欄位一定叫 `upstream_spec:` | DESIGN 用 `upstream_req:` ⇒ 判 unresolved |

⭐ **家族 B 的共通點**：這些假設在寫 validator 的當下**都是對的**（當時的 spec 就長那樣）。
它們是被**後來的合理寫法**破掉的 —— 作者在 pin 行後面加一句註解解釋 hash 為什麼變了，
是完全正確的行為。⇒ **不能靠「叫作者別那樣寫」解決**，只能靠 VR-1。

⚠️ **F-O6 的紅前形狀最值得記**：selftest 的紅前結果是 `stale=0(exp 1)` ——
舊 code 回報「**零問題**」。那不是一個看得出來的錯誤，是一個**「全部乾淨」的假象**。

---

## §4 落實 VR-1 的四條作法

### VR-1.1 —— 每個 validator 必須能回答「我這次檢查了幾個對象」

輸出中必須有一個**計數**，且該計數為 0 時走 §1 的分支。

```python
if ok:
    print(f"  ✅ staleness clean — {len(ok)} 條 pin 逐一比對相符")   # ← 帶數字
else:
    print("  ⏸ 0 downstream covered —— 本次沒有檢查任何東西（⛔ 這不是通過）")
```

⚠️ 帶數字本身就有診斷力：`✅ clean — 2 條` 在你預期 11 條時會讓你停下來。
`✅ clean` 不會。

### VR-1.2 —— selftest 的紅前錨必須拿「**真的會發生的寫法**」

⛔ 不要造一個沒人會寫的畸形 fixture 來證明 gate 會叫。
紅前錨要用**作者自然會寫出來的那個形狀**：

| gate | 該用的紅前錨 |
|---|---|
| pin 解析 | `upstream_pins:   # ✅ 重擷完成（…）` ← 作者真的會這樣寫 |
| covers 解析 | flow-list `covers_req: [REQ-a, REQ-b]` ← repo 內 5 份 FUNC 都這樣寫 |
| 覆蓋率 | 一份用 `for_claim:` 而非 `covers_req:` 的 DESEGN spec |

### VR-1.3 —— 修 gate 之後必須跑**反向錨**：既有 case 逐條不變

「修過頭」與「沒修到」一樣糟。每次改 gate：

```
新 case：舊 code 判紅 → 現版判綠     （= 這個修法有鑑別力）
舊 case：舊 code 判綠 → 現版仍判綠   （= 沒修過頭）
```

⚠️ 少了第二行，「把判準放寬到什麼都不擋」也會讓第一行全綠。

### VR-1.4 —— 判準用**結構**不用字串

⛔ `grep "occupation" app.py` —— 註解、docstring、同名區域變數都會讓它假綠。
✅ AST 的 `keyword` 名單 / 呼叫點計數（且**先剝註解**）。

⚠️ 2026-08-13 的實例：修 `app.py:13760` 時我寫的註解區塊裡出現了好幾次 `occupation`，
grep 判準會**直接假綠**。同一件事 `[[feedback_dead_code_makes_rules_look_alive]]` 說過：
**查落地要數呼叫點，不是數定義**。

---

## §5 ⛔ 明確禁止的兩件事

1. **⛔ 不得為了讓報表變乾淨而讓 gate 去猜。**
   2026-08-13 的實例：4 份 `friend-relation-tag-*-design-spec.md` 判 🟡 unresolved，
   因為它們的 frontmatter **根本沒有指向 REQ 檔的欄位**。
   那是該專案的 spec 撰寫缺口，**不是 validator 的** ⇒ 留著讓它繼續叫。
   讓 gate 去猜上游是哪一份，等於用一個新的隱形假設換掉一個看得見的警告。

2. **⛔ 不得靠「改 gate 讓它閉嘴」清掉真實的紅字。**
   紅字的正確去處是修下游（或明文記為已知缺口），不是調寬判準。

---

## §6 fail-closed（VR-2）

> **VR-2 —— 刪掉 validator 檔不得讓 gate 變綠**

```bash
# ⛔ 反例（lint.sh:199 Stage 1.13 的既有慣例）
if [ -f scripts/xxx_validator.py ]; then python3 scripts/xxx_validator.py; fi
```

檔案不見 ⇒ 整段跳過 ⇒ **綠**。而它守的可能是遮蔽這種安全面。
新 stage 一律 fail-closed：檔案不存在本身就是紅。

---

## §7 檢查清單（新增或修改 validator 時逐條過）

- [ ] **VR-1**：零對象時的輸出，與成功的輸出**在字面上可區分**
- [ ] **VR-1.1**：輸出帶「本次檢查了幾個對象」的計數
- [ ] **VR-1.2**：selftest 的紅前錨用**作者真的會寫**的形狀，不是畸形 fixture
- [ ] **VR-1.3**：新 case 紅前綠後 **且** 既有 case 逐條不變
- [ ] **VR-1.4**：判準用 AST / 結構，不用 grep 字串（要 grep 則先剝註解）
- [ ] **VR-2**：fail-closed —— 刪檔不得變綠
- [ ] ID 若跨 project 聚合 → 帶 project key（`parent_project` 為唯一解析源，D-19 / D-034）

---

## §8 Revision History

| rev | 日期 | 內容 |
|---|---|---|
| `2026-08-13.0` | 2026-08-13 | 初版。PO 於 F-O5/F-O6/F-O7 三個缺口修完後裁決成文。規則本體 = VR-1；§3 的七個實例是歸納來源，⛔ 不是舉例 |
