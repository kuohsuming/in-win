"""色票、字型與共用樣式（畫面設計規格第 2、3 節）。

色票只定義於此；元件以 objectName 或動態屬性（setProperty）套用 QSS（第 9 節）。
目前只實作淺色主題（深色為選配）。
"""

from __future__ import annotations

from pathlib import Path

from PySide6.QtGui import QColor, QFont, QFontDatabase

C = {
    "bg": "#DFE3E1", "panel": "#F7F8F6", "panel-2": "#ECEEEC", "ink": "#1C2326", "ink-2": "#56616A",
    "line": "#C3C9C7", "go": "#1F8A4C", "go-soft": "#DCEFE3", "ng": "#C8322B", "ng-soft": "#F8DEDB",
    "warn": "#B87400", "warn-soft": "#F6EAD2", "stale": "#8A9296", "focus": "#1F5FBF", "white": "#FFFFFF",
}

TEXT_FAMILIES = ["Noto Sans TC", "Noto Sans CJK TC", "PingFang TC", "Microsoft JhengHei"]
NUM_FAMILY = "Barlow Semi Condensed"
FONT_DIR = Path(__file__).resolve().parents[1] / "fonts"
ASSET_DIR = Path(__file__).resolve().parent / "assets"
_text_family = "sans-serif"


def color(name: str) -> QColor:
    return QColor(C[name])


def load_fonts() -> str:
    """載入隨附的數字字型，回傳可用的文字字型（第 3 節；UI-08 離線可用）。"""
    global _text_family
    for ttf in sorted(FONT_DIR.glob("*.ttf")):
        QFontDatabase.addApplicationFont(str(ttf))
    families = set(QFontDatabase.families())
    _text_family = next((f for f in TEXT_FAMILIES if f in families), "sans-serif")
    return _text_family


def text_font(px: int, weight: int = 400) -> QFont:
    f = QFont(_text_family)
    f.setPixelSize(px)
    f.setWeight(QFont.Weight(weight))
    return f


def num_font(px: int, weight: int = 500) -> QFont:
    """數字字型：等寬數字（tabular figures），數值變動時不跳動。"""
    f = QFont([NUM_FAMILY, _text_family])
    f.setPixelSize(px)
    f.setWeight(QFont.Weight(weight))
    try:
        f.setFeature(QFont.Tag("tnum"), 1)
    except (AttributeError, TypeError):
        pass
    return f


def qss() -> str:
    """全 App 共用的樣式表；字級以 px 指定，對應設計規格的數值。"""
    t, n = _text_family, NUM_FAMILY
    return f"""
* {{ font-family: "{t}"; color: {C['ink']}; }}
QMainWindow, #page {{ background: {C['bg']}; }}
QDialog {{ background: {C['panel']}; }}
QToolTip {{ background: {C['ink']}; color: {C['panel']}; border: none; padding: 4px 8px; font-size: 14px; }}

/* ---- 共用面板 ---- */
#panel {{ background: {C['panel']}; border: 1px solid {C['line']}; border-radius: 6px; }}
#panel2 {{ background: {C['panel-2']}; border: 1px solid {C['line']}; border-radius: 6px; }}

/* ---- 按鍵（5.10 按鍵樣式；工具列 5.1）---- */
QPushButton {{ font-size: 16px; padding: 9px 16px; border: 2px solid {C['ink-2']}; background: {C['panel-2']};
              border-radius: 6px; }}
QPushButton:hover {{ border-color: {C['ink']}; }}
QPushButton:focus {{ outline: none; border-color: {C['focus']}; }}
QPushButton:disabled {{ color: rgba(28,35,38,0.35); border-color: rgba(86,97,106,0.35);
                        background: rgba(236,238,236,0.35); }}
QPushButton[kind="primary"] {{ background: {C['ink']}; color: {C['panel']}; border-color: {C['ink']}; }}
QPushButton[kind="primary"]:disabled {{ background: rgba(28,35,38,0.35); color: rgba(247,248,246,0.8);
                                        border-color: transparent; }}
QPushButton[kind="danger"] {{ background: {C['panel']}; color: {C['ng']}; border-color: {C['ng']}; }}
QPushButton[kind="small"] {{ font-size: 14px; padding: 5px 10px; border-width: 1px; }}
QPushButton[kind="small-danger"] {{ font-size: 14px; padding: 5px 10px; border-width: 1px; color: {C['ng']};
                                   border-color: {C['ng']}; }}
QPushButton[kind="tool"] {{ font-size: 17px; font-weight: 700; padding: 10px 18px; }}
QPushButton[kind="icon"] {{ padding: 0; min-width: 42px; max-width: 42px; min-height: 42px; max-height: 42px; }}

/* ---- 輸入框（5.10）---- */
QLineEdit, QSpinBox, QComboBox {{ font-size: 16px; padding: 6px 8px; border: 2px solid {C['line']};
              background: {C['panel']}; border-radius: 4px; min-height: 22px; }}
QLineEdit:focus, QSpinBox:focus, QComboBox:focus {{ border-color: {C['focus']}; }}
QLineEdit[num="true"], QSpinBox[num="true"] {{ font-family: "{n}", "{t}"; font-size: 17px; }}
QLineEdit[error="true"], QSpinBox[error="true"] {{ border-color: {C['ng']}; background: {C['ng-soft']}; }}
QLineEdit:read-only {{ background: {C['panel-2']}; color: {C['ink-2']}; }}
QComboBox[kind="status"] {{ font-weight: 700; border-color: {C['ink-2']}; }}
QComboBox::drop-down {{ width: 30px; border: none; }}
QComboBox::down-arrow {{ image: url("{ASSET_DIR.as_posix()}/chevron-down.svg"); width: 16px; height: 16px; }}
QComboBox QAbstractItemView {{ font-size: 16px; selection-background-color: {C['ink']};
              selection-color: {C['panel']}; background: {C['panel']}; }}
QCheckBox {{ font-size: 15px; spacing: 6px; }}

/* ---- 表格 ---- */
QTableWidget {{ background: {C['panel']}; border: 1px solid {C['line']}; gridline-color: {C['line']};
               font-size: 15px; selection-background-color: {C['ink']}; selection-color: {C['panel']}; }}
QHeaderView::section {{ background: {C['panel-2']}; color: {C['ink-2']}; font-size: 13px; font-weight: 700;
               border: none; border-bottom: 1px solid {C['line']}; padding: 6px 8px; }}
QListWidget {{ background: {C['panel']}; border: 2px solid {C['line']}; border-radius: 4px; font-size: 15px; }}
QListWidget[error="true"] {{ border-color: {C['ng']}; }}
QScrollArea {{ border: none; background: transparent; }}

/* ---- 文字 ---- */
#h1 {{ font-size: 20px; font-weight: 700; }}
#h2 {{ font-size: 17px; font-weight: 700; }}
#note {{ font-size: 13px; color: {C['ink-2']}; }}
#label {{ font-size: 15px; color: {C['ink-2']}; }}
#toast {{ background: {C['ink']}; color: {C['panel']}; font-size: 16px; padding: 12px 20px; border-radius: 6px; }}
"""


def tag_style(status: str) -> tuple[str, str]:
    """清單標籤（5.10 設備類型表）：(背景, 文字)。"""
    return {
        "unclassified": (C["ng-soft"], C["ng"]),
        "dl_en1_live": (C["go-soft"], C["go"]),
        "dl_en1_maint": (C["warn-soft"], C["warn"]),
        "dl_en1_retired": (C["panel-2"], C["ink-2"]),
        "not_dl_en1": (C["panel-2"], C["ink-2"]),
    }[status]
