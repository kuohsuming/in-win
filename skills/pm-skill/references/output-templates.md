# PM Skill — Output Format Templates

> **Loaded by:** `SKILL.md` for `/pm daily`, `/pm dashboard`, `/pm status`, `/pm gate-check` workflows.
> **Source:** Aligned with user manual rev 1.8 scenarios 3 / 6a / 8 / 9 / 10 / 12 PM Skill output blocks.

## Daily Briefing(`/pm daily`)

Output at `docs/pm/<active-project>/reports/<date>-daily.md` AND inline to user.

```markdown
☀ Daily Briefing — <YYYY-MM-DD>(Phase <N> Day <X>)

📊 整體進度
  - <N> REQs total: <X> ✅ done / <Y> 🟡 in-progress / <Z> ⏳ planned
  - Burndown: <on track | ahead | behind X days>
  - 預估 Phase <N> 結束: <YYYY-MM-DD>(信心度 <%>)

👥 Team Status(對齊 §6.4.11 §E.3a 三向 invariant)
  - <engineer>(<module>): <progress> ✅/⚠/❌
  - ...

🚨 Anomalies(健康檢查偵測)
  1. <description> → 違反 <invariant> → 建議 <action>
  2. ...

🆕 Mid-flight REQ tracking(對齊 §6.4.10 §L Override)
  - F-<id>(<title>):<status>,<context>

📍 推薦 Top-3 actions(對齊 §6.4.8 Fix Recommendation Algorithm)
  1. <action>(severity=<X> / 影響 <scope>)
  2. ...

🧪 Flaky test watch(對齊 §6.4.11 §E.4a)
  - <module>: <count>/<max> flaky
  - revisit_at deadlines: ...

—— 一頁完。你想 deep dive 哪個?
```

**Confidence Tier per row:**
- 整體進度 / Team Status / Flaky test watch:🟢 high(file reads / counts)
- Anomalies:🟡 medium(invariant check rules deterministic,但「需 attention」推薦 LLM 判斷)
- Top-3 actions:🟡 medium(Fix Recommendation Algorithm 含 LLM ranking)

## Dashboard(`/pm dashboard`)

```markdown
🏢 PM Skill Cross-Project Dashboard — <YYYY-MM-DD>
   讀取來源:docs/pm/*/state.md(掃所有 project subfolder,排除 _org)

📊 Active Projects(<N> 個)

┌──────────────────────────────┬───────┬─────┬──────┬───────────────────┐
│ Project                      │ Phase │ Day │ Burn │ Health           │
├──────────────────────────────┼───────┼─────┼──────┼───────────────────┤
│ <project>                    │ <N>   │ X/Y │ %    │ ✅/⚠/❌          │
│ ...                                                                    │
└──────────────────────────────┴───────┴─────┴──────┴───────────────────┘

🚨 Cross-Project Anomalies(對齊 §6.4.8 橫向 Fix Recommendation)
  1. <type>: <description>
  2. ...

📊 Cross-Project KPI Rollup(對齊 §7.5 三層 KPI)
  Efficiency: <metric>: <value>
  Quality: <metric>: <value>
  Strategic: <metric>: <value>

📋 Today's Top 3 actions
  1. <action>
```

**Confidence Tier:**
- Active Projects table:🟢 high
- Cross-Project Anomalies(resource conflict / common pattern):🟡 medium(LLM compare;false positives 需 cite evidence)
- KPI Rollup:🟢 high(metric reads deterministic)

## Status(`/pm status`)

```markdown
📊 Project: <project> | Phase: <N> | Type: <type>

Signoffs:
  - Phase <N-1> ✅ signed by <approvers> at <YYYY-MM-DD>
  - Phase <N> ⏸ pending <required approvers>

Target Release: <YYYY-MM-DD>
Outstanding Blockers: <count>
  - <description>
Open Issues(spectra summary): <count>
Last Phase Advance: <YYYY-MM-DD>

🎯 Next Action: <recommendation>
```

## Gate-Check(`/pm gate-check phase-<N>`)

```markdown
🚪 Phase <N> Exit Gate-Check

跑 §6.4.X §B.Y 全部 acceptance criteria + §K Exit Check List:

✅ 1. <criterion>
   - <evidence>
⚠ 2. <criterion>
   - <issue> — 建議 <fix>
❌ 3. <criterion>
   - <fail reason>

🎯 Verdict: ✅ Ready / ⚠ <count> warnings / ❌ NOT ready

📍 Next:
  - <action 1>
  - <action 2>
```

## Onboarding Pack(`/pm onboard`)

詳細格式見 user manual scene 13 lines 1268-1310(6 段:必讀 / Unresolved / 該找誰 / Day 1-3 路徑 / memory + org knowledge inject / 系統 update)。

## Offboard Hand-over(`/pm offboard`)

詳細格式見 user manual scene 13 lines 1316-1330(對齊 §6.4.11 §E.3 三向 invariant + Half-done features 4 步處理)。

---

**Convention reminder:** 所有 PM Skill output 必標 Confidence Tier per §SKILL.md Auto Behavior Confidence Tier convention,fallback 至 "list raw evidence + ask PO" 而非 silent fail。
