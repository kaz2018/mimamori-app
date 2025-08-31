#!/bin/bash
# start_web.sh - FastAPI Webサーバー起動スクリプト（カスタムUI付き）

# Pythonキャッシュ削除
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} +

# ポート8000を使っているプロセスがあればkill
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️ ポート8000が使用中です。プロセスを終了します..."
    lsof -ti:8000 | xargs kill -9
    sleep 2
fi

cd "$(dirname "$0")" || exit 1
source venv/bin/activate
export GOOGLE_APPLICATION_CREDENTIALS="$(pwd)/service-account-key.json"

echo "🚀 FastAPI Webサーバーを起動中..."
echo "📍 アクセス先:"
echo "   - ADK標準UI: http://localhost:8000/"
echo "   - 読み聞かせ選択: http://localhost:8000/src/story_top.html"
echo "   - メインページ: http://localhost:8000/src/index.html"
echo ""

python main.py
