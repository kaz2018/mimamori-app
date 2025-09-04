"""
Text-to-Speech ツール - ストーリーの音声読み上げ機能
"""

import os
import time
from typing import Dict, Any
from google.adk.tools import FunctionTool
from gtts import gTTS
from google.cloud import storage

def generate_story_audio(story_text: str, language: str = "ja") -> Dict[str, Any]:
    """
    ストーリーテキストを音声に変換
    
    Args:
        story_text: 読み上げるストーリーテキスト
        language: 言語コード（デフォルト: "ja"）
        
    Returns:
        音声生成結果
    """
    try:
        print(f"🎤 音声生成開始: {story_text[:50]}...")
        
        # gTTSで音声生成
        tts = gTTS(text=story_text, lang=language, slow=False)
        
        # タイムスタンプ付きのファイル名を生成
        timestamp = int(time.time())
        file_name = f"story_audio_{timestamp}.mp3"
        
        # 一時的にローカルに保存（メモリから直接アップロードはgTTSでは困難）
        tts.save(file_name)
        
        print(f"💾 音声ファイル保存完了: {file_name}")
        
        # Cloud Storageにアップロード
        cloud_url = _upload_audio_to_cloud_storage(file_name)
        
        # ローカルファイルを削除（Cloud Storageアップロード成功時のみ）
        if cloud_url and os.path.exists(file_name):
            os.remove(file_name)
            print(f"🗑️ ローカルファイル削除: {file_name}")
        
        result = {
            "success": True,
            "message": "音声ファイルを生成しました",
            "audio": {
                "file_name": file_name,
                "cloud_url": cloud_url,
                "language": language,
                "duration_estimate": len(story_text) * 0.1  # 概算の再生時間（秒）
            }
        }
        
        print(f"✅ 音声生成完了: {cloud_url}")
        return result
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"❌ 音声生成エラー: {e}")
        print(f"📋 エラー詳細:\n{error_details}")
        return {
            "success": False,
            "message": f"音声生成エラー: {str(e)}",
            "error_details": error_details,
            "audio": None
        }

def _upload_audio_to_cloud_storage(file_name: str) -> str:
    """音声ファイルをCloud Storageにアップロード"""
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
        
        # Cloud Storage クライアント
        from google.cloud import storage
        client = storage.Client()
        bucket_name = "childstory-ggl-research-3db4311e"
        bucket = client.bucket(bucket_name)
        
        # ユニークなブロブ名
        blob_name = f"story-audio/{file_name}"
        blob = bucket.blob(blob_name)
        
        # ファイルをアップロード
        blob.upload_from_filename(file_name)
        blob.make_public()
        
        public_url = f"https://storage.googleapis.com/{bucket_name}/{blob_name}"
        print(f"☁️ Cloud Storage アップロード完了: {public_url}")
        
        return public_url
        
    except Exception as e:
        print(f"❌ Cloud Storage エラー: {e}")
        return None



# ADK用ツール
tts_tool = FunctionTool(func=generate_story_audio)

__all__ = ["tts_tool"]
