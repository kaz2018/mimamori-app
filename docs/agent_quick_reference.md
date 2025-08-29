# エージェント開発クイックリファレンス

## 新規エージェント作成（5分で完了）

### 1. ディレクトリ作成
```bash
mkdir agents/My_New_Agent
cd agents/My_New_Agent
```

### 2. ファイル作成

#### `__init__.py`
```python
from .agent import root_agent
__all__ = ["root_agent"]
```

#### `agent.py`
```python
from google.adk.agents import LlmAgent, SequentialAgent

# エージェント定義
my_agent = LlmAgent(
    name="my_agent",
    model="gemini-2.5-flash",
    instruction="あなたの指示をここに記述"
)

# SequentialAgentで連結
root_agent = SequentialAgent(
    name="My_New_Agent",
    sub_agents=[my_agent]
)

__all__ = ["root_agent"]
```

### 3. テストと起動
```bash
# インポートテスト
python -c "from agents.My_New_Agent.agent import root_agent; print('OK')"

# サーバー再起動
pkill -f "adk_web_server.py"
source venv/bin/activate
source restore_original_auth.sh
python adk_web_server.py
```

## よく使うパターン

### シンプルな会話エージェント
```python
conversation_agent = LlmAgent(
    name="conversation_agent",
    model="gemini-2.5-flash",
    instruction="ユーザーと自然な日本語で会話してください。"
)

root_agent = SequentialAgent(
    name="Simple_Agent",
    sub_agents=[conversation_agent]
)
```

### ツール付きエージェント
```python
from google.adk.tools import google_search

tool_agent = LlmAgent(
    name="tool_agent",
    model="gemini-2.5-flash",
    instruction="ツールを使用してタスクを実行してください。",
    tools=[google_search]
)

root_agent = SequentialAgent(
    name="Tool_Agent",
    sub_agents=[tool_agent]
)
```

### 複数ステップエージェント
```python
step1 = LlmAgent(name="step1", model="gemini-2.5-flash", instruction="ステップ1")
step2 = LlmAgent(name="step2", model="gemini-2.5-flash", instruction="ステップ2")
step3 = LlmAgent(name="step3", model="gemini-2.5-flash", instruction="ステップ3")

root_agent = SequentialAgent(
    name="Multi_Step_Agent",
    sub_agents=[step1, step2, step3]
)
```

## トラブルシューティング

| 問題 | 解決策 |
|------|--------|
| YAMLエラー | YAML設定ファイルを削除、`root_agent`としてエクスポート |
| エージェントが表示されない | `__init__.py`の構造を確認 |
| インポートエラー | ファイル名とクラス名を確認 |
| ツールが動作しない | 認証設定を確認 |

## 重要なポイント

✅ **必ず使用する構造**
- `SequentialAgent`
- `root_agent`としてエクスポート
- `LlmAgent`をサブエージェントとして使用

❌ **避けるべき構造**
- 単一の`Agent`クラス
- YAML設定ファイル
- `from . import agent`

## 参考リンク

- [詳細ガイド](./agent_development_guide.md)
- [ADK公式ドキュメント](https://google.github.io/adk-docs/)
- [ADKサンプルリポジトリ](https://github.com/google/adk-samples.git) 