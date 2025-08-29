#!/usr/bin/env python3
"""
ローカル開発用のOAuth認証情報を作成するスクリプト
"""

import json
import os

def create_local_oauth_credentials():
    """ローカル開発用のOAuth認証情報を作成"""
    
    # 既存の認証情報を読み込み
    if not os.path.exists('oauth_credentials_web.json'):
        print("❌ oauth_credentials_web.json が見つかりません")
        print("Google Cloud ConsoleでOAuth2認証情報を作成してください")
        return False
    
    with open('oauth_credentials_web.json', 'r') as f:
        creds_data = json.load(f)
    
    # ローカル開発用のリダイレクトURIを追加
    local_redirect_uris = [
        "http://localhost:8080/oauth2callback",
        "http://localhost:8000/oauth2callback",
        "http://localhost:0/oauth2callback"
    ]
    
    # 既存のリダイレクトURIを保持
    existing_uris = creds_data['web'].get('redirect_uris', [])
    
    # 新しいリダイレクトURIを追加（重複を避ける）
    all_uris = existing_uris + [uri for uri in local_redirect_uris if uri not in existing_uris]
    
    # 認証情報を更新
    creds_data['web']['redirect_uris'] = all_uris
    
    # ローカル開発用の認証情報ファイルを作成
    local_creds_file = 'oauth_credentials_local.json'
    with open(local_creds_file, 'w') as f:
        json.dump(creds_data, f, indent=2)
    
    print(f"✅ ローカル開発用認証情報を作成しました: {local_creds_file}")
    print("リダイレクトURI:")
    for uri in all_uris:
        print(f"  {uri}")
    
    return True

def update_environment_variables():
    """環境変数をローカル開発用に更新"""
    
    # ローカル環境用の環境変数設定ファイルを作成
    env_content = """#!/bin/bash
# ローカル環境用環境変数設定スクリプト
# 使用方法: source local_env_oauth.sh

export PROJECT_ID="ggl-research"
export SERVICE_NAME="gemini-report"
export GOOGLE_OAUTH_CREDENTIALS="./oauth_credentials_local.json"
export OAUTH_REDIRECT_URI="http://localhost:8000/oauth2callback"
export SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
export GOOGLE_CLOUD_PROJECT="${PROJECT_ID}"
export GOOGLE_DRIVE_FOLDER_ID="133if6XjFG073nG0HuW4npL0JwsksELwv"
export ADK_AGENTS_DIR="./agents"
export FLASK_ENV="development"
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

echo "ローカル環境用OAuth設定が完了しました"
echo "OAuth認証情報: ${GOOGLE_OAUTH_CREDENTIALS}"
echo "リダイレクトURI: ${OAUTH_REDIRECT_URI}"
"""
    
    with open('local_env_oauth.sh', 'w') as f:
        f.write(env_content)
    
    print("✅ ローカル環境用環境変数設定ファイルを作成しました: local_env_oauth.sh")
    print("使用方法: source local_env_oauth.sh")

def main():
    """メイン関数"""
    print("🔧 ローカル開発用OAuth認証情報の作成")
    print("=" * 50)
    
    # ローカル開発用認証情報を作成
    if create_local_oauth_credentials():
        # 環境変数設定ファイルを作成
        update_environment_variables()
        
        print("\n" + "=" * 50)
        print("✅ 設定完了！")
        print("\n次のステップ:")
        print("1. Google Cloud ConsoleでOAuth同意画面にテストユーザーを追加")
        print("2. source local_env_oauth.sh を実行")
        print("3. python test_local_oauth.py でテスト")
        print("4. python adk_web_server.py でADK Web UIを起動")
        
        print("\n📋 Google Cloud Consoleでの設定:")
        print("- OAuth同意画面でテストユーザーを追加:")
        print("  - ysnr.myst@gmail.com")
        print("- リダイレクトURIを確認:")
        print("  - http://localhost:8080/oauth2callback")
        print("  - http://localhost:8000/oauth2callback")
        print("  - http://localhost:0/oauth2callback")
    else:
        print("❌ 設定に失敗しました")

if __name__ == "__main__":
    main() 