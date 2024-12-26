import streamlit as st
from chat_logic import ChatLogic
from database import DatabaseHandler
from llm_handler import LLMHandler

# インスタンスの作成
chat_logic = ChatLogic()
db_handler = DatabaseHandler()
llm_handler = LLMHandler()
# セッション状態の初期化
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'mode' not in st.session_state:
    st.session_state.mode = 'learning'
if 'question' not in st.session_state:
    st.session_state.question = None
if 'embedding' not in st.session_state:
    st.session_state.embedding = None
if 'response' not in st.session_state:
    st.session_state.response = None
if 'notes' not in st.session_state:
    st.session_state.notes = None
if 'count' not in st.session_state:
  st.session_state["count"] = 0
# ボタンの状態を管理するためのセッション状態を設定
if "hello_state" not in st.session_state:
    st.session_state.hello_state = False

if "hello1_state" not in st.session_state:
    st.session_state.hello1_state = False

st.title('My Application')
 
# タブを作成
tab_titles = ['Test', 'Learn']
tab1, tab2= st.tabs(tab_titles)

LOG_FILE = "log.txt"

def read_log(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "ログファイルが見つかりません。ファイルが存在しない場合は新規作成してください。"
    
def write_log(file_path, text):
    with open(file_path, "a", encoding="utf-8") as f:  # "a"モードで追記
        f.write(text + "\n")

# 各タブにコンテンツを追加
with tab1:
    log_data = read_log(LOG_FILE)
    st.text_area("Chat", log_data, height=200)
    question = st.text_area("質問を入力してください:", height=150)

    if st.button("送信"):
        
        if question.strip():  # 入力が空白でない場合のみ処理      
            response = chat_logic.process_test_mode(question)
            st.session_state.messages.append({"role": "assistant", "content": response})
            print(response)
            for message in st.session_state.messages:
                role, content = message["role"], message["content"]
                if role == "user":
                    write_log(LOG_FILE, f"ユーザー: {content}\n")
                else:
                    write_log(LOG_FILE, f"アシスタント: {content}\n")
    
            st.success(f"質問を送信しました:\n{question}")
            
        else:
            st.error("質問を送信失敗")
        



    
    # 動的にコンテンツを表示
    # if option == "テキスト":
    #     my_list = [f"tool{i}" for i in range(1, 13)]  # 12個のボタンを例として作成

    #     # ボタンごとの状態をセッション状態に保存
    #     for item in my_list:
    #         # セッション状態が未初期化の場合、初期化する
    #         if f"{item}_clicked" not in st.session_state:
    #             st.session_state[f"{item}_clicked"] = False

    #     columns_per_row = 4  # 1行あたりのボタン数
    #     for i in range(0, len(my_list), columns_per_row):
    #         cols = st.columns(columns_per_row)  # 列を作成
    #         for col, item in zip(cols, my_list[i:i + columns_per_row]):  # 現在の行に該当するボタンを配置
    #             with col:
    #                 if st.button(item):
    #                     st.session_state[f"{item}_clicked"] = True

    #                 # ボタンの状態に応じてメッセージを表示
    #                 if st.session_state[f"{item}_clicked"]:
    #                     st.write(f'こんにちは({item})')
                    
 
with tab2:
    st.header('Learn')

