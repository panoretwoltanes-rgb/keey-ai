from flask import Blueprint, render_template, request, jsonify, send_from_directory
from services.api_service import submit_quote
from services.database_service import get_recent, get_order_detail
from config import OUTPUT_DIR

quote_bp = Blueprint("quote", __name__)

@quote_bp.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@quote_bp.route("/api/quote", methods=["POST"])
def api_quote():
    data = request.get_json(force=True, silent=True) or {}
    text = data.get("content", "").strip()
    result = submit_quote(text)
    return jsonify(result)

@quote_bp.route("/download/<filename>")
def download(filename):
    return send_from_directory(OUTPUT_DIR, filename, as_attachment=True)

@quote_bp.route("/api/history")
def history():
    limit = request.args.get("limit", 10, type=int)
    items = get_recent(limit)
    return jsonify({"success": True, "data": items})

@quote_bp.route("/api/history/<int:order_id>")
def history_detail(order_id):
    detail = get_order_detail(order_id)
    if not detail:
        return jsonify({"success": False, "message": "未找到"})
    return jsonify({"success": True, "data": detail})