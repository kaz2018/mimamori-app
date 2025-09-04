# ADK (Agent Development Kit) 使い方ガイド

## 概要

ADKは、Googleが提供するエージェント開発キットです。このプロジェクトでは、ADKを使用してGoogle Slidesを作成するエージェントを構築しています。

## 基本的な使い方

### 1. ADK Web UIへのアクセス

```bash
# ローカル環境でADK Webサーバーを起動
./start_local_adk.sh
```

ブラウザで `http://localhost:8080` にアクセスすると、ADKのWeb UIが表示されます。

### 2. エージェントの選択

ADK Web UIの左上にあるドロップダウンメニューから「Slide_Creator」を選択します。

### 3. エージェントとの対話

画面下部のメッセージ入力欄に以下のような指示を入力します：

#### 基本的なスライド作成
```
「AI技術の最新動向について5枚のスライドを作成してください」
```

#### 具体的な内容の指定
```
「日本の文化について以下の内容でスライドを作成してください：
1. 伝統文化
2. 現代文化
3. 食文化
4. 観光地
5. まとめ」
```

#### シンプルな指示
```
「"Japan"と書かれたスライドを作成してください」
```

### 4. エージェントの動作

Slide_Creatorエージェントは以下の3つのステップで動作します：

1. **ドキュメント解析エージェント**: 入力された内容を解析し、スライド作成に必要な情報を抽出
2. **スライド構造設計エージェント**: 解析された情報をもとに、スライドの構造を設計
3. **Google Slides作成エージェント**: 設計された構造をもとに、実際のGoogle Slidesを作成

### 5. 結果の確認

エージェントが実行されると、以下の情報が表示されます：

- 作成されたプレゼンテーションのID
- Google SlidesのURL
- 各スライドの詳細情報

## トラブルシューティング

### よくあるエラーと解決方法

#### エラー1: "Fail to load 'Slide_Creator' module"
**原因**: エージェントの設定に問題がある
**解決方法**: 
- `python test_local_adk.py` を実行して環境を確認
- 必要なファイルが存在するか確認

#### エラー2: "Google Slides API認証エラー"
**原因**: OAuth2認証情報が正しく設定されていない
**解決方法**:
- `oauth_credentials_web.json` ファイルが存在するか確認
- Google Cloud ConsoleでWebアプリケーション用のOAuth2認証情報を作成

#### エラー3: "ツールが見つかりません"
**原因**: カスタムツールの設定に問題がある
**解決方法**:
- `agents/Slide_Creator/custom_slides_tool.py` ファイルが存在するか確認
- ツールの初期化パラメータが正しいか確認

### デバッグ方法

#### 1. ログの確認
ADK Web UIの左側にある「Trace」タブで、エージェントの実行ログを確認できます。

#### 2. 環境テストの実行
```bash
python test_local_adk.py
```

#### 3. 手動でのエージェントテスト
```python
from agents.Slide_Creator.agent import root_agent

# エージェントをテスト実行
result = root_agent.run("テストスライドを作成してください")
print(result)
```

## 高度な使い方

### カスタムツールの拡張

`agents/Slide_Creator/custom_slides_tool.py` を編集して、新しい機能を追加できます：

```python
def custom_function(self, **kwargs):
    """カスタム機能を追加"""
    # 新しい機能の実装
    pass
```

### エージェントの設定変更

`agents/Slide_Creator/agent.py` を編集して、エージェントの動作をカスタマイズできます：

```python
# モデルの変更
model="gemini-2.5-flash"  # 他のモデルに変更可能

# 指示の変更
instruction="""
新しい指示をここに記述
"""
```

## 参考リンク

- [ADK ドキュメント](https://developers.google.com/adk)
- [Google Slides API ドキュメント](https://developers.google.com/slides/api)
- [Google Cloud Console](https://console.cloud.google.com) 