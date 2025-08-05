#!/usr/bin/env bash
set -e

BASE="$HOME/.config/sublime-text/Packages/User/RotMG_bot"
cd "$BASE" || exit
echo "📁 Working directory: $BASE"

# 1. Create venv if missing
if [[ ! -d ".venv" ]]; then
  echo "✨ Creating virtual environment..."
  python3 -m venv .venv
  echo "✔ .venv created"
fi

# 2. Activate
echo "🔄 Activating virtual environment..."
# shellcheck disable=SC1091
source .venv/bin/activate
echo "✔ Activated: $VIRTUAL_ENV"

# 3. Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# 4. Install dependencies
echo "📦 Installing required Python packages..."
pip install opencv-python PySide6 pynput mss

# 5. Check tkinter
echo "🔍 Checking for tkinter support..."
python3 - <<EOF
import sys
try:
    import tkinter
    print("✅ tkinter is available (version: {})".format(tkinter.TkVersion))
except Exception as e:
    print("❌ tkinter import failed:", e)
    sys.exit(1)
EOF

# 6. Quick import test for all main modules
echo "🔍 Verifying module imports..."
python3 - <<EOF
import cv2, PySide6, pynput, mss
print("✅ All imports succeeded!")
EOF

echo
echo "🎉 All systems go! Your virtual environment is ready."
read -p "Press ENTER to exit…"

