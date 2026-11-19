#!/usr/bin/env bash
# Phase 0 引導：在「空白 Ubuntu 桌面、還沒有 Claude」時，由人**手動**執行一次，
# 裝好 Google Chrome + VS Code + Claude 擴充（anthropic.claude-code），
# 之後就能在 VS Code 裡用 Claude 依《新機安裝指南》把其餘環境設定完成。
#
# 這支腳本不能由 Claude 執行（它正是在裝 Claude）。以「要用 App 的一般帳號」在桌面終端機執行：
#
#   在空白機器上取得本腳本並執行（不需先 clone）：
#     wget -qO bootstrap-tools.sh https://raw.githubusercontent.com/kuohsuming/in-win/main/scripts/bootstrap-tools.sh
#     bash bootstrap-tools.sh
#
# 可重複執行（已裝的會略過）。用 Google／Microsoft 官方 apt 來源，之後 `apt upgrade` 會一起更新。
set -euo pipefail
[ "$(id -u)" -ne 0 ] || { echo "請用一般帳號執行（勿用 sudo），腳本會在需要時自行 sudo" >&2; exit 1; }

echo "== 0. 基本工具 =="
sudo apt-get update -qq
sudo apt-get install -y wget gpg apt-transport-https git

echo "== 1. Google Chrome =="
if command -v google-chrome >/dev/null; then
  echo "  已安裝，略過"
else
  wget -qO- https://dl.google.com/linux/linux_signing_key.pub \
    | sudo gpg --dearmor -o /usr/share/keyrings/google-chrome.gpg
  echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome.gpg] https://dl.google.com/linux/chrome/deb/ stable main" \
    | sudo tee /etc/apt/sources.list.d/google-chrome.list >/dev/null
  sudo apt-get update -qq
  sudo apt-get install -y google-chrome-stable
fi

echo "== 2. VS Code（Microsoft apt 來源）=="
if command -v code >/dev/null; then
  echo "  已安裝，略過"
else
  wget -qO- https://packages.microsoft.com/keys/microsoft.asc \
    | sudo gpg --dearmor -o /usr/share/keyrings/packages.microsoft.gpg
  echo "deb [arch=amd64,arm64,armhf signed-by=/usr/share/keyrings/packages.microsoft.gpg] https://packages.microsoft.com/repos/code stable main" \
    | sudo tee /etc/apt/sources.list.d/vscode.list >/dev/null
  sudo apt-get update -qq
  sudo apt-get install -y code
fi

echo "== 3. VS Code 的 Claude 擴充（anthropic.claude-code）=="
# 擴充自帶 Claude Code runtime，不需另裝 node 或 claude CLI。以一般帳號安裝（擴充是 per-user）。
if code --list-extensions 2>/dev/null | grep -qx anthropic.claude-code; then
  echo "  已安裝，略過"
else
  code --install-extension anthropic.claude-code
fi

echo "== 4.（選配）取得專案 =="
if [ ! -d "$HOME/in-win/.git" ]; then
  git clone https://github.com/kuohsuming/in-win.git "$HOME/in-win"
else
  echo "  ~/in-win 已存在，略過 clone"
fi

cat <<'NEXT'

====================================================================
引導完成。接下來（由你操作，之後交給 Claude）：
  1. 開啟 VS Code：  code ~/in-win
  2. 登入 Claude 擴充（側邊欄 Claude；首次需用瀏覽器登入，故先裝了 Chrome）
  3. 對 Claude 說：「依 docs/manual/新機安裝指南.md 把這台從空白設定到 App 可運行」
Claude 會接手階段 1～7（系統套件、venv、網路 bridge、MySQL、桌面/自動啟動、kiosk、驗證）。
====================================================================
NEXT
