# ============================================================
#  script_generator.py — ChatGPT script + image prompts
# ============================================================

from openai import OpenAI
from config import OPENAI_API_KEY, GPT_MODEL, VIDEO_DURATION, NUM_IMAGE_PROMPTS
import json

client = OpenAI(api_key=OPENAI_API_KEY)


SYSTEM_PROMPT = """You are an expert YouTube scriptwriter specializing in 
short-form, highly engaging faceless video content. You write for AI voiceovers 
so avoid filler words, keep sentences punchy, and never use stage directions."""


def generate_script_and_prompts(topic: str) -> dict:
    """
    Returns a dict with:
      - title        : YouTube video title
      - description  : YouTube description (SEO-optimized)
      - tags         : list of tags
      - script       : full voiceover script
      - image_prompts: list of cinematic image prompts
    """

    user_prompt = f"""
Create a complete {VIDEO_DURATION}-second YouTube video package about: "{topic}"

Return a JSON object with exactly these keys:

{{
  "title": "Compelling SEO YouTube title (max 60 chars)",
  "description": "SEO YouTube description 150-200 words with hashtags",
  "tags": ["tag1", "tag2", ... up to 15 tags],
  "script": "Full {VIDEO_DURATION}-second voiceover script. Start with a strong hook. 
             No stage directions. Natural spoken English only.",
  "image_prompts": [
    "{NUM_IMAGE_PROMPTS} cinematic image generation prompts, one per scene. 
     Each prompt must be photorealistic, ultra-HD, include lighting + mood + style details."
  ]
}}

Return ONLY the JSON — no markdown fences, no explanation.
"""

    response = client.chat.completions.create(
        model=GPT_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": user_prompt},
        ],
        response_format={"type": "json_object"},
        temperature=0.8,
    )

    data = json.loads(response.choices[0].message.content)
    return data


def print_package(data: dict):
    print("\n" + "="*60)
    print(f"📌 TITLE:       {data['title']}")
    print(f"🏷️  TAGS:        {', '.join(data['tags'][:5])} ...")
    print(f"\n📝 SCRIPT:\n{data['script']}")
    print(f"\n🖼️  IMAGE PROMPTS:")
    for i, p in enumerate(data["image_prompts"], 1):
        print(f"  {i}. {p}")
    print("="*60 + "\n")
