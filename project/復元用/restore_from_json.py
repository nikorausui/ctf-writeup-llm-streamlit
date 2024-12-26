import mysql.connector
from mysql.connector import Error
import json
import numpy as np
from datetime import datetime
from config import DB_CONFIG

class DatabaseHandler:
    def __init__(self):
        self.connection = self._connect()
    
    def _connect(self):
        try:
            return mysql.connector.connect(**DB_CONFIG)
        except Error as e:
            print(f"データベース接続エラー: {e}")
            return None
    
    def restore_from_json(self, json_file_path):
        """
        JSONファイルからデータを読み込み、データベースに復元する。
        """
        try:
            if self.connection is None:
                print("データベースに接続できていません。")
                return False
            
            # JSONファイルの読み込み
            with open(json_file_path, 'r', encoding='utf-8') as json_file:
                data = json.load(json_file)

            cursor = self.connection.cursor()

            # データをデータベースに挿入
            for row in data:
                question = row['question']
                embedding = np.array(row['question_embedding'], dtype=np.float32)
                answer = row['answer']
                notes = row['notes']
                
                # `created_at` を datetime オブジェクトに変換
                created_at = datetime.fromisoformat(row['created_at'])

                # データベースに挿入
                query = """
                INSERT INTO chat_history (question, question_embedding, answer, notes, created_at)
                VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(query, (
                    question,
                    embedding.tobytes(),
                    answer,
                    notes,
                    created_at
                ))
            
            self.connection.commit()
            print("データベースに復元しました")
            return True
        except Error as e:
            print(f"復元中にエラーが発生しました: {e}")
            return False
        finally:
            cursor.close()

# 実行処理
if __name__ == "__main__":
    db_handler = DatabaseHandler()
    # `chat_history.json`からデータを復元
    db_handler.restore_from_json("chat_history.json")
