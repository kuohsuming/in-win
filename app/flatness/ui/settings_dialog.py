"""設備設定對話框（畫面設計規格 5.10；需求規格書 3.10 DSC、3.8 UPL、3.8.3 EDT）。

三個步驟：密碼 → 編輯（偵測到的設備清單 ＋ 偵測到的設備）→ 確認儲存。
設備與 MAC 一律來自偵測或匯入，不提供手動新增或輸入 MAC（DSC-16）。
編輯作用在資料庫內容的副本上，按「確認儲存」前不寫入資料庫或檔案（EDT-02、DSC-12-A1）；
只有「隱藏」按下即寫入資料庫（DSC-13）。
"""

from __future__ import annotations

import html
import ipaddress
import logging
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import QObject, QSize, Qt, QTimer, Signal
from PySide6.QtGui import QGuiApplication, QTextDocument
from PySide6.QtWidgets import (
    QAbstractItemView, QCheckBox, QComboBox, QDialog, QFileDialog, QFormLayout, QFrame, QHBoxLayout,
    QHeaderView, QInputDialog, QLabel, QLineEdit, QListWidget, QListWidgetItem, QMessageBox,
    QAbstractSpinBox, QPushButton, QScrollArea, QSpinBox, QStackedWidget, QStyle, QStyledItemDelegate,
    QTableWidget, QTableWidgetItem,
    QVBoxLayout, QWidget,
)

from .. import bootp, definition, lan, netinfo
from ..lan import DL_STATUSES, LIVE, MAINT, OTHER, RETIRED, STATUS_NAME, STATUS_SHORT, UNCLASSIFIED
from ..store import StoreError
from .theme import C, tag_style
from .widgets import Toast

log = logging.getLogger(__name__)

STATUS_ORDER = (UNCLASSIFIED, LIVE, MAINT, RETIRED, OTHER)
STATUS_HELP = {
    UNCLASSIFIED: "新偵測到、尚未確認身分。不配發 IP、不顯示在主畫面，紀錄保留在清單中。",
    LIVE: "配發固定 IP，連線讀取探頭，並顯示在主畫面。",
    MAINT: "暫時不使用（例如送修）。保留設定與 IP 配發，不連線、不顯示在主畫面；key、名稱與 IP 仍保留給它。",
    RETIRED: "已不再使用。不配發 IP、不顯示在主畫面；保留最後的設定供查詢，key、名稱與 IP 讓給其他設備。",
    OTHER: "不是 DL-EN1 的設備（例如協同合作設備、筆電）。只能設定 IP，留空表示不配發。",
}
COLS = ("", "設備", "名稱", "MAC", "IPv4", "最後出現", "次數")


def fmt_time(ts: datetime | None, full: bool = False) -> str:
    if ts is None:
        return "—"
    if not full and ts.date() == datetime.now().date():
        return ts.strftime("%H:%M:%S")
    return ts.strftime("%Y-%m-%d %H:%M")


def tag_html(status: str, hidden: bool = False, keyence_hint: bool = False) -> str:
    bg, fg = tag_style(status)
    out = (f'<span style="background:{bg};color:{fg};font-weight:700">&nbsp;{STATUS_SHORT[status]}&nbsp;</span>')
    if hidden:
        out += f' <span style="color:{C["ink-2"]};border:1px solid {C["line"]}">&nbsp;已隱藏&nbsp;</span>'
    if keyence_hint:
        out += f' <span style="background:{C["go-soft"]};color:{C["go"]}">&nbsp;可能是 DL-EN1&nbsp;</span>'
    return out


def _btn(text, kind=None, slot=None, width=None) -> QPushButton:
    b = QPushButton(text)
    if kind:
        b.setProperty("kind", kind)
    if slot:
        b.clicked.connect(slot)
    if width:
        b.setFixedWidth(width)
    b.setCursor(Qt.PointingHandCursor)
    return b


def _label(text="", name=None, wrap=False) -> QLabel:
    lb = QLabel(text)
    if name:
        lb.setObjectName(name)
    lb.setWordWrap(wrap)
    return lb


def _set_prop(w, name, value):
    if w.property(name) != value:
        w.setProperty(name, value)
        w.style().unpolish(w)
        w.style().polish(w)


class HtmlDelegate(QStyledItemDelegate):
    """以 HTML 繪製「設備」欄的類型標籤；選取列先畫選取底色（清單列狀態，5.10）。"""

    ROLE = Qt.UserRole + 1

    def _doc(self, index, option):
        doc = QTextDocument()
        doc.setDefaultFont(option.font)
        doc.setDocumentMargin(0)
        doc.setHtml(index.data(self.ROLE) or "")
        return doc

    def paint(self, painter, option, index):
        if option.state & QStyle.State_Selected:
            painter.fillRect(option.rect, option.palette.highlight())
        doc = self._doc(index, option)
        painter.save()
        painter.translate(option.rect.x() + 8, option.rect.y() + (option.rect.height() - doc.size().height()) / 2)
        doc.drawContents(painter)
        painter.restore()

    def sizeHint(self, option, index):
        doc = self._doc(index, option)
        return QSize(int(doc.idealWidth()) + 16, int(doc.size().height()) + 10)


class _Relay(QObject):
    """背景執行緒（ARP 探測）回到畫面執行緒。"""
    probed = Signal(str, object)


class SettingsDialog(QDialog):
    saved = Signal(object, object)  # (sync.ApplyResult, lan.Preview)

    def __init__(self, backend, parent=None, *, pending_serial: str | None = None, before_save=None):
        super().__init__(parent, Qt.Dialog | Qt.FramelessWindowHint)
        self.setObjectName("settings")
        self.setModal(True)
        self.backend = backend
        self.pending_serial = pending_serial      # 畫面上尚未寫入的量測結果編號（UPL-02）
        self.before_save = before_save            # 儲存前先寫入該結果
        self.original: dict[str, lan.LanDevice] = {}
        self.work: dict[str, lan.LanDevice] = {}
        self.remembered: dict[str, dict] = {}
        self.replaced_from: dict[str, str] = {}   # 新機 MAC → 舊機 MAC（DSC-14 探測時辨識舊機）
        self.ip_checks: dict[str, tuple[str, str, str]] = {}  # mac → (ip, 狀態, 文字)
        self.selected: str | None = None
        self.read_only = False
        self.issues: list[lan.Issue] = []
        self.preview: lan.Preview | None = None
        self._filling = False
        self._relay = _Relay()
        self._relay.probed.connect(self._on_probed)
        self._refresh_timer = QTimer(self, singleShot=True, interval=300, timeout=self._auto_refresh)

        self.setStyleSheet(f"#settings {{ background: {C['panel']}; border: 1px solid {C['line']}; }}")
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)
        outer.addWidget(self._header())
        self.pages = QStackedWidget()
        self.pages.addWidget(self._password_page())
        self.pages.addWidget(self._edit_page())
        self.pages.addWidget(self._confirm_page())
        outer.addWidget(self.pages, 1)
        self.toast = Toast(self)
        backend.devices_seen.connect(lambda _events: self._refresh_timer.start())
        self._size_for(0)

    # ================================================================ 版面

    def _size_for(self, page: int):
        screen = (self.parentWidget().screen() if self.parentWidget() else QGuiApplication.primaryScreen())
        geo = screen.availableGeometry()
        if page == 0:
            w, h = min(560, int(geo.width() * 0.96)), 300
        else:
            w = min(1240, int(geo.width() * 0.97))
            h = int(geo.height() * 0.92)
        self.resize(w, h)
        if self.parentWidget():
            pg = self.parentWidget().window().geometry()
            self.move(pg.x() + (pg.width() - w) // 2, pg.y() + (pg.height() - h) // 2)

    def _header(self) -> QWidget:
        bar = QFrame()
        bar.setStyleSheet(f"QFrame {{ border-bottom: 1px solid {C['line']}; }}")
        lay = QHBoxLayout(bar)
        lay.setContentsMargins(22, 12, 14, 12)
        lay.addWidget(_label("設備設定", "h1"))
        lay.addStretch()
        close = QPushButton("✕")
        close.setFlat(True)
        close.setStyleSheet(f"QPushButton {{ border: none; background: transparent; font-size: 22px;"
                            f" color: {C['ink-2']}; padding: 0 6px; }}")
        close.setCursor(Qt.PointingHandCursor)
        close.setToolTip("關閉")
        close.clicked.connect(self.reject)
        lay.addWidget(close)
        return bar

    def _footer(self, left: list, right: list) -> QFrame:
        bar = QFrame()
        bar.setStyleSheet(f"QFrame#footer {{ border-top: 1px solid {C['line']}; }}")
        bar.setObjectName("footer")
        lay = QHBoxLayout(bar)
        lay.setContentsMargins(22, 14, 22, 14)
        lay.setSpacing(10)
        for w in left:
            lay.addWidget(w)
        lay.addStretch()
        for w in right:
            lay.addWidget(w)
        return bar

    # ---------------------------------------------------------------- 步驟一：密碼（UPL-01）

    def _password_page(self) -> QWidget:
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(0, 0, 0, 0)
        body = QWidget()
        b = QVBoxLayout(body)
        b.setContentsMargins(22, 16, 22, 16)
        b.setSpacing(8)
        b.addWidget(_label("工程人員密碼", "h2"))
        self.pw_edit = QLineEdit()
        self.pw_edit.setEchoMode(QLineEdit.Password)
        self.pw_edit.setMaximumWidth(360)
        self.pw_edit.returnPressed.connect(self._check_password)
        self.pw_edit.textEdited.connect(lambda _: (_set_prop(self.pw_edit, "error", False), self.pw_msg.setText("")))
        b.addWidget(self.pw_edit)
        self.pw_msg = _label("", "note")
        self.pw_msg.setStyleSheet(f"color: {C['ng']}; font-weight: 700; font-size: 13px;")
        b.addWidget(self.pw_msg)
        b.addWidget(_label("此功能會變更 DL-EN1 的 IP 配發與畫面配置，限工程人員使用。", "note", True))
        b.addStretch()
        lay.addWidget(body, 1)
        self.btn_pw_ok = _btn("確認", "primary", self._check_password, 132)
        lay.addWidget(self._footer([], [_btn("取消", None, self.reject, 132), self.btn_pw_ok]))
        return page

    def _check_password(self):
        pw = self.pw_edit.text()
        if not pw:
            _set_prop(self.pw_edit, "error", True)
            self.pw_msg.setText("請輸入密碼")
            return
        if not self.backend.check_password(pw):
            _set_prop(self.pw_edit, "error", True)
            self.pw_msg.setText("密碼錯誤" if self.backend.cfg.engineer_password_sha256
                                else "尚未設定工程人員密碼（config.toml 的 engineer_password_sha256）")
            self.pw_edit.selectAll()
            return
        self.pw_edit.clear()
        self.enter_edit()

    def enter_edit(self):
        """通過密碼後載入資料並進入編輯步驟（測試可直接呼叫）。"""
        self.load()
        self.pages.setCurrentIndex(1)
        self._size_for(1)

    # ---------------------------------------------------------------- 步驟二：編輯

    def _edit_page(self) -> QWidget:
        page = QWidget()
        outer = QVBoxLayout(page)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        body = QWidget()
        body.setObjectName("editBody")
        body.setStyleSheet(f"#editBody {{ background: {C['panel']}; }}")
        b = QVBoxLayout(body)
        b.setContentsMargins(22, 16, 22, 16)
        b.setSpacing(16)

        self.db_banner = _label("", None, True)
        self.db_banner.setStyleSheet(f"background:{C['warn-soft']};color:{C['warn']};font-weight:700;"
                                     f"font-size:15px;padding:8px 12px;border-radius:4px;")
        self.db_banner.hide()
        b.addWidget(self.db_banner)

        cols = QHBoxLayout()
        cols.setSpacing(16)
        cols.addWidget(self._list_panel(), 155)
        cols.addWidget(self._detail_panel(), 100)
        b.addLayout(cols, 1)

        msg_title = QHBoxLayout()
        msg_title.addWidget(_label("檢查訊息", "h2"))
        msg_title.addStretch()
        b.addLayout(msg_title)
        self.msg_list = QListWidget()
        self.msg_list.setMinimumHeight(72)
        self.msg_list.setMaximumHeight(140)
        self.msg_list.itemClicked.connect(self._on_message_clicked)
        b.addWidget(self.msg_list)
        scroll.setWidget(body)
        outer.addWidget(scroll, 1)

        self.dirty_label = _label("")
        self.dirty_label.setStyleSheet(f"color:{C['warn']};font-weight:700;font-size:15px;")
        self.btn_import = _btn("匯入…", "small", self._import)
        self.btn_restore = _btn("從備份還原…", "small", self._restore)
        self.btn_download = _btn("下載目前設定", "small", self._download)
        self.btn_refresh = _btn("重新整理", None, lambda: self._refresh(manual=True), 132)
        self.btn_save = _btn("儲存", "primary", self._go_confirm, 132)
        self.btn_close = _btn("關閉", None, self.reject, 132)
        outer.addWidget(self._footer(
            [self.btn_import, self.btn_restore, self.btn_download, self.dirty_label],
            [self.btn_refresh, self.btn_save, self.btn_close]))
        return page

    def _panel(self) -> tuple[QFrame, QVBoxLayout]:
        f = QFrame()
        f.setObjectName("panel2")
        f.setStyleSheet(f"QFrame#panel2 {{ background:{C['panel-2']}; border:1px solid {C['line']}; border-radius:6px; }}")
        lay = QVBoxLayout(f)
        lay.setContentsMargins(14, 12, 14, 12)
        lay.setSpacing(8)
        return f, lay

    def _list_panel(self) -> QWidget:
        f, lay = self._panel()
        title = QHBoxLayout()
        title.addWidget(_label("偵測到的設備清單", "h2"))
        title.addWidget(_label("送出 BOOTP／DHCP 請求的設備每台一列，自動更新", "note"))
        title.addStretch()
        lay.addLayout(title)
        self.list_hint = _label("", None, True)
        self.list_hint.setStyleSheet(f"font-size:15px;color:{C['ink-2']};")
        lay.addWidget(self.list_hint)

        t = self.table = QTableWidget(0, len(COLS))
        t.setHorizontalHeaderLabels(COLS)
        t.verticalHeader().hide()
        t.setSelectionBehavior(QAbstractItemView.SelectRows)
        t.setSelectionMode(QAbstractItemView.SingleSelection)
        t.setEditTriggers(QAbstractItemView.NoEditTriggers)
        t.setShowGrid(False)
        t.setMinimumHeight(270)
        t.setFocusPolicy(Qt.NoFocus)
        h = t.horizontalHeader()
        h.setHighlightSections(False)
        h.setSectionResizeMode(QHeaderView.ResizeToContents)
        h.setSectionResizeMode(2, QHeaderView.Stretch)
        h.setMinimumSectionSize(28)
        t.setItemDelegateForColumn(1, HtmlDelegate(t))
        t.itemSelectionChanged.connect(self._on_row_selected)
        lay.addWidget(t, 1)

        row = QHBoxLayout()
        self.btn_hide = _btn("隱藏", "small", self._toggle_hidden)
        self.btn_up = _btn("上移", "small", lambda: self._move(-1))
        self.btn_down = _btn("下移", "small", lambda: self._move(1))
        for w in (self.btn_hide, self.btn_up, self.btn_down):
            row.addWidget(w)
        row.addStretch()
        self.chk_hidden = QCheckBox("顯示已隱藏（0）")
        self.chk_hidden.toggled.connect(lambda _: self._render_list())
        row.addWidget(self.chk_hidden)
        lay.addLayout(row)
        return f

    def _detail_panel(self) -> QWidget:
        f, lay = self._panel()
        lay.addWidget(_label("偵測到的設備", "h2"))
        self.detail_empty = _label("在左側清單選擇一台設備。", "label", True)
        lay.addWidget(self.detail_empty)

        self.detail = QWidget()
        d = QVBoxLayout(self.detail)
        d.setContentsMargins(0, 0, 0, 0)
        d.setSpacing(10)
        self.info = QLabel()
        self.info.setTextFormat(Qt.RichText)
        self.info.setStyleSheet(f"background:{C['panel']};border:1px solid {C['line']};padding:8px 10px;"
                                f"font-size:15px;")
        self.info.setWordWrap(True)
        d.addWidget(self.info)

        form = self.form = QFormLayout()
        form.setLabelAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        form.setHorizontalSpacing(12)
        form.setVerticalSpacing(8)
        self.status_box = QComboBox()
        self.status_box.setProperty("kind", "status")
        for s in STATUS_ORDER:
            self.status_box.addItem(STATUS_NAME[s], s)
        self.status_box.currentIndexChanged.connect(self._on_status_changed)
        status_col = QVBoxLayout()
        status_col.setSpacing(4)
        status_col.addWidget(self.status_box)
        self.status_help = _label("", "note", True)
        status_col.addWidget(self.status_help)
        self._form_row("設備", status_col)

        self.key_edit = self._line("小寫英數，例：front", "key")
        self._form_row("識別碼 key", self.key_edit)
        self.name_edit = self._line("例：前排", "name")
        self._form_row("排名稱 name", self.name_edit)
        ip_col = QVBoxLayout()
        ip_col.setSpacing(4)
        self.ip_edit = self._line("例：192.168.10.11", "ipv4", num=True)
        self.ip_edit.editingFinished.connect(self._start_probe_selected)
        ip_col.addWidget(self.ip_edit)
        self.ip_note = _label("", "note", True)
        ip_col.addWidget(self.ip_note)
        self._form_row("IPv4", ip_col)
        self.port_edit = self._line("64000（未填寫時）", "port", num=True)
        self._form_row("TCP 埠 port", self.port_edit)
        self.max_spin = QSpinBox()
        self.max_spin.setRange(1, 15)
        self.max_spin.setProperty("num", True)
        self.max_spin.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.max_spin.setMaximumWidth(120)
        self.max_spin.valueChanged.connect(self._on_field_edited)
        self._form_row("最多探頭數", self.max_spin)
        d.addLayout(form)

        self.note_box = _label("", None, True)
        self.note_box.setStyleSheet(f"background:{C['panel']};border:1px solid {C['line']};padding:10px 12px;"
                                    f"font-size:15px;line-height:150%;")
        d.addWidget(self.note_box)

        self.probe_box = QWidget()
        pb = QVBoxLayout(self.probe_box)
        pb.setContentsMargins(0, 0, 0, 0)
        pb.setSpacing(6)
        pb.addWidget(_label("已安裝的探頭", "label"))
        pt = self.probe_table = QTableWidget(0, 2)
        pt.setHorizontalHeaderLabels(("探頭 ID", "位置名稱"))
        pt.verticalHeader().hide()
        pt.setSelectionBehavior(QAbstractItemView.SelectRows)
        pt.setSelectionMode(QAbstractItemView.SingleSelection)
        pt.setMinimumHeight(180)
        pt.setMaximumHeight(180)
        pt.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        pt.setColumnWidth(0, 110)
        pt.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        pt.itemChanged.connect(lambda _item: self._on_field_edited())
        pb.addWidget(pt)
        prow = QHBoxLayout()
        self.btn_probe_add = _btn("新增探頭", "small", self._add_probe)
        self.btn_probe_del = _btn("刪除探頭", "small", self._del_probe)
        prow.addWidget(self.btn_probe_add)
        prow.addWidget(self.btn_probe_del)
        prow.addStretch()
        pb.addLayout(prow)
        d.addWidget(self.probe_box)

        self.replace_row = QWidget()
        rr = QHBoxLayout(self.replace_row)
        rr.setContentsMargins(0, 0, 0, 0)
        self.btn_replace = _btn("替換…", "small", self._open_replace)
        rr.addWidget(self.btn_replace)
        rr.addWidget(_label("DL-EN1 故障換新機時使用", "note"))
        rr.addStretch()
        d.addWidget(self.replace_row)

        self.replace_area = QFrame()
        self.replace_area.setStyleSheet(f"QFrame#ra {{ border:2px solid {C['ink-2']}; border-radius:6px;"
                                        f" background:{C['panel']}; }}")
        self.replace_area.setObjectName("ra")
        ra = QVBoxLayout(self.replace_area)
        ra.setContentsMargins(12, 10, 12, 10)
        self.replace_title = _label("", "h2")
        ra.addWidget(self.replace_title)
        ra.addWidget(_label("新機（只列出偵測到的設備；KEYENCE 優先、最近出現的在前）", "label", True))
        self.replace_box = QComboBox()
        ra.addWidget(self.replace_box)
        ra.addWidget(_label("新機取得此台全部設定（key、名稱、IP、埠、探頭、順序）並設為使用中；"
                            "此台改為「DL-EN1 已停用」並保留原設定。新機須先上電讓系統偵測到。", "note", True))
        rb = QHBoxLayout()
        rb.addStretch()
        rb.addWidget(_btn("取消", "small", lambda: self.replace_area.hide()))
        self.btn_replace_ok = _btn("確認替換", "small", self._do_replace)
        rb.addWidget(self.btn_replace_ok)
        ra.addLayout(rb)
        self.replace_area.hide()
        d.addWidget(self.replace_area)
        d.addStretch()
        lay.addWidget(self.detail, 1)
        self.detail.hide()
        return f

    def _form_row(self, text, field):
        lb = _label(text, "label")
        lb.setFixedWidth(120)
        self.form.addRow(lb, field)

    def _line(self, placeholder, name, num=False) -> QLineEdit:
        e = QLineEdit()
        e.setPlaceholderText(placeholder)
        e.setObjectName(name)
        if num:
            e.setProperty("num", True)
        e.textEdited.connect(lambda _t: self._on_field_edited())
        return e

    # ---------------------------------------------------------------- 步驟三：確認儲存

    def _confirm_page(self) -> QWidget:
        page = QWidget()
        outer = QVBoxLayout(page)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        self.confirm_body = QWidget()
        self.confirm_body.setObjectName("confirmBody")
        self.confirm_body.setStyleSheet(f"#confirmBody {{ background:{C['panel']}; }}")
        self.confirm_lay = QVBoxLayout(self.confirm_body)
        self.confirm_lay.setContentsMargins(22, 16, 22, 16)
        self.confirm_lay.setSpacing(10)
        scroll.setWidget(self.confirm_body)
        outer.addWidget(scroll, 1)
        self.btn_back = _btn("返回修改", None, self._back_to_edit, 132)
        self.btn_commit = _btn("確認儲存", "primary", self._commit, 132)
        outer.addWidget(self._footer([], [self.btn_back, self.btn_commit]))
        return page

    # ================================================================ 資料

    def load(self):
        try:
            devices = self.backend.load_devices()
            self.read_only = False
        except StoreError as exc:
            log.error("設備設定：無法讀取資料庫：%s", exc)
            devices = self.backend.cached_devices()
            self.read_only = True
        self.original = {d.mac: d.copy() for d in devices}
        self.work = {d.mac: d.copy() for d in devices}
        self.remembered.clear()
        self.replaced_from.clear()
        self._import_label = ""
        self.ip_checks.clear()
        if self.read_only:
            self.db_banner.setText("無法讀取資料庫：清單為上次讀到的資料與尚未寫入的探索紀錄，暫時無法儲存。"
                                   "資料庫恢復後按「重新整理」。")
        self.db_banner.setVisible(self.read_only)
        if self.selected not in self.work:
            first = next(iter(self._visible_devices()), None)
            self.selected = first.mac if first else None
        self._render_all()

    def _devices(self) -> list[lan.LanDevice]:
        return list(self.work.values())

    def _visible_devices(self):
        show = self.chk_hidden.isChecked()
        return [d for d in lan.list_order(self._devices()) if show or not d.hidden or d.mac == self.selected]

    def is_dirty(self) -> bool:
        if set(self.work) - set(self.original):
            return True
        return any(self.work[m].settings() != self.original[m].settings() for m in self.work)

    def _refresh(self, manual=False):
        """重新讀取資料庫：探索欄位更新、新設備加入；編輯中的設定保留（DSC-02 自動更新）。"""
        try:
            fresh = self.backend.load_devices()
        except StoreError:
            if manual:
                self.toast.show_text("無法讀取資料庫，清單未更新")
            return
        if self.read_only:  # 資料庫恢復：重新載入
            self.load()
            self.toast.show_text("資料庫已恢復，清單已重新載入")
            return
        new_unknown = 0
        for f in fresh:
            for target in (self.original, self.work):
                d = target.get(f.mac)
                if d is None:
                    target[f.mac] = f.copy()
                    if target is self.work and f.status == UNCLASSIFIED:
                        new_unknown += 1
                    continue
                d.first_seen, d.last_seen, d.seen_count = f.first_seen, f.last_seen, f.seen_count
                d.last_request, d.hostname, d.vendor_class = f.last_request, f.hostname, f.vendor_class
                if target is self.original or not d.is_dl_en1:  # 編輯中設為 DL-EN1 者已取消隱藏
                    d.hidden, d.hidden_at = f.hidden, f.hidden_at
        self._render_list()
        self._render_info()
        if new_unknown:
            self.toast.show_text(f"偵測到 {new_unknown} 台新設備，已以「不明設備」加入清單")
        elif manual:
            self.toast.show_text("清單已更新")

    def _auto_refresh(self):
        if self.pages.currentIndex() in (1, 2):
            self._refresh()

    # ================================================================ 呈現

    def _render_all(self):
        self._validate()
        self._render_list()
        self._render_detail()
        self._render_messages()
        self._update_buttons()

    def _validate(self):
        self.issues = lan.validate(self._devices(), self.backend.equip_net())

    def _row_issue_macs(self) -> set:
        macs = {i.mac for i in self.issues if i.mac}
        macs |= {m for m, (_ip, st, _t) in self.ip_checks.items() if st == "taken"}
        return macs

    def _render_list(self):
        t = self.table
        devs = self._visible_devices()
        hidden_n = sum(1 for d in self._devices() if d.hidden)
        self.chk_hidden.setText(f"顯示已隱藏（{hidden_n}）")
        unk = sum(1 for d in self._devices() if d.status == UNCLASSIFIED and not d.hidden)
        if not self._devices():
            self.list_hint.setText("尚無偵測到的設備；設備上電並送出 BOOTP／DHCP 請求後會自動出現在清單中。")
        elif unk:
            self.list_hint.setText(f"有 {unk} 台不明設備，請在右側選擇設備類型；不需要的設備可以隱藏。")
        else:
            self.list_hint.setText(f"已隱藏 {hidden_n} 台。" if hidden_n else "")
        self.list_hint.setVisible(bool(self.list_hint.text()))

        bad = self._row_issue_macs()
        net = self.backend.equip_net().network
        self._filling = True
        t.setRowCount(0)
        t.setRowCount(len(devs))
        sel_row = None
        for r, d in enumerate(devs):
            selected = d.mac == self.selected
            if selected:
                sel_row = r
            fg = C["ng"] if d.mac in bad else (C["ink"] if d.is_dl_en1 or d.status == UNCLASSIFIED else C["ink-2"])
            ip = d.ipv4 if d.assigns_ip else "不配發"
            if d.assigns_ip:
                try:
                    if ipaddress.IPv4Address(d.ipv4) not in net:
                        ip = f"{d.ipv4}（IP 不在設備網段）"
                except ValueError:
                    pass
            cells = ["✘" if d.mac in bad else "", "", d.name or "—", d.mac, ip,
                     fmt_time(d.last_seen), str(d.seen_count)]
            for c, text in enumerate(cells):
                item = QTableWidgetItem(text)
                item.setData(Qt.UserRole, d.mac)
                item.setForeground(Qt.white if selected else self._qcolor(fg))
                if c in (3, 4, 5, 6):
                    item.setFont(self._num_font())
                if c == 6:
                    item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                t.setItem(r, c, item)
            t.item(r, 1).setData(HtmlDelegate.ROLE,
                                 tag_html(d.status, d.hidden, d.status == UNCLASSIFIED and d.keyence))
        if sel_row is not None:
            t.selectRow(sel_row)
        else:
            t.clearSelection()
        self._filling = False

    @staticmethod
    def _qcolor(hex_):
        from PySide6.QtGui import QColor
        return QColor(hex_)

    @staticmethod
    def _num_font():
        from .theme import num_font
        return num_font(15)

    def _render_info(self):
        d = self.work.get(self.selected)
        if not d:
            return
        badge = (f' <span style="background:{C["go-soft"]};color:{C["go"]};font-size:13px">'
                 f'&nbsp;KEYENCE｜可能是 DL-EN1&nbsp;</span>' if d.keyence else "")
        rows = [("MAC", f'<b style="font-family:\'Barlow Semi Condensed\';font-size:17px">{d.mac}</b>{badge}'),
                ("首次出現", fmt_time(d.first_seen, full=True) if d.first_seen else "尚未出現（匯入建立）"),
                ("最後出現", f"{fmt_time(d.last_seen)}（{d.last_request or '—'}，共 {d.seen_count} 次）"
                 if d.last_seen else "—")]
        if d.hostname:
            rows.append(("主機名稱", html.escape(d.hostname)))
        if d.vendor_class:
            rows.append(("廠商識別", html.escape(d.vendor_class)))
        self.info.setText("<table cellspacing=0 cellpadding=2>" + "".join(
            f'<tr><td style="color:{C["ink-2"]};padding-right:14px">{k}</td><td>{v}</td></tr>'
            for k, v in rows) + "</table>")

    def _render_detail(self):
        d = self.work.get(self.selected)
        self.detail.setVisible(d is not None)
        self.detail_empty.setVisible(d is None)
        self.replace_area.hide()
        if d is None:
            return
        self._filling = True
        self._render_info()
        self.status_box.setCurrentIndex(STATUS_ORDER.index(d.status))
        self.status_box.setEnabled(not self.read_only)
        self.status_help.setText(STATUS_HELP[d.status])
        dl = d.is_dl_en1
        cfg = d.config or {}
        for row, visible in ((1, dl), (2, dl), (3, dl or d.status == OTHER), (4, dl), (5, dl)):
            self.form.setRowVisible(row, visible)
        self.key_edit.setText(cfg.get("key") or "")
        self.name_edit.setText(cfg.get("name") or "")
        self.ip_edit.setText(d.ipv4 or "" if (dl or d.status == OTHER) else "")
        self.port_edit.setText("" if cfg.get("port") is None else str(cfg.get("port")))
        mp = cfg.get("max_probes")
        self.max_spin.setValue(mp if isinstance(mp, int) and 1 <= mp <= 15 else 4)
        self.probe_box.setVisible(dl)
        self.probe_table.setRowCount(0)
        for p in cfg.get("probes") or []:
            self._append_probe_row(p.get("id"), p.get("description", ""))
        self.replace_row.setVisible(d.status == LIVE and self.original.get(d.mac) is not None
                                    and self.original[d.mac].status == LIVE)
        for w in (self.key_edit, self.name_edit, self.ip_edit, self.port_edit):
            w.setReadOnly(self.read_only)
        self.max_spin.setEnabled(not self.read_only)
        self.probe_table.setEnabled(not self.read_only)

        if d.status == OTHER:
            self.note_box.setText("只能設定 IP。若它其實是 DL-EN1，請將「設備」改為「DL-EN1 使用中」。")
        elif d.status == UNCLASSIFIED:
            self.note_box.setText("尚未確認身分：不配發 IP、不顯示在主畫面，紀錄會保留在清單中。"
                                  "確認後請選擇設備類型；不需要的設備可以在左側「隱藏」。")
        elif d.status == RETIRED:
            if cfg:
                self.note_box.setText(
                    f"最後的設定：識別碼 {cfg.get('key') or '—'}、排名稱 {cfg.get('name') or '—'}、"
                    f"IP {d.ipv4 or '—'}、探頭 {len(cfg.get('probes') or [])} 個。\n"
                    "已停用的設備不佔用 key、名稱與 IP。改回「DL-EN1 使用中」或「維修中」會帶回這些設定，"
                    "並重新檢查是否與現有設備重複。")
            else:
                self.note_box.setText("沒有保留的設定。改回「DL-EN1 使用中」或「維修中」後再填寫設定。")
        self.note_box.setVisible(d.status in (OTHER, UNCLASSIFIED, RETIRED))
        self._filling = False
        self._render_field_errors()
        self._render_ip_note()

    def _append_probe_row(self, pid, desc):
        r = self.probe_table.rowCount()
        self.probe_table.insertRow(r)
        id_item = QTableWidgetItem("" if pid is None else str(pid))
        id_item.setFont(self._num_font())
        self.probe_table.setItem(r, 0, id_item)
        self.probe_table.setItem(r, 1, QTableWidgetItem(desc))

    def _render_field_errors(self):
        mine = {i.field for i in self.issues if i.mac == self.selected}
        for fld, w in (("key", self.key_edit), ("name", self.name_edit), ("port", self.port_edit),
                       ("max_probes", self.max_spin)):
            _set_prop(w, "error", fld in mine)
        ip_bad = "ipv4" in mine or self.ip_checks.get(self.selected, ("", "", ""))[1] == "taken"
        _set_prop(self.ip_edit, "error", ip_bad)
        self.probe_table.setStyleSheet(f"QTableWidget {{ border: 2px solid {C['ng']}; }}"
                                       if "probes" in mine else "")

    def _render_ip_note(self):
        d = self.work.get(self.selected)
        if not d or not (d.is_dl_en1 or d.status == OTHER):
            return
        mine = [i for i in self.issues if i.mac == d.mac and i.field == "ipv4"]
        check = self.ip_checks.get(d.mac)
        color, bold = C["ink-2"], False
        if mine:  # 資料表中的衝突優先顯示（5.10 IPv4 檢查）
            text, color, bold = mine[0].message, C["ng"], True
        elif not d.ipv4:
            text = "留空表示不配發 IP。" if d.status == OTHER else ""
        elif not self._needs_probe(d):
            text = "使用中的 IP，未變更"
        elif check and check[0] == d.ipv4:
            text = check[2]
            color = {"checking": C["ink-2"], "ok": C["go"], "taken": C["ng"], "warn": C["warn"]}[check[1]]
            bold = check[1] in ("taken", "warn")
        else:
            text = "尚未檢查網路上是否已有設備使用此 IP（離開欄位後自動檢查）"
        self.ip_note.setText(text)
        self.ip_note.setStyleSheet(f"font-size:13px;color:{color};{'font-weight:700;' if bold else ''}")

    def _render_messages(self):
        self.msg_list.clear()
        bad = list(self.issues)
        for mac, (ip, st, text) in self.ip_checks.items():
            d = self.work.get(mac)
            if st == "taken" and d and d.ipv4 == ip and d.assigns_ip:
                bad.append(lan.Issue(mac, "ipv4", text, d.label()))
        _set_prop(self.msg_list, "error", bool(bad))
        if bad:
            for i in bad:
                item = QListWidgetItem("✘ " + i.text())
                item.setForeground(self._qcolor(C["ng"]))
                item.setData(Qt.UserRole, i.mac)
                self.msg_list.addItem(item)
            return
        devs = self._devices()
        cnt = lambda s: sum(1 for d in devs if d.status == s)  # noqa: E731
        probes = sum(len((d.config or {}).get("probes") or []) for d in devs if d.status == LIVE)
        text = (f"✔ 檢查通過：DL-EN1 使用中 {cnt(LIVE)} 台（{probes} 個探頭）、維修中 {cnt(MAINT)} 台、"
                f"已停用 {cnt(RETIRED)} 台、其他設備 {cnt(OTHER)} 台、不明設備 {cnt(UNCLASSIFIED)} 台，可以儲存。")
        if self._checking():
            text = "檢查中：確認網路上是否已有設備使用此 IP"
        item = QListWidgetItem(text)
        f = item.font()
        f.setBold(True)
        item.setFont(f)
        item.setForeground(self._qcolor(C["ink-2"] if self._checking() else C["go"]))
        self.msg_list.addItem(item)

    def _checking(self) -> bool:
        return any(st == "checking" and self.work.get(m) and self.work[m].ipv4 == ip
                   for m, (ip, st, _t) in self.ip_checks.items())

    def _blocked_by_probe(self) -> bool:
        return any(st == "taken" and self.work.get(m) and self.work[m].ipv4 == ip and self.work[m].assigns_ip
                   for m, (ip, st, _t) in self.ip_checks.items())

    def _update_buttons(self):
        d = self.work.get(self.selected)
        dirty = self.is_dirty()
        self.dirty_label.setText("● 有尚未儲存的變更" if dirty else "")
        self.btn_save.setEnabled(dirty and not self.issues and not self._checking()
                                 and not self._blocked_by_probe() and not self.read_only)
        o = self.original.get(self.selected)
        can_hide = d is not None and not d.is_dl_en1 and not (o and o.is_dl_en1) and not self.read_only
        self.btn_hide.setEnabled(can_hide)
        self.btn_hide.setText("取消隱藏" if d and d.hidden else "隱藏")
        live = lan.live_devices(self._devices())
        idx = next((i for i, x in enumerate(live) if d and x.mac == d.mac), None)
        self.btn_up.setEnabled(idx is not None and idx > 0 and not self.read_only)
        self.btn_down.setEnabled(idx is not None and idx < len(live) - 1 and not self.read_only)
        for b in (self.btn_import, self.btn_restore):
            b.setEnabled(not self.read_only)
        self.btn_probe_del.setEnabled(self.probe_table.currentRow() >= 0)

    # ================================================================ 操作

    def _on_row_selected(self):
        if self._filling:
            return
        rows = self.table.selectionModel().selectedRows()
        if not rows:
            return
        mac = self.table.item(rows[0].row(), 0).data(Qt.UserRole)
        if mac != self.selected:
            self.select(mac)

    def select(self, mac: str):
        self.selected = mac
        if self.work[mac].hidden and not self.chk_hidden.isChecked():
            self.chk_hidden.setChecked(True)
        self._render_list()
        self._render_detail()
        self._update_buttons()

    def _on_message_clicked(self, item):
        mac = item.data(Qt.UserRole)
        if mac and mac in self.work:
            self.select(mac)

    def _on_status_changed(self, index):
        if self._filling or self.selected is None:
            return
        status = STATUS_ORDER[index]
        lan.set_status(self._devices(), self.selected, status, self.backend.equip_net(),
                       self.backend.cfg.ip_range, self.remembered)
        self._after_change(rebuild_detail=True)
        self._start_probe_selected()

    def _on_field_edited(self):
        """每次輸入即重新檢查；輸入中不重建表單（5.10 即時檢查）。"""
        if self._filling or self.selected is None:
            return
        d = self.work[self.selected]
        if d.is_dl_en1:
            cfg = d.config = dict(d.config or {})
            cfg["key"] = self.key_edit.text().strip()
            cfg["name"] = self.name_edit.text().strip()
            port = self.port_edit.text().strip()
            if port:
                cfg["port"] = int(port) if port.isdigit() else port
            else:
                cfg.pop("port", None)
            cfg["max_probes"] = self.max_spin.value()
            probes = []
            for r in range(self.probe_table.rowCount()):
                pid = (self.probe_table.item(r, 0).text() if self.probe_table.item(r, 0) else "").strip()
                desc = (self.probe_table.item(r, 1).text() if self.probe_table.item(r, 1) else "").strip()
                probes.append({"id": int(pid) if pid.isdigit() else pid, "description": desc})
            cfg["probes"] = probes
            # 保持 3.7.1 欄位順序
            d.config = {k: cfg[k] for k in ("key", "name", "port", "max_probes", "probes") if k in cfg}
        if d.is_dl_en1 or d.status == OTHER:
            ip = self.ip_edit.text().strip()
            d.ipv4 = ip or None
        self._after_change()

    def _after_change(self, rebuild_detail=False):
        self._validate()
        self._render_list()
        if rebuild_detail:
            self._render_detail()
        else:
            self._render_field_errors()
            self._render_ip_note()
        self._render_messages()
        self._update_buttons()

    def _add_probe(self):
        used = set()
        for r in range(self.probe_table.rowCount()):
            item = self.probe_table.item(r, 0)
            if item and item.text().strip().isdigit():
                used.add(int(item.text()))
        pid = next((i for i in range(1, 16) if i not in used), None)
        self._filling = True
        self._append_probe_row(pid, "")
        self._filling = False
        if pid and pid > self.max_spin.value():
            self.max_spin.setValue(min(pid, 15))
        self.probe_table.setCurrentCell(self.probe_table.rowCount() - 1, 1)
        self._on_field_edited()

    def _del_probe(self):
        r = self.probe_table.currentRow()
        if r >= 0:
            self.probe_table.removeRow(r)
            self._on_field_edited()

    def _toggle_hidden(self):
        """隱藏：只影響清單顯示，按下即寫入資料庫、不需儲存（DSC-13）。"""
        d = self.work.get(self.selected)
        if d is None or d.is_dl_en1:
            return
        hidden = not d.hidden
        try:
            self.backend.set_hidden(d.mac, hidden)
        except StoreError as exc:
            self._warn(f"無法寫入資料庫：{exc}")
            return
        for target in (self.original, self.work):
            if d.mac in target:
                target[d.mac].hidden = hidden
                target[d.mac].hidden_at = datetime.now() if hidden else None
        self.toast.show_text(f"已隱藏 {d.mac}（不影響 IP 配發與探索）" if hidden else f"已取消隱藏 {d.mac}")
        if hidden and not self.chk_hidden.isChecked():
            nxt = next((x for x in self._visible_devices() if x.mac != d.mac and not x.hidden), None)
            self.selected = nxt.mac if nxt else None
            self._render_detail()
        self._render_list()
        self._update_buttons()

    def _move(self, step):
        if self.selected and lan.move(self._devices(), self.selected, step):
            self._after_change()

    # ---------------------------------------------------------------- IP 探測（DSC-10）

    def _needs_probe(self, d: lan.LanDevice) -> bool:
        """新設定或變更的 IP 才探測；IP 未變更者不探測（DSC-10-A1）。"""
        o = self.original.get(d.mac)
        old_ip = o.ipv4 if o is not None and o.assigns_ip else None
        return bool(d.assigns_ip and d.ipv4 != old_ip)

    def _start_probe_selected(self):
        if self.selected:
            self.start_probe(self.selected)

    def start_probe(self, mac: str):
        d = self.work.get(mac)
        if not d or not d.ipv4 or not self._needs_probe(d):
            self._render_ip_note()
            return
        if lan.ip_problem(d.ipv4, self.backend.equip_net()) or lan.occupant(self._devices(), d.ipv4, mac):
            self._render_ip_note()
            return
        cur = self.ip_checks.get(mac)
        if cur and cur[0] == d.ipv4 and cur[1] != "checking":
            return
        self.ip_checks[mac] = (d.ipv4, "checking", "檢查中…（ARP 探測）")
        ip = d.ipv4
        self.backend.probe_async(ip, mac, lambda result: self._relay.probed.emit(mac, result))
        self._render_ip_note()
        self._render_messages()
        self._update_buttons()

    def _on_probed(self, mac: str, result: netinfo.ProbeResult):
        d = self.work.get(mac)
        if d is None or d.ipv4 != result.ip:
            return  # IP 已再修改，結果作廢
        old_mac = self.replaced_from.get(mac)
        if result.status == netinfo.TAKEN and old_mac and result.mac == old_mac:
            st = "warn"  # 替換時舊機仍在線上：只提示，不阻擋（DSC-14-A4）
        else:
            st = {netinfo.FREE: "ok", netinfo.SELF: "ok", netinfo.TAKEN: "taken", netinfo.UNKNOWN: "warn"}[result.status]
        self.ip_checks[mac] = (result.ip, st, result.text(old_mac))
        self._render_list()
        self._render_field_errors()
        self._render_ip_note()
        self._render_messages()
        self._update_buttons()

    # ---------------------------------------------------------------- 替換（DSC-14）

    def _open_replace(self):
        d = self.work.get(self.selected)
        if not d or d.status != LIVE:
            return
        cfg = d.config or {}
        self.replace_title.setText(f"替換 {cfg.get('name')}（{cfg.get('key')}）")
        self.replace_box.clear()
        for c in lan.replace_candidates(self._devices(), d.mac):
            hint = "｜可能是 DL-EN1" if c.keyence else ""
            self.replace_box.addItem(f"{c.mac}　{STATUS_SHORT[c.status]}　最後出現 {fmt_time(c.last_seen)}{hint}", c.mac)
        empty = self.replace_box.count() == 0
        if empty:
            self.replace_box.addItem("沒有可用的新機：請先將新機接上設備網路並上電")
        self.replace_box.setEnabled(not empty)
        self.btn_replace_ok.setEnabled(not empty)
        self.replace_area.show()

    def _do_replace(self):
        old_mac, new_mac = self.selected, self.replace_box.currentData()
        if not new_mac:
            return
        lan.replace(self._devices(), old_mac, new_mac)
        self.replaced_from[new_mac] = old_mac
        log.info("設備設定：替換（未儲存）舊機=%s 新機=%s", old_mac, new_mac)
        self.selected = new_mac
        self._after_change(rebuild_detail=True)
        self.start_probe(new_mac)

    # ---------------------------------------------------------------- 匯入、還原、下載（UPL）

    def _import(self):
        path, _ = QFileDialog.getOpenFileName(self, "匯入定義檔", str(Path.home()), "DL-EN1 定義檔 (*.json)")
        if path:
            self.import_file(Path(path))

    def import_file(self, path: Path, label: str | None = None):
        try:
            defn = self.backend.read_definition(path)
        except bootp.DefinitionError as exc:
            self._warn("定義檔有錯誤，未匯入：\n" + "\n".join(f"• {w}：{r}" for w, r in exc.errors[:30]))
            log.warning("匯入定義檔失敗 file=%s 原因=%s", path, exc.errors)
            return
        except OSError as exc:
            self._warn(f"無法讀取檔案：{exc}")
            return
        imported = lan.import_definition(self._devices(), defn)
        self.work = {d.mac: d for d in imported}
        log.info("匯入定義檔（未儲存）file=%s DL-EN1 %d 台", path, len(defn["dl_en1"]))
        self._import_label = label or f"匯入 {path.name}"
        self._validate()
        self._render_all()
        if not self.issues:
            self._go_confirm()

    def _restore(self):
        files = self.backend.backups()
        if not files:
            self._info("目前沒有備份。")
            return
        labels = []
        for f in files:
            stamp = f.name.rsplit(".", 1)[-1]
            try:
                labels.append(datetime.strptime(stamp, "%Y%m%d-%H%M%S-%f").strftime("%Y-%m-%d %H:%M:%S"))
            except ValueError:
                labels.append(f.name)
        choice, ok = QInputDialog.getItem(self, "從備份還原", "選擇備份（最近 20 份）：", labels, 0, False)
        if ok:
            self.import_file(files[labels.index(choice)], label=f"從備份還原 {choice}")

    def _download(self):
        defn = lan.definition_from(self.original.values())
        path, _ = QFileDialog.getSaveFileName(self, "下載目前設定", str(Path.home() / "dl-en1.json"),
                                              "DL-EN1 定義檔 (*.json)")
        if not path:
            return
        try:
            Path(path).write_text(definition.dumps(defn), encoding="utf-8")
        except OSError as exc:
            self._warn(f"無法寫入檔案：{exc}")
            return
        self.toast.show_text(f"已下載目前設定：{path}")

    # ---------------------------------------------------------------- 確認儲存

    def _go_confirm(self):
        self.preview = lan.diff(self.original.values(), self._devices(), self.backend.standards())
        self._render_confirm()
        self.pages.setCurrentIndex(2)

    def _back_to_edit(self):
        self.pages.setCurrentIndex(1)
        self._render_all()

    def _render_confirm(self):
        lay = self.confirm_lay
        while lay.count():
            w = lay.takeAt(0).widget()
            if w:
                w.deleteLater()
        p = self.preview
        lay.addWidget(_label("確認儲存", "h2"))
        if p.empty:
            lay.addWidget(_label("沒有任何變更。", "label"))
        for item in p.items:
            lines = "".join(
                (f'<br><span style="background:{C["ng-soft"]};color:{C["ng"]};font-weight:700">'
                 f'&nbsp;{html.escape(t)}&nbsp;</span>' if hot else f"<br>{html.escape(t)}")
                for t, hot in item.lines)
            box = QLabel(f'<b>【{item.tag}】{html.escape(item.title)}</b>{lines}')
            box.setTextFormat(Qt.RichText)
            box.setWordWrap(True)
            box.setStyleSheet(f"background:{C['panel-2']};border:1px solid {C['line']};border-radius:6px;"
                              f"padding:10px 14px;font-size:15px;")
            lay.addWidget(box)
        impacts = []
        if p.power_cycle:
            impacts.append(("需將下列設備重新上電才會取得新 IP：", p.power_cycle))
        if p.no_standard:
            impacts.append(("下列探頭尚未設定允收標準，量測時將顯示設備異常：", p.no_standard))
        if p.removed_points:
            impacts.append(("下列量測點將從主畫面移除：", p.removed_points))
        if impacts:
            text = "<br>".join(f"<b>{h}</b><br>" + "、".join(html.escape(x) for x in items)
                               for h, items in impacts)
            box = QLabel(text)
            box.setTextFormat(Qt.RichText)
            box.setWordWrap(True)
            box.setStyleSheet(f"background:{C['ng-soft']};color:{C['ng']};border:2px solid {C['ng']};"
                              f"border-radius:6px;padding:10px 14px;font-size:15px;")
            lay.addWidget(box)
        if self.pending_serial:
            note = _label(f"畫面上編號 {self.pending_serial} 的量測結果會先寫入資料庫，再套用設定。", None, True)
            note.setStyleSheet(f"background:{C['panel']};border:1px solid {C['line']};padding:10px 12px;font-size:15px;")
            lay.addWidget(note)
        lay.addStretch()
        self.btn_commit.setEnabled(not p.empty and not self.read_only)

    def _commit(self):
        """先寫入畫面上未寫入的結果（UPL-02）→ 寫入資料庫、產生檔案、重新啟動 dnsmasq；失敗全部還原。"""
        if self.preview is None or self.preview.empty:
            return
        if self.before_save:
            try:
                self.before_save()
            except Exception as exc:
                log.exception("儲存設定前寫入量測結果失敗")
                self._warn(f"畫面上的量測結果寫入失敗，未套用設定：{exc}")
                return
            self.pending_serial = None
        summary = getattr(self, "_import_label", "") or self.preview.summary()
        for key, old, new in self.preview.replaced:
            log.info("替換 DL-EN1 key=%s 舊 MAC=%s 新 MAC=%s", key, old, new)
        QGuiApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            result = self.backend.apply(list(self.original.values()), self._devices(),
                                        summary=f"{summary}（{self.preview.summary()}）")
        except Exception as exc:
            QGuiApplication.restoreOverrideCursor()
            self._warn(f"套用失敗，資料庫與檔案已還原，現場維持原設定。\n\n原因：{exc}")
            return
        QGuiApplication.restoreOverrideCursor()
        self.original = {m: d.copy() for m, d in self.work.items()}
        self.saved.emit(result, self.preview)
        self.accept()

    # ================================================================ 關閉

    def reject(self):
        if self.pages.currentIndex() > 0 and self.is_dirty():
            if not self._ask("有尚未儲存的變更，確定要關閉並放棄這些變更嗎？"):
                return
        super().reject()

    # 以下可在測試中替換
    def _ask(self, text: str) -> bool:
        return QMessageBox.question(self, "設備設定", text) == QMessageBox.Yes

    def _warn(self, text: str):
        QMessageBox.warning(self, "設備設定", text)

    def _info(self, text: str):
        QMessageBox.information(self, "設備設定", text)
