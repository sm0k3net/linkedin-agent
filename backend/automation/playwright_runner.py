import logging
import json
import random
import time
from datetime import datetime, timedelta
from backend.config import Config
from backend.models import AgentLog, db
from backend.automation.deepseek_integration import generate_content

def run_agent(topics, behavior_json):
    from playwright.sync_api import sync_playwright

    try:
        behavior = json.loads(behavior_json) if behavior_json else {}
    except Exception as e:
        logging.error(f"Invalid behavior JSON: {behavior_json} ({e})")
        behavior = {}

    actions_count = {"like": 0, "follow": 0, "comment": 0, "post": 0, "connect": 0}
    topics_list = [t.strip() for t in topics.split(",") if t.strip()]
    logging.info(f"Topics to process: {topics_list}")

    if not topics_list:
        logging.warning("No topics provided. Exiting agent.")
        return actions_count

    now = datetime.now()
    post_time = now.replace(hour=random.randint(8, 22), minute=random.randint(0, 59), second=0, microsecond=0)
    if post_time < now:
        post_time += timedelta(days=1)

    try:
        with sync_playwright() as p:
            logging.info("Launching browser...")
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            logging.info("Navigating to LinkedIn login...")
            page.goto("https://www.linkedin.com/login")
            page.fill('input[name="session_key"]', Config.LINKEDIN_EMAIL)
            page.fill('input[name="session_password"]', Config.LINKEDIN_PASSWORD)
            page.click('button[type="submit"]')
            page.wait_for_load_state("networkidle")
            time.sleep(3)
            logging.info(f"Logged in. Current URL: {page.url}")

            if "feed" not in page.url:
                logging.error("Login failed or captcha encountered. Exiting agent.")
                return actions_count

            page.goto("https://www.linkedin.com/feed/")
            page.wait_for_load_state("networkidle")
            time.sleep(3)
            logging.info("On main feed.")

            posts = page.query_selector_all('div.fie-impression-container')
            logging.info(f"Found {len(posts)} posts in feed.")

            max_posts = behavior.get("max_posts", 2)
            for idx, post in enumerate(posts):
                if idx >= max_posts:
                    break

                try:
                    post_text_elem = post.query_selector('span.break-words')
                    post_text = post_text_elem.inner_text().lower() if post_text_elem else ""
                except Exception:
                    post_text = ""

                if not any(topic.lower() in post_text for topic in topics_list):
                    logging.info(f"Post {idx+1} not relevant to topics, skipping.")
                    continue

                logging.info(f"Interacting with post {idx+1} relevant to topics.")

                # Like
                try:
                    like_btn = post.query_selector('button[aria-label*="React Like"]')
                    if like_btn:
                        like_btn.click()
                        actions_count["like"] += 1
                        db.session.add(AgentLog(action="like", target=post_text[:100]))
                        db.session.commit()
                        logging.info("Liked a post.")
                        time.sleep(random.uniform(1, 2))
                    else:
                        logging.info("Like button not found or already liked.")
                except Exception as e:
                    logging.warning(f"Like failed: {e}")

                # Follow
                try:
                    follow_btn = post.query_selector('button.follow')
                    if follow_btn:
                        follow_btn.click()
                        actions_count["follow"] += 1
                        db.session.add(AgentLog(action="follow", target=post_text[:100]))
                        db.session.commit()
                        logging.info("Followed a user.")
                        time.sleep(random.uniform(1, 2))
                    else:
                        logging.info("Follow button not found for this post.")
                except Exception as e:
                    logging.warning(f"Follow failed: {e}")

                # Comment
                try:
                    if behavior.get("comment", True):
                        comment_btn = post.query_selector('button.comment-button')
                        if comment_btn:
                            comment_btn.click()
                            time.sleep(1)
                            comment_area = post.query_selector('textarea')
                            if comment_area:
                                prompt = behavior.get("comment_prompt", f"Write a relevant, interesting question or feedback about this post: {post_text[:100]}")
                                logging.info(f"Generating comment with prompt: {prompt}")
                                comment = generate_content(prompt, min_words=20, max_words=50)
                                comment_area.fill(comment)
                                submit_btn = post.query_selector('button[aria-label*="Post comment"]')
                                if submit_btn:
                                    submit_btn.click()
                                    actions_count["comment"] += 1
                                    db.session.add(AgentLog(action="comment", target=post_text[:100], extra=comment))
                                    db.session.commit()
                                    logging.info("Commented on a post.")
                                    time.sleep(random.uniform(1, 2))
                                else:
                                    logging.info("Submit comment button not found.")
                            else:
                                logging.info("Comment area not found.")
                        else:
                            logging.info("Comment button not found for this post.")
                except Exception as e:
                    logging.warning(f"Comment failed: {e}")

            # Randomly connect with people (1-12 per day)
            try:
                num_connections = random.randint(1, 12)
                logging.info(f"Attempting to connect with {num_connections} people.")
                page.goto("https://www.linkedin.com/mynetwork/")
                page.wait_for_load_state("networkidle")
                time.sleep(2)
                connect_buttons = page.query_selector_all('button[aria-label^="Connect with"]')
                logging.info(f"Found {len(connect_buttons)} connect buttons.")
                for btn in random.sample(connect_buttons, min(num_connections, len(connect_buttons))):
                    try:
                        btn.click()
                        actions_count["connect"] += 1
                        db.session.add(AgentLog(action="connect", target="random"))
                        db.session.commit()
                        logging.info("Sent connection request.")
                        time.sleep(random.uniform(2, 4))
                    except Exception as e:
                        logging.warning(f"Connection request failed: {e}")
            except Exception as e:
                logging.warning(f"Connecting with people failed: {e}")

            # Post an article at a random time (simulate scheduling)
            try:
                now = datetime.now()
                wait_seconds = (post_time - now).total_seconds()
                if wait_seconds > 0:
                    logging.info(f"Waiting {int(wait_seconds)} seconds to post article at {post_time.strftime('%H:%M')}")
                    time.sleep(min(wait_seconds, 60))
                topic = random.choice(topics_list)
                prompt = f"Write a LinkedIn article about {topic} with relevant hashtags. The article should be at least 600 words and up to 1200 words. Make it insightful and engaging."
                logging.info(f"Generating article with prompt: {prompt}")
                article = generate_content(prompt, min_words=600, max_words=1200)
                logging.info("Generated article for posting.")

                page.goto("https://www.linkedin.com/feed/")
                page.wait_for_load_state("networkidle")
                time.sleep(2)
                start_post_btn = page.query_selector('button.share-box-feed-entry__trigger')
                if start_post_btn:
                    logging.info("Start post button found, clicking...")
                    start_post_btn.click()
                    time.sleep(2)
                    textarea = page.query_selector('div.ql-editor')
                    if textarea:
                        logging.info("Textarea found, filling with article...")
                        textarea.fill(article)
                        post_btn = page.query_selector('button.share-actions__primary-action')
                        if post_btn:
                            logging.info("Post button found, clicking...")
                            post_btn.click()
                            actions_count["post"] += 1
                            db.session.add(AgentLog(action="post", target=topic, extra=article[:100]))
                            db.session.commit()
                            logging.info("Posted an article.")
                            time.sleep(2)
                        else:
                            logging.info("Post button not found.")
                    else:
                        logging.info("Textarea for post not found.")
                else:
                    logging.info("Start post button not found.")
            except Exception as e:
                logging.warning(f"Posting article failed: {e}")

            logging.info(f"Actions summary: {actions_count}")
            browser.close()
    except Exception as e:
        logging.error(f"Agent crashed: {e}")

    return actions_count