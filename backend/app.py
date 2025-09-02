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
CORS(app)
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
Generate 3 LinkedIn post options about the following topic, making them engaging and professional.
Topic: {topic}
Tone: {tone}
Post Length: {post_length}
Hashtags: {hashtags}
"""

prompt = PromptTemplate(
    input_variables=["topic", "tone", "post_length", "hashtags"],
    template=prompt_template
)

# Create LLMChain
chain = prompt | llm


@app.route('/health', methods=['GET'])
def health_check():
    return "OK", 200

@app.route('/api/generate', methods=['POST'])
def generate_posts():
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

        generated_posts = result.content.split("\n\n")[:3]
        print(f"Generated posts: {generated_posts}")

        return jsonify({'posts': generated_posts})

    except Exception as e:
        return jsonify({'error': str(e)}), 500 #Return an error message


if __name__ == '__main__':
    app.run(debug=True, port=5000)