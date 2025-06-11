import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from seo_fetcher import get_seo_metrics
from ai_generator import generate_blog_post
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import json

load_dotenv()
app = Flask(__name__)


# Helper to strip markdown code fence if needed
def strip_leading_fence(md: str) -> str:
    lines = md.splitlines()
    if lines and lines[0].strip().startswith("```"):
        try:
            end_idx = lines.index("```", 1)
            return "\n".join(lines[1:end_idx] + lines[end_idx+1:])
        except ValueError:
            pass  # No closing fence found
    return md


@app.route("/generate", methods=["GET"])
def generate_endpoint():
    keyword = request.args.get("keyword", "").strip()
    if not keyword:
        return jsonify({"error": "Missing 'keyword' query parameter"}), 400

    # 1. Fetch SEO metrics
    seo_data = get_seo_metrics(keyword)

    # 2. Generate blog post (Markdown)
    try:
        raw_markdown = generate_blog_post(keyword, seo_data)
        blog_markdown = strip_leading_fence(raw_markdown)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    # 3. Save Markdown to file
    output_dir = "generated_posts"
    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_keyword = keyword.replace(" ", "_")
    filename = f"{safe_keyword}_{timestamp}.md"
    filepath = os.path.join(output_dir, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(blog_markdown)

    print(f"[INFO] Markdown saved to: {filepath}")

    # 4. Print and return JSON response
    response = {
        "keyword": keyword,
        "seo_data": seo_data,
        "content": blog_markdown
    }

    print("[DEBUG] Response:")
    print(json.dumps(response, indent=2, ensure_ascii=False))

    return jsonify(response), 200


def daily_job():
    PREDEFINED_KEYWORD = "wireless earbuds"
    seo_data = get_seo_metrics(PREDEFINED_KEYWORD)
    raw_markdown = generate_blog_post(PREDEFINED_KEYWORD, seo_data)
    blog_markdown = strip_leading_fence(raw_markdown)

    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"generated_{PREDEFINED_KEYWORD.replace(' ', '_')}_{date_str}.md"
    filepath = os.path.join(output_dir, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(blog_markdown)

    print(f"[INFO] Saved daily blog draft to {filepath}")


def configure_scheduler():
    scheduler = BackgroundScheduler(daemon=True)
    scheduler.add_job(daily_job, trigger="cron", hour=2, minute=0)
    scheduler.start()


if os.getenv("SCHEDULER_ENABLED", "0") == "1":
    configure_scheduler()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=True)
