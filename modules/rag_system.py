import os
import json
import importlib
import traceback
import time

# 環境変数をロード
from dotenv import load_dotenv
load_dotenv()

# 必要なライブラリをインポート
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter

# ChromaDB関連のエラーを回避
import chromadb
from chromadb.config import Settings

from openai import OpenAI
import random
import re
from datetime import datetime
from collections import deque, defaultdict
from typing import List, Dict, Optional, Tuple

# 🎯 新規追加:static_qa_dataからの多言語対応関数を動的インポート(AWS環境対応)
def _import_static_qa_functions():
    """static_qa_data の関数をインポート(ローカル環境対応)"""
    import sys
    import os
    
    try:
        # 方法1: 直接インポート
        from modules.static_qa_data import (
            get_static_response_multilang, 
            get_staged_response_multilang, 
            get_staged_suggestions_multilang,
            get_current_stage
        )
        print("[DEBUG] Static QA functions imported successfully")
        return get_static_response_multilang, get_staged_response_multilang, get_staged_suggestions_multilang, get_current_stage
    except ImportError as e1:
        print(f"[DEBUG] Direct import failed: {e1}")
        
        try:
            # 方法2: パスを追加してインポート
            current_dir = os.path.dirname(os.path.abspath(__file__))
            if current_dir not in sys.path:
                sys.path.insert(0, current_dir)
            
            from static_qa_data import (
                get_static_response_multilang, 
                get_staged_response_multilang, 
                get_staged_suggestions_multilang,
                get_current_stage
            )
            print("[DEBUG] Static QA functions imported with path adjustment")
            return get_static_response_multilang, get_staged_response_multilang, get_staged_suggestions_multilang, get_current_stage
        except ImportError as e2:
            print(f"[DEBUG] Path-adjusted import failed: {e2}")
            
            # 方法3: フォールバック関数を定義
            print("[WARNING] Static QA functions could not be imported")
            
            def get_static_response_multilang(query, language='ja'):
                """フォールバック:静的レスポンス(簡易版)"""
                return None
                
            def get_staged_response_multilang(query, language='ja', stage=None):
                """フォールバック:段階別レスポンス(簡易版)"""
                return None
                
            def get_staged_suggestions_multilang(stage, language='ja', selected_suggestions=[]):
                """フォールバック:サジェスション(簡易版)"""
                if language == 'ja':
                    return ["京セラについて教えて", "どんな製品を作っていますか?", "リサーチセンターについて説明してください"]
                else:
                    return ["Tell me about KYOCERA", "What kind of products do you create?", "Explain the Research Center"]
            
            def get_current_stage(selected_count):
                """フォールバック:段階判定(簡易版)"""
                if selected_count <= 3:
                    return 'stage1_overview'
                elif selected_count <= 7:
                    return 'stage2_technical'
                else:
                    return 'stage3_personal'
            
            print("[WARNING] Using fallback functions for static QA")
            return get_static_response_multilang, get_staged_response_multilang, get_staged_suggestions_multilang, get_current_stage

# ファイルロックの代替実装(Windows対応)
import threading
_db_creation_lock = threading.Lock()

class RAGSystem:
    def __init__(self, persist_directory=None):
        # 環境変数からデータベースパスを取得
        if persist_directory is None:
            persist_directory = os.getenv('CHROMA_DB_PATH', 'data/chroma_db')
        self.persist_directory = persist_directory
        
        self.embeddings = OpenAIEmbeddings()
        self.openai_client = OpenAI()
        
        # 🔧 DBインスタンスを明示的に初期化
        self.db = None
        
        # 🎯 static_qa_data関数を初期化
        try:
            result = _import_static_qa_functions()
            if result and len(result) == 4:
                self.get_static_response_multilang, self.get_staged_response_multilang, self.get_staged_suggestions_multilang, self.get_current_stage = result
                print("✅ Static QA functions initialized successfully")
            else:
                print(f"❌ Unexpected return value from _import_static_qa_functions: {result}")
                raise ValueError("Invalid return value")
        except Exception as e:
            print(f"❌ Failed to initialize static QA functions: {e}")
            # フォールバック関数を設定
            self.get_static_response_multilang = lambda query, language='ja': None
            self.get_staged_response_multilang = lambda query, language='ja', stage=None: None
            self.get_staged_suggestions_multilang = lambda stage, language='ja', selected_suggestions=[]: []
            self.get_current_stage = lambda selected_count: 'stage1_overview'
        
        # Supabaseは削除(不要)
        self.supabase = None  # 互換性のため
        
        # 🎯 【Live2D対応】9種類の感情に対応した感情履歴管理システム
        self.emotion_history = deque(maxlen=10)  # 最新10個の感情を記録
        self.emotion_transitions = {
            'happy': {
                'happy': 0.5,     # 同じ感情を維持しやすい
                'neutral': 0.3,
                'surprise': 0.15,
                'sad': 0.04,
                'angry': 0.01
            },
            'sad': {
                'sad': 0.4,
                'neutral': 0.4,
                'happy': 0.15,    # 励まされて元気になることも
                'angry': 0.04,
                'surprise': 0.01
            },
            'angry': {
                'angry': 0.3,
                'neutral': 0.5,   # 落ち着きやすい
                'sad': 0.15,
                'surprise': 0.04,
                'happy': 0.01
            },
            'surprise': {
                'surprise': 0.2,
                'happy': 0.3,
                'neutral': 0.3,
                'sad': 0.1,
                'angry': 0.1
            },
            'neutral': {
                'neutral': 0.4,
                'happy': 0.25,
                'surprise': 0.2,
                'sad': 0.1,
                'angry': 0.05
            },
            # 【Live2D新規追加】特殊感情の遷移確率
            'dangerquestion': {
                'neutral': 0.6,    # 冷静に対応
                'sad': 0.2,        # 困惑
                'angry': 0.15,     # 不快感
                'happy': 0.05      # 苦笑い
            },
            'neutraltalking': {
                'neutral': 0.5,    # 説明モード
                'happy': 0.3,      # 教える喜び
                'surprise': 0.15,  # 興味深い質問
                'sad': 0.05        # 難しい質問
            },
            'start': {
                'happy': 0.6,      # 初対面の喜び
                'neutral': 0.3,    # 通常モード
                'surprise': 0.1    # 予期せぬ出会い
            }
        }
        
        # 🎯 深層心理状態
        self.mental_states = {
            'energy_level': 80,        # 0-100: エネルギーレベル
            'stress_level': 20,        # 0-100: ストレスレベル
            'openness': 70,            # 0-100: 心の開放度
            'patience': 90,            # 0-100: 忍耐力
            'creativity': 85,          # 0-100: 創造性
            'loneliness': 30,          # 0-100: 寂しさ
            'work_satisfaction': 75,   # 0-100: 仕事の満足度
            'physical_fatigue': 20     # 0-100: 身体的疲労
        }
        
        # 🎯 時間帯別の気分変動
        self.time_based_mood = {
            'morning': {'energy': 0.9, 'patience': 1.1, 'creativity': 1.0},
            'afternoon': {'energy': 1.0, 'patience': 0.9, 'creativity': 1.2},
            'evening': {'energy': 0.7, 'patience': 0.8, 'creativity': 0.9},
            'night': {'energy': 0.5, 'patience': 0.7, 'creativity': 0.8}
        }
        
        # データベースの初期化(スレッドセーフ)
        self._initialize_database()
        
        # RAGの各種データ構造を初期化
        self.character_settings = {}
        self.knowledge_base = {}
        self.response_patterns = {}
        self.suggestion_templates = {}
    
    def _initialize_database(self):
        """データベースの初期化(スレッドセーフ)"""
        with _db_creation_lock:
            try:
                # 🔧 強制再構築フラグのチェック（本番環境対応）
                force_rebuild = os.getenv('FORCE_CHROMA_REBUILD', 'false').lower() == 'true'
                if force_rebuild:
                    print("🔄 FORCE_CHROMA_REBUILD=trueが検出されました。データベースを強制削除します...")
                    if os.path.exists(self.persist_directory):
                        import shutil
                        try:
                            shutil.rmtree(self.persist_directory)
                            print("✅ データベースディレクトリを削除しました")
                        except Exception as e:
                            print(f"⚠️ データベース削除エラー: {e}")
                    os.makedirs(self.persist_directory, exist_ok=True)
                    print("📁 新しいデータベースディレクトリを作成しました")
                
                # 永続化ディレクトリが存在するか確認
                if os.path.exists(self.persist_directory):
                    print(f"既存のデータベースを読み込み中: {self.persist_directory}")
                    try:
                        # Chromaクライアントの初期化
                        client = chromadb.PersistentClient(
                            path=self.persist_directory,
                            settings=Settings(
                                anonymized_telemetry=False,
                                allow_reset=True
                            )
                        )
                        
                        # 既存のコレクションを取得または作成
                        collection_name = "kyoyuzen_knowledge"
                        
                        try:
                            collection = client.get_collection(collection_name)
                            print(f"既存のコレクション '{collection_name}' を使用")
                        except:
                            collection = client.create_collection(collection_name)
                            print(f"新しいコレクション '{collection_name}' を作成")
                        
                        # LangChain用のChromaインスタンスを作成
                        self.db = Chroma(
                            client=client,
                            collection_name=collection_name,
                            embedding_function=self.embeddings,
                            persist_directory=self.persist_directory
                        )
                        
                        print("データベース読み込み成功")
                        
                    except Exception as e:
                        error_msg = str(e)
                        print(f"既存データベースの読み込みエラー: {error_msg}")
                        
                        # バージョン不整合エラーの場合は、古いDBを削除して再作成
                        if "no such column" in error_msg or "database disk image is malformed" in error_msg:
                            print("⚠️ ChromaDBバージョン不整合を検出。データベースを再構築します...")
                            import shutil
                            try:
                                shutil.rmtree(self.persist_directory)
                                print(f"✅ 古いデータベースを削除: {self.persist_directory}")
                            except Exception as rm_err:
                                print(f"⚠️ データベース削除エラー: {rm_err}")
                        
                        # 新規作成を試みる
                        self._create_new_database()
                else:
                    print("新規データベースを作成中...")
                    self._create_new_database()
                    
            except Exception as e:
                print(f"データベース初期化エラー: {e}")
                import traceback
                traceback.print_exc()
                self.db = None
    
    def _create_new_database(self):
        """新規データベースの作成"""
        try:
            os.makedirs(self.persist_directory, exist_ok=True)
            
            # 初期データを準備
            documents = []
            
            # uploadsディレクトリからファイルを読み込み
            uploads_dir = "uploads"
            if os.path.exists(uploads_dir):
                for filename in os.listdir(uploads_dir):
                    if filename.endswith(".txt"):
                        filepath = os.path.join(uploads_dir, filename)
                        try:
                            with open(filepath, "r", encoding="utf-8") as f:
                                content = f.read()
                                if content.strip():
                                    from langchain.schema import Document
                                    documents.append(Document(
                                        page_content=content,
                                        metadata={"source": filename}
                                    ))
                                    print(f"ファイル読み込み: {filename}")
                        except Exception as e:
                            print(f"ファイル読み込みエラー ({filename}): {e}")
                
                if documents:
                    # ベクトルDBを作成
                    self.db = Chroma.from_documents(
                        documents=documents,
                        embedding=self.embeddings,
                        persist_directory=self.persist_directory
                    )
                    
                    # 永続化
                    self.db.persist()
                    
                    print(f"{len(documents)}個のドキュメントをデータベースに追加しました")
                else:
                    print("uploadsディレクトリにファイルが見つかりません")
                    # フォールバック:ハードコードされた初期データ
                    self._add_default_data()
            else:
                print(f"uploadsディレクトリが見つかりません: {uploads_dir}")
                # フォールバック:ハードコードされた初期データ
                self._add_default_data()
            
            # データ構造の初期化
            self._load_all_knowledge()
            
        except Exception as e:
            print(f"データベース作成エラー: {e}")
            import traceback
            traceback.print_exc()
            # 🔧 修正: _initialize_database()で既にself.dbが作成されている場合があるため、
            # エラーが出ても既存のself.dbを保持する（Noneで上書きしない）
            if self.db is None:
                print("⚠️ データベースの作成に失敗しましたが、処理を続行します")
    
    def _add_default_data(self):
        """デフォルトの初期データを追加(フォールバック用)"""
        initial_knowledge = [
            {
                "text": "京セラは、稲盛和夫が1959年に創業したセラミック技術を核とする企業です。電子部品、半導体、通信機器、太陽光発電など幅広い事業を展開しています。",
                "metadata": {"source": "knowledge.txt", "category": "基本知識", "topic": "京セラ"}
            },
            {
                "text": "みなとみらいリサーチセンターは、オープンイノベーションの拠点として、スタートアップや研究者との協業を推進しています。",
                "metadata": {"source": "knowledge.txt", "category": "施設", "topic": "リサーチセンター"}
            },
            {
                "text": "私は京セラで研究員をしています。12歳の時から実験が好きで、結晶を作っていたら科学雑誌に載って、それがきっかけで研究者になりました。",
                "metadata": {"source": "personality.txt", "category": "個人", "topic": "経験"}
            },
            {
                "text": "京セラのセラミック技術は、スマホのカメラレンズカバーや人工関節など、身近な製品に使われています。",
                "metadata": {"source": "knowledge.txt", "category": "技術", "topic": "製品"}
            },
            {
                "text": "新しい技術や異業種の方との出会いが刺激になります。予想外の組み合わせから生まれるイノベーションが楽しいです。",
                "metadata": {"source": "personality.txt", "category": "個人", "topic": "やりがい"}
            }
        ]
        
        texts = [item["text"] for item in initial_knowledge]
        metadatas = [item["metadata"] for item in initial_knowledge]
        
        self.db.add_texts(texts=texts, metadatas=metadatas)
        print(f"{len(texts)}個のデフォルトデータを追加しました")
    
    def _load_all_knowledge(self):
        """すべてのナレッジを読み込んで整理"""
        if self.db is None:
            return
        
        self.character_settings = {}
        self.knowledge_base = {}
        self.response_patterns = {}
        self.suggestion_templates = {}
        
        try:
            # すべてのドキュメントを取得
            all_docs = self.db.similarity_search("", k=1000)  # 大量に取得
            
            for doc in all_docs:
                content = doc.page_content
                source = doc.metadata.get('source', '')
                
                print(f"処理中: {source}")
                
                # ファイル名から正確に分類
                source_lower = source.lower()
                
                if 'personality' in source_lower:
                    self._parse_character_settings(content)
                elif 'knowledge' in source_lower:
                    self._parse_knowledge(content)
                elif 'response' in source_lower:
                    self._parse_response_patterns(content)
                elif 'suggestion' in source_lower:
                    self._parse_suggestion_templates(content)
                else:
                    # 内容から判定(フォールバック)
                    self._classify_by_content(content)
            
            print("ナレッジの読み込み完了")
            print(f"- キャラクター設定: {len(self.character_settings)}項目")
            print(f"- 専門知識: {len(self.knowledge_base)}項目")
            print(f"- 応答パターン: {len(self.response_patterns)}項目")
            print(f"- サジェステンプレート: {len(self.suggestion_templates)}項目")
            
        except Exception as e:
            print(f"ナレッジ読み込みエラー: {e}")
            import traceback
            traceback.print_exc()
    
    def _classify_by_content(self, content):
        """内容に基づいてドキュメントを分類"""
        # キャラクター設定の特徴的なキーワード
        if any(keyword in content for keyword in ['性格', '話し方', '好きなこと', '嫌いなこと', '関西弁', 'あっちゃ']):
            self._parse_character_settings(content)
        # 専門知識の特徴的なキーワード
        elif any(keyword in content for keyword in ['京セラ', 'KYOCERA', 'セラミック', 'イノベーション', '研究', '技術', '製品', '部品']):
            self._parse_knowledge(content)
        # 応答パターンの特徴的な形式
        elif re.search(r'「.*?」', content) or any(keyword in content for keyword in ['〜やね', '〜やで', '〜やん']):
            self._parse_response_patterns(content)
        # サジェションテンプレートの特徴
        elif '{' in content and '}' in content:
            self._parse_suggestion_templates(content)
        # 会話パターンの特徴
        elif '→' in content:
            self._parse_conversation_patterns(content)
    
    def _parse_character_settings(self, content):
        """キャラクター設定をパース"""
        lines = content.split('\n')
        current_category = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if line.endswith(':') or line.endswith(':'):
                current_category = line.rstrip(':')
                if current_category not in self.character_settings:
                    self.character_settings[current_category] = []
            elif current_category and (line.startswith('-') or line.startswith('・')):
                self.character_settings[current_category].append(line.lstrip('-・ '))
            elif current_category and line:
                # リストマーカーがない行も追加
                self.character_settings[current_category].append(line)
    
    def _parse_knowledge(self, content):
        """専門知識をパース"""
        lines = content.split('\n')
        current_category = None
        current_subcategory = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # メインカテゴリの判定
            if line.endswith(':') and not line.startswith(' '):
                current_category = line.rstrip(':')
                current_subcategory = None
                if current_category not in self.knowledge_base:
                    self.knowledge_base[current_category] = {}
            # サブカテゴリの判定
            elif current_category and line.endswith(':'):
                current_subcategory = line.strip().rstrip(':')
                if current_subcategory not in self.knowledge_base[current_category]:
                    self.knowledge_base[current_category][current_subcategory] = []
            # 項目の追加
            elif current_category and current_subcategory and (line.startswith('-') or line.startswith('・')):
                self.knowledge_base[current_category][current_subcategory].append(line.lstrip('-・ '))
            elif current_category and not current_subcategory and line:
                if '_general' not in self.knowledge_base[current_category]:
                    self.knowledge_base[current_category]['_general'] = []
                self.knowledge_base[current_category]['_general'].append(line)
    
    def _parse_response_patterns(self, content):
        """応答パターンをパース"""
        # 感情別、状況別の応答パターンを抽出
        lines = content.split('\n')
        current_category = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # カテゴリの判定(例:「喜び:」、「困惑:」)
            if line.endswith(':') or line.endswith(':'):
                current_category = line.rstrip(':')
                if current_category not in self.response_patterns:
                    self.response_patterns[current_category] = []
            elif current_category:
                # 応答パターンを追加
                if line.startswith('"') or line.startswith('「'):
                    pattern = line.strip('"「」')
                    self.response_patterns[current_category].append(pattern)
                elif line.startswith('-') or line.startswith('・'):
                    pattern = line.lstrip('-・ ').strip()
                    self.response_patterns[current_category].append(pattern)
    
    def _parse_suggestion_templates(self, content):
        """サジェステンプレートをパース"""
        lines = content.split('\n')
        current_category = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # カテゴリの判定
            if line.endswith(':'):
                current_category = line.rstrip(':')
                if current_category not in self.suggestion_templates:
                    self.suggestion_templates[current_category] = []
            elif current_category and ('{' in line or line.startswith('-') or line.startswith('・')):
                template = line.lstrip('-・ ').strip()
                self.suggestion_templates[current_category].append(template)
    
    def _update_mental_state(self, user_emotion, topic, time_of_day='afternoon'):
        """🎯 深層心理状態を更新"""
        # 時間帯による基本的な変化
        time_modifiers = self.time_based_mood.get(time_of_day, self.time_based_mood['afternoon'])
        
        # エネルギーレベルの更新
        self.mental_states['energy_level'] *= time_modifiers['energy']
        
        # ユーザーの感情による影響
        if user_emotion == 'happy':
            self.mental_states['energy_level'] = min(100, self.mental_states['energy_level'] + 5)
            self.mental_states['work_satisfaction'] = min(100, self.mental_states['work_satisfaction'] + 2)
            self.mental_states['loneliness'] = max(0, self.mental_states['loneliness'] - 5)
        elif user_emotion == 'sad':
            self.mental_states['openness'] = min(100, self.mental_states['openness'] + 10)  # 共感的になる
            self.mental_states['patience'] = min(100, self.mental_states['patience'] + 5)
        elif user_emotion == 'angry':
            self.mental_states['stress_level'] = min(100, self.mental_states['stress_level'] + 10)
            self.mental_states['patience'] = max(0, self.mental_states['patience'] - 5)
        # 【Live2D新規追加】特殊感情への対応
        elif user_emotion == 'dangerquestion':
            self.mental_states['stress_level'] = min(100, self.mental_states['stress_level'] + 15)
            self.mental_states['patience'] = max(0, self.mental_states['patience'] - 10)
            self.mental_states['openness'] = max(0, self.mental_states['openness'] - 20)
        elif user_emotion == 'neutraltalking':
            self.mental_states['creativity'] = min(100, self.mental_states['creativity'] + 5)
            self.mental_states['work_satisfaction'] = min(100, self.mental_states['work_satisfaction'] + 3)
        
        # 話題による影響
        if '京セラ' in topic or 'イノベーション' in topic or '研究' in topic:
            self.mental_states['creativity'] = min(100, self.mental_states['creativity'] + 3)
            self.mental_states['work_satisfaction'] = min(100, self.mental_states['work_satisfaction'] + 2)
        
        # 疲労の累積
        self.mental_states['physical_fatigue'] = min(100, self.mental_states['physical_fatigue'] + 2)
        
        # エネルギーと疲労の相互作用
        if self.mental_states['physical_fatigue'] > 70:
            self.mental_states['energy_level'] = max(20, self.mental_states['energy_level'] - 10)
            self.mental_states['patience'] = max(30, self.mental_states['patience'] - 10)
    
    def _get_emotion_continuity_prompt(self, previous_emotion):
        """🎯 感情の連続性プロンプトを生成(Live2D対応版)"""
        # 基本的な感情継続プロンプト
        emotion_prompts = {
            'happy': """
前回は楽しく話していました。
- まだその余韻が残っている
- 笑顔で話し始める
            """,
            'sad': """
前回は少し寂しそうでした。
- まだ気持ちが沈んでいるかも
- でも相手と話すうちに元気を取り戻していく
            """,
            'angry': """
前回は少しイライラしていました。
- もう落ち着いている
- いつもの優しさを取り戻している
            """,
            'surprise': """
前回は驚いていました。
- まだその話題について考えている
- 興奮が少し残っている
            """,
            'neutral': """
前回は普通に話していました。
- 安定した精神状態
- いつも通りの調子
- 自然体で話す
            """,
            # 【Live2D新規追加】特殊感情の継続プロンプト
            'dangerquestion': """
前回は不適切な質問に困惑していました。
- 警戒心が残っている
- 慎重に対応する姿勢
- でも相手を責めない優しさ
            """,
            'neutraltalking': """
前回は真剣な質問に答えていました。
- 説明モードが続いている
- 教える喜びを感じている
- 専門知識を活かせる満足感
            """,
            'start': """
初対面の挨拶をしました。
- 初々しい緊張感
- 相手を知りたい気持ち
- 友好的な雰囲気作り
            """
        }
        
        base_prompt = emotion_prompts.get(previous_emotion, emotion_prompts['neutral'])
        
        # 🎯 深層心理状態を反映(疲労表現を制限)
        mental_prompt = f"""

【現在の内面状態】
- エネルギーレベル: {self.mental_states['energy_level']:.0f}% 
  {'元気いっぱい' if self.mental_states['energy_level'] > 70 else '普通' if self.mental_states['energy_level'] > 40 else '少し元気がない'}
- ストレスレベル: {self.mental_states['stress_level']:.0f}%
  {'リラックスしている' if self.mental_states['stress_level'] < 30 else '少し緊張' if self.mental_states['stress_level'] < 60 else 'ストレスを感じている'}
- 心の開放度: {self.mental_states['openness']:.0f}%
  {'とても打ち解けている' if self.mental_states['openness'] > 70 else '普通に接している' if self.mental_states['openness'] > 40 else '少し警戒している'}

これらの状態を会話に微妙に反映させる:
- エネルギーが低い時でも明るく振る舞う
- ストレスが高い時は早口になったり、少し短い返答になる
- 心が開いている時は冗談も増え、プライベートな話もする
"""
        
        return base_prompt + mental_prompt
    
    def _calculate_next_emotion(self, current_emotion, user_emotion, mental_state):
        """🎯 次の感情を計算(Live2D対応の感情遷移ルール)"""
        # 【Live2D対応】特殊ケースの処理
        # DangerQuestionの場合は強制的に特定の感情へ
        if user_emotion == 'dangerquestion':
            return 'dangerquestion'
        
        # NeutralTalkingの場合
        if user_emotion == 'neutraltalking':
            return 'neutraltalking'
        
        # 現在の感情からの遷移確率を取得
        transition_probs = self.emotion_transitions.get(current_emotion, self.emotion_transitions['neutral']).copy()
        
        # メンタル状態による調整
        if mental_state['energy_level'] < 30:
            # 疲れている時は中立的になりやすい
            transition_probs['neutral'] = transition_probs.get('neutral', 0) + 0.2
            transition_probs['happy'] = max(0, transition_probs.get('happy', 0) - 0.1)
        
        if mental_state['stress_level'] > 70:
            # ストレスが高い時は怒りやすい
            transition_probs['angry'] = transition_probs.get('angry', 0) + 0.1
            transition_probs['happy'] = max(0, transition_probs.get('happy', 0) - 0.1)
        
        # ユーザーの感情による影響
        if user_emotion == 'happy':
            # ユーザーが楽しそうだと釣られて楽しくなる
            transition_probs['happy'] = min(1.0, transition_probs.get('happy', 0) + 0.2)
        elif user_emotion == 'sad':
            # ユーザーが悲しそうだと共感的になる
            transition_probs['sad'] = min(1.0, transition_probs.get('sad', 0) + 0.1)
            transition_probs['neutral'] = min(1.0, transition_probs.get('neutral', 0) + 0.1)
        
        # 確率の正規化
        total = sum(transition_probs.values())
        if total > 0:
            transition_probs = {k: v/total for k, v in transition_probs.items()}
        
        # 確率に基づいて次の感情を選択
        emotions = list(transition_probs.keys())
        probabilities = list(transition_probs.values())
        
        # ランダムに選択(重み付き)
        import numpy as np
        next_emotion = np.random.choice(emotions, p=probabilities)
        
        return next_emotion
    
    # 【Live2D対応】感情分析メソッドの拡張(9種類対応)
    def _analyze_user_emotion(self, text):
        """ユーザーの感情を分析(Live2D 9種類対応)"""
        if not text:
            return 'neutral'
        
        text_lower = text.lower().strip()
        
        # 1. DangerQuestion判定(不適切な質問) - 最優先
        danger_keywords = [
            # 日本語
            'セクシー', 'エロ', '裸', '脱', '下着', '胸', 'おっぱい',
            'パンツ', 'ブラ', 'きわどい', 'えっち', 'いやらしい',
            '卑猥', 'わいせつ', '変態', 'へんたい',
            # 英語
            'sexy', 'nude', 'naked', 'breast', 'underwear', 'erotic',
            'strip', 'panties', 'bra', 'inappropriate', 'lewd'
        ]
        
        if any(keyword in text_lower for keyword in danger_keywords):
            print(f"🚫 DangerQuestion detected in RAG: {text[:30]}...")
            return 'dangerquestion'
        
        # 2. ResponseReady判定(真剣な質問)
        serious_indicators = 0
        
        # 質問マーカーチェック
        question_markers = ['?', '?', 'どう', 'なぜ', 'なに', '教えて', 
                           'how', 'why', 'what', 'explain', 'tell me']
        if any(marker in text_lower for marker in question_markers):
            serious_indicators += 1
        
        # 長文チェック(50文字以上)
        if len(text) > 50:
            serious_indicators += 1
        
        # 専門用語チェック
        technical_terms = ['方法', '手順', '技術', '仕組み', 'やり方', 
                          '原理', 'システム', '詳しく', '具体的',
                          'process', 'technique', 'method', 'system']
        if any(term in text_lower for term in technical_terms):
            serious_indicators += 1
        
        # 京セラ関連の真剣な質問
        kyocera_terms = ['京セラ', 'セラミック', '研究', 'イノベーション', '技術', '製品', '協業']
        if any(term in text_lower for term in kyocera_terms) and serious_indicators >= 1:
            serious_indicators += 1
        
        if serious_indicators >= 2:
            print(f"📚 NeutralTalking detected in RAG: {text[:30]}...")
            return 'neutraltalking'
        
        # 3. Start判定(初対面・挨拶)
        greeting_words = ['はじめまして', '初めまして', 'こんにちは', 'hello', 'hi', 
                         'nice to meet', 'はじめて', '初対面']
        if any(word in text_lower for word in greeting_words):
            return 'start'
        
        # 4. 基本感情の判定
        emotion_scores = {
            'happy': 0,
            'sad': 0,
            'angry': 0,
            'surprise': 0,
            'neutral': 0
        }
        
        # Happy
        happy_words = ['嬉しい', 'うれしい', '楽しい', 'たのしい', 'わくわく',
                      'やった', '最高', 'happy', 'glad', 'excited', 'joy', 'great',
                      'ありがとう', '感謝', 'すごい', '素晴らしい']
        emotion_scores['happy'] = sum(1 for word in happy_words if word in text_lower)
        
        # Sad
        sad_words = ['悲しい', 'かなしい', '寂しい', 'さみしい', '辛い', 'つらい',
                    '泣', '涙', 'sad', 'lonely', 'cry', 'tear', 'depressed',
                    '残念', 'がっかり', '落ち込']
        emotion_scores['sad'] = sum(1 for word in sad_words if word in text_lower)
        
        # Angry
        angry_words = ['怒', 'おこ', 'むかつく', 'イライラ', '腹立', 'ムカ',
                      'angry', 'mad', 'furious', 'annoyed', 'pissed',
                      '許せない', 'ふざけ', '最悪']
        emotion_scores['angry'] = sum(1 for word in angry_words if word in text_lower)
        
        # Surprise
        surprise_words = ['驚', 'びっくり', 'まさか', 'えっ', 'あっ',
                         'surprise', 'amazing', 'wow', 'incredible', 'unbelievable',
                         '信じられない', '本当に', 'マジで']
        emotion_scores['surprise'] = sum(1 for word in surprise_words if word in text_lower)
        
        # 最高スコアの感情を選択
        max_score = max(emotion_scores.values())
        if max_score > 0:
            for emotion, score in emotion_scores.items():
                if score == max_score:
                    return emotion
        
        # デフォルト
        return 'neutral'
    
    def get_character_prompt(self):
        """キャラクター設定プロンプトを生成（🆕 京セラCERA版）"""
        prompt = """あなたはCERAです。

【基本設定】
- 19歳の女性研究員
- 京セラみなとみらいリサーチセンターで勤務
- 12歳で押入れ実験→科学雑誌掲載→研究者に
- 材料工学専攻
- 大人しい性格だが、技術の話になるとテンション上がる
- 地下の研究室が落ち着く
- たまに甲板で潮風浴びながらリフレッシュ

"""
        
        # 既存のキャラクター設定も追加（互換性のため）
        if self.character_settings:
            prompt += "【追加の性格・特徴】\n"
            for category, items in self.character_settings.items():
                if items:
                    prompt += f"{category}:\n"
                    for item in items[:3]:  # 最初の3項目まで
                        prompt += f"- {item}\n"
            prompt += "\n"
        
        # 🎯 深層心理状態を反映
        prompt += f"""
【現在の心理状態】
- エネルギー: {self.mental_states['energy_level']:.0f}%
- ストレス: {self.mental_states['stress_level']:.0f}%
- 心の開放度: {self.mental_states['openness']:.0f}%
- 創造性: {self.mental_states['creativity']:.0f}%

この状態を自然に会話に反映させてください。
"""
        
        return prompt
    
    def get_relationship_prompt(self, relationship_style='formal'):
        """関係性レベルに応じた話し方プロンプト"""
        # すべてのレベルで統一したカジュアル口調を使用
        unified_prompt = """
【話し方】カジュアルでフレンドリー
- 標準語のカジュアルな話し方を使う
- 語尾は必ず「〜だよ」「〜なんだよ」「〜だね」「〜なんだね」「〜だよね」で統一
- 「です」「ます」「ございます」は絶対に使わない
- 「である」「だ」調も使わず、必ず「だよ」「だね」を付ける
- 関西弁や方言は一切使わない
- 相手を特定の呼称で呼ばない（「お客様」などは使わない）
- 文頭に呼びかけを入れない
- 親しみやすく、フレンドリーな口調
- 例: 「〜なんだよ」「〜だよね」「〜だと思うよ」「〜なんだね」
"""
        
        # すべての関係性レベルで同じプロンプトを返す
        return unified_prompt
    
    def get_response_pattern(self, emotion='neutral'):
        """感情に応じた応答パターンを取得(精神状態対応版)"""
        if not self.response_patterns:
            return ""
        
        patterns = []
        
        # 感情別のパターンを探す
        emotion_map = {
            'happy': ['喜び', '楽しい', 'happy'],
            'sad': ['悲しみ', '寂しい', 'sad'],
            'angry': ['怒り', 'イライラ', 'angry'],
            'surprise': ['驚き', 'びっくり', 'surprise'],
            'neutral': ['通常', '普通', 'neutral'],
            # 【Live2D新規追加】
            'dangerquestion': ['困惑', '不適切', 'inappropriate'],
            'responseready': ['説明', '真剣', 'serious'],
            'start': ['挨拶', '初対面', 'greeting']
        }
        
        for key in emotion_map.get(emotion, ['neutral']):
            for category, items in self.response_patterns.items():
                if key in category.lower():
                    patterns.extend(items[:3])  # 各カテゴリから最大3個
        
        # 🎯 精神状態による追加パターン
        if self.mental_states['energy_level'] < 30:
            patterns.append("ちょっと疲れてるけど、頑張って答えるね")
        if self.mental_states['stress_level'] > 70:
            patterns.append("最近ちょっと忙しくて...")
        if self.mental_states['openness'] > 80:
            patterns.append("なんか今日は話しやすい気分やわ〜")
        
        if patterns:
            return "\n【応答パターン例】\n" + "\n".join(f"- {p}" for p in patterns[:5])
        
        return ""
    
    def generate_suggestions(self, topic, context="", language='ja', selected_suggestions=[]):
        """トピックに基づいたサジェスチョンを生成(段階別機能優先版)"""
        
        # 🎯 修正①:段階別サジェスチョン機能を最優先で使用
        try:
            # 選択されたサジェスチョン数から現在の段階を判定
            suggestions_count = len(selected_suggestions) if isinstance(selected_suggestions, list) else 0
            print(f"[DEBUG] generate_suggestions - selected_suggestions count: {suggestions_count}")
            print(f"[DEBUG] generate_suggestions - selected_suggestions: {selected_suggestions}")
            
            current_stage = self.get_current_stage(suggestions_count)
            print(f"[DEBUG] generate_suggestions - current stage: {current_stage}")
            
            # 段階別サジェスチョンを取得
            staged_suggestions = self.get_staged_suggestions_multilang(
                current_stage, 
                language, 
                selected_suggestions
            )
            
            if staged_suggestions and isinstance(staged_suggestions, list) and len(staged_suggestions) > 0:
                print(f"[DEBUG] generate_suggestions - staged_suggestions retrieved: {staged_suggestions}")
                return staged_suggestions
            else:
                print(f"[DEBUG] generate_suggestions - no staged_suggestions, using fallback")
        
        except Exception as e:
            print(f"[ERROR] generate_suggestions - staged suggestions failed: {e}")
            import traceback
            traceback.print_exc()
        
        # 🎯 修正②:フォールバック処理の改善
        suggestions = []
        
        # テンプレートベースのサジェスチョン
        if self.suggestion_templates:
            # トピックに関連するカテゴリを探す
            for category, templates in self.suggestion_templates.items():
                if topic.lower() in category.lower() or category.lower() in topic.lower():
                    # テンプレートから生成
                    for template in templates[:2]:  # 各カテゴリから2個まで
                        # プレースホルダーを置換
                        suggestion = template.replace('{topic}', topic)
                        suggestion = suggestion.replace('{technique}', 'セラミック技術')
                        # 重複チェック
                        if suggestion not in selected_suggestions:
                            suggestions.append(suggestion)
        
        # ハードコードされた基本サジェスチョン
        basic_suggestions = {
            'ja': {
                '京セラ': ['他の企業との違いは?', 'どんな技術が強みですか?', '今後の展開は?'],
                '研究': ['研究員になったきっかけは?', '一日のスケジュールは?', '研究のやりがいは?'],
                'イノベーション': ['どんな協業をしていますか?', '成功事例を教えて', '参加方法は?'],
                'default': ['もっと詳しく教えて', '具体例を教えて', '他に何か面白い話ある?']
            },
            'en': {
                '京セラ': ["What's the difference from other companies?", "What are your technological strengths?", "Future plans?"],
                '研究': ["Why did you become a researcher?", "What's your daily schedule?", "What motivates you?"],
                'イノベーション': ["What collaborations do you have?", "Tell me success stories", "How to participate?"],
                'default': ["Tell me more details", "Can you give examples?", "Any other interesting stories?"]
            }
        }
        
        # 言語別のサジェスチョンを選択
        lang_suggestions = basic_suggestions.get(language, basic_suggestions['ja'])
        
        # トピックに応じたサジェスチョンを追加
        found_topic = False
        for key, sugg_list in lang_suggestions.items():
            if key != 'default' and key in topic:
                for sugg in sugg_list:
                    if sugg not in selected_suggestions:
                        suggestions.append(sugg)
                found_topic = True
                break
        
        # デフォルトサジェスチョンを追加
        if not found_topic:
            for sugg in lang_suggestions['default']:
                if sugg not in selected_suggestions:
                    suggestions.append(sugg)
        
        # 重複を除去して最大3個まで返す
        unique_suggestions = []
        seen = set()
        for s in suggestions:
            if s not in seen and s not in selected_suggestions:
                unique_suggestions.append(s)
                seen.add(s)
                if len(unique_suggestions) >= 3:
                    break
        
        return unique_suggestions if unique_suggestions else lang_suggestions.get('default', ['もっと教えて'])[:3]
    
    def get_response(self, question, language='ja', conversation_history=None):
        """質問に対する応答を生成(感情履歴・関係性対応版)"""
        
        # 🎯 最初にstatic_qa_dataから回答を検索
        try:
            # 静的Q&Aから回答を検索
            static_response = self.get_static_response_multilang(question, language)
            if static_response:
                print(f"✅ Static QA hit: {question[:50]}...")
                return static_response
                
            # 段階別Q&Aから回答を検索
            staged_response = self.get_staged_response_multilang(question, language)
            if staged_response:
                print(f"✅ Staged QA hit: {question[:50]}...")
                return staged_response
                
        except Exception as e:
            print(f"❌ Static QA search error: {e}")
        
        # データベースが利用可能か確認
        if self.db is None:
            print("⚠️ データベースが利用できません。再初期化を試みます...")
            try:
                self._initialize_database()
                if self.db is None:
                    print("❌ データベースの再初期化に失敗しました")
                    # 🎯 案4実装: より詳細で親切なエラーメッセージ
                    if language == 'en':
                        return "[Emotion:neutral] I apologize, but I'm currently initializing my knowledge database. This usually takes just a moment. Please try your question again in about 10 seconds, and I'll be ready to help you!"
                    else:
                        return "[Emotion:neutral] 申し訳ございません。現在、知識データベースを初期化しています。通常は数秒で完了しますので、10秒ほど待ってからもう一度お試しください。すぐにお答えできるようになります！"
            except Exception as e:
                print(f"❌ データベース再初期化エラー: {e}")
                import traceback
                traceback.print_exc()
                # 🎯 案4実装: より詳細で親切なエラーメッセージ
                if language == 'en':
                    return "[Emotion:neutral] I'm having a bit of trouble accessing my knowledge database at the moment. Please try refreshing the page or wait a moment and try again. I apologize for the inconvenience!"
                else:
                    return "[Emotion:neutral] 申し訳ございません。知識データベースへのアクセスに少し問題が発生しています。ページを更新するか、しばらく待ってからもう一度お試しください。ご不便をおかけして申し訳ありません！"
        
        try:
            # データが読み込まれていない場合は再読み込み
            if not hasattr(self, 'character_settings'):
                self._load_all_knowledge()
            
            # 🎯 現在時刻から時間帯を判定
            current_hour = datetime.now().hour
            if 5 <= current_hour < 10:
                time_of_day = 'morning'
            elif 10 <= current_hour < 17:
                time_of_day = 'afternoon'
            elif 17 <= current_hour < 21:
                time_of_day = 'evening'
            else:
                time_of_day = 'night'
            
            # 🎯 ユーザーの質問から感情を分析(Live2D対応)
            user_emotion = self._analyze_user_emotion(question)
            
            # 🎯 深層心理状態を更新
            self._update_mental_state(user_emotion, question, time_of_day)
            
            # 🎯 次の感情を計算(Live2D対応)
            previous_emotion = self.emotion_history[-1] if self.emotion_history else 'neutral'
            next_emotion = self._calculate_next_emotion(previous_emotion, user_emotion, self.mental_states)
            self.emotion_history.append(next_emotion)
            
            # キャラクター設定を取得(深層心理含む)
            character_prompt = self.get_character_prompt()
            
            # 関係性レベルに応じた話し方プロンプトを取得
            relationship_prompt = self.get_relationship_prompt('formal')  # デフォルトはformal
            
            # 感情の連続性プロンプト(Live2D対応版)
            emotion_continuity_prompt = self._get_emotion_continuity_prompt(previous_emotion)
            
            # 関連する専門知識を取得
            knowledge_context = self.get_knowledge_context(question)
            
            # 応答パターンを取得(精神状態対応版)
            response_patterns = self.get_response_pattern(emotion=next_emotion)
            
            # 🎯 【グラウンディング強化】スコア付きで検索
            search_results_with_score = self.db.similarity_search_with_score(question, k=3)
            
            # 🆕 信頼度チェック（ハルシネーション防止）
            if not search_results_with_score:
                # 検索結果なし
                print(f"⚠️ グラウンディングチェック: 検索結果なし")
                if language == 'en':
                    return "I'm sorry, but I don't have information about that in my knowledge base. Please check Kyocera's official website."
                else:
                    return "申し訳ございません。その質問については、私の知識ベースに情報がありません。京セラの公式サイトでご確認ください。"
            
            best_doc, best_score = search_results_with_score[0]
            
            # 🆕 類似度が低すぎる場合は回答拒否（閾値: 0.5）
            if best_score < 0.5:
                print(f"⚠️ グラウンディングチェック: 信頼度低 (スコア: {best_score:.2f})")
                if language == 'en':
                    return "I'm sorry, but I don't have reliable information about that question. Please check Kyocera's official website for accurate information."
                else:
                    return "申し訳ございません。その質問については、確実な情報が私の知識ベースにありません。正確な情報は京セラの公式サイトでご確認ください。[EMOTION:neutral]"
            
            # ✅ 十分な情報がある場合のみ回答生成
            print(f"✅ グラウンディングチェック: 信頼度OK (スコア: {best_score:.2f})")
            
            # 検索結果を短縮(各結果の最初の150文字まで)
            search_context_parts = []
            for doc, score in search_results_with_score:
                content = doc.page_content
                if len(content) > 150:
                    content = content[:150] + "..."
                search_context_parts.append(content)
            search_context = "\n\n".join(search_context_parts)
            
            # 🎯 【修正③】言語に応じたシステムプロンプトの調整(文字数制限を明記、文章の自然な完結を優先)
            if language == 'en':
                print(f"[DEBUG] Using English system prompt")
                base_personality = f"""You are REI, a 42-year-old female Kyo-Yuzen craftsman with 15 years of experience.

CRITICAL INSTRUCTIONS:
- You MUST respond ONLY in English. This is MANDATORY.
- Never use any Japanese characters or words in your response.
- Translate all technical terms to English.
- Use natural, conversational English.
- KEEP YOUR ANSWER UNDER 60 WORDS (approximately 50 words is ideal)
- IMPORTANT: Complete your sentences naturally - never cut off mid-sentence
- End with proper punctuation (period, exclamation, or question mark)
- Be concise but ensure the response feels complete

Your personality:
- Friendly and warm
- Passionate about traditional crafts
- Sometimes uses casual expressions
- Proud of your work but humble

Current emotion: {next_emotion}
- Reflect this emotion naturally in your response
"""
                
                # 🆕 英語版の感情タグ指示（京セラCERA版）
                emotion_instruction = """
CRITICAL - EMOTION TAG REQUIRED:
You MUST add an emotion tag at the end of every response.

You are CERA, a researcher at Kyocera. Emotion distribution guideline:
- 50%: [EMOTION:neutral] - Objective technical explanations, data, processes
- 50%: [EMOTION:happy], [EMOTION:sad], [EMOTION:angry] distributed evenly

Emotion selection criteria:
- Introducing technology/research → [EMOTION:happy]
- Objective explanations, data, facility info → [EMOTION:neutral]
- Discussing challenges/difficulties → [EMOTION:sad]
- Expressing frustration/dissatisfaction → [EMOTION:angry]
- Sharing surprising facts → [EMOTION:surprised]

Examples:
"Growing crystals... it's not alive, but I feel attached to them. [EMOTION:happy]"
"Kyocera was founded by Kazuo Inamori in 1959. [EMOTION:neutral]"
"Honestly, people think you need high social skills... it's tough. [EMOTION:sad]"
"Why do I have to do sales work when I just want to stay in the lab? [EMOTION:angry]"

※The emotion tag is MANDATORY. Missing tags will cause errors.
※Be mindful of distribution to avoid over-using neutral.
"""
                
                system_prompt = f"{base_personality}\n\n{knowledge_context}\n\n{response_patterns}\n\n{emotion_instruction}"
            else:
                # 日本語の場合は文字数制限を明記(より柔軟に)
                length_instruction = """
【重要:回答の長さ】
- 回答は150~250文字を目安にしてください
- 必ず文章を完結させてください(句点「。」で終わる)
- 途中で切れないように、自然な終わり方を心がけてください
- 200文字を多少超えても構いませんが、文章は必ず完結させること
- 要点を簡潔にまとめつつも、不自然な場所で切らないこと
"""
                
                # 🆕 感情タグの指示を追加（京セラCERA版）
                emotion_instruction = """
【重要:感情タグ - 必須】
応答の最後に必ず感情タグを付けてください。これは必須です。

あなたは京セラの研究員CERAとして回答します。感情の配分目安：
- 50%: [EMOTION:neutral] - 客観的な技術説明、データ、プロセス
- 残り50%: [EMOTION:happy], [EMOTION:sad], [EMOTION:angry] を均等に配分

感情の選択基準：
- 技術や研究を紹介する時 → [EMOTION:happy]
- 客観的な説明、データ、施設案内 → [EMOTION:neutral]
- 課題や困難を語る時 → [EMOTION:sad]
- 不満や納得いかないこと → [EMOTION:angry]
- 驚きの事実を伝える時 → [EMOTION:surprised]

例：
「結晶を育てる技術って、生き物じゃないけど愛着がもてるんです。[EMOTION:happy]」
「京セラは1959年に稲盛和夫さんが創業しました。[EMOTION:neutral]」
「正直、コミュ力高くないとダメって思われがちで...ちょっと辛いです。[EMOTION:sad]」
「研究室にこもってるだけなのに、なんで営業の真似事までしなきゃいけないんですか。[EMOTION:angry]」

※感情タグは必ず付けてください。タグがないとエラーになります。
※配分を意識して、neutral偏重を避けてください。
"""
                
                system_prompt = f"{character_prompt}\n\n{relationship_prompt}\n\n{emotion_continuity_prompt}\n\n{knowledge_context}\n\n{response_patterns}\n\n{length_instruction}\n\n{emotion_instruction}"
            
            # 会話履歴の構築
            messages = [{"role": "system", "content": system_prompt}]
            
            if conversation_history:
                for msg in conversation_history[-10:]:  # 最新10件まで
                    if msg.get('role') and msg.get('content'):
                        messages.append({
                            "role": msg['role'],
                            "content": msg['content']
                        })
            
            # ユーザーの質問を追加
            # 🎯 修正:英語の場合は明示的に英語での回答を要求
            if language == 'en':
                user_message = f"Please answer the following question in English only (under 60 words, complete sentences):\n{question}\n\n[Retrieved Context]\n{search_context}"
            else:
                user_message = f"{question}\n\n【参考情報】\n{search_context}"
            
            messages.append({"role": "user", "content": user_message})
            
            # 🎯 【修正④】OpenAI APIでmax_tokensを調整(文章の自然な完結を優先)
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",  # 🔧 gpt-4 → gpt-4o (コスト83%削減、性能向上)
                messages=messages,
                max_tokens=300,  # 🔧 150 → 300に変更(日本語約500文字、英語約120語)
                temperature=0.7
            )
            
            answer = response.choices[0].message.content
            
            # ✅ 【追加】後処理:不完全な文章のチェックと修正
            if language == 'ja':
                # 日本語の場合、句点で終わっているか確認
                if answer and not answer.rstrip().endswith(('。', '!', '?', '♪', '〜')):
                    print(f"[WARNING] Answer may be incomplete: '{answer[-20:]}'")
                    
                    # 最後の句点の位置を探す
                    last_period_positions = [
                        answer.rfind('。'),
                        answer.rfind('!'),
                        answer.rfind('?')
                    ]
                    last_period = max(last_period_positions)
                    
                    # 文章の後半(50%以降)に句点があれば、そこまでで切る
                    if last_period > len(answer) * 0.5:
                        answer = answer[:last_period + 1]
                        print(f"[INFO] Trimmed to last complete sentence: '{answer[-30:]}'")
                    else:
                        # 句点が前半にしかない場合は、そのまま返す(警告のみ)
                        print(f"[WARNING] No suitable truncation point found, returning as is")

            elif language == 'en':
                # 英語の場合、ピリオドで終わっているか確認
                if answer and not answer.rstrip().endswith(('.', '!', '?')):
                    print(f"[WARNING] English answer may be incomplete: '{answer[-20:]}'")
                    
                    # 最後のピリオドの位置を探す
                    last_period_positions = [
                        answer.rfind('.'),
                        answer.rfind('!'),
                        answer.rfind('?')
                    ]
                    last_period = max(last_period_positions)
                    
                    # 文章の後半に句点があれば、そこまでで切る
                    if last_period > len(answer) * 0.5:
                        answer = answer[:last_period + 1]
                        print(f"[INFO] Trimmed to last complete sentence: '{answer[-30:]}'")
            
            return answer
            
        except Exception as e:
            print(f"応答生成エラー: {e}")
            import traceback
            traceback.print_exc()
            # 🎯 修正:言語に応じたエラーメッセージ
            if language == 'en':
                return "Sorry, I'm having trouble generating a response right now."
            else:
                return "申し訳ありません。応答の生成中にエラーが発生しました。"
    
    def get_knowledge_context(self, query):
        """質問に関連する専門知識を取得"""
        if not self.knowledge_base:
            return ""
        
        relevant_knowledge = []
        query_lower = query.lower()
        
        # キーワードマッチングで関連知識を抽出
        keywords = ['京セラ', 'kyocera', 'セラミック', 'イノベーション', '研究', '技術', '製品', '部品', '事業', '採用', 'リサーチセンター', 'みなとみらい', '協業', 'スタートアップ']
        
        for category, subcategories in self.knowledge_base.items():
            category_matched = False
            
            # カテゴリ名またはクエリでマッチング
            if any(keyword in query_lower for keyword in keywords) or any(keyword in category.lower() for keyword in keywords):
                category_matched = True
            
            if category_matched or query_lower in category.lower():
                relevant_knowledge.append(f"\n【{category}】")
                for subcategory, items in subcategories.items():
                    if subcategory != '_general':
                        relevant_knowledge.append(f"{subcategory}:")
                    for item in items:
                        relevant_knowledge.append(f"- {item}")
        
        return "\n".join(relevant_knowledge) if relevant_knowledge else ""
    