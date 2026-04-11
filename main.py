import os
from flask import Flask, jsonify
from flask_cors import CORS
import requests
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    with open('index.html', 'r') as f:
        return f.read()

@app.route('/api/generate-story', methods=['POST'])
def generate_story():
    try:
        from flask import request
        data = request.get_json()
        prompt = data.get('prompt', '')
        
        if not prompt:
            return jsonify({'error': 'Prompt is required'}), 400
        
        api_key = os.getenv('OPENROUTER_API_KEY')
        
        if not api_key:
            return jsonify({'error': 'API key not configured'}), 500
        
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'HTTP-Referer': 'https://localhost:5000'
        }
        
        payload = {
            'model': 'meta-llama/llama-3-8b-instruct',
            'messages': [
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            'max_tokens': 1500
        }
        
        response = requests.post(
            'https://openrouter.ai/api/v1/chat/completions',
            headers=headers,
            json=payload,
            timeout=120
        )
        
        if response.status_code != 200:
            return jsonify({'error': f'API Error: {response.status_code}'}), 500
        
        result = response.json()
        
        if 'choices' in result and len(result['choices']) > 0:
            story = result['choices'][0]['message']['content']
            return jsonify({
                'success': True,
                'story': story,
                'prompt': prompt,
                'genre': data.get('genre', 'fantasy'),
                'tone': data.get('tone', 'adventurous')
            }), 200
        
        return jsonify({'error': 'No story generated'}), 500
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)