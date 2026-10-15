"""探頭位置（3.13 POS-01～POS-03、POS-08～POS-11）：規則、兩層檢查、名稱的存放與套用。"""

import json
import tempfile
import unittest
from pathlib import Path

from helpers import NET, by_mac, sample_devices

from flatness import bootp, definition, lan, positions, sync
from flatness.lan import MAINT, RETIRED
from flatness.positions import Names
from flatness.store import MemoryStore, StoreError

DEV_A, DEV_B, DEV_C, OLD = "00:01:FC:DE:3A:75", "00:01:FC:DE:3A:76", "00:01:FC:DE:3A:77", "00:01:FC:DE:3A:70"


def place(devs, mac, idx, row, point):
    positions.set_pos(by_mac(devs)[mac].config["probes"][idx], row, point)


def defn_of(devs, names=None):
    return lan.definition_from(devs, names)


class RulesTest(unittest.TestCase):
    def test_defaults(self):  # POS-09
        n = Names.default()
        self.assertEqual(n.rows, ("排1", "排2", "排3", "排4", "排5"))
        self.assertEqual(n.points, ("點1", "點2", "點3", "點4", "點5"))
        self.assertEqual(Names.from_json(None), n)
        self.assertEqual(Names.from_json({"rows": ["a"] * 5, "points": list(n.points)}), n)  # 重複 → 預設

    def test_name_errors(self):  # POS-03
        self.assertEqual(positions.name_errors("rows", ["前排", "", "前排", "x" * 11, "後排"]),
                         [(1, "不可空白"), (2, "與第 1 個重複"), (3, "最多 10 字")])

    def test_probe_errors(self):  # POS-01、POS-08
        self.assertEqual(positions.probe_errors({}), [])
        self.assertEqual(positions.probe_errors({"row": 2}), [("point", "排與點須同時設定或同時省略")])
        self.assertEqual(positions.probe_errors({"row": 6, "point": 1}), [("row", "須為 1～5 的整數")])
        self.assertIsNone(positions.pos({"row": 2}))
        self.assertEqual(positions.pos({"row": 2, "point": 3}), (2, 3))
        p = {"row": 1, "point": 1}
        positions.set_pos(p, None, None)
        self.assertEqual(p, {})

    def test_auto_description(self):  # POS-09
        n = Names.default()
        auto = positions.auto_description
        self.assertEqual(auto("探頭 3", None, 2, n), "點2")       # 新增探頭的預設名稱
        self.assertEqual(auto("探頭 7", None, 2, n), "點2")       # ID 重排後的預設名稱也算
        self.assertEqual(auto("點2", 2, 3, n), "點3")             # 等於原本所選點的名稱
        self.assertEqual(auto("", 2, 3, n), "點3")                # 被清空
        self.assertEqual(auto("左邊", 2, 3, n), "左邊")           # 自己取的名稱不覆蓋
        self.assertEqual(auto("點2", 2, None, n), "點2")          # 改回未定：不變
        renamed = Names(n.rows, ("左", "左中", "中", "右中", "右"))
        self.assertEqual(auto("點2", 2, 3, renamed), "中")        # 點名稱改過，舊的預設名稱仍算自動帶入
        self.assertEqual(auto("左中", 2, 5, renamed), "右")

    def test_names_for_people(self):  # PROPOSAL §5.2
        n = Names(("前排", "排2", "排3", "排4", "排5"), positions.DEFAULT_POINTS)
        self.assertEqual(positions.display_name(n, (1, 2), "row-2", "中排", "點2"), "前排 點2")
        self.assertEqual(positions.display_name(n, None, "row-2", "中排", "探頭 3"), "第 2 台 中排 探頭 3")
        self.assertEqual(positions.device_call("row-2", "中排", "點2"), "第 2 台 中排 點2")
        self.assertEqual(positions.disambiguate([("前排 左", "row-1", 1), ("前排 左", "row-2", 3), ("前排 右", "row-1", 2)]),
                         ["前排 左（第 1 台 探頭 1）", "前排 左（第 2 台 探頭 3）", "前排 右"])

    def test_default_config_probe_names(self):  # POS-09：第一次設為 DL-EN1 時為「探頭 1」～「探頭 4」、位置未定
        cfg = lan.default_config()
        self.assertEqual([p["description"] for p in cfg["probes"]], ["探頭 1", "探頭 2", "探頭 3", "探頭 4"])
        self.assertTrue(all(positions.pos(p) is None for p in cfg["probes"]))


class DefinitionFileTest(unittest.TestCase):
    """單台／定義檔層（bootp.validate 與 JSON Schema）。"""

    def check(self, defn):
        return definition.validate(defn, NET)

    def test_valid_with_positions_and_names(self):
        devs = sample_devices()
        place(devs, DEV_A, 0, 1, 2)
        place(devs, DEV_B, 0, 3, 1)
        d = defn_of(devs, Names(("前排", "排2", "中排", "排4", "後排"), positions.DEFAULT_POINTS))
        self.assertEqual(self.check(d), [])
        self.assertEqual(d["position_names"]["rows"][0], "前排")

    def test_only_row_rejected(self):  # POS-08
        devs = sample_devices()
        by_mac(devs)[DEV_A].config["probes"][0]["row"] = 1
        errs = self.check(defn_of(devs))
        self.assertIn(("dl_en1[0].probes[0].point", "排與點須同時設定或同時省略"), errs)

    def test_out_of_range_rejected(self):  # POS-08
        devs = sample_devices()
        place(devs, DEV_A, 0, 6, 1)
        self.assertIn(("dl_en1[0].probes[0].row", "須為 1～5 的整數"), self.check(defn_of(devs)))

    def test_duplicate_in_file_rejected(self):  # POS-02：上傳的定義檔，同一台內與各台之間
        devs = sample_devices()
        place(devs, DEV_A, 0, 1, 1)
        place(devs, DEV_A, 1, 1, 1)
        place(devs, DEV_B, 0, 2, 2)
        place(devs, DEV_C, 0, 2, 2)
        errs = self.check(defn_of(devs))
        self.assertEqual(sum("重複" in why for _, why in errs), 2)

    def test_bad_names_rejected(self):  # POS-03
        d = defn_of(sample_devices())
        d["position_names"]["points"][1] = "點1"
        errs = self.check(d)
        self.assertIn(("position_names.points[1]", "與第 1 個重複"), errs)
        d["position_names"] = {"rows": ["排1"]}
        self.assertTrue(self.check(d))

    def test_schema_agrees(self):  # 3.7.1 JSON Schema 也接受同一份
        import jsonschema
        schema = json.loads(definition.SCHEMA_PATH.read_text(encoding="utf-8"))
        devs = sample_devices()
        place(devs, DEV_A, 0, 1, 2)
        jsonschema.validate(defn_of(devs), schema)
        bad = defn_of(devs)
        del bad["dl_en1"][0]["probes"][0]["point"]
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(bad, schema)


class GridTest(unittest.TestCase):
    """板子版面（POS-10、POS-11）：定義檔、設定頁檢查、預覽、存放。"""

    def test_default_and_json(self):
        g = Names.default()
        self.assertEqual((g.grid_rows, g.grid_points), (5, 5))
        self.assertEqual(Names.from_definition({}).grid_json(), {"rows": 5, "points": 5})
        got = Names.from_definition({"position_grid": {"rows": 2, "points": 3}})
        self.assertEqual((got.grid_rows, got.grid_points, got.rows), (2, 3, positions.DEFAULT_ROWS))
        self.assertEqual(Names.from_definition({"position_grid": {"rows": 6, "points": 3}}).grid_rows, 5)
        self.assertEqual(g.with_grid(2, 3).grid_text(), "2 排 × 3 點")

    def test_definition_carries_grid(self):
        names = Names().with_grid(3, 4)
        self.assertEqual(lan.definition_from(sample_devices(), names)["position_grid"], {"rows": 3, "points": 4})
        self.assertEqual(lan.screen_layout(sample_devices(), names)["position_grid"], {"rows": 3, "points": 4})

    def test_file_probe_outside_grid_rejected(self):  # POS-11
        devs = sample_devices()
        place(devs, DEV_A, 0, 4, 1)
        place(devs, DEV_A, 1, 1, 5)
        errs = definition.validate(defn_of(devs, Names().with_grid(3, 4)), NET)
        self.assertIn(("dl_en1[0].probes[0].row", "第 4 排超出版面 3 排"), errs)
        self.assertIn(("dl_en1[0].probes[1].row", "第 5 點超出版面每排 4 點"), errs)
        self.assertEqual(definition.validate(defn_of(devs), NET), [])  # 沒有版面限制（5 × 5）時合格

    def test_bad_grid_rejected_and_schema(self):
        import jsonschema
        schema = json.loads(definition.SCHEMA_PATH.read_text(encoding="utf-8"))
        d = defn_of(sample_devices(), Names().with_grid(2, 3))
        jsonschema.validate(d, schema)
        d["position_grid"] = {"rows": 0, "points": 3, "x": 1}
        errs = definition.validate(d, NET)
        self.assertIn(("position_grid.rows", "須為 1～5 的整數"), errs)
        self.assertIn(("position_grid.x", "不允許的欄位"), errs)
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(d, schema)

    def test_settings_check_outside_grid(self):  # POS-11：使用中、維修中檢查；已停用不檢查
        devs = sample_devices()
        place(devs, DEV_A, 1, 4, 1)
        place(devs, OLD, 0, 5, 5)
        msgs = [(i.mac, i.message) for i in lan.validate(devs, NET, Names().with_grid(3, 5))]
        self.assertEqual(msgs, [(DEV_A, "第 2 列（ID 2）第 4 排超出版面 3 排")])

    def test_preview_lists_grid_and_unset(self):  # POS-11：預覽列出版面變更與改為未定的探頭
        old = sample_devices()
        place(old, DEV_A, 2, 4, 2)
        new = [d.copy() for d in old]
        positions.set_pos(by_mac(new)[DEV_A].config["probes"][2], None, None)
        p = lan.diff(old, new, old_names=Names(), new_names=Names().with_grid(3, 5))
        lines = [t for item in p.items for t, _ in item.lines]
        self.assertIn("板子版面：5 排 × 5 點 → 3 排 × 5 點", lines)
        self.assertTrue(any("位置：排4 點2 → 未定" in t for t in lines), lines)

    def test_grid_saved_and_from_file_when_db_down(self):  # POS-10：存資料庫，資料庫無法連線時取自定義檔
        with tempfile.TemporaryDirectory() as tmp:
            files = sync.Files(Path(tmp) / "dl-en1.json", Path(tmp) / "dl-en1.hosts")
            store = MemoryStore(sample_devices())
            sync.startup(store, files, NET)
            devs = store.load()
            sync.apply(store, files, NET, devs, [d.copy() for d in devs], names=Names().with_grid(2, 3))
            self.assertEqual(store.load_names().grid_json(), {"rows": 2, "points": 3})
            store.available = False
            r = sync.startup(store, files, NET)
            self.assertEqual(r.names.grid_json(), {"rows": 2, "points": 3})

    def test_initdb_imports_grid(self):  # DEF-10
        from flatness import initdb
        store = MemoryStore()
        initdb.import_if_empty(store, defn_of(sample_devices(), Names().with_grid(4, 4)))
        self.assertEqual(store.load_names().grid_json(), {"rows": 4, "points": 4})

class EnabledTest(unittest.TestCase):
    """探頭啟用（PDT-02、PDT-03）：欄位、定義檔、設定頁檢查、預覽。"""

    def test_helpers(self):
        p = {"id": 1, "description": "左", "row": 1, "point": 2}
        self.assertTrue(positions.is_enabled(p))
        positions.set_enabled(p, False)
        self.assertEqual(p, {"id": 1, "description": "左", "enabled": False})   # 位置改為未定
        positions.set_enabled(p, True)
        self.assertEqual(p, {"id": 1, "description": "左"})                     # 啟用不寫入欄位

    def test_definition_rules_and_schema(self):
        import jsonschema
        schema = json.loads(definition.SCHEMA_PATH.read_text(encoding="utf-8"))
        devs = sample_devices()
        positions.set_enabled(by_mac(devs)[DEV_A].config["probes"][1], False)
        d = defn_of(devs)
        self.assertEqual(definition.validate(d, NET), [])
        jsonschema.validate(d, schema)
        d["dl_en1"][0]["probes"][1].update(row=1, point=1)
        self.assertIn(("dl_en1[0].probes[1].row", "未啟用的探頭不可設定位置"), definition.validate(d, NET))
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(d, schema)
        d["dl_en1"][0]["probes"][1] = {"id": 2, "description": "x", "enabled": "no"}
        self.assertIn(("dl_en1[0].probes[1].enabled", "須為 true 或 false"), definition.validate(d, NET))

    def test_settings_message_and_preview(self):
        old = sample_devices()
        place(old, DEV_A, 1, 1, 2)
        new = [x.copy() for x in old]
        p = by_mac(new)[DEV_A].config["probes"][1]
        positions.set_enabled(p, False)
        self.assertFalse([i for i in lan.validate(new, NET) if i.mac == DEV_A])
        lines = [t for item in lan.diff(old, new).items for t, _ in item.lines]
        self.assertTrue(any("（ID 2）啟用：是 → 否" in t for t in lines), lines)
        self.assertTrue(any("（ID 2）位置：排1 點2 → 未定" in t for t in lines), lines)
        p.update(row=1, point=3)
        msgs = [i.message for i in lan.validate(new, NET) if i.mac == DEV_A]
        self.assertEqual(msgs, ["第 2 列（ID 2）未啟用的探頭不可設定位置"])

class SettingsCheckTest(unittest.TestCase):
    """設定頁全體層（lan.validate）：使用中＋維修中的位置不可重複（POS-02）。"""

    def test_live_and_maint_conflict(self):
        devs = sample_devices()
        by_mac(devs)[DEV_B].status = MAINT
        place(devs, DEV_A, 2, 1, 3)
        place(devs, DEV_B, 0, 1, 3)
        issues = [i for i in lan.validate(devs, NET) if "已由" in i.message]
        self.assertEqual({i.mac for i in issues}, {DEV_A, DEV_B})
        a = next(i for i in issues if i.mac == DEV_A)
        self.assertEqual(a.message, "第 3 列（ID 3）排1 點3 已由 第 2 台 中排 左 使用")

    def test_retired_does_not_occupy(self):  # DSC-09
        devs = sample_devices()
        place(devs, OLD, 0, 1, 3)
        place(devs, DEV_A, 0, 1, 3)
        self.assertFalse([i for i in lan.validate(devs, NET) if "已由" in i.message])

    def test_incomplete_message(self):  # POS-01
        devs = sample_devices()
        by_mac(devs)[DEV_A].config["probes"][1]["row"] = 2
        msgs = [i.message for i in lan.validate(devs, NET) if i.mac == DEV_A]
        self.assertEqual(msgs, ["第 2 列（ID 2）位置須同時設定排與點，或都設為未定"])

    def test_names_used_in_message(self):
        devs = sample_devices()
        place(devs, DEV_A, 0, 2, 4)
        place(devs, DEV_B, 0, 2, 4)
        names = Names(("排1", "中間", "排3", "排4", "排5"), positions.DEFAULT_POINTS)
        msgs = [i.message for i in lan.validate(devs, NET, names) if i.mac == DEV_A]
        self.assertEqual(msgs, ["第 1 列（ID 1）中間 點4 已由 第 2 台 中排 左 使用"])

    def test_replace_carries_positions(self):  # DSC-14：新機接手舊機的探頭位置
        devs = sample_devices()
        place(devs, DEV_A, 0, 1, 2)
        new = lan.replace(devs, DEV_A, "00:01:FC:12:39:A0")
        self.assertEqual(positions.pos(new.config["probes"][0]), (1, 2))
        self.assertFalse([i for i in lan.validate(devs, NET) if "已由" in i.message])

    def test_reactivate_conflict(self):  # DSC-09：已停用改回使用中，原位置已被使用
        devs = sample_devices()
        place(devs, OLD, 0, 1, 3)
        place(devs, DEV_A, 0, 1, 3)
        lan.set_status(devs, OLD, lan.LIVE, NET)
        self.assertTrue([i for i in lan.validate(devs, NET) if i.mac == OLD and "已由" in i.message])

    def test_layout_and_definition_carry_names(self):
        names = Names(("前排", "排2", "排3", "排4", "排5"), positions.DEFAULT_POINTS)
        self.assertEqual(lan.screen_layout(sample_devices(), names)["position_names"], names.to_json())
        self.assertEqual(lan.definition_from(sample_devices())["position_names"], Names.default().to_json())


class NamesStorageTest(unittest.TestCase):
    """名稱存放：資料庫為主檔、定義檔帶一份；與設備設定同一交易（POS-03）。"""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        base = Path(self.tmp.name)
        self.files = sync.Files(base / "etc" / "dl-en1.json", base / "bootp" / "dl-en1.hosts")
        self.store = MemoryStore(sample_devices())
        self.named = Names(("前排", "排2", "排3", "排4", "後排"), positions.DEFAULT_POINTS)

    def tearDown(self):
        self.tmp.cleanup()

    def defn(self):
        return json.loads(self.files.def_path.read_text(encoding="utf-8"))

    def test_startup_defaults(self):
        r = sync.startup(self.store, self.files, NET)
        self.assertEqual(r.names, Names.default())
        self.assertEqual(self.defn()["position_names"], Names.default().to_json())

    def test_only_names_saved(self):  # 只改名稱也可以儲存
        sync.startup(self.store, self.files, NET)
        devs = self.store.load()
        r = sync.apply(self.store, self.files, NET, devs, [d.copy() for d in devs], names=self.named)
        self.assertEqual(r.names, self.named)
        self.assertEqual(self.store.load_names(), self.named)
        self.assertEqual(self.defn()["position_names"]["rows"][0], "前排")
        self.assertEqual(r.layout["position_names"]["rows"][4], "後排")

    def test_other_save_keeps_names(self):  # 校準、刪除、上移／下移等立即儲存（names=None）保留自訂名稱
        sync.startup(self.store, self.files, NET)
        devs = self.store.load()
        sync.apply(self.store, self.files, NET, devs, [d.copy() for d in devs], names=self.named)
        old = self.store.load()
        new = [d.copy() for d in old]
        by_mac(new)[DEV_A].config["probes"][0]["description"] = "改名"
        sync.apply(self.store, self.files, NET, old, new)
        self.assertEqual(self.defn()["position_names"]["rows"][0], "前排")
        self.assertEqual(self.store.load_names(), self.named)

    def test_failed_apply_restores_names(self):  # UPL-08：失敗時名稱與設備一起還原
        sync.startup(self.store, self.files, NET)
        devs = self.store.load()

        def boom():
            raise RuntimeError("dnsmasq 失敗")
        new = [d.copy() for d in devs]
        by_mac(new)[DEV_A].ipv4 = "192.168.10.30"
        with self.assertRaises(RuntimeError):
            sync.apply(self.store, self.files, NET, devs, new, restart=boom, names=self.named)
        self.assertEqual(self.store.load_names(), Names.default())
        self.assertEqual(self.defn()["position_names"], Names.default().to_json())

    def test_db_down_uses_definition_file(self):  # DSC-06：資料庫無法連線時名稱取自定義檔
        sync.startup(self.store, self.files, NET)
        devs = self.store.load()
        sync.apply(self.store, self.files, NET, devs, [d.copy() for d in devs], names=self.named)
        self.store.available = False
        r = sync.startup(self.store, self.files, NET)
        self.assertFalse(r.db_ok)
        self.assertEqual(r.names, self.named)

    def test_startup_conflict_keeps_files(self):  # 資料庫中的位置衝突：沿用上次的設定（DSC-06-A3）
        sync.startup(self.store, self.files, NET)
        devs = self.store.load()
        new = [d.copy() for d in devs]
        place(new, DEV_A, 0, 1, 1)
        place(new, DEV_B, 0, 1, 1)
        with self.store.transaction() as tx:
            tx.save(devs, new)
        r = sync.startup(self.store, self.files, NET)
        self.assertIn("設備設定有錯誤", r.problem)

    def test_initdb_imports_names(self):  # DEF-10
        from flatness import initdb
        store = MemoryStore()
        d = defn_of(sample_devices(), self.named)
        self.assertEqual(initdb.import_if_empty(store, d), 3)
        self.assertEqual(store.load_names(), self.named)

    def test_store_unavailable(self):
        self.store.available = False
        with self.assertRaises(StoreError):
            self.store.load_names()


if __name__ == "__main__":
    unittest.main()


from test_store import _dev_env  # noqa: E402


@unittest.skipIf(_dev_env() is None, "開發用 MySQL 未啟動（./scripts/dev-mysql.sh start）")
class MySQLNamesTest(unittest.TestCase):
    def setUp(self):
        from flatness.store import MySQLStore
        env, root = _dev_env()
        with root.cursor() as cur:
            cur.execute("CREATE DATABASE IF NOT EXISTS flatness_test")
            cur.execute("DROP TABLE IF EXISTS flatness_test.plate_position_name")
            cur.execute("DROP TABLE IF EXISTS flatness_test.plate_layout")
            cur.execute("DROP TABLE IF EXISTS flatness_test.inspection_point")
            cur.execute("DROP TABLE IF EXISTS flatness_test.inspection")
            cur.execute("CREATE TABLE flatness_test.inspection LIKE flatness.inspection")
            cur.execute("CREATE TABLE flatness_test.inspection_point LIKE flatness.inspection_point")
            cur.execute("GRANT SELECT, INSERT, UPDATE ON flatness_test.* TO 'flatness_app'@'localhost'")
        self.root = root
        self.addCleanup(root.close)
        self.store = MySQLStore(database="flatness_test", user=env["DB_USER"], password=env["DB_PASS"],
                                unix_socket=env["DB_SOCKET"])

    def test_missing_table_gives_defaults(self):  # 升級後尚未執行 sql/in-win.sql（MySQL 1146）
        with self.assertLogs("flatness.store", "WARNING"):
            self.assertEqual(self.store.load_names(), Names.default())

    def test_layout_table_missing_gives_5x5(self):  # POS-10：plate_layout 尚未建立 → 5 × 5，名稱照常
        with self.root.cursor() as cur:
            cur.execute("CREATE TABLE flatness_test.plate_position_name LIKE flatness.plate_position_name")
        with self.assertLogs("flatness.store", "WARNING") as cm:
            got = self.store.load_names()
        self.assertEqual((got.grid_rows, got.grid_points), (5, 5))
        self.assertIn("plate_layout", cm.output[0])

    def test_save_without_layout_table_explains(self):  # 升級後尚未執行 sql/in-win.sql：白話說明處理方式
        with self.root.cursor() as cur:
            cur.execute("CREATE TABLE flatness_test.plate_position_name LIKE flatness.plate_position_name")
        with self.assertRaises(StoreError) as cm:
            with self.store.transaction() as tx:
                tx.save_names(Names().with_grid(3, 3))
        self.assertIn("資料庫還沒有升級（缺少資料表 plate_layout）", str(cm.exception))
        self.assertIn("sudo mysql < sql/in-win.sql", str(cm.exception))

    def test_save_and_load(self):  # POS-03
        with self.root.cursor() as cur:
            cur.execute("CREATE TABLE flatness_test.plate_position_name LIKE flatness.plate_position_name")
            cur.execute("CREATE TABLE flatness_test.plate_layout LIKE flatness.plate_layout")
        self.assertEqual(self.store.load_names(), Names.default())
        named = Names(("前排", "排2", "排3", "排4", "後排"), ("左", "點2", "中", "點4", "右"), 2, 3)  # POS-10
        with self.store.transaction() as tx:
            tx.save_names(named)
        self.assertEqual(self.store.load_names(), named)
        with self.assertRaises(RuntimeError):  # 交易中失敗 → 不寫入
            with self.store.transaction() as tx:
                tx.save_names(Names.default())
                raise RuntimeError("x")
        self.assertEqual(self.store.load_names(), named)

    def test_inspection_keeps_position(self):  # POS-08：量測紀錄保存當時的排、點與排名稱
        from datetime import datetime
        t = datetime(2026, 10, 15, 9, 0, 0)
        head = {"serial": "20261015090000000", "station_id": "ST01", "measured_at": t, "judgment": "PASS",
                "reread_count": 0}
        base = {"device_key": "row-1", "device_name": "前排", "measured_value": 0.01, "standard_value": 0.0,
                "lower_limit": -0.5, "upper_limit": 0.5, "judgment": "OK", "raw_response": "+000000100",
                "error_text": None, "device_mac": DEV_A, "zero_offset": None}
        pts = [dict(base, probe_id=1, probe_description="點2", pos_row=1, pos_point=2, row_name="前排"),
               dict(base, probe_id=2, probe_description="探頭 2")]           # 未定、舊格式暫存檔沒有這三欄
        self.assertTrue(self.store.write_inspection(head, pts))
        (got,) = self.store.read_inspections(t.date())
        self.assertEqual([(p["pos_row"], p["pos_point"], p["row_name"]) for p in got["points"]],
                         [(1, 2, "前排"), (None, None, None)])
