"""
app.py - Flask application for Book Express.

Flask routes create Boundary objects, which delegate to Controllers.
BCE flow: app.py (Flask) → Boundary → Controller → Entity

This keeps the BCE pattern explicit:
  - Routes handle HTTP (request/response)
  - Boundaries handle delegation logic
  - Controllers orchestrate workflows
  - Entities hold data
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, render_template, request, redirect, url_for, flash
from database import init_db
from boundaries.CSVImportPage import CSVImportPage
from boundaries.SearchPage import SearchPage
from boundaries.ItemDetailView import ItemDetailView
from entities.InventoryItem import InventoryItem
from entities.ImportLog import ImportLog
from entities.LowStockAlert import LowStockAlert
from entities.AuditLog import AuditLog

app = Flask(__name__)
app.secret_key = "book-express-dev-key"


# ============================================================
# Dashboard
# ============================================================

@app.route("/")
def index():
    items = InventoryItem.get_all()
    alerts = LowStockAlert.get_active_alerts()
    logs = ImportLog.get_recent(5)
    return render_template("index.html", items=items, alerts=alerts, logs=logs)


# ============================================================
# UC-001: Import Daily Sales (via CSVImportPage Boundary)
# ============================================================

@app.route("/import", methods=["GET"])
def import_page():
    return render_template("import.html")


@app.route("/import", methods=["POST"])
def process_import():
    """Flask route → CSVImportPage boundary → ImportController."""
    if "csv_file" not in request.files:
        flash("No file selected.", "error")
        return redirect(url_for("import_page"))

    file = request.files["csv_file"]
    if file.filename == "" or not file.filename.lower().endswith(".csv"):
        flash("Please upload a valid .csv file.", "error")
        return redirect(url_for("import_page"))

    try:
        file_content = file.read().decode("utf-8")
    except UnicodeDecodeError:
        flash("Cannot read file. Ensure it is a valid UTF-8 CSV.", "error")
        return redirect(url_for("import_page"))

    # Delegate to Boundary → Controller
    boundary = CSVImportPage()
    report = boundary.trigger_import(file_content, "staff_001")

    return render_template("report.html",
                           report=report.to_dict(),
                           filename=file.filename)


# ============================================================
# UC-002: Check Item Availability (via SearchPage Boundary)
# ============================================================

@app.route("/search", methods=["GET"])
def search_page():
    """Flask route → SearchPage boundary → SearchController."""
    query = request.args.get("q", "").strip()
    grade = request.args.get("grade", "").strip()
    subject = request.args.get("subject", "").strip()

    boundary = SearchPage()
    results = []

    if query:
        results = boundary.submit_search(query)
    elif grade:
        results = boundary.filter_by_grade(grade)
    elif subject:
        results = boundary.filter_by_subject(subject)

    # Get unique grades and subjects for filter dropdowns
    all_items = InventoryItem.get_all()
    grades = sorted(set(item.grade for item in all_items if item.grade))
    subjects = sorted(set(item.subject for item in all_items if item.subject))

    return render_template("search.html",
                           results=results, query=query,
                           selected_grade=grade, selected_subject=subject,
                           grades=grades, subjects=subjects,
                           has_searched=bool(query or grade or subject))


# ============================================================
# UC-002: View Item Details (via ItemDetailView Boundary)
# ============================================================

@app.route("/item/<item_id>")
def item_detail(item_id):
    """Flask route → ItemDetailView boundary → SearchController."""
    boundary = ItemDetailView()
    details = boundary.display_details(item_id)

    if details is None:
        flash(f"Item '{item_id}' not found.", "error")
        return redirect(url_for("search_page"))

    return render_template("item_detail.html", item=details)


# ============================================================
# Supporting pages
# ============================================================

@app.route("/inventory")
def inventory():
    items = InventoryItem.get_all()
    return render_template("inventory.html", items=items)


@app.route("/alerts")
def alerts():
    active_alerts = LowStockAlert.get_active_alerts()
    return render_template("alerts.html", alerts=active_alerts)


@app.route("/logs")
def logs():
    import_logs = ImportLog.get_recent(20)
    audit_logs = AuditLog.get_recent(20)
    return render_template("logs.html",
                           import_logs=import_logs,
                           audit_logs=audit_logs)


# ============================================================
# Initialize and run
# ============================================================

if __name__ == "__main__":
    init_db()
    print("\n  Book Express Inventory Management System")
    print("  UC-001: Import Daily Sales | UC-002: Check Item Availability")
    print("  Running at http://127.0.0.1:5000\n")
    app.run(debug=True, port=5000)