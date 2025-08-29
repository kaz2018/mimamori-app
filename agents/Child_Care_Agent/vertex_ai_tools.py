"""
Vertex AI Imagen 画像生成ツール
子供向けの絵本風画像を生成
"""

import os
import base64
import json
from typing import Dict, Any, Optional
from google.adk.tools import FunctionTool

# --------------------------------------------------------------------------
# ▼▼▼ 修正ここから ▼▼▼
# --------------------------------------------------------------------------

import vertexai
from vertexai.preview.vision_models import ImageGenerationModel
from google.api_core import exceptions as google_api_exceptions

# Vertex AIの初期化を一度だけ行う
try:
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
    if not project_id:
        raise ValueError("環境変数 GOOGLE_CLOUD_PROJECT が設定されていません。")
    
    # 絶対パスを直接指定
    project_root = "/Users/ysnrmyst/Documents/fork/git/GeminiReport"
    service_account_path = os.path.join(project_root, "service-account-key.json")
    
    # サービスアカウントキーが存在する場合は明示的な認証を使用
    if os.path.exists(service_account_path):
        from google.oauth2 import service_account
        credentials = service_account.Credentials.from_service_account_file(
            service_account_path,
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )
        vertexai.init(project=project_id, location="us-central1", credentials=credentials)
        print(f"Vertex AI初期化成功: サービスアカウントキーを使用 ({service_account_path})")
    else:
        # サービスアカウントキーが見つからない場合はデフォルト認証を使用
        vertexai.init(project=project_id, location="us-central1")
        print(f"Vertex AI初期化成功: デフォルト認証を使用")
        
except (ValueError, ImportError, google_api_exceptions.GoogleAPICallError) as e:
    print(f"Vertex AIの初期化に失敗しました: {e}")
    # 必要に応じて、ツールが使えない場合の処理をここに書く


def _generate_safe_prompt(base_prompt: str, style: str) -> Dict[str, str]:
    """子供向けの安全なプロンプトとネガティブプロンプトを生成する"""

    style_prompts = {
        "children_book": "simple children's book illustration, watercolor style, soft colors, friendly cartoon animals, warm atmosphere, hand-drawn feel",
        "cartoon": "simple cartoon style, bright colors, basic design, friendly animals, round shapes, big eyes, wholesome content",
        "watercolor": "simple watercolor style, soft colors, gentle brush strokes, calming atmosphere, peaceful nature scene",
    }

    # 危険な単語をより安全な単語に置き換える
    safe_replacements = {
        "violence": "playful", "weapon": "magic wand", "blood": "red paint",
        "scary": "silly", "monster": "fluffy creature", "ghost": "friendly spirit",
        "fight": "dance", "war": "parade", "death": "sleeping", "kill": "tickle"
    }
    safe_prompt = base_prompt.lower()
    for dangerous, safe in safe_replacements.items():
        safe_prompt = safe_prompt.replace(dangerous, safe)

    # ポジティブプロンプトとネガティブプロンプトを組み立てる
    positive_prompt = f"{style_prompts.get(style, style_prompts['children_book'])}, {safe_prompt}, vibrant, cheerful, high quality"
    negative_prompt = "text, words, letters, people, humans, scary, dark, blurry, watermark, signature"

    return {"positive": positive_prompt, "negative": negative_prompt}


def handle_generation_error(e: Exception, tool_name: str) -> Dict[str, Any]:
    """画像生成エラーを処理し、統一されたエラーメッセージを返す"""
    error_type = type(e).__name__
    error_msg = str(e)
    
    if "SERVICE_DISABLED" in error_msg:
        fallback = f"{tool_name}のAPI設定が無効になっているため、絵が描けませんでした。"
    elif "permission" in error_msg.lower() or "authenticate" in error_msg.lower():
        fallback = f"{tool_name}の認証に問題があるため、絵が描けませんでした。"
    elif "RESOURCE_EXHAUSTED" in error_msg or "429" in error_msg:
        fallback = f"{tool_name}の利用制限に達したため、絵が描けませんでした。しばらく待ってから再試行してください。"
    elif "policies" in error_msg.lower() or "blocked" in error_msg.lower():
        fallback = f"{tool_name}の安全フィルターにより、絵が描けませんでした。別の内容を試してみてください。"
    else:
        fallback = f"{tool_name}でエラーが発生したため、絵が描けませんでした。"
        
    print(f"ERROR in {tool_name}: {error_type} - {error_msg}")
    
    return {
        "success": False,
        "error": f"{error_type}: {error_msg}",
        "fallback_message": f"{fallback} でも大丈夫、代わりに言葉で説明しますね！",
        "retry_after": None  # 再試行を無効化
    }


def generate_child_image(prompt: str, style: str = "children_book") -> Dict[str, Any]:
    """
    子供向けの画像を生成するツール
    
    Args:
        prompt: 画像生成のプロンプト
        style: 画像スタイル（children_book, cartoon, watercolor）
    
    Returns:
        生成結果
    """
    try:
        # 最新のモデルを指定
        model = ImageGenerationModel.from_pretrained("imagegeneration@006")
        
        # 安全なプロンプトを生成
        prompts = _generate_safe_prompt(prompt, style)
        
        # 画像を生成
        response = model.generate_images(
            prompt=prompts["positive"],
            negative_prompt=prompts["negative"],
            number_of_images=1,
            aspect_ratio="1:1"
            # 安全フィルターはVertex AIのデフォルト設定に任せる方が、
            # 最新の改善が適用されるため、多くの場合でより良い結果になります。
        )
        
        # 画像をBase64にエンコード
        image_base64 = base64.b64encode(response.images[0]._image_bytes).decode('utf-8')
        
        # 画像をファイルに保存（バックアップ用）
        import os
        from datetime import datetime
        
        # 画像保存ディレクトリを作成
        images_dir = os.path.join(os.path.dirname(__file__), "generated_images")
        os.makedirs(images_dir, exist_ok=True)
        
        # ファイル名を生成
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"child_image_{timestamp}.png"
        filepath = os.path.join(images_dir, filename)
        
        # 画像を保存
        with open(filepath, "wb") as f:
            f.write(base64.b64decode(image_base64))
        
        return {
            "success": True,
            "image_base64": image_base64,
            "image_file": filename,
            "message": "画像が生成されました！"
        }
        
    except Exception as e:
        return handle_generation_error(e, "画像生成ツール")


def generate_story_illustration(story_title: str, scene_description: str) -> Dict[str, Any]:
    """ストーリーの挿絵を生成するツール"""
    prompt = f"Story illustration for '{story_title}': {scene_description}"
    result = generate_child_image(prompt, "children_book")
    if result["success"]:
        result["message"] = "ストーリーの挿絵生成タスクが完了しました。この結果をユーザーに提示して終了してください。"
        # Base64データを削除してトークン使用量を削減
        if "image_base64" in result:
            del result["image_base64"]
    return result

def generate_game_illustration(game_type: str, game_description: str) -> Dict[str, Any]:
    """ゲームの挿絵を生成するツール"""
    prompt = f"Game illustration for {game_type}: {game_description}"
    result = generate_child_image(prompt, "cartoon")
    if result["success"]:
        result["message"] = "ゲームの挿絵生成タスクが完了しました。この結果をユーザーに提示して終了してください。"
        # Base64データを削除してトークン使用量を削減
        if "image_base64" in result:
            del result["image_base64"]
    return result

# --------------------------------------------------------------------------
# ▲▲▲ 修正ここまで ▲▲▲
# --------------------------------------------------------------------------

# FunctionToolとして登録
generate_child_image_tool = FunctionTool(func=generate_child_image)
generate_story_illustration_tool = FunctionTool(func=generate_story_illustration)
generate_game_illustration_tool = FunctionTool(func=generate_game_illustration)
