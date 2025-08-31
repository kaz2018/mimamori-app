// Story Agent JavaScript Functions
class StoryAgent {
    constructor() {
        this.currentSession = null;
        this.isLoading = false;
        this.speechSynthesis = window.speechSynthesis;
        this.isReading = false;
        this.apiBaseUrl = window.location.origin; // ADK APIのベースURL
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
        this.showLoading();
        
        try {
            // ADKエージェントとの通信をシミュレート
            const response = await this.callStoryAgent(storyType);
            this.displayStory(response);
        } catch (error) {
            console.error('Story generation failed:', error);
            this.showError('お話の準備に失敗しました。もう一度お試しください。');
        }
    }

    async callStoryAgent(storyType) {
        try {
            console.log(`ADKエージェントを呼び出し中: ${storyType}`);
            
            const response = await fetch(`${this.apiBaseUrl}/agent/storytelling`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    input: `${storyType}の読み聞かせを始めてください。インタラクティブなお話をお願いします。`
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            console.log('ADKエージェント応答:', data);
            
            // ADKエージェントからの応答を解析して選択肢を抽出
            const parsedStory = this.parseStoryResponse(data.result);
            
            // 画像URLがあれば保存
            this.extractAndSaveImageUrl(data.result);
            
            return {
                text: parsedStory.text || `${storyType}のお話を始めましょう。`,
                choices: parsedStory.choices || [
                    "物語を続ける",
                    "別の選択をする"
                ],
                image: null
            };
            
        } catch (error) {
            console.error('ADKエージェント呼び出しエラー:', error);
            
            // エラー時のフォールバック（デモ用）
            return {
                text: `ADKエージェントに接続中です...\n\n（デモモード）\nわーい！${storyType}、いいね！\n\nむかしむかし、深い森の奥に、ちっちゃなウサギさんが住んでいました。名前は「ふわふわ」。\n\nある日、ふわふわは森の奥から聞こえてくる、美しい歌声に気づきました。\n\nさて、ふわふわはどうするかな？`,
                choices: [
                    "歌声のする方へ、勇気を出して進んでみる！",
                    "やっぱりちょっと怖いから、いつものお気に入りの場所で遊ぶ！"
                ],
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
        if (hasImage) {
            // 画像URL行を除去
            storyText = storyText.replace(/画像URL:\s*https:\/\/[^\s\n]+/g, '');
            // Markdown画像を除去
            storyText = storyText.replace(/!\[ハッピーエンド\]\([^)]+\)/g, '');
            // 画像関連の説明文を除去
            storyText = storyText.replace(/素敵な絵ができたよ！見てみて！\s*/g, '');
            storyText = storyText.replace(/わあ！見て！これが.*?絵だよ！\s*/g, '');
            // 余分な改行を整理
            storyText = storyText.replace(/\n\s*\n\s*\n/g, '\n\n').trim();
        }

        // 画像がある場合や物語が終了している場合の特別な選択肢
        let finalChoices = choices;
        if (hasImage || responseText.includes('おしまい') || responseText.includes('めでたし') || choices.length === 0) {
            finalChoices = [
                "🖼️ 生成された画像を見る",
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
        this.isLoading = false;
        document.getElementById('loading-section').classList.add('hidden');
        document.getElementById('story-section').classList.remove('hidden');
        
        // ストーリーテキストを表示
        document.getElementById('story-text').textContent = storyData.text;
        
        // 選択肢を表示
        this.displayChoices(storyData.choices);
        
        // 画像があれば表示
        if (storyData.image) {
            this.displayImage(storyData.image);
        }
        
        // 自動読み上げ（オプション）
        this.readStoryText(storyData.text);
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

    displayImage(imageUrl) {
        const imageContainer = document.getElementById('story-image');
        imageContainer.innerHTML = `
            <img src="${imageUrl}" alt="物語の絵" loading="lazy">
            <p>素敵な絵ができました！</p>
        `;
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
        
        this.showLoading();
        
        try {
            // 選択した内容を次のストーリーに送信
            const response = await this.sendChoice(choice, index);
            this.displayStory(response);
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
                    input: `ユーザーの選択: ${choice}。この選択に基づいて物語を続けてください。`
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            console.log('ADKエージェント応答（選択肢）:', data);
            
            // ADKエージェントからの応答を解析して選択肢を抽出
            const parsedStory = this.parseStoryResponse(data.result);
            
            // 画像URLがあれば保存
            this.extractAndSaveImageUrl(data.result);
            
            return {
                text: parsedStory.text || '物語が続きます...',
                choices: parsedStory.choices || [
                    "さらに物語を続ける",
                    "別の選択をする"
                ],
                image: null
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
        if (this.speechSynthesis && !this.isReading) {
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.lang = 'ja-JP';
            utterance.rate = 0.8;
            utterance.pitch = 1.2;
            
            utterance.onend = () => {
                this.isReading = false;
                this.updateReadAloudButton();
            };
            
            this.speechSynthesis.speak(utterance);
            this.isReading = true;
            this.updateReadAloudButton();
        }
    }

    toggleReadAloud() {
        if (this.isReading) {
            this.speechSynthesis.cancel();
            this.isReading = false;
        } else {
            const storyText = document.getElementById('story-text').textContent;
            if (storyText) {
                this.readStoryText(storyText);
            }
        }
        this.updateReadAloudButton();
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

    newStory() {
        // 新しいお話選択ページに戻る
        this.speechSynthesis.cancel();
        this.isReading = false;
        this.lastImageUrl = null; // 画像URLをクリア
        
        window.location.href = 'story_top.html';
    }

    showError(message) {
        this.isLoading = false;
        document.getElementById('loading-section').classList.add('hidden');
        alert(message); // 実際の実装では、より良いエラー表示を使用
    }
}

// Global functions for onclick handlers
function goHome() {
    window.location.href = 'story_top.html';
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
