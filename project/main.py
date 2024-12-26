import streamlit as st
from chat_logic import ChatLogic
from database import DatabaseHandler  # データベース処理クラス
from llm_handler import LLMHandler    # LLM処理クラス

# Streamlitアプリケーションの開始
st.title("HTB Writeup ")

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

# タブの作成
tab_titles = ['Test','Learn']
tab1, tab2 = st.tabs(tab_titles)
# --- Testタブの内容 ---
with tab1:
    # 質問入力欄
    question = st.text_area("質問を入力してください:", height=150, key="test_question")

    # 送信ボタン
    if st.button("送信", key="test_send_button"):
        if question.strip():  # 質問が空白でない場合のみ処理
            response = chat_logic.process_test_mode(question)
            st.session_state.messages.append({"role": "user", "content": question})
            st.session_state.messages.append({"role": "assistant", "content": response})
        else:
            st.error("質問を入力してください。")

    # チャット履歴表示
    for message in st.session_state.messages:
        role, content = message["role"], message["content"]
        if role == "user":
            st.write(f"ユーザー: {content}")
        else:
            st.write(f"アシスタント: {content}")
# --- Learnタブの内容 ---
with tab2:
    # 質問入力欄
    question = st.text_area("質問を入力してください:", height=150, key="learn_question")
    
    # 備考入力欄
    st.text_area("備考", key='learn_notes')

    # 送信ボタン
    if st.button("送信", key="learn_send_button"):
        if question.strip():  # 質問が空白でない場合のみ処理
            analyzed_question, response, embedding = chat_logic.process_learning_mode(
                question, st.session_state.learn_notes
            )
            st.session_state.messages.append({"role": "user", "content": f"元の質問: {question}"})
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.session_state.question = analyzed_question  # 分析された質問を保存
            st.session_state.embedding = embedding
            st.session_state.response = response
        else:
            st.error("質問を入力してください。")

    # チャット履歴表示
    for message in st.session_state.messages:
        role, content = message["role"], message["content"]
        if role == "user":
            st.write(f"ユーザー: {content}")
        else:
            st.write(f"アシスタント: {content}")

    # 保存ボタン
    if st.button("保存", key="learn_save_button"):
        if (
            st.session_state.question is None or
            st.session_state.embedding is None or
            st.session_state.response is None
        ):
            st.warning("保存する前に質問を入力してください")
        else:
            try:
                chat_logic.save_chat(
                    st.session_state.question,  # 分析された質問を保存
                    st.session_state.embedding,
                    st.session_state.response,
                    st.session_state.notes
                )
                st.info("保存しました")
            except Exception as e:
                st.error(f"保存中にエラーが発生しました: {e}")

    # 埋め込みベクトル更新ボタン
    if st.button("埋め込みベクトルを更新", key="learn_update_embeddings_button"):
        db_handler.update_embeddings(llm_handler)
        st.success("埋め込みベクトルを更新しました")


