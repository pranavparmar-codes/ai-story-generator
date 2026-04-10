from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)

# API key from environment variable
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Homepage route (frontend)
@app.route("/")
def home():
    return render_template("index.html")

# Story generation API
@app.route('/api/generate-story', methods=['POST'])
def generate_story():
    try:
        data = request.json
        prompt = data.get('prompt', '')
        tone = data.get('tone', 'adventure')
        genre = data.get('genre', 'fantasy')
        length = data.get('length', 'medium')

        if not prompt:
            return jsonify({'error': 'Prompt is required'}), 400

        length_params = {
            'short': (200, 300),
            'medium': (500, 800),
            'long': (1000, 1500)
        }

        min_words, max_words = length_params.get(length, (500, 800))

        system_prompt = f"""
You are a creative storyteller.

Tone: {tone}
Genre: {genre}
Length: {min_words}-{max_words} words

Write an engaging story with vivid descriptions, interesting characters,
and a compelling plot.
"""

        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "HTTP-Referer": "https://ai-story-generator",
            "X-Title": "AI Story Generator"
        }

        payload = {
            "model": "meta-llama/llama-3-8b-instruct",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Write a story about: {prompt}"}
            ],
            "temperature": 0.7,
            "max_tokens": 2000
        }

        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload
        )

        result = response.json()

        if response.status_code != 200:
            return jsonify({'error': result}), 500

        story = result['choices'][0]['message']['content']

        return jsonify({
            "success": True,
            "story": story
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Health check
@app.route("/api/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)