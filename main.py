from fastapi import FastAPI, Request, HTTPException, Query
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from agents.Child_Care_Agent import root_agent as child_care_agent
from agents.StoryTelling_Agent import root_agent as storytelling_agent
from google.adk.runners import InMemoryRunner
from google.genai.types import Part, UserContent
import os
import uvicorn
import yaml

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
            with open(os.path.join(adk_browser_path, "index.html"), "r", encoding="utf-8") as f:
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
                <p>Available agents: {', '.join(AGENT_MAP.keys())}</p>
            </body>
            </html>
            """)
            
except Exception as e:
    print(f"Warning: Could not load ADK standard UI: {e}")

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

@app.post("/agent/{agent_name}")
async def run_agent_post(agent_name: str, request: Request):
    data = await request.json()
    user_input = data.get("input", "こんにちは")  # inputが指定されていない場合は「こんにちは」をデフォルトとして使用
    agent = AGENT_MAP.get(agent_name)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # InMemoryRunnerを使用してエージェントを実行
    runner = RUNNER_MAP[agent_name]
    session = await runner.session_service.create_session(
        app_name=runner.app_name, user_id="web_user"
    )
    
    content = UserContent(parts=[Part(text=user_input)])
    
    # エージェントを実行して結果を取得
    result = ""
    print(f"Starting agent execution for {agent_name} with input: {user_input}")
    for event in runner.run(
        user_id=session.user_id, session_id=session.id, new_message=content
    ):
        print(f"Event received: {type(event)} - {hasattr(event, 'content')}")
        if hasattr(event, 'content') and hasattr(event.content, 'parts'):
            print(f"Event has {len(event.content.parts)} parts")
            for part in event.content.parts:
                print(f"Part type: {type(part)} - has text: {hasattr(part, 'text')}")
                if hasattr(part, 'text') and part.text is not None:
                    print(f"Adding text: {part.text[:100]}...")
                    result += part.text
    
    print(f"Final result length: {len(result)}")
    return {"result": result}

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