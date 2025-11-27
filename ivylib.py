import requests
import json
import base64
import os
from dotenv import load_dotenv
load_dotenv()

API_KEY = os.getenv("API_KEY")

def encode_image_to_base64(image_path):
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode('utf-8')

def completion(model_name, text_msg, image_path=None):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    content = [{"type": "text", "text": text_msg}]
    if image_path:
        b64_image = encode_image_to_base64(image_path)
        data_url = f"data:image/jpeg;base64,{b64_image}"
        content.append({
            "type": "image_url",
            "image_url": {"url": data_url}
        })

    messages = [{"role": "user", "content": content}]
    payload = {
        "model": model_name,
        "messages": messages,
        "stream": True
    }

    with requests.post(url, headers=headers, json=payload, stream=True) as resp:
        if resp.status_code != 200:
            raise Exception(f"OpenRouter error {resp.status_code}: {resp.text}")

        for line in resp.iter_lines():
            if line:
                decoded = line.decode('utf-8')
                if decoded.startswith("data: "):
                    data_json = decoded[len("data: "):].strip()
                    if data_json == "[DONE]":
                        break
                    try:
                        chunk = json.loads(data_json)
                        content_chunk = chunk["choices"][0]["delta"].get("content")
                        if content_chunk:
                            yield content_chunk
                    except json.JSONDecodeError:
                        continue
