# 提案：表面 3D 繪圖模組（plate3d）

> 表面平整檢查系統的子功能。作業員在主畫面按「3D 繪圖」，彈出視窗以立體圖顯示這一片表面的凹凸。
> 本文件是給 VS Code + Claude Code 啟動開發用的完整規格；畫面效果以 `reference/` 內的原型為準。

---

## 0. 給 Claude Code 的說明

- 本資料夾內容：
  - `PROPOSAL.md`：本文件，所有規格以這裡為準。
  - `reference/board-station.html`：瀏覽器原型（可直接開啟，點「不合格」再點「3D 繪圖」）。
  - `reference/plate3d_prototype.js`：原型中 3D 繪圖的完整 JavaScript，演算法與常數要 1:1 移植到 Python。
  - `reference/preview.png`：預期畫面。
  - `tests/vectors.json`：計算結果的測試資料（含預期殘差與平面度）。
- 請先做第 12 節的里程碑 M1（純計算＋單元測試），通過後再做繪圖與對話框。
- 一律使用繁體中文撰寫畫面文字、註解與文件。
- 不要使用 matplotlib；繪圖用 PySide6 `QPainter`。

---

## 1. 背景與目標

主畫面目前以 12 個探頭各自的上下限判定合格與否，作業員只看得到數字，看不出整片表面「哪裡凸、哪裡凹、整體是什麼形狀」。

本模組要做到：

1. 用目前這一片的 12 個讀值，畫出一塊有厚度的立體板子，表面的凹凸一眼可見。
2. 自動扣除整片的傾斜與高低（平面擬合），只顯示真正的不平。
3. 板子每 0.7 秒旋轉 30°，12 個角度循環，讓作業員看清楚形狀。
4. 顯示平面度（最高減最低），作為日後改用平面度判定的基礎。
5. 在產線 IPC（Intel Atom x6425E）上即時繪製，開啟視窗不用等待。

---

## 2. 範圍

**要做**

- 計算：平面擬合、殘差、平面度、插值網格。
- 繪圖：自訂 Qt 元件，以 `QPainter` 畫出立體板子、量測點與標籤。
- 對話框：3D 繪圖視窗（標題、繪圖區、資訊欄、控制列）。
- 主畫面整合：結果橫幅新增「3D 繪圖」按鍵與啟用條件。
- 定義檔擴充：板子尺寸、探頭位置、探頭在上方或下方。
- 單元測試與一支獨立的展示程式（不需連 DL-EN1 即可開視窗）。

**不做**

- 不改變現有的合格／不合格判定（3D 只供檢視）。
- 不提供滑鼠拖曳旋轉、縮放、視角切換、色彩切換（皆固定）。
- 不輸出圖片或 GIF。
- 不寫入資料庫。

---

## 3. 平台與套件

| 項目 | 版本 | 備註 |
| --- | --- | --- |
| 作業系統 | Ubuntu 22.04 LTS | 產線 IPC：DRP-A100-E4（Atom x6425E，4 核心） |
| Python | 3.10 | 系統內建版本，使用 venv |
| PySide6 | 與主程式相同版本 | 已確認 6.12.0 有 Python 3.10 的 wheel，需 glibc 2.34（22.04 為 2.35） |
| numpy | 2.2.6 | 2.3 以後需要 Python 3.11 |
| scipy | 1.15.3 | 使用 `RBFInterpolator`；1.16 以後需要 Python 3.11 |
| pytest | 最新版 | 僅開發與測試用 |

字型：Qt 透過 fontconfig 讀取系統字型，`QFont("Noto Sans CJK TC")` 可正確顯示繁體中文字形（matplotlib 3.10 才有日文字形的問題，本模組不用 matplotlib）。數字使用 Barlow Semi Condensed，由主程式在啟動時載入。

---

## 4. 輸入資料

### 4.1 定義檔擴充（`dl-en1.json`）

新增選填欄位，未設定時使用預設值，舊定義檔不需修改即可使用：

```json
{
  "version": 1,
  "plate": {
    "length": 1000,
    "width": 600,
    "thickness": 5,
    "probe_side": "below"
  },
  "dl_en1": [
    {
      "key": "front", "name": "前排", "mac": "00:01:FC:12:34:56", "ipv4": "192.168.10.11",
      "max_probes": 4,
      "probes": [
        {"id": 1, "description": "左", "x": 125, "y": 100},
        {"id": 2, "description": "左中"}
      ]
    }
  ]
}
```

| 欄位 | 型別 | 預設 | 說明 |
| --- | --- | --- | --- |
| `plate.length` | 數字（mm） | 1000 | 板長，沿 x 方向（作業員看過去的左右） |
| `plate.width` | 數字（mm） | 600 | 板寬，沿 y 方向（前到後） |
| `plate.thickness` | 數字（mm） | 5 | 實際板厚；畫面上的厚度為示意，不按比例 |
| `plate.probe_side` | `"above"`／`"below"` | `"below"` | 探頭在板子上方或下方 |
| `probes[].x`、`probes[].y` | 數字（mm） | 自動 | 由上往下看、左前角為原點；未設定時見 4.2 |

JSON Schema 需同步更新：`x` 範圍 0～`length`，`y` 範圍 0～`width`；同一排的探頭 `x` 不可重複。

### 4.2 未設定座標時的預設位置

- 第 `ri` 排（主畫面由上而下的順序，第一排在最前面），共 `R` 排：`y = width × (ri + 0.5) / R`
- 該排依 ID 排序後第 `i` 個探頭，共 `N` 個：`x = length × (i + 0.5) / N`

### 4.3 讀值

每個探頭一筆，來自主程式本次讀取結果：

```python
@dataclass
class ProbeReading:
    label: str          # 代號：排名稱首字 + 序號，例「中3」
    name: str           # 全名：排名稱 + 位置，例「中排 右中」
    x: float            # mm
    y: float            # mm
    value_mm: float | None   # None = 無數據（設備異常、超出範圍等）
    state: str          # "ok" | "hi" | "lo" | "err"，沿用主畫面單點判定
```

---

## 5. 計算

全部在 `plate3d/model.py`，純 numpy／scipy，不依賴 Qt。

1. **篩選**：只用 `value_mm` 不是 None 的點。少於 3 點 → 錯誤「有效量測點不足 3 點，無法畫出表面。」
2. **高度換算**：`probe_side == "below"` 時 `h = −value_mm`，否則 `h = value_mm`。
   理由：探頭在下方往上頂，表面越低，探頭被壓越多，讀值越大。
3. **平面擬合**：最小平方解 `h = a + b·X + c·Y`，`X = x/1000`、`Y = y/1000`（換成公尺，避免數值過大）。
   矩陣奇異（點排成一直線）→ 錯誤「有效量測點排成一直線，無法擬合平面。」
4. **殘差**：`r = (h − (a + b·X + c·Y)) × 1000`，單位 µm。
5. **平面度**：`flatness = max(r) − min(r)`；同時記下最高點與最低點。
6. **插值網格**：薄板樣條，`scipy.interpolate.RBFInterpolator(pts, r, kernel="thin_plate_spline")`，
   座標用 `(x/length, y/length)`（兩軸同比例）。
   - 網格點數：`nx = 41`，`ny = max(9, round(40 × width / length) + 1)`
   - 網格座標：`x_i = length × i/(nx−1)`，`y_j = width × j/(ny−1)`
   - 插值只用來畫點與點之間的形狀，不得用於判定。
7. **顯示比例**：
   - `lim = max(1, max|網格值|, max|r|)`（µm，色階與明暗用的對稱範圍）
   - 示意板厚 `Tv = 0.05 × length`
   - 高度倍率 `ex = 0.4 × Tv / lim`（每 µm 對應的顯示單位）；畫面標示「高度放大約 ×round(ex×1000) 倍」

回傳：

```python
@dataclass
class SurfaceModel:
    points: list[ProbeReading]
    residual_um: dict[str, float]   # label → 殘差；無數據的點不在內
    grid: np.ndarray                # shape (ny, nx)，µm
    flatness_um: float
    highest: tuple[str, float]      # (label, µm)
    lowest: tuple[str, float]
    lim_um: float
    thickness_vis: float            # Tv
    exaggeration: float             # ex
    probe_side: str
    error: str | None               # 有錯誤時其他欄位可為空
```

---

## 6. 繪圖演算法

全部在 `plate3d/renderer.py`，輸入 `SurfaceModel`、旋轉角、畫布寬高，用 `QPainter` 畫。演算法與常數與 `reference/plate3d_prototype.js` 的 `draw3d()` 相同。

### 6.1 座標與視角

- 世界座標：x 向右（板長）、y 向後（板寬）、z 向上；原點為左前角。
- 視角固定：仰角 `el = 15°`（眼睛在上方）。
- 方位：`az = (−45° + rot)`，`rot` 為目前旋轉角（0、30、60…330）。`rot = 0` 時從左前方 45° 看過去。
- 向量：
  - 視線（指向眼睛）`v = (cos el·cos az, cos el·sin az, sin el)`
  - 螢幕右 `rt = (−sin az, cos az, 0)`
  - 螢幕上 `up = (−sin el·cos az, −sin el·sin az, cos el)`

### 6.2 投影（正交投影）

```
X = x − L/2,  Y = y − W/2,  Z = z + Tv/2
sx    = cw/2 + sc·(X·rt.x + Y·rt.y)
sy    = ch/2 − sc·(X·up.x + Y·up.y + Z·up.z)
depth = X·v.x + Y·v.y + Z·v.z          （越大越靠近眼睛）
D  = √(L² + W²),  hmax = 0.4·Tv
sc = min( cw·0.92 / D ,  ch·0.84 / (D·sin el + (Tv + 2·hmax)·cos el) )
```

`sc` 對所有旋轉角都相同，旋轉時板子大小不跳動。上表面某網格點的 `z = grid[j][i] × ex`。

### 6.3 多邊形

1. **上表面**：每個網格 (i, j) 一個四邊形，共 (nx−1)·(ny−1) 個。
2. **側面**：四個側面只畫面向眼睛的（外法線 n 滿足 `n.x·v.x + n.y·v.y > 1e−6`）。
   沿邊緣每一段一個四邊形：上緣跟著表面高度，下緣 = 上緣 − Tv。
   側面深度減 0.001，讓同深度時上表面畫在後面。
3. **排序**：所有多邊形依四邊形對角兩點的平均深度由小到大排序，依序填色（畫家演算法）。
4. **接縫**：每個多邊形用同色填滿，並以同色 0.7px 描邊，消除相鄰多邊形間的細縫；開啟反鋸齒。

### 6.4 上表面明暗（白灰渲染）

常數：`SHADE = {lo: 140, hi: 228, relief: 6, light: (−0.55, 0.75, 0.6)}`

1. 底色：`t = (r̄ / lim + 1) / 2`（r̄ 為四角殘差平均），`base = lo + (hi − lo)·clamp(t, 0, 1)`；越高越白。
2. 光源：相對眼睛的方向（左 0.55、上 0.75、朝向眼睛 0.6），換成世界座標並正規化：
   `LW = normalize(light.x·rt + light.y·up + light.z·v)`。光源跟著眼睛走，旋轉時陰影會變化。
3. 法線：高度再放大 `relief` 倍，強化起伏。
   ```
   dzx = (z(i+1,j) + z(i+1,j+1) − z(i,j) − z(i,j+1)) / 2 × relief
   dzy = (z(i,j+1) + z(i+1,j+1) − z(i,j) − z(i+1,j)) / 2 × relief
   dx = L/(nx−1),  dy = W/(ny−1)
   n  = normalize(−dzx·dy, −dzy·dx, dx·dy)
   ```
4. 光照係數：`k = clamp(1 + 1.8·(n·LW − LW.z), 0.5, 1.14)`（平面時 k = 1）。
5. 顏色：`gray = min(255, round(base × k))`，RGB 三值相同。

### 6.5 側面、輪廓、尺寸

- 側面顏色：`s = 0.45 + 0.35·min(1, (n·v_xy) / cos el)`，RGB = (0.5s+0.12, 0.5s+0.12, 0.5s+0.14) × 255。
- 輪廓：上表面四邊、可見側面的下緣、可見側面兩端的垂直邊，1.1px，黑色 75% 不透明。
- 尺寸文字：可見側面中點往外 0.12·W 處、z = −Tv，往下 8px，寫「長 1000 mm」（前後側面）或「寬 600 mm」（左右側面），13px，`ink` 色。

### 6.6 量測點與標籤

- 點位置：有數據的點在 `z = r × ex`；無數據的點在 `z = 0`。
- 有數據：橘色 #FF7A00 實心圓，半徑 4.5px，1.2px 黑框。
- 無數據：紅色（`ng`）✕，臂長 6px，線寬 3px。
- 標籤：兩行置中，第一行代號（例「中3」），第二行殘差（帶正負號、1 位小數，例「+39.5」），無數據寫「無數據」；
  數字字型 13px 粗體；框寬 = 兩行較寬者 + 10px，高 34px，圓角 4px。
  - 一般：白底 90%，文字 #1C2326。
  - 超出允收（state 為 hi／lo）或無數據：紅底 rgba(200,50,43,.94)，白字。
- 避讓：依深度由近到遠逐一放置，每個標籤依序嘗試以下位置（相對於點），取第一個不與已放標籤重疊（含 2px 間距）的：
  1. 上方：(−w/2, −h−10)
  2. 下方：(−w/2, +10)
  3. 左方：(−w−10, −h/2)
  4. 右方：(+10, −h/2)
  5. 更上方：(−w/2, −2h−14)
  6. 更下方：(−w/2, +h+14)
  全部重疊時用第 1 個。
- 引線：從點畫到標籤框上最近的一點，1px，黑色 55%。
- 繪製順序：所有多邊形與輪廓之後，再依深度由遠到近畫點與標籤。

---

## 7. 對話框

`plate3d/dialog.py`，`QDialog`（模態），寬 min(1280px, 螢幕 96%)，高最多螢幕 94%。樣式沿用主程式色票（`panel`、`panel-2`、`line`、`ink`、`ink-2`、`go`、`ng`、`go-soft`、`ng-soft`）。

| 區域 | 內容 |
| --- | --- |
| 標題列 | 「3D 繪圖」20px 粗體；編號（數字字型 20px，`ink-2`）；結果標籤（合格：`go-soft` 底 `go` 字；不合格、設備異常：`ng-soft` 底 `ng` 字；15px 特粗）；右上 ✕ |
| 繪圖區 | 左側，填滿；背景 `panel-2`，邊框 1px `line`，圓角 6px，最小高度 min(60% 視窗高, 560px)。有錯誤時中央顯示紅字錯誤訊息，不畫圖 |
| 資訊欄 | 右側寬 260px，由上而下四張卡片＋說明（見下表） |
| 控制列 | 「◀ 30°」「❚❚ 暫停」／「▶ 播放」「30° ▶」、目前角度「旋轉 N°」（數字字型 18px）；最右「關閉」（`ink` 實心白字，寬 132px）。有錯誤時前三個按鍵停用 |

**資訊欄**（卡片：`panel-2` 底，1px `line` 框，圓角 6px，內距 10px 12px）

| 卡片 | 內容 |
| --- | --- |
| 平面度 | 小標「平面度（最高 − 最低）」；數字字型 44px 粗體＋「µm」；「允許值：未定（TBD）」 |
| 最高／最低點 | 「最高點 中排 右（中4）　+39.5」「最低點 中排 右中（中3）　−33.0」；小字「單位 µm，相對於擬合平面」 |
| 明暗圖例 | 小字「越高越白、越低越灰；光從左上方照射」；灰 RGB(140) 到白 RGB(228) 漸層條，高 14px；刻度 −lim、0、+lim |
| 異常（有才顯示，紅框） | 「超出允收：…」「無數據（不參與擬合）：…」；探頭在下方時加小字「探頭在下方：讀值『偏高』＝該處表面較低」 |
| 說明（13px，`ink-2`，項目符號） | 使用 N/M 點；已扣除整片傾斜與高低。／高度放大約 ×N 倍，厚度為示意。／點與點之間的形狀是推估，判定以實測點為準。／探頭在下方，已換算成由上往下看的高度（或「探頭在上方」）。 |

**行為**

- 開啟時：計算模型、旋轉角歸零、自動播放。
- 播放：`QTimer` 每 700ms，`rot = (rot + 30) % 360` 並重畫。
- 「◀ 30°」「30° ▶」：先暫停，再轉 ∓30°。
- 鍵盤：← → 轉動，空白鍵播放／暫停，Esc 關閉。
- 關閉時停止計時器；視窗大小改變時重畫。
- 寬度 ≤ 900px 時，資訊欄移到繪圖區下方。

---

## 8. 主畫面整合

- 結果橫幅的按鍵區依序為「重讀」「下一片」「3D 繪圖」；「3D 繪圖」在最右，與「下一片」間距多 14px。
- 外觀同「重讀」（`panel` 底、`ink` 字、3px `ink-2` 框，滑過框變 `ink`），前方加立方體圖示 28px：
  ```svg
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><path d="M12 2.5l8.5 4.8v9.4L12 21.5l-8.5-4.8V7.3z"/><path d="M3.5 7.3L12 12l8.5-4.7M12 12v9.5"/></svg>
  ```
- 啟用條件：本次讀取有至少 3 個有效量測點（合格、不合格、設備異常都可以看）。
  待放置、倒數、讀取中、偵測設備期間停用。
- 提示文字：可按時「以立體圖檢視這一片的表面高低」，停用時「需要至少 3 個有效量測點」。
- 主程式只需呼叫：`Plate3DDialog(readings, plate_cfg, serial, result_state, parent).exec()`。

---

## 9. 模組結構與 API

```
plate3d/
  __init__.py
  config.py        # PlateConfig：由定義檔讀取 plate 與探頭座標、套用預設值
  model.py         # build_model(readings, plate_cfg) -> SurfaceModel（純計算）
  renderer.py      # render(painter, rect, model, rot_deg, palette)（純繪圖，無狀態）
  widget.py        # Plate3DView(QWidget)：持有 model 與 rot，paintEvent 呼叫 renderer
  dialog.py        # Plate3DDialog(QDialog)：標題、資訊欄、控制列、計時器
  demo.py          # python -m plate3d.demo [vectors.json 的 case 名稱]：不連設備直接開視窗
tests/
  test_model.py    # 用 tests/vectors.json 驗證殘差與平面度
  test_config.py   # 預設座標、probe_side、Schema 驗證
  test_renderer.py # 離屏 QImage 繪製不拋例外；12 個角度都畫得出來；標籤不重疊
```

設計原則：

- `model.py` 不 import Qt，方便測試與日後重用（例如報表）。
- `renderer.py` 無狀態，只依參數畫；色票由呼叫端傳入，支援深淺主題。
- 所有常數（6.4 的 `SHADE`、視角 15°、旋轉 30°／700ms、網格 41）集中在 `renderer.py` 頂端。

---

## 10. 效能目標

在 DRP-A100-E4（Atom x6425E）上：

| 項目 | 目標 |
| --- | --- |
| `build_model`（含插值 41×25） | < 50 ms |
| 單張繪製（約 1,000 個多邊形＋12 個標籤，1100×560 畫布） | < 60 ms |
| 按下「3D 繪圖」到出現第一張圖 | < 300 ms |
| 播放時 CPU 使用率 | 單核心 < 15% |

做法：`build_model` 只在開啟時算一次；投影與排序每張重算（量很小）；不預先產生圖片。
若單張超過目標，先把網格降為 31×19，再考慮快取多邊形頂點。

---

## 11. 測試與驗收

**單元測試**（`pytest`）

1. `tests/vectors.json` 的每個 case：殘差與平面度誤差 < 0.01 µm。
   - `fail_below`：平面度 66.433 µm。
   - `fail_above`：殘差與 `fail_below` 正負相反，平面度相同。
   - `missing_one`：第 2 點為 None，不參與擬合，平面度 66.591 µm。
   - `pure_tilt`：純傾斜平面，所有殘差為 0、平面度 0。
2. 少於 3 點、3 點以上但共線：回傳對應錯誤訊息。
3. 預設座標：3 排 × 4 探頭、1000×600 時，前排左為 (125, 100)，後排右為 (875, 500)。
4. 插值網格在每個量測點位置的值，與該點殘差相差 < 0.01 µm。
5. 繪製：12 個旋轉角都能畫到離屏 `QImage` 而不拋例外；標籤框兩兩不重疊。

**畫面驗收**（與 `reference/preview.png`、`reference/board-station.html` 比對）

- 板子有厚度，可見兩個側面，側面上緣隨表面起伏。
- 凸起處白、凹陷處灰，左上光源造成的明暗清楚可見。
- 旋轉時板子大小不變、不跳動，每 0.7 秒轉 30°。
- 超出允收的點標籤為紅底；無數據的點為紅 ✕。
- 繁體中文字形正確（不可出現日文字形）。

**現場驗收**

- 在 DRP-A100-E4 上量測第 10 節的時間並記錄。
- 放一片已知凸起位置的樣品（例如在某點下方墊薄片），確認圖上凸起位置與方向正確；同時確認 `probe_side` 設定正確。

---

## 12. 開發步驟

| 里程碑 | 內容 | 完成條件 |
| --- | --- | --- |
| M1 計算 | `config.py`、`model.py`、`test_model.py`、`test_config.py` | 第 11 節單元測試 1～4 全部通過 |
| M2 繪圖 | `renderer.py`、`widget.py`、`demo.py`（只有繪圖區，固定角度） | `python -m plate3d.demo fail_below` 顯示與 preview.png 相近的圖 |
| M3 對話框 | `dialog.py`：資訊欄、控制列、播放、鍵盤 | demo 可完整操作；測試 5 通過 |
| M4 整合 | 主畫面「3D 繪圖」按鍵、啟用條件、定義檔 Schema 擴充 | 主程式各情境（合格、不合格、設備異常）都能開啟 |
| M5 現場 | IPC 效能量測、實物方向確認 | 第 10 節目標達成並記錄 |

---

## 13. 待決事項

| # | 事項 | 影響 | 建議 |
| --- | --- | --- | --- |
| 1 | 探頭實際在上方還是下方 | 凹凸方向會整個顛倒 | 預設 `below`；M5 用墊片實測確認 |
| 2 | 板子尺寸與各探頭實際座標 | 圖上位置與形狀 | 量測治具後填入定義檔；未填用平均分佈 |
| 3 | 主畫面「偏高／偏低」用語 | 探頭在下方時，讀值偏高＝表面較低，與 3D 圖相反 | 改為「凸起／凹陷」或「讀值偏高／偏低」 |
| 4 | 平面度允許值 | 資訊欄目前顯示 TBD | 收集至少 30 片合格品的平面度，取平均 + 3σ 後決定 |
| 5 | 是否改用平面度判定 | 判定邏輯 | 本模組先只檢視；確定後另案修改判定 |
