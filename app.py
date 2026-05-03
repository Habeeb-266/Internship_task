from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path

from flask import Flask, jsonify, request, send_file, send_from_directory

BASE_DIR = Path(__file__).resolve().parent
CSV_FILE = BASE_DIR / "enquiries.csv"

FIELDNAMES = ["timestamp", "name", "phone", "course", "duration", "fee"]

app = Flask(__name__)


def ensure_csv_exists() -> None:
    if CSV_FILE.exists():
        return
    with CSV_FILE.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
        writer.writeheader()


def read_enquiries() -> list[dict[str, str]]:
    ensure_csv_exists()
    with CSV_FILE.open("r", newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


@app.get("/")
def index():
    return send_from_directory(BASE_DIR, "education.html")


@app.get("/api/enquiries")
def get_enquiries():
    return jsonify({"ok": True, "enquiries": read_enquiries()})


@app.get("/api/enquiries/csv")
def open_enquiries_csv():
    ensure_csv_exists()
    return send_file(
        CSV_FILE,
        mimetype="text/csv",
        as_attachment=False,
        download_name="enquiries.csv",
    )


@app.post("/api/enquiries")
def add_enquiry():
    data = request.get_json(silent=True) or {}

    name = str(data.get("name", "")).strip()
    phone = str(data.get("phone", "")).strip()
    course = str(data.get("course", "")).strip()
    duration = str(data.get("duration", "")).strip()
    fee = str(data.get("fee", "")).strip()

    if not all([name, phone, course, duration, fee]):
        return jsonify({"ok": False, "message": "All fields are required."}), 400
    if not phone.isdigit() or len(phone) != 10:
        return jsonify({"ok": False, "message": "Phone must be 10 digits."}), 400

    ensure_csv_exists()
    row = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "name": name,
        "phone": phone,
        "course": course,
        "duration": duration,
        "fee": fee,
    }

    with CSV_FILE.open("a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
        writer.writerow(row)

    return jsonify({"ok": True, "message": "Enquiry saved."})


if __name__ == "__main__":
    ensure_csv_exists()
    app.run(host="127.0.0.1", port=5000, debug=True)
