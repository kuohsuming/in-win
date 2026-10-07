-- =============================================================================
-- in-win 表面平整檢查系統 — 資料庫與資料表建立腳本
--
-- 用途：在新的量測 PC（或開發機）上建立整套資料庫、App 帳號與資料表。
-- 依據：Downloads/表面平整檢查系統_需求規格書.md
--       INS-05、3.0.6、3.0.8、DAT-02～DAT-04、DAT-06、DEF-08、DEF-09、SIM-15、5.2、3.10（lan_device）
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
  device_mac         CHAR(17)              NULL COMMENT '量測當時該排 DL-EN1 的 MAC（DAT-06）',
  PRIMARY KEY (serial, device_key, probe_id),
  CONSTRAINT fk_point_inspection
    FOREIGN KEY (serial) REFERENCES flatness.inspection (serial)
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
  COMMENT='量測明細';

-- 舊版已建立的明細表補上 device_mac（DAT-06；可重複執行）
SET @col_missing := (
  SELECT COUNT(*) = 0 FROM information_schema.COLUMNS
  WHERE TABLE_SCHEMA = 'flatness' AND TABLE_NAME = 'inspection_point' AND COLUMN_NAME = 'device_mac'
);
SET @sql := IF(@col_missing,
  'ALTER TABLE flatness.inspection_point ADD COLUMN device_mac CHAR(17) NULL COMMENT ''量測當時該排 DL-EN1 的 MAC（DAT-06）'' AFTER error_text',
  'DO 0');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 設備網路探索與 DL-EN1 設定（3.10 DSC；DL-EN1 設定的主檔，DEF-01）
-- 每個 MAC 一筆；App 帳號沒有 DELETE 權限，設備只會新增或更新
CREATE TABLE IF NOT EXISTS flatness.lan_device (
  mac            CHAR(17)          NOT NULL COMMENT 'XX:XX:XX:XX:XX:XX，統一大寫（DSC-01）',
  status         ENUM('unclassified','dl_en1_live','dl_en1_maint','dl_en1_retired','not_dl_en1')
                                   NOT NULL DEFAULT 'unclassified'
                                   COMMENT '不明設備／DL-EN1 使用中／維修中／已停用／其他設備',
  first_seen     DATETIME(3)           NULL COMMENT '首次收到請求的時間；匯入建立、尚未出現過者為 NULL',
  last_seen      DATETIME(3)           NULL COMMENT '最後一次收到請求的時間',
  seen_count     INT UNSIGNED      NOT NULL DEFAULT 0 COMMENT '請求封包數，每個 BOOTP／DHCP 請求或 ARP 位址偵測封包加 1',
  last_request   ENUM('BOOTP','DHCP','ARP') NULL COMMENT '最後一次請求的類型（ARP：位址偵測封包，DSC-19）',
  hostname       VARCHAR(64)           NULL COMMENT 'DHCP option 12 主機名稱',
  vendor_class   VARCHAR(64)           NULL COMMENT 'DHCP option 60 廠商識別',
  seen_ip        VARCHAR(15)           NULL COMMENT '設備實際使用的 IP（ARP 位址偵測封包，DSC-19）',
  ipv4           VARCHAR(15)           NULL COMMENT '配發的 IP；DL-EN1 使用中與維修中必填，其他設備可留空',
  dl_en1_config  JSON                  NULL COMMENT 'DL-EN1 設定（3.7.1 去除 mac、ipv4；DSC-12）',
  sort_order     SMALLINT UNSIGNED     NULL COMMENT '主畫面由上而下的順序',
  hidden         TINYINT(1)        NOT NULL DEFAULT 0 COMMENT '清單中隱藏（DSC-13）',
  hidden_at      DATETIME(3)           NULL COMMENT '隱藏時間',
  updated_at     DATETIME(3)       NOT NULL DEFAULT CURRENT_TIMESTAMP(3) COMMENT '狀態或設定最後修改時間',
  PRIMARY KEY (mac),
  KEY idx_lan_device_status (status)
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
  COMMENT='設備網路探索與 DL-EN1 設定';

-- 舊版已建立的 lan_device：請求類型加入 ARP、補上 seen_ip（DSC-19；可重複執行）
ALTER TABLE flatness.lan_device
  MODIFY last_request ENUM('BOOTP','DHCP','ARP') NULL COMMENT '最後一次請求的類型（ARP：位址偵測封包，DSC-19）',
  MODIFY seen_count INT UNSIGNED NOT NULL DEFAULT 0 COMMENT '請求封包數，每個 BOOTP／DHCP 請求或 ARP 位址偵測封包加 1';
SET @col_missing := (
  SELECT COUNT(*) = 0 FROM information_schema.COLUMNS
  WHERE TABLE_SCHEMA = 'flatness' AND TABLE_NAME = 'lan_device' AND COLUMN_NAME = 'seen_ip'
);
SET @sql := IF(@col_missing,
  'ALTER TABLE flatness.lan_device ADD COLUMN seen_ip VARCHAR(15) NULL COMMENT ''設備實際使用的 IP（ARP 位址偵測封包，DSC-19）'' AFTER vendor_class',
  'DO 0');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- -----------------------------------------------------------------------------
-- 3. 資料表（模擬資料庫，結構與正式相同；模擬模式不探索，不建 lan_device，3.10）
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

-- 舊版已建立的模擬明細表補上 device_mac
SET @col_missing := (
  SELECT COUNT(*) = 0 FROM information_schema.COLUMNS
  WHERE TABLE_SCHEMA = 'flatness_sim' AND TABLE_NAME = 'inspection_point' AND COLUMN_NAME = 'device_mac'
);
SET @sql := IF(@col_missing,
  'ALTER TABLE flatness_sim.inspection_point ADD COLUMN device_mac CHAR(17) NULL AFTER error_text',
  'DO 0');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- -----------------------------------------------------------------------------
-- 4. App 帳號（INS-05）
--    只能從本機連線；SELECT、INSERT、UPDATE；另只對 lan_device 有 DELETE（設定頁「刪除」DSC-18），
--    量測紀錄（inspection、inspection_point）與資料表本身無法刪除
-- -----------------------------------------------------------------------------
CREATE USER IF NOT EXISTS 'flatness_app'@'localhost' IDENTIFIED BY RANDOM PASSWORD;

GRANT SELECT, INSERT, UPDATE ON flatness.*     TO 'flatness_app'@'localhost';
GRANT SELECT, INSERT, UPDATE ON flatness_sim.* TO 'flatness_app'@'localhost';
GRANT DELETE ON flatness.lan_device TO 'flatness_app'@'localhost';
