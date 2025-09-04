"""
子供見守りアプリ用ツール
音声対話、ゲーム、読み聞かせ、安全監視、記憶機能を提供
"""

import json
import random
import time
from typing import Dict, Any, List
from google.adk.tools import FunctionTool

# ==================== 音声対話ツール ====================

def voice_interaction(message: str, child_age: int = 4) -> Dict[str, Any]:
    """
    子供との音声対話を処理するツール
    
    Args:
        message: 子供からの音声メッセージ
        child_age: 子供の年齢（デフォルト: 4歳）
    
    Returns:
        対話結果
    """
    try:
        # 年齢に応じた応答スタイルの調整
        if child_age <= 3:
            response_style = "simple"
        elif child_age <= 5:
            response_style = "friendly"
        else:
            response_style = "normal"
        
        # 音声認識の精度向上（子供の発音を考慮）
        processed_message = _process_child_speech(message)
        
        # 感情分析
        emotion = _analyze_child_emotion(processed_message)
        
        # 適切な応答生成
        response = _generate_age_appropriate_response(processed_message, emotion, response_style)
        
        return {
            "success": True,
            "original_message": message,
            "processed_message": processed_message,
            "emotion": emotion,
            "response": response,
            "response_style": response_style,
            "timestamp": time.time()
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"音声対話処理エラー: {str(e)}",
            "fallback_response": "ごめんね、よく聞こえなかったよ。もう一度言ってくれるかな？"
        }

def _process_child_speech(message: str) -> str:
    """子供の発音を考慮した音声処理"""
    # 子供特有の発音パターンを修正
    corrections = {
        "わんわん": "ワンワン",
        "にゃんにゃん": "ニャンニャン",
        "ちゅうちゅう": "チュウチュウ",
        "ぴよぴよ": "ピヨピヨ"
    }
    
    processed = message
    for child_word, correct_word in corrections.items():
        processed = processed.replace(child_word, correct_word)
    
    return processed

def _analyze_child_emotion(message: str) -> str:
    """子供の感情を分析"""
    happy_words = ["たのしい", "うれしい", "わくわく", "すごい", "やった"]
    sad_words = ["かなしい", "こわい", "つかれた", "いやだ", "だめ"]
    excited_words = ["やったー", "すごい", "わくわく", "ドキドキ"]
    
    message_lower = message.lower()
    
    if any(word in message_lower for word in happy_words):
        return "happy"
    elif any(word in message_lower for word in sad_words):
        return "sad"
    elif any(word in message_lower for word in excited_words):
        return "excited"
    else:
        return "neutral"

def _generate_age_appropriate_response(message: str, emotion: str, style: str) -> str:
    """年齢に適した応答を生成"""
    if style == "simple":
        responses = {
            "happy": ["うれしいね！", "すごいね！", "やったね！"],
            "sad": ["大丈夫？", "だいじょうぶ？", "うさぎさんがいるよ"],
            "excited": ["わくわくするね！", "すごい！", "やったー！"],
            "neutral": ["そうなんだ", "うんうん", "わかった"]
        }
    else:  # friendly
        responses = {
            "happy": ["うれしい！うさぎさんも一緒に楽しくなっちゃった！", "すごいね！もっと教えて！", "やったね！うさぎさんも応援してるよ！"],
            "sad": ["大丈夫？うさぎさんが元気をくれるよ！", "だいじょうぶ？一緒に考えようね", "うさぎさんがいるよ。何かあった？"],
            "excited": ["わくわくするね！何がそんなに楽しいの？", "すごい！うさぎさんも知りたいな！", "やったー！うさぎさんも一緒に喜んでるよ！"],
            "neutral": ["そうなんだ！うさぎさんも知りたいな", "うんうん、うさぎさんも聞いてるよ", "わかった！うさぎさんも一緒に考えてみるね"]
        }
    
    return random.choice(responses.get(emotion, responses["neutral"]))

# ==================== ゲームツール ====================

def game_tool(game_type: str, child_age: int = 4, difficulty: str = "easy") -> Dict[str, Any]:
    """
    子供向けゲームを提供するツール
    
    Args:
        game_type: ゲームの種類（しりとり、なぞなぞ、歌・ダンス）
        child_age: 子供の年齢
        difficulty: 難易度
    
    Returns:
        ゲーム結果
    """
    try:
        if game_type == "しりとり":
            return _play_shiritori(child_age, difficulty)
        elif game_type == "なぞなぞ":
            return _play_riddle(child_age, difficulty)
        elif game_type == "歌・ダンス":
            return _play_song_dance(child_age, difficulty)
        else:
            return {
                "success": False,
                "error": f"未対応のゲームタイプ: {game_type}",
                "available_games": ["しりとり", "なぞなぞ", "歌・ダンス"]
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": f"ゲーム実行エラー: {str(e)}",
            "fallback_response": "ゲームでエラーが起きたよ。もう一度やってみよう！"
        }

def _play_shiritori(child_age: int, difficulty: str) -> Dict[str, Any]:
    """しりとりゲーム"""
    # 年齢に応じた単語リスト
    if child_age <= 4:
        words = ["りんご", "ごりら", "らくだ", "だんご", "ごま", "まくら", "らっこ", "こま", "まつ", "つき"]
    else:
        words = ["りんご", "ごりら", "らくだ", "だんご", "ごま", "まくら", "らっこ", "こま", "まつ", "つき", "きつね", "ねこ"]
    
    current_word = random.choice(words)
    next_letter = current_word[-1]
    
    return {
        "success": True,
        "game_type": "しりとり",
        "current_word": current_word,
        "next_letter": next_letter,
        "instruction": f"「{current_word}」で終わったよ！「{next_letter}」で始まる言葉を言ってね！",
        "hint": f"ヒント：「{next_letter}」で始まる動物や食べ物を考えてみて！",
        "score": 0,
        "max_score": 10
    }

def _play_riddle(child_age: int, difficulty: str) -> Dict[str, Any]:
    """なぞなぞゲーム"""
    # 年齢に応じたなぞなぞ
    riddles = {
        "easy": [
            {
                "question": "りんごは赤い、バナナは何色？",
                "answer": "黄色",
                "hint": "太陽と同じ色だよ！"
            },
            {
                "question": "空を飛ぶ鳥、何の鳥？",
                "answer": "とり",
                "hint": "「とり」という名前の鳥だよ！"
            },
            {
                "question": "お昼に食べるごはん、何という？",
                "answer": "昼ごはん",
                "hint": "お昼のごはんだよ！"
            }
        ]
    }
    
    riddle = random.choice(riddles[difficulty])
    
    return {
        "success": True,
        "game_type": "なぞなぞ",
        "question": riddle["question"],
        "answer": riddle["answer"],
        "hint": riddle["hint"],
        "instruction": "なぞなぞに答えてね！",
        "score": 0,
        "max_score": 5
    }

def _play_song_dance(child_age: int, difficulty: str) -> Dict[str, Any]:
    """歌・ダンスゲーム"""
    songs = [
        {
            "title": "うさぎのダンス",
            "lyrics": "うさぎさん うさぎさん ぴょんぴょんぴょん",
            "dance_move": "ぴょんぴょんジャンプ",
            "duration": 30
        },
        {
            "title": "森のコンサート",
            "lyrics": "森の動物たち みんなで歌おう",
            "dance_move": "手を振って踊ろう",
            "duration": 45
        },
        {
            "title": "星の歌",
            "lyrics": "きらきら星 きらきら光る",
            "dance_move": "手で星を作って踊ろう",
            "duration": 60
        }
    ]
    
    song = random.choice(songs)
    
    return {
        "success": True,
        "game_type": "歌・ダンス",
        "title": song["title"],
        "lyrics": song["lyrics"],
        "dance_move": song["dance_move"],
        "duration": song["duration"],
        "instruction": f"「{song['title']}」を歌って踊ろう！",
        "score": 0,
        "max_score": 100
    }

# ==================== 読み聞かせツール ====================

def story_telling_tool(story_type: str = "random", child_age: int = 4, duration: int = 5) -> Dict[str, Any]:
    """
    子供向け読み聞かせを提供するツール
    
    Args:
        story_type: ストーリーの種類
        child_age: 子供の年齢
        duration: 読み聞かせ時間（分）
    
    Returns:
        読み聞かせ結果
    """
    try:
        stories = {
            "うさぎの冒険": {
                "title": "うさぎの冒険",
                "content": """
                むかしむかし、ピンクのうさぎが森に住んでいました。
                うさぎは毎日、森の友達と楽しく遊んでいました。
                ある日、うさぎは新しい友達を見つけたいと思いました。
                森の奥へ行くと、小さなリスが泣いていました。
                「どうしたの？」とうさぎが聞くと、
                「お母さんとはぐれちゃった」とリスが答えました。
                うさぎはリスと一緒にお母さんを探しました。
                そして、無事にお母さんを見つけることができました。
                リスは「ありがとう！」と言って、うさぎと友達になりました。
                うさぎは新しい友達ができて、とてもうれしかったです。
                """,
                "moral": "友達を助けることは素晴らしいことだよ",
                "age_appropriate": True,
                "duration": 3
            },
            "魔法の森": {
                "title": "魔法の森",
                "content": """
                森の奥に、魔法の森がありました。
                そこには、魔法を使える動物たちが住んでいました。
                ある日、森に大きな嵐が来ました。
                動物たちは怖がって、みんな隠れてしまいました。
                でも、小さなうさぎは勇気を出して、
                魔法の力で嵐を止めようとしました。
                うさぎの魔法で、嵐はやみました。
                動物たちは「ありがとう！」と言って、
                うさぎを森のヒーローにしました。
                うさぎは「みんなで力を合わせれば、何でもできるね」と言いました。
                """,
                "moral": "勇気と友達の力で、どんな困難も乗り越えられるよ",
                "age_appropriate": True,
                "duration": 4
            },
            "宇宙旅行": {
                "title": "宇宙旅行",
                "content": """
                うさぎは宇宙に行ってみたいと思いました。
                ある夜、星がうさぎに話しかけました。
                「一緒に宇宙旅行に行こう！」
                うさぎは星と一緒に宇宙船に乗りました。
                宇宙では、月や他の星たちが待っていました。
                うさぎは宇宙の美しさに感動しました。
                地球に帰ってきたうさぎは、
                みんなに宇宙の話をしました。
                みんなは「すごいね！」と言って、
                うさぎの冒険を聞いてくれました。
                うさぎは「夢は叶うんだね」と思いました。
                """,
                "moral": "夢を持って挑戦することは素晴らしいよ",
                "age_appropriate": True,
                "duration": 5
            }
        }
        
        if story_type == "random":
            story_key = random.choice(list(stories.keys()))
        else:
            story_key = story_type if story_type in stories else "うさぎの冒険"
        
        story = stories[story_key]
        
        return {
            "success": True,
            "title": story["title"],
            "content": story["content"].strip(),
            "moral": story["moral"],
            "duration": story["duration"],
            "age_appropriate": story["age_appropriate"],
            "instruction": f"「{story['title']}」を読むよ。静かに聞いてね！",
            "engagement_score": random.randint(80, 100)
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"読み聞かせエラー: {str(e)}",
            "fallback_response": "読み聞かせでエラーが起きたよ。もう一度やってみよう！"
        }

# ==================== 安全監視ツール ====================

def safety_monitor_tool(child_activity: str, session_duration: int, energy_level: int) -> Dict[str, Any]:
    """
    子供の安全を監視するツール
    
    Args:
        child_activity: 子供の現在の活動
        session_duration: セッション時間（分）
        energy_level: エネルギーレベル（0-100）
    
    Returns:
        安全監視結果
    """
    try:
        warnings = []
        recommendations = []
        
        # セッション時間チェック
        if session_duration > 30:
            warnings.append("長時間の使用です。休憩を取ることをお勧めします。")
            recommendations.append("15分休憩を取ってから再開しましょう")
        
        # エネルギーレベルチェック
        if energy_level < 30:
            warnings.append("エネルギーが低いです。休憩が必要かもしれません。")
            recommendations.append("お水を飲んだり、トイレに行ったりしましょう")
        
        # 活動内容チェック
        if "ゲーム" in child_activity and session_duration > 20:
            warnings.append("ゲームを長時間続けています。他の活動もしてみましょう。")
            recommendations.append("読み聞かせや歌を歌うのも楽しいよ！")
        
        # 安全レベル判定
        if len(warnings) == 0:
            safety_level = "safe"
            status = "安全です"
        elif len(warnings) == 1:
            safety_level = "caution"
            status = "注意が必要です"
        else:
            safety_level = "warning"
            status = "休憩を推奨します"
        
        return {
            "success": True,
            "safety_level": safety_level,
            "status": status,
            "warnings": warnings,
            "recommendations": recommendations,
            "session_duration": session_duration,
            "energy_level": energy_level,
            "current_activity": child_activity,
            "timestamp": time.time()
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"安全監視エラー: {str(e)}",
            "fallback_response": "安全監視でエラーが起きました。"
        }

# ==================== 記憶ツール ====================

def memory_tool(action: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    子供の活動記録を管理するツール
    
    Args:
        action: アクション（save, load, update, clear）
        data: 保存するデータ
    
    Returns:
        記憶操作結果
    """
    try:
        # 簡易的なメモリシステム（実際の実装ではデータベースを使用）
        memory_file = "child_memory.json"
        
        if action == "save":
            if data:
                with open(memory_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                return {
                    "success": True,
                    "action": "save",
                    "message": "記憶を保存しました",
                    "data_saved": data
                }
            else:
                return {
                    "success": False,
                    "error": "保存するデータがありません"
                }
        
        elif action == "load":
            try:
                with open(memory_file, 'r', encoding='utf-8') as f:
                    memory_data = json.load(f)
                return {
                    "success": True,
                    "action": "load",
                    "memory_data": memory_data
                }
            except FileNotFoundError:
                return {
                    "success": True,
                    "action": "load",
                    "memory_data": {},
                    "message": "記憶ファイルが見つかりません。新しい記憶を開始します。"
                }
        
        elif action == "update":
            try:
                with open(memory_file, 'r', encoding='utf-8') as f:
                    memory_data = json.load(f)
            except FileNotFoundError:
                memory_data = {}
            
            if data:
                memory_data.update(data)
                with open(memory_file, 'w', encoding='utf-8') as f:
                    json.dump(memory_data, f, ensure_ascii=False, indent=2)
                return {
                    "success": True,
                    "action": "update",
                    "message": "記憶を更新しました",
                    "updated_data": data
                }
            else:
                return {
                    "success": False,
                    "error": "更新するデータがありません"
                }
        
        elif action == "clear":
            try:
                import os
                os.remove(memory_file)
                return {
                    "success": True,
                    "action": "clear",
                    "message": "記憶をクリアしました"
                }
            except FileNotFoundError:
                return {
                    "success": True,
                    "action": "clear",
                    "message": "記憶ファイルは既に存在しません"
                }
        
        else:
            return {
                "success": False,
                "error": f"未対応のアクション: {action}",
                "supported_actions": ["save", "load", "update", "clear"]
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": f"記憶操作エラー: {str(e)}"
        }

# ==================== ツールの登録 ====================

# FunctionToolとしてツールを登録
voice_interaction_tool = FunctionTool(func=voice_interaction)
game_tool = FunctionTool(func=game_tool)
story_telling_tool = FunctionTool(func=story_telling_tool)
safety_monitor_tool = FunctionTool(func=safety_monitor_tool)
memory_tool = FunctionTool(func=memory_tool)
