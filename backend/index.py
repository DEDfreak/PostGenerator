from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
import google.generativeai as genai
from langchain.prompts import PromptTemplate
#from langchain.llms import Gemini #Old broken import
# from langchain_community.chat_models import ChatGoogleGenerativeAI #NEW IMPORT
from langchain_google_genai import ChatGoogleGenerativeAI

from langchain.chains import LLMChain

app = Flask(__name__)

# Configure CORS properly - Allow all origins for Vercel deployment
CORS(app, 
     origins="*",  # Allow all origins
     methods=["GET", "POST", "OPTIONS"],
     allow_headers=["Content-Type", "Authorization"]
)

load_dotenv()

# Configure Gemini API
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

# Initialize Gemini LLM
#llm = Gemini(model="gemini-pro", google_api_key=GOOGLE_API_KEY, temperature=0.7) # OLD CODE, Broken
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=GOOGLE_API_KEY, temperature=0.7) #New code.

# Define the prompt template
prompt_template = """
You are a social media expert.
Generate exactly 3 LinkedIn post options about the following topic, making them engaging and professional.

Topic: {topic}
Tone: {tone}
Post Length: {post_length}
Include these hashtags: {hashtags}

Please format your response as follows - each post should be separated by "---":
POST 1: [write the first post here]
---
POST 2: [write the second post here]
---
POST 3: [write the third post here]

Make sure each post is complete and ready to publish on LinkedIn.
"""

prompt = PromptTemplate(
    input_variables=["topic", "tone", "post_length", "hashtags"],
    template=prompt_template
)

# Create LLMChain
chain = prompt | llm


@app.route('/', methods=['GET'])
def home():
    return "Flask Backend is Running!", 200

@app.route('/health', methods=['GET'])
def health_check():
    return "OK", 200

@app.route('/api/generate', methods=['POST', 'OPTIONS'])
def generate_posts():
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'OK'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
        return response
    data = request.get_json()
    topic = data['topic']
    options = data['options']

    tone = options.get('tone', 'professional') #Default tone to professional if not supplied
    post_length = options.get('post_length', 'medium') #Similar default
    hashtags = options.get('hashtags', '#linkedin #socialmedia')
    print(f"Generating posts for topic: {topic}, tone: {tone}, post_length: {post_length}, hashtags: {hashtags}")
    try:
        # Run the LLMChain
        result = chain.invoke({
            "topic": topic,
            "tone": tone,
            "post_length": post_length,
            "hashtags": hashtags
        })

        # Parse the AI response to extract clean posts
        generated_text = result.content
        print(f"Raw AI response: {generated_text}")
        
        # Split by "---" to get individual posts
        if "---" in generated_text:
            raw_posts = generated_text.split("---")
            posts = []
            for post in raw_posts:
                # Clean up each post
                cleaned_post = post.strip()
                # Remove "POST 1:", "POST 2:", etc. prefixes
                if cleaned_post.startswith(("POST 1:", "POST 2:", "POST 3:")):
                    cleaned_post = cleaned_post.split(":", 1)[1].strip()
                # Remove any leading/trailing brackets
                cleaned_post = cleaned_post.strip("[]")
                if cleaned_post:  # Only add non-empty posts
                    posts.append(cleaned_post)
        else:
            # Fallback: split by double newlines if no "---" found
            posts = [post.strip() for post in generated_text.split("\n\n") if post.strip()]
        
        # Ensure we have exactly 3 posts
        posts = posts[:3]  # Take only first 3
        while len(posts) < 3:  # Add fallback posts if needed
            posts.append(f"Here's a professional post about {topic} with a {tone} tone. {hashtags}")
        
        print(f"Cleaned posts: {posts}")
        return jsonify({'posts': posts})

    except Exception as e:
        return jsonify({'error': str(e)}), 500 #Return an error message


# For Vercel, we don't need the if __name__ == '__main__' block
# The app is imported directly

if __name__ == '__main__':
    app.run(debug=True, port=5000)