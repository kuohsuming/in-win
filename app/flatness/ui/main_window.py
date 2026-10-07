"""主畫面（畫面設計規格第 4、5 節；需求規格書 3.1～3.4、UI-01～UI-08）。

由上而下：頂端工具列 → 編號列 → 結果橫幅 → 每台「DL-EN1 使用中」一排（依定義檔順序，DEF-04）。
量測來源（Station）與結果寫入（ResultSink）由外部提供；偵測與讀取在背景執行緒進行，畫面不凍結。
"""

from __future__ import annotations

import html
import logging
import threading
from dataclasses import dataclass, field
from datetime import datetime

from PySide6.QtCore import QEvent, QObject, QPointF, QRectF, QSize, Qt, QTimer, Signal
from PySide6.QtGui import QColor, QFont, QFontMetrics, QPainter, QPolygonF
from PySide6.QtWidgets import (
    QDateEdit, QDialog, QFileDialog, QFrame, QGraphicsOpacityEffect, QGridLayout, QHBoxLayout, QLabel,
    QMainWindow, QPushButton, QScrollArea, QSizePolicy, QVBoxLayout, QWidget,
)

from .. import lan, measure
from ..measure import ERR, HI, LO, OK
from . import icons
from .theme import C, num_font, text_font
from .widgets import Backdrop, Dot, Toast

log = logging.getLogger(__name__)

WORD = {OK: "合格", HI: "偏高", LO: "偏低", ERR: "異常"}
BADGE_ICON = {OK: "pass", HI: "hi", LO: "lo", ERR: "err"}


def make_serial(now: datetime | None = None) -> str:
    """DAT-01：17 碼 YYYYMMDDHHmmssSSS。"""
    now = now or datetime.now()
    return now.strftime("%Y%m%d%H%M%S") + f"{now.microsecond // 1000:03d}"


def f3(v: float) -> str:
    return f"{v:.3f}"


@dataclass
class PointResult:
    key: str
    probe_id: int
    device_name: str
    description: str
    device_mac: str
    state: str                      # ok／hi／lo／err
    value: float | None = None
    std: object = None
    raw: str = ""
    error: str | None = None
    zero_offset: float | None = None  # 量測當時的校準偏移量（CAL-09）


@dataclass
class InspectionResult:
    """畫面上的一片結果；按「下一片」時寫入（MEA-01、MEA-06、DAT-02）。"""
    serial: str
    measured_at: datetime
    judgment: str                   # PASS／FAIL／ERROR
    rereads: int
    points: list = field(default_factory=list)
    written: bool = False


class MemorySink:
    """結果寫入（示範用）：只記錄在記憶體；資料庫寫入（DAT-02～DAT-05）於量測整合時實作。"""
    real = False

    def __init__(self):
        self.rows: list[InspectionResult] = []

    def write(self, result: InspectionResult):
        self.rows.append(result)
        log.info("示範模式：編號 %s 結果 %s（未寫入資料庫）", result.serial, result.judgment)

    def count(self, day) -> int:
        return sum(1 for r in self.rows if r.measured_at.date() == day)

    def export(self, day, path):
        raise NotImplementedError("取出測試數據（Excel）尚未實作")


class _Relay(QObject):
    detected = Signal(object)
    read_done = Signal(object)
    failed = Signal(str)
    sink_event = Signal(object)    # 結果寫入資料庫的進度（DAT-04）


# ====================================================================== 元件

class ScaleBar(QWidget):
    """刻度條（5.6）：允收區間佔中間 60%，標準值線固定 50%，三角形指標依公式定位。"""

    def __init__(self):
        super().__init__()
        self.k = 1.0
        self.setFixedHeight(34)
        self.value = self.std = None
        self.color = C["ink"]

    def set_scale(self, k: float):
        self.k = k
        self.setFixedHeight(max(14, round(34 * k)))
        self.update()

    def set(self, value, std, color):
        self.value, self.std, self.color = value, std, color
        self.update()

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, k = self.width(), self.k
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(C["line"]))
        p.drawRoundedRect(QRectF(0, 14 * k, w, 6 * k), 3 * k, 3 * k)
        ok = QColor(C["go"])
        ok.setAlphaF(0.35)
        p.setBrush(ok)
        p.drawRoundedRect(QRectF(w * 0.2, 10 * k, w * 0.6, 14 * k), 2, 2)
        p.setBrush(QColor(C["ink-2"]))
        p.drawRect(QRectF(w * 0.5 - 1, 7 * k, 2, 20 * k))
        if self.value is not None and self.std is not None:
            span = (self.std.upper - self.std.lower) / 0.6
            start = self.std.lower - span * 0.2
            pct = max(0.02, min(0.98, (self.value - start) / span))
            x = w * pct
            p.setBrush(QColor(self.color))
            p.drawPolygon(QPolygonF([QPointF(x - 9 * k, 0), QPointF(x + 9 * k, 0), QPointF(x, 13 * k)]))


class ProbeTile(QFrame):
    """探頭方塊（5.5）。"""

    def __init__(self, description: str, std):
        super().__init__()
        self.std = std
        self.k = 1.0                     # 依螢幕自動縮放（UI-11）
        self.setObjectName("probe")
        lay = self._lay = QVBoxLayout(self)
        top = QHBoxLayout()
        self.pos = QLabel(description)
        top.addWidget(self.pos)
        top.addStretch()
        self.badge_icon = QLabel()
        self.badge_text = QLabel()
        top.addWidget(self.badge_icon)
        top.addSpacing(6)
        top.addWidget(self.badge_text)
        lay.addLayout(top)

        # 測量值在左（大字）、標準值與允收在右，兩列高度即可（UI-11：讓 4 排以上放得下）
        grid = self._grid = QGridLayout()
        self._keys = []
        for k in ("測量值", "標準值", "允收"):
            lb = QLabel(k)
            lb.setStyleSheet(f"color:{C['ink-2']}")
            self._keys.append(lb)
        self.m = QLabel("—")
        self.m.setTextFormat(Qt.RichText)
        self.s = QLabel(f3(std.nominal) if std else "—")
        self.rg = QLabel(f"{f3(std.lower)} ～ {f3(std.upper)}" if std else "未設定")
        grid.addWidget(self._keys[0], 0, 0, 2, 1, Qt.AlignLeft | Qt.AlignVCenter)
        grid.addWidget(self.m, 0, 1, 2, 1, Qt.AlignLeft | Qt.AlignVCenter)
        grid.addWidget(self._keys[1], 0, 2, Qt.AlignRight | Qt.AlignBaseline)
        grid.addWidget(self.s, 0, 3, Qt.AlignLeft | Qt.AlignBaseline)
        grid.addWidget(self._keys[2], 1, 2, Qt.AlignRight | Qt.AlignBaseline)
        grid.addWidget(self.rg, 1, 3, Qt.AlignLeft | Qt.AlignBaseline)
        self.rg.setStyleSheet(f"color:{C['ink-2']}")
        grid.setColumnStretch(1, 1)
        lay.addLayout(grid)
        self.scale = ScaleBar()
        lay.addWidget(self.scale)
        self.note = QLabel()
        self.note.setStyleSheet(f"color:{C['ng']}")
        # 隱藏時保留位置：方塊高度不隨結果改變，排的大小固定（UI-11）
        sp = self.scale.sizePolicy()
        sp.setRetainSizeWhenHidden(True)
        self.scale.setSizePolicy(sp)
        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background:{C['line']}")
        lay.addWidget(sep)
        dev = QHBoxLayout()
        dev.setSpacing(6)
        self.dot = Dot()
        self.dev_text = QLabel()
        dev.addWidget(self.dot)
        dev.addWidget(self.dev_text)
        dev.addStretch()
        dev.addWidget(self.note)  # 超出多少等說明放在設備狀態列右側，不另佔一列（UI-11）
        lay.addLayout(dev)
        self._fx = QGraphicsOpacityEffect(self)
        self._fx.setOpacity(1.0)
        self.setGraphicsEffect(self._fx)
        self.state = "blank"
        self._last = (self.set_blank, ("stale", ""), {})
        self.set_scale(1.0)

    def _px(self, v: float) -> int:
        return max(1, round(v * self.k))

    def _fpx(self, v: float) -> int:
        """字級：縮放後不小於 12px，維持可讀（UI-11）。"""
        return max(12, round(v * self.k))

    def set_scale(self, k: float):
        """依縮放比例設定字級、間距與刻度條（UI-11）；目前的顯示內容以同樣參數重畫。"""
        self.k = k
        px = self._px
        self._lay.setSpacing(px(8))
        self.badge_icon.setFixedSize(px(36), px(36))  # 有無徽章時高度相同
        self._grid.setHorizontalSpacing(px(10))
        self._grid.setVerticalSpacing(px(2))
        self.pos.setFont(text_font(self._fpx(20), 700))
        self.badge_text.setFont(text_font(self._fpx(22), 900))
        for lb in self._keys:
            lb.setFont(text_font(self._fpx(15)))
        self.s.setFont(num_font(self._fpx(22)))
        self.rg.setFont(num_font(self._fpx(18)))
        self.note.setFont(text_font(self._fpx(18), 700))
        self.dev_text.setFont(text_font(self._fpx(14)))
        self.scale.set_scale(k)
        # 預留測量值寬度（例如「-88.888 mm」），有結果時方塊不變寬
        big = QFontMetrics(num_font(self._fpx(44), 700)).horizontalAdvance("-88.888")
        unit = QFontMetrics(num_font(self._fpx(18), 500)).horizontalAdvance(" mm")
        self.m.setMinimumWidth(big + unit + 4)
        # 預留測量值高度：數值與「mm」混排的行比單獨的「—」高；排高在空白狀態決定（_apply_scale），
        # 不預留時出現結果後測量值被壓扁裁切
        self.m.setMinimumHeight(0)
        self.m.setFont(num_font(self._fpx(44), 700))
        self.m.setText(self._value_html(-88.888))
        self.m.setMinimumHeight(self.m.sizeHint().height())
        # 預留設備狀態列高度：結果的紅字說明（18px 粗體）比「設備正常」（14px）高
        self.note.setText("低於下限 88.888")
        self.dev_text.setMinimumHeight(self.note.sizeHint().height())
        fn, args, kw = self._last
        fn(*args, **kw)

    def _frame(self, border_px, border, bg):
        # 邊框粗細不同時以內距補足，方塊內容與高度不變（UI-11）
        px, extra = self._px, 5 - border_px
        self._lay.setContentsMargins(px(14) + extra, px(12) + extra, px(14) + extra, px(12) + extra)
        self.setStyleSheet(f"QFrame#probe {{ background:{bg}; border:{border_px}px solid {border}; border-radius:6px; }}"
                           f" QFrame#probe QLabel {{ background: transparent; border: none; }}")

    def _device(self, color, text, bold=False, blink=False):
        self.dot.set_color(color, blink)
        self.dev_text.setText(text)
        self.dev_text.setStyleSheet(f"color:{C['ng'] if bold else C['ink-2']};{'font-weight:700' if bold else ''}")

    def set_blank(self, dev_color="stale", dev_text="", blink=False):
        """空白（倒數、讀取中）或偵測中：徽章與指標隱藏，測量值「—」。"""
        self._last = (self.set_blank, (dev_color, dev_text, blink), {})
        self.state = "blank"
        self._frame(3, C["line"], C["panel-2"])
        self.badge_icon.clear()
        self.badge_text.clear()
        self.m.setFont(num_font(self._fpx(44), 700))
        self.m.setText("—")
        self.m.setStyleSheet(f"color:{C['ink']}")
        self.scale.show()
        self.scale.set(None, self.std, C["ink"])
        self.note.hide()
        self._device(dev_color, dev_text, blink=blink)
        self.fade(False)

    def set_result(self, state, value=None, note="", device_text="設備正常", device_error=False):
        self._last = (self.set_result, (state, value, note, device_text, device_error), {})
        self.state = state
        color = C["go"] if state == OK else C["ng"]
        if state == OK:
            self._frame(3, C["go"], C["panel-2"])
        else:
            self._frame(5, C["ng"], C["ng-soft"])
        self.badge_icon.setPixmap(icons.pixmap(BADGE_ICON[state], color, self._px(36)))
        self.badge_text.setText(WORD[state])
        self.badge_text.setStyleSheet(f"color:{color}")
        if state == ERR:
            self.m.setFont(text_font(self._fpx(26), 900))
            self.m.setText("無數據")
            self.m.setStyleSheet(f"color:{C['ng']}")
            self.scale.hide()
        else:
            self.m.setFont(num_font(self._fpx(44), 700))
            self.m.setText(self._value_html(value))
            self.m.setStyleSheet(f"color:{C['ink'] if state == OK else C['ng']}")
            self.scale.show()
            self.scale.set(value, self.std, C["ink"] if state == OK else C["ng"])
        self.note.setText(note)
        self.note.setVisible(bool(note) and note != device_text)  # 與設備狀態相同時不重複顯示
        if device_error:
            self._device("ng", device_text, bold=True)
        else:
            self._device("go", device_text)

    def _value_html(self, value: float) -> str:
        return (f'{f3(value)}<span style="font-size:{self._fpx(18)}px;font-weight:500;color:{C["ink-2"]}">'
                f'&nbsp;mm</span>')

    def fade(self, on: bool):
        self._fx.setOpacity(0.55 if on else 1.0)


class DeviceRow(QFrame):
    """排（5.4）：左欄排名稱與 DL-EN1 標示，右欄探頭方塊；欄數最少 4、最多 6。"""

    def __init__(self, index: int, dev: dict, standards: dict):
        super().__init__()
        self.index, self.dev = index, dev
        self.maint = bool(dev.get("maint"))  # 維修中：顯示但不連線、不量測（DSC-15）
        self.seen_ip: str | None = None      # 實際使用 IP 與設定不同時為實際 IP（DSC-20）
        self.border_px = 1                   # 目前的邊框粗細（set_down）
        self.setObjectName("row")
        lay = self._lay = QHBoxLayout(self)
        left = self._left = QFrame()
        left.setObjectName("rowname")
        ll = QVBoxLayout(left)
        ll.setContentsMargins(4, 10, 4, 10)
        ll.setSpacing(6)
        ll.addStretch()
        self.name = QLabel(dev["name"])
        self.name.setAlignment(Qt.AlignCenter)
        self.name.setWordWrap(True)
        ll.addWidget(self.name)
        unit = QHBoxLayout()
        unit.setSpacing(4)
        unit.addStretch()
        self.unit_dot = Dot()
        self.unit_text = QLabel(self.tag)
        self.unit_text.setAlignment(Qt.AlignCenter)
        unit.addWidget(self.unit_dot)
        unit.addWidget(self.unit_text)
        unit.addStretch()
        ll.addLayout(unit)
        ll.addStretch()
        lay.addWidget(left)

        self.tiles: dict[int, ProbeTile] = {}
        self._grid = self._note = None
        if self.maint:
            note = self._note = QLabel(f"維修中：不連線、不量測（{len(dev['probes'])} 個探頭）")
            note.setAlignment(Qt.AlignCenter)
            note.setStyleSheet(f"color:{C['ink-2']};background:{C['panel-2']};border:2px dashed {C['line']};"
                               f"border-radius:6px;")
            lay.addWidget(note, 1)
            self.set_scale(1.0)
            self.set_down(False)
            return
        grid = self._grid = QGridLayout()
        probes = sorted(dev["probes"], key=lambda p: p["id"])
        ncols = min(max(len(probes), 4), 6)
        for i, p in enumerate(probes):
            t = ProbeTile(p["description"], (standards.get(dev["key"]) or {}).get(p["id"]))
            self.tiles[p["id"]] = t
            grid.addWidget(t, i // ncols, i % ncols)
        for c in range(ncols):
            grid.setColumnStretch(c, 1)
        lay.addLayout(grid, 1)
        self.set_scale(1.0)
        self.set_down(False)

    BORDER_MAX = 4  # 偵測不到、IP 不符時的邊框粗細

    def _margins(self):
        """邊框粗細不同時以內距補足，排內探頭方塊的高度不變（UI-11）。"""
        m = max(1, round(12 * self._k) + 1 - self.border_px)  # 內距 ＋ 邊框 固定為 12 ＋ 1
        self._lay.setContentsMargins(m, m, m, m)

    @property
    def fixed_height(self) -> int:
        """此比例下排的固定高度：內容 ＋ 內距 ＋ 最粗的邊框（_apply_scale）。"""
        return self._lay.sizeHint().height() + 2 * self.border_px

    def set_scale(self, k: float):
        """排與探頭方塊依縮放比例調整（UI-11）。"""
        px = lambda v: max(1, round(v * k))  # noqa: E731
        self._k = k
        self._margins()
        self._lay.setSpacing(px(12))
        self._left.setFixedWidth(max(84, px(110)))
        self.name.setFont(text_font(max(14, px(26)), 900))
        self.unit_text.setFont(num_font(max(11, px(12))))
        if self._note is not None:
            self._note.setFont(text_font(px(22), 700))
            self._note.setMinimumHeight(px(90))
        if self._grid is not None:
            self._grid.setSpacing(px(10))
        for t in self.tiles.values():
            t.set_scale(k)

    @property
    def tag(self) -> str:
        """排的標示：位置標籤「第 N 排」（EDT-05），與設定頁一致；沒有位置標籤時用畫面上的序號。"""
        key = self.dev.get("key")
        return lan.row_label(key) if lan.row_no(key) else f"DL-EN1 #{self.index + 1}"

    def set_index(self, index: int):
        """排的位置改變時更新標示，維持目前的偵測狀態顯示。"""
        self.index = index
        self.set_down(*self._down_args)

    def set_ip_mismatch(self, seen_ip: str | None):
        """DSC-20：DL-EN1 實際使用的 IP 與設定不同時，以警告色框與「IP 不符」標示這一排。"""
        if seen_ip != self.seen_ip:
            self.seen_ip = seen_ip
            self.set_down(*self._down_args)

    def set_down(self, down: bool, dot="stale", blink=False):
        self._down_args = (down, dot, blink)
        self.border_px = self.BORDER_MAX if down or self.seen_ip else 1
        if hasattr(self, "_k"):
            self._margins()
        border = (f"4px solid {C['ng']}" if down else f"4px solid {C['warn']}" if self.seen_ip
                  else f"1px solid {C['line']}")
        self.setStyleSheet(
            f"QFrame#row {{ background:{C['panel']}; border:{border}; border-radius:6px; }}"
            f"QFrame#rowname {{ background:{C['ng-soft'] if down else C['panel-2']}; border-radius:4px; border:none; }}")
        self.name.setStyleSheet(f"color:{C['ng'] if down else (C['ink-2'] if self.maint else C['ink'])};"
                                f" background:transparent;")
        if self.seen_ip and not down:
            self.unit_dot.hide()
            self.unit_text.setText(f"{self.tag}\nIP 不符" + ("・維修中" if self.maint else ""))
            self.unit_text.setStyleSheet(f"background:{C['warn']};color:white;font-weight:700;"
                                         f"padding:2px 8px;border-radius:3px;")
            return
        if self.maint:
            self.unit_dot.hide()
            self.unit_text.setText(f"{self.tag}\n維修中")
            self.unit_text.setStyleSheet(f"background:{C['warn-soft']};color:{C['warn']};font-weight:700;"
                                         f"padding:2px 8px;border-radius:3px;")
            return
        if down:
            self.unit_dot.hide()
            self.unit_text.setText(f"{self.tag}\n偵測不到")
            self.unit_text.setStyleSheet(f"background:{C['ng']};color:white;padding:2px 8px;border-radius:3px;")
        else:
            self.unit_dot.show()
            self.unit_dot.set_color(dot, blink)
            self.unit_text.setText(self.tag)
            self.unit_text.setStyleSheet(f"color:{C['ink-2']};background:transparent;")


class TightText(QWidget):
    """依字形實際上下範圍排版的單行大字（橫幅的「不合格」「FAIL」）。

    中文字型的行高約為字級的 1.45 倍，上下留白很多；橫幅高度固定（UI-11），以行高排版時大字與副標
    放不下而被裁切。這裡高度只取字形本身的範圍，文字垂直置中繪製。
    """

    def __init__(self):
        super().__init__()
        self._text, self._color, self._spacing = "", QColor(C["ink"]), 0.0
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)

    def text(self) -> str:
        return self._text

    def setText(self, text: str):
        self._text = text
        self._relayout()

    def set_style(self, color: str, spacing_em: float = 0.0):
        self._color, self._spacing = QColor(color), spacing_em
        self._relayout()

    def setFont(self, font):
        super().setFont(font)
        self._relayout()

    def _font(self):
        f = QFont(self.font())
        f.setLetterSpacing(QFont.AbsoluteSpacing, self._spacing * f.pixelSize())
        return f

    def _box(self):
        fm = QFontMetrics(self._font())
        r = fm.tightBoundingRect(self._text or " ")
        return fm, r

    def _relayout(self):
        fm, r = self._box()
        self.setFixedHeight(r.height() + 4 if self._text else 0)
        self.updateGeometry()
        self.update()

    def sizeHint(self):
        fm, r = self._box()
        return QSize(fm.horizontalAdvance(self._text) + 4, r.height() + 4 if self._text else 0)

    def minimumSizeHint(self):
        return self.sizeHint()

    def paintEvent(self, _e):
        if not self._text:
            return
        p = QPainter(self)
        p.setRenderHint(QPainter.TextAntialiasing)
        p.setFont(self._font())
        p.setPen(self._color)
        _, r = self._box()
        p.drawText(2 - min(0, r.left()), (self.height() - r.height()) // 2 - r.top(), self._text)
        p.end()


class Banner(QFrame):
    """結果橫幅（5.3）。"""

    def __init__(self, on_reread, on_next):
        super().__init__()
        self.setObjectName("banner")
        self.k = 1.0                     # 依螢幕自動縮放（UI-11）
        lay = self._lay = QHBoxLayout(self)
        left = self._left = QHBoxLayout()
        self.icon = QLabel()
        left.addWidget(self.icon)
        words = QVBoxLayout()
        words.setSpacing(6)
        words.addStretch()
        self.word = TightText()
        self.sub = TightText()
        words.addWidget(self.word)
        words.addWidget(self.sub)
        words.addStretch()
        left.addLayout(words)
        lay.addLayout(left)
        self.say = QLabel()
        self.say.setTextFormat(Qt.RichText)
        self.say.setWordWrap(True)
        self.say.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        lay.addWidget(self.say, 1)
        self.btn_reread = QPushButton("重讀")
        self.btn_next = QPushButton("下一片")
        for b in (self.btn_reread, self.btn_next):
            b.setCursor(Qt.PointingHandCursor)
        self.btn_reread.clicked.connect(on_reread)
        self.btn_next.clicked.connect(on_next)
        lay.addWidget(self.btn_reread)
        lay.addWidget(self.btn_next)
        self._spin_angle = 0
        self._spin = QTimer(self, interval=40, timeout=self._rotate)
        self.state = ""
        self._last = None
        self.set_scale(1.0)

    def _px(self, v: float) -> int:
        return max(1, round(v * self.k))

    def set_scale(self, k: float):
        """橫幅依縮放比例調整字級、圖示與按鍵（UI-11）；目前狀態以同樣參數重畫。"""
        self.k = k
        px = self._px
        # 上下內距 14：大字（112px 字形約 111px）＋ 副標「FAIL」需約 151px，固定高度 190 內放得下
        self._lay.setContentsMargins(px(32), px(14), px(32), px(14))
        self._lay.setSpacing(px(36))
        self._left.setSpacing(px(20))
        self.icon.setFixedSize(px(110), px(110))
        self.setFixedHeight(px(190))  # 固定高度：狀態改變時排的大小不跳動（UI-11）
        self.sub.setFont(num_font(px(40), 700))
        self.say.setFont(text_font(px(28), 500))
        for b in (self.btn_reread, self.btn_next):
            b.setFont(text_font(px(24), 700))
            b.setMinimumHeight(px(76))
        if self._last is not None:
            self.set(*self._last[0], **self._last[1])

    def set(self, state: str, *, icon=None, word="", sub="", say="", word_px=112, color=None,
            reread=False, next_=False, spin=False, countdown=False):
        self._last = ((state,), dict(icon=icon, word=word, sub=sub, say=say, word_px=word_px, color=color,
                                     reread=reread, next_=next_, spin=spin, countdown=countdown))
        px = self._px
        self.state = state
        bg, border = {"pass": (C["go-soft"], C["go"]), "fail": (C["ng-soft"], C["ng"]),
                      "error": (C["ng-soft"], C["ng"])}.get(state, (C["panel"], C["line"]))
        self.setStyleSheet(f"QFrame#banner {{ background:{bg}; border:4px solid {border}; border-radius:8px; }}"
                           f" QFrame#banner QLabel {{ background:transparent; border:none; }}")
        color = color or {"pass": C["go"], "fail": C["ng"], "error": C["ng"]}.get(state, C["ink-2"])
        self._icon_name, self._icon_color = icon, color
        self._spin.stop()
        self._spin_angle = 0
        if icon:
            self.icon.setPixmap(icons.pixmap(icon, color, px(110)))
            self.icon.show()
            if spin:
                self._spin.start()
        else:
            self.icon.hide()
        self.word.setFont(num_font(px(112), 700) if countdown else text_font(px(word_px), 900))
        self.word.setText(word)
        self.word.set_style(C["ink"] if countdown else color, 0.05)
        self.sub.setText(sub)
        self.sub.setVisible(bool(sub))
        self.sub.set_style(color, 0.12)
        self.say.setText(say)
        self.btn_reread.setEnabled(reread)
        self.btn_next.setEnabled(next_)
        primary = {"pass": C["go"], "fail": C["ng"], "error": C["ng"]}.get(state, C["ink"])
        self.btn_next.setStyleSheet(
            f"QPushButton {{ background:{primary}; color:white; border:none; border-radius:8px;"
            f" padding:{px(18)}px {px(30)}px; font-size:{px(24)}px; font-weight:700; }}"
            f"QPushButton:disabled {{ background: rgba(28,35,38,0.35); color: rgba(255,255,255,0.8); }}")
        self.btn_reread.setStyleSheet(
            f"QPushButton {{ background:{C['panel']}; color:{C['ink']}; border:3px solid {C['ink-2']};"
            f" border-radius:8px; padding:{px(18)}px {px(30)}px; font-size:{px(24)}px; font-weight:700; }}"
            f" QPushButton:hover {{ border-color:{C['ink']}; }}"
            f"QPushButton:disabled {{ color: rgba(28,35,38,0.35); border-color: rgba(86,97,106,0.35); }}")

    def _rotate(self):
        """偵測圖示每 1.6 秒旋轉一圈（第 7 節）。"""
        self._spin_angle = (self._spin_angle + 360 * 40 / 1600) % 360
        base = icons.pixmap(self._icon_name, self._icon_color, self._px(110))
        pm = base.copy()
        pm.fill(Qt.transparent)
        p = QPainter(pm)
        p.setRenderHint(QPainter.SmoothPixmapTransform)
        size = base.width() / base.devicePixelRatio()
        p.translate(size / 2, size / 2)
        p.rotate(self._spin_angle)
        p.translate(-size / 2, -size / 2)
        p.drawPixmap(0, 0, base)
        p.end()
        self.icon.setPixmap(pm)


class ExportDialog(QDialog):
    """取出測試數據（5.8、EXP-01～EXP-04）。"""

    def __init__(self, sink, parent=None):
        super().__init__(parent, Qt.Dialog | Qt.FramelessWindowHint)
        self.sink = sink
        self.setObjectName("export")
        self.setStyleSheet(f"#export {{ background:{C['panel']}; border:1px solid {C['line']}; border-radius:8px; }}")
        self.setFixedWidth(460)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(22, 20, 22, 20)
        lay.setSpacing(14)
        lay.addWidget(_obj(QLabel("取出測試數據"), "h1"))
        lay.addWidget(_obj(QLabel("日期"), "label"))
        self.date = QDateEdit()
        self.date.setCalendarPopup(True)
        self.date.setDisplayFormat("yyyy-MM-dd")
        self.date.setDate(datetime.now().date())
        self.date.setFont(num_font(20))
        self.date.dateChanged.connect(self._update)
        lay.addWidget(self.date)
        self.info = QLabel()
        self.info.setTextFormat(Qt.RichText)
        self.info.setStyleSheet(f"background:{C['panel-2']};border-radius:4px;padding:10px 12px;font-size:16px;")
        lay.addWidget(self.info)
        row = QHBoxLayout()
        row.addStretch()
        cancel = QPushButton("取消")
        cancel.clicked.connect(self.reject)
        self.save = QPushButton("選擇位置並儲存")
        self.save.setProperty("kind", "primary")
        self.save.clicked.connect(self._save)
        row.addWidget(cancel)
        row.addWidget(self.save)
        lay.addLayout(row)
        self._update()

    def _update(self):
        day = self.date.date().toPython()
        n = self.sink.count(day)
        if n:
            self.info.setText(f"該日共 <b>{n}</b> 筆紀錄<br>預設檔名：平整檢查_{day:%Y-%m-%d}.xlsx")
        else:
            self.info.setText("該日沒有紀錄，不會產生檔案。")
        self.save.setEnabled(n > 0)

    def _save(self):
        day = self.date.date().toPython()
        path, _ = QFileDialog.getSaveFileName(self, "取出測試數據", f"平整檢查_{day:%Y-%m-%d}.xlsx", "Excel (*.xlsx)")
        if not path:
            return
        try:
            self.sink.export(day, path)
        except Exception as exc:
            self.parent().toast.show_text(f"無法產生檔案：{exc}")
            return
        self.parent().toast.show_text(f"已儲存 {path}")
        self.accept()


def _obj(w, name):
    w.setObjectName(name)
    return w


# ====================================================================== 主畫面

class MainWindow(QMainWindow):
    def __init__(self, backend, station_factory, sink=None, *, countdown: int | None = None,
                 redetect: int | None = None):
        super().__init__()
        self.backend = backend
        self.station_factory = station_factory      # definition → Station（偵測、讀取）
        self.sink = sink or MemorySink()
        self.countdown_s = countdown or backend.cfg.countdown_seconds
        self.redetect_s = redetect or backend.cfg.redetect_seconds
        self.setWindowTitle("表面平整檢查系統")
        self.serial: str | None = None
        self.rereads = 0
        self.result: InspectionResult | None = None
        self.detect_count = 0
        self.busy = False                           # 倒數、讀取、偵測中
        self.flags = {"sim": backend.simulate, "bootp": None, "db": None, "ip": None, "sync": None}
        self.seen_ips: dict[str, str] = {}  # MAC → 實際使用 IP（ARP 位址偵測封包，DSC-19）
        self._relay = _Relay()
        self._relay.detected.connect(self._on_detected)
        self._relay.read_done.connect(self._on_read)
        self._relay.failed.connect(self._on_worker_failed)
        self._relay.sink_event.connect(self._on_sink_event)
        if hasattr(self.sink, "listener"):
            self.sink.listener = self._relay.sink_event.emit
            if self.sink.pending():
                self.set_flag("sync", f"待同步 {self.sink.pending()} 筆（寫入資料庫中）")

        page = QWidget()
        page.setObjectName("page")
        self.setCentralWidget(page)
        outer = QVBoxLayout(page)
        outer.setContentsMargins(16, 16, 16, 16)
        body = QWidget()
        outer.addWidget(body, 0, Qt.AlignHCenter)
        page.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        body.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.body_lay = QVBoxLayout(body)
        self.body_lay.setContentsMargins(0, 0, 0, 0)
        self.body_lay.setSpacing(14)
        self._top = self._topbar()
        self._serial = self._serialbar()
        self.body_lay.addWidget(self._top)
        self.body_lay.addWidget(self._serial)
        self.banner = Banner(self.reread, self.next_piece)
        self.body_lay.addWidget(self.banner)
        self.rows_area = QScrollArea()
        self.rows_area.setWidgetResizable(True)
        self.rows_area.setFrameShape(QFrame.NoFrame)
        self.rows_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.rows_area.setStyleSheet("QScrollArea, QScrollArea > QWidget > QWidget { background: transparent; }")
        self.body_lay.addWidget(self.rows_area, 1)
        self.rows_area.installEventFilter(self)  # 排區大小改變（例如編號列變高）時重新縮放（UI-11）
        outer.setStretch(0, 1)
        body.setMinimumWidth(0)

        self.backdrop = Backdrop(page)
        self.toast = Toast(page)
        self._clock = QTimer(self, interval=1000, timeout=self._tick)
        self._clock.start()
        self._tick()
        self._cd_timer = QTimer(self, interval=1000, timeout=self._countdown_tick)
        self._retry_timer = QTimer(self, interval=1000, timeout=self._retry_tick)
        self._boot_timer = QTimer(self, singleShot=True, timeout=self.detect)
        self._retry_left = 0

        backend.bootp_state.connect(self._on_bootp)
        backend.devices_seen.connect(self._on_seen)
        backend.db_state.connect(lambda ok: self.set_flag("db", None if ok else "無法讀取資料庫，使用上次的設定"))
        r = backend.startup_result
        if r is not None and r.problem:
            self.set_flag("db", r.problem)
        self.rebuild(backend.layout)

    # ------------------------------------------------------------------ 版面

    def resizeEvent(self, e):
        super().resizeEvent(e)
        body = self.body_lay.parentWidget()
        body.setFixedWidth(self.centralWidget().width() - 32)  # 使用整個螢幕寬度（UI-11）
        if self.backdrop.isVisible():
            self.backdrop.cover()
        self._fit_later()

    # 依螢幕自動縮放（UI-11）：至少 4 排（設備少於 4 排時為全部）不捲動即可看到全部探頭
    MIN_VISIBLE_ROWS = 4
    SCALE_MIN = 0.45

    def eventFilter(self, obj, e):
        if obj is self.rows_area and e.type() == QEvent.Resize and not getattr(self, "_fitting", False):
            self._fit_later()
        return super().eventFilter(obj, e)

    def _fit_later(self):
        if not getattr(self, "_fit_pending", False):
            self._fit_pending = True
            QTimer.singleShot(0, self.fit_to_screen)

    def _apply_scale(self, k: float):
        self.scale_k = k
        self.banner.set_scale(min(1.0, 0.4 + 0.6 * k))  # 橫幅是主要結果，縮得比排少
        for r in self.rows:
            r.set_scale(k)
            r.setFixedHeight(r.fixed_height)  # 排高固定為此比例所需，不被捲動區拉伸或壓縮
        holder = self.rows_area.widget()
        if holder is not None:  # 立即重新排版，避免沿用上一個比例的高度
            holder.layout().invalidate()
            holder.layout().activate()
        self.body_lay.invalidate()
        self.body_lay.activate()

    def fit_to_screen(self):
        """選擇最大的縮放比例，使全部的排（多於 4 排時至少前 4 排）與橫幅在畫面內，不需捲動。"""
        self._fit_pending = False
        self._fitting = True
        try:
            self._fit()
        finally:
            self._fitting = False

    def _fit(self):
        avail_w = self.body_lay.parentWidget().width()
        if self.centralWidget().height() <= 32 or not self.rows:
            self._apply_scale(1.0)
            return

        def fits(k, count):
            self._apply_scale(k)  # 套用後版面已重新計算：以排區實際高度比較
            rows = self.rows[:count]
            h = sum(r.maximumHeight() for r in rows) + 12 * (len(rows) - 1)  # 排高已固定（_apply_scale）
            w = max(r.minimumSizeHint().width() for r in self.rows)
            return h <= self.rows_area.height() and w <= avail_w

        n = len(self.rows)
        counts = [n] if n <= self.MIN_VISIBLE_ROWS else [n, self.MIN_VISIBLE_ROWS]
        for count in counts:
            if fits(1.0, count):
                return
            if not fits(self.SCALE_MIN, count):
                continue
            lo, hi = self.SCALE_MIN, 1.0          # 二分搜尋最大的可容納比例
            while hi - lo > 0.01:
                mid = (lo + hi) / 2
                lo, hi = (mid, hi) if fits(mid, count) else (lo, mid)
            self._apply_scale(round(lo, 3))
            return
        self._apply_scale(self.SCALE_MIN)

    def _topbar(self) -> QWidget:
        bar = QFrame()
        bar.setObjectName("panel")
        lay = QHBoxLayout(bar)
        lay.setContentsMargins(16, 10, 16, 10)
        lay.setSpacing(12)
        title = QLabel("表面平整檢查")
        title.setFont(text_font(20, 700))
        lay.addWidget(title)
        lay.addStretch()
        self.flag_box = QHBoxLayout()
        self.flag_box.setSpacing(8)
        lay.addLayout(self.flag_box)
        self.sum_dot = Dot()
        self.sum_text = QLabel()
        self.sum_text.setFont(text_font(15))
        self.sum_text.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)  # 不被系統狀態提示擠壓
        lay.addWidget(self.sum_dot)
        lay.addWidget(self.sum_text)
        self.btn_detect = self._tool("偵測設備", "detect", self.detect)
        self.btn_export = self._tool("取出測試數據", "excel", self.open_export)
        lay.addWidget(self.btn_detect)
        lay.addWidget(self.btn_export)
        self.btn_settings = QPushButton()
        self.btn_settings.setProperty("kind", "icon")
        self.btn_settings.setIcon(icons.icon("edit", C["ink"], 22))
        self.btn_settings.setIconSize(icons.pixmap("edit", C["ink"], 22).size() / 2)
        self.btn_settings.setToolTip("設備設定")
        self.btn_settings.setCursor(Qt.PointingHandCursor)
        self.btn_settings.setFixedSize(46, 46)
        self.btn_settings.clicked.connect(self.open_settings)
        lay.addWidget(self.btn_settings)
        return bar

    def _tool(self, text, icon, slot):
        b = QPushButton(text)
        b.setProperty("kind", "tool")
        b.setIcon(icons.icon(icon, C["ink"], 20))
        b.setCursor(Qt.PointingHandCursor)
        b.clicked.connect(slot)
        return b

    def _serialbar(self) -> QWidget:
        bar = QFrame()
        bar.setObjectName("panel")
        lay = QHBoxLayout(bar)
        lay.setContentsMargins(18, 12, 18, 12)
        col = QVBoxLayout()
        col.setSpacing(2)
        lb = QLabel("編號（按下一片自動產生）")
        lb.setFont(text_font(14))
        lb.setStyleSheet(f"color:{C['ink-2']}")
        col.addWidget(lb)
        line = QHBoxLayout()
        line.setSpacing(6)
        self.serial_label = QLabel("—")
        self.serial_label.setFont(num_font(32, 700))
        self.reread_label = QLabel()
        self.reread_label.setFont(text_font(15))
        self.reread_label.setStyleSheet(f"color:{C['ink-2']}")
        line.addWidget(self.serial_label)
        line.addWidget(self.reread_label, 0, Qt.AlignBottom)
        line.addStretch()
        col.addLayout(line)
        lay.addLayout(col, 1)
        self.clock = QLabel()
        self.clock.setFont(num_font(20))
        self.clock.setStyleSheet(f"color:{C['ink-2']}")
        lay.addWidget(self.clock, 0, Qt.AlignRight | Qt.AlignVCenter)
        return bar

    def _tick(self):
        n = datetime.now()
        self.clock.setText(f"{n.year}/{n.month}/{n.day} {n:%H:%M:%S}")

    def set_flag(self, name: str, text: str | None):
        """系統狀態提示（5.1）：BOOTP 服務停止、無法讀取資料庫、模擬模式。"""
        self.flags[name] = text
        while self.flag_box.count():
            w = self.flag_box.takeAt(0).widget()
            if w:
                w.hide()
                w.setParent(None)
                w.deleteLater()
        if self.flags.get("sim"):
            lb = QLabel("模擬模式")
            lb.setStyleSheet(f"background:{C['ink']};color:{C['panel']};font-size:17px;font-weight:700;"
                             f"padding:5px 10px;border-radius:4px;letter-spacing:0.15em;")
            self.flag_box.addWidget(lb)
        for key, fg, bg in (("bootp", C["ng"], C["ng-soft"]), ("db", C["warn"], C["warn-soft"]),
                            ("ip", "white", C["warn"]), ("sync", C["warn"], C["warn-soft"])):
            text = self.flags.get(key)
            if text:
                lb = QLabel(f'<span style="color:{fg}">●</span> {html.escape(text)}')
                lb.setStyleSheet(f"background:{bg};color:{fg};font-size:15px;font-weight:700;padding:5px 10px;"
                                 f"border-radius:4px;")
                lb.setMaximumWidth(900 if key == "ip" else 520)
                lb.setWordWrap(key == "ip")
                lb.setToolTip(text)
                self.flag_box.addWidget(lb)

    def _on_seen(self, events):
        """探索事件：更新設備實際使用的 IP（DSC-19），檢查與設定是否不同（DSC-20）。"""
        changed = False
        for e in events:
            if e.ip and self.seen_ips.get(e.mac) != e.ip:
                self.seen_ips[e.mac] = e.ip
                changed = True
        if changed:
            self._check_ips()

    def _check_ips(self):
        """DSC-20：使用中／維修中 DL-EN1 實際使用的 IP 與設定不同時，該排以警告色標示，
        頂端提示按住 DL-EN1 的 RST 鍵 3 秒重設，使其重新以 BOOTP 取得設定的 IP。"""
        notes = []
        net = self.backend.equip_net()
        for row in self.rows:
            try:
                mac = lan.normalize_mac(row.dev.get("mac", ""))
            except ValueError:
                mac = ""
            seen, want = self.seen_ips.get(mac), row.dev.get("ipv4")
            bad = lan.ip_mismatch(seen, want)
            row.set_ip_mismatch(seen if bad else None)
            if bad:
                why = lan.seen_ip_problem(seen, net)
                notes.append(f"{row.dev.get('name') or mac}（{row.tag}）實際 IP {seen}"
                             + (f"（{why}）" if why else "") + f"，設定為 {want}")
        self.set_flag("ip", ("IP 不符：" + "；".join(notes) + "。請按住該台 DL-EN1 上的 RST 鍵 3 秒重設，"
                             "使其重新取得設定的 IP") if notes else None)
        if notes:
            log.warning("DL-EN1 IP 不符：%s", "；".join(notes))

    def _on_bootp(self, running: bool, reason: str):
        self.set_flag("bootp", None if running or not reason else "BOOTP 服務停止，自動重新啟動中")

    def rebuild(self, layout: dict):
        """依主畫面版面建立排與探頭（DEF-04）；套用設定後不需重啟程式。

        layout 為定義檔格式，含使用中與維修中（"maint": True）；只有使用中連線、偵測、量測（DSC-15）。
        """
        self.layout = layout
        self.devices = [d for d in layout.get("dl_en1", []) if not d.get("maint")]
        self.definition = {"version": 1, "dl_en1": self.devices}
        old = getattr(self, "station", None)
        if old is not None and hasattr(old, "close"):
            old.close()  # 關閉舊設定的 DL-EN1 連線（DEV-09）
        self.station = self.station_factory(self.definition)
        holder = QWidget()
        holder.setStyleSheet("background: transparent;")
        lay = QVBoxLayout(holder)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(12)
        self.rows: list[DeviceRow] = []
        std = self.backend.standards()
        for i, d in enumerate(layout.get("dl_en1", [])):
            row = DeviceRow(i, d, std)
            self.rows.append(row)
            lay.addWidget(row)
        if not self.devices:
            hint = QLabel("尚未設定「DL-EN1 使用中」的設備，請至「設備設定」設定。")
            hint.setFont(text_font(24, 700))
            hint.setAlignment(Qt.AlignCenter)
            hint.setStyleSheet(f"color:{C['ng']}")
            lay.addWidget(hint)
        lay.addStretch()
        self.rows_area.setWidget(holder)
        self.seen_ips.update({d.mac: d.seen_ip for d in self.backend.cached_devices() if d.seen_ip})
        self._check_ips()
        self._apply_scale(getattr(self, "scale_k", 1.0))
        self._fit_later()

    @property
    def live_rows(self) -> list[DeviceRow]:
        return [r for r in self.rows if not r.maint]

    @property
    def n_probes(self) -> int:
        return sum(len(d["probes"]) for d in self.devices)

    # ------------------------------------------------------------------ 共用

    def _lock(self, busy: bool):
        """倒數、讀取、偵測中：工具按鍵與設備設定停用（5.1 停用規則、MEA-03）。"""
        self.busy = busy
        for b in (self.btn_detect, self.btn_export, self.btn_settings):
            b.setEnabled(not busy)

    def _summary(self, mode: str, n_err: int = 0):
        if mode == "detecting":
            self.sum_dot.set_color("ink-2", blink=True)
            self.sum_text.setText(f"偵測設備中（第 {self.detect_count} 次）")
            self.sum_text.setStyleSheet(f"color:{C['ink-2']}")
        elif mode == "ok":
            self.sum_dot.set_color("go")
            self.sum_text.setText(f"{len(self.devices)} 台 DL-EN1、{self.n_probes} 個探頭正常")
            self.sum_text.setStyleSheet(f"color:{C['ink-2']}")
        else:
            self.sum_dot.set_color("ng")
            self.sum_text.setText(f"{n_err} 個量測點異常")
            self.sum_text.setStyleSheet(f"color:{C['ng']};font-weight:700")

    def _meta(self):
        self.serial_label.setText(self.serial or "—")
        self.reread_label.setText(f"重讀 {self.rereads} 次" if self.rereads else "")

    def _clear_tiles(self, dev_color="stale", dev_text="", blink=False):
        for row in self.live_rows:
            row.set_down(False, dev_color, blink)
            for t in row.tiles.values():
                t.set_blank(dev_color, dev_text, blink)

    def _run(self, fn, signal):
        def work():
            try:
                signal.emit(fn())
            except Exception as exc:  # 背景工作失敗不可讓畫面卡住
                log.exception("背景工作失敗")
                self._relay.failed.emit(str(exc))
        threading.Thread(target=work, daemon=True, name="station").start()

    def _on_worker_failed(self, message: str):
        self._lock(False)
        self.show_device_error([f"設備通訊失敗：{message}"], [])

    # ------------------------------------------------------------------ 偵測（DEV-01～DEV-08）

    def detect(self):
        if self.busy:
            return
        self._retry_timer.stop()
        self._lock(True)
        self.detect_count += 1
        self._clear_tiles("ink-2", "偵測中…", blink=True)
        self._summary("detecting")
        self.banner.set("detecting", icon="detect", word="偵測設備中", word_px=84, spin=True,
                        say=f"第 <b>{self.detect_count}</b> 次偵測<br>正在檢查 {len(self.devices)} 台 DL-EN1 與 "
                            f"{self.n_probes} 個探頭…<br>全部正常後即可開始工作。")
        if not self.devices:
            QTimer.singleShot(0, lambda: self._on_detected([]))
            return
        self._run(self.station.detect, self._relay.detected)

    def _on_detected(self, statuses):
        self._lock(False)
        if not self.devices:
            self.show_device_error(["尚未設定「DL-EN1 使用中」的設備"], [])
            return
        by_key = {s.key: s for s in statuses}
        if any(s.booting for s in statuses):
            self.banner.set("booting", icon="detect", word="設備啟動中", word_px=84, spin=True,
                            say="DL-EN1 啟動中，自動重試")
            self._boot_timer.start(1000)
            return
        errs, n_err = [], 0
        std = self.backend.standards()
        for row in self.live_rows:
            d = row.dev
            s = by_key.get(d["key"], measure.DeviceStatus(d["key"], reachable=False))
            if not s.reachable:
                errs.append(f"{d['name']} DL-EN1 偵測不到")
                row.set_down(True)
                for t in row.tiles.values():
                    t.set_result(ERR, device_text="DL-EN1 偵測不到", device_error=True)
                    n_err += 1
                continue
            if s.error:  # 整台設備異常：連得上，但不能量測（本機錯誤、探頭台數超出定義 DEF-06）
                errs.append(f"{d['name']} {s.error}")
                row.set_down(False, "ng")
                for t in row.tiles.values():
                    t.set_result(ERR, note=s.error, device_text="設備異常", device_error=True)
                    n_err += 1
                continue
            row.set_down(False, "go")
            missing = uncal = 0
            for pid, t in row.tiles.items():
                if pid in s.probe_errors:
                    t.set_result(ERR, note=s.probe_errors[pid], device_text="探頭無回應", device_error=True)
                    errs.append(f"{d['name']} {self._desc(d, pid)}探頭無回應（{s.probe_errors[pid]}）")
                    n_err += 1
                elif pid in s.uncalibrated:  # CAL-07：未校準不量測
                    t.set_result(ERR, note="請在設備設定校準", device_text="未校準", device_error=True)
                    uncal += 1
                    n_err += 1
                elif (std.get(d["key"]) or {}).get(pid) is None:
                    t.set_result(ERR, note="未設定允收標準", device_text="未設定允收標準", device_error=True)
                    missing += 1
                    n_err += 1
                else:
                    t.set_blank("go", "設備正常")
            if missing:
                errs.append(f"{d['name']} 有 {missing} 個探頭未設定允收標準")
            if uncal:
                errs.append(f"{d['name']} 有 {uncal} 個探頭未校準，請在設備設定以標準件校準")
        if errs:
            self._summary("error", n_err)
            self.show_device_error(errs, [])
            return
        self._summary("ok")
        if self.result is not None:
            # 量測後發生的設備異常已排除：保留畫面上的結果，可重讀或下一片
            self.banner.set("idle", word="待放置", say=f"設備已恢復正常（第 {self.detect_count} 次偵測）。<br>"
                            "按「重讀」重新量測此片，或放上新的一片後按「下一片」。", reread=True, next_=True)
            return
        self.banner.set("idle", word="待放置",
                        say=f"設備正常（第 {self.detect_count} 次偵測），可以開始工作。<br>"
                            "請將表面放到治具上，再按「下一片」。", next_=True)

    @staticmethod
    def _desc(dev, pid):
        return next((p["description"] for p in dev["probes"] if p["id"] == pid), str(pid))

    def show_device_error(self, errs, outs):
        """設備異常（5.3）：列出原因；每 10 秒自動重新偵測（DEV-05、DEV-06）。"""
        def brief(items, n=2):
            """橫幅高度固定（UI-11）：最多列出 n 項，其餘以「等 N 項」表示；各排的異常仍標示在排與探頭上。"""
            text = "、".join(map(html.escape, items[:n]))
            return text + (f" 等 {len(items)} 項" if len(items) > n else "")
        more = f"<br>另有：<b>{brief(outs, 1)}</b>" if outs else ""
        self._err_text = (f"<b>{brief(errs)}</b>{more}<br>請通知工程人員；排除後自動恢復。")
        self._retry_left = self.redetect_s
        self._render_error()
        self._retry_timer.start()

    def _render_error(self):
        self.banner.set("error", icon="err", word="設備異常", sub="FAIL", word_px=84,
                        say=f"{self._err_text}<br><span style='font-size:{self.banner._px(25)}px;color:{C['ink-2']}'>"
                            f"已偵測 <b>{self.detect_count}</b> 次，<b>{self._retry_left}</b> 秒後自動重新偵測</span>")
        self._fade_ok(True)

    def _retry_tick(self):
        if self.busy:
            return
        self._retry_left -= 1
        if self._retry_left <= 0:
            self._retry_timer.stop()
            self.detect()
        else:
            self._render_error()

    # ------------------------------------------------------------------ 量測（MEA-01～MEA-06）

    def next_piece(self):
        """MEA-01：先寫入畫面上的結果，再產生新編號、清空畫面並開始量測。"""
        if self.busy:
            return
        self.flush_result()
        self.serial = make_serial()
        self.rereads = 0
        self._start_measure()

    def reread(self):
        """MEA-05：編號不變，重讀次數加 1。"""
        if self.busy or not self.serial:
            return
        self.rereads += 1
        self._start_measure()

    def flush_result(self) -> str | None:
        """寫入畫面上尚未寫入的結果（MEA-01、MEA-02、UPL-02、DAT-05）；回傳寫入的編號。"""
        r = self.result
        if r is None or r.written:
            return None
        r.rereads = self.rereads
        self.sink.write(r)
        r.written = True
        self.result = None
        if self.sink.real:
            pass  # 寫入資料庫在背景進行，完成時提示（_on_sink_event）
        else:
            self.toast.show_text(f"示範模式：編號 {r.serial} 未寫入資料庫")
        return r.serial

    def _on_sink_event(self, event):
        """DAT-04：寫入成功提示；資料庫無法寫入時頂端顯示待同步筆數，補寫完成後消失。"""
        kind, what, pending = event
        if kind == "written":
            self.toast.show_text(f"編號 {what} 已寫入資料庫")
            self.set_flag("sync", f"待同步 {pending} 筆（寫入資料庫中）" if pending else None)
        else:
            self.set_flag("sync", f"資料庫無法寫入，待同步 {pending} 筆（自動重試）")

    def pending_serial(self) -> str | None:
        return self.result.serial if self.result and not self.result.written else None

    def _start_measure(self):
        self._retry_timer.stop()
        self._lock(True)
        self._meta()
        self._clear_tiles("go", "設備正常")
        self._fade_ok(False)
        self.result = None
        self._cd_left = self.countdown_s
        self._show_countdown()
        self._cd_timer.start()

    def _show_countdown(self):
        self.banner.set("countdown", word=str(self._cd_left), countdown=True,
                        say=f"請勿移動表面<br>{self._cd_left} 秒後自動讀取探頭數值")

    def _countdown_tick(self):
        self._cd_left -= 1
        if self._cd_left > 0:
            self._show_countdown()
            return
        self._cd_timer.stop()
        self.banner.set("reading", word="讀取中", say=f"正在讀取 {self.n_probes} 個探頭…")
        self._measured_at = datetime.now()
        self._run(self.station.read, self._relay.read_done)

    def _on_read(self, readings):
        self._lock(False)
        self.show_result(readings, self._measured_at)

    def show_result(self, readings, measured_at=None):
        """判定並顯示（JDG-01～JDG-04、UI-03～UI-07）。"""
        by = {(r.key, r.probe_id): r for r in readings}
        std = self.backend.standards()
        points, outs, errs, n_err = [], [], [], 0
        mac = {d["key"]: d.get("mac", "") for d in self.devices}
        for row in self.live_rows:
            d = row.dev
            row.set_down(False, "go")
            missing = 0
            for pid, tile in row.tiles.items():
                r = by.get((d["key"], pid)) or measure.ProbeReading(d["key"], pid, None, "", "探頭無回應")
                s = (std.get(d["key"]) or {}).get(pid)
                desc = self._desc(d, pid)
                if r.error == "未校準":  # CAL-07
                    state = ERR
                    tile.set_result(ERR, note="請在設備設定校準", device_text="未校準", device_error=True)
                    errs.append(f"{d['name']} {desc}未校準")
                    n_err += 1
                elif r.error or r.value is None:
                    state = ERR
                    tile.set_result(ERR, note=r.error or "無有效數據", device_text="探頭無回應", device_error=True)
                    errs.append(f"{d['name']} {desc}探頭無回應（{r.error or '無有效數據'}）")
                    n_err += 1
                elif s is None:
                    state = ERR
                    tile.set_result(ERR, note="未設定允收標準", device_text="未設定允收標準", device_error=True)
                    missing += 1
                    n_err += 1
                else:
                    state = measure.judge(r.value, s)
                    note = (f"超出上限 {f3(r.value - s.upper)}" if state == HI else
                            f"低於下限 {f3(s.lower - r.value)}" if state == LO else "")
                    tile.set_result(state, r.value, note)
                    if state != OK:
                        outs.append(f"{d['name']} {desc}{WORD[state]}")
                points.append(PointResult(d["key"], pid, d["name"], desc, mac.get(d["key"], ""), state,
                                          r.value, s, r.raw, r.error or ("未設定允收標準" if s is None else None),
                                          r.offset))
            if missing:
                errs.append(f"{d['name']} 有 {missing} 個探頭未設定允收標準")
        verdict = measure.overall(p.state for p in points)
        self.result = InspectionResult(self.serial or make_serial(), measured_at or datetime.now(),
                                       {"pass": "PASS", "fail": "FAIL", "error": "ERROR"}[verdict],
                                       self.rereads, points)
        self._fade_ok(verdict != "pass")
        if verdict == "error":
            self._summary("error", n_err)
            self.show_device_error(errs, outs)
        elif verdict == "fail":
            self._summary("ok")
            self.banner.set("fail", icon="fail", word="不合格", sub="FAIL", reread=True, next_=True,
                            say=f"<b>{'、'.join(map(html.escape, outs))}</b><br>懷疑沒放好可重新放置後按「重讀」；"
                                "<br>確認不良請放到不良品區，放上新的一片後按「下一片」。")
        else:
            self._summary("ok")
            self.banner.set("pass", icon="pass", word="合格", sub="PASS", reread=True, next_=True,
                            say=f"{self.n_probes} 個量測點都在標準範圍內。<br>送往下一站，放上新的一片後按「下一片」。")

    def _fade_ok(self, on: bool):
        """淡化規則（5.5）：不合格或設備異常時，合格方塊透明度 55%。"""
        for row in self.live_rows:
            for t in row.tiles.values():
                t.fade(on and t.state == OK)

    # ------------------------------------------------------------------ 對話框

    def _modal(self, dlg) -> int:
        """對話框嵌入遮罩、置於主畫面中央（UI-09），以模態方式執行。"""
        self.backdrop.host(dlg)
        try:
            return dlg.exec()
        finally:
            self.backdrop.release()

    def open_export(self):
        if not self.busy:
            self._modal(ExportDialog(self.sink, self))

    def open_settings(self):
        """設備設定（5.10）：只能在待放置或結果顯示時使用（UPL-02）。"""
        if self.busy:
            return
        from .settings_dialog import SettingsDialog
        station = self.station if hasattr(self.station, "sample") else None
        dlg = SettingsDialog(self.backend, self, pending_serial=self.pending_serial(),
                             before_save=self.flush_result,
                             calibrator=(lambda: self.station) if station is not None else None)  # CAL-02
        dlg.saved.connect(self._on_settings_saved)
        self._modal(dlg)

    def _on_settings_saved(self, result, preview):
        """儲存後：清除編號與重讀次數 → 依新設定重建主畫面 → 自動偵測設備（5.10 儲存後）。"""
        self.serial, self.rereads, self.result = None, 0, None
        self._meta()
        self.rebuild(result.layout)
        msg = "已儲存設定並更新 BOOTP 對應"
        if preview.reset:
            msg += "；請按住 " + "、".join(preview.reset) + " 上的 RST 鍵 3 秒重設，才會取得新 IP"
        if preview.power_cycle:
            msg += "；請將 " + "、".join(preview.power_cycle) + " 重新連線或重新上電"
        QTimer.singleShot(0, lambda: self.toast.show_text(msg, 6000))
        self.detect()

    def closeEvent(self, e):
        """DAT-05：關閉程式時，畫面上尚未寫入的結果自動寫入。"""
        try:
            self.flush_result()
        finally:
            super().closeEvent(e)
