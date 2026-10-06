---
title: Ops Runbook — Azure MySQL + WebApp Operations
project_scope: cross-project (all PM projects sharing Azure infrastructure)
maintained_by: PM-kuohsuming
created: 2026-06-24
created_via: F3.3 (Phase 6 ops review C-T1.1 batch)
related_reports:
  - docs/pm/backend-schema-auto-sync/reports/2026-06-24-f3-azure-mysql-firewall-review.md
  - docs/pm/backend-schema-auto-sync/reports/2026-06-24-f4-audit-log-retention-review.md
revision: 1.0
---

# Ops Runbook — Azure MySQL + WebApp Operations

> 🧭 **Audience:** PO + future engineers operating Azure infrastructure for this project family。Living document — update when ops procedures change。
>
> ⚠ Scope:**read-only audit procedures + safety check workflows**。Destructive operations(eg. add/remove firewall rule,delete DB,rotate credentials)require PO authorize per `[[backend_change_rule]]` spirit + `[[backend_schema_change_workflow]]`。

---

## § 1. Azure MySQL Firewall Rule Audit

### 1.1 — How to list current firewall rules(read-only)

Pre-req:Azure CLI installed + `az login` complete + subscription set。

```bash
# List all firewall rules for the MySQL server
az mysql server firewall-rule list \
  --resource-group beautyreservation_group \
  --server liffbeauty \
  --output table
```

Expected output(example shape):
```
Name                StartIpAddress   EndIpAddress     ResourceGroup
------------------  ---------------  ---------------  ---------------------
AllowDevHomeOffice  120.96.X.X       120.96.X.X       beautyreservation_group
AllowAzureServices  0.0.0.0          0.0.0.0          beautyreservation_group
...
```

**`AllowAzureServices`(0.0.0.0)is special** — allows ALL Azure-internal IPs through。Required for App Service → MySQL connectivity but acts as a wide door。

### 1.2 — How to add a firewall rule(destructive — PO authorize required)

```bash
# Add rule for a specific dev IP (eg. PO home office)
az mysql server firewall-rule create \
  --resource-group beautyreservation_group \
  --server liffbeauty \
  --name "AllowDevHomeOffice-<YYYYMMDD>" \
  --start-ip-address <ip> \
  --end-ip-address <ip>
```

**Convention:** rule name MUST include date suffix `-YYYYMMDD` to enable expiry audit。Rule older than 90 days → review for removal in quarterly audit。

### 1.3 — How to remove a firewall rule(destructive — PO authorize required)

```bash
az mysql server firewall-rule delete \
  --resource-group beautyreservation_group \
  --server liffbeauty \
  --name "<rule-name>" \
  --yes
```

### 1.4 — Quarterly audit checklist

| Item | Verify |
|:---|:---|
| All rules have date suffix | `-YYYYMMDD` in name |
| No rules older than 90 days without review | Compare suffix to today;flag for renewal or removal |
| `AllowAzureServices` exists | Required for App Service connectivity |
| No unnamed test rules left over from incidents | Look for `temp-` / `debug-` / single-letter names |

---

## § 2. Staging vs PROD DB Separation Guidelines

### 2.1 — Current state(2026-06-24)

| Environment | Resource | Status |
|:---|:---|:---|
| Local dev | `localhost` MySQL(WSL2 / Docker)| ✅ In use |
| PROD | `liffbeauty.mysql.database.azure.com` | ✅ In use |
| **Staging** | ❌ Does not exist | Tier 2 F3.4 proposes creating |

### 2.2 — Recommended target state

| Environment | Resource | Access |
|:---|:---|:---|
| Local dev | `localhost` | Self-managed |
| **Staging**(F3.4 proposal) | `liffbeauty-staging.mysql.database.azure.com`(Basic tier ~$10-20/mo)| Dev IPs whitelisted here for integration testing |
| PROD | `liffbeauty.mysql.database.azure.com` | **Only Azure WebApp egress IPs** — dev IPs removed after staging available |

### 2.3 — When to use which

| Scenario | Use |
|:---|:---|
| Daily dev / unit tests | local `localhost` |
| Integration tests with real Azure connectivity(eg. schema_sync.py end-to-end)| staging(when F3.4 done) |
| Pilot v0 sanity_test_runner LIFF dogfood | local with ngrok(see /pm sanity-check workflow) |
| Phase 5 / Phase 6 integration test scenarios | staging(safer than PROD near-miss pattern from Phase 5 F3 finding) |
| /pm deploy --target prod precondition smoke | PROD `/health` 200 only(no DB write) |
| /pm deploy --target prod | PROD(schema_sync.py boots,writes to `_schema_sync_log`) |

### 2.4 — `Const_Run_in_local_environment` safety check

This boolean in `local_build_environment.py` controls which DB `system_constant.Const_db_info` points to。

**Mandatory pre-commit verification:** `Const_Run_in_local_environment = False` in committed state(per backend deploy chain → Azure)。**Local dev sets to `True` ONLY in local working tree,never commits the flip。**

Manual check:
```bash
grep "Const_Run_in_local_environment" local_build_environment.py
# Expected output: Const_Run_in_local_environment = False
```

Future automation(F3.6 proposal):pre-commit lint hook auto-rejects commits where this line says `True`。

---

## § 3. Azure WebApp Log Audit

### 3.1 — How to verify current log retention(read-only)

```bash
# Show current log configuration
az webapp log show \
  --resource-group beautyreservation_group \
  --name liffbeauty \
  --output table
```

Look for:
- `applicationLogs.fileSystem.level`(verbose / information / warning / error / off)
- `applicationLogs.fileSystem.retentionInDays`(default 35)
- `httpLogs.fileSystem.retentionInDays`
- `httpLogs.azureBlobStorage.retentionInDays`(if blob forwarding enabled)

### 3.2 — How to tail live logs(troubleshooting)

```bash
az webapp log tail \
  --resource-group beautyreservation_group \
  --name liffbeauty
```

⚠ Captures stdout/stderr of running app — INFORMATION_SCHEMA query output may appear if schema_sync.py emits debug。Verify no PII leakage during troubleshooting sessions。

---

## § 4. Schema-Sync Audit Log Retention

See `azure-config.yaml` → `mysql.audit_log_retention` section(F4.1 added 2026-06-24)for `_schema_sync_log` MySQL table retention policy:**90 days OR > 10k rows,whichever first,daily cleanup cadence**。This applies ONLY to the MySQL audit table — NOT to Azure App Service application logs(those follow §3 retention)。

Source of truth in code:`schema_sync.py` AuditLogger class constants(`RETENTION_DAYS=90` / `RETENTION_ROW_MAX=10000` / `CLEANUP_INTERVAL_SEC=86400`)— azure-config.yaml mirrors these for ops visibility。

If constants in code change,update yaml + this runbook simultaneously。

---

## § 5. Emergency Procedures

### 5.1 — Suspected PROD data leak

1. **Stop** any running pytest / schema_sync session that might be hitting PROD
2. Verify by `tail /var/log/...` and `az webapp log tail`
3. Check `_schema_sync_log` for unexpected recent rows:
   ```sql
   SELECT * FROM _schema_sync_log
   WHERE created_at > NOW() - INTERVAL 1 HOUR
   ORDER BY created_at DESC;
   ```
4. Escalate to PO with timestamp + suspected source
5. If TEST_FAKE_* prefixed rows found in PROD → run cleanup_sanity_fake_data.sql analog adapted for PROD(with PO authorize)

### 5.2 — Suspected firewall rule misconfiguration

1. List current rules per §1.1
2. Compare against audit_trail in `azure-config.yaml`(when F3.2 lands)
3. Flag any unexpected rule to PO with: name / IP / when added / suspected source
4. Do NOT remove rule unilaterally — PO authorize required

### 5.3 — Const_Run_in_local_environment = True committed accidentally

If `git log -p local_build_environment.py` shows accidental commit of `= True`:
1. **Immediate:** Revert via new commit setting back to `False` + force-deploy if already in PROD
2. **Within 1 hour:** Verify Azure PROD WebApp logs for any local-pointing connect attempts since the bad commit
3. **Within 24 hours:** Post-mortem to PO with: how commit slipped past review,what test data wrote where,remediation

---

## § 6. Cross-references

- `azure-config.yaml` — current Azure infrastructure schema
- `docs/pm/backend-schema-auto-sync/reports/2026-06-24-f3-azure-mysql-firewall-review.md` — full F3 analysis
- `docs/pm/backend-schema-auto-sync/reports/2026-06-24-f4-audit-log-retention-review.md` — full F4 analysis
- `docs/pm/_org/org-decision-log.md` — D-backend-schema-auto-sync-phase-6-f3-* + f4-* entries
- `schema_sync.py:540-608` — AuditLogger class with retention constants
- `local_build_environment.py` — `Const_Run_in_local_environment` flag SSOT
- memory `[[backend_change_rule]]` — propose-first discipline for any *.py change
- memory `[[backend_schema_change_workflow]]` — schema SSOT enforcement
- memory `[[azure_webapp_runtime]]` — Microsoft Azure Linux 3.0 constraints
- memory `[[dep_management]]` — pip dep authorize hard rule

---

(End of Ops Runbook v1.0)
