# Web開発分担詳細 - エンジニア2名体制

## 🎯 分担戦略

### 基本方針
- **Engineer A**: フロントエンドWebアプリ・UI/UX・3Dキャラクター重視
- **Engineer B**: バックエンド・AI/ML・データ処理重視  
- **並行開発**: PWA技術で独立開発可能な設計

---

## 👨‍💻 Engineer A - Frontend Web担当

### 🎨 主要責任領域
```
🔹 React/Vue.js Webアプリ開発
🔹 PWA実装（オフライン対応、ホーム画面追加）
🔹 3Dピンクうさぎキャラクター（Three.js）
🔹 レスポンシブUI/UX設計
🔹 Web Camera API・写真機能
🔹 ブラウザストレージ管理
```

### 📱 具体的な実装項目

#### Day 1-2: プロジェクト基盤
```typescript
// 1. Webアプリ プロジェクト設定
- React/Vue.js プロジェクト作成
- TypeScript + Vite/Webpack 設定
- PWA 設定 (manifest.json, service-worker)
- Firebase SDK Web版 統合

// 2. 基本UI フレームワーク
- コンポーネントアーキテクチャ構築
- ルーティング設定 (React Router/Vue Router)
- CSS-in-JS / SCSS スタイリングシステム
- レスポンシブデザインシステム
```

#### Day 3-4: コア機能実装
```typescript
// 3. Web音声入力システム
- Web Speech API / WebRTC 統合
- マイクアイコン UIコンポーネント
- リアルタイム音声レベル表示
- 音声認識状態フィードバック

// 4. 3Dキャラクターシステム
- Three.js セットアップ
- ピンクうさぎ 3Dモデルロード
- 基本アニメーション (待機・話す・リアクション)
- 表情変化システム
- Web Audio API でリップシンク
```

#### Day 5-6: 高度な機能
```typescript
// 5. Webカメラ・写真機能
- getUserMedia API 統合
- カメラUIコンポーネント
- Canvas API で画像加工
- CSS Filters / WebGL シェーダーフィルター

// 6. ゲーム UIコンポーネント
- しりとりゲームインターフェース
- なぞなぞ選択肢UI
- 歌・ダンスビジュアライザー
- スコア・プログレスアニメーション
```

### 🛠️ 技術スタック詳細

#### Web開発
```json
// package.json
{
  "dependencies": {
    "react": "^18.2.0",
    "@types/react": "^18.2.0",
    "three": "^0.157.0",
    "@react-three/fiber": "^8.15.0",
    "@react-three/drei": "^9.88.0",
    "firebase": "^10.5.0",
    "workbox-webpack-plugin": "^7.0.0"
  },
  "devDependencies": {
    "typescript": "^5.2.0",
    "vite": "^4.5.0",
    "@vitejs/plugin-react": "^4.1.0",
    "@types/three": "^0.157.0"
  }
}
```

#### Webアプリ構造
```
src/
├── components/
│   ├── character/
│   │   ├── CharacterCanvas.tsx
│   │   ├── AnimationController.ts
│   │   └── EmotionManager.ts
│   ├── camera/
│   │   ├── CameraCapture.tsx
│   │   └── PhotoEditor.tsx
│   └── games/
│       ├── ShiritoriGame.tsx
│       ├── RiddleGame.tsx
│       └── SongGame.tsx
├── services/
│   ├── firebase.ts
│   ├── speech.ts
│   └── camera.ts
├── assets/
│   ├── models/
│   ├── textures/
│   └── sounds/
└── pwa/
    ├── manifest.json
    └── sw.js
```

---

## 🔧 Engineer B - Backend & AI担当

### ⚙️ 主要責任領域
```
🔹 Google Cloud Platform インフラ
🔹 AI・機械学習システム
🔹 対話エンジン (Dialogflow ES)
🔹 ゲームロジック実装
🔹 データベース設計・管理
```

### 📊 具体的な実装項目

#### Day 1-2: インフラ構築
```python
# 1. GCP プロジェクト設定
- Google Cloud プロジェクト作成
- API 有効化 (Dialogflow, Speech, Vertex AI)
- サービスアカウント・認証設定
- Cloud Functions 環境構築

# 2. Dialogflow ES 設定
- Agent 作成・設定
- インテント定義
- エンティティ作成
- コンテキスト管理
```

#### Day 3-4: コアロジック実装
```python
# 3. ゲームエンジン
- しりとり判定アルゴリズム
- なぞなぞ生成・管理
- 楽曲データベース
- スコア計算システム

# 4. AI 物語生成
- Vertex AI (Gemini Pro) 連携
- プロンプトテンプレート
- コンテンツフィルタリング
- 青空文庫 API 連携
```

#### Day 5-6: 高度なシステム
```python
# 5. 音声処理
- Speech-to-Text 最適化
- Text-to-Speech カスタマイズ
- 音声品質向上
- リアルタイム処理

# 6. データ分析・管理
- 使用状況ログ
- パフォーマンス監視
- 自動スケーリング
- バックアップ・復旧
```

### 🏗️ 技術スタック詳細

#### Cloud Functions 構造
```
functions/
├── main.py                 # メインエントリーポイント
├── agents/
│   ├── core_agent.py      # セッション管理・ルーティング
│   ├── game_agent.py      # ゲームロジック
│   ├── story_agent.py     # 読み聞かせ・AI生成
│   └── memory_agent.py    # データ保存・検索
├── services/
│   ├── dialogflow_service.py
│   ├── vertexai_service.py
│   ├── speech_service.py
│   └── storage_service.py
├── utils/
│   ├── validators.py      # 入力検証
│   ├── filters.py         # コンテンツフィルタ
│   └── analytics.py       # ログ・分析
└── requirements.txt
```

#### Firestore データ設計
```javascript
// セッション管理
sessions/{sessionId}
{
  userId: string,
  startTime: timestamp,
  currentActivity: string,
  gameState: object,
  emotionalState: string,
  photos: array,
  voiceRecordings: array
}

// ゲームデータ
games/shiritori/words
{
  word: string,
  difficulty: number,
  category: string,
  isValid: boolean
}

// ユーザープロファイル  
users/{userId}
{
  name: string,
  age: number,
  preferences: object,
  achievements: array,
  totalPlayTime: number
}
```

---

## 🤝 協力・連携ポイント

### 📡 Web API 統合
```typescript
// Engineer A が実装するクライアント側
interface GameAPI {
  startShiritori(): Promise<GameSession>;
  checkWord(word: string): Promise<ValidationResult>;
  getHint(): Promise<string>;
}

// RESTful API クライアント
class APIClient {
  async post<T>(endpoint: string, data: any): Promise<T> {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    return response.json();
  }
}
```

```python
# Engineer B が実装するサーバー側
@app.route('/api/game/shiritori/start', methods=['POST'])
def start_shiritori():
    session = create_game_session('shiritori')
    return jsonify(session)
```

### 🔄 リアルタイムデータ同期
```typescript
// Firestore リアルタイム同期 (Engineer A)
import { onSnapshot, doc } from 'firebase/firestore';

const unsubscribe = onSnapshot(doc(db, 'sessions', sessionId), (doc) => {
  const sessionData = doc.data();
  // UI更新処理
  updateCharacterEmotion(sessionData.emotionalState);
  updateGameState(sessionData.gameState);
});
```

```python
# データ更新 (Engineer B)
def update_game_state(session_id, new_state):
    db.collection('sessions').document(session_id).update({
        'gameState': new_state,
        'lastUpdate': firestore.SERVER_TIMESTAMP
    })
```

### 🎭 キャラクター制御
```typescript
// Engineer A: 3Dキャラクター表示
class CharacterController {
  private scene: THREE.Scene;
  private character: THREE.Object3D;
  
  showEmotion(emotion: string) {
    // Three.js アニメーション実行
    this.playAnimation(emotion);
  }
  
  speak(text: string, audioUrl: string) {
    // 音声再生 + リップシンク
    this.syncLipMovement(audioUrl);
  }
}
```

```python
# Engineer B: 感情・発話内容生成
def generate_character_response(context):
    emotion = analyze_emotional_state(context)
    speech_text = generate_appropriate_response(context)
    audio_url = synthesize_speech(speech_text)
    
    return {
        'emotion': emotion,
        'text': speech_text,
        'audioUrl': audio_url,
        'animation': select_animation(emotion)
    }
```

---

## 🌐 PWA 特有の実装

### 📱 Progressive Web App 機能

#### Service Worker (Engineer A)
```typescript
// sw.js - オフライン対応
const CACHE_NAME = 'kidwatch-v1';
const STATIC_ASSETS = [
  '/',
  '/static/js/bundle.js',
  '/static/css/main.css',
  '/assets/models/rabbit.glb',
  '/assets/sounds/default.mp3'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(STATIC_ASSETS))
  );
});

self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request)
      .then(response => response || fetch(event.request))
  );
});
```

#### Manifest.json
```json
{
  "name": "うさぎさんとあそぼ",
  "short_name": "うさぎさん",
  "description": "子供見守りアプリ",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#FFB6C1",
  "theme_color": "#FF69B4",
  "icons": [
    {
      "src": "/icons/icon-192.png",
      "sizes": "192x192",
      "type": "image/png"
    },
    {
      "src": "/icons/icon-512.png",
      "sizes": "512x512",
      "type": "image/png"
    }
  ]
}
```

### 🎙️ Web API 活用

#### 音声認識・合成
```typescript
// Engineer A: Web Speech API実装
class WebSpeechService {
  private recognition: SpeechRecognition;
  private synthesis: SpeechSynthesis;
  
  startListening(callback: (text: string) => void) {
    this.recognition = new (window as any).webkitSpeechRecognition();
    this.recognition.lang = 'ja-JP';
    this.recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      callback(transcript);
    };
    this.recognition.start();
  }
  
  speak(text: string) {
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'ja-JP';
    this.synthesis.speak(utterance);
  }
}
```

#### カメラ・写真機能
```typescript
// getUserMedia API
class CameraService {
  private stream: MediaStream | null = null;
  
  async startCamera(): Promise<MediaStream> {
    this.stream = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: 'user' },
      audio: false
    });
    return this.stream;
  }
  
  capturePhoto(videoElement: HTMLVideoElement): string {
    const canvas = document.createElement('canvas');
    const context = canvas.getContext('2d')!;
    canvas.width = videoElement.videoWidth;
    canvas.height = videoElement.videoHeight;
    context.drawImage(videoElement, 0, 0);
    return canvas.toDataURL('image/jpeg');
  }
}
```

---

## 📅 詳細タイムライン

### Day 1 (環境構築)
| 時間 | Engineer A | Engineer B |
|------|------------|------------|
| 午前 | React/TypeScript プロジェクト作成<br/>PWA設定・Vite設定 | GCP プロジェクト設定<br/>API 有効化 |
| 午後 | Firebase Web SDK統合<br/>基本UIコンポーネント | Dialogflow ES 初期設定<br/>Cloud Functions 環境 |

### Day 2 (基盤実装)
| 時間 | Engineer A | Engineer B |
|------|------------|------------|
| 午前 | Web Speech API統合<br/>マイクUIコンポーネント | インテント・エンティティ定義<br/>Firestore スキーマ |
| 午後 | Three.js セットアップ<br/>3Dキャラクター基本表示 | 基本的なゲームロジック<br/>しりとり判定 |

### Day 3-4 (MVP機能)
| Engineer A | Engineer B |
|------------|------------|
| 3Dアニメーション・表情システム<br/>ゲームUIコンポーネント<br/>Webカメラ統合 | 完全なしりとりエンジン<br/>音声認識・合成連携<br/>基本読み聞かせ |

### Day 5-6 (拡張機能)
| Engineer A | Engineer B |
|------------|------------|
| 高度な3Dアニメーション<br/>写真加工・フィルター<br/>PWA最適化・オフライン対応 | AI物語生成<br/>スタンプ・報酬システム<br/>分析・監視機能 |

### Day 7 (統合・テスト)
**両エンジニア協力**
- クロスブラウザテスト
- PWA動作確認
- パフォーマンス最適化  
- デモ環境構築

---

## 🚦 進捗管理・コミュニケーション

### 📊 日次チェックポイント
```
毎日 17:00 - 進捗確認会議 (15分)
- 完了した機能の報告
- 発生した課題・ブロッカー
- 翌日の作業計画確認
- Web API仕様の調整・確認
```

### 📝 共有ドキュメント
- **API仕様書**: OpenAPI/Swagger形式で共有
- **Git リポジトリ**: モノレポ構成で管理
- **コンポーネントライブラリ**: Storybook で管理
- **デプロイ手順**: Vercel/Netlify 自動デプロイ

### 🔧 開発ツール
- **コミュニケーション**: Slack/Discord
- **コード管理**: Git (GitHub/GitLab)
- **API テスト**: Postman/Thunder Client  
- **監視**: Cloud Monitoring/Vercel Analytics
- **PWAテスト**: Lighthouse/PWA Builder

### 🌍 ブラウザ対応・テスト
```
対象ブラウザ:
✅ Chrome 90+ (最優先)
✅ Safari 14+ (iOS対応重要)
✅ Firefox 88+
✅ Edge 90+

テスト項目:
- WebRTC音声認識・カメラ
- Three.js 3D描画性能
- PWA インストール・オフライン
- タッチ操作・レスポンシブ
```

この分担により、2名のエンジニアがWebアプリケーション技術を活用し、効率的に協力しながら、ハッカソン期間内で高品質な子供見守りPWAアプリを完成させることができます！
