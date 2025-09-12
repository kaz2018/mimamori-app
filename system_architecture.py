#!/usr/bin/env python3
"""
読み聞かせアプリ システムアーキテクチャー図
diagramsライブラリを使用してシステム構成を可視化
"""

from diagrams import Diagram, Cluster, Edge
from diagrams import Node
from diagrams.gcp.compute import Run
from diagrams.gcp.storage import GCS
from diagrams.gcp.devtools import Build
from diagrams.gcp.network import LoadBalancing
from diagrams.onprem.client import Users, User
from diagrams.onprem.network import Internet
from diagrams.programming.language import Python, JavaScript
from diagrams.programming.framework import FastAPI
from diagrams.generic.storage import Storage

# システムアーキテクチャー図の作成
with Diagram("読み聞かせアプリ システムアーキテクチャー", 
             filename="system_architecture", 
             show=False, 
             direction="TB",
             graph_attr={"fontsize": "20", "bgcolor": "white"}):
    
    # ユーザー層
    with Cluster("ユーザー層"):
        users = Users("ユーザー\n(保護者・子供)")
        mobile = User("モバイル端末")
        desktop = User("デスクトップ")
    
    # フロントエンド層
    with Cluster("フロントエンド層"):
        with Cluster("Webアプリケーション"):
            html = Python("HTML5")
            css = Python("CSS3")
            js = JavaScript("JavaScript\n(ES6+)")
            web_ui = FastAPI("Web UI\n(story_top.html,\nstory_agent.html)")
        
        with Cluster("ブラウザ機能"):
            speech_api = Python("Speech Synthesis API")
            audio_api = Python("Audio API")
            storage_api = Python("localStorage")
    
    # ネットワーク層
    with Cluster("ネットワーク層"):
        internet = Internet("インターネット")
        cdn = Node("CDN\n(静的ファイル配信)", icon_path="")
        lb = LoadBalancing("ロードバランサー")
    
    # バックエンド層
    with Cluster("バックエンド層"):
        with Cluster("Cloud Run"):
            fastapi_app = FastAPI("FastAPI\n(main.py)")
            uvicorn = Python("Uvicorn\n(ASGI Server)")
        
        with Cluster("認証・セキュリティ"):
            auth_init = Python("auth_init.py\n(認証初期化)")
            service_account = Node("Service Account", icon_path="")
            oauth = Node("OAuth 2.0", icon_path="")
    
    # AI/ML層
    with Cluster("AI/ML層"):
        with Cluster("Google Gemini"):
            gemini_flash = Node("Gemini 2.5 Flash\n(物語生成)", icon_path="")
            gemini_image = Node("Gemini 2.5 Flash Image\n(画像生成)", icon_path="")
        
        with Cluster("音声合成"):
            gtts = Python("Google gTTS\n(Text-to-Speech)")
            speech_synthesis = Python("Browser Speech\nSynthesis")
    
    # エージェント層
    with Cluster("エージェント層"):
        with Cluster("Google ADK"):
            adk_runner = Python("InMemoryRunner")
            parallel_tool = Python("simple_parallel_tool.py\n(並行画像生成)")
            tts_tool = Python("tts_tool.py\n(音声生成)")
        
        with Cluster("エージェント"):
            storytelling_agent = Python("StoryTelling_Agent\n(物語生成エージェント)")
            child_care_agent = Python("Child_Care_Agent\n(子供見守りエージェント)")
    
    # ストレージ層
    with Cluster("ストレージ層"):
        with Cluster("Google Cloud Storage"):
            story_images = GCS("story-images/\n(生成画像)")
            story_audio = GCS("story-audio/\n(生成音声)")
            reference_images = GCS("reference-images/\n(参照画像)")
        
        with Cluster("ローカルストレージ"):
            session_storage = Storage("セッション管理\n(SESSIONS)")
            temp_files = Storage("一時ファイル")
    
    # 監視・ログ層
    with Cluster("監視・ログ層"):
        cloudwatch = Node("CloudWatch\n(ログ・メトリクス)", icon_path="")
        logging = Python("Python Logging")
        health_check = Python("Health Check\n(/health/static-files)")
    
    # デプロイメント層
    with Cluster("デプロイメント層"):
        with Cluster("Google Cloud Build"):
            docker_build = Build("Docker Build")
            container_registry = Node("Container Registry", icon_path="")
        
        with Cluster("CI/CD"):
            deploy_script = Python("deploy_to_cloud_run.sh")
            cloud_run_deploy = Run("Cloud Run Deploy")
    
    # データフロー
    users >> internet
    mobile >> internet
    desktop >> internet
    
    internet >> cdn
    cdn >> lb
    lb >> fastapi_app
    
    fastapi_app >> uvicorn
    uvicorn >> auth_init
    auth_init >> service_account
    auth_init >> oauth
    
    fastapi_app >> adk_runner
    adk_runner >> storytelling_agent
    adk_runner >> child_care_agent
    
    storytelling_agent >> gemini_flash
    storytelling_agent >> gemini_image
    storytelling_agent >> parallel_tool
    storytelling_agent >> tts_tool
    
    parallel_tool >> story_images
    parallel_tool >> reference_images
    tts_tool >> story_audio
    tts_tool >> gtts
    
    web_ui >> speech_api
    web_ui >> audio_api
    web_ui >> storage_api
    
    fastapi_app >> session_storage
    fastapi_app >> temp_files
    
    fastapi_app >> cloudwatch
    fastapi_app >> logging
    fastapi_app >> health_check
    
    docker_build >> container_registry
    container_registry >> cloud_run_deploy
    deploy_script >> cloud_run_deploy
    
    # 静的ファイル配信
    cdn >> html
    cdn >> css
    cdn >> js
    cdn >> web_ui

# データフロー図の作成
with Diagram("読み聞かせアプリ データフロー\n(Gemini ADK マルチエージェント構成)", 
             filename="data_flow", 
             show=False, 
             direction="LR",
             graph_attr={"fontsize": "14", "bgcolor": "white"}):
    
    # ユーザー操作（左側配置）
    user = Users("ユーザー\n(保護者・子供)")
    
    # フロントエンド処理
    frontend = FastAPI("フロントエンド\n(HTML/CSS/JS)")
    
    # バックエンド処理
    backend = FastAPI("バックエンド\n(FastAPI)")
    
    # Gemini ADK マルチエージェント層
    with Cluster("Gemini ADK\nマルチエージェント", graph_attr={"style": "rounded,filled", "fillcolor": "white", "margin": "20,20", "label": "Gemini ADK\nマルチエージェント", "image": "https://raw.githubusercontent.com/google/generative-ai-docs/main/site/en/static/images/gemini-logo.png", "imagepos": "tc", "imagescale": "true"}):
        adk_runner = Python("InMemoryRunner\n(ADK実行エンジン)")
        
        with Cluster("エージェント"):
            storytelling_agent = Python("StoryTelling_Agent\n(物語生成)")
        
        with Cluster("並行処理ツール"):
            parallel_tool = Python("simple_parallel_tool.py\n(並行画像生成)")
            tts_tool = Python("tts_tool.py\n(音声生成)")
    
    # AI処理（VertexAIアイコン付き）
    with Cluster("VertexAI", graph_attr={"style": "rounded,filled", "fillcolor": "white", "margin": "40,40", "label": "VertexAI", "height": "3.0", "width": "2.5"}):
        # 上部に余白を作るためのダミーノード
        dummy_top = Node("", style="invis", height="0.5")
        
        story_generation = Node("Gemini 2.5 Flash\n(物語生成)", icon_path="https://raw.githubusercontent.com/mingrammer/diagrams/master/resources/gcp/ai/vertex-ai.png", height="0.8", width="1.2")
        image_generation = Node("Gemini 2.5 Flash\nImage\n(画像生成)", icon_path="https://raw.githubusercontent.com/mingrammer/diagrams/master/resources/gcp/ai/vertex-ai.png", height="0.8", width="1.2")
        audio_generation = Node("Google gTTS\n(音声生成)", icon_path="https://raw.githubusercontent.com/mingrammer/diagrams/master/resources/gcp/ai/vertex-ai.png", height="0.8", width="1.2")
        
        # 下部に余白を作るためのダミーノード
        dummy_bottom = Node("", style="invis", height="0.5")
    
    # ストレージ
    storage = GCS("Cloud Storage\n(画像・音声保存)")
    
    # データフロー
    user >> frontend
    frontend >> backend
    backend >> adk_runner
    adk_runner >> storytelling_agent
    storytelling_agent >> parallel_tool
    storytelling_agent >> tts_tool
    storytelling_agent >> story_generation  # 物語生成への直接接続
    parallel_tool >> story_generation
    parallel_tool >> image_generation
    tts_tool >> audio_generation
    story_generation >> storage
    image_generation >> storage
    audio_generation >> storage
    storage >> adk_runner
    adk_runner >> backend
    backend >> frontend
    frontend >> user
    
    # ダミーノードの配置（余白確保）
    dummy_top >> story_generation
    audio_generation >> dummy_bottom

# 技術スタック図の作成
with Diagram("読み聞かせアプリ 技術スタック", 
             filename="tech_stack", 
             show=False, 
             direction="TB",
             graph_attr={"fontsize": "14", "bgcolor": "white"}):
    
    with Cluster("フロントエンド"):
        html5 = Python("HTML5")
        css3 = Python("CSS3")
        js = JavaScript("JavaScript ES6+")
        web_apis = Python("Web APIs\n(Speech, Audio, Storage)")
    
    with Cluster("バックエンド"):
        fastapi = FastAPI("FastAPI")
        uvicorn = Python("Uvicorn")
        python = Python("Python 3.13")
    
    with Cluster("AI/ML"):
        gemini = Node("Google Gemini 2.5 Flash", icon_path="")
        gtts = Python("Google gTTS")
        adk = Python("Google ADK")
    
    with Cluster("クラウド"):
        cloud_run = Run("Google Cloud Run")
        cloud_storage = GCS("Google Cloud Storage")
        cloud_build = Build("Google Cloud Build")
    
    with Cluster("開発・運用"):
        docker = Python("Docker")
        yaml = Python("YAML")
        shell = Python("Shell Scripts")
    
    # 技術スタックの関係
    html5 >> fastapi
    css3 >> fastapi
    js >> fastapi
    web_apis >> fastapi
    
    fastapi >> uvicorn
    uvicorn >> python
    
    python >> gemini
    python >> gtts
    python >> adk
    
    fastapi >> cloud_run
    gemini >> cloud_storage
    gtts >> cloud_storage
    
    docker >> cloud_build
    yaml >> cloud_build
    shell >> cloud_build

print("✅ システムアーキテクチャー図のコードを生成しました！")
print("📁 生成されるファイル:")
print("   - system_architecture.png")
print("   - data_flow.png") 
print("   - tech_stack.png")
print("")
print("🚀 実行方法:")
print("   python system_architecture.py")
print("")
print("📋 必要なライブラリ:")
print("   pip install diagrams")
