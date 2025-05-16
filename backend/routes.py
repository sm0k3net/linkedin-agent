# backend/routes.py

import logging
from flask import Blueprint, jsonify, request, render_template
from backend.models import AgentConfig, AgentLog, db
from backend.automation.playwright_runner import run_agent
import threading

bp = Blueprint("routes", __name__)

agent_thread = None
agent_running = False
agent_lock = threading.Lock()

@bp.route("/")
def dashboard():
    config = AgentConfig.get_current()
    return render_template("dashboard.html", config=config)

@bp.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok"})

@bp.route("/api/config", methods=["GET", "POST"])
def agent_config():
    if request.method == "POST":
        AgentConfig.update_from_json(request.json)
        logging.info("Configuration updated: %s", request.json)
        return jsonify({"message": "Config updated"})
    config = AgentConfig.get_current()
    return jsonify({
        "topics": config.topics,
        "behavior": config.behavior
    })

@bp.route("/api/start", methods=["POST"])
def start_agent():
    global agent_thread, agent_running
    with agent_lock:
        if agent_running:
            return jsonify({"message": "Agent already running"})
        config = AgentConfig.get_current()
        agent_running = True
        def agent_job():
            global agent_running
            logging.info("Agent started.")
            try:
                run_agent(config.topics, config.behavior)
            except Exception as e:
                logging.error("Agent crashed: %s", e)
            agent_running = False
            logging.info("Agent stopped.")
        agent_thread = threading.Thread(target=agent_job)
        agent_thread.start()
    return jsonify({"message": "Agent started"})

@bp.route("/api/stop", methods=["POST"])
def stop_agent():
    global agent_running
    with agent_lock:
        agent_running = False
    logging.info("Agent stop requested.")
    return jsonify({"message": "Agent stop requested"})

@bp.route("/api/analytics", methods=["GET"])
def analytics():
    like_count = AgentLog.query.filter_by(action="like").count()
    follow_count = AgentLog.query.filter_by(action="follow").count()
    comment_count = AgentLog.query.filter_by(action="comment").count()
    return jsonify({
        "like": like_count,
        "follow": follow_count,
        "comment": comment_count
    })

@bp.route("/api/state", methods=["GET"])
def agent_state():
    global agent_running
    return jsonify({"running": agent_running})