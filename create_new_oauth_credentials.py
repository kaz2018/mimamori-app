#!/usr/bin/env python3
"""
新しいOAuth認証情報を作成するスクリプト
Google Cloud ConsoleからダウンロードしたOAuth認証情報を適切な形式に変換します
"""

import json
import os
import sys

def create_oauth_credentials():
    """
    新しいOAuth認証情報ファイルを作成
    """
    print("=== 新しいOAuth認証情報の作成 ===")
    print()
    
    # プロジェクト情報
    project_id = "ggl-research"
    
    # OAuth認証情報のテンプレート
    oauth_template = {
        "web": {
            "client_id": "",
            "project_id": project_id,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_secret": "",
            "redirect_uris": [
                "http://localhost:8000/oauth2callback",
                "http://localhost:8080/oauth2callback"
            ]
        }
    }
    
    print("Google Cloud ConsoleからOAuth認証情報を取得してください:")
    print("1. https://console.cloud.google.com/apis/credentials にアクセス")
    print("2. プロジェクト: ggl-research を選択")
    print("3. OAuth 2.0 クライアントIDを作成または既存のものを使用")
    print("4. 認証情報をダウンロード")
    print()
    
    # ユーザーからの入力
    client_id = input("Client IDを入力してください: ").strip()
    client_secret = input("Client Secretを入力してください: ").strip()
    
    if not client_id or not client_secret:
        print("エラー: Client IDとClient Secretは必須です")
        return False
    
    # テンプレートに値を設定
    oauth_template["web"]["client_id"] = client_id
    oauth_template["web"]["client_secret"] = client_secret
    
    # ファイルに保存
    output_file = "oauth_credentials_new.json"
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(oauth_template, f, indent=2, ensure_ascii=False)
        
        print(f"✓ OAuth認証情報が {output_file} に保存されました")
        return True
        
    except Exception as e:
        print(f"エラー: ファイルの保存に失敗しました: {e}")
        return False

def create_environment_scripts():
    """
    環境設定スクリプトを作成
    """
    print("\n=== 環境設定スクリプトの作成 ===")
    
    # ローカル環境用スクリプト
    local_script = """#!/bin/bash
# ローカル環境用OAuth設定
export PROJECT_ID="ggl-research"
export SERVICE_NAME="gemini-report"
export GOOGLE_OAUTH_CREDENTIALS="./oauth_credentials_new.json"
export OAUTH_REDIRECT_URI="http://localhost:8000/oauth2callback"
export SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
export GOOGLE_CLOUD_PROJECT="${PROJECT_ID}"
export GOOGLE_DRIVE_FOLDER_ID="133if6XjFG073nG0HuW4npL0JwsksELwv"
export ADK_AGENTS_DIR="./agents"
export FLASK_ENV="development"
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

echo "新しいOAuth設定が完了しました"
echo "OAuth認証情報: ${GOOGLE_OAUTH_CREDENTIALS}"
echo "リダイレクトURI: ${OAUTH_REDIRECT_URI}"
"""
    
    # スクリプトを保存
    with open("setup_new_oauth.sh", 'w', encoding='utf-8') as f:
        f.write(local_script)
    
    # 実行権限を付与
    os.chmod("setup_new_oauth.sh", 0o755)
    
    print("✓ 環境設定スクリプト setup_new_oauth.sh を作成しました")

def main():
    """
    メイン処理
    """
    print("OAuth認証情報の再設定を行います")
    print("既存のOAuthファイルは backup_oauth/ にバックアップされています")
    print()
    
    # OAuth認証情報の作成
    if create_oauth_credentials():
        create_environment_scripts()
        
        print("\n=== 設定完了 ===")
        print("次の手順で設定を有効にしてください:")
        print("1. source setup_new_oauth.sh")
        print("2. python -c \"from agents.Slide_Creator.auth_helper import get_google_slides_service; print('認証テスト:', get_google_slides_service())\"")
        print()
        print("注意: 初回実行時はブラウザでOAuth認証が必要です")
    else:
        print("OAuth認証情報の作成に失敗しました")
        sys.exit(1)

if __name__ == "__main__":
    main() 