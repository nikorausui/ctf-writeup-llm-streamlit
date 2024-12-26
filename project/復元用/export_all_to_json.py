import mysql.connector
from mysql.connector import Error
import json
import numpy as np
from datetime import datetime

# データベース設定
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'password',
    'database': 'chat_db'
}

class DatabaseHandler:
    def __init__(self):
        self.connection = self._connect()
    
    def _connect(self):
        try:
            return mysql.connector.connect(**DB_CONFIG)
        except Error as e:
            print(f"データベース接続エラー: {e}")
            return None

    def export_all_to_json(self, json_file_path):
        """
        データベース内の全データをJSONファイルにエクスポートする。
        """
        try:
            if self.connection is None:
                print("データベースに接続できていません。")
                return False
            
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM chat_history")
            rows = cursor.fetchall()

            # NumPy埋め込みをリスト形式に変換して保存
            for row in rows:
                row['question_embedding'] = np.frombuffer(row['question_embedding'], dtype=np.float32).tolist()
                
                # `created_at` を文字列に変換
                if isinstance(row['created_at'], datetime):
                    row['created_at'] = row['created_at'].isoformat()

            with open(json_file_path, 'w', encoding='utf-8') as json_file:
                json.dump(rows, json_file, ensure_ascii=False, indent=4)
            
            print(f"データをJSONファイルにエクスポートしました: {json_file_path}")
            return True
        except Error as e:
            print(f"エクスポート中にエラーが発生しました: {e}")
            return False
        finally:
            cursor.close()

# 実行処理
if __name__ == "__main__":
    db_handler = DatabaseHandler()
    # データベース全データをJSON形式で保存
    db_handler.export_all_to_json("chat_history.json")
