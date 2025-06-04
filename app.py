# app.py

import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from seo_fetcher import get_seo_metrics
from ai_generator import generate_blog_post

# Optionally, for APScheduler
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime

load_dotenv()

app = Flask(__name__)

# ----------------------------------------------------------
# 1) Define the /generate endpoint
# ----------------------------------------------------------
@app.route("/generate", methods=["GET"])
def generate_endpoint():
    keyword = request.args.get("keyword", "").strip()
    if not keyword:
        return jsonify({"error": "Missing 'keyword' query parameter"}), 400

    # 1. Fetch SEO metrics (mock or real)
    seo_data = get_seo_metrics(keyword)

    # 2. Generate blog post (Markdown)
    try:
        blog_markdown = generate_blog_post(keyword, seo_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    # 3. Build JSON response
    response = {
        "keyword": keyword,
        "seo_data": seo_data,
        "content": blog_markdown
    }
    return jsonify(response), 200


# ----------------------------------------------------------
# 2) (Optional) APScheduler setup to generate daily automatically
# ----------------------------------------------------------
def daily_job():
    """
    Example: Generate for a predefined keyword each day and save to disk.
    """
    PREDEFINED_KEYWORD = "wireless earbuds"
    seo_data = get_seo_metrics(PREDEFINED_KEYWORD)
    blog_markdown = generate_blog_post(PREDEFINED_KEYWORD, seo_data)

    # Create a timestamped filename
    date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"generated_{PREDEFINED_KEYWORD.replace(' ', '_')}_{date_str}.md"

    # Save to a local file
    with open(filename, "w") as f:
        f.write(blog_markdown)
    print(f"Saved daily blog draft to ./{filename}")


def configure_scheduler():
    scheduler = BackgroundScheduler(daemon=True)
    # Run once every day at 02:00 AM server time (adjust as desired)
    scheduler.add_job(daily_job, trigger="cron", hour=2, minute=0)
    scheduler.start()


# Only configure scheduler if explicitly desired (set env var SCHEDULER=1)
if os.getenv("SCHEDULER_ENABLED", "0") == "1":
    configure_scheduler()


if __name__ == "__main__":
    # For local testing, default port 80
    app.run(host="0.0.0.0", port=80, debug=True)
