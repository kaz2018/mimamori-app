# Google認証設定ガイド

## 1. Google Cloud Projectの設定

### 1.1 Google Cloud Consoleでプロジェクトを作成
1. [Google Cloud Console](https://console.cloud.google.com/)にアクセス
2. 新しいプロジェクトを作成または既存のプロジェクトを選択

### 1.2 Google Slides APIを有効化
1. Google Cloud Consoleで「APIとサービス」→「ライブラリ」に移動
2. 「Google Slides API」を検索して有効化

### 1.3 サービスアカウントの作成
1. 「APIとサービス」→「認証情報」に移動
2. 「認証情報を作成」→「サービスアカウント」を選択
3. サービスアカウント名を入力（例：`slide-creator-service`）
4. 「キーを作成」→「JSON」を選択
5. ダウンロードされたJSONファイルを`credentials.json`として保存

## 2. OAuth認証情報の設定

### 2.1 OAuth認証情報作成スクリプト

プロジェクトには複数のOAuth認証情報作成スクリプトが用意されています：

#### 2.1.1 ローカル開発用認証情報作成
```bash
# 既存のWeb認証情報からローカル用を作成
python create_local_oauth_credentials.py
```

**機能**:
- `oauth_credentials_web.json`を基にローカル用認証情報を作成
- ローカル開発用のリダイレクトURIを自動追加
- `local_env_oauth.sh`環境変数設定ファイルを作成

#### 2.1.2 新しい認証情報作成
```bash
# 完全に新しいOAuth認証情報を作成
python create_new_oauth_credentials.py
```

**機能**:
- ユーザーからClient IDとClient Secretを入力
- 新しい認証情報ファイル`oauth_credentials_new.json`を作成
- `setup_new_oauth.sh`環境変数設定ファイルを作成

### 2.2 環境変数設定スクリプト

#### 2.2.1 元の認証情報を使用
```bash
# 元の認証情報を使用する設定
source restore_original_auth.sh
```

#### 2.2.2 デスクトップ用認証情報を使用
```bash
# デスクトップ用認証情報を使用する設定
source setup_desktop_oauth.sh
```

#### 2.2.3 ローカル環境用OAuth設定
```bash
# ローカル環境用OAuth設定
source local_env_oauth.sh
```

### 2.3 OAuth認証情報の種類

| 認証情報ファイル | 用途 | 設定スクリプト |
|----------------|------|---------------|
| `oauth_credentials_desktop.json` | デスクトップアプリケーション用 | `restore_original_auth.sh` |
| `oauth_credentials_web.json` | Webアプリケーション用 | `local_env_oauth.sh` |
| `oauth_credentials_new.json` | 新規作成用 | `setup_new_oauth.sh` |

## 3. 環境変数の設定

### 3.1 .envファイルの作成
```bash
# .envファイルを作成
touch .env
```

### 3.2 環境変数の追加
```env
# Google認証設定
GOOGLE_APPLICATION_CREDENTIALS=./credentials.json
GOOGLE_CLOUD_PROJECT=your-project-id

# Google Slides API設定
GOOGLE_SLIDES_SCOPES=https://www.googleapis.com/auth/presentations

# OAuth認証設定
GOOGLE_OAUTH_CREDENTIALS=./oauth_credentials_desktop.json
OAUTH_REDIRECT_URI=http://localhost:8000/oauth2callback
```

## 4. 認証ファイルの配置

### 4.1 credentials.jsonの配置
```bash
# プロジェクトルートにcredentials.jsonを配置
mv ~/Downloads/your-project-credentials.json ./credentials.json
```

### 4.2 OAuth認証情報ファイルの配置
```bash
# OAuth認証情報ファイルを配置
# デスクトップ用
mv ~/Downloads/oauth_credentials_desktop.json ./

# Web用（Cloud Runデプロイメント用）
mv ~/Downloads/oauth_credentials_web.json ./
```

### 4.3 .gitignoreの更新
```gitignore
# 認証情報をGitに含めない
credentials.json
oauth_credentials_*.json
.env
*.pickle
```

## 5. 権限の設定

### 5.1 Google Drive APIの有効化
1. Google Cloud Consoleで「Google Drive API」も有効化
2. サービスアカウントに適切な権限を付与

### 5.2 OAuth同意画面の設定
1. Google Cloud Consoleで「OAuth同意画面」を設定
2. テストユーザーを追加（開発環境の場合）
3. 必要なスコープを有効化：
   - `https://www.googleapis.com/auth/presentations`
   - `https://www.googleapis.com/auth/drive.file`
   - `https://www.googleapis.com/auth/drive`

### 5.3 リダイレクトURIの設定
以下のリダイレクトURIをOAuth認証情報に追加：

**ローカル開発用**:
- `http://localhost:8000/oauth2callback`
- `http://localhost:8080/oauth2callback`

**Cloud Run用**:
- `https://gemini-report-ggl-research.run.app/oauth2callback`

## 6. 動作確認

### 6.1 認証テスト
```python
from google.oauth2 import service_account
from googleapiclient.discovery import build

# 認証情報の読み込み
credentials = service_account.Credentials.from_service_account_file(
    'credentials.json',
    scopes=['https://www.googleapis.com/auth/presentations']
)

# Google Slides APIクライアントの作成
slides_service = build('slides', 'v1', credentials=credentials)
print("認証成功！")
```

### 6.2 OAuth認証テスト
```bash
# 元の認証情報でテスト
source restore_original_auth.sh
python -c "from agents.Slide_Creator.auth_helper import get_google_slides_service; print('認証テスト:', get_google_slides_service())"
```

## 7. トラブルシューティング

### 7.1 よくあるエラー
- **403 Forbidden**: APIが有効化されていない、または権限不足
- **401 Unauthorized**: 認証情報が正しくない
- **404 Not Found**: プロジェクトIDが間違っている
- **redirect_uri_mismatch**: OAuthリダイレクトURIが正しく設定されていない

### 7.2 解決方法
1. Google Cloud ConsoleでAPIが有効化されているか確認
2. サービスアカウントの権限を確認
3. 環境変数が正しく設定されているか確認
4. credentials.jsonファイルが正しい場所にあるか確認
5. OAuth同意画面でテストユーザーが追加されているか確認
6. リダイレクトURIが正確に設定されているか確認

### 7.3 OAuth認証情報の使い分け

| 用途 | 認証情報ファイル | 設定スクリプト | 説明 |
|------|----------------|---------------|------|
| ローカル開発 | `oauth_credentials_desktop.json` | `restore_original_auth.sh` | 安定版、推奨 |
| Webアプリケーション | `oauth_credentials_web.json` | `local_env_oauth.sh` | Cloud Run用 |
| 新規作成 | `oauth_credentials_new.json` | `setup_new_oauth.sh` | 手動設定用 | 