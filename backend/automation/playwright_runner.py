# backend/automation/playwright_runner.py

import logging
import json
from backend.config import Config
from backend.models import AgentLog, db
from backend.automation.deepseek_integration import generate_content

def run_agent(topics, behavior_json):
    from playwright.sync_api import sync_playwright
    import time

    behavior = json.loads(behavior_json) if behavior_json else {}
    actions_count = {"like": 0, "follow": 0, "comment": 0}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        # Login
        page.goto("https://www.linkedin.com/login")
        page.fill('input[name="session_key"]', Config.LINKEDIN_EMAIL)
        page.fill('input[name="session_password"]', Config.LINKEDIN_PASSWORD)
        page.click('button[type="submit"]')
        page.wait_for_load_state("networkidle")
        time.sleep(2)

        for topic in topics.split(","):
            search_url = f"https://www.linkedin.com/search/results/content/?keywords={topic.strip()}"
            page.goto(search_url)
            page.wait_for_load_state("networkidle")
            time.sleep(2)
            posts = page.query_selector_all('div.feed-shared-update-v2')
            for post in posts[:behavior.get("max_posts", 2)]:
                # Like
                try:
                    like_btn = post.query_selector('button[aria-label*="Like"]')
                    if like_btn:
                        like_btn.click()
                        actions_count["like"] += 1
                        db.session.add(AgentLog(action="like", target=topic))
                        db.session.commit()
                        time.sleep(1)
                except Exception as e:
                    logging.warning(f"Like failed: {e}")

                # Follow
                try:
                    follow_btn = post.query_selector('button[aria-label*="Follow"]')
                    if follow_btn:
                        follow_btn.click()
                        actions_count["follow"] += 1
                        db.session.add(AgentLog(action="follow", target=topic))
                        db.session.commit()
                        time.sleep(1)
                except Exception as e:
                    logging.warning(f"Follow failed: {e}")

                # Comment
                try:
                    if behavior.get("comment", False):
                        comment_btn = post.query_selector('button[aria-label*="Comment"]')
                        if comment_btn:
                            comment_btn.click()
                            time.sleep(1)
                            comment_area = post.query_selector('textarea')
                            if comment_area:
                                prompt = behavior.get("comment_prompt", f"Write a comment about {topic}")
                                comment = generate_content(prompt)
                                comment_area.fill(comment)
                                submit_btn = post.query_selector('button[aria-label*="Post comment"]')
                                if submit_btn:
                                    submit_btn.click()
                                    actions_count["comment"] += 1
                                    db.session.add(AgentLog(action="comment", target=topic))
                                    db.session.commit()
                                    time.sleep(1)
                except Exception as e:
                    logging.warning(f"Comment failed: {e}")

        browser.close()
    return actions_count