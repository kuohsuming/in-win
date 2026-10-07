"""產生操作說明書（docs/manual）的畫面截圖：示範資料、不連線真機、不寫資料庫。

執行：QT_QPA_PLATFORM=offscreen .venv/bin/python scripts/manual-shots.py
"""
import sys, time
from pathlib import Path
sys.path[:0] = ["app", "tests"]
import test_ui
from test_ui import pump
from helpers import sample_devices, by_mac
OUT = Path("docs/manual/images")

class Shots(test_ui.UiBase):
    def runTest(self):
        from flatness import lan, measure
        from flatness.ui.main_window import MainWindow, ExportDialog
        from flatness.ui.settings_dialog import SettingsDialog
        devs = sample_devices()
        for d in devs:
            if d.is_dl_en1 and d.config:
                for p in d.config["probes"]:
                    p.update(zero_offset=-0.3219, zeroed_at="2026-10-08T08:30:00", tolerance=0.2)
        be = self.make_backend(devs)
        stations = []
        def factory(defn):
            s = measure.DemoStation(defn, lan.standards(defn), seed=3, delay=0.05)
            stations.append(s); return s
        w = MainWindow(be, factory, countdown=0.5, redetect=10)
        w.resize(1920, 1080); w.show(); pump(self.app, 0.3)
        def shot(name, widget=None, wait=0.3):
            pump(self.app, wait)
            (widget or w).grab().save(str(OUT / f"{name}.png")); print("saved", name)
        def wait_state(*st):
            end = time.monotonic() + 8
            while time.monotonic() < end:
                pump(self.app, 0.02)
                if w.banner.state in st and not w.busy: return
            raise RuntimeError(w.banner.state)
        w.detect(); pump(self.app, 0.02); shot("main-detecting", wait=0.05)
        wait_state("idle"); shot("main-idle")
        stations[-1].force = "pass"; w.next_piece(); pump(self.app, 0.1); shot("main-reading", wait=0.05)
        wait_state("pass"); shot("main-pass", wait=4.0)
        stations[-1].force = "fail"; w.reread(); wait_state("fail"); shot("main-fail", wait=4.0)
        stations[-1].force = "error"; w.next_piece(); wait_state("error"); shot("main-error", wait=4.0)
        stations[-1].force = "pass"; w.next_piece(); wait_state("pass")
        dlg = ExportDialog(w.sink, w); dlg.show(); shot("export", dlg)
        dlg.close()
        s = SettingsDialog(be); s.resize(560, 300); s.show(); shot("settings-password", s)
        s.enter_edit(); s.resize(1920, 1080)
        live = next(d for d in devs if d.status == lan.LIVE)
        s.select(live.mac); shot("settings-edit", s)
        unk = next((d for d in devs if d.status == lan.UNCLASSIFIED), None)
        if unk: s.select(unk.mac); shot("settings-unknown", s)
        s.select(live.mac)
        box = s.probe_table.cellWidget(0, 4); box.setCurrentIndex(box.findText("0.5 mm"))
        s.btn_save.click(); shot("settings-confirm", s)
        s._ask = lambda *a, **k: True; s.close(); w.close()

t = Shots(); t.setUpClass(); t.runTest()
