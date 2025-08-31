"""
シンプル並行処理ツール - 安定した1つのツールで画像生成
ADKの複数ツール問題を回避した実装
"""

import os
import time
import concurrent.futures
from typing import Dict, Any
from google.adk.tools import FunctionTool
import google.generativeai as genai
from google.cloud import storage

# グローバル変数で画像結果を保存
_last_image_result = None

def get_last_image_result() -> Dict[str, Any]:
    """
    最後に生成された画像結果を取得
    
    Returns:
        画像生成結果（辞書）またはNone
    """
    global _last_image_result
    return _last_image_result

def clear_last_image_result():
    """
    最後の画像結果をクリア
    """
    global _last_image_result
    _last_image_result = None

def generate_story_image_parallel(story_content: str, image_type: str) -> Dict[str, Any]:
    """
    ストーリー内容に基づいて画像を並行生成
    
    Args:
        story_content: ストーリーの内容
        image_type: 画像タイプ ("single", "p2", "p3")
        
    Returns:
        画像生成結果
    """
    try:
        print(f"🎨 画像生成開始: {story_content[:50]}...")
        
        # Google AI API設定
        api_key = os.environ.get('GOOGLE_API_KEY')
        if not api_key:
            return {
                "success": False,
                "message": "GOOGLE_API_KEY環境変数が設定されていません",
                "images": []
            }
        
        genai.configure(api_key=api_key)
        
        # ThreadPoolExecutorを使った並行処理
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            # 画像生成タスクを並行実行
            future = executor.submit(_generate_single_image, story_content, image_type)
            
            try:
                # 最大60秒でタイムアウト
                result = future.result(timeout=60)
                print(f"✅ 並行画像生成完了!")
                
                # グローバル変数に結果を保存
                global _last_image_result
                _last_image_result = result
                
                return result
                
            except concurrent.futures.TimeoutError:
                print(f"⏰ 画像生成タイムアウト（60秒）")
                return {
                    "success": False,
                    "message": "画像生成がタイムアウトしました",
                    "images": []
                }
            except Exception as e:
                print(f"❌ 並行処理エラー: {e}")
                return {
                    "success": False,
                    "message": f"並行処理エラー: {str(e)}",
                    "images": []
                }
                
    except Exception as e:
        print(f"❌ ツール実行エラー: {e}")
        return {
            "success": False,
            "message": f"ツール実行エラー: {str(e)}",
            "images": []
        }

def generate_story_image_with_reference(story_content: str, reference_image_url: str, image_type: str) -> Dict[str, Any]:
    """
    参照画像を使用してストーリー内容に基づいて画像を生成
    
    Args:
        story_content: ストーリーの内容
        reference_image_url: 参照画像のURL
        image_type: 画像タイプ ("p3_with_p2_reference")
        
    Returns:
        画像生成結果
    """
    try:
        print(f"🎨 参照画像付き画像生成開始: {story_content[:50]}...")
        print(f"🖼️ 参照画像URL: {reference_image_url}")
        
        # Google AI API設定
        api_key = os.environ.get('GOOGLE_API_KEY')
        if not api_key:
            return {
                "success": False,
                "message": "GOOGLE_API_KEY環境変数が設定されていません",
                "images": []
            }
        
        genai.configure(api_key=api_key)
        
        # ThreadPoolExecutorを使った並行処理
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            # 画像生成タスクを並行実行
            future = executor.submit(_generate_image_with_reference, story_content, reference_image_url, image_type)
            
            try:
                # 最大60秒でタイムアウト
                result = future.result(timeout=60)
                print(f"✅ 参照画像付き並行画像生成完了!")
                
                # グローバル変数に結果を保存
                global _last_image_result
                _last_image_result = result
                
                return result
                
            except concurrent.futures.TimeoutError:
                print(f"⏰ 画像生成タイムアウト（60秒）")
                return {
                    "success": False,
                    "message": "画像生成がタイムアウトしました",
                    "images": []
                }
            except Exception as e:
                print(f"❌ 並行処理エラー: {e}")
                return {
                    "success": False,
                    "message": f"並行処理エラー: {str(e)}",
                    "images": []
                }
                
    except Exception as e:
        print(f"❌ ツール実行エラー: {e}")
        return {
            "success": False,
            "message": f"ツール実行エラー: {str(e)}",
            "images": []
        }

def _generate_single_image(story_content: str, image_type: str) -> Dict[str, Any]:
    """
    単一画像生成の内部実装
    
    Args:
        story_content: ストーリー内容
        image_type: 画像タイプ ("single", "p2", "p3")
        
    Returns:
        画像生成結果
    """
    try:
        # Gemini 2.5 Flash Image Previewモデル
        model = genai.GenerativeModel('gemini-2.5-flash-image-preview')
        
        # 画像生成プロンプト
        image_prompt = f"""Create a colorful children's book illustration based on this story:

{story_content}

Style requirements:
- Cute children's picture book art style
- Bright, warm, and cheerful colors
- Friendly and safe atmosphere
- Perfect for ages 3-8
- Happy ending scene
- No scary or violent content

Create a heartwarming final scene that shows the happy conclusion of this story."""
        
        print(f"📝 画像プロンプト生成完了")
        print(f"📋 生成されたプロンプト:")
        print(f"---")
        print(image_prompt)
        print(f"---")
        
        # 画像生成実行
        print(f"🎨 Gemini API呼び出し開始...")
        response = model.generate_content(image_prompt)
        print(f"📋 Gemini API応答: {response}")
        
        if not response:
            raise ValueError("画像生成レスポンスが空です")
        
        print(f"📊 レスポンス詳細:")
        print(f"  - candidates: {response.candidates}")
        print(f"  - candidates数: {len(response.candidates) if response.candidates else 0}")
        
        if not response.candidates:
            raise ValueError("画像生成レスポンスにcandidatesがありません")
        
        candidate = response.candidates[0]
        print(f"📊 最初のcandidate:")
        print(f"  - content: {candidate.content}")
        print(f"  - parts: {candidate.content.parts if candidate.content else 'None'}")
        
        if not candidate.content:
            raise ValueError("candidateにcontentがありません")
        
        if not candidate.content.parts:
            raise ValueError("candidateにpartsがありません")
        
        # 画像データを抽出
        image_data = None
        print(f"🔍 partsの詳細検索:")
        for i, part in enumerate(candidate.content.parts):
            print(f"  - part[{i}]: {part}")
            print(f"    - hasattr(inline_data): {hasattr(part, 'inline_data')}")
            if hasattr(part, 'inline_data'):
                print(f"    - inline_data: {part.inline_data}")
                if part.inline_data:
                    print(f"    - inline_data.data: {len(part.inline_data.data) if part.inline_data.data else 'None'} bytes")
                    image_data = part.inline_data.data
                    break
        
        if not image_data:
            raise ValueError("画像データが生成されませんでした")
        
        print(f"🖼️ 画像データ抽出完了: {len(image_data)} bytes")
        
        # ファイル保存
        timestamp = int(time.time())
        file_path = f"story_parallel_{timestamp}.png"
        
        with open(file_path, 'wb') as f:
            f.write(image_data)
        
        print(f"💾 ローカル保存完了: {file_path}")
        
        # Cloud Storage アップロード
        cloud_url = _upload_to_cloud_storage(file_path, image_data)
        
        result = {
            "success": True,
            "message": "1個の画像を並行生成しました",
            "images": [{
                "id": 1,
                "prompt": image_prompt[:100] + "...",
                "file_path": file_path,
                "cloud_url": cloud_url,
                "description": "ストーリーのハッピーエンドシーン",
                "mime_type": "image/png"
            }]
        }
        
        print(f"✅ 画像生成完了: 1個")
        print(f"📋 結果: {result}")
        
        return result
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"❌ 画像生成エラー: {e}")
        print(f"📋 エラー詳細:\n{error_details}")
        return {
            "success": False,
            "message": f"画像生成エラー: {str(e)}",
            "error_details": error_details,
            "images": []
        }

def _generate_image_with_reference(story_content: str, reference_image_url: str, image_type: str) -> Dict[str, Any]:
    """
    参照画像を使用した画像生成の内部実装
    
    Args:
        story_content: ストーリー内容
        reference_image_url: 参照画像のURL
        image_type: 画像タイプ ("p3_with_p2_reference")
        
    Returns:
        画像生成結果
    """
    try:
        # Gemini 2.5 Flash Image Previewモデル
        model = genai.GenerativeModel('gemini-2.5-flash-image-preview')
        
        # 参照画像をダウンロード
        import requests
        print(f"📥 参照画像をダウンロード中: {reference_image_url}")
        response = requests.get(reference_image_url)
        if response.status_code != 200:
            raise ValueError(f"参照画像のダウンロードに失敗: {response.status_code}")
        
        reference_image_data = response.content
        print(f"📥 参照画像ダウンロード完了: {len(reference_image_data)} bytes")
        
        # 画像生成プロンプト
        image_prompt = f"""Create a colorful children's book illustration for the continuation of this story, maintaining the same art style and characters as the reference image:

Story continuation:
{story_content}

Style requirements:
- Maintain the exact same art style, colors, and character designs as the reference image
- Keep the same visual consistency and atmosphere
- Use the same drawing technique and color palette
- Ensure characters look identical to the reference image
- Create a natural continuation of the story scene
- Bright, warm, and cheerful children's book style
- Perfect for ages 3-8
- No scary or violent content

Create a scene that naturally follows from the reference image while maintaining visual consistency."""
        
        print(f"📝 参照画像付きプロンプト生成完了")
        print(f"📋 生成されたプロンプト:")
        print(f"---")
        print(image_prompt)
        print(f"---")
        
        # 参照画像とプロンプトを組み合わせて画像生成
        print(f"🎨 Gemini API呼び出し開始（参照画像付き）...")
        
        # 参照画像をPartとして追加
        import base64
        reference_image_part = {
            "mime_type": "image/png",
            "data": base64.b64encode(reference_image_data).decode('utf-8')
        }
        
        # テキストと画像を組み合わせたコンテンツを作成
        content_parts = [
            {"text": image_prompt},
            reference_image_part
        ]
        
        response = model.generate_content(content_parts)
        print(f"📋 Gemini API応答: {response}")
        
        if not response:
            raise ValueError("画像生成レスポンスが空です")
        
        print(f"📊 レスポンス詳細:")
        print(f"  - candidates: {response.candidates}")
        print(f"  - candidates数: {len(response.candidates) if response.candidates else 0}")
        
        if not response.candidates:
            raise ValueError("画像生成レスポンスにcandidatesがありません")
        
        candidate = response.candidates[0]
        print(f"📊 最初のcandidate:")
        print(f"  - content: {candidate.content}")
        print(f"  - parts: {candidate.content.parts if candidate.content else 'None'}")
        
        if not candidate.content:
            raise ValueError("candidateにcontentがありません")
        
        if not candidate.content.parts:
            raise ValueError("candidateにpartsがありません")
        
        # 画像データを抽出
        image_data = None
        print(f"🔍 partsの詳細検索:")
        for i, part in enumerate(candidate.content.parts):
            print(f"  - part[{i}]: {part}")
            print(f"    - hasattr(inline_data): {hasattr(part, 'inline_data')}")
            if hasattr(part, 'inline_data'):
                print(f"    - inline_data: {part.inline_data}")
                if part.inline_data:
                    print(f"    - inline_data.data: {len(part.inline_data.data) if part.inline_data.data else 'None'} bytes")
                    image_data = part.inline_data.data
                    break
        
        if not image_data:
            raise ValueError("画像データが生成されませんでした")
        
        print(f"🖼️ 画像データ抽出完了: {len(image_data)} bytes")
        
        # ファイル保存
        timestamp = int(time.time())
        file_path = f"story_reference_{timestamp}.png"
        
        with open(file_path, 'wb') as f:
            f.write(image_data)
        
        print(f"💾 ローカル保存完了: {file_path}")
        
        # Cloud Storage アップロード
        cloud_url = _upload_to_cloud_storage(file_path, image_data)
        
        result = {
            "success": True,
            "message": "1個の参照画像付き画像を生成しました",
            "images": [{
                "id": 1,
                "prompt": image_prompt[:100] + "...",
                "file_path": file_path,
                "cloud_url": cloud_url,
                "description": "参照画像を基にしたストーリー続編シーン",
                "mime_type": "image/png"
            }]
        }
        
        print(f"✅ 参照画像付き画像生成完了: 1個")
        print(f"📋 結果: {result}")
        
        return result
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"❌ 参照画像付き画像生成エラー: {e}")
        print(f"📋 エラー詳細:\n{error_details}")
        return {
            "success": False,
            "message": f"参照画像付き画像生成エラー: {str(e)}",
            "error_details": error_details,
            "images": []
        }

def _upload_to_cloud_storage(file_path: str, image_data: bytes) -> str:
    """Cloud Storageへのアップロード"""
    try:
        # 認証設定
        credentials_path = os.path.join(os.getcwd(), "service-account-key.json")
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
        
        # Cloud Storage クライアント
        client = storage.Client()
        bucket_name = "childstory-ggl-research-3db4311e"
        bucket = client.bucket(bucket_name)
        
        # ユニークなブロブ名
        blob_name = f"story-images/{file_path}"
        blob = bucket.blob(blob_name)
        
        # アップロード実行
        blob.upload_from_string(image_data, content_type='image/png')
        blob.make_public()
        
        public_url = f"https://storage.googleapis.com/{bucket_name}/{blob_name}"
        print(f"☁️ Cloud Storage アップロード完了: {public_url}")
        
        return public_url
        
    except Exception as e:
        print(f"❌ Cloud Storage エラー: {e}")
        return None

# ADK用ツール
simple_parallel_tool = FunctionTool(func=generate_story_image_parallel)
reference_image_tool = FunctionTool(func=generate_story_image_with_reference)

__all__ = ["simple_parallel_tool", "reference_image_tool"]
