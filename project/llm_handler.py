import requests
from config import OLLAMA_HOST, MODEL_NAME
import numpy as np
class LLMHandler:
    def __init__(self):
        self.base_url = OLLAMA_HOST
        self.model = MODEL_NAME
    
    def get_embedding(self, text):
        response = requests.post(
            f"{self.base_url}/api/embeddings",
            json={"model": MODEL_NAME, "prompt": text}
        )
        embedding = response.json()['embedding']
        return np.array(embedding, dtype=np.float32)  # NumPy配列に変換


    
    def generate_response(self, prompt, context=""):
        print(f'context:  {context}')
        print(f'prompt:  {prompt}')
    
 
        response = requests.post(
            f"{self.base_url}/api/chat",
            json={
                "model": self.model,
                "options":{"temperature":0},
                "messages": [
                    {"role": "user", "content": prompt},
                    {"role": "system", "content": context}
                ],
                "stream": False
            }
        )
        return response.json()['message']['content']
