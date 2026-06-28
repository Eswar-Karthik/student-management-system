"""Database models for EduManage SMS."""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # admin / teacher / student
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Student(db.Model):
    __tablename__ = "students"
    id = db.Column(db.Integer, primary_key=True)
    roll_no = db.Column(db.String(30), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120))
    phone = db.Column(db.String(30))
    gender = db.Column(db.String(10))
    dob = db.Column(db.String(20))
    course = db.Column(db.String(80))
    semester = db.Column(db.String(20))
    department = db.Column(db.String(80))
    address = db.Column(db.String(255))
    guardian_name = db.Column(db.String(120))
    guardian_contact = db.Column(db.String(30))
    blood_group = db.Column(db.String(10))
    admission_date = db.Column(db.String(20))
    fee_status = db.Column(db.String(20), default="Pending")
    cgpa = db.Column(db.Float, default=0.0)
    photo = db.Column(db.String(200), default="")


class Teacher(db.Model):
    __tablename__ = "teachers"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120))
    phone = db.Column(db.String(30))
    subject = db.Column(db.String(120))
    department = db.Column(db.String(120))


class Course(db.Model):
    __tablename__ = "courses"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    code = db.Column(db.String(20))
    duration = db.Column(db.String(40))
    department = db.Column(db.String(120))


class Attendance(db.Model):
    __tablename__ = "attendance"
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"))
    date = db.Column(db.String(20))
    status = db.Column(db.String(20))  # Present/Absent/Late/Leave


class Fee(db.Model):
    __tablename__ = "fees"
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"))
    amount = db.Column(db.Float, default=0)
    paid = db.Column(db.Float, default=0)
    status = db.Column(db.String(20), default="Pending")
    date = db.Column(db.String(20))


class Result(db.Model):
    __tablename__ = "results"
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"))
    subject = db.Column(db.String(120))
    internal = db.Column(db.Float, default=0)
    external = db.Column(db.Float, default=0)
    total = db.Column(db.Float, default=0)
    percentage = db.Column(db.Float, default=0)
    grade = db.Column(db.String(5))


class Activity(db.Model):
    __tablename__ = "activities"
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(80))
    message = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
