"""
LinkedIn Post Generator Prompt Templates
This module contains all the prompt templates used for generating LinkedIn posts.
"""

from langchain.prompts import PromptTemplate

# Stage 1: Topic Analysis Template
analysis_template = """
You are a LinkedIn content strategist. Analyze the given topic and suggest specific input fields that would help create more personalized LinkedIn posts.

Topic: {topic}

Based on this topic, suggest 3-5 specific input fields that would help create more authentic and engaging LinkedIn posts.

Return your response as a valid JSON array with this exact format:
[
    {{"field": "field_name", "label": "Display Label", "description": "Helper text for user", "type": "text"}},
    {{"field": "field_name2", "label": "Display Label 2", "description": "Helper text", "type": "textarea"}}
]

Field types can be: "text", "textarea", "number"

Examples of good fields for different topics:
- Internship: company_name, skills_learned, duration, key_projects
- Job change: previous_role, new_company, career_growth, motivation  
- Achievement: accomplishment_details, impact_numbers, team_size, timeline
- Event: event_name, key_takeaways, networking_value, future_plans

Only return the JSON array, no other text.
"""

# Stage 2: Basic Post Generation Template
generation_template = """
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

# Stage 3: Enhanced Post Generation Template (with additional fields)
enhanced_template = """
You are a social media expert creating personalized LinkedIn content.

Generate exactly 3 LinkedIn post options using the provided information:

Basic Information:
- Topic: {topic}
- Tone: {tone}
- Post Length: {post_length}
- Hashtags: {hashtags}

Additional Context:
{enhanced_context}

Use the additional context to make the posts more specific, authentic, and engaging. Incorporate the details naturally into compelling LinkedIn posts.

Please format your response as follows - each post should be separated by "---":
POST 1: [write the first personalized post here]
---
POST 2: [write the second personalized post here]  
---
POST 3: [write the third personalized post here]

Make sure each post feels authentic and includes specific details from the additional context.
"""

# Create PromptTemplate objects
analysis_prompt = PromptTemplate(
    input_variables=["topic"],
    template=analysis_template
)

generation_prompt = PromptTemplate(
    input_variables=["topic", "tone", "post_length", "hashtags"],
    template=generation_template
)

enhanced_prompt = PromptTemplate(
    input_variables=["topic", "tone", "post_length", "hashtags", "enhanced_context"],
    template=enhanced_template
)