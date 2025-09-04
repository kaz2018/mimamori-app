# サービスアカウントJSONキー設定ガイド

## 概要
Cloud Run環境でサービスアカウント認証を使用するには、サービスアカウントのJSONキーファイルが必要です。

## 手順

### 1. Google Cloud Consoleでサービスアカウントキーを作成

#### 1.1 Google Cloud Consoleにアクセス
1. [Google Cloud Console](https://console.cloud.google.com/)にアクセス
2. プロジェクト `ggl-research` を選択

#### 1.2 サービスアカウントに移動
1. 左側メニューから「IAM と管理」→「サービスアカウント」を選択
2. サービスアカウント一覧が表示される

#### 1.3 既存のサービスアカウントを確認
- `slide-creator-service@ggl-research.iam.gserviceaccount.com` が存在するか確認
- 存在しない場合は新規作成

#### 1.4 キーを作成
1. サービスアカウント名をクリック
2. 「キー」タブを選択
3. 「キーを追加」→「新しいキーを作成」をクリック
4. 「JSON」を選択
5. 「作成」をクリック
6. JSONファイルが自動ダウンロードされる

### 2. JSONキーファイルの内容確認

#### 2.1 ダウンロードされたファイルの内容
```json
{
  "type": "service_account",
  "project_id": "ggl-research",
  "private_key_id": "...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "slide-creator-service@ggl-research.iam.gserviceaccount.com",
  "client_id": "...",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/slide-creator-service%40ggl-research.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}
```

### 3. Cloud Run環境変数の設定

#### 3.1 環境変数として設定
```bash
# Cloud Runサービスを更新
gcloud run services update your-service-name \
  --region us-central1 \
  --set-env-vars GOOGLE_APPLICATION_CREDENTIALS_JSON='{"type":"service_account","project_id":"ggl-research","private_key_id":"...","private_key":"-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n","client_email":"slide-creator-service@ggl-research.iam.gserviceaccount.com","client_id":"...","auth_uri":"https://accounts.google.com/o/oauth2/auth","token_uri":"https://oauth2.googleapis.com/token","auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs","client_x509_cert_url":"https://www.googleapis.com/robot/v1/metadata/x509/slide-creator-service%40ggl-research.iam.gserviceaccount.com","universe_domain":"googleapis.com"}'
```

#### 3.2 注意事項
- **セキュリティ**: JSONキーは機密情報です
- **環境変数**: 長い文字列なので適切にエスケープ
- **権限**: サービスアカウントに適切な権限を付与

### 4. 必要なAPIの有効化

#### 4.1 Google Cloud ConsoleでAPIを有効化
1. 「APIとサービス」→「ライブラリ」に移動
2. 以下のAPIを有効化:
   - Google Slides API
   - Google Drive API
   - Google Docs API

### 5. 権限の確認

#### 5.1 サービスアカウントの権限
- **Google Slides API**: プレゼンテーションの作成・編集
- **Google Drive API**: ファイルの移動・管理
- **Google Docs API**: ドキュメントの読み取り

#### 5.2 Google Drive共有設定
- フォルダをサービスアカウントと共有
- 権限: 「編集者」

### 6. テスト実行

#### 6.1 ローカルテスト
```bash
# 環境変数を設定してテスト
export GOOGLE_APPLICATION_CREDENTIALS_JSON='{"type":"service_account",...}'
python test_slides_tool.py
```

#### 6.2 Cloud Runテスト
```bash
# Cloud Runにデプロイしてテスト
gcloud run deploy your-service-name --source .
```

## トラブルシューティング

### よくあるエラー

#### 1. "Invalid credentials" エラー
**原因**: JSONキーが無効または破損
**解決策**: 新しいキーを作成

#### 2. "Permission denied" エラー
**原因**: サービスアカウントの権限不足
**解決策**: IAMで適切な権限を付与

#### 3. "API not enabled" エラー
**原因**: 必要なAPIが有効化されていない
**解決策**: Google Cloud ConsoleでAPIを有効化

### 確認事項

- [ ] サービスアカウントJSONキーが作成されている
- [ ] Cloud Run環境変数が正しく設定されている
- [ ] 必要なAPIが有効化されている
- [ ] Google Driveフォルダが共有されている
- [ ] サービスアカウントに適切な権限が付与されている

## セキュリティ注意事項

1. **JSONキーの管理**: 機密情報として適切に管理
2. **環境変数**: 本番環境では適切なシークレット管理を使用
3. **権限の最小化**: 必要最小限の権限のみ付与
4. **定期的な更新**: キーを定期的に更新 