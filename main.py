from fastapi import FastAPI, Request, HTTPException, Query, BackgroundTasks
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from agents.Child_Care_Agent import root_agent as child_care_agent
from agents.StoryTelling_Agent import root_agent as storytelling_agent
from agents.StoryTelling_Agent.simple_parallel_tool import get_last_image_result, clear_last_image_result
from google.adk.runners import InMemoryRunner
from google.genai.types import Part, UserContent
# ToolOutputEventのインポートを削除（利用できないため）
import os
import uvicorn
import yaml

# ★★★★★★★★★★★★★★★★★★★★★★★★★★★★★
# セッション全体のデータを保存する辞書
SESSIONS = {}
# ★★★★★★★★★★★★★★★★★★★★★★★★★★★★★

# 環境変数の読み込み
def load_env_files():
    env_files = ['api_key_env.yaml', 'env.yaml']
    for env_file in env_files:
        if os.path.exists(env_file):
            with open(env_file, 'r') as f:
                env_vars = yaml.safe_load(f)
                for key, value in env_vars.items():
                    os.environ[key] = str(value)
                    print(f"Loaded env var: {key}")

load_env_files()

app = FastAPI()

# CORS設定を追加
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

AGENT_MAP = {
    "child_care": child_care_agent,
    "storytelling": storytelling_agent,
}

# 各エージェントのInMemoryRunnerを作成
RUNNER_MAP = {}
for agent_name, agent in AGENT_MAP.items():
    RUNNER_MAP[agent_name] = InMemoryRunner(agent=agent)

# srcフォルダを静的ファイルとして提供
app.mount("/src", StaticFiles(directory="src"), name="src")

# 背景で画像生成を実行する関数
def generate_image_task(session_id: str, page_num: int, story_text: str, reference_image_url: str = None):
    print(f"🖼️ Background task started for Session {session_id}, Page {page_num}")
    
    # reference_image_url があれば、それを使って生成
    if reference_image_url:
        print(f"🖼️ Using reference image: {reference_image_url}")
        from agents.StoryTelling_Agent.simple_parallel_tool import generate_story_image_with_reference
        result = generate_story_image_with_reference(story_text, reference_image_url, f"p{page_num}_with_ref")
    else:
        # なければ通常の生成
        from agents.StoryTelling_Agent.simple_parallel_tool import generate_story_image_parallel
        result = generate_story_image_parallel(story_text, f"p{page_num}")
    
    if result and result.get("success"):
        image_url = result["images"][0].get("cloud_url")
        # セッションデータに画像URLを保存
        if session_id in SESSIONS:
            SESSIONS[session_id]["image_urls"][page_num] = image_url
            print(f"🖼️ Image URL for P{page_num} saved for Session {session_id}: {image_url}")
        else:
            print(f"⚠️ Session {session_id} not found when saving image URL")
    else:
        print(f"❌ Image generation failed for P{page_num}")
        # エラー時はNoneを保存して次のページに遷移できるようにする
        if session_id in SESSIONS:
            SESSIONS[session_id]["image_urls"][page_num] = None
            print(f"⚠️ Setting P{page_num} image URL to None due to generation failure")
        else:
            print(f"⚠️ Session {session_id} not found when handling image generation failure")

# ADKの標準的なWeb UIの静的ファイルを提供
try:
    # ADKのbrowserディレクトリのパスを取得
    import google.adk.cli.browser as adk_browser
    adk_browser_path = os.path.dirname(adk_browser.__file__)
    
    # 静的ファイルをマウント
    app.mount("/adk-ui", StaticFiles(directory=adk_browser_path), name="adk-ui")
    
    # ADKの標準UIのHTMLを提供
    @app.get("/", response_class=HTMLResponse)
    async def adk_standard_ui():
        """ADKの標準的なWeb UIを提供"""
        try:
            index_path = os.path.join(adk_browser_path, "index.html")
            if not os.path.exists(index_path):
                raise FileNotFoundError(f"ADK UI index.html not found at {index_path}")
                
            with open(index_path, "r", encoding="utf-8") as f:
                html_content = f.read()
            
            # ADKの標準UIのパスを修正
            html_content = html_content.replace('href="/', 'href="/adk-ui/')
            html_content = html_content.replace('src="/', 'src="/adk-ui/')
            
            return HTMLResponse(content=html_content)
        except Exception as e:
            return HTMLResponse(content=f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>ADK Standard UI</title>
                <meta charset="utf-8">
            </head>
            <body>
                <h1>ADK Standard UI</h1>
                <p>Error loading ADK UI: {e}</p>
                <p>ADK browser path: {adk_browser_path}</p>
                <p>Available agents: {', '.join(AGENT_MAP.keys())}</p>
                <hr>
                <h2>Direct Agent Access:</h2>
                <ul>
                    <li><a href="/agent/storytelling">Storytelling Agent</a></li>
                    <li><a href="/agent/child_care">Child Care Agent</a></li>
                </ul>
            </body>
            </html>
            """)
            
except Exception as e:
    print(f"Warning: Could not load ADK standard UI: {e}")
    
    # フォールバック: シンプルなエージェント選択UI
    @app.get("/", response_class=HTMLResponse)
    async def fallback_ui():
        return HTMLResponse(content=f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>GeminiReport Agents</title>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .agent-card {{ border: 1px solid #ddd; padding: 20px; margin: 10px 0; border-radius: 8px; }}
                .agent-card h3 {{ margin-top: 0; }}
            </style>
        </head>
        <body>
            <h1>🎭 GeminiReport Agents</h1>
            <p>ADK Standard UI could not be loaded. Using fallback interface.</p>
            
            <div class="agent-card">
                <h3>📚 Storytelling Agent</h3>
                <p>3ページ構成の子供向け絵本を作成します</p>
                <a href="/agent/storytelling">Access Storytelling Agent</a>
            </div>
            
            <div class="agent-card">
                <h3>👶 Child Care Agent</h3>
                <p>子供の見守りに関するアドバイスを提供します</p>
                <a href="/agent/child_care">Access Child Care Agent</a>
            </div>
            
            <hr>
            <p><a href="/src/story_top.html">📖 Custom Storytelling UI</a></p>
        </body>
        </html>
        """)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "GeminiReport API is running"}

@app.get("/agent/{agent_name}")
async def run_agent_get(agent_name: str, input: str = Query(None, description="質問内容を指定してください（省略時は「こんにちは」で開始）")):
    agent = AGENT_MAP.get(agent_name)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # inputが指定されていない場合は「こんにちは」をデフォルトとして使用
    user_input = input if input else "こんにちは"
    
    # InMemoryRunnerを使用してエージェントを実行
    runner = RUNNER_MAP[agent_name]
    session = await runner.session_service.create_session(
        app_name=runner.app_name, user_id="web_user"
    )
    
    content = UserContent(parts=[Part(text=user_input)])
    
    # エージェントを実行して結果を取得
    result = ""
    for event in runner.run(
        user_id=session.user_id, session_id=session.id, new_message=content
    ):
        if hasattr(event, 'content') and hasattr(event.content, 'parts'):
            for part in event.content.parts:
                if hasattr(part, 'text') and part.text is not None:
                    result += part.text
    
    return {"result": result}

@app.post("/agent/storytelling/start")
async def start_story(request: Request, background_tasks: BackgroundTasks):
    data = await request.json()
    topic = data.get("topic", "動物の話")
    
    print(f"🔄 ストーリー開始: topic={topic}")

    runner = RUNNER_MAP["storytelling"]
    session = await runner.session_service.create_session(
        app_name=runner.app_name, user_id="web_user"
    )
    session_id = session.id
    print(f"💾 セッション作成: {session_id}")
    
    # 1. エージェントを一度だけ呼び出し、3ページ分の物語を取得
    full_story_text = ""
    content = UserContent(parts=[Part(text=topic)])
    for event in runner.run(user_id=session.user_id, session_id=session_id, new_message=content):
        if hasattr(event, 'content'):
            for part in event.content.parts:
                if hasattr(part, 'text'):
                    full_story_text += part.text
    
    print(f"📝 生成された物語テキスト: {full_story_text[:200]}...")
    
    # 2. 物語をページごとに分割
    pages = {}
    # 正規表現で[PAGE_X]と次の[PAGE_X]の間のテキストを抽出
    import re
    matches = re.finditer(r'\[PAGE_(\d+)\]\s*(.*?)\s*(?=\[PAGE_\d+\]|$)', full_story_text, re.DOTALL)
    for match in matches:
        page_num = int(match.group(1))
        text = match.group(2).strip()
        # 3ページまでしか受け入れない
        if page_num <= 3:
            pages[page_num] = text
            print(f"📄 P{page_num}抽出: {text[:50]}...")
        else:
            print(f"⚠️ P{page_num}は無視（3ページ制限）")

    print(f"📚 抽出されたページ数: {len(pages)}")
    print(f"📋 利用可能なページ: {list(pages.keys())}")

    # 3. セッションデータを作成・保存
    SESSIONS[session_id] = {
        "story_pages": pages,
        "current_page": 1,
        "image_urls": {} # 生成された画像URLをここに保存
    }
    print(f"💾 セッションデータ保存: {session_id}")

    # 4. P1の画像を同期的に生成
    if 1 in pages:
        print(f"🖼️ P1画像生成開始: {session_id}")
        from agents.StoryTelling_Agent.simple_parallel_tool import generate_story_image_parallel
        p1_result = generate_story_image_parallel(pages[1], "p1")
        
        if p1_result and p1_result.get("success"):
            p1_image_url = p1_result["images"][0].get("cloud_url")
            SESSIONS[session_id]["image_urls"][1] = p1_image_url
            print(f"✅ P1画像生成完了: {p1_image_url}")
        else:
            print(f"❌ P1画像生成失敗")
            p1_image_url = None
    else:
        print(f"⚠️ P1のページが見つかりません")
        p1_image_url = None

    # 5. P1のテキストとセッションIDを返す
    result = {
        "session_id": session_id,
        "text_result": pages.get(1, "物語の生成に失敗しました。"),
        "image_url": p1_image_url
    }
    print(f"✅ レスポンス返却: session_id={session_id}, text_len={len(result['text_result'])}")
    
    # 6. P2の画像をバックグラウンドで先行生成
    if 2 in pages:
        print(f"🖼️ P2画像生成タスク開始: {session_id}")
        # ★ p1_image_url を引数として渡すように修正
        background_tasks.add_task(generate_image_task, session_id, 2, pages[2], p1_image_url)
        print(f"✅ P2画像生成タスク登録完了")
    else:
        print(f"⚠️ P2のページが見つかりません")
    
    return result

@app.post("/agent/storytelling/next")
async def next_page(request: Request, background_tasks: BackgroundTasks):
    data = await request.json()
    session_id = data.get("session_id")
    
    print(f"🔄 ストーリー継続: session_id={session_id}")
    print(f"📊 現在のセッション数: {len(SESSIONS)}")
    print(f"🔍 利用可能なセッション: {list(SESSIONS.keys())}")

    if not session_id or session_id not in SESSIONS:
        print(f"❌ セッションが見つかりません: {session_id}")
        raise HTTPException(status_code=404, detail="Session not found")

    session_data = SESSIONS[session_id]
    print(f"✅ セッション発見: {session_id}")
    print(f"📄 現在のページ: {session_data['current_page']}")
    print(f"📚 利用可能なページ: {list(session_data['story_pages'].keys())}")
    
    # 次のページに進める
    session_data["current_page"] += 1
    current_page_num = session_data["current_page"]
    print(f"🔄 次のページに進行: P{current_page_num}")
    
    # ページと画像URLを取得
    text_result = session_data["story_pages"].get(current_page_num, "")
    image_url = session_data["image_urls"].get(current_page_num)
    
    print(f"📝 取得したテキスト: {text_result[:100]}...")
    print(f"🖼️ 取得した画像URL: {image_url}")
    print(f"📊 現在の画像URL一覧: {session_data['image_urls']}")
    
    # 画像URLがない場合は、少し待ってから再確認
    if not image_url:
        import asyncio
        print(f"⏳ P{current_page_num}の画像URLを待機中...")
        # 最大15秒まで待機（3秒ずつ5回）
        for i in range(5):
            await asyncio.sleep(3)
            image_url = session_data["image_urls"].get(current_page_num)
            if image_url:
                print(f"✅ P{current_page_num}の画像URL取得: {image_url}")
                break
            else:
                print(f"⏳ P{current_page_num}の画像URL待機中... ({i+1}/5)")
        
        if not image_url:
            print(f"⚠️ P{current_page_num}の画像URLが取得できませんでした（画像なしで続行）")

    # さらに次のページがあれば、その画像をバックグラウンドで先行生成
    next_page_to_preload = current_page_num + 1
    if next_page_to_preload in session_data["story_pages"]:
        print(f"🖼️ P{next_page_to_preload}画像生成タスク開始: {session_id}")
        # ★ このターンの画像URL (image_url) を引数として渡すように修正
        background_tasks.add_task(
            generate_image_task, 
            session_id, 
            next_page_to_preload, 
            session_data["story_pages"][next_page_to_preload],
            image_url 
        )
        print(f"✅ P{next_page_to_preload}画像生成タスク登録完了")
    else:
        print(f"⚠️ P{next_page_to_preload}のページが見つかりません")

    # セッションが終了したらデータを削除（任意）
    if "おしまい" in text_result:
        print(f"🏁 ストーリー終了検出")
        # del SESSIONS[session_id] # すぐに消すと画像取得が間に合わない可能性があるので、実際には定期的なクリーンアップ処理が望ましい
        pass

    result = {
        "session_id": session_id,
        "text_result": text_result,
        "image_url": image_url
    }
    print(f"✅ レスポンス返却: session_id={session_id}, text_len={len(text_result)}")
    return result

@app.post("/agent/storytelling/generate-audio")
async def generate_audio(request: Request):
    """ストーリーテキストを音声に変換"""
    data = await request.json()
    text = data.get("text", "")
    language = data.get("language", "ja")
    
    if not text:
        raise HTTPException(status_code=400, detail="Text is required")
    
    print(f"🎤 音声生成リクエスト: {text[:50]}...")
    
    try:
        from agents.StoryTelling_Agent.tts_tool import generate_story_audio
        result = generate_story_audio(text, language)
        
        if result and result.get("success"):
            audio_url = result["audio"]["cloud_url"]
            return {
                "success": True,
                "audio_url": audio_url,
                "message": "音声生成完了"
            }
        else:
            raise HTTPException(status_code=500, detail="Audio generation failed")
            
    except Exception as e:
        print(f"❌ 音声生成エラー: {e}")
        raise HTTPException(status_code=500, detail=f"Audio generation error: {str(e)}")

@app.get("/agent/storytelling/image-status/{session_id}")
async def get_image_status(session_id: str):
    """指定されたセッションの画像生成状況を取得"""
    if session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session_data = SESSIONS[session_id]
    current_page = session_data["current_page"]
    image_urls = session_data["image_urls"]
    
    # 次のページの画像URLが存在するかチェック
    next_page = current_page + 1
    has_next_image = next_page in image_urls and image_urls[next_page] is not None
    
    return {
        "session_id": session_id,
        "current_page": current_page,
        "next_page": next_page,
        "has_next_image": has_next_image,
        "image_urls": image_urls
    }



@app.get("/info")
def info():
    return {
        "message": "Welcome to GeminiReport API.",
        "usage": "GET or POST /agent/{agent_name} with input (optional), or POST /agent/{agent_name} with JSON: {'input': 'your question'} (input is optional)",
        "available_agents": list(AGENT_MAP.keys()),
        "endpoints": {
            "/": "ADK標準UI（ブラウザでアクセス）",
            "/src/story_top.html": "読み聞かせ選択ページ（カスタムUI）",
            "/src/story_agent.html": "読み聞かせ実行ページ（カスタムUI）",
            "/src/index.html": "メインページ",
            "/agent/child_care": "Child Care Agent（子供見守りアプリ）",
            "/agent/storytelling": "Storytelling Agent（インタラクティブ読み聞かせ）"
        },
        "note": "inputパラメータを省略すると、自動的に「こんにちは」でエージェントが開始されます。"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000))) 