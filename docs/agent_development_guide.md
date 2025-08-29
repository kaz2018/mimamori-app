# エージェント開発ガイド

## 概要
このガイドでは、ADK 1.7.0を使用して新しいエージェントを追加する手順を説明します。今回の実装で得られた重要なノウハウを含みます。

## 前提条件
- ADK 1.7.0がインストール済み
- Google Cloud認証が設定済み
- 仮想環境が有効化済み
- `.env`ファイルでAPIキーが設定済み

## 重要な技術的ノウハウ

### 1. カスタムツールの正しい実装

#### FunctionToolを使った実装（推奨）
```python
from google.adk.tools import FunctionTool

def send_email(to_email: str, subject: str, body: str) -> Dict[str, Any]:
    """メール送信関数"""
    # 実装...
    return {"success": True, "message": "送信成功"}

# FunctionToolでラップ
gmail_sender_tool = FunctionTool(func=send_email)
```

#### BaseToolを使った実装（上級者向け）
```python
from google.adk.tools import BaseTool

class GmailSenderTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="gmail_sender",
            description="Send emails using SMTP"
        )
    
    async def run_async(self, *, args: Dict[str, Any], tool_context) -> Dict[str, Any]:
        # 実装...
        return result
```

### 2. ツール競合問題の解決

**問題**: 複数のツールを同時に使用すると`Tool use with function calling is unsupported`エラーが発生

**解決策**:
1. **個別エージェント**: 各エージェントで1つのツールのみを使用
2. **SequentialAgent**: ツールを分離して連携
3. **手動ワークフロー**: エージェント間で手動でデータを渡す

## エージェント追加手順

### 1. エージェントディレクトリの作成

```bash
# agentsディレクトリに新しいエージェントフォルダを作成
mkdir agents/Your_Agent_Name
cd agents/Your_Agent_Name
```

### 2. 基本ファイル構造

以下のファイルを作成します：

#### `__init__.py`
```python
from .agent import root_agent
__all__ = ["root_agent"]
```

#### `agent.py`
```python
"""Your Agent Description."""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'common'))

from google.adk.agents import LlmAgent, SequentialAgent
# 必要に応じてツールをインポート
from google.adk.tools import google_search
from gmail_tool import gmail_sender_tool

# 単一エージェントの場合
root_agent = LlmAgent(
    name="Your_Agent_Name",
    model="gemini-2.5-flash",
    instruction="""
    エージェントの指示をここに記述
    """,
    tools=[your_tool]  # 必要に応じてツールを追加
)

# SequentialAgentの場合
# 1. 最初のエージェント
first_agent = LlmAgent(
    name="first_agent",
    model="gemini-2.5-flash",
    instruction="""
    エージェントの指示をここに記述
    """,
    tools=[tool1]  # 1つのツールのみ
)

# 2. 2番目のエージェント
second_agent = LlmAgent(
    name="second_agent",
    model="gemini-2.5-flash",
    instruction="""
    エージェントの指示をここに記述
    """,
    tools=[tool2]  # 1つのツールのみ
)

# SequentialAgentで直列に連結
root_agent = SequentialAgent(
    name="Your_Agent_Name",
    sub_agents=[first_agent, second_agent]
)

__all__ = ["root_agent"]
```

### 3. カスタムツールの作成（必要に応じて）

#### `agents/common/your_tool.py`
```python
from google.adk.tools import FunctionTool

def your_function(param1: str, param2: str) -> Dict[str, Any]:
    """カスタムツール関数"""
    # 実装
    return {"result": "success"}

# FunctionToolでラップ
your_tool = FunctionTool(func=your_function)
```

### 4. エージェントのテスト

```bash
# エージェントのインポートテスト
python -c "from agents.Your_Agent_Name.agent import root_agent; print('Import OK')"
```

### 5. ADK Web UIの再起動

```bash
# サーバーを停止
pkill -f "adk web" || true

# 環境を有効化
source venv/bin/activate

# サーバーを再起動
python adk_web_server.py
```

## トラブルシューティング

### よくある問題と解決策

#### 1. UNEXPECTED_TOOL_CALL エラー
**原因**: エージェントがツールを呼び出そうとしているが、実際には呼び出されていない

**解決策**:
- エージェントの指示をより明確にする
- ツールの登録を確認する
- FunctionToolを使用する

#### 2. ツール競合エラー
**原因**: 複数のツールを同時に使用

**解決策**:
- 各エージェントで1つのツールのみを使用
- SequentialAgentでツールを分離

#### 3. インポートエラー
**原因**: モジュールパスの問題

**解決策**:
```python
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'common'))
```

## ベストプラクティス

### 1. エージェント設計
- **単一責任**: 各エージェントは1つの機能に集中
- **明確な指示**: エージェントの指示は具体的で明確に
- **エラーハンドリング**: 適切なエラーメッセージを提供

### 2. ツール設計
- **FunctionTool**: シンプルな関数にはFunctionToolを使用
- **BaseTool**: 複雑なロジックにはBaseToolを使用
- **適切な説明**: ツールの説明は具体的で分かりやすく

### 3. テスト戦略
- **個別テスト**: 各エージェントを個別にテスト
- **統合テスト**: SequentialAgentで統合テスト
- **手動テスト**: 必要に応じて手動ワークフローも使用

## 実装例

### Auto_Workflowエージェント（完成版）
```python
"""Auto Workflow agent - 検索、要約、メール送信を自動実行"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'common'))

from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.tools import google_search
from gmail_tool import gmail_sender_tool

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
    instruction="Summarize the search results about Gemini AI"
)

# 3. メール送信エージェント
email_agent = LlmAgent(
    name="email_agent",
    model="gemini-2.5-flash",
    instruction="""
    Call the send_email tool with:
    - to_email: "user@example.com"
    - subject: "GeminiReportからの要約結果"
    - body: [the summary content]
    """,
    tools=[gmail_sender_tool]
)

# SequentialAgentで自動ワークフローを作成
root_agent = SequentialAgent(
    name="Auto_Workflow",
    sub_agents=[search_agent, summary_agent, email_agent]
)

__all__ = ["root_agent"]
```

## まとめ

このガイドで説明したノウハウを使用することで、ADKを使った実用的なAIエージェントシステムを構築できます。特に重要なのは：

1. **FunctionToolの正しい使用**
2. **ツール競合問題の回避**
3. **SequentialAgentの適切な設計**
4. **段階的なテストとデバッグ**

これらの原則に従うことで、安定したAIエージェントシステムを構築できます。 