from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

# Your OpenRouter API Key
OPENROUTER_API_KEY = "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"

@app.route('/api/generate-story', methods=['POST'])
def generate_story():
    """Generate a story based on user input using OpenRouter"""
    try:
        data = request.json
        prompt = data.get('prompt', '')
        tone = data.get('tone', 'adventure')
        genre = data.get('genre', 'fantasy')
        length = data.get('length', 'medium')
        
        if not prompt:
            return jsonify({'error': 'Prompt is required'}), 400
        
        # Define length parameters
        length_params = {
            'short': (200, 300),
            'medium': (500, 800),
            'long': (1000, 1500)
        }
        
        min_words, max_words = length_params.get(length, (500, 800))
        
        # Construct the system prompt
        system_prompt = f"""You are a creative storyteller. Generate engaging stories with the following characteristics:
- Tone: {tone}
- Genre: {genre}
- Length: approximately {min_words}-{max_words} words
- Make the story vivid, engaging, and entertaining
- Include interesting characters and plot development
- Create immersive descriptions"""
        
        # Call OpenRouter API
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "HTTP-Referer": "http://localhost:5000",
            "X-Title": "AI Story Generator"
        }
        
        data_payload = {
            "model": "meta-llama/llama-3-8b-instruct",  # Free model!
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": f"Write a story about: {prompt}"
                }
            ],
            "max_tokens": 2000,
            "temperature": 0.7
        }
        
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=data_payload
        )
        
        if response.status_code != 200:
            error_msg = response.json().get('error', {}).get('message', 'Unknown error')
            return jsonify({'error': f'API Error: {error_msg}'}), 500
        
        result = response.json()
        story = result['choices'][0]['message']['content']
        
        return jsonify({
            'success': True,
            'story': story,
            'prompt': prompt,
            'tone': tone,
            'genre': genre
        })
    
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Network error: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Error generating story: {str(e)}'}), 500

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)