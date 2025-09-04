# Cloud Run デプロイメントガイド

## 概要

このドキュメントでは、GeminiReportプロジェクトをGoogle Cloud Runで公開し、他の人に使わせるための設定手順を説明します。

## 前提条件

- Google Cloud Project（ggl-research）が存在すること
- Google Cloud Consoleへのアクセス権限があること
- Google Cloud CLI（gcloud）がインストールされていること

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

### 1.2 OAuth2認証情報の作成（Webアプリケーション用）

1. [Google Cloud Console](https://console.cloud.google.com/apis/credentials)にアクセス
2. プロジェクト「ggl-research」を選択
3. **「+ 認証情報を作成」**をクリック
4. **「OAuth 2.0 クライアントID」**を選択
5. **「同意画面を構成」**をクリック（初回の場合）
6. OAuth同意画面の設定：
   - アプリ名：「GeminiReport Slide Creator」
   - ユーザーサポートメール：`[your-email@example.com]`
   - 開発者の連絡先情報：`[your-email@example.com]`
   - スコープ：必要なスコープを追加
7. **「保存して続行」**をクリック
8. 再度**「+ 認証情報を作成」**→**「OAuth 2.0 クライアントID」**を選択
9. アプリケーションの種類で**「ウェブアプリケーション」**を選択
10. 名前を「GeminiReport Web OAuth」に設定
11. **承認済みのリダイレクトURI**に以下を追加：
    - `https://[YOUR-SERVICE-NAME]-[YOUR-PROJECT-ID].run.app/oauth2callback`
    - 例：`https://gemini-report-ggl-research.run.app/oauth2callback`
12. **「作成」**をクリック
13. ダウンロードされたJSONファイルを`oauth_credentials_web.json`として保存

### 1.3 OAuth同意画面の設定

1. **「OAuth同意画面」**タブを選択
2. **「本番環境」**タブを選択（または「テスト」タブでテストユーザーを追加）
3. 必要に応じて**「テストユーザーを追加」**をクリック
4. **`[your-email@example.com]`**を追加
5. **「保存」**をクリック

## 2. ローカル環境の準備

### 2.1 Google Cloud CLIの設定

```bash
# Google Cloud CLIでログイン
gcloud auth login

# プロジェクトを設定
gcloud config set project ggl-research

# 必要なAPIを有効化
gcloud services enable slides.googleapis.com
gcloud services enable drive.googleapis.com
```

### 2.2 認証情報ファイルの配置

1. ダウンロードした`oauth_credentials_web.json`をプロジェクトルートに配置
2. ファイル名を確認：`oauth_credentials_web.json`

## 3. Cloud Runデプロイメント

### 3.1 Dockerfileの修正

まず、DockerfileをCloud Run用に修正します：

```dockerfile
# Use the official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Expose the port
EXPOSE 8080

# Use uvicorn to run the FastAPI app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
```

### 3.2 環境変数の設定

Cloud Runサービス用の環境変数を設定します：

```bash
# 環境変数を設定
export GOOGLE_OAUTH_CREDENTIALS=./oauth_credentials_web.json
export OAUTH_REDIRECT_URI=https://gemini-report-ggl-research.run.app/oauth2callback
export SECRET_KEY=your-secret-key-here-change-this
export GOOGLE_CLOUD_PROJECT=ggl-research
export GOOGLE_DRIVE_FOLDER_ID=133if6XjFG073nG0HuW4npL0JwsksELwv
```

### 3.3 Dockerイメージのビルドとデプロイ

```bash
# Dockerイメージをビルド
docker build -t gcr.io/ggl-research/gemini-report .

# Google Container Registryにプッシュ
docker tag gcr.io/ggl-research/gemini-report gcr.io/ggl-research/gemini-report:latest
docker push gcr.io/ggl-research/gemini-report:latest

# Cloud Runにデプロイ
gcloud run deploy gemini-report \
  --image gcr.io/ggl-research/gemini-report:latest \
  --platform managed \
  --region asia-northeast1 \
  --allow-unauthenticated \
  --set-env-vars="GOOGLE_OAUTH_CREDENTIALS=./oauth_credentials_web.json" \
  --set-env-vars="OAUTH_REDIRECT_URI=https://gemini-report-ggl-research.run.app/oauth2callback" \
  --set-env-vars="SECRET_KEY=your-secret-key-here-change-this" \
  --set-env-vars="GOOGLE_CLOUD_PROJECT=ggl-research" \
  --set-env-vars="GOOGLE_DRIVE_FOLDER_ID=133if6XjFG073nG0HuW4npL0JwsksELwv"
```

### 3.4 認証情報ファイルのアップロード

Cloud Runサービスに認証情報ファイルをアップロードする必要があります：

```bash
# 認証情報ファイルをCloud Storageにアップロード
gsutil cp oauth_credentials_web.json gs://ggl-research-credentials/

# Cloud Runサービスに認証情報ファイルをマウント
gcloud run services update gemini-report \
  --region asia-northeast1 \
  --set-env-vars="GOOGLE_OAUTH_CREDENTIALS=gs://ggl-research-credentials/oauth_credentials_web.json"
```

## 4. セキュリティ設定

### 4.1 秘密鍵の生成

```bash
# 安全な秘密鍵を生成
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

生成された秘密鍵を`SECRET_KEY`環境変数に設定してください。

### 4.2 IAM権限の設定

Cloud Runサービスに必要な権限を付与：

```bash
# Cloud Runサービスアカウントに権限を付与
gcloud projects add-iam-policy-binding ggl-research \
  --member="serviceAccount:ggl-research@appspot.gserviceaccount.com" \
  --role="roles/slides.admin"

gcloud projects add-iam-policy-binding ggl-research \
  --member="serviceAccount:ggl-research@appspot.gserviceaccount.com" \
  --role="roles/drive.admin"
```

## 5. 動作確認

### 5.1 サービスの確認

```bash
# Cloud RunサービスのURLを取得
gcloud run services describe gemini-report --region=asia-northeast1 --format="value(status.url)"
```

### 5.2 ブラウザでの確認

1. 取得したURLにアクセス
2. 「Googleでログイン」ボタンをクリック
3. Googleアカウントで認証
4. スライド作成機能をテスト

## 6. トラブルシューティング

### 6.1 よくあるエラーと解決方法

#### エラー1: "redirect_uri_mismatch"
**原因**: OAuth2認証情報のリダイレクトURIが正しく設定されていない
**解決方法**: 
- Google Cloud ConsoleでOAuth2認証情報のリダイレクトURIを正しく設定
- Cloud RunサービスのURLと一致しているか確認

#### エラー2: "The caller does not have permission"
**原因**: Cloud Runサービスに必要な権限が不足
**解決方法**:
- IAM権限の設定を確認
- サービスアカウントに適切な権限を付与

#### エラー3: "File not found: oauth_credentials_web.json"
**原因**: 認証情報ファイルがCloud Runサービスに配置されていない
**解決方法**:
- 認証情報ファイルをCloud Storageにアップロード
- 環境変数で正しいパスを指定

### 6.2 ログの確認

```bash
# Cloud Runサービスのログを確認
gcloud logs read "resource.type=cloud_run_revision AND resource.labels.service_name=gemini-report" --limit=50
```

## 7. 本番環境での注意事項

### 7.1 スケーリング設定

```bash
# 自動スケーリングの設定
gcloud run services update gemini-report \
  --region asia-northeast1 \
  --min-instances=0 \
  --max-instances=10
```

### 7.2 監視とアラート

```bash
# Cloud Monitoringでアラートを設定
gcloud alpha monitoring policies create \
  --policy-from-file=monitoring-policy.yaml
```

### 7.3 コスト最適化

- 最小インスタンス数を0に設定
- 最大インスタンス数を適切に制限
- 使用量に応じてスケーリング設定を調整

## 8. 次のステップ

デプロイメントが完了したら、以下の作業を行ってください：

1. **ドメインの設定**: カスタムドメインを設定
2. **SSL証明書**: 自動的に設定されます
3. **CDN設定**: Cloud CDNを有効化
4. **監視設定**: Cloud Monitoringでアラートを設定
5. **バックアップ**: 定期的なバックアップを設定

## 参考リンク

- [Cloud Run ドキュメント](https://cloud.google.com/run/docs)
- [Google Slides API ドキュメント](https://developers.google.com/slides/api)
- [OAuth 2.0 設定](https://developers.google.com/identity/protocols/oauth2)
- [Cloud Run セキュリティ](https://cloud.google.com/run/docs/securing) 