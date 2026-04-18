from flask import Flask, render_template, Response, request, redirect, send_file
import cv2
import os
from datetime import datetime

# Models
from models.face_model import load_faces, recognize_faces
from models.attention_model import detect_attention
from models.seat_model import map_seat
from models.engagement_score import calculate_engagement

# Database
from database.db import students_collection, attendance_collection

# Reports
from analytics.report_generator import generate_attendance_report

# Config
from config import UPLOAD_FOLDER

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Initialize Camera
camera = cv2.VideoCapture(0)

# Load Registered Faces
load_faces(UPLOAD_FOLDER)

# =========================
# ROUTES
# =========================

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@app.route("/admin")
def admin():
    students = list(students_collection.find({}, {"_id": 0}))
    return render_template("admin.html", students=students)


@app.route("/student")
def student():
    return render_template("student.html")


@app.route("/insights")
def insights():
    data = list(attendance_collection.find({}, {"_id": 0}))
    total = len(data)

    if total == 0:
        overall = 0
    else:
        overall = sum(d.get("engagement_score", 0) for d in data) / total

    return render_template("insights.html", overall=round(overall, 2))


# =========================
# REGISTER STUDENT
# =========================

@app.route("/register", methods=["POST"])
def register():
    name = request.form["name"]
    file = request.files["image"]

    file_path = os.path.join(app.config["UPLOAD_FOLDER"], f"{name}.jpg")
    file.save(file_path)

    students_collection.insert_one({
        "name": name,
        "registered_on": datetime.now()
    })

    load_faces(UPLOAD_FOLDER)

    return redirect("/admin")


# =========================
# VIDEO STREAM
# =========================

def generate_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break

        face_locations, names = recognize_faces(frame)
        height, width, _ = frame.shape

        for (top, right, bottom, left), name in zip(face_locations, names):

            # Calculate center for seat mapping
            center_x = (left + right) // 2
            center_y = (top + bottom) // 2

            seat = map_seat(width, height, center_x, center_y)

            # Attention detection
            attention_score = detect_attention(frame)

            # Attendance score (basic hackathon logic)
            attendance_score = 95 if name != "Unknown" else 0

            # Engagement score
            engagement = calculate_engagement(attendance_score, attention_score)

            # Draw bounding box
            color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)

            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)

            cv2.putText(frame,
                        f"{name} | Seat:{seat}",
                        (left, top - 25),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        color,
                        2)

            cv2.putText(frame,
                        f"Attention:{attention_score}% | Eng:{engagement['overall_score']}%",
                        (left, top - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        color,
                        2)

            # Update attendance DB
            if name != "Unknown":
                attendance_collection.update_one(
                    {"name": name},
                    {"$set": {
                        "status": "Present",
                        "seat": seat,
                        "attention_score": attention_score,
                        "engagement_score": engagement["overall_score"],
                        "last_seen": datetime.now()
                    }},
                    upsert=True
                )

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route("/video_feed")
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


# =========================
# REPORT DOWNLOAD
# =========================

@app.route("/download_report")
def download_report():
    file_path = generate_attendance_report()

    if file_path:
        return send_file(file_path, as_attachment=True)

    return "No attendance data available."


# =========================
# RUN APP
# =========================

if __name__ == "__main__":
    app.run(debug=True)