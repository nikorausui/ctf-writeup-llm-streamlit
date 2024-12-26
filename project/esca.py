import streamlit as st
import requests
import json
import os
import html
from bs4 import BeautifulSoup
from pathlib import Path

class LLMClient:
    def __init__(self, base_url, model):
        self.base_url = base_url
        self.model = model

    def generate_response(self, prompt, context=""):
        try:
            response = requests.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": "qwen2.5:3b",
                    "options":{"temperature":0},
                    "messages": [
                        {"role": "user", "content": prompt},
                        {"role": "system", "content": context}
                    ],
                    "stream": False
                }
            )
            return response.json()['message']['content']
        except Exception as e:
            st.error(f"LLM APIエラー: {str(e)}")
            return None

def load_log():
    if os.path.exists('log.json'):
        with open('log.json', 'r') as f:
            return json.load(f)
    return {}

def save_log(log_data):
    with open('log.json', 'w') as f:
        json.dump(log_data, f, indent=4)

def extract_command(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    shell_section = soup.find('h2', {'id': 'shell'})
    if shell_section:
        code_element = shell_section.find_next('pre').find('code')
        if code_element:
            return html.unescape(code_element.text)
    return None

def process_tool(tool_name, url, log_data):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            command = extract_command(response.text)
            if command:
                log_data[url] = command
                save_log(log_data)
                st.success(f"{tool_name} - 新規取得:")
                st.code(command)
            else:
                st.warning(f"{tool_name} - コマンドが見つかりませんでした")
        else:
            st.error(f"{tool_name} - エラー: {response.status_code}")
    except Exception as e:
        st.error(f"エラーが発生しました: {str(e)}")

def main():
    st.title("LLM Integration")
    
    # 直接URLとモデルを指定
    llm_client = LLMClient(
        base_url="http://localhost:11434",
        model="qwen2.5:3b"
    )
    
    # 以下のコードは変更なし
    log_data = load_log()
    llm_input = st.text_area("LLMへの入力テキストを入力してください")
    llm_input = """Instructions: The following is the result of running the elevation of authority investigation script. Please output
the name of the tool or command that may be promoted.
Input:\n"""+llm_input+"\nOutput://Only the command or tool is output, no explanations, explanatory notes, or other aids are needed."
    if llm_input and st.button("LLMで解析"):
        llm_response = llm_client.generate_response(llm_input)
        if llm_response:
            st.subheader("LLMの応答:")
            st.write(llm_response)
            
            linux_paths = [line.strip() for line in llm_response.split('\n') if '/' in line]
            
            for linux_path in linux_paths:
                tool_name = linux_path.split('/')[-1]
                url = f"https://gtfobins.github.io/gtfobins/{tool_name}/"
                
                st.write(f"処理中: {tool_name}")
                
                if url in log_data:
                    st.success(f"{tool_name} - キャッシュから取得:")
                    st.code(log_data[url])
                else:
                    process_tool(tool_name, url, log_data)

    
    if log_data:
        st.subheader("保存されているコマンド履歴")
        for url, command in log_data.items():
            st.code(command)

if __name__ == "__main__":
    main()
