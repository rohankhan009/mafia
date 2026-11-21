#!/usr/bin/env bash
# Linux/VPS launcher
cd "$(dirname "$0")"
if [ -d "venv" ]; then source venv/bin/activate; fi
echo "🤖 Starting Bulk SMS Telegram Bot..."
python3 bot.py
