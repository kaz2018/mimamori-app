# Google Slides API 設定ガイド

## 概要

このドキュメントでは、GeminiReportプロジェクトでGoogle Slides APIを使用するための設定手順を説明します。

## 前提条件

- Google Cloud Project（ggl-research）が存在すること
- Google Cloud Consoleへのアクセス権限があること
- Python 3.8以上がインストールされていること

## 1. Google Cloud Consoleでの設定

### 1.1 必要なAPIの有効化

以下のAPIをGoogle Cloud Consoleで有効化してください：

1. **Google Slides API**
   - [Google Cloud Console](https://console.cloud.google.com/apis/library/slides.googleapis.com)にアクセス
   - プロジェクト「ggl-research」を選択
   - 「有効にする」をクリック

2. **Google Drive API**
   - [Google Cloud Console](https://console.cloud.google.com/apis/library/drive.googleapis.com)にアクセス
   - プロジェクト「ggl-research」を選択
   - 「有効にする」をクリック

### 1.2 OAuth2認証情報の作成

1. [Google Cloud Console](https://console.cloud.google.com/apis/credentials)にアクセス
2. プロジェクト「ggl-research」を選択
3. **「+ 認証情報を作成」**をクリック
4. **「OAuth 2.0 クライアントID」**を選択
5. **「同意画面を構成」**をクリック（初回の場合）
6. OAuth同意画面の設定：
   - アプリ名：「Slide Creator」
   - ユーザーサポートメール：`[your-email@example.com]`
   - 開発者の連絡先情報：`[your-email@example.com]`
   - スコープ：必要なスコープを追加
7. **「保存して続行」**をクリック
8. 再度**「+ 認証情報を作成」**→**「OAuth 2.0 クライアントID」**を選択
9. アプリケーションの種類で**「デスクトップアプリケーション」**を選択
10. 名前を「Slide Creator OAuth」に設定
11. **「作成」**をクリック
12. ダウンロードされたJSONファイルを`oauth_credentials.json`として保存

### 1.3 OAuth同意画面の設定

1. **「OAuth同意画面」**タブを選択
2. **「テスト」**タブを選択
3. **「テストユーザーを追加」**をクリック
4. **`[your-email@example.com]`**を追加
5. **「保存」**をクリック

## 2. ローカル環境の設定

### 2.1 必要なライブラリのインストール

```bash
pip install google-auth-oauthlib
```

### 2.2 認証情報ファイルの配置

1. ダウンロードした`oauth_credentials.json`をプロジェクトルートに配置
2. ファイル名を確認：`oauth_credentials.json`

### 2.3 環境変数の設定（オプション）

```bash
export GOOGLE_OAUTH_CREDENTIALS=./oauth_credentials.json
export GOOGLE_CLOUD_PROJECT=ggl-research
export GOOGLE_DRIVE_FOLDER_ID=133if6XjFG073nG0HuW4npL0JwsksELwv
```

### 2.4 設定ファイルの作成

プロジェクトルートに`.env`ファイルを作成して設定を管理：

```bash
# .env ファイル
GOOGLE_OAUTH_CREDENTIALS=./oauth_credentials.json
GOOGLE_CLOUD_PROJECT=ggl-research
GOOGLE_DRIVE_FOLDER_ID=133if6XjFG073nG0HuW4npL0JwsksELwv
```

**注意**: `.env`ファイルは機密情報を含むため、`.gitignore`に追加してください。

## 3. Google Driveフォルダの設定

### 3.1 フォルダの作成

1. [Google Drive](https://drive.google.com)にアクセス
2. **「新規」**→**「フォルダ」**をクリック
3. フォルダ名を「Slide Creator Output」に設定
4. フォルダIDを取得する手順：
   - 作成したフォルダを右クリック
   - **「共有」**を選択
   - **「リンクをコピー」**をクリック
   - コピーされたURLからフォルダIDを抽出
   - URL形式：`https://drive.google.com/drive/folders/[フォルダID]`
   - 例：`https://drive.google.com/drive/folders/133if6XjFG073nG0HuW4npL0JwsksELww`
   - フォルダID：`133if6XjFG073nG0HuW4npL0JwsksELww`
5. フォルダIDをメモ（例：`133if6XjFG073nG0HuW4npL0JwsksELww`）

### 3.2 フォルダの共有設定

1. 作成したフォルダを右クリック
2. **「共有」**を選択
3. **「ユーザーやグループを追加」**をクリック
4. **`[your-email@example.com]`**を追加
5. 権限を**「編集者」**に設定
6. **「送信」**をクリック

## 4. 認証のテスト

### 4.1 テストスクリプトの実行

```bash
python test_google_auth.py
```

### 4.2 初回認証時の手順

1. ブラウザが自動で開く
2. Googleアカウントでログイン（`[your-email@example.com]`）
3. 権限を許可：
   - Google Slidesへのアクセス
   - Google Driveへのアクセス
4. 認証が完了すると自動的にリダイレクトされる

### 4.3 期待される出力

```
=== Google認証設定テスト ===

=== Google認証設定チェック ===
✓ 認証情報ファイル: ./oauth_credentials.json
✓ Google Cloud Project ID: ggl-research
Google Slides API認証成功！（OAuth2認証）
✓ Google Slides API接続成功

✓ 認証設定が完了しています

サンプルプレゼンテーションを作成してテストします...
create_sample_presentation関数が呼ばれました
タイトル: GeminiReport テスト
フォルダID: 133if6XjFG073nG0HuW4npL0JwsksELwv
Google Slides APIサービスを取得中...
Google Slides API認証成功！（OAuth2認証）
プレゼンテーションを作成中...
フォルダIDが指定されました: 133if6XjFG073nG0HuW4npL0JwsksELwv
Google Slides API認証成功！（OAuth2認証）
フォルダ情報を取得中...
アクセス先フォルダ: Slide Creator Output (ID: 133if6XjFG073nG0HuW4npL0JwsksELwv)
フォルダURL: https://drive.google.com/drive/folders/133if6XjFG073nG0HuW4npL0JwsksELwv
プレゼンテーションをフォルダに移動中...
プレゼンテーションをフォルダ 'Slide Creator Output' に移動しました
サンプルプレゼンテーション作成成功: [プレゼンテーションID]
URL: https://docs.google.com/presentation/d/[プレゼンテーションID]

=== テスト完了 ===
✓ Google Slides APIが正常に動作しています
✓ Slide Creatorエージェントが使用可能です
```

## 5. トラブルシューティング

### 5.1 よくあるエラーと解決方法

#### エラー1: "The caller does not have permission"
**原因**: APIが有効化されていない、または権限が不足
**解決方法**: 
- Google Slides APIとGoogle Drive APIが有効化されているか確認
- OAuth同意画面の設定を確認

#### エラー2: "Slide-Creator は Google の審査プロセスを完了していません"
**原因**: OAuth同意画面でテストユーザーが設定されていない
**解決方法**:
- OAuth同意画面の「テスト」タブで`[your-email@example.com]`をテストユーザーとして追加

#### エラー3: "'Resource' object has no attribute '_credentials'"
**原因**: OAuth2認証での認証情報取得方法の問題
**解決方法**:
- `agents/Slide_Creator/auth_helper.py`の認証情報取得部分を修正

#### エラー4: "No access token in response"
**原因**: サービスアカウント認証の問題
**解決方法**:
- OAuth2認証に切り替える

### 5.2 認証情報の再生成

認証情報に問題がある場合：

1. `token.pickle`ファイルを削除
2. 再度`python test_google_auth.py`を実行
3. ブラウザで認証を再実行

## 6. 設定ファイルの説明

### 6.1 oauth_credentials.json
OAuth2認証情報ファイル。Google Cloud Consoleからダウンロード。

### 6.2 token.pickle
認証トークンのキャッシュファイル。自動生成される。

### 6.3 .env
環境変数設定ファイル。Google DriveフォルダIDなどの設定を含む。

### 6.4 agents/Slide_Creator/auth_helper.py
認証処理を行うPythonモジュール。

## 7. セキュリティに関する注意事項

- `oauth_credentials.json`は機密情報を含むため、Gitにコミットしない
- `.env`ファイルも機密情報を含むため、Gitにコミットしない
- `.gitignore`に以下を追加：
  ```
  oauth_credentials.json
  token.pickle
  credentials.json
  .env
  ```

## 8. 次のステップ

認証設定が完了したら、Slide Creatorエージェントを使用してスライド作成をテストできます：

```python
from agents.Slide_Creator import root_agent

# エージェントの使用例
result = root_agent.run("サンプルドキュメントからスライドを作成してください")
```

## 参考リンク

- [Google Slides API ドキュメント](https://developers.google.com/slides/api)
- [Google Drive API ドキュメント](https://developers.google.com/drive/api)
- [Google Cloud Console](https://console.cloud.google.com)
- [OAuth 2.0 スコープ](https://developers.google.com/identity/protocols/oauth2/scopes) 