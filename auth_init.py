"""
Google認証の事前初期化モジュール
アプリ起動時に認証を一括初期化して、API呼び出し時の遅延を解消
"""

import os
import logging
from typing import Optional, Dict, Any
from google.cloud import storage
import google.generativeai as genai

# グローバル変数で認証済みクライアントを保持
_storage_client: Optional[storage.Client] = None
_genai_configured: bool = False
_initialization_error: Optional[str] = None

def initialize_google_services() -> Dict[str, Any]:
    """
    Google認証を事前初期化
    
    Returns:
        初期化結果の辞書
    """
    global _storage_client, _genai_configured, _initialization_error
    
    result = {
        "success": False,
        "storage_client": None,
        "genai_configured": False,
        "error": None
    }
    
    try:
        print("🔑 Google認証の事前初期化を開始...")
        
        # 1. Google AI API設定
        api_key = os.environ.get('GOOGLE_API_KEY')
        if not api_key:
            error_msg = "GOOGLE_API_KEY環境変数が設定されていません"
            print(f"❌ {error_msg}")
            _initialization_error = error_msg
            result["error"] = error_msg
            return result
        
        genai.configure(api_key=api_key)
        _genai_configured = True
        print("✅ Google AI API認証完了")
        
        # 2. Cloud Storage クライアント初期化
        _storage_client = _create_storage_client()
        if _storage_client:
            print("✅ Cloud Storage クライアント初期化完了")
        else:
            error_msg = "Cloud Storage クライアントの初期化に失敗"
            print(f"❌ {error_msg}")
            _initialization_error = error_msg
            result["error"] = error_msg
            return result
        
        result["success"] = True
        result["storage_client"] = _storage_client
        result["genai_configured"] = _genai_configured
        
        print("🎉 Google認証の事前初期化完了!")
        return result
        
    except Exception as e:
        error_msg = f"認証初期化エラー: {str(e)}"
        print(f"❌ {error_msg}")
        _initialization_error = error_msg
        result["error"] = error_msg
        return result

def _create_storage_client() -> Optional[storage.Client]:
    """
    Cloud Storage クライアントを作成
    
    Returns:
        Cloud Storage クライアントまたはNone
    """
    try:
        # 認証設定 - Cloud Run環境での認証ファイルパスを修正
        if os.path.exists("/app/service-account-key.json"):
            credentials_path = "/app/service-account-key.json"
        elif os.path.exists("service-account-key.json"):
            credentials_path = os.path.join(os.getcwd(), "service-account-key.json")
        else:
            # 環境変数からBase64エンコードされた認証情報を使用
            credentials_base64 = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS_BASE64')
            if credentials_base64:
                import base64
                import tempfile
                
                # Base64デコードして一時ファイルに保存
                credentials_json = base64.b64decode(credentials_base64).decode('utf-8')
                with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                    f.write(credentials_json)
                    credentials_path = f.name
                print(f"🔑 一時的な認証ファイルを作成: {credentials_path}")
            else:
                # デフォルトの認証方法を使用（Cloud Run環境での自動認証）
                print("🔑 Cloud Run環境での自動認証を使用")
                credentials_path = None
        
        if credentials_path:
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
        else:
            # Cloud Run環境での自動認証を使用する場合、環境変数をクリア
            if 'GOOGLE_APPLICATION_CREDENTIALS' in os.environ:
                del os.environ['GOOGLE_APPLICATION_CREDENTIALS']
        
        # Cloud Storage クライアント作成
        client = storage.Client()
        
        # 接続テスト
        bucket_name = "childstory-ggl-research-3db4311e"
        bucket = client.bucket(bucket_name)
        # バケットの存在確認（軽量な操作）
        bucket.exists()
        
        return client
        
    except Exception as e:
        print(f"❌ Cloud Storage クライアント作成エラー: {e}")
        return None

def get_storage_client() -> Optional[storage.Client]:
    """
    認証済みのCloud Storage クライアントを取得
    
    Returns:
        Cloud Storage クライアントまたはNone
    """
    global _storage_client, _initialization_error
    
    if _storage_client is None and _initialization_error is None:
        # 初期化がまだ実行されていない場合
        print("⚠️ 認証が初期化されていません。初期化を実行します...")
        initialize_google_services()
    
    if _storage_client is None:
        print(f"❌ Cloud Storage クライアントが利用できません: {_initialization_error}")
    
    return _storage_client

def is_genai_configured() -> bool:
    """
    Google AI APIが設定済みかどうかを確認
    
    Returns:
        設定済みの場合True
    """
    global _genai_configured, _initialization_error
    
    if not _genai_configured and _initialization_error is None:
        # 初期化がまだ実行されていない場合
        print("⚠️ 認証が初期化されていません。初期化を実行します...")
        initialize_google_services()
    
    return _genai_configured

def get_initialization_status() -> Dict[str, Any]:
    """
    初期化状態を取得
    
    Returns:
        初期化状態の辞書
    """
    return {
        "storage_client_ready": _storage_client is not None,
        "genai_configured": _genai_configured,
        "error": _initialization_error
    }
