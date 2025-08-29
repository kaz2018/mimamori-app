# GeminiReport 環境設定

## 概要

GeminiReportプロジェクトの開発環境と本番環境の設定について説明します。

## 開発環境

### 1. 仮想環境設定

#### 1.1 仮想環境の作成
```bash
# Python仮想環境を作成
python -m venv venv

# 仮想環境をアクティベート
source venv/bin/activate  # macOS/Linux
# または
venv\Scripts\activate     # Windows
```

#### 1.2 依存関係のインストール
```bash
# 必要なパッケージをインストール
pip install -r requirements.txt
```

### 2. 開発サーバー起動

#### 2.1 start_server.shの実行
開発環境では`start_server.sh`を実行してサーバーを起動します。

```bash
# 開発サーバー起動
./start_server.sh
```

#### 2.2 start_server.shの内容
```bash
#!/bin/bash
# start_server.sh

# 仮想環境をアクティベート
source venv/bin/activate

# ポートを解放（必要に応じて）
# sudo lsof -ti:8000 | xargs kill -9

# 開発サーバーを起動
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. 開発環境の設定

#### 3.1 環境変数設定
```bash
# .envファイルを作成
cp .env.example .env

# 環境変数を設定
export GOOGLE_APPLICATION_CREDENTIALS="path/to/credentials.json"
export GEMINI_API_KEY="your-gemini-api-key"
export BIGQUERY_DATASET="gemini_report_dev"
export BIGQUERY_PROJECT="ggl-research"
export PUBSUB_TOPIC="data-collection-events-dev"
export CLOUD_STORAGE_BUCKET="gemini-report-files-dev"
export SLACK_WEBHOOK_URL="your-slack-webhook-url"
```

#### 3.2 ローカル開発用設定
- **データベース**: BigQuery（開発用データセット）
- **ストレージ**: Cloud Storage（開発用バケット）
- **メッセージング**: Pub/Sub（開発用トピック）
- **AI API**: Gemini API（開発用キー）

## 本番環境

### 1. Cloud Run設定

#### 1.1 プロジェクト情報
- **Project ID**: `ggl-research`
- **Region**: `us-central1`
- **Service Name**: `gemini-report`

#### 1.2 Cloud Run設定
```yaml
# cloudrun.yaml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: gemini-report
  namespace: default
spec:
  template:
    metadata:
      annotations:
        autoscaling.knative.dev/minScale: "0"
        autoscaling.knative.dev/maxScale: "10"
    spec:
      containerConcurrency: 80
      timeoutSeconds: 300
      containers:
      - image: gcr.io/ggl-research/gemini-report:latest
        ports:
        - containerPort: 8080
        env:
        - name: GOOGLE_APPLICATION_CREDENTIALS
          value: "/app/credentials.json"
        - name: GEMINI_API_KEY
          valueFrom:
            secretKeyRef:
              name: gemini-api-key
              key: api-key
        - name: BIGQUERY_DATASET
          value: "gemini_report"
        - name: BIGQUERY_PROJECT
          value: "ggl-research"
        - name: PUBSUB_TOPIC
          value: "data-collection-events"
        - name: CLOUD_STORAGE_BUCKET
          value: "gemini-report-files"
        - name: SLACK_WEBHOOK_URL
          valueFrom:
            secretKeyRef:
              name: slack-webhook
              key: url
        resources:
          limits:
            cpu: "2"
            memory: "4Gi"
          requests:
            cpu: "1"
            memory: "2Gi"
```

### 2. デプロイ手順

#### 2.1 事前準備
```bash
# 現在のプロジェクトを指定する
gcloud auth application-default set-quota-project ggl-research
# gcloud認証
gcloud auth login
gcloud auth configure-docker
# Google Cloud CLIの設定
gcloud config set project ggl-research
gcloud config set run/region us-central1

# 必要なAPIを有効化
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
#gcloud services enable bigquery.googleapis.com
#gcloud services enable pubsub.googleapis.com
#gcloud services enable storage.googleapis.com
#gcloud services enable aiplatform.googleapis.com
```

#### 2.2 Dockerイメージのビルド
```bash
# Dockerfileからイメージをビルド
#docker buildx build --platform linux/amd64 -t gcr.io/ggl-research/gemini-report:latest .

# イメージをGoogle Container Registryにプッシュ
#docker push gcr.io/ggl-research/gemini-report:latest

# こっちなら一回でいいらしい
gcloud builds submit --tag gcr.io/ggl-research/gemini-report:latest
```

#### 2.3 Cloud Runへのデプロイ
```bash
# Cloud Runサービスをデプロイ
#gcloud run deploy gemini-report \
#  --image gcr.io/ggl-research/gemini-report:latest \
#  --platform managed \
#  --region us-central1 \
#  --allow-unauthenticated \
#  --memory 4Gi \
#  --cpu 2 \
#  --max-instances 10 \
#  --min-instances 0 \
#  --timeout 300 \
#  --set-env-vars GEMINI_API_KEY=your-gemini-api-key

export $(cat .env | grep GEMINI_API_KEY | xargs)
gcloud run deploy gemini-report \
  --image gcr.io/ggl-research/gemini-report:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GEMINI_API_KEY=$GEMINI_API_KEY
```

#### 2.4 シークレットの設定
```bash
# Gemini APIキーをシークレットとして保存
echo -n "your-gemini-api-key" | gcloud secrets create gemini-api-key --data-file=-

# Slack Webhook URLをシークレットとして保存
echo -n "your-slack-webhook-url" | gcloud secrets create slack-webhook --data-file=-

# Cloud Runサービスにシークレットをマウント
gcloud run services update gemini-report \
  --region us-central1 \
  --set-secrets GEMINI_API_KEY=gemini-api-key:latest,SLACK_WEBHOOK_URL=slack-webhook:latest
```

### 3. 本番環境の設定

#### 3.1 BigQuery設定
```sql
-- 本番用データセットを作成
CREATE DATASET `ggl-research.gemini_report`;

-- 必要なテーブルを作成
CREATE TABLE `ggl-research.gemini_report.updates_raw` (
  id STRING,
  service_name STRING,
  update_title STRING,
  update_content STRING,
  importance_level STRING,
  category STRING,
  created_at TIMESTAMP,
  raw_data JSON
) PARTITION BY DATE(created_at);

CREATE TABLE `ggl-research.gemini_report.updates_processed` (
  id STRING,
  service_name STRING,
  update_title STRING,
  update_content STRING,
  importance_level STRING,
  category STRING,
  ai_classified BOOLEAN,
  ai_confidence_score FLOAT64,
  created_at TIMESTAMP,
  processed_at TIMESTAMP
) PARTITION BY DATE(created_at);

CREATE TABLE `ggl-research.gemini_report.analysis_results` (
  id STRING,
  analysis_type STRING,
  analysis_data JSON,
  created_at TIMESTAMP
) PARTITION BY DATE(created_at);

CREATE TABLE `ggl-research.gemini_report.reports` (
  id STRING,
  report_type STRING,
  report_content STRING,
  report_url STRING,
  created_at TIMESTAMP
) PARTITION BY DATE(created_at);

CREATE TABLE `ggl-research.gemini_report.ai_insights` (
  id STRING,
  insight_type STRING,
  insight_content STRING,
  confidence_score FLOAT64,
  service_name STRING,
  created_at TIMESTAMP
) PARTITION BY DATE(created_at);
```

#### 3.2 Cloud Storage設定
```bash
# 本番用バケットを作成
gsutil mb -p ggl-research -c STANDARD -l us-central1 gs://gemini-report-files

# バケットのライフサイクル設定
gsutil lifecycle set lifecycle.json gs://gemini-report-files
```

#### 3.3 Pub/Sub設定
```bash
# 本番用トピックを作成
gcloud pubsub topics create data-collection-events

# サブスクリプションを作成（必要に応じて）
gcloud pubsub subscriptions create data-collection-subscription \
  --topic data-collection-events
```

### 4. 監視・ログ設定

#### 4.1 Cloud Monitoring
```bash
# アラートポリシーを作成
gcloud alpha monitoring policies create \
  --policy-from-file=monitoring-policy.yaml
```

#### 4.2 Cloud Logging
```bash
# ログシンクを設定
gcloud logging sinks create gemini-report-logs \
  bigquery.googleapis.com/projects/ggl-research/datasets/gemini_report_logs \
  --log-filter="resource.type=cloud_run_revision AND resource.labels.service_name=gemini-report"
```

### 5. CI/CD設定

#### 5.1 GitHub Actions設定
```yaml
# .github/workflows/deploy.yml
name: Deploy to Cloud Run

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    
    - name: Setup Google Cloud CLI
      uses: google-github-actions/setup-gcloud@v0
      with:
        project_id: ggl-research
        service_account_key: ${{ secrets.GCP_SA_KEY }}
    
    - name: Build and Push Docker Image
      run: |
        gcloud auth configure-docker
        docker build -t gcr.io/ggl-research/gemini-report:${{ github.sha }} .
        docker push gcr.io/ggl-research/gemini-report:${{ github.sha }}
    
    - name: Deploy to Cloud Run
      run: |
        gcloud run deploy gemini-report \
          --image gcr.io/ggl-research/gemini-report:${{ github.sha }} \
          --region us-central1 \
          --platform managed \
          --allow-unauthenticated
```

### 6. 環境変数一覧

#### 6.1 開発環境
```bash
# .env
GOOGLE_APPLICATION_CREDENTIALS=path/to/credentials.json
GEMINI_API_KEY=your-gemini-api-key
BIGQUERY_DATASET=gemini_report_dev
BIGQUERY_PROJECT=ggl-research
PUBSUB_TOPIC=data-collection-events-dev
CLOUD_STORAGE_BUCKET=gemini-report-files-dev
SLACK_WEBHOOK_URL=your-slack-webhook-url
VERTEX_AI_PROJECT=ggl-research
```

#### 6.2 本番環境
```bash
# Cloud Run環境変数
GOOGLE_APPLICATION_CREDENTIALS=/app/credentials.json
GEMINI_API_KEY=${GEMINI_API_KEY_SECRET}
BIGQUERY_DATASET=gemini_report
BIGQUERY_PROJECT=ggl-research
PUBSUB_TOPIC=data-collection-events
CLOUD_STORAGE_BUCKET=gemini-report-files
SLACK_WEBHOOK_URL=${SLACK_WEBHOOK_SECRET}
VERTEX_AI_PROJECT=ggl-research
```

### 7. トラブルシューティング

#### 7.1 よくある問題
- **認証エラー**: Service Accountの権限確認
- **BigQuery接続エラー**: データセット・テーブルの存在確認
- **Cloud Run起動エラー**: 環境変数・シークレットの設定確認
- **AI API制限**: クォータ・レート制限の確認

#### 7.2 ログ確認
```bash
# Cloud Runログの確認
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=gemini-report" --limit=50

# BigQueryログの確認
gcloud logging read "resource.type=bigquery_dataset" --limit=50
```

この環境設定に基づいて開発とデプロイを進めていきます。 