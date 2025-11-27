from flask import Flask, render_template, request, jsonify, Response, stream_with_context
import requests
import json
import base64
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API_KEY")

app = Flask(__name__)

def encode_image_to_base64(image_path):
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode('utf-8')

def completion(model_name, text_msg, image_data=None):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    content = [{"type": "text", "text": text_msg}]
    
    if image_data:
        content.append({
            "type": "image_url",
            "image_url": {"url": image_data}
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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    message = data.get('message', '')
    model = data.get('model', 'openai/gpt-3.5-turbo')
    image_data = data.get('image')
    
    def generate():
        try:
            for chunk in completion(model, message, image_data):
                yield f"data: {json.dumps({'content': chunk})}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return Response(stream_with_context(generate()), mimetype='text/event-stream')

@app.route('/models')
def models():
    try:
        with open("config.json", "r") as f:
            data = json.load(f)

        llms = data.get("llms", {})

        # Turn this:
        #   "gemma-3": { by:"google", url:"...", short:"general" }
        #
        # Into this:
        #   [{ "id":"gemma-3", "by":"google", "url": "...", "short":"general" }, ...]
        #
        models_list = []
        for model_id, info in llms.items():
            entry = {
                "key": info.get("url", model_id),
                "id": model_id,
                "by": info.get("by", ""),
                "name": info.get("name", ""),
                "short": info.get("short", "")
            }
            models_list.append(entry)

        return jsonify(models_list)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')