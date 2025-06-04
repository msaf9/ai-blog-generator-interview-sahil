# ai_generator.py

import os
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")

AFF_LINK_PLACEHOLDERS = ["{{AFF_LINK_1}}", "{{AFF_LINK_2}}", "{{AFF_LINK_3}}"]

def build_prompt(keyword: str, seo_data: dict) -> str:
    """
    Construct a structured prompt that:
    - Mentions keyword
    - Mentions SEO metrics
    - Asks for a blog structure (Header, Intro, 3–5 sections, Conclusion)
    - Asks to insert placeholders {{AFF_LINK_n}}.
    Returns the prompt as a string.
    """
    prompt = f"""
You are an SEO‐savvy content writer and marketer. You have the following SEO data for the keyword "{keyword}":
- Search Volume: {seo_data['search_volume']} searches/month
- Keyword Difficulty: {seo_data['keyword_difficulty']} (scale 0-100)
- Average CPC: ${seo_data['avg_cpc']}

Please generate a detailed blog post draft (in Markdown) optimized for the above keyword. The post should include:
1. A clear title using the keyword
2. An introduction that hooks readers
3. 3–5 subheadings/sections with explanatory paragraphs
4. A conclusion
5. Within the body, insert affiliate link placeholders {{AFF_LINK_1}}, {{AFF_LINK_2}}, and {{AFF_LINK_3}} in logical places with dummy URLs (e.g., https://example.com/product1) for future affiliate links.

Output only the Markdown for the blog post. Do not include any additional commentary or explanations outside of the blog post itself.
    """
    return prompt.strip()

def generate_blog_post(keyword: str, seo_data: dict) -> str:
    """
    Calls OpenAI’s chat‐completions endpoint to generate the blog post.
    Returns the raw Markdown string (with placeholders).
    """
    prompt = build_prompt(keyword, seo_data)

    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",   # or "gpt-3.5-turbo"
        messages=[
            { "role": "system", "content": "You are a helpful assistant." },
            { "role": "user",   "content": prompt }
        ],
        temperature=0.7,
        max_tokens=1200
    )

    markdown_content = response.choices[0].message.content.strip()
    return markdown_content
