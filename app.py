"""
EduManage - Student Management System
Main Flask application entry point.
"""
import os
import io
import csv
from datetime import datetime, date
from functools import wraps

from flask import (
    Flask, render_template, request, redirect, url_for,
    session, flash, jsonify, send_file, abort
)
from werkzeug.security import generate_password_hash, check_password_hash

from models import db, User, Student, Teacher, Course, Attendance, Fee, Result, Activity
from seed import seed_database

# ---- App Factory ----------------------------------------------------------
def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "edumanage-secret-key-change-me"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///edumanage.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["UPLOAD_FOLDER"] = os.path.join("static", "uploads")
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    db.init_app(app)

    with app.app_context():
        db.create_all()
        seed_database()

    return app


app = create_app()


# ---- Helpers --------------------------------------------------------------
def login_required(role=None):
    """Decorator enforcing authentication + optional role check."""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if "user_id" not in session:
                flash("Please log in to continue.", "warning")
                return redirect(url_for("login"))
            if role and session.get("role") not in (role if isinstance(role, list) else [role]):
                flash("You don't have access to this page.", "danger")
                return redirect(url_for("dashboard"))
            return f(*args, **kwargs)
        return wrapper
    return decorator


def log_activity(message):
    """Record an activity entry visible on dashboard."""
    entry = Activity(user=session.get("username", "system"), message=message)
    db.session.add(entry)
    db.session.commit()


# ---- Public / Home --------------------------------------------------------
@app.route("/")
def home():
    stats = {
        "students": Student.query.count(),
        "teachers": Teacher.query.count(),
        "courses": Course.query.count(),
    }
    return render_template("home.html", stats=stats)


# ---- Authentication -------------------------------------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        role = request.form.get("role", "admin")

        user = User.query.filter_by(username=username, role=role).first()
        if user and check_password_hash(user.password, password):
            session["user_id"] = user.id
            session["username"] = user.username
            session["role"] = user.role
            log_activity(f"{user.username} ({user.role}) logged in")
            flash(f"Welcome back, {user.username}!", "success")
            return redirect(url_for("dashboard"))
        flash("Invalid credentials. Try the demo accounts shown below.", "danger")
    return render_template("login.html")


@app.route("/logout")
def logout():
    if "username" in session:
        log_activity(f"{session['username']} logged out")
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))


# ---- Dashboard ------------------------------------------------------------
@app.route("/dashboard")
@login_required()
def dashboard():
    total_students = Student.query.count()
    total_teachers = Teacher.query.count()
    total_courses = Course.query.count()

    # Attendance %
    att_records = Attendance.query.all()
    present = sum(1 for a in att_records if a.status == "Present")
    att_pct = round((present / len(att_records)) * 100, 1) if att_records else 0

    # Fee collected
    fees = Fee.query.all()
    fee_collected = sum(f.paid for f in fees)
    fee_total = sum(f.amount for f in fees)

    activities = Activity.query.order_by(Activity.created_at.desc()).limit(8).all()

    # Chart data
    courses = Course.query.all()
    course_labels = [c.name for c in courses]
    course_counts = [Student.query.filter_by(course=c.name).count() for c in courses]

    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    # demo growth distribution
    growth = [4, 7, 10, 14, 18, 22, 27, 32, 38, 44, 49, max(total_students, 55)]

    attendance_breakdown = {
        "Present": sum(1 for a in att_records if a.status == "Present"),
        "Absent": sum(1 for a in att_records if a.status == "Absent"),
        "Late": sum(1 for a in att_records if a.status == "Late"),
        "Leave": sum(1 for a in att_records if a.status == "Leave"),
    }

    return render_template(
        "dashboard.html",
        total_students=total_students,
        total_teachers=total_teachers,
        total_courses=total_courses,
        att_pct=att_pct,
        fee_collected=fee_collected,
        fee_total=fee_total,
        activities=activities,
        course_labels=course_labels,
        course_counts=course_counts,
        months=months,
        growth=growth,
        attendance_breakdown=attendance_breakdown,
    )


# ---- Students CRUD --------------------------------------------------------
@app.route("/students")
@login_required()
def students():
    q = request.args.get("q", "").strip()
    query = Student.query
    if q:
        like = f"%{q}%"
        query = query.filter(
            (Student.name.ilike(like)) |
            (Student.roll_no.ilike(like)) |
            (Student.email.ilike(like)) |
            (Student.course.ilike(like)) |
            (Student.department.ilike(like))
        )
    page = int(request.args.get("page", 1))
    per_page = 10
    pagination = query.order_by(Student.id.desc()).paginate(page=page, per_page=per_page, error_out=False)
    return render_template("students.html", pagination=pagination, q=q)


@app.route("/students/add", methods=["GET", "POST"])
@login_required(role="admin")
def add_student():
    if request.method == "POST":
        s = Student(
            roll_no=request.form["roll_no"],
            name=request.form["name"],
            email=request.form["email"],
            phone=request.form["phone"],
            gender=request.form["gender"],
            dob=request.form["dob"],
            course=request.form["course"],
            semester=request.form["semester"],
            department=request.form["department"],
            address=request.form["address"],
            guardian_name=request.form["guardian_name"],
            guardian_contact=request.form["guardian_contact"],
            blood_group=request.form["blood_group"],
            admission_date=request.form["admission_date"],
            fee_status=request.form.get("fee_status", "Pending"),
            cgpa=float(request.form.get("cgpa") or 0),
        )
        db.session.add(s)
        db.session.commit()
        log_activity(f"Added student {s.name} ({s.roll_no})")
        flash("Student added successfully.", "success")
        return redirect(url_for("students"))
    return render_template("student_form.html", student=None, courses=Course.query.all())


@app.route("/students/<int:sid>")
@login_required()
def student_profile(sid):
    student = Student.query.get_or_404(sid)
    attendance = Attendance.query.filter_by(student_id=sid).all()
    results = Result.query.filter_by(student_id=sid).all()
    fees = Fee.query.filter_by(student_id=sid).all()
    return render_template("student_profile.html",
                           student=student, attendance=attendance,
                           results=results, fees=fees)


@app.route("/students/<int:sid>/edit", methods=["GET", "POST"])
@login_required(role="admin")
def edit_student(sid):
    student = Student.query.get_or_404(sid)
    if request.method == "POST":
        for field in ["roll_no", "name", "email", "phone", "gender", "dob", "course",
                      "semester", "department", "address", "guardian_name",
                      "guardian_contact", "blood_group", "admission_date", "fee_status"]:
            setattr(student, field, request.form.get(field, getattr(student, field)))
        student.cgpa = float(request.form.get("cgpa") or student.cgpa or 0)
        db.session.commit()
        log_activity(f"Updated student {student.name}")
        flash("Student updated.", "success")
        return redirect(url_for("student_profile", sid=sid))
    return render_template("student_form.html", student=student, courses=Course.query.all())


@app.route("/students/<int:sid>/delete", methods=["POST"])
@login_required(role="admin")
def delete_student(sid):
    student = Student.query.get_or_404(sid)
    name = student.name
    Attendance.query.filter_by(student_id=sid).delete()
    Result.query.filter_by(student_id=sid).delete()
    Fee.query.filter_by(student_id=sid).delete()
    db.session.delete(student)
    db.session.commit()
    log_activity(f"Deleted student {name}")
    flash("Student deleted.", "info")
    return redirect(url_for("students"))


# ---- Teachers -------------------------------------------------------------
@app.route("/teachers", methods=["GET", "POST"])
@login_required(role="admin")
def teachers():
    if request.method == "POST":
        t = Teacher(
            name=request.form["name"],
            email=request.form["email"],
            phone=request.form["phone"],
            subject=request.form["subject"],
            department=request.form["department"],
        )
        db.session.add(t)
        db.session.commit()
        log_activity(f"Added teacher {t.name}")
        flash("Teacher added.", "success")
        return redirect(url_for("teachers"))
    items = Teacher.query.order_by(Teacher.id.desc()).all()
    return render_template("teachers.html", teachers=items)


@app.route("/teachers/<int:tid>/delete", methods=["POST"])
@login_required(role="admin")
def delete_teacher(tid):
    t = Teacher.query.get_or_404(tid)
    db.session.delete(t)
    db.session.commit()
    flash("Teacher removed.", "info")
    return redirect(url_for("teachers"))


# ---- Courses --------------------------------------------------------------
@app.route("/courses", methods=["GET", "POST"])
@login_required(role="admin")
def courses():
    if request.method == "POST":
        c = Course(
            name=request.form["name"],
            code=request.form["code"],
            duration=request.form["duration"],
            department=request.form["department"],
        )
        db.session.add(c)
        db.session.commit()
        flash("Course added.", "success")
        return redirect(url_for("courses"))
    items = Course.query.all()
    return render_template("courses.html", courses=items)


@app.route("/courses/<int:cid>/delete", methods=["POST"])
@login_required(role="admin")
def delete_course(cid):
    c = Course.query.get_or_404(cid)
    db.session.delete(c)
    db.session.commit()
    flash("Course removed.", "info")
    return redirect(url_for("courses"))


# ---- Attendance -----------------------------------------------------------
@app.route("/attendance", methods=["GET", "POST"])
@login_required(role=["admin", "teacher"])
def attendance():
    if request.method == "POST":
        att_date = request.form.get("date") or date.today().isoformat()
        for sid_key, status in request.form.items():
            if sid_key.startswith("status_"):
                sid = int(sid_key.split("_")[1])
                a = Attendance(student_id=sid, date=att_date, status=status)
                db.session.add(a)
        db.session.commit()
        log_activity(f"Marked attendance for {att_date}")
        flash("Attendance saved.", "success")
        return redirect(url_for("attendance"))

    students_list = Student.query.order_by(Student.name).all()
    records = Attendance.query.order_by(Attendance.id.desc()).limit(50).all()
    return render_template("attendance.html",
                           students=students_list, records=records,
                           today=date.today().isoformat())


# ---- Results --------------------------------------------------------------
def calculate_grade(pct):
    if pct >= 90: return "A+"
    if pct >= 80: return "A"
    if pct >= 70: return "B"
    if pct >= 60: return "C"
    if pct >= 50: return "D"
    return "F"


@app.route("/results", methods=["GET", "POST"])
@login_required(role=["admin", "teacher"])
def results():
    if request.method == "POST":
        sid = int(request.form["student_id"])
        subject = request.form["subject"]
        internal = float(request.form["internal"])
        external = float(request.form["external"])
        total = internal + external
        pct = round(total / 1.5, 2)  # out of 150 -> %
        grade = calculate_grade(pct)
        r = Result(student_id=sid, subject=subject, internal=internal,
                   external=external, total=total, percentage=pct, grade=grade)
        db.session.add(r)
        db.session.commit()
        log_activity(f"Added result for student #{sid} - {subject}")
        flash("Result recorded.", "success")
        return redirect(url_for("results"))

    items = Result.query.order_by(Result.id.desc()).all()
    students_list = Student.query.order_by(Student.name).all()
    return render_template("results.html", results=items, students=students_list)


# ---- Fees -----------------------------------------------------------------
@app.route("/fees", methods=["GET", "POST"])
@login_required(role="admin")
def fees():
    if request.method == "POST":
        sid = int(request.form["student_id"])
        amount = float(request.form["amount"])
        paid = float(request.form["paid"])
        status = "Paid" if paid >= amount else ("Partial" if paid > 0 else "Pending")
        f = Fee(student_id=sid, amount=amount, paid=paid, status=status,
                date=date.today().isoformat())
        db.session.add(f)
        # update student fee status
        s = Student.query.get(sid)
        if s: s.fee_status = status
        db.session.commit()
        log_activity(f"Recorded fee {paid}/{amount} for student #{sid}")
        flash("Fee record saved.", "success")
        return redirect(url_for("fees"))

    items = Fee.query.order_by(Fee.id.desc()).all()
    students_list = Student.query.order_by(Student.name).all()
    return render_template("fees.html", fees=items, students=students_list)


@app.route("/fees/<int:fid>/receipt")
@login_required()
def fee_receipt(fid):
    fee = Fee.query.get_or_404(fid)
    student = Student.query.get(fee.student_id)
    return render_template("receipt.html", fee=fee, student=student, now=datetime.now())


# ---- Reports + Export -----------------------------------------------------
@app.route("/reports")
@login_required()
def reports():
    return render_template("reports.html",
                           total_students=Student.query.count(),
                           total_teachers=Teacher.query.count(),
                           total_courses=Course.query.count(),
                           total_fees=sum(f.paid for f in Fee.query.all()))


@app.route("/export/<kind>.csv")
@login_required()
def export_csv(kind):
    output = io.StringIO()
    writer = csv.writer(output)

    if kind == "students":
        writer.writerow(["Roll No", "Name", "Email", "Phone", "Course", "Department", "CGPA", "Fee Status"])
        for s in Student.query.all():
            writer.writerow([s.roll_no, s.name, s.email, s.phone, s.course, s.department, s.cgpa, s.fee_status])
    elif kind == "attendance":
        writer.writerow(["Student", "Date", "Status"])
        for a in Attendance.query.all():
            s = Student.query.get(a.student_id)
            writer.writerow([s.name if s else "-", a.date, a.status])
    elif kind == "fees":
        writer.writerow(["Student", "Amount", "Paid", "Status", "Date"])
        for f in Fee.query.all():
            s = Student.query.get(f.student_id)
            writer.writerow([s.name if s else "-", f.amount, f.paid, f.status, f.date])
    elif kind == "results":
        writer.writerow(["Student", "Subject", "Internal", "External", "Total", "%", "Grade"])
        for r in Result.query.all():
            s = Student.query.get(r.student_id)
            writer.writerow([s.name if s else "-", r.subject, r.internal, r.external, r.total, r.percentage, r.grade])
    else:
        abort(404)

    mem = io.BytesIO(output.getvalue().encode("utf-8"))
    return send_file(mem, mimetype="text/csv",
                     as_attachment=True, download_name=f"{kind}.csv")


@app.route("/export/<kind>.pdf")
@login_required()
def export_pdf(kind):
    """Lightweight HTML-to-print PDF: renders a printable HTML page."""
    title = kind.title()
    if kind == "students":
        rows = [(s.roll_no, s.name, s.course, s.department, s.cgpa, s.fee_status) for s in Student.query.all()]
        headers = ["Roll", "Name", "Course", "Dept", "CGPA", "Fee"]
    elif kind == "attendance":
        rows = [(Student.query.get(a.student_id).name if Student.query.get(a.student_id) else "-", a.date, a.status) for a in Attendance.query.all()]
        headers = ["Student", "Date", "Status"]
    elif kind == "fees":
        rows = [(Student.query.get(f.student_id).name if Student.query.get(f.student_id) else "-", f.amount, f.paid, f.status) for f in Fee.query.all()]
        headers = ["Student", "Amount", "Paid", "Status"]
    elif kind == "results":
        rows = [(Student.query.get(r.student_id).name if Student.query.get(r.student_id) else "-", r.subject, r.total, r.percentage, r.grade) for r in Result.query.all()]
        headers = ["Student", "Subject", "Total", "%", "Grade"]
    else:
        abort(404)
    return render_template("print_report.html", title=title, headers=headers, rows=rows, now=datetime.now())


# ---- Profile / Settings ---------------------------------------------------
@app.route("/profile")
@login_required()
def profile():
    user = User.query.get(session["user_id"])
    return render_template("profile.html", user=user)


@app.route("/settings", methods=["GET", "POST"])
@login_required()
def settings():
    user = User.query.get(session["user_id"])
    if request.method == "POST":
        new_pw = request.form.get("password")
        if new_pw:
            user.password = generate_password_hash(new_pw)
            db.session.commit()
            flash("Password updated.", "success")
        return redirect(url_for("settings"))
    return render_template("settings.html", user=user)


@app.route("/users", methods=["GET", "POST"])
@login_required(role="admin")
def users():
    if request.method == "POST":
        u = User(
            username=request.form["username"],
            password=generate_password_hash(request.form["password"]),
            role=request.form["role"],
        )
        db.session.add(u)
        db.session.commit()
        flash("User created.", "success")
        return redirect(url_for("users"))
    return render_template("users.html", users=User.query.all())


@app.route("/users/<int:uid>/delete", methods=["POST"])
@login_required(role="admin")
def delete_user(uid):
    if uid == session["user_id"]:
        flash("You can't delete your own account.", "warning")
        return redirect(url_for("users"))
    u = User.query.get_or_404(uid)
    db.session.delete(u)
    db.session.commit()
    flash("User removed.", "info")
    return redirect(url_for("users"))


# ---- Backup / Restore -----------------------------------------------------
@app.route("/backup")
@login_required(role="admin")
def backup():
    path = os.path.join("instance", "edumanage.db")
    if not os.path.exists(path):
        flash("No database file found yet.", "warning")
        return redirect(url_for("settings"))
    return send_file(path, as_attachment=True, download_name="edumanage_backup.db")


# ---- Errors ---------------------------------------------------------------
@app.errorhandler(404)
def not_found(e):
    return render_template("error.html", code=404, message="Page not found"), 404


@app.errorhandler(500)
def server_error(e):
    return render_template("error.html", code=500, message="Something went wrong"), 500


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
