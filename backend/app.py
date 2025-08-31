from flask import Flask, request, jsonify
from flask_cors import CORS  # Import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/health', methods=['GET'])
def health_check():
    return "OK", 200

@app.route('/api/generate', methods=['POST'])
def generate_posts():
    data = request.get_json()
    topic = data['topic']
    options = data['options']

    # Replace this with your AI agent logic to generate posts
    # Example:
    # generated_posts = ai_agent.generate(topic, options)

    # For now, return some dummy posts
    generated_posts = [
        f"Dummy post 1 about {topic} with tone: {options['tone']}",
        f"Dummy post 2 about {topic} with tone: {options['tone']}",
        f"Dummy post 3 about {topic} with tone: {options['tone']}"
    ]

    return jsonify({'posts': generated_posts})

if __name__ == '__main__':
    app.run(debug=True, port=5000) # Or your desired port