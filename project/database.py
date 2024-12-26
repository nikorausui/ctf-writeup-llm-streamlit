import mysql.connector
from mysql.connector import Error
import numpy as np
from config import DB_CONFIG
from llm_handler import LLMHandler

class DatabaseHandler:
    def __init__(self):
        self.connection = self._connect()
        self._create_tables()
    
    def _connect(self):
        try:
            return mysql.connector.connect(**DB_CONFIG)
        except Error as e:
            print(f"データベース接続エラー: {e}")
            return None

    def _create_tables(self):
        cursor = self.connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_history (
                id INT AUTO_INCREMENT PRIMARY KEY,
                question TEXT,
                question_embedding BLOB,
                answer TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.connection.commit()

    def update_embeddings(self, llm):
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute("SELECT id, question FROM chat_history")
        results = cursor.fetchall()
        
        for row in results:
            new_embedding = llm.get_embedding(row['question'])
            new_embedding = np.array(new_embedding, dtype=np.float32)
            cursor.execute("""
                UPDATE chat_history 
                SET question_embedding = %s 
                WHERE id = %s
            """, (new_embedding.tobytes(), row['id']))
        
        self.connection.commit()
        print("全ての埋め込みベクトルを更新しました")

    def find_similar_questions(self, embedding, limit=5):
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM chat_history")
        results = cursor.fetchall()

        similarities = []
        for row in results:
            stored_embedding = np.frombuffer(row['question_embedding'], dtype=np.float32)
            if len(stored_embedding) != len(embedding):
                print(f"不一致: {len(stored_embedding)} != {len(embedding)}")
                continue
            similarity = np.dot(np.array(embedding), stored_embedding)
            similarities.append((similarity, row))
        
        similarities.sort(reverse=True)
        
        return similarities[:limit]
    def insert_chat(self, question, embedding, response, notes):
        cursor = self.connection.cursor()
        query = """
        INSERT INTO chat_history (question, question_embedding, answer, notes)
        VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query, (question, embedding.tobytes(), response, notes))
        self.connection.commit()
    def save_chat(self, question, embedding, response, notes):
        try:
            cursor = self.connection.cursor()
            
            # NumPy配列をバイト列に変換
            if isinstance(embedding, np.ndarray):
                embedding_bytes = embedding.tobytes()
            else:
                embedding_bytes = np.array(embedding, dtype=np.float32).tobytes()
                
            query = """
            INSERT INTO chat_history 
            (question, question_embedding, answer, notes)
            VALUES (%s, %s, %s, %s)
            """
            
            cursor.execute(query, (
                question,
                embedding_bytes,
                response,
                notes
            ))
            
            self.connection.commit()
            print("チャット履歴を保存しました")
            return True
            
        except Error as e:
            print(f"保存中にエラーが発生しました: {e}")
            return False
        finally:
            cursor.close()
