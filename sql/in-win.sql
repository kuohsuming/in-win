-- =============================================================================
-- in-win 表面平整檢查系統 — 資料庫與資料表建立腳本
--
-- 用途：在新的量測 PC（或開發機）上建立整套資料庫、App 帳號與資料表。
-- 依據：Downloads/表面平整檢查系統_需求規格書.md
--       INS-05、3.0.6、3.0.8、DAT-02～DAT-04、DEF-08、DEF-09、SIM-15、5.2
--
-- 執行方式（MySQL root 以作業系統帳號驗證，不需密碼）：
--     sudo mysql < sql/in-win.sql
--
-- 可重複執行（3.0.8）：資料庫、帳號、資料表已存在則略過，不刪除、不變更任何資料。
--
-- App 帳號密碼（INS-05「密碼自動產生」）：
--     首次執行時由 MySQL 隨機產生，並在輸出中顯示「generated password」一次。
--     請立即寫入 /etc/flatness/db.env（root 擁有，App 帳號可讀，其他人不可讀）。
--     帳號已存在時不會重新產生密碼。
--
-- ⚠️ 欄位為依需求規格書推導；需求規格書所參照的「功能規格：資料寫入規則與資料表設計」
--    尚未納入 repo，取得後須逐欄核對本檔。
-- =============================================================================

-- -----------------------------------------------------------------------------
-- 1. 資料庫
--    flatness     ：正式量測紀錄
--    flatness_sim ：模擬模式專用（SIM-15），不得與正式資料混用
-- -----------------------------------------------------------------------------
CREATE DATABASE IF NOT EXISTS flatness
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_0900_ai_ci;

CREATE DATABASE IF NOT EXISTS flatness_sim
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_0900_ai_ci;

-- -----------------------------------------------------------------------------
-- 2. 資料表（正式資料庫）
-- -----------------------------------------------------------------------------

-- 主檔：每片 1 筆（DAT-02）
CREATE TABLE IF NOT EXISTS flatness.inspection (
  serial        CHAR(17)      NOT NULL COMMENT '編號 YYYYMMDDHHmmssSSS（DAT-01），主鍵（5.2）',
  station_id    VARCHAR(16)   NOT NULL COMMENT '工站代號，來自 site.conf STATION_ID',
  measured_at   DATETIME(3)   NOT NULL COMMENT '量測時間：畫面上最後一次讀取的時間',
  written_at    DATETIME(3)   NOT NULL COMMENT '寫入時間：實際寫入資料庫的時間（斷線補寫時晚於量測時間）',
  judgment      ENUM('PASS','FAIL','ERROR') NOT NULL COMMENT '整片結果；ERROR = 設備異常（JDG-04）',
  reread_count  SMALLINT UNSIGNED NOT NULL DEFAULT 0 COMMENT '重讀次數（MEA-05、MEA-06）',
  PRIMARY KEY (serial),
  KEY idx_inspection_measured_at (measured_at) COMMENT '依日期取出測試數據（EXP-01）'
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
  COMMENT='量測主檔';

-- 明細：每片每個已安裝探頭 1 筆（DAT-02、DEF-05、DEF-08）
CREATE TABLE IF NOT EXISTS flatness.inspection_point (
  serial             CHAR(17)          NOT NULL COMMENT '對應 inspection.serial',
  device_key         VARCHAR(30)       NOT NULL COMMENT 'DL-EN1 key（定義檔），取代原 row_no',
  probe_id           TINYINT UNSIGNED  NOT NULL COMMENT '探頭 id = 放大器 ID（1～15），取代原 pos_no',
  device_name        VARCHAR(10)       NOT NULL COMMENT '當時的排名稱（DEF-08）',
  probe_description  VARCHAR(10)       NOT NULL COMMENT '當時的位置名稱（DEF-08）',
  measured_value     DECIMAL(12,6)         NULL COMMENT '測量值（mm，完整精度 JDG-03）；無有效數據時為 NULL',
  standard_value     DECIMAL(12,6)         NULL COMMENT '當時的標準值（DAT-03）；未設定允收標準時為 NULL（DEF-09）',
  lower_limit        DECIMAL(12,6)         NULL COMMENT '當時的下限（DAT-03）',
  upper_limit        DECIMAL(12,6)         NULL COMMENT '當時的上限（DAT-03）',
  judgment           ENUM('OK','HIGH','LOW','ERROR') NOT NULL COMMENT '單點判定：合格／偏高／偏低／設備異常（JDG-01、JDG-04）',
  raw_response       VARCHAR(64)           NULL COMMENT 'DL-EN1 原始回傳字串（DAT-03）',
  error_text         VARCHAR(255)          NULL COMMENT '設備異常原因（3.0.6）',
  PRIMARY KEY (serial, device_key, probe_id),
  CONSTRAINT fk_point_inspection
    FOREIGN KEY (serial) REFERENCES flatness.inspection (serial)
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
  COMMENT='量測明細';

-- -----------------------------------------------------------------------------
-- 3. 資料表（模擬資料庫，結構與正式相同）
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS flatness_sim.inspection       LIKE flatness.inspection;
CREATE TABLE IF NOT EXISTS flatness_sim.inspection_point LIKE flatness.inspection_point;

-- CREATE TABLE ... LIKE 不複製外鍵，補上（僅在不存在時加入，可重複執行）
SET @fk_missing := (
  SELECT COUNT(*) = 0
  FROM information_schema.TABLE_CONSTRAINTS
  WHERE CONSTRAINT_SCHEMA = 'flatness_sim'
    AND TABLE_NAME = 'inspection_point'
    AND CONSTRAINT_NAME = 'fk_sim_point_inspection'
);
SET @sql := IF(@fk_missing,
  'ALTER TABLE flatness_sim.inspection_point
     ADD CONSTRAINT fk_sim_point_inspection
     FOREIGN KEY (serial) REFERENCES flatness_sim.inspection (serial)',
  'DO 0');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- -----------------------------------------------------------------------------
-- 4. App 帳號（INS-05）
--    只能從本機連線；只有 SELECT、INSERT、UPDATE，無法刪除資料或資料表
-- -----------------------------------------------------------------------------
CREATE USER IF NOT EXISTS 'flatness_app'@'localhost' IDENTIFIED BY RANDOM PASSWORD;

GRANT SELECT, INSERT, UPDATE ON flatness.*     TO 'flatness_app'@'localhost';
GRANT SELECT, INSERT, UPDATE ON flatness_sim.* TO 'flatness_app'@'localhost';
