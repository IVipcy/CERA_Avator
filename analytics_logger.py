# analytics_logger.py - Google Sheetsを使った訪問者ログ記録システム
"""
訪問者の行動ログをGoogle Sheetsに記録するモジュール
アンケート機能と同じ認証情報を使用
"""

import os
from datetime import datetime
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class AnalyticsLogger:
    """Google Sheetsにアナリティクスデータを記録するクラス"""
    
    def __init__(self):
        self.credentials_path = 'credentials.json'
        self.spreadsheet_id = os.getenv('ANALYTICS_SHEET_ID', os.getenv('SPREADSHEET_ID'))
        self.service = None
        self.enabled = False
        
        # 初期化を試行
        self._initialize()
    
    def _initialize(self):
        """Google Sheets APIサービスを初期化"""
        try:
            # 認証情報ファイルの存在確認
            if not os.path.exists(self.credentials_path):
                print(f"⚠️ 認証情報ファイルが見つかりません: {self.credentials_path}")
                print("💡 アナリティクスログ機能は無効化されます")
                return
            
            # スプレッドシートIDの確認
            if not self.spreadsheet_id:
                print("⚠️ ANALYTICS_SHEET_ID または SPREADSHEET_IDが設定されていません")
                print("💡 アナリティクスログ機能は無効化されます")
                return
            
            # 認証情報を読み込み
            SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
            creds = Credentials.from_service_account_file(
                self.credentials_path, 
                scopes=SCOPES
            )
            
            # APIサービスを構築
            self.service = build('sheets', 'v4', credentials=creds)
            self.enabled = True
            
            print(f"✅ Analytics Logger初期化成功")
            print(f"📊 スプレッドシートID: {self.spreadsheet_id[:20]}...")
            
        except Exception as e:
            print(f"❌ Analytics Logger初期化エラー: {e}")
            print("💡 アナリティクスログ機能は無効化されます")
            self.enabled = False
    
    def log_visitor(self, visitor_data):
        """
        訪問者データをログに記録
        
        Args:
            visitor_data: {
                'visitor_id': str,
                'first_visit': str (ISO format),
                'last_visit': str (ISO format),
                'visit_count': int,
                'total_conversations': int,
                'relationship_level': int
            }
        """
        if not self.enabled:
            return False
        
        try:
            # データ行を作成
            values = [[
                visitor_data.get('visitor_id', ''),
                visitor_data.get('first_visit', ''),
                visitor_data.get('last_visit', ''),
                visitor_data.get('visit_count', 0),
                visitor_data.get('total_conversations', 0),
                visitor_data.get('relationship_level', 0)
            ]]
            
            # Sheetsに追記
            body = {'values': values}
            result = self.service.spreadsheets().values().append(
                spreadsheetId=self.spreadsheet_id,
                range='訪問者ログ!A:F',  # シート名: 訪問者ログ
                valueInputOption='RAW',
                insertDataOption='INSERT_ROWS',
                body=body
            ).execute()
            
            print(f"✅ 訪問者ログ記録: {visitor_data.get('visitor_id', '')[:8]}... (会話数: {visitor_data.get('total_conversations', 0)})")
            return True
            
        except HttpError as e:
            print(f"❌ Google Sheets APIエラー (訪問者ログ): {e}")
            return False
        except Exception as e:
            print(f"❌ 訪問者ログ記録エラー: {e}")
            return False
    
    def log_session(self, session_data):
        """
        セッションデータをログに記録
        
        Args:
            session_data: {
                'session_id': str,
                'visitor_id': str,
                'started_at': str (ISO format),
                'ended_at': str (ISO format),
                'conversation_count': int,
                'language': str,
                'user_type': str,
                'max_level_reached': int,
                'quiz_completed': bool
            }
        """
        if not self.enabled:
            return False
        
        try:
            # データ行を作成
            values = [[
                session_data.get('session_id', ''),
                session_data.get('visitor_id', ''),
                session_data.get('started_at', ''),
                session_data.get('ended_at', ''),
                session_data.get('conversation_count', 0),
                session_data.get('language', 'ja'),
                session_data.get('user_type', ''),
                session_data.get('max_level_reached', 0),
                'はい' if session_data.get('quiz_completed', False) else 'いいえ'
            ]]
            
            # Sheetsに追記
            body = {'values': values}
            result = self.service.spreadsheets().values().append(
                spreadsheetId=self.spreadsheet_id,
                range='セッションログ!A:I',  # シート名: セッションログ
                valueInputOption='RAW',
                insertDataOption='INSERT_ROWS',
                body=body
            ).execute()
            
            print(f"✅ セッションログ記録: {session_data.get('session_id', '')[:8]}... (会話: {session_data.get('conversation_count', 0)}回)")
            return True
            
        except HttpError as e:
            print(f"❌ Google Sheets APIエラー (セッションログ): {e}")
            return False
        except Exception as e:
            print(f"❌ セッションログ記録エラー: {e}")
            return False
    
    def log_question(self, question_data):
        """
        質問内容をログに記録
        
        Args:
            question_data: {
                'visitor_id': str,
                'session_id': str,
                'question': str,
                'timestamp': str (ISO format)
            }
        """
        if not self.enabled:
            return False
        
        try:
            # データ行を作成
            values = [[
                question_data.get('visitor_id', ''),
                question_data.get('session_id', ''),
                question_data.get('question', ''),
                question_data.get('timestamp', '')
            ]]
            
            # Sheetsに追記
            body = {'values': values}
            result = self.service.spreadsheets().values().append(
                spreadsheetId=self.spreadsheet_id,
                range='質問ログ!A:D',  # シート名: 質問ログ
                valueInputOption='RAW',
                insertDataOption='INSERT_ROWS',
                body=body
            ).execute()
            
            return True
            
        except HttpError as e:
            # 質問ログは大量に記録されるのでエラーは警告レベルに
            if 'RATE_LIMIT_EXCEEDED' in str(e):
                print(f"⚠️ Google Sheets APIレート制限 (質問ログ)")
            return False
        except Exception as e:
            return False
    
    def initialize_sheets(self):
        """
        スプレッドシートに必要なシートとヘッダーを作成
        手動で実行する必要がある場合に使用
        """
        if not self.enabled:
            print("❌ Analytics Loggerが無効化されています")
            return False
        
        try:
            # 訪問者ログのヘッダー
            visitor_headers = [['visitor_id', '初回訪問', '最終訪問', '訪問回数', '会話総数', 'レベル']]
            
            # セッションログのヘッダー
            session_headers = [['session_id', 'visitor_id', '開始時刻', '終了時刻', '会話数', '言語', 'ユーザー属性', '到達レベル', 'クイズ完了']]
            
            # 質問ログのヘッダー
            question_headers = [['visitor_id', 'session_id', '質問内容', 'タイムスタンプ']]
            
            # 各シートにヘッダーを書き込み
            sheets = [
                ('訪問者ログ!A1:F1', visitor_headers),
                ('セッションログ!A1:I1', session_headers),
                ('質問ログ!A1:D1', question_headers)
            ]
            
            for range_name, headers in sheets:
                body = {'values': headers}
                self.service.spreadsheets().values().update(
                    spreadsheetId=self.spreadsheet_id,
                    range=range_name,
                    valueInputOption='RAW',
                    body=body
                ).execute()
                print(f"✅ シート初期化: {range_name.split('!')[0]}")
            
            return True
            
        except Exception as e:
            print(f"❌ シート初期化エラー: {e}")
            print("💡 Google Sheetsに「訪問者ログ」「セッションログ」「質問ログ」シートを手動で作成してください")
            return False


# グローバルインスタンス
analytics_logger = AnalyticsLogger()
