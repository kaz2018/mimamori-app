"""
画像生成ツール
Gemini 2.5 Flash Image Previewモデルを使用した画像生成機能
"""

import os
import base64
import mimetypes
import uuid
from datetime import datetime
from google import genai
from google.genai import types
from google.adk.tools import FunctionTool
from google.cloud import storage


def upload_to_cloud_storage(image_data: bytes, filename: str, bucket_name: str = "childstory-ggl-research-3db4311e") -> str:
    """
    画像をCloud Storage（childstoryバケット）にアップロードして公開URLを返す
    
    Args:
        image_data: 画像のバイナリデータ
        filename: ファイル名（images/フォルダに保存）
        bucket_name: Cloud Storageバケット名（デフォルト: childstory-ggl-research-3db4311e）
    
    Returns:
        str: 公開URL
    """
    try:
        # Cloud Storageクライアントを初期化（認証情報を明示的に指定）
        import os
        credentials_path = os.path.join(os.getcwd(), "service-account-key.json")
        if os.path.exists(credentials_path):
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
        
        client = storage.Client()
        
        # 既存のバケットを取得
        bucket = client.bucket(bucket_name)
        
        # ファイルをアップロード
        blob = bucket.blob(filename)
        blob.upload_from_string(image_data, content_type='image/png')
        
        # 公開アクセス可能にする
        blob.make_public()
        
        # 公開URLを返す
        return blob.public_url
        
    except Exception as e:
        print(f"Cloud Storageアップロードエラー: {e}")
        print(f"認証ファイルパス: {os.environ.get('GOOGLE_APPLICATION_CREDENTIALS', 'None')}")
        print(f"現在のディレクトリ: {os.getcwd()}")
        print(f"service-account-key.json存在確認: {os.path.exists('service-account-key.json')}")
        return None


def generate_story_images(story_theme: str, image_count: int = 1) -> dict:
    """
    ストーリーテーマに基づいて複数の画像を生成します
    
    Args:
        story_theme: ストーリーのテーマ（例：「森の動物たちの冒険」）
        image_count: 生成する画像の数（デフォルト：4）
    
    Returns:
        dict: 生成された画像の情報
    """
    try:
        # Gemini APIクライアントを初期化
        client = genai.Client(
            api_key=os.environ.get("GEMINI_API_KEY"),
        )

        model = "gemini-2.5-flash-image-preview"
        
        # 結末シーンの画像生成
        image_prompts = [
            f"Create a colorful illustration image for children: {story_theme} happy ending scene with cute animals celebrating. Draw a bright, cheerful picture showing the conclusion of the story."
        ]
        
        generated_images = []
        
        for i, prompt in enumerate(image_prompts[:image_count]):
            contents = [
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_text(text=prompt),
                    ],
                ),
            ]
            
            generate_content_config = types.GenerateContentConfig(
                response_modalities=[
                    "IMAGE",
                    "TEXT",
                ],
            )
            
            # 画像生成実行
            try:
                response = client.models.generate_content(
                    model=model,
                    contents=contents,
                    config=generate_content_config,
                )
                print(f"画像生成レスポンス: {response}")
            except Exception as e:
                print(f"画像生成エラー: {e}")
                continue
            
            # 生成された画像を保存
            print(f"レスポンス候補数: {len(response.candidates) if response.candidates else 0}")
            if (response.candidates and 
                response.candidates[0].content and 
                response.candidates[0].content.parts):
                
                print(f"パート数: {len(response.candidates[0].content.parts)}")
                for part in response.candidates[0].content.parts:
                    print(f"パートタイプ: {type(part)}, inline_data: {hasattr(part, 'inline_data')}")
                    if part.inline_data and part.inline_data.data:
                        inline_data = part.inline_data
                        data_buffer = inline_data.data
                        file_extension = mimetypes.guess_extension(inline_data.mime_type) or ".png"
                        
                        # ユニークなファイル名を生成（images/フォルダ内に配置）
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        unique_id = str(uuid.uuid4())[:8]
                        filename = f"images/story_scene_{timestamp}_{unique_id}{file_extension}"
                        
                        # ローカルにも保存（バックアップ）
                        local_path = f"story_ending_scene{file_extension}"
                        with open(local_path, "wb") as f:
                            f.write(data_buffer)
                        
                        # Cloud Storageにアップロード
                        public_url = upload_to_cloud_storage(data_buffer, filename)
                        
                        if public_url:
                                                    generated_images.append({
                            "id": 1,
                            "prompt": prompt,
                            "file_path": local_path,
                            "cloud_url": public_url,
                            "description": f"ハッピーエンド: {story_theme}の物語の結末",
                            "mime_type": inline_data.mime_type
                        })
                        else:
                            # Cloud Storageアップロードに失敗した場合はローカルパスのみ
                            generated_images.append({
                                "id": 1,
                                "prompt": prompt,
                                "file_path": local_path,
                                "cloud_url": None,
                                "description": f"ハッピーエンド: {story_theme}の物語の結末",
                                "mime_type": inline_data.mime_type
                            })
                        break
                else:
                    print("画像データが見つかりませんでした")
            else:
                print("有効なレスポンスが取得できませんでした")
        
        return {
            "success": True,
            "message": f"{len(generated_images)}個の画像を生成しました",
            "images": generated_images
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"画像生成エラー: {str(e)}",
            "images": []
        }


def create_single_story_image(description: str, scene_type: str = "general") -> dict:
    """
    単一のストーリー画像を生成します
    
    Args:
        description: 画像の詳細説明
        scene_type: シーンタイプ（beginning, adventure, climax, ending, general）
    
    Returns:
        dict: 生成された画像の情報
    """
    try:
        client = genai.Client(
            api_key=os.environ.get("GEMINI_API_KEY"),
        )

        model = "gemini-2.5-flash-image-preview"
        
        # シーンタイプに応じたプロンプト調整
        scene_prefixes = {
            "beginning": "物語の始まり：",
            "adventure": "冒険シーン：",
            "climax": "クライマックス：",
            "ending": "ハッピーエンド：",
            "general": ""
        }
        
        prefix = scene_prefixes.get(scene_type, "")
        prompt = f"子供向け絵本のイラスト：{prefix}{description}。明るく可愛らしいスタイルで、教育的価値のある内容。"
        
        contents = [
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(text=prompt),
                ],
            ),
        ]
        
        generate_content_config = types.GenerateContentConfig(
            response_modalities=[
                "IMAGE",
                "TEXT",
            ],
        )
        
        # 画像生成実行
        response = client.models.generate_content(
            model=model,
            contents=contents,
            config=generate_content_config,
        )
        
        # 生成された画像を保存
        if (response.candidates and 
            response.candidates[0].content and 
            response.candidates[0].content.parts):
            
            for part in response.candidates[0].content.parts:
                if part.inline_data and part.inline_data.data:
                    file_name = f"single_story_image_{scene_type}"
                    inline_data = part.inline_data
                    data_buffer = inline_data.data
                    file_extension = mimetypes.guess_extension(inline_data.mime_type)
                    
                    # ファイルを保存
                    save_path = f"{file_name}{file_extension}"
                    with open(save_path, "wb") as f:
                        f.write(data_buffer)
                    
                    return {
                        "success": True,
                        "message": "画像を生成しました",
                        "image": {
                            "prompt": prompt,
                            "file_path": save_path,
                            "description": description,
                            "scene_type": scene_type
                        }
                    }
        
        return {
            "success": False,
            "message": "画像生成に失敗しました",
            "image": None
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"画像生成エラー: {str(e)}",
            "image": None
        }


# FunctionToolでツールを作成
generate_story_images_tool = FunctionTool(func=generate_story_images)
create_single_story_image_tool = FunctionTool(func=create_single_story_image)

__all__ = ["generate_story_images_tool", "create_single_story_image_tool"]
