# Google Driveフォルダ共有設定ガイド

## 問題の原因
スライド作成が失敗する主な原因は、**Google Driveフォルダにサービスアカウントが共有されていない**ことです。

## 解決手順

### 1. サービスアカウントの確認
現在使用されているサービスアカウント:
```
slide-creator-service@ggl-research.iam.gserviceaccount.com
```

### 2. Google Driveフォルダの共有設定

#### 2.1 フォルダを開く
1. [Google Drive](https://drive.google.com)にアクセス
2. スライドを作成したいフォルダを開く

#### 2.2 共有設定を開く
1. フォルダを右クリック
2. 「共有」を選択
3. 「詳細設定」をクリック

#### 2.3 サービスアカウントを追加
1. 「ユーザーやグループを追加」をクリック
2. 以下のメールアドレスを入力:
   ```
   slide-creator-service@ggl-research.iam.gserviceaccount.com
   ```
3. 権限を「編集者」に設定
4. 「送信」をクリック

### 3. 権限の確認

#### 3.1 フォルダの権限確認
- フォルダが「編集者」権限で共有されているか確認
- サービスアカウントが表示されているか確認

#### 3.2 テスト実行
```bash
# 認証を復元
source restore_original_auth.sh

# テスト実行
python test_slides_tool.py
```

### 4. 代替方法: 新しいフォルダを作成

#### 4.1 新しいフォルダの作成
1. Google Driveで新しいフォルダを作成
2. フォルダ名: `GeminiReport_Slides`

#### 4.2 共有設定
1. 新しいフォルダを右クリック
2. 「共有」→「詳細設定」
3. サービスアカウントを追加:
   ```
   slide-creator-service@ggl-research.iam.gserviceaccount.com
   ```
4. 権限: 「編集者」

#### 4.3 フォルダIDの取得
1. フォルダを開く
2. URLからフォルダIDをコピー:
   ```
   https://drive.google.com/drive/folders/FOLDER_ID_HERE
   ```

### 5. 環境変数の更新

#### 5.1 .envファイルの更新
```env
# Google Drive設定
GOOGLE_DRIVE_FOLDER_ID=your_new_folder_id_here
```

#### 5.2 エージェント設定の更新
```python
# agents/Slide_Creator/agent.py
folder_id = os.getenv('GOOGLE_DRIVE_FOLDER_ID', 'your_new_folder_id_here')
```

## トラブルシューティング

### よくあるエラー

#### 1. "Permission denied" エラー
**原因**: サービスアカウントがフォルダにアクセスできない
**解決策**: フォルダの共有設定を確認

#### 2. "File not found" エラー
**原因**: フォルダIDが間違っている
**解決策**: 正しいフォルダIDを確認

#### 3. "Authentication failed" エラー
**原因**: 認証情報の問題
**解決策**: 認証情報を再設定

### 確認事項

- [ ] サービスアカウントがフォルダに共有されている
- [ ] 権限が「編集者」に設定されている
- [ ] フォルダIDが正しい
- [ ] 認証情報が正しく設定されている

## 次のステップ

1. **フォルダ共有設定を実行**
2. **テスト実行で動作確認**
3. **エージェントでの使用テスト** 