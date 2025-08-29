# GeminiReport ドキュメント

このフォルダには、GeminiReportプロジェクトのドキュメントが格納されています。

## ファイル構成

- `complete_development_guide.md`: **完全開発ガイド**（今回のノウハウを反映）
- `requirements.md`: プロジェクト要件定義書
- `agent_development_guide.md`: エージェント開発ガイド
- `adk_usage_guide.md`: ADK使用ガイド
- `environment.md`: 環境設定ガイド
- `README.md`: このファイル

## プロジェクト概要

**GeminiReport**は、Google Workspace関連サービスのアップデート情報を自動収集し、構造化されたレポートを生成するマルチエージェントシステムです。

### 主要技術
- **Google Agent Development Kit (ADK)** - エージェント開発フレームワーク
- **Gemini API** - 主要AI機能
- **FunctionTool/BaseTool** - カスタムツール実装
- **SequentialAgent** - エージェント連携
- **SMTP** - メール送信機能

### 完成したエージェント構成
```
agents/
├── Auto_Workflow/          # メイン機能（検索→要約→メール送信の自動化）
├── Search_Agent/           # 検索専用
├── Default_Agent/          # 基本会話
├── Gemini_Update/          # バックアップ
├── Slide_Creator/          # スライド作成
├── test_slides_agent/      # スライド作成テスト
└── common/                 # 共通ツール
    └── gmail_tool.py       # Gmail送信ツール（FunctionTool実装）
```

## 重要な技術的ノウハウ

### 1. カスタムツールの正しい実装
- **FunctionTool**: シンプルな関数にはFunctionToolを使用
- **BaseTool**: 複雑なロジックにはBaseToolを使用
- **async run_async**: BaseToolの正しいメソッド実装

### 2. ツール競合問題の解決
- 各エージェントで1つのツールのみを使用
- SequentialAgentでツールを分離
- 手動ワークフローも活用

### 3. SequentialAgentの適切な設計
- 検索エージェント（google_searchのみ）
- 要約エージェント（ツールなし）
- メール送信エージェント（gmail_sender_toolのみ）

## 実装例

### Auto_Workflowエージェント（完成版）
```python
# 1. 検索エージェント
search_agent = LlmAgent(
    name="search_agent",
    model="gemini-2.5-flash",
    instruction="Search for 'Google Gemini AI' using google_search",
    tools=[google_search]
)

# 2. 要約エージェント
summary_agent = LlmAgent(
    name="summary_agent",
    model="gemini-2.5-flash",
    instruction="Summarize the search results"
)

# 3. メール送信エージェント
email_agent = LlmAgent(
    name="email_agent",
    model="gemini-2.5-flash",
    instruction="Call send_email tool with the summary",
    tools=[gmail_sender_tool]
)

# SequentialAgentで連結
root_agent = SequentialAgent(
    name="Auto_Workflow",
    sub_agents=[search_agent, summary_agent, email_agent]
)
```

## 環境設定

### 必要な環境変数
```bash
# .envファイル
GOOGLE_API_KEY=your_api_key_here
EMAIL_ADDRESS=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
```

### 依存関係
```bash
pip install google-adk
pip install python-dotenv
```

## 使用方法

### 1. ADK Webサーバー起動
```bash
python adk_web_server.py
```

### 2. ブラウザでアクセス
```
http://localhost:8000
```

### 3. エージェント選択
- **Auto_Workflow**: 検索→要約→メール送信の自動化
- **Search_Agent**: 検索専用
- **Default_Agent**: 基本会話

## トラブルシューティング

### よくある問題
1. **UNEXPECTED_TOOL_CALL**: エージェントの指示を明確にする
2. **ツール競合**: 各エージェントで1つのツールのみ使用
3. **インポートエラー**: モジュールパスを確認

詳細は `complete_development_guide.md` を参照してください。

## NotebookLM検索対象

このプロジェクトはNotebookLMの検索対象として設定されています。以下の内容が検索可能です：

### 検索対象ファイル
- `complete_development_guide.md`: 完全開発ガイド
- `requirements.md`: プロジェクト要件定義
- その他のMarkdownファイル
- コードファイル（Python、YAML、JSON等）

### 検索可能な内容
- プロジェクト概要
- 技術スタック（ADK、Gemini API、FunctionTool等）
- エージェント設計
- カスタムツール実装
- トラブルシューティング
- ベストプラクティス

詳細は `complete_development_guide.md` を参照してください。