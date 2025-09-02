from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import LLMChain
import json
import re
from prompts import analysis_prompt, generation_prompt, enhanced_prompt
import time

app = Flask(__name__)

# Configure CORS properly - Allow all origins for Vercel deployment
# CORS(app, 
#      origins="*",  # Allow all origins
#      methods=["GET", "POST", "OPTIONS"],
#      allow_headers=["Content-Type", "Authorization"]
# )
CORS(app, resources={r"/*": {"origins": "*"}})

load_dotenv()

# Configure Gemini API
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

# Initialize Gemini LLM for all operations using LangChain
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=GOOGLE_API_KEY, temperature=0.7)



# Create LangChain chains for all operations
print("Creating LangChain chains...")
analysis_chain = analysis_prompt | llm
generation_chain = generation_prompt | llm  
enhanced_chain = enhanced_prompt | llm
print("LangChain chains created successfully!")


@app.route('/', methods=['GET'])
def home():
    return "Flask Backend is Running!", 200

@app.route('/health', methods=['GET'])
def health_check():
    return "OK", 200

@app.route('/api/analyze-topic', methods=['POST'])
def analyze_topic():
    """Stage 1: Analyze topic and suggest dynamic input fields"""
    print("=== TOPIC ANALYSIS ENDPOINT CALLED ===")
    
    
    try:
        data = request.get_json()
        topic = data.get('topic', '').strip()
        print(f"Topic received: '{topic}'")
        
        if not topic:
            return jsonify({'error': 'Topic is required'}), 400
        
        
        print("Sending analysis prompt to LangChain...")
        
        # Call LangChain analysis chain with timing
        start_time = time.time()
        response = analysis_chain.invoke({"topic": topic})
        analysis_time = time.time() - start_time
        
        raw_response = response.content.strip()
        print(f"Raw LangChain response: {raw_response}")
        print(f"Analysis took {analysis_time:.2f} seconds")
        
        # Clean and parse the JSON response
        try:
            # Remove any markdown formatting
            clean_response = raw_response.replace('```json', '').replace('```', '').strip()
            print(f"Cleaned response: {clean_response}")
            
            # Parse JSON
            suggested_fields = json.loads(clean_response)
            print(f"Parsed suggested fields: {suggested_fields}")
            
            # Validate the structure
            if not isinstance(suggested_fields, list):
                raise ValueError("Response is not a list")
            
            # Ensure each field has required properties
            validated_fields = []
            for field in suggested_fields:
                if isinstance(field, dict) and 'field' in field and 'label' in field:
                    validated_field = {
                        'field': field.get('field', ''),
                        'label': field.get('label', ''),
                        'description': field.get('description', ''),
                        'type': field.get('type', 'text')
                    }
                    validated_fields.append(validated_field)
            
            print(f"Validated fields: {validated_fields}")
            
            if not validated_fields:
                # Fallback fields if parsing fails
                validated_fields = [
                    {"field": "specific_details", "label": "Specific Details", "description": "Add specific details about your topic", "type": "textarea"},
                    {"field": "personal_impact", "label": "Personal Impact", "description": "How did this impact you personally?", "type": "text"}
                ]
                print("Using fallback fields due to parsing issues")
            
            return jsonify({
                'suggested_fields': validated_fields,
                'topic': topic,
                'metrics': {
                    'analysis_time': round(analysis_time, 2),
                    'estimated_tokens': len(raw_response.split()),
                    'estimated_cost': round(len(raw_response.split()) * 0.0001, 4)  # Rough estimate
                }
            })
            
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {str(e)}")
            print(f"Attempted to parse: {clean_response}")
            
            # Fallback: provide default fields based on common patterns
            fallback_fields = [
                {"field": "specific_details", "label": "Specific Details", "description": f"Add specific details about your {topic}", "type": "textarea"},
                {"field": "key_impact", "label": "Key Impact", "description": "What was the main impact or outcome?", "type": "text"},
                {"field": "personal_reflection", "label": "Personal Reflection", "description": "What did you learn or how did you grow?", "type": "text"}
            ]
            
            return jsonify({
                'suggested_fields': fallback_fields,
                'topic': topic,
                'note': 'Using fallback fields due to parsing issues',
                'metrics': {
                    'analysis_time': round(analysis_time, 2),
                    'estimated_tokens': len(clean_response.split()),
                    'estimated_cost': round(len(clean_response.split()) * 0.0001, 4)
                }
            })
        
    except Exception as e:
        print(f"Error in topic analysis: {str(e)}")
        return jsonify({'error': f'Topic analysis failed: {str(e)}'}), 500

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
        # Run the generation LLMChain with timing
        print("Using generation_chain for basic post generation...")
        start_time = time.time()
        result = generation_chain.invoke({
            "topic": topic,
            "tone": tone,
            "post_length": post_length,
            "hashtags": hashtags
        })
        generation_time = time.time() - start_time

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
        
        # Calculate metrics
        total_tokens = len(generated_text.split())
        estimated_cost = round(total_tokens * 0.0001, 4)
        
        return jsonify({
            'posts': posts,
            'metrics': {
                'generation_time': round(generation_time, 2),
                'total_tokens': total_tokens,
                'estimated_cost': estimated_cost,
                'posts_generated': len(posts)
            }
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500 #Return an error message

@app.route('/api/generate-enhanced', methods=['POST'])
def generate_enhanced_posts():
    """Stage 2: Generate posts using enhanced context from user input"""
    print("=== ENHANCED GENERATION ENDPOINT CALLED ===")
    
    try:
        data = request.get_json()
        topic = data.get('topic', '').strip()
        options = data.get('options', {})
        enhanced_fields = data.get('enhanced_fields', {})
        
        print(f"Topic: {topic}")
        print(f"Options: {options}")
        print(f"Enhanced fields: {enhanced_fields}")
        
        if not topic:
            return jsonify({'error': 'Topic is required'}), 400
        
        # Extract basic options
        tone = options.get('tone', 'professional')
        post_length = options.get('post_length', 'medium')
        hashtags = options.get('hashtags', '#linkedin #socialmedia')
        
        # Build enhanced context from user-provided fields
        enhanced_context_parts = []
        for field_name, field_value in enhanced_fields.items():
            if field_value and str(field_value).strip():
                # Convert field names to readable format
                readable_name = field_name.replace('_', ' ').title()
                enhanced_context_parts.append(f"- {readable_name}: {field_value}")
        
        enhanced_context = "\n".join(enhanced_context_parts) if enhanced_context_parts else "No additional context provided."
        
        print(f"Enhanced context: {enhanced_context}")
        
        # Use enhanced chain if we have additional context, otherwise use basic generation
        start_time = time.time()
        if enhanced_context_parts:
            print("Using enhanced_chain for personalized post generation...")
            result = enhanced_chain.invoke({
                "topic": topic,
                "tone": tone,
                "post_length": post_length,
                "hashtags": hashtags,
                "enhanced_context": enhanced_context
            })
        else:
            print("No enhanced context, using basic generation_chain...")
            result = generation_chain.invoke({
                "topic": topic,
                "tone": tone,
                "post_length": post_length,
                "hashtags": hashtags
            })
        generation_time = time.time() - start_time
        
        # Parse the AI response to extract clean posts (same logic as basic generation)
        generated_text = result.content
        print(f"Raw enhanced AI response: {generated_text}")
        
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
        
        print(f"Final enhanced posts: {posts}")
        
        # Calculate metrics
        total_tokens = len(generated_text.split())
        estimated_cost = round(total_tokens * 0.0001, 4)
        
        return jsonify({
            'posts': posts,
            'enhanced': bool(enhanced_context_parts),
            'context_used': enhanced_context,
            'metrics': {
                'generation_time': round(generation_time, 2),
                'total_tokens': total_tokens,
                'estimated_cost': estimated_cost,
                'posts_generated': len(posts),
                'enhanced_fields_used': len(enhanced_context_parts)
            }
        })
        
    except Exception as e:
        print(f"Error in enhanced generation: {str(e)}")
        return jsonify({'error': f'Enhanced generation failed: {str(e)}'}), 500

# For Vercel, we don't need the if __name__ == '__main__' block
# The app is imported directly

if __name__ == '__main__':
    app.run(debug=True, port=5000)