import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import DatabaseHandler
from llm_handler import LLMHandler
import numpy as np

class ChatLogic:
    def __init__(self):
        self.db = DatabaseHandler()
        self.llm = LLMHandler()

    def process_learning_mode(self, question, notes):

        # 学習モード:
        # - 質問をプロンプトで分析。
        # - 分析された質問と備考を使用して回答を生成。
        # - 分析された質問と回答を埋め込み化して返却。

        # 質問をプロンプトで分析
        analysis_prompt = f"Please,Output a detailed step-by-step analysis of the system name, software name, and all other relevant properties, sites, and information.:\n{question}"
        analyzed_question = self.llm.generate_response(analysis_prompt)
        # print("analysis_prompt--------------------------------")
        # print(analysis_prompt)
        # print("analyzed_question--------------------------------")
        # print(analyzed_question)
        # 分析された質問と備考を使用して回答を生成
        notes="Please output a concise and detailed step-by-step procedure with specific and step-by-step instructions from the following information context. Please be sure to output all tools (e.g. gobusting) and Linux and other commands used in that context, along with specific examples.\n\nContext: \n" + notes
        combined_input = f"From the results of the nmap analysis that will be provided, please output the next command that should be executed.: {analyzed_question}\n以下のテキストを見て具体的かつ詳細な手順を最初から最後まで簡潔に出力してください。 subinformations: {notes} \n\n手順をすべて出力しなさい"
        # print("combined_input--------------------------------")
        # print(combined_input)
        response = self.llm.generate_response(combined_input)
        print(response)
        
        # 分析された質問と回答を埋め込み化
        embedding = self.llm.get_embedding(f"question: {analyzed_question}\nAnswer: {response}")
        
        return analyzed_question, response, embedding

    def save_chat(self, question, embedding, answer, notes):
    
        # 分析された質問、埋め込み、回答、備考をデータベースに保存。
      
        self.db.save_chat(question, embedding, answer, notes)

    def process_test_mode(self, question):
        # テストモード:
        # - 質問をプロンプトで分析して、分析結果を埋め込み化。
        # - データベースで類似検索を行い、その結果を基に回答を生成。
        # 質問をプロンプトで分析
        analysis_prompt = f"Please,Output a detailed step-by-step analysis of the system name, software name, and all other relevant properties, sites, and information.:\n{question}"
        a="From the results of the nmap analysis that will be provided, please output the next command that should be executed."
        analyzed_question = self.llm.generate_response(analysis_prompt)
        analyzed_question=a+analyzed_question
        print(analyzed_question)
        # 分析結果を埋め込み化
        embedding = np.array(self.llm.get_embedding(analyzed_question), dtype=np.float32)
        
        # 埋め込みに基づいて類似質問を検索
        similar_chats = self.db.find_similar_questions(embedding, limit=1)
        
        # 類似質問データをコンテキストとして生成
        context = "Below are similar questions and answers from the past:\n"
        for sim, chat in similar_chats:
            context += f"\n\n類似度: {sim:.2f}\n\n"
            context += f"Q: {chat['question']}\nA: {chat['answer']}\n\n"
        
        # コンテキストを基に回答を生成
        # response = self.llm.generate_response(f"question: {question}\n{context}")
        
        return context
