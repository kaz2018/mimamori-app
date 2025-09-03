# 技術選定書

## プロジェクト概要
FlaskベースのWebアプリケーションをGoogle Cloud Runでデプロイし、AI機能をGoogle Agent Development Kit (ADK)で実装、ユーザー認証機能とBigQueryを活用したデータ管理を行うプロジェクト

## 選定技術スタック

### バックエンド
#### Flask
- **選定理由**
  - Pythonの軽量なWebフレームワーク
  - 学習コストが低く、迅速な開発が可能
  - Cloud Runとの相性が良い
  - マイクロサービスアーキテクチャに適している
- **バージョン**: Flask 3.1.2 (2025年8月19日リリース)
- **要件**: Python 3.9以上、Werkzeug >= 3.1、ItsDangerous >= 2.2、Blinker >= 1.9

### 認証システム
#### Flask-Login + Werkzeug
- **選定理由**
  - Flask-Login: セッション管理とユーザー認証の業界標準
  - Werkzeug: 安全なパスワードハッシング機能
  - シンプルなニックネーム・パスワード認証に最適
  - BigQueryとの統合が容易
- **関連ライブラリ**
  - Flask-Login: ユーザーセッション管理
  - Flask-WTF: フォームバリデーション
  - Flask-Bcrypt: パスワードハッシング強化（オプション）

### データベース
#### Google BigQuery
- **選定理由**
  - サーバーレス・フルマネージドデータウェアハウス
  - ペタバイト規模のデータ処理能力
  - SQLベースのクエリによる簡単なデータ操作
  - Cloud Runとの同一プロジェクト内統合
  - リアルタイム分析機能
  - 従量課金制でコスト効率が良い
- **用途**
  - ユーザー情報の保存（ニックネーム、ハッシュ化パスワード）
  - アプリケーションログの保存と分析
  - ユーザー行動データの蓄積と分析
- **接続方法**
  - google-cloud-bigquery Pythonクライアント
  - サービスアカウント認証

### フロントエンド
#### HTML + CSS
- **選定理由**
  - シンプルで保守性が高い
  - 追加のビルドプロセスが不要
  - 高速なページロード
  - SEOに優れている
- **技術詳細**
  - HTML5
  - CSS3 (Flexbox/Grid Layout活用)
  - レスポンシブデザイン対応

### インフラストラクチャ
#### Google Cloud Run
- **選定理由**
  - フルマネージドのサーバーレスプラットフォーム
  - オートスケーリング機能
  - 従量課金制でコスト効率が良い
  - コンテナベースでポータビリティが高い
  - HTTPS自動対応
- **補足技術**
  - Docker Desktop 4.44以上 (セキュリティパッチ対応版)
  - Docker Engine 27.5.1 (2025年1月22日リリース)
  - Google Cloud SDK 507.0.0 (2025年1月22日リリース)
  - Cloud Build (CI/CD)

### AI/エージェント機能
#### Google Agent Development Kit (ADK)
- **選定理由**
  - Googleが提供する最新のAIエージェント開発フレームワーク
  - Pythonネイティブで、Flaskとの統合が容易
  - Geminiモデルとの最適化された統合
  - マルチエージェントシステムの構築が可能
  - エンタープライズレベルのスケーラビリティ
- **バージョン**: Python ADK v1.13.0 (本番環境対応の安定版)
- **使用モデル**: Gemini 2.5 Flash
- **主な機能**
  - コードファーストの開発アプローチ
  - リアルタイムストリーミング対応
  - 組み込みの評価ツール
  - 100以上の事前構築コネクタ

#### Gemini 2.5 Flash選定理由
- **コスト効率**: Googleの最もコスト効率の良いモデル
- **低レイテンシ**: 高速レスポンスで優れたユーザー体験
- **思考機能**: thinking機能をデフォルトで搭載
- **マルチモーダル対応**: テキスト、音声、画像、動画の入力に対応
- **大規模コンテキスト**: 100万トークンのコンテキストウィンドウ
- **ネイティブ音声機能**: 複数話者のテキスト読み上げ対応
- **ADKとの完全互換性**: ADKでの利用が正式にサポート

## アーキテクチャ概要

```
[ユーザー] 
    ↓ HTTPS
[Cloud Run (Flask App)]
    ├── 認証システム (Flask-Login)
    ├── 静的ファイル配信 (HTML/CSS)
    └── APIエンドポイント
         ├── BigQuery (ユーザーデータ・ログ)
         └── Google ADK エージェント
              └── Gemini 2.5 Flash API
```

## 技術的な統合ポイント

### Flask + 認証システム + BigQuery統合
```python
# Flask アプリケーション内での認証とBigQuery統合例
from flask import Flask, request, jsonify, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from google.cloud import bigquery
import google.adk as adk

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # 環境変数から読み込む

# Flask-Login設定
login_manager = LoginManager()
login_manager.init_app(app)

# BigQuery クライアント初期化
bigquery_client = bigquery.Client()

# ADKエージェントの初期化
agent = adk.Agent(
    name="assistant",
    model="gemini-2.5-flash",
    description="ユーザーサポートアシスタント",
    instruction="ユーザーの質問に丁寧に回答してください"
)

# ユーザークラス
class User(UserMixin):
    def __init__(self, nickname):
        self.id = nickname

@login_manager.user_loader
def load_user(user_id):
    # BigQueryからユーザー情報を取得
    query = f"""
    SELECT nickname FROM `project.dataset.users`
    WHERE nickname = @nickname
    LIMIT 1
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("nickname", "STRING", user_id)
        ]
    )
    results = bigquery_client.query(query, job_config=job_config).result()
    for row in results:
        return User(row.nickname)
    return None

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    nickname = data['nickname']
    password = data['password']
    
    # パスワードをハッシュ化
    password_hash = generate_password_hash(password)
    
    # BigQueryにユーザー情報を保存
    table_id = "project.dataset.users"
    rows_to_insert = [
        {"nickname": nickname, "password_hash": password_hash}
    ]
    
    errors = bigquery_client.insert_rows_json(table_id, rows_to_insert)
    if errors:
        return jsonify({"error": "Registration failed"}), 400
    
    return jsonify({"message": "User registered successfully"}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    nickname = data['nickname']
    password = data['password']
    
    # BigQueryからユーザー情報を取得
    query = f"""
    SELECT nickname, password_hash FROM `project.dataset.users`
    WHERE nickname = @nickname
    LIMIT 1
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("nickname", "STRING", nickname)
        ]
    )
    results = bigquery_client.query(query, job_config=job_config).result()
    
    for row in results:
        if check_password_hash(row.password_hash, password):
            user = User(row.nickname)
            login_user(user)
            return jsonify({"message": "Login successful"}), 200
    
    return jsonify({"error": "Invalid credentials"}), 401

@app.route('/api/chat', methods=['POST'])
@login_required
async def chat():
    user_message = request.json['message']
    response = await agent.execute(user_message)
    
    # チャット履歴をBigQueryに保存
    table_id = "project.dataset.chat_logs"
    rows_to_insert = [
        {
            "nickname": current_user.id,
            "message": user_message,
            "response": response,
            "timestamp": datetime.now()
        }
    ]
    bigquery_client.insert_rows_json(table_id, rows_to_insert)
    
    return jsonify({'response': response})
```

### BigQueryテーブル設計
```sql
-- ユーザーテーブル
CREATE TABLE `project.dataset.users` (
    nickname STRING NOT NULL,
    password_hash STRING NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    last_login TIMESTAMP
);

-- チャットログテーブル
CREATE TABLE `project.dataset.chat_logs` (
    nickname STRING NOT NULL,
    message STRING,
    response STRING,
    timestamp TIMESTAMP,
    session_id STRING
);
```

### デプロイメント構成
```dockerfile
# Dockerfile
FROM python:3.13.2-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["gunicorn", "--bind", ":8080", "app:app"]
```

### requirements.txt
```txt
Flask==3.1.2
Flask-Login==0.6.3
google-cloud-bigquery==3.17.2
google-adk==1.13.0
gunicorn==22.0.0
python-dotenv==1.0.1
```

## 開発環境要件
- Python 3.13.2 (最新安定版)
- Docker Desktop 4.44以上
- Google Cloud SDK 507.0.0
- Git

## セキュリティ考慮事項
- **認証関連**
  - パスワードは必ずハッシュ化して保存
  - セッションキーは環境変数で管理
  - CSRF保護の実装（Flask-WTF）
  - レート制限の実装
- **BigQuery関連**
  - サービスアカウントによる認証
  - 最小権限の原則に基づくIAM設定
  - パラメータクエリによるSQLインジェクション対策
- **一般的なセキュリティ**
  - Cloud Runの認証機能を活用
  - HTTPSの強制
  - CORSの適切な設定
  - 最新のセキュリティパッチを含むDockerバージョンの使用

## スケーラビリティ
- Cloud Runの自動スケーリング (0-1000インスタンス)
- BigQueryの自動スケーリング機能
- ADKのマルチエージェント並列処理
- Gemini 2.5 Flashの高速レスポンスによる高スループット
- 静的ファイルのCDN配信検討

## コスト見積もり
- **Cloud Run**: リクエスト数とCPU/メモリ使用量に基づく従量課金
- **BigQuery**: 
  - ストレージ: $0.02/GB/月（アクティブストレージ）
  - クエリ: $5/TB（オンデマンド）
  - ストリーミング挿入: $0.010/200MB
- **Gemini 2.5 Flash API**: 最もコスト効率の良いモデル
- **予想月額**: 小規模利用で$10-50程度

## 今後の検討事項
1. 静的ファイルのCloud Storage + CDN配信
2. BigQueryのパーティション・クラスタリング最適化
3. Cloud Loggingによるログ管理
4. より高度な認証機能（2FA、OAuth）
5. ADKエージェントのカスタマイズと拡張
6. Gemini 2.5 Flashの画像生成機能の活用検討
7. ネイティブ音声機能を使った音声対話インターフェース
8. BigQuery MLによる予測分析機能の追加

## まとめ
シンプルなフロントエンド（HTML/CSS）とFlaskバックエンドの組み合わせにより、開発の迅速性と保守性を確保。ニックネーム・パスワードによる基本的な認証機能とBigQueryによるスケーラブルなデータ管理を実装。Google ADKとGemini 2.5 Flashによる高度なAI機能により、コスト効率と処理速度の両方を最適化。Cloud RunとBigQueryのサーバーレス特性により、スケーラビリティとコスト効率の両立が可能な構成となっている。