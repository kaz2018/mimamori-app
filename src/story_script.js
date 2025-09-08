// Story Agent JavaScript Functions
class StoryAgent {
    constructor() {
        this.currentSession = null;
        this.isLoading = false;
        this.speechSynthesis = window.speechSynthesis;
        this.isReading = false;
        this.currentAudio = null; // 現在再生中の音声ファイル
        this.apiBaseUrl = window.location.origin; // ADK APIのベースURL
        this.pageCount = 0; // ページカウンター追加
        this.maxPages = 3; // 最大3ページ
        this.nextPagePromise = null; // 次ページの事前準備
        this.nextPageData = null; // 次ページのプリロードデータ
        this.p3ImageUrl = null; // P3の画像URLを保持
        this.imageStatusInterval = null; // 画像生成状況監視のインターバル
        this.audioEnabled = true; // 音声読み上げの有効/無効状態
        this.currentPageRead = false; // 現在のページが読み上げ済みかどうか
        this.init();
    }

    init() {
        this.bindEvents();
        this.updateRabbitMessage();
        
        // URLパラメータからストーリータイプを取得して自動開始
        const urlParams = new URLSearchParams(window.location.search);
        const storyType = urlParams.get('type');
        if (storyType) {
            this.autoStartStory(storyType);
        }
    }

    bindEvents() {
        // Control buttons
        const newStoryBtn = document.getElementById('new-story-btn');
        const readAloudBtn = document.getElementById('read-aloud-btn');
        
        if (newStoryBtn) {
            newStoryBtn.addEventListener('click', () => {
                this.newStory();
            });
        }

        if (readAloudBtn) {
            // 既存のイベントリスナーを削除（重複防止）
            readAloudBtn.removeEventListener('click', this.toggleReadAloud);
            // 新しいイベントリスナーを設定
            readAloudBtn.addEventListener('click', () => {
                this.toggleReadAloud();
            });
        }
    }

    updateRabbitMessage() {
        // このページにはラビットメッセージはないのでスキップ
    }

    async autoStartStory(storyType) {
        console.log(`自動開始: ${storyType}`);
        
        // ページタイトルを更新
        document.title = `${storyType} - みまもりうさぎの読み聞かせ`;
        
        // DOMが完全に読み込まれるまで待つ
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => {
                this.startStory(storyType);
            });
        } else {
            // 少し待ってからストーリーを開始
            setTimeout(() => {
                this.startStory(storyType);
            }, 100);
        }
    }

    async startStory(storyType) {
        // 既存の画像生成状況の監視を停止
        this.stopImageStatusMonitoring();
        
        // 現在の読み上げを停止
        this.stopReading();
        
        // 新しいストーリー開始時に読み上げ済みフラグをリセット
        this.currentPageRead = false;
        this.audioEnabled = true; // 新しいストーリーでは音声を有効にする
        console.log('📚 新しいストーリー開始: 読み上げ状態をリセット');
        
        this.pageCount = 1; // P1から開始
        console.log('新しいストーリー開始 - P1');
        
        this.showLoading();
        
        try {
            // P1のデータを取得
            const p1Response = await this.callStoryAgentStart(storyType);
            
            // P1を表示
            this.displayStory(p1Response);
            
        } catch (error) {
            console.error('Story generation failed:', error);
            this.showError('お話の準備に失敗しました。もう一度お試しください。');
        }
    }
    


    async callStoryAgentStart(topic) {
        try {
            console.log(`🔄 ストーリー開始APIを呼び出し中: ${topic}`);
            console.log(`📡 API URL: ${this.apiBaseUrl}/agent/storytelling/start`);
            
            const requestBody = { topic: topic };
            console.log(`📤 リクエストボディ:`, requestBody);
            
            const response = await fetch(`${this.apiBaseUrl}/agent/storytelling/start`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestBody)
            });
            
            console.log(`📥 レスポンスステータス: ${response.status}`);
            
            if (!response.ok) {
                const errorText = await response.text();
                console.error(`❌ HTTP エラー: ${response.status} - ${errorText}`);
                throw new Error(`HTTP error! status: ${response.status} - ${errorText}`);
            }
            
            const data = await response.json();
            console.log('✅ ストーリー開始API応答:', data);
            
            // セッションIDを保存
            this.currentSession = data.session_id;
            console.log(`💾 セッションID保存: ${this.currentSession}`);
            
            const textResult = data.text_result || '';
            const imageUrl = data.image_url;
            
            console.log('📝 テキスト結果:', textResult);
            console.log('🖼️ 画像URL:', imageUrl);
            
            return {
                text: textResult,
                choices: ["物語を続ける"],
                image: imageUrl,
                originalResponse: textResult
            };
            
        } catch (error) {
            console.error('❌ ストーリー開始API呼び出しエラー:', error);
            
            // エラー時のフォールバック
            return {
                text: `ストーリー生成中です...\n\n（デモモード）\nわーい！${topic}、いいね！\n\nむかしむかし、深い森の奥に、ちっちゃなウサギさんが住んでいました。名前は「ふわふわ」。`,
                choices: ["物語を続ける"],
                image: null
            };
        }
    }

    async callStoryAgentNext() {
        try {
            console.log(`🔄 ストーリー継続APIを呼び出し中: session_id=${this.currentSession}`);
            console.log(`📡 API URL: ${this.apiBaseUrl}/agent/storytelling/next`);
            
            const requestBody = { session_id: this.currentSession };
            console.log(`📤 リクエストボディ:`, requestBody);
            
            const response = await fetch(`${this.apiBaseUrl}/agent/storytelling/next`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestBody)
            });
            
            console.log(`📥 レスポンスステータス: ${response.status}`);
            
            if (!response.ok) {
                const errorText = await response.text();
                console.error(`❌ HTTP エラー: ${response.status} - ${errorText}`);
                throw new Error(`HTTP error! status: ${response.status} - ${errorText}`);
            }
            
            const data = await response.json();
            console.log('✅ ストーリー継続API応答:', data);
            
            const textResult = data.text_result || '';
            const imageUrl = data.image_url;
            
            console.log('📝 テキスト結果:', textResult);
            console.log('🖼️ 画像URL:', imageUrl);
            
            // 「おしまい」が含まれているかチェック
            const isEnd = textResult.includes('おしまい');
            console.log(`🏁 ストーリー終了チェック: ${isEnd}`);
            
            return {
                text: textResult,
                choices: isEnd ? [] : ["物語を続ける"],
                image: imageUrl,
                originalResponse: textResult
            };
            
        } catch (error) {
            console.error('❌ ストーリー継続API呼び出しエラー:', error);
            
            return {
                text: 'ストーリーの続きを読み込み中です...',
                choices: ["物語を続ける"],
                image: null
            };
        }
    }

    parseStoryResponse(responseText) {
        console.log('応答テキストを解析中:', responseText);
        
        if (!responseText) {
            return { text: "", choices: [] };
        }

        // 画像URLまたは画像関連の文言があるかチェック
        const hasImage = responseText.includes('![ハッピーエンド]') || 
                         responseText.includes('画像URL:') || 
                         responseText.includes('絵ができたよ') ||
                         responseText.includes('画像が');

        // 番号付きの選択肢を探す（1. 2. の形式）
        const numberedChoicesRegex = /(\d+)\.\s*([^\n\r]+)/g;
        const choices = [];
        let match;
        
        while ((match = numberedChoicesRegex.exec(responseText)) !== null) {
            const choiceText = match[2].trim();
            // .pngや変な文字列は除外
            if (choiceText && choiceText.length > 3 && 
                !choiceText.includes('png') && 
                !choiceText.includes('URL') && 
                choiceText.length < 100) {
                choices.push(choiceText);
            }
        }
        
        // 選択肢が見つからない場合は、**で囲まれた選択肢を探す
        if (choices.length === 0) {
            const boldChoicesRegex = /\*\*([^*]+)\*\*/g;
            while ((match = boldChoicesRegex.exec(responseText)) !== null) {
                const choiceText = match[1].trim();
                if (choiceText && choiceText.length > 3 && 
                    !choiceText.includes('png') && 
                    choiceText.length < 100) {
                    choices.push(choiceText);
                }
            }
        }

        // 選択肢部分を除いたテキストを取得
        let storyText = responseText;
        
        // 最後の番号付きリストまたは**選択肢を除去
        if (choices.length > 0) {
            // 最後の選択肢の位置を探して、それより前をストーリーテキストとする
            const lastChoiceIndex = responseText.lastIndexOf(choices.length + '.');
            if (lastChoiceIndex !== -1) {
                const beforeLastChoice = responseText.substring(0, lastChoiceIndex);
                const lines = beforeLastChoice.split('\n');
                
                // 空行を除いて最後の意味のある行を探す
                for (let i = lines.length - 1; i >= 0; i--) {
                    if (lines[i].trim() && !lines[i].match(/^\d+\./)) {
                        storyText = lines.slice(0, i + 1).join('\n').trim();
                        break;
                    }
                }
            } else {
                // **形式の場合も同様に処理
                const lastBoldIndex = responseText.lastIndexOf('**');
                if (lastBoldIndex !== -1) {
                    const beforeBold = responseText.substring(0, lastBoldIndex);
                    storyText = beforeBold.trim();
                }
            }
        }

        // 画像URLやMarkdown画像を文章から除去
        // 画像URL行を除去
        storyText = storyText.replace(/画像URL:\s*https:\/\/[^\s\n]+/gi, '');
        // 全てのMarkdown画像を除去
        storyText = storyText.replace(/!\[[^\]]*\]\([^)]+\)/g, '');
        // 選択肢A, B形式の画像も除去
        storyText = storyText.replace(/!\[選択肢[AB]\]\([^)]+\)/g, '');
        // 画像関連の説明文を除去
        storyText = storyText.replace(/素敵な絵ができたよ！見てみて！\s*/g, '');
        storyText = storyText.replace(/わあ！見て！これが.*?絵だよ！\s*/g, '');
        storyText = storyText.replace(/画像を.*?しました[。！]?\s*/g, '');
        // 「続きを読む」などの不要なテキストを除去
        storyText = storyText.replace(/続きを読む[。\.…]*\s*/g, '');
        storyText = storyText.replace(/続きは次回[。\.…]*\s*/g, '');
        storyText = storyText.replace(/\.\.\.\s*$/g, '');
        // 余分な改行を整理
        storyText = storyText.replace(/\n\s*\n\s*\n/g, '\n\n').trim();

        // 物語が終了している場合の特別な選択肢
        let finalChoices = choices;
        if (responseText.includes('おしまい') || responseText.includes('めでたし')) {
            finalChoices = [
                "🔄 新しいお話を始める"
            ];
        } else if (choices.length === 0) {
            finalChoices = ["物語を続ける", "別の選択をする"];
        }

        console.log('解析結果 - テキスト:', storyText.substring(0, 100) + '...');
        console.log('解析結果 - 選択肢:', finalChoices);

        return {
            text: storyText.trim(),
            choices: finalChoices
        };
    }

    extractAndSaveImageUrl(responseText) {
        // 画像URLを抽出して保存
        const imageUrlMatch = responseText.match(/https:\/\/storage\.googleapis\.com\/[^\s)]+\.png/);
        if (imageUrlMatch) {
            this.lastImageUrl = imageUrlMatch[0];
            console.log('画像URL保存:', this.lastImageUrl);
        }
    }

    showLoading() {
        this.isLoading = true;
        const featuresSection = document.getElementById('features');
        if (featuresSection) featuresSection.classList.add('hidden');
        const storySection = document.getElementById('story-section');
        if (storySection) storySection.classList.add('hidden');
        document.getElementById('loading-section').classList.remove('hidden');
        
        // ローディング中のメッセージを変更
        const loadingMessages = [
            "お話を準備しています...",
            "魔法をかけています...",
            "キャラクターたちが準備中...",
            "素敵な物語を作っています..."
        ];
        
        let messageIndex = 0;
        const messageInterval = setInterval(() => {
            if (!this.isLoading) {
                clearInterval(messageInterval);
                return;
            }
            document.querySelector('.loading-text').textContent = 
                loadingMessages[messageIndex % loadingMessages.length];
            messageIndex++;
        }, 1000);
    }

    displayStory(storyData) {
        console.log('=== displayStory 開始 ===');
        console.log('🔍 displayStory呼び出し元のスタックトレース:');
        console.trace();
        console.log('受信したストーリーデータ:', storyData);
        
        // 現在の読み上げを停止
        this.stopReading();
        
        this.isLoading = false;
        document.getElementById('loading-section').classList.add('hidden');
        document.getElementById('story-section').classList.remove('hidden');
        
        // ストーリーテキストを表示
        document.getElementById('story-text').textContent = storyData.text;
        console.log('ストーリーテキスト表示:', storyData.text);
        
        // 画像表示の処理
        let imageUrlToDisplay = null;
        
        if (storyData.image_url) {
            // APIレスポンスのimage_urlフィールドを使用
            imageUrlToDisplay = storyData.image_url;
            console.log(`P${this.pageCount}の画像URLを表示:`, imageUrlToDisplay);
        } else if (storyData.image) {
            // フォールバック: imageフィールドもチェック
            imageUrlToDisplay = storyData.image;
            console.log(`P${this.pageCount}の画像URLを表示（フォールバック）:`, imageUrlToDisplay);
        }
        
        // 画像を表示
        if (imageUrlToDisplay) {
            console.log('画像URLを表示:', imageUrlToDisplay);
            this.showPictureArea();
            this.displayImage(imageUrlToDisplay);
        } else {
            console.log('画像URLなし - 画像エリア非表示');
            this.hidePictureArea();
        }
        
        // 選択肢を表示（分岐なしの場合は「続きを読む」ボタン）
        this.displaySimpleChoices(storyData.choices);
        
        console.log('=== displayStory 完了 ===');
        
        // ストーリー表示完了後にスクロール位置を一番上に移動
        setTimeout(() => {
            try {
                // 複数のスクロール方法を試行
                if (window.scrollTo) {
                    window.scrollTo({ top: 0, behavior: 'smooth' });
                    console.log('📜 displayStory完了後にスクロール位置を一番上に移動 (scrollTo)');
                } else if (document.documentElement.scrollTop !== undefined) {
                    document.documentElement.scrollTop = 0;
                    console.log('📜 displayStory完了後にスクロール位置を一番上に移動 (documentElement)');
                } else if (document.body.scrollTop !== undefined) {
                    document.body.scrollTop = 0;
                    console.log('📜 displayStory完了後にスクロール位置を一番上に移動 (body)');
                }
            } catch (error) {
                console.warn('スクロール処理でエラーが発生:', error);
                // フォールバック: 即座にスクロール
                window.scrollTo(0, 0);
            }
        }, 200); // 200ms待ってから実行
        
        // 音声が有効な場合のみ自動読み上げ
        console.log('🔍 自動読み上げ判定開始');
        if (this.audioEnabled && !this.currentPageRead && !this.isReading) {
            console.log('🎤 自動読み上げを開始 - 条件: audioEnabled=true, currentPageRead=false, isReading=false');
            this.readStoryText(storyData.text);
            this.currentPageRead = true;
        } else if (!this.audioEnabled) {
            console.log('🔇 音声が無効のため自動読み上げをスキップ - audioEnabled=false');
        } else if (this.currentPageRead) {
            console.log('🔇 既に読み上げ済みのため自動読み上げをスキップ - currentPageRead=true');
        } else if (this.isReading) {
            console.log('🔇 既に読み上げ中のため自動読み上げをスキップ - isReading=true');
        }
        
        // デバッグ用: 現在の状態をログ出力
        console.log('🔍 displayStory時の状態:', {
            audioEnabled: this.audioEnabled,
            currentPageRead: this.currentPageRead,
            isReading: this.isReading
        });
    }
    
    showPictureArea() {
        const pictureArea = document.getElementById('picture-area');
        if (pictureArea) {
            pictureArea.style.display = 'flex';
        }
    }
    
    hidePictureArea() {
        const pictureArea = document.getElementById('picture-area');
        if (pictureArea) {
            pictureArea.style.display = 'none';
        }
    }
    
    displayPicturebookImages(images, choices) {
        console.log('=== displayPicturebookImages 開始 ===');
        console.log('画像データ:', images);
        console.log('選択肢:', choices);
        
        const pictureDisplay = document.getElementById('picture-display');
        console.log('picture-display要素:', pictureDisplay);
        
        if (!pictureDisplay) {
            console.error('picture-display要素が見つかりません');
            return;
        }
        
        // 画像表示エリアをクリア
        pictureDisplay.innerHTML = '';
        
        if (images.length === 1 && images[0].cloud_url) {
            console.log('単一画像表示:', images[0].cloud_url);
            // 単一画像を自動表示
            const img = document.createElement('img');
            img.src = images[0].cloud_url;
            img.alt = 'ストーリー画像';
            img.style.maxWidth = '100%';
            img.style.height = 'auto';
            img.onload = () => console.log('✅ ストーリー画像読み込み完了:', images[0].cloud_url);
            img.onerror = () => console.error('❌ ストーリー画像読み込み失敗:', images[0].cloud_url);
            
            pictureDisplay.appendChild(img);
            console.log('単一画像DOM追加完了');
        } else if (images.length > 1) {
            console.log('複数画像 - 最初の画像を表示:', images[0].cloud_url);
            // 複数画像がある場合は最初の画像を表示
            const img = document.createElement('img');
            img.src = images[0].cloud_url;
            img.alt = 'ストーリー画像';
            img.style.maxWidth = '100%';
            img.style.height = 'auto';
            img.onload = () => console.log('ストーリー画像読み込み完了');
            img.onerror = () => console.error('ストーリー画像読み込み失敗');
            
            pictureDisplay.appendChild(img);
        }
    }
    
    hidePictureLoading() {
        const pictureDisplay = document.getElementById('picture-display');
        if (pictureDisplay) {
            pictureDisplay.innerHTML = '<p style="color: #999;">画像準備中...</p>';
        }
    }
    
    selectImageChoice(index, choiceText) {
        console.log(`画像選択: ${index} - ${choiceText}`);
        this.selectChoice(choiceText);
    }
    
    extractImageDataFromResponse(responseText) {
        console.log('画像データ抽出中:', responseText);
        
        const images = [];
        
        // 最優先: Cloud Storage URLの直接検索
        const cloudStorageMatches = responseText.match(/https:\/\/storage\.googleapis\.com\/childstory-ggl-research-3db4311e\/[^\s\n)]+\.png/g);
        if (cloudStorageMatches) {
            console.log('Cloud Storage URLを発見:', cloudStorageMatches);
            cloudStorageMatches.forEach((url, index) => {
                images.push({
                    cloud_url: url,
                    choice_index: index,
                    alt: `ストーリー画像${index + 1}`
                });
            });
        }
        
        // Markdown画像の抽出（バックアップ）
        const allMarkdownMatches = responseText.match(/!\[[^\]]*\]\((https:\/\/storage\.googleapis\.com\/[^)]+)\)/g);
        if (allMarkdownMatches) {
            console.log('Markdown画像を発見:', allMarkdownMatches);
            allMarkdownMatches.forEach((match, index) => {
                const urlMatch = match.match(/\((https:\/\/[^)]+)\)/);
                if (urlMatch && !images.some(img => img.cloud_url === urlMatch[1])) {
                    images.push({
                        cloud_url: urlMatch[1],
                        choice_index: index,
                        alt: `ストーリー画像${index + 1}`
                    });
                }
            });
        }
        
        console.log('抽出された画像データ:', images);
        return images;
    }

    displayChoices(choices) {
        const choicesContainer = document.getElementById('story-choices');
        choicesContainer.innerHTML = '';
        
        if (choices && choices.length > 0) {
            choices.forEach((choice, index) => {
                const button = document.createElement('button');
                button.className = 'choice-btn';
                button.textContent = `${index + 1}. ${choice}`;
                button.addEventListener('click', () => {
                    this.selectChoice(choice, index);
                });
                choicesContainer.appendChild(button);
            });
        }
    }
    
    displaySimpleChoices(choices) {
        const choicesContainer = document.getElementById('story-choices');
        choicesContainer.innerHTML = '';

        // choicesが空配列なら、物語の終わり。
        if (!choices || choices.length === 0) {
            // 「新しいお話を始める」ボタンを表示
            const endBtn = document.createElement('button');
            endBtn.className = 'choice-btn';
            endBtn.textContent = '🔄 新しいお話を始める';
            endBtn.onclick = () => this.newStory();
            choicesContainer.appendChild(endBtn);
            return; // ここで処理を終了
        }

        // choicesに何か（"物語を続ける"）が入っている場合は、「続きを読む」ボタンを表示
        const continueBtn = document.createElement('button');
        continueBtn.className = 'choice-btn';
        // ★ IDを追加して、後からボタンを特定できるようにする
        continueBtn.id = 'continue-btn'; 
        
        // ★ 最初は必ず非活性状態で表示
        continueBtn.textContent = '⏳ 画像を準備中...';
        continueBtn.disabled = true;
        continueBtn.style.opacity = '0.6';
        
        continueBtn.onclick = () => this.continueStory();
        
        choicesContainer.appendChild(continueBtn);
        
        // ★ 画像生成状況の監視を開始する関数を呼び出す
        this.startImageStatusMonitoring();
    }
    
    // 画像生成状況を監視する関数
    async startImageStatusMonitoring() {
        if (!this.currentSession || this.pageCount >= this.maxPages) {
            return;
        }
        
        // 既に監視中の場合はスキップ
        if (this.imageStatusInterval) {
            console.log('⚠️ 画像生成状況の監視は既に実行中です');
            return;
        }
        
        console.log(`🔄 画像生成状況の監視を開始 - 対象: P${this.pageCount + 1}`);
        
        // 既存のインターバルをクリア（念のため）
        this.stopImageStatusMonitoring();
        
        this.imageStatusInterval = setInterval(async () => {
            // 実行中のフラグをチェック（重複実行防止）
            if (this.imageStatusChecking) {
                console.log('⚠️ 画像生成状況チェックは既に実行中です');
                return;
            }
            
            this.imageStatusChecking = true;
            
            try {
                const response = await fetch(`${this.apiBaseUrl}/agent/storytelling/image-status/${this.currentSession}`);
                if (response.ok) {
                    const data = await response.json();
                    console.log('📊 画像生成状況:', data);
                    
                    const continueBtn = document.getElementById('continue-btn');
                    if (continueBtn && data.has_next_image) {
                        // 画像が生成完了したら、ポーリングを停止してボタンを活性化
                        console.log('✅ 次のページの画像が準備完了');
                        
                        // 重複実行を防ぐため、既に停止済みかチェック
                        if (this.imageStatusInterval) {
                            this.stopImageStatusMonitoring();
                        } else {
                            console.log('⚠️ 画像監視は既に停止済みです');
                        }
                        
                        // 画像準備完了 - 読み上げとは無関係
                        console.log('🖼️ 画像準備完了 - 続きを読むボタンを有効化');
                        
                        // ボタンが既に有効化されている場合はスキップ
                        if (!continueBtn.disabled) {
                            console.log('⚠️ 続きを読むボタンは既に有効化済みです');
                        } else {
                            continueBtn.disabled = false;
                            continueBtn.textContent = '📖 続きを読む';
                            continueBtn.style.opacity = '1';
                        }
                    }
                } else {
                    // APIエラー時もポーリングを停止
                    this.stopImageStatusMonitoring();
                }
            } catch (error) {
                console.error('❌ 画像生成状況の取得に失敗:', error);
                this.stopImageStatusMonitoring();
            } finally {
                this.imageStatusChecking = false;
            }
        }, 3000); // 3秒ごとにチェック
    }
    
    // 画像生成状況の監視を停止する関数
    stopImageStatusMonitoring() {
        if (this.imageStatusInterval) {
            clearInterval(this.imageStatusInterval);
            this.imageStatusInterval = null;
            this.imageStatusChecking = false; // 実行中フラグもリセット
            console.log('🛑 画像生成状況の監視を停止');
        } else {
            console.log('🛑 画像生成状況の監視は既に停止済み');
        }
    }
    
    async continueStory() {
        // 進行中の画像監視を停止
        this.stopImageStatusMonitoring();

        // 現在の読み上げを停止
        this.stopReading();
        
        // ページ遷移時に読み上げ済みフラグをリセット
        this.currentPageRead = false;
        console.log('📄 ページ遷移: 読み上げ済みフラグをリセット');

        // ページ制限チェック
        if (this.pageCount >= this.maxPages) {
            console.log('最大ページ数に達しました');
            this.endStory();
            return;
        }
        
        this.showLoading();
        
        try {
            this.pageCount++;
            console.log(`🔄 P${this.pageCount}に進行中（前のページ: ${this.pageCount - 1}）`);
            
            // 新しいAPIを使用して次のページを取得
            const response = await this.callStoryAgentNext();
            
            this.displayStory(response);
            
            // ページめくり時にスクロール位置を一番上に移動（より確実な方法）
            setTimeout(() => {
                try {
                    // 複数のスクロール方法を試行
                    if (window.scrollTo) {
                        window.scrollTo({ top: 0, behavior: 'smooth' });
                        console.log('📜 スクロール位置を一番上に移動 (scrollTo)');
                    } else if (document.documentElement.scrollTop !== undefined) {
                        document.documentElement.scrollTop = 0;
                        console.log('📜 スクロール位置を一番上に移動 (documentElement)');
                    } else if (document.body.scrollTop !== undefined) {
                        document.body.scrollTop = 0;
                        console.log('📜 スクロール位置を一番上に移動 (body)');
                    }
                } catch (error) {
                    console.warn('スクロール処理でエラーが発生:', error);
                    // フォールバック: 即座にスクロール
                    window.scrollTo(0, 0);
                }
            }, 100); // 100ms待ってから実行
            
        } catch (error) {
            console.error('Story continuation failed:', error);
            this.showError('お話の続きに失敗しました。');
        }
    }
    
    endStory() {
        // 画像生成状況の監視を停止
        this.stopImageStatusMonitoring();
        
        const choicesContainer = document.getElementById('story-choices');
        choicesContainer.innerHTML = '';
        
        const endBtn = document.createElement('button');
        endBtn.className = 'choice-btn';
        endBtn.textContent = '🔄 新しいお話を始める';
        endBtn.onclick = () => this.newStory();
        choicesContainer.appendChild(endBtn);
    }
    


    displayImage(imageUrl) {
        console.log('displayImage呼び出し:', imageUrl);
        
        // picture-displayエリアに画像を表示
        const pictureDisplay = document.getElementById('picture-display');
        if (pictureDisplay) {
            pictureDisplay.innerHTML = `
                <img src="${imageUrl}" alt="物語の絵" style="max-width: 100%; height: auto; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
            `;
            console.log('画像をpicture-displayに表示完了');
        } else {
            console.error('picture-display要素が見つかりません');
        }
    }

    async selectChoice(choice, index) {
        // 特別な選択肢の処理
        if (choice.includes('生成された画像を見る')) {
            this.showImageViewer();
            return;
        }
        
        if (choice.includes('新しいお話を始める')) {
            this.newStory();
            return;
        }
        
        // 現在の読み上げを停止
        this.stopReading();
        
        // 選択肢選択時に読み上げ済みフラグをリセット
        this.currentPageRead = false;
        console.log('📄 選択肢選択: 読み上げ済みフラグをリセット');
        
        this.showLoading();
        
        try {
            // 選択した内容を次のストーリーに送信
            const response = await this.sendChoice(choice, index);
            this.displayStory(response);
            
            // 選択肢選択時にスクロール位置を一番上に移動（より確実な方法）
            setTimeout(() => {
                try {
                    // 複数のスクロール方法を試行
                    if (window.scrollTo) {
                        window.scrollTo({ top: 0, behavior: 'smooth' });
                        console.log('📜 選択肢選択時にスクロール位置を一番上に移動 (scrollTo)');
                    } else if (document.documentElement.scrollTop !== undefined) {
                        document.documentElement.scrollTop = 0;
                        console.log('📜 選択肢選択時にスクロール位置を一番上に移動 (documentElement)');
                    } else if (document.body.scrollTop !== undefined) {
                        document.body.scrollTop = 0;
                        console.log('📜 選択肢選択時にスクロール位置を一番上に移動 (body)');
                    }
                } catch (error) {
                    console.warn('スクロール処理でエラーが発生:', error);
                    // フォールバック: 即座にスクロール
                    window.scrollTo(0, 0);
                }
            }, 100); // 100ms待ってから実行
            
        } catch (error) {
            console.error('Choice processing failed:', error);
            this.showError('選択の処理に失敗しました。');
        }
    }

    async sendChoice(choice, index) {
        try {
            console.log(`選択肢をADKエージェントに送信: ${choice} (index: ${index})`);
            
            const response = await fetch(`${this.apiBaseUrl}/agent/storytelling`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    input: `ユーザーの選択: ${choice}。この選択に基づいて物語を続けてください。`,
                    session_id: this.currentSession // セッションIDを送信
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            console.log('ADKエージェント応答（選択肢）:', data);
            
            // セッションIDを保存
            this.currentSession = data.session_id;
            
            // 新しいAPIレスポンス形式に対応
            const textResult = data.text_result || data.result || '';
            const imageUrl = data.image_url;
            
            console.log('テキスト結果:', textResult);
            console.log('画像URL:', imageUrl);
            
            // ADKエージェントからの応答を解析して選択肢を抽出
            const parsedStory = this.parseStoryResponse(textResult);
            
            return {
                text: parsedStory.text || '物語が続きます...',
                choices: parsedStory.choices || [
                    "さらに物語を続ける",
                    "別の選択をする"
                ],
                image: imageUrl, // 新しい画像URL
                originalResponse: textResult // 生のレスポンスを保持
            };
            
        } catch (error) {
            console.error('選択肢送信エラー:', error);
            
            // エラー時のフォールバック（デモ用）
            if (index === 0) {
                return {
                    text: `「${choice}」を選びました！\n\n（デモモード）\nふわふわは勇気を出して歌声の方へ向かいました。すると、美しい鳥さんに出会いました！\n\n鳥さんと友達になったふわふわ。さあ、次はどうする？`,
                    choices: [
                        "鳥さんと一緒に空を飛んでみる",
                        "鳥さんの歌を一緒に歌ってみる"
                    ],
                    image: null
                };
            } else {
                return {
                    text: `「${choice}」を選びました！\n\n（デモモード）\nふわふわはお気に入りの花畑で遊びました。すると、そこには他の動物の友達がいました！\n\nみんなでどんな遊びをする？`,
                    choices: [
                        "みんなでかくれんぼをする",
                        "お花でかんむりを作る"
                    ],
                    image: null
                };
            }
        }
    }

    showImageViewer() {
        // 最後のADK応答から画像URLを抽出（this.lastRawResponseに保存）
        if (this.lastImageUrl) {
            this.showImageModal(this.lastImageUrl);
        } else {
            // フォールバック：表示されている文章から抽出を試行
            const storyText = document.getElementById('story-text').textContent;
            const imageUrlMatch = storyText.match(/https:\/\/storage\.googleapis\.com\/[^\s)]+\.png/);
            
            if (imageUrlMatch) {
                const imageUrl = imageUrlMatch[0];
                this.showImageModal(imageUrl);
            } else {
                alert('申し訳ございません。画像が見つかりませんでした。');
            }
        }
    }

    showImageModal(imageUrl) {
        // モーダル用のHTMLを作成
        const modal = document.createElement('div');
        modal.className = 'image-modal';
        modal.innerHTML = `
            <div class="modal-content">
                <span class="close-button" onclick="this.parentElement.parentElement.remove()">&times;</span>
                <img src="${imageUrl}" alt="物語の結末画像" class="story-image">
                <div class="image-actions">
                    <button class="modal-btn" onclick="this.parentElement.parentElement.parentElement.remove()">閉じる</button>
                    <button class="modal-btn" onclick="window.open('${imageUrl}', '_blank')">新しいタブで開く</button>
                </div>
            </div>
        `;
        
        // スタイルを追加
        if (!document.getElementById('modal-styles')) {
            const style = document.createElement('style');
            style.id = 'modal-styles';
            style.textContent = `
                .image-modal {
                    position: fixed;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    background-color: rgba(0, 0, 0, 0.8);
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    z-index: 1000;
                }
                
                .modal-content {
                    background: white;
                    border-radius: 10px;
                    padding: 20px;
                    max-width: 90%;
                    max-height: 90%;
                    position: relative;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                }
                
                .close-button {
                    position: absolute;
                    top: 10px;
                    right: 15px;
                    font-size: 28px;
                    font-weight: bold;
                    color: #aaa;
                    cursor: pointer;
                }
                
                .close-button:hover {
                    color: #000;
                }
                
                .story-image {
                    max-width: 100%;
                    max-height: 70vh;
                    border-radius: 8px;
                    box-shadow: 0 4px 8px rgba(0,0,0,0.2);
                }
                
                .image-actions {
                    margin-top: 15px;
                    display: flex;
                    gap: 10px;
                }
                
                .modal-btn {
                    background-color: var(--primary-pink);
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 20px;
                    cursor: pointer;
                    font-weight: bold;
                }
                
                .modal-btn:hover {
                    background-color: var(--dark-pink);
                }
            `;
            document.head.appendChild(style);
        }
        
        document.body.appendChild(modal);
    }

    readStoryText(text) {
        // 音声が無効化されている場合は読み上げをスキップ
        if (!this.audioEnabled) {
            console.log('🔇 音声が無効化されているため、読み上げをスキップ');
            return;
        }
        
        // 既に読み上げ中の場合は停止してから開始
        if (this.isReading) {
            console.log('🔇 既存の読み上げを停止してから新しい読み上げを開始');
            this.stopReading();
        }
        
        // 無限ループ防止: 同じページで既に読み上げ済みの場合はスキップ
        if (this.currentPageRead) {
            console.log('🔇 同じページで既に読み上げ済みのため、読み上げをスキップ');
            return;
        }
        
        console.log('🎤 読み上げ開始:', text.substring(0, 50) + '...');
        console.log('🔍 readStoryText時の状態:', {
            audioEnabled: this.audioEnabled,
            currentPageRead: this.currentPageRead,
            isReading: this.isReading
        });
        
        // Text-to-Speech APIを呼び出して音声を生成・再生
        this.generateAndPlayAudio(text);
    }
    
    async generateAndPlayAudio(text) {
        try {
            console.log('🎤 音声生成開始');
            
            // 音声生成開始前に停止状態をチェック
            if (!this.audioEnabled) {
                console.log('🔇 音声生成中に停止されたため、生成をキャンセル');
                return;
            }
            
            // TTS APIを呼び出し
            const response = await fetch(`${this.apiBaseUrl}/agent/storytelling/generate-audio`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    text: text,
                    language: 'ja'
                })
            });
            
            if (response.ok) {
                const data = await response.json();
                console.log('🎵 TTS APIレスポンス:', data);
                console.log('🎵 レスポンス詳細 - success:', data.success, 'audio_url:', data.audio_url);
                
                // ★★★★★★★★★★★★★★★★★★★★★★★★★★★★★
                // 修正点：音声ファイル受信後に、現在の音声状態を再確認
                if (!this.audioEnabled) {
                    console.log('🔇 音声生成完了後に停止が指示されたため、再生をキャンセルします。');
                    return; // 再生せずに処理を終了
                }
                // ★★★★★★★★★★★★★★★★★★★★★★★★★★★★★
                
                if (data.success && data.audio_url) {
                    console.log('🎵 音声再生開始:', data.audio_url);
                    console.log('🎵 音声URLの形式:', typeof data.audio_url, '長さ:', data.audio_url.length);
                    this.playAudio(data.audio_url);
                } else {
                    console.log('⚠️ 音声生成に失敗、ブラウザ音声合成を使用');
                    console.log('⚠️ 失敗理由 - success:', data.success, 'audio_url存在:', !!data.audio_url);
                    this.fallbackSpeechSynthesis(text);
                }
            } else {
                console.log('⚠️ TTS APIエラー、ブラウザ音声合成を使用');
                console.log('⚠️ HTTPステータス:', response.status, response.statusText);
                this.fallbackSpeechSynthesis(text);
            }
        } catch (error) {
            console.error('❌ 音声生成エラー:', error);
            console.log('⚠️ ブラウザ音声合成を使用');
            this.fallbackSpeechSynthesis(text);
        }
    }
    
    playAudio(audioUrl) {
        // 音声再生開始前に停止状態をチェック
        if (!this.audioEnabled) {
            console.log('🔇 音声再生開始時に停止されたため、再生をキャンセル');
            return;
        }
        
        // 既存の音声を停止
        if (this.currentAudio) {
            this.currentAudio.pause();
            this.currentAudio.currentTime = 0;
        }
        
        const audio = new Audio(audioUrl);
        this.currentAudio = audio; // 現在の音声を保持
        
        audio.onloadstart = () => console.log('🎵 音声読み込み開始');
        audio.oncanplay = () => console.log('🎵 音声再生可能');
        audio.onloadeddata = () => console.log('🎵 音声データ読み込み完了');
        audio.oncanplaythrough = () => console.log('🎵 音声バッファリング完了');
        audio.onwaiting = () => console.log('🎵 音声バッファリング中...');
        audio.onstalled = () => console.log('⚠️ 音声読み込みが停止しました');
        audio.onsuspend = () => console.log('⚠️ 音声読み込みが中断されました');
        audio.onplay = () => {
            console.log('🎵 音声再生開始');
            this.isReading = true;
            this.updateReadAloudButton();
            // 音声再生開始時にボタンを再有効化
            this.setReadAloudButtonEnabled(true);
            
            // 音声の進行状況を監視
            this.startAudioProgressMonitoring(audio);
        };
        audio.onended = () => {
            console.log('🎵 音声再生終了');
            this.isReading = false;
            this.currentAudio = null;
            this.updateReadAloudButton();
            // 音声再生終了時にボタンを再有効化
            this.setReadAloudButtonEnabled(true);
        };
        audio.onerror = (e) => {
            console.error('❌ 音声再生エラー:', e);
            console.error('❌ エラー詳細:', {
                error: e,
                networkState: audio.networkState,
                readyState: audio.readyState,
                src: audio.src,
                currentTime: audio.currentTime,
                duration: audio.duration
            });
            console.log('⚠️ ブラウザ音声合成を使用');
            this.isReading = false;
            this.currentAudio = null;
            this.updateReadAloudButton();
            // エラー時もボタンを再有効化
            this.setReadAloudButtonEnabled(true);
        };
        audio.onpause = () => {
            console.log('🎵 音声一時停止');
            this.isReading = false;
            this.updateReadAloudButton();
            // 一時停止時もボタンを再有効化
            this.setReadAloudButtonEnabled(true);
        };
        
        audio.play().catch(error => {
            console.error('❌ 音声再生失敗:', error);
            console.log('⚠️ ブラウザ音声合成を使用');
            this.isReading = false;
            this.currentAudio = null;
            this.updateReadAloudButton();
            // 再生失敗時もボタンを再有効化
            this.setReadAloudButtonEnabled(true);
        });
    }
    
    fallbackSpeechSynthesis(text) {
        // 音声合成開始前に停止状態をチェック
        if (!this.audioEnabled) {
            console.log('🔇 音声合成開始時に停止されたため、合成をキャンセル');
            return;
        }
        
        // ブラウザの音声合成APIを使用（フォールバック）
        if (this.speechSynthesis && !this.isReading) {
            console.log('🎤 ブラウザ音声合成を使用（フォールバック）');
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.lang = 'ja-JP';
            utterance.rate = 0.8;
            utterance.pitch = 1.2;
            
            utterance.onend = () => {
                console.log('🎤 ブラウザ音声合成終了');
                this.isReading = false;
                this.updateReadAloudButton();
                // ブラウザ音声合成終了時にボタンを再有効化
                this.setReadAloudButtonEnabled(true);
            };
            
            utterance.onerror = (event) => {
                console.error('❌ ブラウザ音声合成エラー:', event);
                this.isReading = false;
                this.updateReadAloudButton();
                // エラー時もボタンを再有効化
                this.setReadAloudButtonEnabled(true);
            };
            
            this.speechSynthesis.speak(utterance);
            this.isReading = true;
            this.updateReadAloudButton();
            // ブラウザ音声合成開始時にボタンを再有効化
            this.setReadAloudButtonEnabled(true);
        } else if (this.isReading) {
            console.log('⚠️ 既に読み上げ中のため、ブラウザ音声合成をスキップ');
        }
    }

    toggleReadAloud() {
        console.log('🔍 StoryAgent.toggleReadAloud が呼び出されました');
        console.log('🔍 現在の状態:', {
            isReading: this.isReading,
            audioEnabled: this.audioEnabled,
            currentPageRead: this.currentPageRead
        });
        console.trace();
        
        // ボタンを一時的に無効化（連続押し防止）
        this.setReadAloudButtonEnabled(false);
        
        if (this.isReading) {
            // 音声を停止する場合
            console.log('🔇 読み上げ停止ボタンが押されました');
            this.stopReading();
            this.audioEnabled = false; // 音声を無効にする
            
            // 停止処理完了後にボタンを再有効化（タイミングを調整）
            setTimeout(() => {
                this.setReadAloudButtonEnabled(true);
                console.log('🔘 停止処理完了 - ボタンを再有効化');
            }, 1000); // 500ms → 1000msに変更
        } else {
            // 音声を開始/再開する場合
            const storyText = document.getElementById('story-text').textContent;
            if (storyText) {
                console.log('🎤 読み上げ開始/再開ボタンが押されました');
                this.audioEnabled = true; // 音声を有効にする
                this.currentPageRead = false; // 読み上げ済みフラグをリセット（再開のため）
                this.readStoryText(storyText);
                this.currentPageRead = true; // 読み上げ開始後にフラグを設定
                
                // 読み上げ開始処理完了後にボタンを再有効化
                setTimeout(() => {
                    this.setReadAloudButtonEnabled(true);
                }, 1000);
            } else {
                // テキストがない場合は即座にボタンを再有効化
                this.setReadAloudButtonEnabled(true);
            }
        }
        this.updateReadAloudButton();
    }

    stopReading() {
        console.log('🔇 読み上げ停止処理開始 - isReading:', this.isReading, 'currentAudio:', !!this.currentAudio, 'audioEnabled:', this.audioEnabled);
        
        // まず読み上げ状態をfalseに設定（重複実行を防ぐ）
        this.isReading = false;
        
        // ブラウザ音声合成を停止（複数回実行して確実に停止）
        if (this.speechSynthesis) {
            this.speechSynthesis.cancel();
            this.speechSynthesis.cancel(); // 念のため2回実行
            console.log('🔇 ブラウザ音声合成を停止');
        }
        
        // 現在再生中の音声ファイルを停止
        if (this.currentAudio) {
            this.currentAudio.pause();
            this.currentAudio.currentTime = 0;
            this.currentAudio = null;
            console.log('🔇 音声ファイルを停止');
        }
        
        // ボタン表示を更新
        this.updateReadAloudButton();
        console.log('🔇 読み上げを停止しました');
        console.log('🔍 停止後の状態:', {
            audioEnabled: this.audioEnabled,
            currentPageRead: this.currentPageRead,
            isReading: this.isReading
        });
    }

    updateReadAloudButton() {
        const button = document.getElementById('read-aloud-btn');
        const icon = button.querySelector('.icon');
        if (this.isReading) {
            icon.textContent = '⏹️';
            button.querySelector('span:last-child').textContent = '停止';
        } else {
            icon.textContent = '🔊';
            button.querySelector('span:last-child').textContent = '読み上げ';
        }
    }

    setReadAloudButtonEnabled(enabled) {
        const button = document.getElementById('read-aloud-btn');
        if (button) {
            button.disabled = !enabled;
            button.style.opacity = enabled ? '1' : '0.5';
            button.style.cursor = enabled ? 'pointer' : 'not-allowed';
            console.log('🔘 読み上げボタンの状態を変更:', enabled ? '有効' : '無効');
        }
    }

    startAudioProgressMonitoring(audio) {
        // 音声進行状況の監視は不要（現在の問題とは関係ないため）
        // 必要に応じて後で再有効化可能
    }

    newStory() {
        // 新しいお話選択ページに戻る
        this.speechSynthesis.cancel();
        this.isReading = false;
        this.lastImageUrl = null; // 画像URLをクリア
        
        window.location.href = '/src/story_top.html';
    }

    showError(message) {
        this.isLoading = false;
        document.getElementById('loading-section').classList.add('hidden');
        alert(message); // 実際の実装では、より良いエラー表示を使用
    }
}

// Global functions for onclick handlers
function goHome() {
    window.location.href = '/src/story_top.html';
}

function startStory(storyType) {
    storyAgent.startStory(storyType);
}

function newStory() {
    if (typeof storyAgent !== 'undefined') {
        storyAgent.newStory();
    }
}

function toggleReadAloud() {
    console.log('🔍 グローバル関数 toggleReadAloud が呼び出されました');
    console.trace();
    if (typeof storyAgent !== 'undefined') {
        storyAgent.toggleReadAloud();
    }
}

// Initialize the story agent when the page loads
let storyAgent;
document.addEventListener('DOMContentLoaded', () => {
    storyAgent = new StoryAgent();
});

// Smooth scrolling for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Add some interactive animations
document.addEventListener('DOMContentLoaded', () => {
    // Add floating animation to cards on hover
    document.querySelectorAll('.story-type-btn').forEach(btn => {
        btn.addEventListener('mouseenter', () => {
            btn.style.transform = 'translateY(-5px) scale(1.02)';
        });
        
        btn.addEventListener('mouseleave', () => {
            btn.style.transform = 'translateY(0) scale(1)';
        });
    });
    
    // Rabbit interaction
    const rabbit = document.querySelector('.rabbit-character');
    if (rabbit) {
        rabbit.addEventListener('click', () => {
            rabbit.style.animation = 'bounce 0.6s ease-in-out';
            setTimeout(() => {
                rabbit.style.animation = 'float 3s ease-in-out infinite';
            }, 600);
            
            // Change the speech bubble message
            const speechBubble = document.getElementById('rabbit-message');
            const messages = [
                "わーい！クリックしてくれてありがとう！",
                "一緒に楽しいお話を読もうね！",
                "今日はどんな冒険をしようかな？",
                "きみはとっても優しいね！"
            ];
            speechBubble.textContent = messages[Math.floor(Math.random() * messages.length)];
        });
    }
});
