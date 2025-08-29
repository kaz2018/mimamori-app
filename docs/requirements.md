# GeminiReport - Google Workspace アップデート収集・レポート作成システム

## 要件定義書

### 1. プロジェクト概要

**プロジェクト名**: GeminiReport - Google Workspace アップデート収集・レポート作成システム

**目的**: Gemini、Google Workspace、NotebookLM等のアップデート情報を自動収集し、構造化されたレポートを生成するマルチエージェントシステム

### 2. システム要件

#### 2.1 機能要件

**主要機能**:
- Google Workspace関連サービスのアップデート情報収集
- Gemini APIのアップデート情報収集
- NotebookLMのアップデート情報収集
- 収集した情報の構造化・分析
- 自動レポート生成
- 定期実行機能
- 通知機能

#### 2.2 非機能要件

- **可用性**: 24/7稼働
- **応答性**: レポート生成は5分以内
- **拡張性**: 新しい情報源の追加が容易
- **セキュリティ**: API認証情報の安全な管理
- **スケーラビリティ**: Cloud Runによる自動スケーリング

### 3. エージェント設計

#### 3.1 エージェント構成

1. **Data Collector Agent**
   - 責任: 各種ソースからのデータ収集
   - 対象: Google Workspace、Gemini、NotebookLM、その他関連サービス
   - AI機能: Gemini APIによるデータ検証・分類

2. **Data Processor Agent**
   - 責任: 収集データの前処理・構造化
   - 機能: 重複除去、データ正規化、重要度判定
   - AI機能: Gemini APIによる重要度判定・分類

3. **Analysis Agent**
   - 責任: データ分析・洞察生成
   - 機能: トレンド分析、影響度評価、優先度付け
   - AI機能: Gemini APIによる洞察生成、Vertex AIによる高度分析（必要時）

4. **Report Generator Agent**
   - 責任: レポート作成
   - 機能: テンプレート適用、可視化、フォーマット変換
   - AI機能: Gemini APIによるレポート生成、自然言語要約

5. **Notification Agent**
   - 責任: 通知管理
   - 機能: メール通知、Slack通知、Webhook送信
   - AI機能: Gemini APIによる通知内容の最適化

6. **Orchestrator Agent**
   - 責任: 全体のワークフロー制御
   - 機能: エージェント間調整、エラーハンドリング、スケジューリング
   - AI機能: Gemini APIによるワークフロー最適化

### 4. 技術スタック

#### 4.1 基盤技術
- **Google Agent Development Kit**: エージェント開発フレームワーク
- **Python**: メイン開発言語
- **FastAPI**: APIサーバー
- **Google Cloud Run**: コンテナ実行環境
- **Google Cloud BigQuery**: データウェアハウス・分析
- **Google Cloud Pub/Sub**: メッセージング・イベント駆動
- **Google Cloud Storage**: ファイル保存・レポート保存
- **Google Cloud Scheduler**: 定期実行

#### 4.2 AI・機械学習
- **Gemini API**: 主要AI機能（ADK標準統合）
  - データ分析・洞察生成
  - レポート自動生成
  - 自然言語処理
  - 重要度判定
- **Vertex AI**: 高度なAI機能（必要時）
  - カスタムモデル使用
  - バッチ処理での大量データ分析
  - より詳細な生成設定が必要な場合
- **Google Cloud Natural Language API**: テキスト分析
- **Google Cloud Vision API**: 画像分析（必要に応じて）

#### 4.3 外部API
- **Google Workspace Admin API**: Workspace情報取得
- **Gemini API**: AI機能利用
- **NotebookLM API**: NotebookLM情報取得（利用可能時）
- **Google Sheets API**: レポート出力

#### 4.4 データベース・ストレージ
- **BigQuery**: メインデータウェアハウス
  - 用途: 収集データの保存、分析クエリ実行、履歴管理
  - テーブル設計:
    - `updates_raw`: 生データ保存
    - `updates_processed`: 処理済みデータ
    - `analysis_results`: 分析結果
    - `reports`: レポート履歴
    - `ai_insights`: AI生成の洞察データ
- **Google Cloud Storage**: ファイル保存
  - 用途: レポートファイル、ログファイル、一時データ

### 5. データフロー

```
1. Cloud Scheduler → 定期実行トリガー
2. Orchestrator Agent → ワークフロー開始
3. Data Collector Agent → 各種ソースからデータ収集
   └─ Gemini API → データ検証・分類（Google Workspace、Gemini、NotebookLM）
4. Pub/Sub → データ収集完了通知
5. Data Processor Agent → データ前処理・構造化
   └─ Gemini API → 重要度判定・分類
6. BigQuery → 処理済みデータ保存
7. Analysis Agent → データ分析・洞察生成
   ├─ Gemini API → 基本分析・洞察生成
   └─ Vertex AI → 高度分析（必要時）
8. Report Generator Agent → レポート作成
   └─ Gemini API → レポート生成・要約
9. Cloud Storage → レポートファイル保存
10. Notification Agent → 結果通知
    └─ Gemini API → 通知内容最適化
```

### 6. AI機能詳細設計

#### 6.1 Gemini API活用

**Data Collector Agent**:
```python
# データ検証・分類
async def validate_and_classify(self, raw_data):
    prompt = f"""
    以下のアップデート情報を検証し、分類してください:
    {raw_data}
    
    分類: [重要/中程度/低] 
    カテゴリ: [機能追加/バグ修正/セキュリティ/その他]
    サービス: [Google Workspace/Gemini/NotebookLM/その他]
    """
    response = await self.gemini.generate(prompt)
    return self.parse_classification(response)
```

**Analysis Agent**:
```python
# 洞察生成
async def generate_insights(self, processed_data):
    prompt = f"""
    以下のアップデートデータから洞察を生成してください:
    {processed_data}
    
    分析項目:
    1. 主要トレンド
    2. 影響度の高いアップデート
    3. 推奨アクション
    """
    insights = await self.gemini.generate(prompt)
    return insights
```

**Report Generator Agent**:
```python
# レポート生成
async def generate_report(self, analysis_data):
    prompt = f"""
    以下の分析データからレポートを生成してください:
    {analysis_data}
    
    形式: Markdown
    内容: 実行サマリー、主要アップデート、推奨事項
    """
    report = await self.gemini.generate(prompt)
    return report
```

#### 6.2 Vertex AI活用（必要時）

**高度な分析が必要な場合**:
```python
# Vertex AI使用例
async def advanced_analysis(self, large_dataset):
    if len(large_dataset) > 1000:  # 大量データの場合
        vertex_model = GenerativeModel("gemini-pro")
        response = vertex_model.generate_content(
            large_dataset,
            generation_config={
                "temperature": 0.1,
                "max_output_tokens": 4096,
                "top_p": 0.8
            }
        )
        return response.text
    else:
        # 通常はGemini API使用
        return await self.gemini.generate(large_dataset)
```

### 7. BigQuery活用計画

#### 7.1 データ保存戦略
- **Raw Data**: 収集した生データをそのまま保存
- **Processed Data**: 前処理済みの構造化データ
- **Analytics Data**: 分析用に最適化されたデータ
- **AI Insights**: AI生成の洞察データ

#### 7.2 分析クエリ例
```sql
-- AI生成洞察の分析
SELECT 
  insight_type,
  COUNT(*) as insight_count,
  AVG(confidence_score) as avg_confidence
FROM `project.dataset.ai_insights`
WHERE created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
GROUP BY insight_type;

-- 重要度別アップデート分析
SELECT 
  importance_level,
  service_type,
  COUNT(*) as update_count,
  AVG(ai_confidence_score) as avg_ai_confidence
FROM `project.dataset.updates_processed`
WHERE ai_classified = true
GROUP BY importance_level, service_type;

-- サービス別アップデート分析（Google Workspace、Gemini、NotebookLM）
SELECT 
  service_name,
  COUNT(*) as update_count,
  AVG(importance_score) as avg_importance
FROM `project.dataset.updates_processed`
WHERE service_name IN ('Google Workspace', 'Gemini', 'NotebookLM')
  AND created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
GROUP BY service_name
ORDER BY update_count DESC;
```

### 8. Cloud Run設計

#### 8.1 サービス構成
- **main-service**: メインAPIサーバー
- **collector-service**: データ収集サービス
- **processor-service**: データ処理サービス
- **analysis-service**: 分析サービス（Gemini API + Vertex AI）
- **report-service**: レポート生成サービス
- **notification-service**: 通知サービス

#### 8.2 スケーリング設定
- **最小インスタンス**: 0（コスト最適化）
- **最大インスタンス**: 10（負荷対応）
- **CPU**: 1-2 vCPU
- **メモリ**: 2-4 GB

### 9. 実装計画

#### Phase 1: 基盤構築
- Google Cloud Project設定
- Cloud Run環境構築
- BigQueryデータセット・テーブル作成
- Google Agent Development Kit環境構築
- Gemini API設定

#### Phase 2: データ収集機能
- Data Collector Agent実装
- 各種API連携実装（Google Workspace、Gemini、NotebookLM）
- BigQueryデータ取り込み実装
- Gemini API統合（データ検証・分類）

#### Phase 3: 処理・分析機能
- Data Processor Agent実装
- Analysis Agent実装（Gemini API）
- BigQuery分析クエリ実装
- Vertex AI統合（高度分析用）

#### Phase 4: レポート・通知機能
- Report Generator Agent実装（Gemini API）
- Notification Agent実装
- Cloud Storage連携実装

#### Phase 5: 統合・最適化
- Orchestrator Agent実装
- Cloud Scheduler設定
- モニタリング・ログ設定
- AI機能の最適化

### 10. 設定・環境変数

#### 10.1 Cloud Run環境変数
```yaml
GOOGLE_APPLICATION_CREDENTIALS: /app/credentials.json
GEMINI_API_KEY: ${GEMINI_API_KEY}
BIGQUERY_DATASET: gemini_report
BIGQUERY_PROJECT: ${PROJECT_ID}
PUBSUB_TOPIC: data-collection-events
CLOUD_STORAGE_BUCKET: gemini-report-files
SLACK_WEBHOOK_URL: ${SLACK_WEBHOOK_URL}
VERTEX_AI_PROJECT: ${PROJECT_ID}  # 必要時のみ
```

#### 10.2 必要なIAM権限
- BigQuery Data Editor
- Cloud Storage Object Admin
- Pub/Sub Publisher/Subscriber
- Cloud Scheduler Admin
- Vertex AI User（必要時）

### 11. コスト最適化

#### 11.1 AI API使用量
- **Gemini API**: 基本機能（コスト効率的）
- **Vertex AI**: 必要時のみ使用（高コスト）
- **使用量監視**: Cloud MonitoringでAPI使用量追跡

#### 11.2 BigQuery
- パーティショニング: 日付ベース
- クラスタリング: サービス種別
- データ保持期間: 1年（その後Archive）

#### 11.3 Cloud Run
- 最小インスタンス: 0（コスト削減）
- 自動スケーリング: 負荷に応じて
- リクエストタイムアウト: 適切な設定

### 12. セキュリティ

#### 12.1 認証・認可
- Service Account使用
- IAM最小権限の原則
- API認証情報の安全な管理

#### 12.2 データ保護
- BigQuery暗号化
- Cloud Storage暗号化
- ネットワークセキュリティ
- AI生成データのプライバシー保護

### 13. 監視・ログ

#### 13.1 Cloud Monitoring
- エージェント実行状況
- API応答時間
- エラー率監視
- AI API使用量監視

#### 13.2 Cloud Logging
- 構造化ログ出力
- エラーログ集約
- パフォーマンスログ
- AI生成ログ

この要件定義に基づいて実装を進めていきます。 