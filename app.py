# app.py

import os
from flask import Flask, request, abort
from dotenv import load_dotenv
from seo_fetcher import get_seo_metrics
from ai_generator import generate_blog_post

# Optionally, for APScheduler
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime

load_dotenv()

app = Flask(__name__)

def strip_leading_fence(md: str) -> str:
    """
    If the Markdown starts with ```markdown (or just ```), remove that opening fence
    and the corresponding closing fence at the end.
    """
    lines = md.splitlines()
    if not lines:
        return md

    # Check for an opening fence of the form ```markdown or ``` 
    first_line = lines[0].strip()
    if first_line.startswith("```"):
        # Find where the opening fence ends (skip exactly that line)
        # Then find a matching closing ``` somewhere below.
        closing_index = None
        for i in range(1, len(lines)):
            if lines[i].strip() == "```":
                closing_index = i
                break

        # If we found a closing fence, drop both fences.
        if closing_index is not None:
            # Keep everything between line 1 and closing_index (exclusive),
            # then append any remaining lines after closing fence.
            body_lines = lines[1:closing_index]
            tail_lines = lines[closing_index+1 :]
            return "\n".join(body_lines + tail_lines)

    # If it doesn’t start with ``` or no matching closing fence, return as-is
    return md


# ----------------------------------------------------------
# 1) Define the /generate endpoint (returns raw Markdown inline)
# ----------------------------------------------------------
@app.route("/generate", methods=["GET"])
def generate_endpoint():
    keyword = request.args.get("keyword", "").strip()
    if not keyword:
        return abort(400, description="Missing 'keyword' query parameter")

    # 1. Fetch SEO metrics (mock or real)
    seo_data = get_seo_metrics(keyword)

    # 2. Generate blog post (Markdown)
    try:
        raw_markdown = generate_blog_post(keyword, seo_data)
    except Exception as e:
        return abort(500, description=str(e))

    # 2a. Strip any leading/trailing ```markdown fences
    blog_markdown = strip_leading_fence(raw_markdown)

    # 3. Save the resulting Markdown to disk
    output_dir = "generated_posts"
    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_keyword = keyword.replace(" ", "_")
    filename = f"{safe_keyword}_{timestamp}.md"
    filepath = os.path.join(output_dir, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(blog_markdown)
    app.logger.info(f"Saved generated markdown to {filepath}")

    # 4. Return the raw Markdown text (inline) with Content-Type: text/markdown
    return blog_markdown, 200, {"Content-Type": "text/markdown"}


# ----------------------------------------------------------
# 2) (Optional) APScheduler setup to generate daily automatically
# ----------------------------------------------------------
def daily_job():
    """
    Example: Generate for a predefined keyword each day and save to disk.
    """
    PREDEFINED_KEYWORD = "wireless earbuds"
    seo_data = get_seo_metrics(PREDEFINED_KEYWORD)
    raw_markdown = generate_blog_post(PREDEFINED_KEYWORD, seo_data)
    blog_md = strip_leading_fence(raw_markdown)

    date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"generated_{PREDEFINED_KEYWORD.replace(' ', '_')}_{date_str}.md"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(blog_md)
    print(f"Saved daily blog draft to ./{filename}")


def configure_scheduler():
    scheduler = BackgroundScheduler(daemon=True)
    # Run once every day at 02:00 AM server time (adjust as desired)
    scheduler.add_job(daily_job, trigger="cron", hour=2, minute=0)
    scheduler.start()


# Only configure scheduler if explicitly desired (set env var SCHEDULER_ENABLED=1)
if os.getenv("SCHEDULER_ENABLED", "0") == "1":
    configure_scheduler()


if __name__ == "__main__":
    # For local testing, default port 80
    app.run(host="0.0.0.0", port=80, debug=True)
