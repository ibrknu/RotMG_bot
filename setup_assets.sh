#!/usr/bin/env bash
set -e

BASE_DIR="$PWD"
cd "$BASE_DIR"

echo "🔄 Cloning or updating exalt-extractor..."
if [ -d "exalt-extractor" ]; then
  (cd exalt-extractor && git pull)
else
  git clone https://github.com/rotmg-network/exalt-extractor.git
fi

echo "🔄 Cloning or updating RotMG-SpriteRenderer..."
if [ -d "RotMG-SpriteRenderer" ]; then
  (cd RotMG-SpriteRenderer && git pull)
else
  git clone https://github.com/Mystery3/RotMG-SpriteRenderer.git
fi

echo "✅ Installing requirements in your virtual environment (if active)..."
if [ -f ".venv/bin/activate" ]; then
  source .venv/bin/activate
else
  echo "⚠️  No venv detected. Activate manually before running."
fi

pip install -r exalt-extractor/requirements.txt
pip install -r RotMG-SpriteRenderer/requirements.txt

echo
read -p "Press ENTER to exit..."
