"""
Text-to-Speech ツール - ストーリーの音声読み上げ機能
"""

import os
import time
from typing import Dict, Any
from google.adk.tools import FunctionTool
from gtts import gTTS
from google.cloud import storage

# 認証初期化モジュールをインポート
from auth_init import get_storage_client

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
    """音声ファイルをCloud Storageにアップロード（認証済みクライアント使用）"""
    try:
        # 認証済みのCloud Storage クライアントを取得
        client = get_storage_client()
        if client is None:
            raise Exception("Cloud Storage クライアントが利用できません")
        
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
